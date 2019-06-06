import cryptography.utils
import logging
import os
import pysftp
import warnings

warnings.simplefilter("ignore", cryptography.utils.CryptographyDeprecationWarning)


class SftpHandler:

    """
    This class consolidates the SFTP functions.
    """

    def __init__(self, host, user, pwd):
        """
        Initializing the method will return an SFTP handler.

        :param host: Host
        :param user: Username
        :param pwd: Password
        """
        # Loads .ssh/known_hosts
        self.host = host
        self.cnopts = pysftp.CnOpts()
        if self.cnopts.hostkeys.lookup(host) is None:
            self.get_hostkeys(user, pwd)
        # At this point the hostkeys are available for the host.
        self.sftp = pysftp.Connection(self.host, username=user, password=pwd, cnopts=self.cnopts)
        return

    def get_hostkeys(self, user, pwd):
        """
        This method gets the hostkeys for the server.

        :param user: Username for SFTP connection
        :param pwd: for SFTP connection
        :return:
        """
        # Backup loaded .ssh/known_hosts file
        hostkeys = self.cnopts.hostkeys
        # And do not verify host key of the new host
        self.cnopts.hostkeys = None
        with pysftp.Connection(self.host, username=user, password=pwd, cnopts=self.cnopts) as sftp:
            logging.info("Connected to new host {}, caching its hostkey".format(self.host))
            hostkeys.add(self.host, sftp.remote_server_key.get_name(), sftp.remote_server_key)
            hostkeys.save(pysftp.helpers.known_hosts())
        return

    def close_connection(self):
        """
        Close the SFTP Connection.

        :return:
        """
        self.sftp.close()
        logging.debug("SFTP Connection closed.")
        return

    def get_content(self):
        """
        This method will collect the content (list of filenames) from the FTP directory.

        :return: List of filenames on the remote connection.
        """
        return self.ftp.nlst()

    def load_file(self, file=None, mode="ascii"):
        """
        Load file on FTP Server. If file exists already, then overwrite. Note that ascii mode has maximum line length
        so selecting binary is a better choice.

        :param file: Filename (including path) of the file to be loaded.
        :param mode: Required file transfer mode (ascii or bin, default is ascii)
        :return:
        """
        logging.debug("Moving file {file} to FTP Server, mode {mode}".format(file=file, mode=mode))
        # Get Filename from file pointer
        (filepath, filename) = os.path.split(file)
        stor_cmd = 'STOR ' + filename
        # Load the File
        if mode == "ascii":
            fh = open(file, mode='r')
            self.ftp.storlines(stor_cmd, fh)
        else:
            fh = open(file, mode='rb')
            self.ftp.storbinary(stor_cmd, fh)
        fh.close()
        return

    def read_file(self, file=None, workdir=None, mode="ascii"):
        """
        Read file on FTP Server and store locally as file on workdir. Note that ascii mode has maximum line length
        so selecting binary is a better choice.

        :param file: Filename of the file to be read.
        :param workdir: Local directory to store files that are read.
        :param mode: Required file transfer mode (ascii or bin, default is ascii)
        :return:
        """
        logging.debug("Reading file {file} from FTP Server, mode {mode}".format(file=file, mode=mode))
        local_file = os.path.join(workdir, file)
        retr_cmd = 'RETR ' + file
        # Load the File
        if mode == "ascii":
            fh = open(local_file, mode='w')
            self.ftp.retrlines(retr_cmd, fh.write)
        else:
            fh = open(local_file, mode='wb')
            self.ftp.retrbinary(retr_cmd, fh.write)
        fh.close()
        return

    def remove_file(self, file=None):
        """
        Remove file from FTP directory.

        :param file: Filename of the file to be removed. Path can be part of the filename.
        :return:
        """
        logging.debug("Removing file {file} from FTP Server".format(file=file))
        # Get Filename from file pointer
        (filepath, filename) = os.path.split(file)
        # Remove the File
        self.sftp.remove(filename)
        return

    def set_dir(self, dirname):
        """
        This method will change to the directory on the remote site. Directory can have subdirectories, / as separator.

        :param dirname:
        :return:
        """
        self.sftp.cwd(dirname)
        return

import logging
import os
from ftplib import FTP


class FtpHandler:

    """
    This class consolidates the FTP functions.
    """

    def __init__(self, host, user, pwd):
        """
        Initializing the method will return an FTP connection.

        :param host: FTP Host
        :param user: FTP Username
        :param pwd: FTP Password
        """
        self.ftp = FTP()
        self.ftp.connect(host=host, timeout=10)
        self.ftp.login(user=user, passwd=pwd)
        logging.debug("FTP Connection to {host} is configured".format(host=host))
        return

    def close_connection(self):
        """
        Close the FTP Connection.
        :return:
        """
        self.ftp.quit()
        logging.debug("FTP Connection closed.")
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
        self.ftp.delete(filename)
        return

    def set_dir(self, dir):
        """
        This method will change to the directory on the remote site. Directory can have subdirectories, / as separator.

        :param dir:
        :return:
        """
        self.ftp.cwd(dir)
        return

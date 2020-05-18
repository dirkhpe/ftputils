#!/home/mowdr/env/dataroom/bin/python
"""
This script will connect to an FTP Source directory, collect all files available and move them to an FTP Target
directory.
Files will be removed from the source directory.
"""
import logging
import os
from lib import my_env
from lib import ftp_handler
from lib import sftp_handler

cfg = my_env.init_env("ftputils", __file__)

workdir = cfg["Main"]["workdir"]
# Source
cfg_section = "FTPSource"
host = cfg[cfg_section]["host"]
user = cfg[cfg_section]["user"]
pwd = cfg[cfg_section]["pwd"]
ftpdir = cfg[cfg_section]["dir"]
ftp_source = ftp_handler.FtpHandler(host=host, user=user, pwd=pwd)
ftp_source.set_dir(ftpdir)

# Target
cfg_section = "FTPTarget"
host = cfg[cfg_section]["host"]
user = cfg[cfg_section]["user"]
pwd = cfg[cfg_section]["pwd"]
ftpdir = cfg[cfg_section]["dir"]
ftp_target = sftp_handler.SftpHandler(host=host, user=user, pwd=pwd)
ftp_target.set_dir(ftpdir)

res = ftp_source.get_content()
for file in res:
    logging.info("Move file {} from source to target".format(file))
    localfile = os.path.join(workdir, file)
    ftp_source.read_file(file, workdir, mode="bin")
    ftp_target.load_file(localfile)
    ftp_source.remove_file(file)
    os.remove(os.path.join(localfile))

ftp_source.close_connection()
ftp_target.close_connection()

#!/root/home/dirkv63/env/dr/bin/python
"""
This script will create a file, add a timestamp and move the file to an FTP directory. This allows to test FTP
connections.
The script runs in a loop for max_cnt times with sleep of wait seconds.
Use cron instead of ftp_loop.
"""
import datetime
import logging
import os
import platform
import socket
from lib import my_env
from lib import ftp_handler
from time import sleep

max_cnt = 5
wait = 10

cfg = my_env.init_env("ftputils", __file__)

workdir = cfg["Main"]["workdir"]
hostname = platform.node()
fn = os.path.join(workdir, "{host}.txt".format(host=hostname))

with open(fn, 'w') as fh:
    now = datetime.datetime.now()
    fh.write(now.strftime("%Y-%m-%d %H:%M:%S"))

# FTP
cfg_section = "FTPSource"
host = cfg[cfg_section]["host"]
user = cfg[cfg_section]["user"]
pwd = cfg[cfg_section]["pwd"]
ftpdir = cfg[cfg_section]["dir"]
for cnt in range(max_cnt):
    ftp_source = ftp_handler.FtpHandler(host=host, user=user, pwd=pwd)
    ftp_source.set_dir(ftpdir)
    try:
        ftp_source.load_file(fn, mode="bin")
        os.remove(os.path.join(fn))
        ftp_source.close_connection()
    except socket.timeout:
        logging.error("Timeout in FTP")
    sleep(wait)

logging.info("End Application")

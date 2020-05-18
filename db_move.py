#!/home/mowdr/env/dataroom/bin/python
"""
This script will moves the database tables to the dropserver.
"""
import logging
import os
from lib import my_env
from lib import sftp_key

cfg = my_env.init_env("ftputils", __file__)
source = cfg['DBDump']['source']
props = dict(
    host=cfg['DBDump']["host"],
    user=cfg['DBDump']["user"],
    pkf=cfg['DBDump']["pkf"]
)
remote = sftp_key.SftpHandler(**props)
remote.set_dir('IN')

file_list = [file for file in os.listdir(source) if '.csv' in file]
for file in file_list:
    logging.info("Copy {}".format(file))
    ffn = os.path.join(source, file)
    remote.load_file(ffn)

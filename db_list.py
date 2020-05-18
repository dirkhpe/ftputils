#!/home/mowdr/env/dataroom/bin/python
"""
This script will moves the database tables to the dropserver.
"""
from lib import my_env
from lib import sftp_key

cfg = my_env.init_env("ftputils", __file__)
props = dict(
    host=cfg['DBDump']["host"],
    user=cfg['DBDump']["user"],
    pkf=cfg['DBDump']["pkf"]
)
remote = sftp_key.SftpHandler(**props)
remote.set_dir('IN')
res = remote.listdir_attr()
for attr in res:
    print(attr)
remote.close_connection()

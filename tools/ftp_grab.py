#!/home/mowdr/env/dataroom/bin/python
"""
This script will grab all files from a remote directory and moves them to local directory. This is to be used in test
scenarios where files need to be removed before the production process will grab them.
"""

import argparse
import logging
from lib import my_env
from lib import sftp_handler

parser = argparse.ArgumentParser(
    description="Move files from Remote Server to local server."
)
parser.add_argument('-t', '--target', type=str, required=True,
                    choices=["MOWMDK", "Drupal", "MobielVlaanderen"],
                    help='Please provide the target on the Dropserver - select MOWMDK or Drupal')
parser.add_argument('-d', '--dir', type=str, required=True,
                    help='Please provide the target directory on the Dropserver - select IN or OUT')
args = parser.parse_args()

cfg = my_env.init_env("ftputils", __file__)
logging.info("Arguments: {a}".format(a=args))

# Collect files in from_dir
cfg_section = args.target
from_dir = args.dir
to_dir = cfg["Main"]["apex_log"]
# Connect to server
host = cfg[cfg_section]["host"]
user = cfg[cfg_section]["user"]
pwd = cfg[cfg_section]["pwd"]
sftph = sftp_handler.SftpHandler(host, user, pwd)
sftph.set_dir(from_dir)
files = sftph.listdir()
if len(files) > 0:
    for file in files:
        sftph.read_file(file, workdir=to_dir)
        sftph.remove_file(file)
        logging.info("{} collected from {} directory {}".format(file, args.target, args.dir))
sftph.close_connection()

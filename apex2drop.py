"""
This script moves csv files from apex server to dropserver for MOW_MDK or Drupal. After copy the files will be removed
from the source directory.
"""

import argparse
import logging
import os
from lib import my_env
from lib import sftp_handler

parser = argparse.ArgumentParser(
    description="Move files from APEX Server to Dropserver."
)
parser.add_argument('-t', '--target', type=str, required=True,
                    choices=["MOWMDK", "Drupal"],
                    help='Please provide the target on the Dropserver - select MOWMDK or Drupal')
args = parser.parse_args()

cfg = my_env.init_env("ftputils", __file__)
logging.info("Arguments: {a}".format(a=args))

# Collect files in from_dir
cfg_section = args.target
from_dir = cfg["Main"]["apex_out"]
file_ext = cfg[cfg_section]["extension"]
files = [file for file in os.listdir(from_dir) if file.endswith(file_ext)]
if files:
    # Move files to server
    # Connect to server
    host = cfg[cfg_section]["host"]
    user = cfg[cfg_section]["user"]
    pwd = cfg[cfg_section]["pwd"]
    to_dir = cfg[cfg_section]["to_dir"]
    sftph = sftp_handler.SftpHandler(host, user, pwd)
    sftph.set_dir(to_dir)
    for file in files:
        from_file = os.path.join(from_dir, file)
        sftph.load_file(from_file)
        os.remove(from_file)
        logging.info("{} moved to dropserver for {}".format(file, cfg_section))
    sftph.close_connection()
else:
    logging.debug("No files to be moved for {}.".format(cfg_section))

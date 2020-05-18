#!/home/mowdr/env/dataroom/bin/python
"""
This script moves csv files from dropserver to apex server for MOW_MDK. After copy the files will be removed from the
source directory.
"""

import datetime
import logging
import os
from lib import my_env
from lib import sftp_handler

cfg = my_env.init_env("ftputils", __file__)

# Collect files in from_dir
cfg_section = "MOWMDK"
from_dir = cfg[cfg_section]["from_dir"]
to_dir = cfg["Main"]["apex_in"]
apex_log = cfg["Main"]["apex_log"]
# Link to log file
now = datetime.datetime.now()
day = now.strftime("%d")
ds = now.strftime("%Y%m%d")
ts = now.strftime("%H%M%S")
fn = "mdk2apex.sh.{}".format(day)
ffn = os.path.join(apex_log, fn)
logfh = open(ffn, "a+")
script = os.path.realpath(__file__)
# Connect to server
host = cfg[cfg_section]["host"]
user = cfg[cfg_section]["user"]
pwd = cfg[cfg_section]["pwd"]
sftph = sftp_handler.SftpHandler(host, user, pwd)
sftph.set_dir(from_dir)
files = sftph.listdir()
if len(files) > 0:
    for file in files:
        try:
            sftph.read_file(file, workdir=to_dir)
        except IOError:
            logging.error("Error reading file {}".format(file))
        else:
            logline = "{script};{date};{time}FROM;databestand {file} van de dropserver afgehaald\n".format(script=script,
                                                                                                       date=ds, time=ts,
                                                                                                       file=file)
            logfh.write(logline)
        sftph.remove_file(file)
else:
    logline = "{script};{date};{time}FROM;geen databestanden aanwezig.\n".format(script=script, date=ds, time=ts)
    logfh.write(logline)
sftph.close_connection()
logfh.close()

"""
This script will create a file, add a timestamp and move the file to an STP directory. This allows to test SFTP
connections.
"""
import cryptography.utils
import datetime
import logging
import os
import platform
import pysftp
import warnings
from lib import my_env

warnings.simplefilter("ignore", cryptography.utils.CryptographyDeprecationWarning)

cfg = my_env.init_env("ftputils", __file__)

workdir = cfg["Main"]["workdir"]
hostname = platform.node()
fn = os.path.join(workdir, "{host}.txt".format(host=hostname))
with open(fn, 'w') as fh:
    now = datetime.datetime.now()
    fh.write(now.strftime("%Y-%m-%d %H:%M:%S"))

cfg_section = "SFTPTest"
host = cfg[cfg_section]["host"]
user = cfg[cfg_section]["user"]
pwd = cfg[cfg_section]["pwd"]
ftpdir = cfg[cfg_section]["dir"]

# Loads .ssh/known_hosts
cnopts = pysftp.CnOpts()
if cnopts.hostkeys.lookup(host) is None:
    print("New host - will accept any host key")
    # Backup loaded .ssh/known_hosts file
    hostkeys = cnopts.hostkeys
    # And do not verify host key of the new host
    cnopts.hostkeys = None

with pysftp.Connection(host, username=user, password=pwd, cnopts=cnopts) as sftp:
    try:
        logging.info("Connected to new host, caching its hostkey")
        hostkeys.add(host, sftp.remote_server_key.get_name(), sftp.remote_server_key)
        hostkeys.save(pysftp.helpers.known_hosts())
    except NameError:
        logging.debug("Host Key exists.")
    with sftp.cd(ftpdir):             # temporarily chdir to public
        # sftp.put('/my/local/filename')  # upload file to public/ on remote
        sftp.get('kf')         # get a remote file

#!/home/mowdr/env/dataroom/bin/python
"""
This script will connect to an AWS Source directory, collect all files available and move them to the FTP Target
directory.
Files will be removed from the source directory.
"""
import logging
import os
from lib import my_env
from lib import aws_handler
from lib import sftp_handler

my_env.init_env("ftputils", __file__)

workdir = os.getenv("WORKDIR")
# Source
aws_source = aws_handler.AwsHandler()
ftp_dir = os.getenv('FTP_DIR')

# Target
ftp_target = sftp_handler.SftpHandler(host=os.getenv('TARGET_HOST'),
                                      user=os.getenv('TARGET_USER'),
                                      pwd=os.getenv('TARGET_PWD'))
ftp_target.set_dir(os.getenv('TARGET_DIR'))

res = aws_source.get_objects(ftp_dir)
for file in res:
    logging.info("Move file {file} from source to target".format(file=file))
    localfile = os.path.join(workdir, file)
    content = aws_source.get_file(file, ftp_dir)
    with open(localfile, 'wb') as fh:
        fh.write(content)
    ftp_target.load_file(localfile)
    aws_source.remove_file(file, ftp_dir)
    os.remove(os.path.join(localfile))

ftp_target.close_connection()

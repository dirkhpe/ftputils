import os
from lib import my_env
from lib import aws_handler

my_env.init_env("ftputils", __file__)
aws_source = aws_handler.AwsHandler()
ftp_dir = os.getenv('FTP_DIR')

aws_source.get_file('filezwaarte_nb_cijfers.csv')

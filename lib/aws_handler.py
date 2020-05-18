#!/opt/csw/bin/python3

import boto3
import logging
import mimetypes
import os
import re
from botocore.exceptions import ClientError


class AwsHandler:

    """
    This class consolidates the AWS functions. On initialization the S3 Client object is created.
    """

    def __init__(self):
        sts_client = boto3.client('sts')
        assumed_role_object = sts_client.assume_role(
            RoleArn=os.getenv('ARN'),
            RoleSessionName="AssumeRoleSession",
            ExternalId=os.getenv('EXTERNALID')
        )
        credentials = assumed_role_object['Credentials']
        self.client = boto3.client(
            's3',
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
        self.bucket = os.getenv('BUCKET')
        return

    def load_file(self, file, ftp_dir=None):
        """
        Load file on repository server. If file exists already, then overwrite.

        :param file: Filename (including path) of the file to be loaded.
        :param ftp_dir: Directory in which to load the file.
        :return:
        """
        logging.debug("Moving file {} to S3 Bucket".format(file))
        content_type = mimetypes.guess_type(file)[0]
        (filepath, filename) = os.path.split(file)
        with open(file, 'rb') as fh:
            body = fh.read()
        if ftp_dir:
            key = "{ftp_dir}/{filename}".format(ftp_dir=ftp_dir, filename=filename)
        else:
            key = filename
        res = self.client.put_object(Body=body, Bucket=self.bucket, Key=key, ContentType=content_type)
        try:
            http_status = res['ResponseMetadata']['HTTPStatusCode']
        except KeyError:
            logging.error("Load file {file} not successful, response: {res}".format(file=file, res=res))
        else:
            if http_status == 200:
                msg = "Load file {file} as type {content_type} done.".format(file=file, content_type=content_type)
                logging.info(msg)
            else:
                msg = "Unexpected status {status}, Response: {res}".format(status=http_status, res=res)
                logging.error(msg)
        return

    def remove_file(self, file, ftp_dir=None):
        """
        Remove file from repository server. Remove 'empty' identifier if it is still in the filename.

        :param file: Filename of the file to be removed. Path can be part of the filename. Filename is the Key in S3
        speak.
        :param ftp_dir: FTP Directory containing the file.
        :return:
        """
        # Get Filename from file pointer
        (filepath, filename) = os.path.split(file)
        filename = re.sub('empty\.', '', filename)
        logging.info("Removing file {file} ({filename}) from Server".format(file=file, filename=filename))
        if ftp_dir:
            key = "{ftp_dir}/{filename}".format(ftp_dir=ftp_dir, filename=filename)
        else:
            key = filename
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return

    def list_files(self):
        """
        List files (objects) in S3 Bucket.

        :return: Dictionary containing files (objects) in the S3 Container.
        """
        res = self.client.list_objects_v2(Bucket=self.bucket)
        return res

    def get_objects(self, direct):
        """
        Get objects in the bucket on directory dir.

        :param direct: Directory containing the objects to get. Case sensitive.
        :return: List containing the key names (not including the dir/)
        """
        direct = "{dir}/".format(dir=direct)
        files = []
        res = self.list_files()
        for item in res['Contents']:
            key = item['Key']
            if direct == key[:len(direct)]:
                files.append(key[len(direct):])
        return files

    def get_file(self, file, ftp_dir=None):
        """
        get file from repository server.

        :param file: Filename of the file to be retrieved.
        :param ftp_dir: Directory in which to load the file.
        :return:
        """
        logging.debug("Getting file {} from S3 Bucket".format(file))
        if ftp_dir:
            key = "{ftp_dir}/{filename}".format(ftp_dir=ftp_dir, filename=file)
        else:
            key = file
        try:
            res = self.client.get_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            logging.error("Received error: %s", e, exc_info=True)
            return False
        else:
            return res['Body'].read()

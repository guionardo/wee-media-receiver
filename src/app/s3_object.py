import datetime
import logging
import os
import tempfile

import boto3
import filetype
from botocore.exceptions import ClientError
from src import __appname__, __version__
from src.config.config import Config


class S3Object:

    def __init__(self, config: Config, key: str, keep_file: bool = False):
        self.config = config
        self.key = key
        self.log = logging.getLogger(self.__class__.__name__)
        self.client = boto3.client('s3', **self.config.s3_to_dict())
        self.bucket = boto3.resource(
            's3', **self.config.s3_to_dict()).Bucket(self.config.bucket_name)

        self.log.info('S3Object(%s:%s) initialized',
                      self.config.bucket_name, key)

        self.metadata = {}
        self.last_modified = datetime.datetime(1, 1, 1)
        self.downloaded = False
        self.public_url = ''
        self._keep = keep_file

    def filename(self) -> str:
        if self.downloaded:
            return self.file.name

    def __enter__(self):
        try:
            self.file = tempfile.NamedTemporaryFile(
                'w+', prefix=os.path.basename(self.key), delete=not self._keep)
            obj = self.bucket.Object(self.key)
            obj.load()
            self.exists = True
            self.metadata = obj.metadata
            self.last_modified = obj.last_modified
            self.public_url = f'{self.config.endpoint_url}/{self.config.bucket_name}/{self.key}'
            self.log.info('Object %s:%s %s %s', self.config.bucket_name,
                          self.key, self.last_modified, self.metadata)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.exists = False
            else:
                self.log.error('Error loading object %s: %s', self.key, e)
                raise

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.log.error('Exiting with exception: %s', exc_val)
        self.file.close()

    def download(self) -> bool:
        if not self.exists:
            return False

        try:
            self.log.info('Downloading %s:%s',
                          self.config.bucket_name, self.key)
            self.client.download_file(
                Bucket=self.config.bucket_name,
                Key=self.key,
                Filename=self.file.name)
            self.log.info('Downloaded file #%s', self.key)
            self.downloaded = True
            return True
        except Exception as e:
            self.log.error('Error downloading object %s: %s', self.key, e)
            return False

    def upload(self, filename: str, content_type: str = None, **metadata) -> bool:
        if not os.path.isfile(filename):
            return False
        try:
            if not content_type:
                content_type = filetype.guess_mime(filename)
            extra_args = {
                'ACL': 'public-read',
                'ContentType': content_type,
                'Metadata': {
                    'processor': __appname__+'-'+__version__,
                    **metadata
                }
            }
            if hasattr(filename, 'read'):
                self.client.upload_fileobj(
                    filename, self.config.bucket_name, self.key, ExtraArgs=extra_args)
            else:
                self.client.upload_file(
                    filename, self.config.bucket_name, self.key, ExtraArgs=extra_args)
            self.public_url = f'{self.config.endpoint_url}/{self.config.bucket_name}/{self.key}'
            return True
        except Exception as e:
            self.log.error('Error uploading object %s: %s', self.key, e)
            return False

    def get_metadata(self, media_id: str) -> dict:
        try:
            obj = self.bucket.Object(media_id)
            metadata = obj.metadata
            self.log.info('Metadata: #%s = %s', media_id, metadata)
        except Exception as e:
            metadata = {}
            self.log.error('Error getting metadata for %s: %s', media_id, e)
        return metadata

    def set_metadata(self, media_id: str, metadata: dict) -> bool:
        try:
            s3 = boto3.resource('s3', **self.config.s3_to_dict())
            obj = s3.Object(self.config.bucket_name, media_id)
            obj.metadata.update(metadata)
            obj.copy_from(CopySource={'Bucket': self.config.bucket_name, 'Key': media_id},
                          Metadata=obj.metadata,
                          MetadataDirective='REPLACE')

            self.metadata = metadata
            self.log.info('Metadata updated: #%s = %s', media_id, metadata)
            return True
        except Exception as exc:
            self.log.error('Error setting metadata for %s: %s', media_id, exc)

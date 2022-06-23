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
        self.exists = False
        self.forbidden = False

    def filename(self) -> str:
        if self.downloaded:
            return self.file.name

    def __enter__(self):
        try:
            self.file = tempfile.NamedTemporaryFile(
                'w+', prefix=os.path.basename(self.key), delete=not self._keep)
            if not self.key.startswith(self.config.endpoint_path_prefix):
                key = os.path.join(self.config.endpoint_path_prefix, self.key)
            else:
                key = self.key
            if key.startswith('/'):
                key = key[1:]
            self.key = key
            _ = self.object_load()

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                self.exists = False
            elif e.response['Error']['Code'] == '403':
                self.forbidden = True
            else:
                self.log.error('Error loading object %s: %s', self.key, e)
                raise

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.log.error('Exiting with exception: %s', exc_val,
                           exc_info=(exc_type, exc_val, exc_tb))
        self.file.close()

    def object_load(self):
        obj = self.bucket.Object(self.key)
        obj.load()
        self.exists = True
        self.forbidden = False
        self.metadata = obj.metadata
        self.last_modified = obj.last_modified
        self.public_url = f'{self.config.endpoint_url}/{self.key}'
        self.log.info('Object %s:%s %s %s', self.config.bucket_name,
                      self.key, self.last_modified, self.metadata)
        return obj

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

    def delete(self) -> bool:
        if not self.exists:
            return True

        try:
            self.log.info('Deleting %s:%s', self.config.bucket_name, self.key)
            self.client.delete_object(
                Bucket=self.config.bucket_name, Key=self.key)
            self.log.info('Deleted object %s:%s',
                          self.config.bucket_name, self.key)
            return True
        except Exception as exc:
            self.log.error('Error deleting object %s: %s', self.key, exc)

    def upload(self, filename: str,
               content_type: str = None,
               **metadata) -> bool:
        if not os.path.isfile(filename):
            return False
        try:
            if not content_type:
                content_type = filetype.guess_mime(
                    filename) or 'application/octet-stream'
            metadata = parse_metadata(metadata)

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
                    filename, self.config.bucket_name,
                    self.key, ExtraArgs=extra_args)
            else:
                self.client.upload_file(
                    filename, self.config.bucket_name,
                    self.key, ExtraArgs=extra_args)
            self.public_url = self.config.endpoint_url +\
                f'{self.config.bucket_name}/{self.key}'
            _ = self.object_load()
            return True
        except Exception as e:
            self.log.error('Error uploading object %s: %s', self.key, e)
            return False

    def set_metadata(self, new_metadata: dict,
                     do_not_update: bool = False) -> bool:
        try:
            obj = self.object_load()
            new_metadata = parse_metadata(new_metadata)
            if obj.metadata == new_metadata:
                return True

            if do_not_update:
                obj.metadata.clear()

            obj.metadata.update(new_metadata)

            obj.copy_from(CopySource=dict(Bucket=self.config.bucket_name,
                                          Key=self.key),
                          Metadata=obj.metadata,
                          MetadataDirective='REPLACE')

            self.metadata = new_metadata

            self.log.info('Metadata updated: #%s = %s', self.key, new_metadata)
            return True
        except Exception as exc:
            self.log.error('Error setting metadata for %s: %s', self.key, exc)


def parse_metadata(metadata: dict) -> dict:
    if not metadata or not isinstance(metadata, dict):
        return {}

    return {key: str(value) for key, value in metadata.items()}

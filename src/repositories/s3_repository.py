import logging
import time

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from src.config.config import Config
from src.dto.media_status_enum import MediaStatusEnum


class S3Client:

    def __init__(self, config: Config):
        self._config = config
        self.log = logging.getLogger(self.__class__.__name__)
        self.client = boto3.client('s3', **self._config.s3_to_dict())
        self.bucket = self.setup_bucket()
        self.log.info('S3Client initialized - %s:%s',
                      self._config.endpoint_url, self._config.bucket_name)

    def setup_bucket(self):
        bucket = boto3.resource(
            's3', **self._config.s3_to_dict()).Bucket(self._config.bucket_name)

        return bucket

    def file_exists(self, key: str) -> bool:
        try:
            self.bucket.Object(key).load()
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def get_file_info(self, media_id) -> MediaStatusEnum:
        try:
            obj = self.bucket.Object(media_id)

            last_modified = obj.last_modified
            return MediaStatusEnum.Accepted
        except ClientError as e:
            if '404' in str(e):
                return MediaStatusEnum.NOT_FOUND
        except Exception as e:
            self.log.error(e)
            return None

    def put_file(self, media_id: str, file: UploadFile, content_length: int) -> bool:
        try:
            start_time = time.time()
            self.log.info('Uploading #%s - %s (%s) @ %s',
                          media_id, file.filename, file.content_type, self._config.bucket_name)
            self.bucket.upload_fileobj(file.file, media_id, ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'public-read',
                'Metadata': {'wmr-status': MediaStatusEnum.Accepted.value}
            })

            self.log.info('Done upload %s bytes @ %s B/s', content_length,
                          content_length / (time.time() - start_time))
            return True
        except Exception as e:
            self.log.error(e)
            return None

    def download_file(self, media_id: str, filename: str):
        try:
            self.client.download_file(
                Bucket=self._config.bucket_name,
                Key=media_id,
                Filename=filename)
            self.log.info('Downloaded file #%s', media_id)
            return True
        except Exception as e:
            self.log.error(e)
            return False

    def get_file_metadata(self, media_id: str) -> dict:
        try:
            obj = self.bucket.Object(media_id)
            metadata = obj.metadata
            self.log.info('Metadata: #%s = %s', media_id, metadata)
        except Exception as e:
            metadata = {}
            self.log.error('Error getting metadata for %s: %s', media_id, e)
        return metadata

    def set_file_metadata(self, media_id: str, metadata: dict) -> bool:
        try:
            obj = self.bucket.Object(media_id)
            obj.metadata.update(metadata)
            obj.copy_from(CopySource={'Bucket': self._config.bucket_name, 'Key': media_id},
                          Metadata=obj.metadata, MetadataDirective='REPLACE')
            self.log.info('Metadata updated: #%s = %s', media_id, metadata)
            return True
        except Exception as exc:
            self.log.error('Error setting metadata for %s: %s', media_id, exc)

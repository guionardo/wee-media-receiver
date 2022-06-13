import logging
from typing import List

import boto3
from src.config.config import Config


class S3Collection:

    def __init__(self, config: Config):
        self.config = config
        self.log = logging.getLogger(self.__class__.__name__)
        self.client = boto3.client('s3', **config.s3_to_dict())

    def get_unprocessed_objects(self) -> List[str]:
        response = self.client.list_objects(
            Bucket=self.config.bucket_name,
            Prefix='uploads/')
        for obj in response['Contents']:
            try:
                key = obj['Key']
                obj = self.client.head_object(
                    Bucket=self.config.bucket_name,
                    Key=key)
                obj = self.bucket.Object(key)
                if obj.metadata and obj.metadata.get('processor', ''):
                    yield key

            except Exception as e:
                self.log.error(
                    'Error getting metadata for %s: %s', key, e)

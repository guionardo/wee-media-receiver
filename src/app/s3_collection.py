import logging
from queue import Empty, Full, Queue
from threading import Thread
import threading
from typing import List

import boto3
from src.config.config import Config


class S3Collection:

    def __init__(self, config: Config):
        self.config = config
        self.log = logging.getLogger(self.__class__.__name__)
        self.client = boto3.client('s3', **config.s3_to_dict())

    def get_unprocessed_objects(self, limit: int = 0, prefix='') -> List[str]:
        prefix = prefix or self.config.endpoint_path_prefix

        # Get all files

        paginator = self.client.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=self.config.bucket_name,
            Prefix=prefix
        )
        source_queue = Queue()
        for page in pages:
            for obj in page['Contents']:
                key = obj.get('Key', '')
                if not key.endswith('/'):
                    source_queue.put(key)

        # response = self.client.list_objects_v2(
        #     Bucket=self.config.bucket_name,
        #     Prefix=prefix
        # )
        # if response.get('KeyCount', 0) == 0 or not response.get('Contents'):
        #     return []
        # if limit < 1:
        #     limit = len(response['Contents'])
        # else:
        #     limit = min(limit, len(response['Contents']))

        # for obj in response['Contents'][0:limit]:
        #     source_queue.put(obj.get('Key'))

        result_queue = Queue(maxsize=limit)

        def consume_queue():
            try:
                while result_queue.maxsize > result_queue.qsize():
                    obj_key = source_queue.get(block=False)
                    obj = self.client.head_object(
                        Bucket=self.config.bucket_name,
                        Key=obj_key)
                    # self.log.info('Got object: %s', obj)
                    if not obj.get('Metadata', {}).get('wmr-status', '') \
                            and obj.get('ContentLength'):
                        self.log.info('#%s Got unprocessed object: %s',
                                      threading.current_thread, obj_key)
                        result_queue.put(obj_key, block=False)
            except Empty:
                ...
            except Full:
                ...
            except Exception as exc:
                self.log.error('Error fetching object %s', exc)

        threads = [
            Thread(name=f'fetcher_{n}',
                   target=consume_queue,
                   daemon=True)
            for n in range(4)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        while not result_queue.empty():
            yield result_queue.get()

    def get_storage_folders(self, prefix: str = '') -> List[str]:
        paginator = self.client.get_paginator('list_objects_v2')
        pages = paginator.paginate(
            Bucket=self.config.bucket_name,
            Prefix=prefix
        )
        for page in pages:
            for obj in page['Contents']:
                key = obj.get('Key', '')
                if key.endswith('/'):
                    yield key

import logging
import os
import sys
import unittest

from src.app.s3_collection import S3Collection
from src.config.config import Config
from src.config.dotenv import load_dotenv

SKIP = 'Skipping test for s3 collection'
def SKIPPING(): return os.getenv('S3_ACCESS_KEY') is None


class TestS3Collection(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.filename = 'uploading_test.txt'
        load_dotenv(filename='.env.testing')
        logging.basicConfig(level=logging.DEBUG,
                            format=logging.BASIC_FORMAT,
                            stream=sys.stderr)

        return super().setUpClass()

    @unittest.skipIf(SKIPPING(), SKIP)
    def test_unprocessed_objects(self):
        config = Config()
        col = S3Collection(config)
        for unprocessed in col.get_unprocessed_objects():
            logging.info('Unprocessed: %s', unprocessed)
        self.assertTrue(bool(unprocessed))

    def test_get_folders(self):
        config = Config()
        col = S3Collection(config)
        for folder in col.get_storage_folders():
            logging.info('Folder: %s', folder)
        self.assertTrue(bool(folder))

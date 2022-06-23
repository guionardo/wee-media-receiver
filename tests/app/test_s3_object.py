import logging
import os
import sys
import tempfile
import unittest

from src.app.s3_object import S3Object
from src.config.config import Config
from src.config.dotenv import load_dotenv

SKIP = 'Skipping test for s3 object'
def SKIPPING(): return os.getenv('S3_ACCESS_KEY') is None


class TestS3Object(unittest.TestCase):

    @classmethod
    def delete_test_file(cls):
        if SKIPPING():
            return
        with S3Object(Config(), cls.filename, keep_file=True) as s3_object:
            s3_object.delete()

    @classmethod
    def setUpClass(cls) -> None:
        cls.filename = 'uploading_test.txt'
        load_dotenv(filename='.env.testing')
        logging.basicConfig(level=logging.DEBUG,
                            format=logging.BASIC_FORMAT,
                            stream=sys.stderr)
        cls.delete_test_file()

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.delete_test_file()
        return super().tearDownClass()

    @unittest.skipIf(SKIPPING(), SKIP)
    def test_0_cleaning(self):
        config = Config()
        with S3Object(config, 'uploading_test.txt') as s3_object:
            self.assertFalse(s3_object.exists)

    @unittest.skipIf(SKIPPING(), SKIP)
    def test_1_upload(self):
        config = Config()
        with S3Object(config, self.filename) as s3_object:
            with tempfile.NamedTemporaryFile(mode='w+') as f:
                f.write('Hello, world!')
                f.flush()
                s3_object.upload(f.name, testing=True)
                self.assertTrue(s3_object.exists)

            s3_object.set_metadata({'updated': 'ABCD_EFGH',
                                    'level': 1})

        with S3Object(config, self.filename) as s3_object2:
            self.assertTrue(s3_object2.exists)
            self.assertEqual('ABCD_EFGH', s3_object2.metadata['updated'])
            self.assertEqual('1', s3_object2.metadata['level'])

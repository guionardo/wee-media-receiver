import logging
import os
import unittest

from src.app.s3_object import S3Object
from src.config.config import Config
from src.config.dotenv import load_dotenv


class TestS3Object(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
        logging.basicConfig(level=logging.DEBUG, format=logging.BASIC_FORMAT)
        return super().setUpClass()

    @unittest.skipIf(os.getenv('S3_ACCESS_KEY') is None, 'Skipping test_update_object')
    def test(self):
        config = Config()
        # dict(S3_ACCESS_KEY='M8HHAKCPE0ISM2LL0E9X',
        #      S3_SECRET_KEY='dN9OjGDJUA54tDiAaBCIMxixEgf75CIcF3H60ZNn',
        #      S3_BUCKET_NAME='teste-videos',
        #      S3_ENDPOINT_URL='https://teste-videos.us-east-1.linodeobjects.com/')
        with S3Object(config, 'test_1') as s3:
            self.assertTrue(s3.download())
            print(s3)

        with S3Object(config, 'uploads/test_2') as s3:
            self.assertTrue(s3.upload('olha.mp4'))
            print(s3)

    # def test_update_object(self):


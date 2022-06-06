import logging
import os
import sys
import unittest
from src.domain.media_data import MediaData
from src.repositories.media_repository import MediaRepository
from src.config.config import Config


class TestMediaRepository(unittest.TestCase):

    config: Config

    @classmethod
    def setUpClass(cls) -> None:
        logging.basicConfig(level=logging.DEBUG,
                            format=logging.BASIC_FORMAT,
                            stream=sys.stderr)
        cls.config = Config(source=dict(S3_ACCESS_KEY='ABCD',
                                        S3_SECRET_KEY='ABCD',
                                        S3_BUCKET_NAME='test',
                                        S3_ENDPOINT_URL='https://test.com/',
                                        LOCAL_DB='./testing.db'))

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isfile('./testing.db'):
            os.remove('./testing.db')

    def test_(self):
        repo = MediaRepository(self.config)

        self.assertTrue(repo.set_media(MediaData(
            media_id=1234, media_path='/tmp/teste.mp4', media_new_path='/tmp/teste.webm')))

        md = repo.get_media(1234)
        self.assertEqual(md.media_path, '/tmp/teste.mp4')

        self.assertTrue(repo.set_media(MediaData(
            media_id=2, media_path='/tmp/teste2.mp4', media_new_path='/tmp/teste.webm', notification_accepted=1)))
        self.assertTrue(repo.set_media(MediaData(
            media_id=3, media_path='/tmp/teste3.mp4', media_new_path='/tmp/teste.webm', notification_accepted=0)))
        self.assertTrue(repo.set_media(MediaData(
            media_id=4, media_path='/tmp/teste4.mp4', media_new_path='/tmp/teste.webm', notification_accepted=1)))

        unnotified = repo.get_unnotified_media()
        self.assertEqual(len(unnotified), 2)

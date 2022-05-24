import unittest

from src.repositories.s3_repository import S3Client, S3Config


class TestS3Repository(unittest.TestCase):

    def test_setup_bucket(self):
        config = S3Config(source=dict(S3_ACCESS_KEY='M8HHAKCPE0ISM2LL0E9X',
                                      S3_SECRET_KEY='dN9OjGDJUA54tDiAaBCIMxixEgf75CIcF3H60ZNn',
                                      S3_BUCKET_NAME='dev-bucket',
                                      S3_ENDPOINT_URL='https://teste-videos.us-east-1.linodeobjects.com/'))
        client = S3Client(config)

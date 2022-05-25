import unittest

from src.config.dotenv import load_dotenv
from src.repositories.s3_repository import Config, S3Client


class TestS3Repository(unittest.TestCase):

    def test_setup_bucket(self):
        # TODO: Remover teste 
        config = Config(source=dict(S3_ACCESS_KEY='M8HHAKCPE0ISM2LL0E9X',
                                    S3_SECRET_KEY='dN9OjGDJUA54tDiAaBCIMxixEgf75CIcF3H60ZNn',
                                    S3_BUCKET_NAME='dev-bucket',
                                    S3_ENDPOINT_URL='https://teste-videos.us-east-1.linodeobjects.com/'))
        client = S3Client(config)

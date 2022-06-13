import logging
import os

from src.config.dotenv import load_dotenv


class Config:

    def __init__(self, source: dict = os.environ):
        self.log = logging.getLogger(__name__)
        self._source = source
        self.setup()
        self.log.info('Config initialized')

    def setup(self):
        # S3 Setup
        self.access_key = self._getenv('S3_ACCESS_KEY')
        self.secret_key = self._getenv('S3_SECRET_KEY')
        self.bucket_name = self._getenv('S3_BUCKET_NAME')
        self.endpoint_url = self._getenv('S3_ENDPOINT_URL')

        if not self.endpoint_url.endswith('/'):
            self.endpoint_url += '/'
        self.endpoint_path_prefix = self._getenv(
            'S3_ENDPOINT_PATH_PREFIX', 'uploads/')
        if (self.endpoint_path_prefix and
                not self.endpoint_path_prefix.endswith('/')):
            self.endpoint_path_prefix += '/'

        # Website notification
        self.backend_url = self._getenv('BACKEND_URL', '')
        self.backend_auth = self._getenv('BACKEND_AUTH', '')

        # Upload
        self.max_upload_size = int(self._getenv('MAX_UPLOAD_SIZE', '52428800'))

        # CORS
        self.cors_origins = self._getenv('CORS_ORIGINS', '*').split(',')

        # Local Repository
        self.local_db = self._getenv(
            'LOCAL_DB', './wee-media-receiver.db')

        # HTTP Server
        self.http_port = int(self._getenv('HTTP_PORT', '8000'))

    def s3_to_dict(self) -> dict:
        return dict(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )

    def _getenv(self, key: str, default: str = None) -> str:
        value = self._source.get(key, default)
        if value is None:
            raise ValueError(f'{key} is not set')
        return value


def get_config() -> Config:
    load_dotenv()
    return Config()

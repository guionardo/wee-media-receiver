import logging
import os


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
        # Website notification
        self.backend_url = self._getenv('BACKEND_URL', '')
        # Database
        self.db_connectionstring = self._getenv('DB_CONNECTIONSTRING', '')

        # Upload
        self.max_upload_size = int(self._getenv('MAX_UPLOAD_SIZE', '52428800'))

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

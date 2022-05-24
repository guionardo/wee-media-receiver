from .base_config import BaseConfig


class S3Config(BaseConfig):

    def setup(self):
        self.access_key = self._getenv('S3_ACCESS_KEY')
        self.secret_key = self._getenv('S3_SECRET_KEY')
        self.bucket_name = self._getenv('S3_BUCKET_NAME')
        self.endpoint_url = self._getenv('S3_ENDPOINT_URL')

    def to_dict(self) -> dict:
        return dict(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=self.endpoint_url,
        )

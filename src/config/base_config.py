import logging
import os


class BaseConfig:

    def __init__(self, source: dict = os.environ):
        self.log = logging.getLogger(self.__class__.__name__)
        self._source = source
        self.setup()
        self.log.info('BaseConfig initialized')

    def setup(self):
        raise NotImplementedError(
            'Must implement setup() in subclass', __class__.__name__)

    def _getenv(self, key: str, default: str = None) -> str:
        value = self._source.get(key, default)
        if value is None:
            raise ValueError(f'{key} is not set')
        return value

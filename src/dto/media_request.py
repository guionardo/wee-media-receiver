import urllib.parse

import pydantic
from src.config.config import Config


class MediaRequestValidator:

    def __init__(self, url: str, config: Config):
        u = urllib.parse.urlparse(url)
        if not u.hostname:
            ucfg = urllib.parse.urlparse(config.endpoint_url)
            url = f'{ucfg.scheme}://{ucfg.netloc}/{config.endpoint_path_prefix}/{url}'
            u = urllib.parse.urlparse(url)
        self.url = url
        self.bucket_name = u.netloc.split('.')[0]
        self.s3_host = f'{u.scheme}://{u.netloc}/'
        paths = [p for p in u.path.split('/') if p]
        self.media_id = '/'.join(paths[1:])
        while self.media_id.startswith('/'):
            self.media_id = self.media_id[1:]
        self.media_id = self.media_id.replace('//', '/')
        if (not(bool(u.scheme) and
                bool(u.netloc) and
            bool(self.bucket_name) and
                bool(self.media_id))):
            raise ValueError(f'Invalid url: {url}')

    def __repr__(self) -> str:
        return f'<MediaRequest {self.media_id}>'


class MediaProcessRequest(pydantic.BaseModel):
    url: str
    post_id: int

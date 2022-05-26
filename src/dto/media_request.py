from urllib.parse import urlparse
from pydantic import BaseModel


class MediaRequestValidator:

    def __init__(self, url: str, path_prefix: str = '/uploads'):
        u = urlparse(url)
        self.url = url
        self.bucket_name = u.netloc.split('.')[0]
        self.s3_host = f'{u.scheme}://{u.netloc}/'
        self.media_id = u.path.replace(path_prefix, '')
        if not(bool(u.scheme) and bool(u.netloc) and bool(self.bucket_name) and bool(self.media_id)):
            raise ValueError(f'Invalid url: {url}')

    def __repr__(self) -> str:
        return f'<MediaRequest {self.media_id}>'


class MediaProcessRequest(BaseModel):
    url: str

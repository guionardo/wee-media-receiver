
from src.dto.media_status_enum import MediaStatusEnum


class FileMetadata:

    def __init__(self, metadata: dict):
        self.filename = metadata.get('wmr_filename')
        self.status = MediaStatusEnum[metadata.get('status')]

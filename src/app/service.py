from fastapi import UploadFile
from src.config.config import Config
from src.dto.media_status_enum import MediaStatusEnum
from src.dto.media_status_response import MediaStatusResponse
from src.repositories.s3_repository import S3Client


class MediaReceiverService:

    def __init__(self, config: Config, s3_client: S3Client = None):
        self.config = config
        self.s3_client = s3_client or S3Client(config)

    def receive_media(self, media_type: str, media_id: str) -> MediaStatusResponse:
        file_info = self.s3_client.get_file_info(media_id)

        return MediaStatusResponse(media_id=media_id, status=file_info)

    def upload_media(self, media_id: str, file: UploadFile, content_length: int) -> MediaStatusResponse:
        if self.s3_client.put_file(media_id, file, int(content_length)):
            return MediaStatusResponse(media_id=media_id, status=MediaStatusEnum.Accepted)

        return MediaStatusResponse(media_id=media_id, status=MediaStatusEnum.Rejected)

    def get_media_status(self, media_id: str) -> MediaStatusEnum:
        file_info = self.s3_client.get_file_info(media_id)

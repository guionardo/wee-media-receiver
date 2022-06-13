from fastapi import UploadFile
from src.app.s3_collection import S3Collection
from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import ScheduleWorker
from src.config.config import Config
from src.dto.app_status_response import AppStatusResponse
from src.dto.media_notification_response import MediaNotificationResponse
from src.dto.media_status_enum import MediaStatusEnum
from src.dto.media_status_response import MediaStatusResponse
from src.repositories.media_repository import get_repository


class MediaReceiverService:

    def __init__(self, config: Config,
                 schedule_worker: ScheduleWorker = None):
        self.config = config
        self.scheduler = schedule_worker or ScheduleWorker(config)

    def upload_media(self, media_id: str,
                     file: UploadFile) -> MediaStatusResponse:
        with S3Object(self.config, media_id) as s3_object:
            if s3_object.upload(file):
                return MediaStatusResponse(media_id=media_id,
                                           status=MediaStatusEnum.Accepted)

        return MediaStatusResponse(media_id=media_id,
                                   status=MediaStatusEnum.Rejected)

    def register_process_video(self, media_id: str, post_id: int) -> bool:
        with S3Object(self.config, media_id) as s3_object:
            if not s3_object.exists:
                return False
        self.scheduler.publish_event(
            'video', media_id=media_id, post_id=post_id)
        return True

    def get_app_index(self) -> AppStatusResponse:
        from src.app.setup import app
        repo = get_repository(self.config)
        status_count = repo.get_media_status_count()
        return AppStatusResponse(openapi_url=app.docs_url, status=status_count)

    def get_media_info(self, post_id: int) -> MediaNotificationResponse:
        repo = get_repository(self.config)
        media = repo.get_media_by_postid(post_id)
        if media:
            return MediaNotificationResponse(
                media_id=media.media_id,
                new_media_id=media.new_media_id,
                status=media.status.value,
                metadata={k: float(v) for k, v in media.category.items()},
                post_id=media.post_id)

    def get_storage_unprocessed(self):
        s3coll = S3Collection(self.config)
        return s3coll.get_unprocessed_objects()

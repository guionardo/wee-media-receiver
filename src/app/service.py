import logging
from typing import Tuple

from fastapi import UploadFile
from src.app.jobs import JobName
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
        self.log = logging.getLogger(self.__class__.__name__)

    def upload_media(self, media_id: str,
                     file: UploadFile) -> MediaStatusResponse:
        with S3Object(self.config, media_id) as s3_object:
            if s3_object.upload(file):
                return MediaStatusResponse(media_id=media_id,
                                           status=MediaStatusEnum.Accepted)

        return MediaStatusResponse(media_id=media_id,
                                   status=MediaStatusEnum.Rejected)

    def register_process_video(self, media_id: str, post_id: int) -> Tuple[bool, int, str]:
        try:
            with S3Object(self.config, media_id, keep_file=True) as s3_object:
                if s3_object.forbidden:
                    return False, 403, 'Forbidden'
                if not s3_object.exists:
                    return False, 404, 'Object not found'
                if s3_object.metadata and s3_object.metadata.get('wmr-status'):
                    return False, 409, f'Object already processed URL: /media/{post_id}'
                # if not s3_object.download():
                #     return False, 500, 'Download failed'

            self.scheduler.publish_event(JobName.Analysis.value,
                                         media_id=media_id,
                                         post_id=post_id,
                                         metadata=s3_object.metadata or {},
                                         filename=s3_object.filename())
            return True, 202, 'OK'
        except Exception as exc:
            self.log.error('Error registering video: %s', exc)
            return False, 400, str(exc)

    def get_app_index(self) -> AppStatusResponse:
        from src.app.setup import app
        repo = get_repository(self.config)
        status_count = repo.get_media_status_count()
        latest_media = []
        for media in repo.get_latest_media(10):
            latest_media.append(MediaNotificationResponse(
                media_id=media.media_id,
                new_media_id=media.new_media_id,
                status=media.status.value,
                metadata={k: float(v) for k, v in media.category.items()},
                post_id=media.post_id))
        # latest_media = [
        #     MediaNotificationResponse(media_id=media.media_id,
        #                               new_media_id=media.new_media_id,
        #                               status=media.status,
        #                               post_id=media.post_id,
        #                               metadata=media.category)
        #     for media in repo.get_latest_media(10)]
        return AppStatusResponse(openapi_url=app.docs_url,
                                 status=status_count,
                                 latest_media=latest_media,
                                 s3_url=self.config.endpoint_url)

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

    def get_storage_unprocessed(self, limit: int = 0, prefix: str = ''):
        s3coll = S3Collection(self.config)
        return s3coll.get_unprocessed_objects(limit, prefix)

    def get_storage_folders(self, prefix: str = ''):
        s3coll = S3Collection(self.config)
        return s3coll.get_storage_folders(prefix)


_service: MediaReceiverService = None


def set_service(service: MediaReceiverService):
    global _service
    _service = service


def get_service() -> MediaReceiverService:
    return _service

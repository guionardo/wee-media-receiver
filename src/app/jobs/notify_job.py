import datetime
import logging
import os

from src.app.backend_api import BackendAPI
from src.app.jobs import JobName
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_notification import MediaNotification
from src.dto.media_status_enum import MediaStatusEnum
from src.repositories.media_repository import MediaRepository


class NotifyJob(Job):

    def __init__(self):
        self._setup(JobName.Notify.value, 'media_id', 'post_id', 'metadata',
                    'new_media_id', 'filename', 'new_filename',
                    'content_metadata')
        self.log = logging.getLogger(self.__class__.__name__)

    def do_process(self, event, context: ScheduleContext) -> bool:
        (media_id, post_id, metadata, new_media_id,
         filename, new_filename, content_metadata) = self.get_event_fields(event)

        api = BackendAPI(context.config)
        if not api.is_available():
            return False

        context.repository.set_media(
            MediaData(post_id=post_id,
                      media_id=media_id,
                      category=content_metadata,
                      status=MediaStatusEnum.Notifying,
                      new_media_id=new_media_id))

        media_repository = MediaRepository(context.config)
        media_repository.set_media(
            MediaData(media_id=media_id,
                      media_path=filename,
                      new_media_path=new_filename))
        notification = MediaNotification(
            media_id, new_media_id, 'PROCESSED', post_id, metadata)
        if api.notify_backend(notification):
            # backend accepted the notification
            context.repository.set_media(
                MediaData(post_id=post_id,
                          media_id=media_id,
                          category=content_metadata,
                          status=MediaStatusEnum.Notified,
                          new_media_id=new_media_id))
            if os.path.isfile(filename):
                os.remove(filename)
            if os.path.isfile(new_filename):
                os.remove(new_filename)
            context.schedule.publish_event(
                JobName.RemoveVideo.value, media_id=media_id)
            return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

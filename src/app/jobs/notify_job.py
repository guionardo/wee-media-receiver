import datetime
import logging

from src.app.backend_api import BackendAPI
from src.app.jobs import JobName
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_notification import MediaNotification
from src.dto.media_status_enum import MediaStatusEnum


class NotifyJob(Job):

    def __init__(self):
        self._setup(JobName.Notify.value, 'media_id', 'post_id', 'metadata',
                    'new_media_id', 'content_metadata')
        self.log = logging.getLogger(self.__class__.__name__)

    def do_process(self, event, context: ScheduleContext) -> bool:
        (media_id, post_id, metadata,
         new_media_id, content_metadata) = self.get_event_fields(event)

        api = BackendAPI(context.config)
        if not api.is_available():
            return False

        update_media_id = new_media_id \
            if new_media_id and new_media_id != media_id \
            else media_id

        context.repository.set_media(MediaData(
            post_id=post_id,
            media_id=update_media_id,
            category=content_metadata,
            status=MediaStatusEnum.Notifying.value
        ))

        notification = MediaNotification(
            media_id, new_media_id, MediaStatusEnum.Processed.value,
            post_id, metadata)
        if not api.notify_backend(notification):
            return False

        # backend accepted the notification
        context.repository.set_media(
            MediaData(post_id=post_id,
                      media_id=update_media_id,
                      category=content_metadata,
                      status=MediaStatusEnum.Notified,
                      new_media_id=new_media_id))

        if new_media_id:
            context.schedule.publish_event(
                JobName.RemoveVideo.value, media_id=media_id)
        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

import datetime
import logging

from src.app.backend_api import BackendAPI
from src.app.jobs import JobName
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.dto.media_notification import MediaNotification
from src.dto.media_status_enum import MediaStatusEnum


class RenotifyJob(Job):

    def __init__(self):
        self._setup(JobName.Renotify.value)
        self.log = logging.getLogger(self.__class__.__name__)
        self.last_run = datetime.datetime(1970, 1, 1)

    def do_process(self, event, context: ScheduleContext) -> bool:
        if self.last_run + self.interval() > datetime.datetime.now():
            return True
        self.last_run = datetime.datetime.now()
        api = BackendAPI(context.config)
        if not api.is_available():
            return False

        unnotified = context.repository.get_unnotified_media(5)
        if not unnotified:
            return True

        for media in unnotified:
            notification = MediaNotification(
                media.media_id, media.new_media_id, 'PROCESSED', media.post_id, media.category)
            media.notification_sent += 1
            if api.notify_backend(notification):
                # backend accepted the notification
                media.status = MediaStatusEnum.Notified
                media.notification_accepted += 1
                if media.new_media_id != media.media_id:
                    context.schedule.publish_event(
                        JobName.RemoveVideo.value,
                        media_id=notification.media_id)

            context.repository.set_media(media)

            return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=10)

    def can_log(self) -> bool:
        return False

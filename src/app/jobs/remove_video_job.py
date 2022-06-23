import datetime
import logging

from src.app.jobs import JobName
from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import Job, ScheduleContext


class RemoveVideoJob(Job):

    def __init__(self):
        self._setup(JobName.RemoveVideo.value, 'media_id')
        self.log = logging.getLogger(self.__class__.__name__)

    def do_process(self, event, context: ScheduleContext) -> bool:
        (media_id,) = self.get_event_fields(event)

        with S3Object(context.config, media_id, keep_file=True) as s3_object:
            if not s3_object.exists:
                self.log.warning(
                    'File %s does not exist in S3', media_id)
            elif s3_object.delete():
                self.log.info('File %s deleted from S3', media_id)
            else:
                self.log.error('Failed to delete file %s from S3', media_id)
                return False

            return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

import datetime
import logging

from src.app.jobs import JobName
from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_status_enum import MediaStatusEnum


class RemoveVideoJob(Job):

    def __init__(self):
        self._setup(JobName.RemoveVideo.value, 'media_id')
        self.log = logging.getLogger(self.__class__.__name__)

    def do_process(self, event, context: ScheduleContext) -> bool:
        (media_id) = self.get_event_fields(event)

        with S3Object(context.config, media_id, keep_file=True) as s3_object:
            if not s3_object.exists:
                self.log.warning(
                    'File %s does not exist in S3', media_id)
            elif s3_object.delete():
                self.log.info('File %s deleted from S3', media_id)
            else:
                self.log.error('Failed to delete file %s from S3', media_id)
                return False

            context.repository.delete_media(media_id)

            return True
            context.repository.set_media(MediaData(
                post_id=post_id,
                media_id=media_id,
                status=MediaStatusEnum.Accepted))

            wmr_status = s3_object.metadata.get(
                'wmr-status', 'UNKNOWN')
            if wmr_status == 'OPTIMIZED':
                self.log.warning(
                    'File %s already processed: %s', media_id, wmr_status)
                context.repository.set_media(MediaData(
                    post_id=post_id,
                    media_id=media_id,
                    status=MediaStatusEnum.Done))
                return False

            self.log.info('Content analysing file %s', media_id)
            if not s3_object.download():
                return False
            context.repository.set_media(MediaData(
                post_id=post_id,
                media_id=media_id,
                media_path=s3_object.filename(),
                status=MediaStatusEnum.Downloaded))

            context.schedule.publish_event('analyze',
                                           media_id=media_id,
                                           post_id=post_id,
                                           filename=s3_object.filename(),
                                           metadata=s3_object.metadata)

        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

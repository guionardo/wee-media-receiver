import datetime
import logging

from src.analysis.model_processor import VideoAnalyzer
from src.app.jobs import JobName
from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_status_enum import MediaStatusEnum


class AnalysisJob(Job):

    def __init__(self):
        self._setup(JobName.Analysis.value,
                    'media_id', 'post_id', 'metadata')
        self.log = logging.getLogger(self.__class__.__name__)

    def do_process(self, event, context: ScheduleContext) -> bool:
        media_id, post_id, metadata = self.get_event_fields(event)

        self.log.info('Content analysing file %s', media_id)
        context.repository.set_media(MediaData(
            post_id=post_id,
            media_id=media_id,
            status=MediaStatusEnum.Downloading
        ))
        with S3Object(context.config, media_id, keep_file=True) as s3_object:
            if not s3_object.download():
                return False
            filename = s3_object.filename()

        context.repository.set_media(MediaData(
            post_id=post_id,
            media_id=media_id,
            media_path=filename,
            status=MediaStatusEnum.Analysing))
        video_response = VideoAnalyzer(media_id, filename)()
        if video_response:
            if not video_response.categories:
                self.log.warning(
                    'No categories found for %s', media_id)
                return False
            content_metadata = video_response.categories.values()
        else:
            content_metadata = dict()

        context.repository.set_media(MediaData(
            post_id=post_id,
            media_id=media_id,
            media_path=filename,
            category=content_metadata,
            status=MediaStatusEnum.Analysed))

        context.schedule.publish_event(
            JobName.Optimize.value, filename=filename,
            media_id=media_id, post_id=post_id, metadata=metadata,
            content_metadata=content_metadata)

        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

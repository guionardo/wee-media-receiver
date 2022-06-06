import datetime
import logging

from src.analysis.model_processor import VideoAnalyzer
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_status_enum import MediaStatusEnum


class AnalysisJob(Job):

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def can_process(self, event) -> bool:
        return event.get('type', '') == 'analyze' and event.get('filename') and event.get('media_id') and event.get('post_id') and event.get('metadata')

    def do_process(self, event, context: ScheduleContext) -> bool:
        filename, media_id, post_id, metadata = self.get_event_fields(
            event, 'filename', 'media_id', 'post_id', 'metadata')
        # filename, media_id, post_id, metadata = event.get('filename'), event.get(
        #     'media_id'), event.get('post_id'), event.get('metadata')
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

        context.schedule.publish_event('optimize', filename=filename, media_id=media_id,
                                       post_id=post_id, metadata=metadata, content_metadata=content_metadata)

        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

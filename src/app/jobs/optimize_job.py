import datetime
import logging

from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.app.video_optimizer import VideoOptimizer
from src.domain.media_data import MediaData
from src.dto.media_status_enum import MediaStatusEnum


class OptimizeJob(Job):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def can_process(self, event) -> bool:
        return event.get('type', '') == 'optimize' and event.get('filename') and event.get('media_id') and event.get('post_id') and event.get('metadata')

    def do_process(self, event, context: ScheduleContext) -> bool:
        filename, media_id, post_id, metadata, content_metadata = event.get('filename'), event.get(
            'media_id'), event.get('post_id'), event.get('metadata'), event.get('content_metadata', {})

        self.log.info('Processing video: %s', media_id)
        context.repository.set_media(MediaData(
            post_id=post_id,
            media_id=media_id,
            media_path=filename,
            category=content_metadata,
            status=MediaStatusEnum.Optimizing))

        with VideoOptimizer(media_id, filename, keep_temp=True) as video_optimizer:
            video_optimizer.run()
            context.repository.set_media(MediaData(
                post_id=post_id,
                media_id=media_id,
                media_path=filename,
                new_media_path=video_optimizer.new_file,
                category=content_metadata,
                status=MediaStatusEnum.Optimized,
                new_media_id=video_optimizer.new_media_id())
            )
            metadata['wmr-status'] = 'OPTIMIZED'

            context.schedule.publish_event('upload', filename=filename, new_filename=video_optimizer.new_file,
                                           media_id=media_id, post_id=post_id, metadata=metadata, content_metadata=content_metadata,
                                           new_media_id=video_optimizer.new_media_id())

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

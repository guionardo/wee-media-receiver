import datetime
import logging

from src.analysis.model_processor import VideoAnalyzer
from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.app.video_optimizer import VideoOptimizer


class VideoJob(Job):

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def can_process(self, event):
        return event.get('type', '') == 'video_' and event.get('media_id')

    def do_process(self, event, context: ScheduleContext) -> bool:
        media_id = event.get('media_id')

        with S3Object(context.config, media_id) as s3_object:
            if not s3_object.exists:
                self.log.warning(
                    'File %s does not exist in S3', media_id)
                return False
            wmr_status = s3_object.metadata.get(
                'wmr-status', 'UNKNOWN')
            if wmr_status == 'OPTIMIZED':
                self.log.warning(
                    'File %s already processed: %s', media_id, wmr_status)
                return False

            self.log.info('Content analysing file %s', media_id)
            if not s3_object.download():
                return False

            video_response = VideoAnalyzer(
                media_id, s3_object.filename())()
            if video_response:
                if not video_response.categories:
                    self.log.warning(
                        'No categories found for %s', media_id)
                    return False
                content_metadata = video_response.categories.values()
            else:
                content_metadata = dict()

            self.log.info('Processing video: %s', media_id)

            with VideoOptimizer(media_id, s3_object.filename()) as video_optimizer:
                video_optimizer.run()
                metadata = s3_object.metadata
                metadata['wmr-status'] = 'OPTIMIZED'
                metadata['wmr-source'] = media_id
                for key in content_metadata:
                    metadata['wmr-analisys-' +
                             key] = content_metadata[key]
                if video_optimizer.new_file:
                    with S3Object(self.config, video_optimizer.new_media_id()) as s3_object_new:
                        if s3_object_new.upload(
                                video_optimizer.new_file, **metadata):
                            self.log.info(
                                'Successfully uploaded optimized video: %s %s', video_optimizer.new_media_id(), metadata)
                else:
                    with S3Object(self.config, media_id) as s3_object_update:
                        if s3_object_update.upload(s3_object.filename(), **metadata):
                            self.log.info(
                                'Successfully updated video: %s %s', media_id, metadata)

                    self.log.info(
                        'Video already optimized: %s', media_id)

        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

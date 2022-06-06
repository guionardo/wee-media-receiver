import datetime
import logging
import os

from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_status_enum import MediaStatusEnum


class UploadJob(Job):
    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def can_process(self, event) -> bool:
        return event.get('type', '') == 'upload' and event.get('filename') and event.get('media_id') and event.get('post_id') and event.get('metadata')

    def do_process(self, event, context: ScheduleContext) -> bool:
        filename, new_filename,        media_id, post_id, metadata, content_metadata, new_media_id = event.get('filename'), event.get(
            'new_filename'), event.get('media_id'), event.get('post_id'), event.get('metadata'), event.get('content_metadata', {}), event.get('new_media_id')

        context.repository.set_media(MediaData(
            post_id=post_id,
            media_id=media_id,
            media_path=filename,
            new_media_path=new_filename,
            category=content_metadata,
            status=MediaStatusEnum.Uploading,
            new_media_id=new_media_id)
        )
        metadata['wmr-source'] = media_id
        for key in content_metadata:
            metadata['wmr-analisys-' +
                     key] = content_metadata[key]
        if new_filename:
            with S3Object(context.config, new_media_id) as s3_object_new:
                if s3_object_new.upload(
                        new_filename, **metadata):
                    self.log.info(
                        'Successfully uploaded optimized video: %s %s', new_media_id, metadata)

                else:
                    return False
        else:
            with S3Object(context.config, media_id) as s3_object_update:
                if s3_object_update.upload(filename, **metadata):
                    self.log.info(
                        'Successfully updated video: %s %s', media_id, metadata)
                else:
                    return False
        if os.path.isfile(filename):
            os.remove(filename)
        if os.path.isfile(new_filename):
            os.remove(new_filename)

        context.repository.set_media(
            MediaData(post_id=post_id,
                      media_id=media_id,
                      category=content_metadata,
                      status=MediaStatusEnum.Uploaded,
                      new_media_id=new_media_id))

        context.schedule.publish_event(
            'notify', media_id=media_id, post_id=post_id, metadata=metadata, new_media_id=new_media_id, content_metadata=content_metadata)
        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

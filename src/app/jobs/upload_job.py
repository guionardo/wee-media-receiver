import datetime
import logging
import os

from src.app.jobs import JobName
from src.app.s3_object import S3Object
from src.app.schedule.schedule_worker import Job, ScheduleContext
from src.domain.media_data import MediaData
from src.dto.media_status_enum import MediaStatusEnum


class UploadJob(Job):
    def __init__(self):
        self._setup(JobName.Upload.value, 'filename', 'new_filename',
                    'media_id', 'post_id', 'metadata', 'content_metadata',
                    'new_media_id')
        self.log = logging.getLogger(self.__class__.__name__)

    def do_process(self, event, context: ScheduleContext) -> bool:
        (filename, new_filename, media_id, post_id, metadata,
         content_metadata, new_media_id) = self.get_event_fields(event)

        content_metadata = content_metadata or dict()
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
        metadata.update({'wmr_analisys-'+key: content_metadata[key]
                         for key in content_metadata})

        if new_filename:
            with S3Object(context.config, new_media_id) as s3_object_new:
                if not s3_object_new.upload(
                        new_filename, **metadata):
                    return False
                self.log.info('Successfully uploaded optimized video: %s %s',
                              new_media_id, metadata)

        else:
            with S3Object(context.config, media_id) as s3_object_update:
                if not s3_object_update.set_metadata(metadata, True):
                    return False

                # if s3_object_update.upload(filename, **metadata):
                self.log.info('Successfully updated video: %s %s',
                              media_id, metadata)

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
            JobName.Notify.value, media_id=media_id, post_id=post_id,
            metadata=metadata, new_media_id=new_media_id,
            content_metadata=content_metadata,
            new_filename=new_filename,
            filename=filename)
        return True

    def interval(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=0)

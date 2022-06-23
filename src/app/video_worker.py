import logging
import os
import tempfile
import threading
from queue import Empty, Queue
from typing import Tuple

import filetype
from src.analysis.model_processor import VideoAnalyzer
from src.app.s3_object import S3Object
from src.app.video_optimizer import VideoOptimizer, optimize_video
from src.config.config import Config

q = Queue()


class VideoWorker:

    def __init__(self, config: Config):
        self.config = config
        # self.s3_client = s3_client
        self.can_run = False
        self.log = logging.getLogger(__name__)

    def add_received_file(self, media_id: str) -> bool:
        with S3Object(self.config, media_id) as s3_object:
            if not s3_object.exists:
                return False
        q.put(media_id, block=True)
        self.log.info('Added file to queue: %s (total enqueued=%d)',
                      media_id, q.qsize())
        return True

    def start(self):
        self.can_run = True
        t = threading.Thread(target=self.process_queue,
                             name='VideoWorker', daemon=True, kwargs=dict(q=q))
        self.log.info('VideoWorker starting - queue %x', id(q))
        t.start()

    def stop(self):
        self.can_run = False
        self.log.info('VideoWorker is stopping')

    def process_queue(self, **kwargs):
        queue = kwargs.get('q')
        self.log.info('VideoWorker started - queue')
        while self.can_run:
            try:
                media_id = queue.get(block=True, timeout=2)
                with S3Object(self.config, media_id) as s3_object:
                    if not s3_object.exists:
                        self.log.warning(
                            'File %s does not exist in S3', media_id)
                        continue

                    wmr_status = s3_object.metadata.get(
                        'wmr-status', 'UNKNOWN')
                    if wmr_status == 'OPTIMIZED':
                        self.log.warning(
                            'File %s already processed: %s', media_id, wmr_status)
                        continue

                    self.log.info('Content analysing file %s', media_id)
                    if not s3_object.download():
                        continue

                    video_response = VideoAnalyzer(
                        media_id, s3_object.filename())()
                    if video_response:
                        if not video_response.categories:
                            self.log.warning(
                                'No categories found for %s', media_id)
                            continue
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

            except Empty:
                ...

        self.log.info('VideoWorker stopped')

    def optimize_video(self, media_id: str, tmp_file: str) -> Tuple[str, str, bool]:
        """Optimize video to webm, returning new media_id, new temporary file and success"""
        self.log.info('Processing video: %s', media_id)
        with tempfile.NamedTemporaryFile("w+", delete=False) as file:
            with S3Object(self.config, media_id) as s3_object:
                if not s3_object.download():
                    self.log.error('Failed to download file %s', media_id)
                    return '', '', False

                s3_object.filename()
            if not self.s3_client.download_file(media_id, file.name):
                ...
            if not self.check_filetype_video(file.name):
                return '', '', False
            self.log.info('Optimizing video: %s', media_id)
            output_file, success = optimize_video(file.name, media_id)
            if not success:
                self.log.error('Failed to optimize video %s', media_id)
                return '', file.name, False
            start_size = os.path.getsize(file.name)
            end_size = os.path.getsize(output_file)
            if end_size > start_size:
                self.log.info('Optimization not needed: %s', media_id)
                return media_id, file.name, True
            else:
                self.log.info('Optimized video: %s (%d -> %d) = %d%%', output_file,
                              start_size, end_size, (end_size-start_size)/start_size*100)
                root, _ = os.path.splitext(media_id)
                return root+'.webm', output_file, True

    def check_filetype_video(self, filename: str) -> bool:
        try:
            kind = filetype.guess(filename)
            if filetype.is_video(filename):
                self.log.info('Detected video file %s', kind)
                return True
            self.log.warning('Invalid filetype: %s', kind)
        except Exception as exc:
            self.log.error(
                'Exception reading filetype: %s', exc)
        return False

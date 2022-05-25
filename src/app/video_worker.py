import logging
import os
import tempfile
import threading
from queue import Empty, Queue

import filetype
from src.app.video_optimizer import optimize_video
from src.config.config import Config
from src.repositories.s3_repository import S3Client

q = Queue()


class VideoWorker:

    def __init__(self, config: Config, s3_client: S3Client):
        self.config = config
        self.s3_client = s3_client        
        self.can_run = False
        self.log = logging.getLogger(__name__)

    def add_received_file(self, media_id: str) -> bool:
        if not self.s3_client.file_exists(media_id):
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
                self.process_video(media_id)
            except Empty:
                ...

        self.log.info('VideoWorker stopped')

    def process_video(self, media_id: str):
        self.log.info('Processing video: %s', media_id)
        with tempfile.NamedTemporaryFile("w+", delete=True) as file:
            if not self.s3_client.download_file(media_id, file.name):
                self.log.error('Failed to download file %s', media_id)
                return
            if not self.check_filetype_video(file.name):
                return
            self.log.info('Optimizing video: %s', media_id)
            output_file, success = optimize_video(file.name, media_id)
            if not success:
                self.log.error('Failed to optimize video %s', media_id)
                return
            start_size = os.path.getsize(file.name)
            end_size = os.path.getsize(output_file)
            if end_size > start_size:
                self.log.info('Optimization not needed: %s', media_id)
            else:
                self.log.info('Optimized video: %s (%d -> %d) = %d%%', output_file,
                              start_size, end_size, (end_size-start_size)/start_size*100)

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

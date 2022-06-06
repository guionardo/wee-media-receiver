# https://trac.ffmpeg.org/wiki/Encode/VP9

# ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 0 -crf 30 -pass 1 -an -f null /dev/null && \
# ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 0 -crf 30 -pass 2 -c:a libopus output.webm
import asyncio
import datetime
import logging
import os
import tempfile
from time import time
from typing import Tuple

from ffmpeg import FFmpeg


class VideoOptimizer:

    def __init__(self, media_id: str, filename: str, keep_temp: bool = False):
        if not os.path.isfile(filename):
            raise FileNotFoundError(filename)
        self.media_id = media_id
        self.filename = filename
        self.log = logging.getLogger(self.__class__.__name__)

        self.output = tempfile.NamedTemporaryFile(
            suffix='.output.webm',
            prefix=os.path.basename(filename),
            delete=not keep_temp)

        self.new_file = ''
        self.message = ''
        self.elapsed_time = datetime.timedelta(seconds=0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self.log.error('Exit with error: %s', exc_val)
        self.output.close()

    def __str__(self):
        return f'{self.media_id} ({self.filename})'

    def new_media_id(self) -> str:
        if not self.new_file:
            return self.media_id

        current_root, current_ext = os.path.splitext(self.media_id)
        _, new_ext = os.path.splitext(self.new_file)

        if current_ext == new_ext:
            # same extension, optimized
            return os.path.join(current_root+'.optimized', new_ext)

        return current_root + current_ext + new_ext

    def run(self):
        try:
            start_time = time()

            async def run():
                await self._create_ffmpeg(1).execute()
                await self._create_ffmpeg(2).execute()
            asyncio.run(run())
            self.elapsed_time = datetime.timedelta(
                seconds=time()-start_time)

            source_len = os.path.getsize(self.filename)
            output_len = os.path.getsize(self.output.name)
            if output_len < source_len:
                self.new_file = self.output.name
                self.message = f'Video optimized: {self.media_id} ({source_len} -> {output_len} {(output_len-source_len)/source_len*100:1f}%)'
            else:
                self.message = f'Video not optimized: {self.media_id} ({source_len} -> {output_len} {(output_len-source_len)/source_len*100:1f}%)'

        except Exception as e:
            self.message = f'Failed to optimize video: {self.media_id} ({self.filename}): {e}'

    def _create_ffmpeg(self, pass_no: int) -> FFmpeg:
        ff = FFmpeg().option('y').input(self.filename)
        if pass_no == 1:
            desc = 'Pass#1'
            ff = ff.option('an')\
                .output('/dev/null', {
                    'c:v': 'libvpx-vp9',
                    'b:v': '0',
                    'crf': '30',
                    'pass': '1',
                    'f': 'null'})
        else:
            desc = 'Pass#2'
            ff = ff.output(self.output.name, {
                '-c:v': 'libvpx-vp9',
                '-b:v': '0',
                '-crf': '30',
                '-pass': '2',
                '-c:a': 'libopus'})

        ff.on('start', lambda args: self.log.info(
            'Started %s (%s) %s', desc, self.media_id, args))
        ff.on('stderr', lambda line: self.log.debug('stderr: %s', line))
        ff.on('progress', lambda progress: self.log.info('%s', progress))
        ff.on('completed', lambda: self.log.info(
            'Completed %s [%s]', desc, self.media_id))
        ff.on('error', lambda args: self.log.error('Error %s %s', desc, args))
        ff.on('terminated', lambda: self.log.info('Terminated %s', desc))
        return ff


def _logging(ff: FFmpeg, log: logging.Logger, desc: str, media_id: str):
    ff.on('start', lambda args: log.info(
        'Started %s (%s) %s', desc, media_id, args))
    ff.on('stderr', lambda line: log.debug('stderr: %s', line))
    ff.on('progress', lambda progress: log.info('%s', progress))
    ff.on('completed', lambda: log.info('Completed %s [%s]', desc, media_id))
    ff.on('error', lambda args: log.error('Error %s %s', desc, args))
    ff.on('terminated', lambda: log.info('Terminated %s', desc))


def _first_pass(filename: str, media_id: str, log: logging.Logger) -> FFmpeg:
    ff = FFmpeg().option('y')\
        .input(filename)\
        .option('an')\
        .output('/dev/null', {
            'c:v': 'libvpx-vp9',
            'b:v': '0',
            'crf': '30',
            'pass': '1',
            'f': 'null'})
    _logging(ff, log, 'first pass', media_id)
    return ff


def _second_pass(filename: str, media_id: str, output: str, log: logging.Logger) -> FFmpeg:
    ff = FFmpeg().option('y')\
        .input(filename)\
        .output(output, {
            '-c:v': 'libvpx-vp9',
            '-b:v': '0',
            '-crf': '30',
            '-pass': '2',
            '-c:a': 'libopus'})
    _logging(ff, log, 'second pass', media_id)
    return ff


def optimize_video(filename: str, media_id: str, output_file=None) -> Tuple[str, bool]:
    filename = os.path.abspath(filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    if not output_file:
        if filename.startswith(tempfile.gettempdir()):
            output_file = tempfile.NamedTemporaryFile(suffix='.webm').name
        else:
            root, _ = os.path.splitext(filename)
            output_file = root + '.webm'
    log = logging.getLogger(__name__)

    fp = _first_pass(filename, media_id, log)
    sp = _second_pass(filename, media_id, output_file, log)

    async def run():
        await fp.execute()
        await sp.execute()

    asyncio.run(run())
    return output_file, os.path.isfile(output_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with VideoOptimizer('123', './olha.mp4') as v:
        v.run()
        print(v.new_file)
        print(v.message)
    # print(optimize_video('./olha.mp4'))

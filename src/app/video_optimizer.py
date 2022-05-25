# https://trac.ffmpeg.org/wiki/Encode/VP9

# ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 0 -crf 30 -pass 1 -an -f null /dev/null && \
# ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 0 -crf 30 -pass 2 -c:a libopus output.webm
import asyncio
import logging
import os
import tempfile
from typing import Tuple

from ffmpeg import FFmpeg


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


def optimize_video(filename: str, media_id: str) -> Tuple[str, bool]:
    filename = os.path.abspath(filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

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
    print(optimize_video('./olha.mp4'))

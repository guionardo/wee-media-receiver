import glob
import os
from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel
from src import __description__, __version__
from src.dto.media_notification_response import MediaNotificationResponse


def get_last_update() -> datetime:
    src = os.path.abspath('.')
    lu = 0
    for f in glob.iglob(os.path.join(src, '**', '*.py'), recursive=True):
        fu = os.path.getmtime(f)
        if fu > lu:
            lu = fu
    return datetime.fromtimestamp(lu)


def get_release_timestamp() -> datetime:
    release_file = os.path.abspath('./release.txt')
    try:
        with open(release_file, 'r') as f:
            return datetime.strptime(f.read(), '%Y-%m-%dT%H:%M:%SZ')
    except:
        return datetime.now()


last_update = get_last_update()
release_timestamp = get_release_timestamp()
started_time = datetime.now()


class AppStatusResponse(BaseModel):
    title: str = __description__
    debug: bool = False
    version: str = __version__
    openapi_url: str
    status: Dict[str, int]
    last_update: datetime = last_update
    release: datetime = release_timestamp
    started_time: datetime = started_time
    s3_url: str
    latest_media: List[MediaNotificationResponse] = []

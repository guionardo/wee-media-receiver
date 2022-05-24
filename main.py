"""Main entry"""

from pathlib import Path

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Request, UploadFile

from src import __appname__, __description__, __version__
from src.app.service import MediaReceiverService
from src.config.config import Config
from src.dto.media_status_enum import MediaStatusEnum
from src.dto.media_status_response import MediaStatusResponse
from src.logging.custom_logging import CustomizeLogger
from src.middlewares.limit_upload_size import LimitUploadSize

config = Config(source=dict(S3_ACCESS_KEY='M8HHAKCPE0ISM2LL0E9X',
                            S3_SECRET_KEY='dN9OjGDJUA54tDiAaBCIMxixEgf75CIcF3H60ZNn',
                            S3_BUCKET_NAME='teste-videos',
                            S3_ENDPOINT_URL='https://teste-videos.us-east-1.linodeobjects.com/'))

app_config = dict(
    title=__description__,
    debug=True,
    version="0.0.1",
)

app = FastAPI(**app_config)
app.logger = CustomizeLogger.make_logger(
    Path('src/logging/logging_config.json'))

app.add_middleware(LimitUploadSize, max_upload_size=config.max_upload_size)
service = MediaReceiverService(config)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/media/{media_type}/{media_id}', response_model=MediaStatusResponse)
async def receive_media(media_type: str, media_id: str):
    return service.receive_media(media_type, media_id)


@app.post('/media/{media_id}', response_model=MediaStatusResponse)
async def upload_media(file: UploadFile, media_id: str, background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(
        service.upload_media, media_id, file, request.headers.get('content-length'))
    return MediaStatusResponse(media_id=media_id, status=MediaStatusEnum.Accepted)


@app.get('/media/{media_id}')
async def get_media(media_id: str):
    return {"media_id": media_id}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

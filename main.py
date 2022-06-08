"""Main entry"""

import sys
from pathlib import Path

import uvicorn
from fastapi import (BackgroundTasks, FastAPI, Request, Response, UploadFile,
                     status)
from fastapi.middleware.cors import CORSMiddleware

from src import __appname__, __description__, __version__
from src.app.jobs.analysis_job import AnalysisJob
from src.app.jobs.notify_job import NotifyJob
from src.app.jobs.optimize_job import OptimizeJob
from src.app.jobs.receive_video_job import ReceiveVideoJob
from src.app.jobs.renotify_job import RenotifyJob
from src.app.jobs.upload_job import UploadJob
from src.app.schedule.schedule_worker import ScheduleWorker
from src.app.service import MediaReceiverService
from src.app.stop_control import StopControl
from src.config.config import Config
from src.config.dotenv import load_dotenv
from src.dto.media_request import MediaProcessRequest, MediaRequestValidator
from src.dto.media_status_enum import MediaStatusEnum
from src.dto.media_status_response import MediaStatusResponse
from src.dto.video_receive_response import VideoReceiveResponse
from src.logging.custom_logging import CustomizeLogger
from src.middlewares.limit_upload_size import LimitUploadSize

stop_control = StopControl()

load_dotenv()
config = Config()

app_config = dict(
    title=__description__,
    debug=True,
    version=__version__,
)

app = FastAPI(**app_config)
app.logger = CustomizeLogger.make_logger(
    Path('src/logging/logging_config.json'))

app.add_middleware(LimitUploadSize, max_upload_size=config.max_upload_size)
if config.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

scheduler = ScheduleWorker(config, stop_control)
scheduler.add_job(ReceiveVideoJob())
scheduler.add_job(NotifyJob())
scheduler.add_job(AnalysisJob())
scheduler.add_job(OptimizeJob())
scheduler.add_job(UploadJob())
scheduler.add_job(RenotifyJob())


service = MediaReceiverService(config, stop_control=stop_control)


@app.on_event("startup")
async def startup():
    # if 'stop' in sys.argv:
    #     stop_control.stop()
    #     exit(0)
    # if not stop_control.can_start():        
    #     app.logger.error('Cannot start the server. Instance already running.')
    #     exit(1)
    
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.stop()
    # del(stop_control)


@app.get("/")
async def root():
    return app_config


# @app.post('/media/{media_type}/{media_id}', response_model=MediaStatusResponse)
# async def receive_media(media_type: str, media_id: str):
#     return service.receive_media(media_type, media_id)


@app.post('/media', response_model=MediaStatusResponse)
async def upload_media(file: UploadFile, media_id: str, background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(
        service.upload_media, media_id, file, request.headers.get('content-length'))
    return MediaStatusResponse(media_id=media_id, status=MediaStatusEnum.Accepted)


@app.post('/video', response_model=VideoReceiveResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_video(media_request: MediaProcessRequest, response: Response):
    try:
        request = MediaRequestValidator(media_request.url)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return VideoReceiveResponse(media_id=request.media_id, status=MediaStatusEnum.Rejected, message=str(e))

    media_id = request.media_id

    if request.s3_host != config.endpoint_url:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return VideoReceiveResponse(media_id=media_id, status=MediaStatusEnum.Rejected, message='Invalid S3 host')

    if request.bucket_name != config.bucket_name:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return VideoReceiveResponse(media_id=media_id, status=MediaStatusEnum.Rejected, message='Invalid S3 bucket')

    if not service.register_process_video(media_id, media_request.post_id):
        response.status_code = status.HTTP_404_NOT_FOUND
        return VideoReceiveResponse(media_id=media_id, message="NOT FOUND")
    return VideoReceiveResponse(media_id=media_id, message="ACCEPTED")


if __name__ == '__main__':
    if 'stop' in sys.argv:
        stop_control.stop()
        exit(0)
    if not stop_control.can_start():
        app.logger.error('Cannot start the server. Instance already running.')
        exit(1)
    uvicorn.run(app, host='0.0.0.0', port=8000)
    del(stop_control)

import logging
import os
from pathlib import Path

import src.app.api.media as media_api
import src.app.api.stats as stats_api
import src.app.api.storage as storage_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src import __appname__, __description__, __version__
from src.app.service import MediaReceiverService, set_service
from src.app.setup_scheduler import get_scheduler
from src.config.config import get_config
from src.logging.custom_logging import CustomizeLogger
from src.middlewares.limit_upload_size import LimitUploadSize

config = get_config()
scheduler = get_scheduler(config)
service = MediaReceiverService(config)
set_service(service)

app_config = dict(
    title=__description__,
    debug=True,
    version=__version__,
    contact=dict(
        name='Guionardo Furlan',
        email='guionardo@gmail.com'
    )
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

app.include_router(media_api.router)
app.include_router(storage_api.router)
app.include_router(stats_api.router)

static_folder = os.path.abspath('./static')
if os.path.isdir(static_folder):
    app.mount('/ui', StaticFiles(directory=static_folder,
              html=True), name='static')


@app.on_event("startup")
async def startup():
    logging.info('Starting %s v%s', __appname__, __version__)
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.stop()


# @app.get("/stats", response_model=AppStatusResponse)
# async def stats():
#     return service.get_app_index()


# @app.get('/storage/unprocessed', response_model=List[str])
# async def get_storage_unprocessed():
#     return service.get_storage_unprocessed()


# @app.get('/media/{post_id}', response_model=MediaNotificationResponse)
# async def get_media_info(post_id: int, response: Response):
#     media_info = service.get_media_info(post_id)
#     if not media_info:
#         response.status_code = status.HTTP_404_NOT_FOUND
#     else:
#         return media_info


# @app.post('/media', response_model=MediaStatusResponse)
# async def upload_media(file: UploadFile, media_id: str,
#                        background_tasks: BackgroundTasks, request: Request):
#     background_tasks.add_task(
#         service.upload_media, media_id, file)
#     return MediaStatusResponse(media_id=media_id,
#                                status=MediaStatusEnum.Accepted)


# @app.post('/video', response_model=VideoReceiveResponse,
#           status_code=status.HTTP_202_ACCEPTED)
# async def process_video(media_request: MediaProcessRequest,
#                         response: Response):
#     """Processamento de vídeo no S3

#     Retornará um código 202 Accepted caso o vídeo seja aceito.

#     """
#     try:
#         request = MediaRequestValidator(media_request.url, config)
#     except Exception as e:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return VideoReceiveResponse(media_id=media_request.url,
#                                     post_id=media_request.post_id,
#                                     status=MediaStatusEnum.Rejected,
#                                     message=str(e))

#     media_id = request.media_id

#     if request.s3_host != config.endpoint_url:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return VideoReceiveResponse(media_id=media_id,
#                                     post_id=media_request.post_id,
#                                     status=MediaStatusEnum.Rejected,
#                                     message='Invalid S3 host')

#     if request.bucket_name != config.bucket_name:
#         response.status_code = status.HTTP_400_BAD_REQUEST
#         return VideoReceiveResponse(media_id=media_id,
#                                     post_id=media_request.post_id,
#                                     status=MediaStatusEnum.Rejected,
#                                     message='Invalid S3 bucket')

#     success, code, msg = service.register_process_video(
#         media_id, media_request.post_id)
#     if not success:
#         response.status_code = code
#         return VideoReceiveResponse(media_id=media_id,
#                                     post_id=media_request.post_id,
#                                     message=msg)
#     return VideoReceiveResponse(media_id=media_id,
#                                 post_id=media_request.post_id,
#                                 message="ACCEPTED")

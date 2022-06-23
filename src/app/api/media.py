from fastapi import APIRouter, BackgroundTasks, Response, UploadFile, status
from src.app.service import get_service
from src.config.config import get_config
from src.dto.media_notification_response import MediaNotificationResponse
from src.dto.media_request import MediaProcessRequest, MediaRequestValidator
from src.dto.media_status_enum import MediaStatusEnum
from src.dto.media_status_response import MediaStatusResponse
from src.dto.video_receive_response import VideoReceiveResponse

router = APIRouter(prefix='/media', tags=['media'])
config = get_config()


@router.get('/{post_id}', response_model=MediaNotificationResponse)
async def get_media_info(post_id: int, response: Response):
    """Media info from post"""
    media_info = get_service().get_media_info(post_id)
    if not media_info:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        return media_info


@router.post('/upload', response_model=MediaStatusResponse)
async def upload_media(file: UploadFile, media_id: str,
                       background_tasks: BackgroundTasks):
    background_tasks.add_task(
        get_service().upload_media, media_id, file)
    return MediaStatusResponse(media_id=media_id,
                               status=MediaStatusEnum.Accepted)


@router.post('/process', response_model=VideoReceiveResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def process_media(media_request: MediaProcessRequest,
                        response: Response):
    """Processamento de vídeo no S3

    Retornará um código 202 Accepted caso o vídeo seja aceito.

    """
    try:
        request = MediaRequestValidator(media_request.url, config)
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return VideoReceiveResponse(media_id=media_request.url,
                                    post_id=media_request.post_id,
                                    status=MediaStatusEnum.Rejected,
                                    message=str(e))

    media_id = request.media_id

    if request.s3_host != config.endpoint_url:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return VideoReceiveResponse(media_id=media_id,
                                    post_id=media_request.post_id,
                                    status=MediaStatusEnum.Rejected,
                                    message='Invalid S3 host')

    if request.bucket_name != config.bucket_name:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return VideoReceiveResponse(media_id=media_id,
                                    post_id=media_request.post_id,
                                    status=MediaStatusEnum.Rejected,
                                    message='Invalid S3 bucket')

    success, code, msg = get_service().register_process_video(
        media_id, media_request.post_id)
    if not success:
        response.status_code = code
        return VideoReceiveResponse(media_id=media_id,
                                    post_id=media_request.post_id,
                                    message=msg)
    return VideoReceiveResponse(media_id=media_id,
                                post_id=media_request.post_id,
                                message="ACCEPTED")

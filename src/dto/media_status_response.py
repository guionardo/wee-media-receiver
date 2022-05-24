from pydantic import BaseModel

from src.dto.media_status_enum import MediaStatusEnum


class MediaStatusResponse(BaseModel):

    media_id: str
    status: MediaStatusEnum

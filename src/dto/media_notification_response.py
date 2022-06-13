from pydantic import BaseModel


class MediaNotificationResponse(BaseModel):
    """Dados enviados ao backend sobre a mídia processada"""
    media_id: str
    new_media_id: str
    status: str
    post_id: int
    metadata: dict

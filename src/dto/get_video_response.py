"""Video Data Response"""

from typing import Optional

from pydantic import BaseModel
from src.dto.video_categories import VideoCategory


class GetVideoResponse(BaseModel):
    """Video Data Model"""

    video_id: Optional[str]
    categories: Optional[VideoCategory]
    message: Optional[str]
    processing_time: Optional[float]

    def __str__(self) -> str:
        return f'{self.video_id} [{self.message}] ({self.processing_time}s): {self.categories}'

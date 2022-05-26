from pydantic import BaseModel


class VideoCategory(BaseModel):
    drawings: float = 0.0
    hentai: float = 0.0
    neutral: float = 0.0
    porn: float = 0.0
    sexy: float = 0.0

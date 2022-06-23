from pydantic import BaseModel


class VideoReceiveResponse(BaseModel):

    media_id: str
    post_id: int
    message: str

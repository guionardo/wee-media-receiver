from pydantic import BaseModel


class VideoReceiveResponse(BaseModel):
   
    media_id: str
    message: str

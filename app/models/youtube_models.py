from pydantic import BaseModel

class VideoIDResponse(BaseModel):
    video_id: str

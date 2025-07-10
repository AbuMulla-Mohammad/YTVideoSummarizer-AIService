from pydantic import BaseModel

class VideoIDResponse(BaseModel):
    video_id: str
class TranscriptRequest(BaseModel):
    video_url: str
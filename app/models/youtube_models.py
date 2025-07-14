from pydantic import BaseModel

class VideoIDResponse(BaseModel):
    video_id: str
class TranscriptRequest(BaseModel):
    video_url: str

class TranscriptTextResponse(BaseModel):
    video_id: str
    text: str
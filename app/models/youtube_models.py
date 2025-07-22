from pydantic import BaseModel
from app.models.ai_result_models import VideoSummaryTranscriptResponse

class VideoIDResponse(BaseModel):
    video_id: str
class TranscriptRequest(BaseModel):
    video_url: str

class TranscriptTextResponse(BaseModel):
    video_id: str
    text: str
class SummarizeFormatTranscriptRequest(BaseModel):
    video_url: str
    prompt_type: str = "friendly_summary_with_emojis_and_ideas_explenation" 
    text_with_timestamp: str | None = None
    model: str = "command-a-03-2025"

class SummarizeFormatTranscriptResponse(VideoSummaryTranscriptResponse):
    pass
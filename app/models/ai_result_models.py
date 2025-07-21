from pydantic import BaseModel


class SummarySectionResponse(BaseModel):
    title: str
    summary: str
    start: float
    end: float


class FormatedTranscriptResponse(BaseModel):
    title: str
    text: str
    start: float
    end: float


class VideoSummaryTranscriptResponse(BaseModel):
    summary_sections: list[SummarySectionResponse]
    formatted_transcript: list[FormatedTranscriptResponse]
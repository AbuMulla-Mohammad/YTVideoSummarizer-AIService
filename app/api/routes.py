from fastapi import APIRouter, HTTPException
from app.utils import (
    extract_video_id,
    get_video_transcript,
    convert_transcript_to_text,
    summarize_format_text,
)
from app.models.youtube_models import (
    VideoIDResponse,
    TranscriptRequest,
    TranscriptTextResponse,
    SummarizeFormatTranscriptRequest,
)
from app.prompts import PROMPT_MAP

router = APIRouter()


@router.post("/get_video_id", response_model=VideoIDResponse)
async def get_video_id(url: str):

    video_id = extract_video_id(url)
    if "error" in video_id:
        raise HTTPException(status_code=400, detail=video_id["error"])
    return {"video_id": video_id}


@router.post("/get_video_transcript")
async def fetch_transcript(request: TranscriptRequest):
    transcript = await get_video_transcript(request.video_url)
    if "error" in transcript:
        raise HTTPException(status_code=400, detail=transcript["error"])
    return {"transcript": transcript}


@router.post("/convert_transcript_text_endpoint")
async def convert_transcript_text_endpoint(
    request: TranscriptRequest, response_model=TranscriptTextResponse
):
    video_id = extract_video_id(request.video_url)
    if "error" in video_id:
        raise HTTPException(status_code=400, detail=video_id["error"])
    transcript = await get_video_transcript(request.video_url)

    if "error" in transcript:
        raise HTTPException(status_code=400, detail=transcript["error"])
    text = await convert_transcript_to_text(transcript)
    if "error" in text:
        raise HTTPException(status_code=400, detail=text["error"])
    return TranscriptTextResponse(video_id=video_id, text=text["text"])


@router.post("/summarize_format_transcript")
async def summarize_format_transcript(request: SummarizeFormatTranscriptRequest):
    print("Summarizeing")
    video_id = extract_video_id(request.video_url)
    if "error" in video_id:
        raise HTTPException(status_code=400, detail=video_id["error"])
    transcript = await get_video_transcript(request.video_url)
    if "error" in transcript:
        raise HTTPException(status_code=400, detail=transcript["error"])
    text = await convert_transcript_to_text(transcript)
    if "error" in text:
        raise HTTPException(status_code=400, detail=text["error"])
    prompt_template = PROMPT_MAP.get(request.prompt_type)
    if not prompt_template:
        raise HTTPException(
            status_code=400, detail=f"Invalid prompt type: {request.prompt_type}"
        )
    print("Using prompt:", request.prompt_type, "and the prompt:", prompt_template)
    result = summarize_format_text(
        text=text["text"], model=request.model, prompt=prompt_template
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    print("done")
    return result

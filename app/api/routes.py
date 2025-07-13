from fastapi import APIRouter, HTTPException
from app.utils import extract_video_id,get_video_transcript,convert_transcript_to_text
from app.models.youtube_models import VideoIDResponse, TranscriptRequest

router = APIRouter()
@router.post("/get_video_id",response_model=VideoIDResponse)
async def get_video_id(url: str):
    
    video_id = extract_video_id(url)
    if "error" in video_id:
        raise HTTPException(status_code=400, detail=video_id["error"])
    return {"video_id": video_id}

@router.post("/get_video_transcript")
async def fetch_transcript(request: TranscriptRequest):
    transcript=await get_video_transcript(request.video_url)
    if "error" in transcript:
        raise HTTPException(status_code=400, detail=transcript["error"])
    return {"transcript": transcript}    

@router.post("/convert_transcript_text_endpoint")
async def convert_transcript_text_endpoint(request: TranscriptRequest):
    transcript=await get_video_transcript(request.video_url)
    
    if "error" in transcript:
        raise HTTPException(status_code=400, detail=transcript["error"])
    text= await convert_transcript_to_text(transcript)
    if "error" in text:
        raise HTTPException(status_code=400, detail=text["error"])  
    return {"text": text}
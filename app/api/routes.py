from fastapi import APIRouter, HTTPException
from app.utils import extract_video_id
from app.models.youtube_models import VideoIDResponse

router = APIRouter()
@router.post("/get_video_id",response_model=VideoIDResponse)
async def get_video_id(url: str):
    
    video_id = extract_video_id(url)
    if "error" in video_id:
        raise HTTPException(status_code=400, detail=video_id["error"])
    return {"video_id": video_id}

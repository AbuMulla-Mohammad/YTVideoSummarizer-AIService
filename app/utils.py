from pytube import extract
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
def extract_video_id(url:str)->str:
    try:
        yt_id=extract.video_id(url)
        return yt_id
    except Exception as e:
        return{"error":str(e)}

async def get_video_transcript(video_url: str):
    try:
        video_id=extract_video_id(video_url)
        if "error" in video_id:
            return {"error": video_id["error"]}
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except TranscriptsDisabled:
        return {"error": "Transcripts are disabled for this video."}
    
    except NoTranscriptFound:
        return {"error": "No transcript available for this video."}
    
    except VideoUnavailable:
        return {"error": "This video is unavailable."}
    
    except Exception as e:
        return {"error": str(e)} 
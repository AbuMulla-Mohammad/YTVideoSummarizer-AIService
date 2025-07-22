from pytube import extract
from pytube.exceptions import RegexMatchError, VideoUnavailable, PytubeError
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from dotenv import load_dotenv
import cohere
import os
from app.models.ai_result_models import VideoSummaryTranscriptResponse,FormatedTranscriptResponse,SummarySectionResponse
from app.prompts import friendly_summary_with_emojis_and_ideas_explenation
import json


load_dotenv()
api_key=os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(api_key=api_key)


def extract_video_id(url:str)->str:
    try:
        yt_id=extract.video_id(url)
        return yt_id
    except RegexMatchError:
        return {"error": "Invalid YouTube URL."}
    except VideoUnavailable:
        return {"error": "Video is unavailable."}
    except PytubeError:
        return {"error": "Failed to process video data."}
    except Exception:
        return {"error": "Unknown error occurred."}

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

async def convert_transcript_to_text(transcript:dict)->dict:
    try:
        lines = []
        for entry in transcript:
            start = entry["start"]
            end = entry["start"] + entry["duration"]
            text = entry["text"]
            lines.append(f"[{start:.2f} - {end:.2f}] {text}")
        return {"text": "\n".join(lines)}
    except Exception as e:
        return {"error": str(e)}


def summarize_format_text(text:str,model:str="command-a-03-2025",prompt:str=friendly_summary_with_emojis_and_ideas_explenation) -> VideoSummaryTranscriptResponse:
    try:
        schema=VideoSummaryTranscriptResponse.model_json_schema()
        schema["type"] = "object"

        schema["properties"]["summary_sections"]["type"] = "array"
        schema["properties"]["summary_sections"]["items"] = SummarySectionResponse.model_json_schema()

        schema["properties"]["formatted_transcript"]["type"] = "array"
        schema["properties"]["formatted_transcript"]["items"] = FormatedTranscriptResponse.model_json_schema()
        res = co.chat(
            model=model,
            messages=[{"role": "user", "content": f"{prompt}\n\n{text}"}],
            
            response_format={
                "type": "json_object",
                "schema": schema,
                }
                
        )
        content = res.message.content
        if isinstance(content, list) and len(content) == 1:
            
            json_str = content[0].text
            json_obj = json.loads(json_str)

            return VideoSummaryTranscriptResponse.model_validate(json_obj)
        
        if isinstance(content, str):
            return VideoSummaryTranscriptResponse.model_validate_json(content)
        elif isinstance(content, dict):
            return VideoSummaryTranscriptResponse.model_validate(content)
        else:
            return {"error": "Unexpected response format from cohere chat"}

    except Exception as e:
        return {"error": str(e)}

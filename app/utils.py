from pytube import extract

def extract_video_id(url:str)->str:
    try:
        yt_id=extract.video_id(url)
        return yt_id
    except Exception as e:
        return{"error":str(e)}

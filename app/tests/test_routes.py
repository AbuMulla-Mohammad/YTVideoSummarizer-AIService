import pytest
from fastapi import HTTPException
from unittest.mock import patch
from fastapi.testclient import TestClient


@patch("app.api.routes.extract_video_id")
def test_get_video_id_success(mock_extract_video_id,client):
    mock_extract_video_id.return_value="abc123XYZ89"
    response=client.post("/api/get_video_id",params={"url": "https://www.youtube.com/watch?v=abc123XYZ89"})
    assert response.status_code==200
    assert response.json()=={"video_id": "abc123XYZ89"}
    mock_extract_video_id.assert_called_once_with("https://www.youtube.com/watch?v=abc123XYZ89")

@pytest.mark.parametrize(
    "error_message",
    [
        "Invalid YouTube URL.",
        "Video is unavailable.",
        "Failed to process video data.",
        "Unknown error occurred.",
    ]
)

@patch("app.api.routes.extract_video_id")
def test_get_video_id_errors(mock_extract_video_id,client,error_message):
    mock_extract_video_id.side_effect=HTTPException(status_code=400, detail=error_message)
    response=client.post("/api/get_video_id",params={"url": "https://www.youtube.com/watch?v=13"})
    assert response.status_code==400
    assert response.json() == {"detail": error_message}

@patch("app.api.routes.get_video_transcript")
def test_fetch_transcript_success(mock_get_video_transcript, client):
    mock_get_video_transcript.return_value=[
        {"text": "hello", "start": 0, "duration": 2}
    ]
    response=client.post("api/get_video_transcript",json={"video_url": "https://www.youtube.com/watch?v=abc123XYZ89"})
    assert response.status_code==200
    assert response.json() == {"transcript": [{"text": "hello", "start": 0, "duration": 2}]}
    mock_get_video_transcript.assert_called_once_with("https://www.youtube.com/watch?v=abc123XYZ89")


@pytest.mark.parametrize(
    "error_message",
    [
        "Transcripts are disabled for this video.",
        "This video is unavailable.",
        "No transcript available for this video.",
        "Unknown error occurred.",
    ]
)
@patch("app.api.routes.get_video_transcript")
def test_fetch_transcript_error(mock_get_video_transcript, client, error_message):
    mock_get_video_transcript.return_value = {"error": error_message}
    response = client.post("api/get_video_transcript", json={"video_url": "https://www.youtube.com/watch?v=abc123XYZ89"})
    assert response.status_code == 400
    assert response.json() == {"detail": error_message}

@patch("app.api.routes.convert_transcript_to_text")
@patch("app.api.routes.get_video_transcript")
@patch("app.api.routes.extract_video_id")
def test_convert_transcript_to_text(mock_extract_video_id, mock_get_video_transcript, mock_convert_transcript_to_text, client):
    mock_extract_video_id.return_value = "abc123XYZ89"
    mock_get_video_transcript.return_value = [
        {"text": "hello", "start": 0, "duration": 2}
    ]
    mock_convert_transcript_to_text.return_value = "[0.00 - 2.00] hello"
    
    response = client.post("/api/convert_transcript_text_endpoint", json={"video_url": "https://youtu.be/abc123XYZ89"})
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["video_id"] == "abc123XYZ89"
    assert "[0.00 - 2.00] hello" in json_response["text"]

    mock_extract_video_id.assert_called_once_with("https://youtu.be/abc123XYZ89")
    mock_get_video_transcript.assert_called_once_with("https://youtu.be/abc123XYZ89")
    mock_convert_transcript_to_text.assert_called_once_with(mock_get_video_transcript.return_value)


@pytest.mark.integration
def test_full_flow_real(client):
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    response = client.post("/api/convert_transcript_text_endpoint", json={"video_url": url})
    assert response.status_code == 200
    assert "video_id" in response.json()
    assert "text" in response.json()
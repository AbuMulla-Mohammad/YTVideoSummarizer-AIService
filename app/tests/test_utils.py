import pytest
from .test_data import youtube_url_formats
from unittest.mock import patch,MagicMock
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from app.utils import get_video_transcript,convert_transcript_to_text,extract_video_id,summarize_format_text
from app.models.ai_result_models import VideoSummaryTranscriptResponse
import json

@pytest.mark.parametrize("url, expected_video_id", youtube_url_formats)
def test_extract_video_id(url, expected_video_id):
    result = extract_video_id(url)
    assert isinstance(result, str)
    assert result == expected_video_id


@pytest.mark.parametrize(
    "invalid_url, expected_error",
    [
        ("not-a-url", "Invalid YouTube URL."),
        ("", "Invalid YouTube URL."),
        ("https://example.com/watch?v=123", "Invalid YouTube URL."),
    ],
)
def test_extract_video_id_invalid(invalid_url, expected_error):
    result = extract_video_id(invalid_url)
    assert isinstance(result, dict)
    assert "error" in result
    assert result["error"] == expected_error


@pytest.mark.asyncio
@patch("app.utils.extract_video_id")
@patch("app.utils.YouTubeTranscriptApi.get_transcript")
async def test_get_video_transcript_success(mock_get_transcript, mock_extract_video_id):
    mock_extract_video_id.return_value = "abc123"
    fake_transcript = [
        {
            "text": "today is scammer destruction look at all",
            "start": 0.32,
            "duration": 4.2,
        },
        {"text": "the icons going away on her screen", "start": 2.96, "duration": 3.08},
        {
            "text": "because the files are deleting and we're",
            "start": 4.52,
            "duration": 2.879,
        },
    ]
    mock_get_transcript.return_value = fake_transcript
    result = await get_video_transcript("https://www.youtube.com/watch?v=abc123")
    assert result == fake_transcript
    mock_extract_video_id.assert_called_once_with(
        "https://www.youtube.com/watch?v=abc123"
    )
    mock_get_transcript.assert_called_once_with("abc123")


@pytest.mark.asyncio
@patch("app.utils.extract_video_id")
async def test_get_video_transcript_extract_video_id_error(mock_extract_video_id):
    mock_extract_video_id.return_value = {"error": "Invalid video URL"}
    result = await get_video_transcript("invalid-url")
    assert isinstance(result, dict)
    assert "error" in result
    assert result["error"] == "Invalid video URL"
    mock_extract_video_id.assert_called_once_with("invalid-url")


@pytest.mark.asyncio
@patch("app.utils.extract_video_id")
@patch("app.utils.YouTubeTranscriptApi.get_transcript")
async def test_get_video_transcript_transcripts_disabled(
    mock_get_transcript, mock_extract_video_id
):
    mock_extract_video_id.return_value = "abc123"
    mock_get_transcript.side_effect = TranscriptsDisabled("abc123")
    result = await get_video_transcript("https://www.youtube.com/watch?v=abc123")
    assert isinstance(result, dict)
    assert result == {"error": "Transcripts are disabled for this video."}


@pytest.mark.asyncio
@patch("app.utils.extract_video_id")
@patch("app.utils.YouTubeTranscriptApi.get_transcript")
async def test_get_video_transcript_no_transcript_found(
    mock_get_transcript, mock_extract_video_id
):
    mock_extract_video_id.return_value = "abc123"
    mock_get_transcript.side_effect = NoTranscriptFound("abc123", ["en"], [])

    result = await get_video_transcript("https://youtube.com/watch?v=abc123")

    assert result == {"error": "No transcript available for this video."}


@pytest.mark.asyncio
@patch("app.utils.extract_video_id")
@patch("app.utils.YouTubeTranscriptApi.get_transcript")
async def test_get_video_transcript_video_unavailable(
    mock_get_transcript, mock_extract_video_id
):
    mock_extract_video_id.return_value = "abc123"
    mock_get_transcript.side_effect = VideoUnavailable("abc123")

    result = await get_video_transcript("https://youtube.com/watch?v=abc123")

    assert result == {"error": "This video is unavailable."}


@pytest.mark.asyncio
@patch("app.utils.extract_video_id")
@patch("app.utils.YouTubeTranscriptApi.get_transcript")
async def test_get_video_transcript_generic_exception(
    mock_get_transcript, mock_extract_video_id
):
    mock_extract_video_id.return_value = "abc123"
    mock_get_transcript.side_effect = Exception("Unexpected error")

    result = await get_video_transcript("https://youtube.com/watch?v=abc123")

    assert result == {"error": "Unexpected error"}


@pytest.mark.asyncio
async def test_convert_transcript_to_text_success():
    transcript = [
        {"start": 0.0, "duration": 2.5, "text": "Hello world"},
        {"start": 2.5, "duration": 3.0, "text": "This is a test"},
    ]

    expected_output = "[0.00 - 2.50] Hello world\n[2.50 - 5.50] This is a test"
    result = await convert_transcript_to_text(transcript)
    assert result["text"] == expected_output


@pytest.mark.asyncio
async def test_convert_transcript_to_text_error():
    transcript = [
        {"duration": 2.5, "text": "Hello world"},
    ]

    result = await convert_transcript_to_text(transcript)
    assert isinstance(result, dict)
    assert "error" in result
    assert "start" in result["error"]  


@pytest.fixture
def mock_response_dict():
    return {
        "summary_sections": [
            {
                "title": "📌 Important Idea",
                "summary": "This is a friendly summary 😊",
                "start": 0.0,
                "end": 10.0
            }
        ],
        "formatted_transcript": [
            {
                "title": "💡 Main Thought",
                "text": "Some explanation without timestamps.",
                "start": 0.0,
                "end": 10.0
            }
        ]
    }


@patch("app.utils.co.chat")
def test_summarize_format_text_success(mock_chat,mock_response_dict):
    mock_chat.return_value.message.content = mock_response_dict
    
    result = summarize_format_text("Hello [0.0 - 10.0] World")
    assert isinstance(result, VideoSummaryTranscriptResponse)
    assert result.summary_sections[0].title == "📌 Important Idea"
    assert result.formatted_transcript[0].title == "💡 Main Thought"

@patch("app.utils.co.chat")
def test_summarize_format_text_with_json_string(mock_chat, mock_response_dict):
    json_content = json.dumps(mock_response_dict)
    mock_chat.return_value.message.content = json_content

    result = summarize_format_text("Hello [0.0 - 10.0] World")

    assert isinstance(result, VideoSummaryTranscriptResponse)
    assert result.summary_sections[0].summary == "This is a friendly summary 😊"


@patch("app.utils.co.chat")
def test_summarize_format_text_with_list_wrapped_text(mock_chat, mock_response_dict):
    # Simulate response: a list with one element that has a `.text` attribute
    message_mock = MagicMock()
    message_mock.text = json.dumps(mock_response_dict)
    mock_chat.return_value.message.content = [message_mock]

    result = summarize_format_text("Hello [0.0 - 10.0] World")

    assert isinstance(result, VideoSummaryTranscriptResponse)
    assert result.formatted_transcript[0].text == "Some explanation without timestamps."


@patch("app.utils.co.chat")
def test_summarize_format_text_with_invalid_format(mock_chat):
    # Simulate an unexpected format
    mock_chat.return_value.message.content = 12345

    result = summarize_format_text("Hello [0.0 - 10.0] World")
    assert isinstance(result, dict)
    assert "error" in result


@patch("app.utils.co.chat")
def test_summarize_format_text_with_exception(mock_chat):
    # Simulate an exception
    mock_chat.side_effect = RuntimeError("API failure")

    result = summarize_format_text("Hello [0.0 - 10.0] World")
    assert isinstance(result, dict)
    assert result["error"] == "API failure"
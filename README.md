# Samuraizer — AI Service

> Part of the **Samuraizer** project — an intelligent YouTube video summarization platform. Users submit a YouTube URL and receive a structured summary and formatted transcript powered by AI.

This repository contains the **AI microservice** responsible for all AI operations: extracting video transcripts from YouTube using youtube-transcript-api, converting them into readable text, and generating structured summaries using Cohere's language models. It is consumed internally by the [Samuraizer ASP.NET Backend](https://github.com/AbuMulla-Mohammad/AIYTVideoSummarizerASPBackend).

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Prompt Types](#prompt-types)
- [Configuration / Environment Variables](#configuration--environment-variables)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Running Tests](#running-tests)

---

## Overview

The AI Service is a lightweight **FastAPI** application that exposes four endpoints consumed by the ASP.NET backend. Given a YouTube URL, it:

1. Extracts the YouTube video ID from the URL.
2. Fetches the video's auto-generated or user-provided transcript via `youtube-transcript-api`.
3. Converts the raw transcript into timestamped text.
4. Sends that text to **Cohere's `command-a-03-2025` model** along with a structured prompt, receiving back a JSON response containing:
   - **Summary sections** — topic-divided sections, each with a title, summary text, and timestamps.
   - **Formatted transcript** — the original transcript grouped into clean, readable paragraphs with timestamps.

The service is stateless and designed to run as an internal dependency alongside the ASP.NET backend. It listens on port `8000` by default.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.13 |
| Web Framework | FastAPI 0.116 |
| ASGI Server | Uvicorn 0.35 |
| Data Validation | Pydantic 2.11 |
| AI / LLM | Cohere Python SDK v5 (`command-a-03-2025`) |
| YouTube Transcript | `youtube-transcript-api` 1.1.1 |
| YouTube URL Parsing | `pytube` 15.0.0 |
| Environment Config | `python-dotenv` |
| Testing | Pytest 8.4 + pytest-asyncio |
| Containerization | Docker |
| Package Manager | `uv` |

---

## Project Structure

```
app/
├── main.py                  # FastAPI app entry point
├── api/
│   └── routes.py            # All route definitions
├── models/
│   ├── youtube_models.py    # Request/response Pydantic models
│   └── ai_result_models.py  # AI output models (summary sections, transcript)
├── prompts.py               # Prompt templates and PROMPT_MAP registry
├── utils.py                 # Core logic: transcript fetch, text conversion, Cohere call
└── tests/
    ├── conftest.py
    ├── test_data.py
    ├── test_routes.py
    └── test_utils.py
```

---

## API Endpoints

> Full interactive documentation is available on the [Postman collection](https://documenter.getpostman.com/view/37800136/2sB3Wk14it).

All routes are prefixed with `/api`.

---

### `POST /api/get_video_id`

Extracts the YouTube video ID from a given URL.

**Query Parameter:**

| Parameter | Type | Description |
|---|---|---|
| `url` | `string` | A valid YouTube video URL |

**Response:**

```json
{
  "video_id": "9JPnN1Z_iSY"
}
```

**Errors:** Returns `400` with a descriptive message for invalid or unavailable URLs.

---

### `POST /api/get_video_transcript`

Fetches the raw transcript (list of timestamped segments) for a given video URL.

**Request Body:**

```json
{
  "video_url": "https://www.youtube.com/watch?v=9JPnN1Z_iSY&t=6s"
}
```

**Response:** A list of transcript segment objects with `text`, `start`, and `duration` fields.

**Errors:** Returns `400` if transcripts are disabled, not found, or the video is unavailable.

---

### `POST /api/convert_transcript_text_endpoint`

Fetches the transcript and converts it into a single formatted text string where each line includes a `[start - end]` timestamp, suitable for passing to an LLM.

**Request Body:**

```json
{
  "video_url": "https://www.youtube.com/watch?v=9JPnN1Z_iSY&t=6s"
}
```

**Response:**

```json
{
  "transcript": [
    {
      "text": "Before a system can authorize or",
      "start": 0,
      "duration": 4.24
    },
    {
      "text": "restrict anything, it first needs to",
      "start": 2.32,
      "duration": 4.64
    },

      .
      .
      .

    {
      "text": "user can do in your system. And that is",
      "start": 358,
      "duration": 4.72
    },
    {
      "text": "what we will cover next in the next",
      "start": 360.72,
      "duration": 4.479
    },
    {
      "text": "video.",
      "start": 362.72,
      "duration": 2.479
    }
  ]
}
```

---

### `POST /api/summarize_format_transcript`

The **main endpoint** — given a YouTube URL, it fetches the transcript, converts it to text, selects a prompt, and calls the Cohere model to produce a structured summary with a formatted transcript.

**Request Body:**

```json
{
  "video_url": "https://youtu.be/9JPnN1Z_iSY?si=d9vXUWzdlbXhVl9Q",
  "prompt_type": "friendly_summary_with_emojis_and_ideas_explenation",
  "model": "command-a-03-2025"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `video_url` | `string` | required | YouTube video URL |
| `prompt_type` | `string` | `friendly_summary_with_emojis_and_ideas_explenation` | Which prompt strategy to use (see below) |
| `model` | `string` | `command-a-03-2025` | Cohere model to use |

**Response:**

```json
{
  "summary_sections": [
    {
      "title": "🛡️ What is Authentication?",
      "summary": "Authentication is the process of verifying the identity of a user or system trying to access an app. It's the first step before authorization, ensuring the requestor is legitimate. Think of it like showing your ID before entering a secure area.",
      "start": 0,
      "end": 72.32
    },
    {
      "title": "🔑 Authentication Methods Explained",
      "summary": "From basic username/password combos to modern techniques like Bearer Tokens, OAuth2, and GVT tokens, authentication methods vary in security and complexity. Bearer Tokens are fast and stateless, while OAuth2 allows login via trusted providers like Google. Access and Refresh Tokens keep users logged in securely, and Single Sign-On (SSO) simplifies access across multiple services.",
      "start": 72.32,
      "end": 279.52
    },
    {
      "title": "🤝 Protocols and Future Steps",
      "summary": "Identity protocols like OAuth2 and SAML define how apps securely exchange user login info. OAuth2 is modern and JSON-based, while SAML is XML-based and common in legacy systems. After authentication, authorization determines what resources a user can access, which we'll cover in the next video.",
      "start": 279.52,
      "end": 365.2
    }
  ],
  "formatted_transcript": [
    {
      "text": "Before a system can authorize or restrict anything, it first needs to know the identity of the requestor. That's what authentication does. It verifies that the person or system trying to access your app is legit. And in this video, you'll learn how modern applications handle authentication from basic to bear tokens to OAuth2 authentication and GVT tokens as well as access and refresh tokens and also single sign on and identity protocols.",
      "start": 0,
      "end": 30.88
    },
    {
      "text": "Before learning the different types, let's first understand what is authentication. Authentication basically answers who the user is and if they are allowed to access your system. So whenever a login request is sent either by the user or another service, this is where we confirm the identity of the user and either provide them access so approve their request or reject it with unauthorized request. This is basically the first step before authorization begins which is the topic of the next lesson.",
      "start": 29.2,
      "end": 63.12
    },
    {
      "text": "So before you access any data or perform any actions on this service, the system needs to know who you are and this is where the authentication is used. The first and simplest type of authentication is basic authentication. This is where you use username and password in combination and you send a login request which contains the base 64 encoded version of username and password. This is a very simple way of encoding data and it's easily reversible. And because it's easily reversible, it's now considered insecure unless it's wrapped within HTTPS.",
      "start": 60.08,
      "end": 99.68
    },
    .
    .
    .
  ]
}
```

---

## Prompt Types

The service supports three built-in prompt strategies, selectable via the `prompt_type` field:

| Prompt Type | Description |
|---|---|
| `section_based_summary_and_formatting` | Divides the transcript into idea-based sections. Each section gets a title, a concise summary, and a timestamp range. The full transcript is also grouped into the same sections. |
| `simple_summary` | Groups sentences into natural paragraphs and produces 2–5 independent summary sections with titles, summaries, and timestamps. |
| `friendly_summary_with_emojis_and_ideas_explenation` *(default)* | Same as `simple_summary` but rewrites content in a friendly, conversational tone with relevant emojis, analogies, and clear explanations — ideal for general audiences. |

---

## Configuration / Environment Variables

Create a `.env` file in the project root:

```env
COHERE_API_KEY=your_cohere_api_key_here
```

| Variable | Required | Description |
|---|---|---|
| `COHERE_API_KEY` | ✅ Yes | Your Cohere API key. Obtain one from [cohere.com](https://cohere.com). |

---

## Running Locally

**Prerequisites:** Python 3.13, `uv` package manager.

```bash
# Clone the repository
git clone https://github.com/AbuMulla-Mohammad/YTVideoSummarizer-AIService
cd YTVideoSummarizer-AIService

# Install dependencies
uv sync

# Create and populate your .env file
echo "COHERE_API_KEY=your_key_here" > .env

# Start the development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at `http://127.0.0.1:8000`. Swagger UI is accessible at `http://127.0.0.1:8000/docs`.


---

## Running Tests

```bash
uv run pytest
```

Tests are located in `app/tests/` and cover route behavior, utility functions, and data models.

---

## Related Repositories

- **[Samuraizer ASP.NET Backend](https://github.com/AbuMulla-Mohammad/AIYTVideoSummarizerASPBackend)** — The main backend service that handles user authentication, request management, data persistence, and orchestrates calls to this AI service.
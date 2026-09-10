# 🎬 VideoRAG

**An AI pipeline that turns any recording — YouTube link or local file — into a transcript, a summary, extracted decisions, and a queryable chat interface.**

Built with **Python · Whisper · yt-dlp · LangChain · Mistral api · Streamlit**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Mistral AI](https://img.shields.io/badge/Mistral%20AI-FF7000?logo=mistral&logoColor=white)](https://mistral.ai/)
[![Whisper](https://img.shields.io/badge/OpenAI-Whisper-412991?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Live Demo](https://videorag-5pecbftlyc3hqkgzmmzgwo.streamlit.app/)** 


---

## Overview

Watching back a long meeting or lecture to find the one decision that mattered is a waste of time. **VideoRAG turns a recording into a structured, searchable record** — download or load the source, transcribe it, summarize it, pull out the action items and open questions, and then ask it follow-up questions directly instead of scrubbing through audio.

```
YouTube URL / File → Audio Extraction → Transcription → Summarization → Extraction → RAG Chat
```

Enter a link or a local path, and VideoRAG returns a title, a summary, action items, key decisions, and open questions — plus a chat interface grounded in the actual transcript.

---

## Why This Project Matters

This project demonstrates practical, end-to-end experience with the skills modern AI engineering roles look for:

| Area | Demonstrated Skill |
|---|---|
| **Audio/media pipelines** | Handling both remote (YouTube) and local media sources, chunking audio for transcription at scale |
| **Speech-to-text integration** | Running Whisper locally for offline, cost-free transcription |
| **Retrieval-augmented generation** | Grounding chat answers in the transcript rather than model memory |
| **LLM application development** | Building with LangChain and Google Gemini across four distinct tasks (title, summary, extraction, chat) |
| **Prompt engineering** | Distinct prompts tuned per task — summarization, action-item extraction, and conversational QA behave differently |
| **Full-stack delivery** | Both a CLI entry point (`main.py`) and a deployed, interactive Streamlit UI (`app.py`) |
| **Software design** | Clean separation between input handling, transcription, language tasks, and retrieval |

---

## How It Works

```
                    ┌───────────────────────┐
                    │  YouTube URL / File    │
                    └───────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │ 01 Audio Processing    │  → yt-dlp download / local load + chunking
                    └───────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │ 02 Transcription       │  → Whisper (english / hinglish)
                    └───────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │ 03 Title + Summary     │  → Google Gemini
                    └───────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │ 04 Extraction          │  → Action items, decisions, questions
                    └───────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │ 05 RAG Chat Engine     │  → Query the transcript conversationally
                    └───────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │  Report + Live Chat    │
                    └───────────────────────┘
```

| Stage | Responsibility | Tool / Model |
|---|---|---|
| **Audio Processing** | Downloads YouTube audio or loads a local file, splits into chunks | yt-dlp |
| **Transcription** | Converts audio chunks into text, supports English and Hinglish | OpenAI Whisper (local) |
| **Title + Summary** | Generates a session title and a structured summary | Google Gemini |
| **Extraction** | Pulls action items, key decisions, and open questions from the transcript | Google Gemini |
| **RAG Engine** | Builds a retrievable index over the transcript and answers follow-up questions | LangChain + Google Gemini |

---

## Features

- 🔊 Accepts both YouTube URLs and local audio/video file paths
- 🗣️ Local Whisper transcription — no audio leaves your machine
- 🌐 English and Hinglish transcription support
- ✍️ Auto-generated session title and structured summary
- ✅ Extracted action items, key decisions, and open questions
- 💬 Chat interface grounded in the transcript via retrieval-augmented generation
- 📊 Real-time pipeline status for each processing stage
- 🖥️ Both a Streamlit UI and a CLI entry point (`main.py`) for the same pipeline
- 🔐 Secrets managed via environment variables, never hardcoded

---

## Tech Stack

- **Language:** Python 3.12
- **Transcription:** OpenAI Whisper (local inference)
- **Audio Download:** yt-dlp
- **LLM:** Mistral
- **Orchestration / RAG:** LangChain
- **UI:** Streamlit, custom CSS

---

## Getting Started

### 1. Clone & set up environment

```bash
git clone https://github.com/YOUR_USERNAME/VideoRAG.git
cd VideoRAG
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API keys

Create a `.env` file in the project root (use `.env.example` as a template):

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Access to Google Gemini for title generation, summarization, extraction, and RAG chat |

> **Never commit real API keys.** Keep `.env` in `.gitignore`; commit `.env.example` instead. If a key is ever pushed by mistake, revoke and rotate it immediately.

> **Note:** Transcription runs locally via Whisper and downloads a model on first use — no API key is required for this step, but a working `ffmpeg` install is.

### 3. Run the app

```bash
streamlit run app.py
```

### 4. Or use the CLI

```bash
python main.py
```

The CLI runs the same pipeline end to end and drops you into a terminal chat loop with the transcript once processing finishes.

---

## Project Structure

```
VideoRAG/
├── app.py                     # Streamlit UI & pipeline orchestration
├── main.py                    # CLI entry point for the same pipeline
├── core/
│   ├── transcriber.py         # Whisper-based transcription
│   ├── summarizer.py          # Title + summary generation (Gemini)
│   ├── extractor.py           # Action items, decisions, questions (Gemini)
│   └── rag_engine.py          # RAG chain build + question answering
├── utils/
│   └── audio_processor.py     # YouTube download / local file handling + chunking
├── requirements.txt
├── .env.example
├── README.md
└── tests/
    └── test_pipeline.py
```

---

## Example Sources to Try

```
https://www.youtube.com/watch?v=<any-talk-or-meeting-recording>
/path/to/local/meeting.mp4
/path/to/local/lecture.mp3
```

---

## Roadmap

- [x] Core pipeline (Audio → Transcript → Summary → Extraction → RAG)
- [x] Interactive Streamlit UI with live pipeline status
- [x] CLI entry point with terminal chat loop
- [x] Hinglish transcription support
- [ ] Speaker diarization (who said what)
- [ ] Downloadable Markdown / PDF report export
- [ ] Parallel chunk transcription for long recordings
- [ ] Persistent session history + multiple saved meetings
- [ ] Docker deployment & CI/CD

---

## Testing

```bash
pytest
```

Coverage targets each pipeline stage independently — valid/invalid sources, empty transcripts, and failure handling for audio processing, transcription, summarization, extraction, and RAG chat.

---

## Author

**YOUR NAME**

[GitHub](https://github.com/iiitianrajan/videoRAG) · [LinkedIn](www.linkedin.com/in/rajan-kumar-b787382b9)

---

## License

Licensed under the [MIT License](LICENSE).

If you find this project useful, consider giving it a ⭐ on GitHub.

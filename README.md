# Offline Language Coach (Streamlit)

## What it does
- Records audio in the browser (mic button)
- Offline Speech-to-Text using faster-whisper (Whisper)
- Offline language detection (langdetect)
- Offline grammar/rule flags (LanguageTool via language_tool_python)
- Offline LLM coaching + practice module using Ollama (local)
- Progress tracker saved locally (SQLite)

## Setup
1) Install uv: https://docs.astral.sh/uv/
2) In this folder:

```bash
uv venv
uv sync
uv run streamlit run app.py
```

## Ollama (offline LLM)
Install Ollama and pull a model, e.g.:

```bash
ollama pull qwen2.5:14b-instruct
ollama serve
```

Then keep "Use local LLM" enabled in the sidebar.

## Notes
- LanguageTool may download its engine the first time you run it. After that it runs locally.
- Pronunciation feedback is marked experimental and is transcript-based (no phoneme scoring yet).

from __future__ import annotations

import os
import requests
from services.prompts import (
    WEAKEST_POINT_PROMPT,
    PRACTICE_MODULE_PROMPT,
    PRONUNCIATION_PROMPT,
)

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")



def _chat(system: str, user: str, model: str) -> str:
    """
    Calls Ollama /api/chat and returns assistant message content as a string.
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
    }

    r = requests.post(url, json=payload, timeout=120)

    if not r.ok:
        # Print useful debug info for terminal logs
        print("LLM HTTP status:", r.status_code)
        print("LLM URL:", url)
        print("LLM response (first 2000 chars):", r.text[:2000])
        r.raise_for_status()

    data = r.json()

    # Ollama chat response usually looks like:
    # {"message": {"role":"assistant","content":"..."} , ...}
    msg = data.get("message") or {}
    content = msg.get("content")

    if not isinstance(content, str):
        # Fallback: return entire JSON as string for visibility
        return str(data)

    return content


def llm_weakest_point(
    text: str,
    detected_lang: str,
    target_lang: str,
    native_lang: str,
    grammar_tool_summary: str,
    model: str | None = None,
):
    user_prompt = WEAKEST_POINT_PROMPT.format(
        text=text,
        detected_lang=detected_lang,
        target_lang=target_lang,
        grammar_tool_summary=grammar_tool_summary,
        native_lang=native_lang,
    )

    out_text = _chat(system="You are a precise language tutor.", user=user_prompt, model=model)

    weakest = "Unknown"
    why = ""
    fixes: list[str] = []

    for line in out_text.splitlines():
        low = line.lower().strip()
        if low.startswith("weakest:"):
            weakest = line.split(":", 1)[1].strip()
        elif low.startswith("why:"):
            why = line.split(":", 1)[1].strip()
        elif line.strip().startswith("-"):
            fixes.append(line.strip()[1:].strip())

    if not why:
        why = out_text.strip()

    return {"weakest_point": weakest, "explanation": why, "fixes": fixes[:8]}


def llm_generate_practice_module(
    text: str,
    detected_lang: str,
    target_lang: str,
    weakest_point: str,
    native_lang: str,
    model: str | None = None,
) -> str:
    user_prompt = PRACTICE_MODULE_PROMPT.format(
        text=text,
        detected_lang=detected_lang,
        target_lang=target_lang,
        weakest_point=weakest_point,
        native_lang=native_lang,
    )
    return _chat(
        system="You create targeted practice modules for language learners.",
        user=user_prompt,
        model=model,
    )


def llm_pronunciation_feedback(
    text: str,
    target_lang: str,
    latin_pron: str,
    model: str | None = None,
) -> str:
    user_prompt = PRONUNCIATION_PROMPT.format(
        text=text,
        target_lang=target_lang,
        latin_pron=latin_pron,
    )
    return _chat(
        system="You provide cautious, practical pronunciation coaching.",
        user=user_prompt,
        model=model,
    )

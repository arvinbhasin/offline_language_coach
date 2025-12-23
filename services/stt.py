import tempfile
from faster_whisper import WhisperModel

_MODEL = None

def _get_model():
    """
    Offline STT:
    - On CPU: small + int8 is a good speed/quality tradeoff.
    - If you have GPU/CUDA, change device to "cuda" and compute_type to "float16".
    """
    global _MODEL
    if _MODEL is None:
        _MODEL = WhisperModel("small", device="cpu", compute_type="int8")
    return _MODEL

# services/stt.py
import os
import tempfile
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")

def transcribe_audio_bytes(audio_bytes: bytes, language_hint=None):
    tmp_path = None
    try:
        # IMPORTANT on Windows: delete=False + close the file before reopening
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
            f.write(audio_bytes)
            f.flush()  # not strictly required, but nice

        segments, info = model.transcribe(
            tmp_path,
            language=language_hint,
            vad_filter=True,
        )

        text = "".join(seg.text for seg in segments).strip()
        return {"text": text, "language": info.language, "duration": info.duration}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except PermissionError:
                # If Streamlit reruns instantly, Windows may still have it locked for a moment.
                pass

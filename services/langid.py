from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Offline language identification (LID).
    For best accuracy later, you can swap to fastText LID (still offline).
    """
    try:
        return detect(text)
    except Exception:
        return "unknown"

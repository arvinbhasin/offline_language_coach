import re

def latinize_text(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z\s\.,;:\-\?!']", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def latin_pronunciation_hint(latin_text: str) -> str:
    t = latin_text.lower()
    t = t.replace("j", "y")
    t = t.replace("v", "w")
    t = t.replace("qu", "kw")
    t = t.replace("ae", "eye")
    t = t.replace("oe", "oy")
    return t

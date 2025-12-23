import language_tool_python

_TOOL_CACHE = {}

def _map_lang(lang_code: str) -> str:
    """
    Map short codes to LanguageTool codes.
    """
    lang_code = (lang_code or "").lower()
    if lang_code.startswith("en"):
        return "en-US"
    if lang_code.startswith("de"):
        return "de-DE"
    if lang_code.startswith("es"):
        return "es"
    if lang_code.startswith("fr"):
        return "fr"
    return "en-US"

def _get_tool(lang_code: str):
    key = _map_lang(lang_code)
    if key not in _TOOL_CACHE:
        # language_tool_python runs LanguageTool locally (it may download LT on first run).
        _TOOL_CACHE[key] = language_tool_python.LanguageTool(key)
    return _TOOL_CACHE[key]

def grammar_feedback(text: str, lang_code: str):
    tool = _get_tool(lang_code)
    matches = tool.check(text)

    simplified = []
    for m in matches:
        ctx = (m.context or "").replace("\n", " ")
        simplified.append({
            "rule": getattr(m, "ruleId", "RULE"),
            "message": m.message,
            "context": ctx,
        })

    summary = f"{len(matches)} potential issues flagged by LanguageTool."
    return {"summary": summary, "matches": simplified, "num_matches": len(matches)}

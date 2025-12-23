WEAKEST_POINT_PROMPT = """
You are analyzing learner language.

Detected language: {detected_lang}
Target language: {target_lang}
External grammar tool summary: {grammar_tool_summary}
Native language: {native_lang}

Text:
{text}
All text about explanations should be in {native_lang}, all examples should be in {target_lang} (with {native_lang} translation for clarity)
Return exactly this format:
Weakest: <one short phrase like "verb tense consistency" or "article usage">
Why: <2-4 sentences>
Fixes:
- <actionable fix 1>
- <actionable fix 2>
- <actionable fix 3>
"""

PRACTICE_MODULE_PROMPT = """
Create a compact practice module for a language learner.

Detected language: {detected_lang}
Target language: {target_lang}
Weakest point: {weakest_point}
Native language: {native_lang}

Base it on this transcript:
{text}
All text about explanations should be in {native_lang}, all examples should be in {target_lang} (with {native_lang} translation for clarity)

Return in this structure (plain text):
1) Micro-lesson (max 6 lines)
2) Drills:
   - 5 corrections (with answers)
   - 5 fill-in-the-blank (with answers)
   - 3 rewrites (include sample answers)
3) 60-second speaking prompt targeting the weakness
Keep it short and extremely practical.
"""

PRONUNCIATION_PROMPT = """
You are a pronunciation coach.

Important:
- You are NOT hearing audio. You only see a transcript and an approximate Latin-based pronunciation hint.
- Mark everything as probabilistic.
- Keep it short and actionable.
- End with: Experimental pronunciation feedback: yes

Target language: {target_lang}

Transcript:
{text}

Latin-ish pronunciation hint (approximate):
{latin_pron}

Return:
- 3-6 likely pronunciation pitfalls (bullets)
- 2 short drills (minimal-pair style if possible)
- Experimental pronunciation feedback: yes
"""

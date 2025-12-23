import os
import datetime as dt
import streamlit as st
import pandas as pd
import requests
from streamlit_mic_recorder import mic_recorder
from services.pron_analysis import pronunciation_targets


from services.stt import transcribe_audio_bytes
from services.langid import detect_language
from services.grammar import grammar_feedback
from services.latin import latinize_text, latin_pronunciation_hint
from services.llm import llm_weakest_point, llm_generate_practice_module, llm_pronunciation_feedback
from services.progress import init_db, save_attempt, load_attempts

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def ollama_has_model(model_name: str) -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        return model_name in models
    except Exception:
        return False
st.set_page_config(page_title="Offline Language Coach", layout="wide")

init_db()

st.title("Offline Language Coach")
st.caption("Record -> Offline Speech-to-Text -> Grammar + Feedback + hard pronunciation -> Practice Module -> Progress Tracking")

with st.sidebar:
    st.header("Settings")
    target_lang = st.selectbox("Target language", ["en", "es", "de", "fr"], index=0)
    st.markdown("**LLM (with the Goated Ollama)**")
    use_llm = st.checkbox("Use local LLM (Ollama)", value=True)
    st.caption(f"Model: `{OLLAMA_MODEL}` (requires [Ollama](https://ollama.com/))")
    native_lang = st.selectbox("Native language (L1)", ["en", "es", "de", "fr"], index=0)
    st.caption("Used to flag words with letter patterns uncommon in your native language.")
    st.divider()
    speaker_id = st.text_input("Speaker ID (for progress tracking)", value="default")
    st.caption("Saved locally to data/progress.db")

tabs = st.tabs(["Record & Analyze", "Progress"])

with tabs[0]:
    st.subheader("1) Record audio")
    st.write("Click **Start recording**, speak for ~30–90 seconds, then **Stop**.")
    audio = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop",
        just_once=False,
        use_container_width=True,
        format="wav"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("2) Transcript")
        if "transcript" not in st.session_state:
            st.session_state["transcript"] = ""
        if audio and isinstance(audio, dict) and audio.get("bytes"):
            st.info("Audio captured. Click **Transcribe (offline)**.")
        if st.button("Transcribe (offline)"):
            if not (audio and audio.get("bytes")):
                st.warning("Record audio first.")
            else:
                res = transcribe_audio_bytes(audio["bytes"], language_hint=None)
                st.session_state["transcript"] = res["text"]
                st.success("Transcription complete (offline).")
                if res.get("detected_language"):
                    st.caption(f"Whisper detected: {res['detected_language']} (p={res.get('language_probability')})")

        text = st.text_area(
            "You can also paste/edit the transcript here:",
            height=220,
            value=st.session_state.get("transcript", "")
        )

    with col2:
        st.subheader("3) Analyze")
        if st.button("Analyze transcript"):
            if not text.strip():
                st.warning("Need transcript text first.")
                st.stop()

            detected = detect_language(text)
            gt = grammar_feedback(text, detected)

            weakest = {"weakest_point":"(LLM disabled)", "explanation":"", "fixes":[]}
            practice = "(LLM disabled)"
            pron = None

            if use_llm:
                weakest = llm_weakest_point(
                    text=text,
                    detected_lang=detected,
                    target_lang=target_lang,
                    native_lang=native_lang,
                    grammar_tool_summary=gt["summary"],
                    model=OLLAMA_MODEL
                )
                practice = llm_generate_practice_module(
                    text=text,
                    detected_lang=detected,
                    target_lang=target_lang,native_lang=native_lang,
                    weakest_point=weakest["weakest_point"],
                    model=OLLAMA_MODEL
                )

            latin_text = latinize_text(text)
            latin_pron = latin_pronunciation_hint(latin_text)
            pron_targets = pronunciation_targets(text, native_lang=native_lang)

    
            # Save attempt locally
            save_attempt(
                speaker_id=speaker_id,
                ts=dt.datetime.now().isoformat(timespec="seconds"),
                target_lang=target_lang,
                detected_lang=detected,
                transcript=text,
                weakest_point=weakest["weakest_point"],
                num_issues=gt["num_matches"],
                llm_model=(OLLAMA_MODEL if use_llm else ""),
            )

            st.session_state["last_result"] = {
                "detected": detected,
                "grammar": gt,
                "weakest": weakest,
                "practice": practice,
                "latin_text": latin_text,
                "latin_pron": latin_pron,
                "pron_feedback": pron,
                "pron_targets": pron_targets,
                
            }
            st.success("Analysis complete + saved to progress tracker.")

        res = st.session_state.get("last_result")
        if res:
            st.markdown("---")
            st.subheader("Results")
            r1, r2 = st.columns(2)

            with r1:
                st.markdown(f"**Detected language:** `{res['detected']}`")
                st.markdown(f"**Grammar flags:** {res['grammar']['summary']}")
                if res["grammar"]["matches"]:
                    st.write("Top flags:")
                    for m in res["grammar"]["matches"][:10]:
                        st.markdown(f"- **{m['rule']}**: {m['message']}  \n  _…{m['context']}…_")

            with r2:
                st.markdown("**Weakest point**")
                st.markdown(f"**{res['weakest']['weakest_point']}**")
                if res['weakest']['explanation']:
                    st.write(res['weakest']['explanation'])
                if res['weakest']['fixes']:
                    st.write("Fixes:")
                    for fx in res['weakest']['fixes']:
                        st.markdown(f"- {fx}")

            st.subheader("Practice module")
            st.write(res["practice"])

            st.subheader("Pronunciation targets (text-based)")
            st.caption(f"Native language (L1): `{native_lang}` — heuristic flags based on letter-patterns and syllable length.")

            bw = res["pron_targets"]["biggest_words"]
            mw = res["pron_targets"]["mismatch_words"]

            if bw:
                st.markdown("**Biggest words (most syllables)**")
                for item in bw:
                    st.markdown(f"- `{item['word']}` — {item['syllables']} syllables")

            if mw:
                st.markdown("**Words likely tricky for your L1 (pattern-based)**")
                for item in mw:
                    reasons = ", ".join(item["reasons"])
                    st.markdown(f"- `{item['word']}` — {item['syllables']} syllables (why: {reasons})")



with tabs[1]:
    st.subheader("Progress")
    attempts = load_attempts(speaker_id=speaker_id)
    if attempts.empty:
        st.info("No attempts saved yet. Record + analyze on the first tab.")
    else:
        st.write("Latest attempts (saved locally):")
        st.dataframe(attempts, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Trends")
        # Convert timestamps
        df = attempts.copy()
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        df = df.sort_values("ts")
        st.line_chart(df.set_index("ts")["num_issues"])
        st.caption("This uses LanguageTool flag count as a rough proxy. (Lower is often better, but not always.)")

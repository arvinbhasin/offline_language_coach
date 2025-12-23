from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

WORD_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ]+(?:'[A-Za-zÀ-ÖØ-öø-ÿ]+)?")

VOWELS = set("aeiouyàáâäãåæèéêëìíîïòóôöõøœùúûüÿ")

UNCOMMON_FOR_L1 = {
    "en": [
        "tsch", "sch", "zsch", "ch", "ç", "eau", "oin", "ille", "gn", "rr", "ll", "ñ",
    ],
    "es": [
        "th", "sh", "zh", "st", "str", "spl", "spr", "sk", "ts", "ck", "ght", "wr",
    ],
    "de": [
        "th", "sh", "zh", "ñ", "ll", "rr", "tion", "sion", "eau", "ille",
    ],
    "fr": [
        "th", "sh", "zh", "ñ", "ll", "rr", "sch", "tsch", "cht", "sp", "st", "str",
    ],
}

CONSONANT_RUN = re.compile(r"[bcdfghjklmnpqrstvwxz]{4,}", re.IGNORECASE)


def tokenize_words(text: str) -> List[str]:
    return [m.group(0) for m in WORD_RE.finditer(text)]


def rough_syllable_count(word: str) -> int:
    """
    Very lightweight syllable estimator:
    counts vowel groups. Works “okay” across en/es/de/fr for ranking longest words.
    """
    w = word.lower()
    groups = 0
    in_vowel = False
    for ch in w:
        is_v = ch in VOWELS
        if is_v and not in_vowel:
            groups += 1
        in_vowel = is_v

    # Small English-ish tweak: silent trailing 'e' reduces syllable count sometimes
    if w.endswith("e") and groups > 1 and not w.endswith(("le", "ee")):
        groups -= 1

    return max(groups, 1)


def biggest_words(text: str, top_n: int = 10) -> List[Dict]:
    words = tokenize_words(text)
    scored = []
    for w in words:
        syl = rough_syllable_count(w)
        scored.append((syl, len(w), w))
    scored.sort(reverse=True)  # highest syllables first, then length
    out = []
    seen = set()
    for syl, ln, w in scored:
        key = w.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"word": w, "syllables": syl, "length": ln})
        if len(out) >= top_n:
            break
    return out


def mismatch_words(text: str, native_lang: str, top_n: int = 12) -> List[Dict]:
    """
    Flags words likely to be tricky for the native language based on uncommon letter clusters.
    This is heuristic (offline) and intended as a “practice target” list.
    """
    words = tokenize_words(text)
    patterns = UNCOMMON_FOR_L1.get(native_lang, [])
    flagged = []

    for w in words:
        wl = w.lower()
        hits = []

        for p in patterns:
            if p in wl:
                hits.append(p)

        if CONSONANT_RUN.search(wl):
            hits.append("consonant-run(4+)")

        if hits:
            flagged.append((len(hits), rough_syllable_count(w), len(w), w, sorted(set(hits))))

    # Sort: more “reasons” first, then syllables, then length
    flagged.sort(reverse=True)

    out = []
    seen = set()
    for reasons, syl, ln, w, hits in flagged:
        key = w.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"word": w, "syllables": syl, "reasons": hits})
        if len(out) >= top_n:
            break
    return out


def pronunciation_targets(text: str, native_lang: str) -> Dict:
    return {
        "biggest_words": biggest_words(text, top_n=10),
        "mismatch_words": mismatch_words(text, native_lang=native_lang, top_n=12),
    }

"""Pure text normalization. No I/O, no network, no framework imports.

Known limitation: homoglyph folding is heuristic. Definitive folding will be
taxonomy-driven in the matcher (Phase 1). Tests pin the current behaviour.
"""

import re
import unicodedata

REDACTED = "[redacted]"

_HOMOGLYPHS = str.maketrans(
    {
        "А": "A",
        "В": "B",
        "Е": "E",
        "К": "K",
        "М": "M",
        "Н": "H",
        "О": "O",
        "Р": "P",
        "С": "C",
        "Т": "T",
        "У": "Y",
        "Х": "X",
        "а": "a",
        "е": "e",
        "о": "o",
        "р": "p",
        "с": "c",
        "у": "y",
        "х": "x",
    }
)
_WS = re.compile(r"\s+")
_CYR = re.compile(r"[а-яё]", re.IGNORECASE)
_LAT = re.compile(r"[a-z]", re.IGNORECASE)
_URL = re.compile(r"https?://\S+")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_HANDLE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{3,}")
_PHONE_CANDIDATE = re.compile(r"(?<!\d)\+?\d[\d\s().\-]{7,}\d(?!\d)")
_TECH_PUNCT = frozenset("+#.")


def normalize(text: str) -> str:
    return _WS.sub(" ", unicodedata.normalize("NFKC", text)).strip()


def fold_homoglyphs(token: str) -> str:
    has_cyr = bool(_CYR.search(token))
    has_lat = bool(_LAT.search(token))
    if has_cyr and not has_lat and not (set(token) & _TECH_PUNCT):
        return token
    return token.translate(_HOMOGLYPHS)


def normalize_for_match(text: str) -> str:
    return " ".join(fold_homoglyphs(t) for t in normalize(text).split()).casefold()


def _redact_phones(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        digits = sum(char.isdigit() for char in match.group())
        return REDACTED if digits >= 10 else match.group()

    return _PHONE_CANDIDATE.sub(repl, text)


def redact_pii(text: str) -> str:
    out = _URL.sub(REDACTED, text)
    out = _EMAIL.sub(REDACTED, out)
    out = _HANDLE.sub(REDACTED, out)
    return _redact_phones(out)

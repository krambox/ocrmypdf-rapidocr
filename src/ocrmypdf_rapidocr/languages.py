from __future__ import annotations

from typing import Any, Sequence

from ocrmypdf.exceptions import BadArgsError

# Map OCRmyPDF/Tesseract language codes to RapidOCR LangRec values.
_DIRECT_LANGUAGE_MAP: dict[str, str] = {
    "ara": "ARABIC",
    "chi_sim": "CH",
    "chi_tra": "CHINESE_CHT",
    "eng": "EN",
    "ell": "EL",
    "gre": "EL",
    "jpn": "JAPAN",
    "kor": "KOREAN",
    "tha": "TH",
    "tam": "TA",
    "tel": "TE",
    "bel": "CYRILLIC",
    "bul": "CYRILLIC",
    "mkd": "CYRILLIC",
    "rus": "CYRILLIC",
    "srp": "CYRILLIC",
    "ukr": "CYRILLIC",
}

# German uses the PP-OCRv6 multilingual recognizer (same file as "en"),
# not the LATIN script model. See select_single_language.
_GERMAN_LANGUAGE = "deu"

_LATIN_LANGUAGE_CODES: set[str] = {
    "afr",
    "cat",
    "ces",
    "dan",
    "est",
    "eus",
    "fin",
    "fra",
    "gle",
    "hrv",
    "hun",
    "ind",
    "isl",
    "ita",
    "lav",
    "lit",
    "mlt",
    "msa",
    "nld",
    "nor",
    "pol",
    "por",
    "ron",
    "slk",
    "slv",
    "spa",
    "sqi",
    "swe",
    "tgl",
    "tur",
    "vie",
}

SUPPORTED_LANGUAGE_CODES: frozenset[str] = frozenset(
    set(_DIRECT_LANGUAGE_MAP) | _LATIN_LANGUAGE_CODES | {_GERMAN_LANGUAGE}
)


def normalize_languages(languages: Sequence[str] | None) -> list[str]:
    if not languages:
        return ["eng"]
    return [
        str(language).strip().lower() for language in languages if str(language).strip()
    ]


def _split_language_codes(languages: Sequence[str]) -> list[str]:
    codes: list[str] = []
    for language in languages:
        codes.extend(part for part in language.split("+") if part)
    return codes


def select_single_language(options: Any) -> str:
    languages = _split_language_codes(
        normalize_languages(getattr(options, "languages", None))
    )
    # Production passes deu+eng. PP-OCRv6 has one recognizer, so German wins.
    german_pair = {_GERMAN_LANGUAGE, "eng"}
    if languages and set(languages) <= german_pair and _GERMAN_LANGUAGE in languages:
        return _GERMAN_LANGUAGE

    if len(languages) != 1:
        raise BadArgsError(
            "RapidOCR supports exactly one language. "
            "Pass a single language to -l/--language."
        )

    language = languages[0]

    if language not in SUPPORTED_LANGUAGE_CODES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGE_CODES))
        raise BadArgsError(
            f"Language '{language}' is not supported by ocrmypdf-rapidocr. "
            f"Supported values: {supported}"
        )
    return language


def map_language_to_langrec_name(language: str) -> str:
    normalized = language.lower()
    if normalized == _GERMAN_LANGUAGE:
        raise KeyError(normalized)
    if normalized in _DIRECT_LANGUAGE_MAP:
        return _DIRECT_LANGUAGE_MAP[normalized]
    if normalized in _LATIN_LANGUAGE_CODES:
        return "LATIN"
    raise KeyError(normalized)

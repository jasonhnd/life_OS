"""Non-LLM utilities for archiver Phase 2 concept extraction.

These are deterministic helpers archiver can call (via Bash tool) before
the LLM judgment step. They handle:

- Frequency counting (which candidate noun phrases appear ≥2 times?)
- Name normalization (case-fold, strip punctuation)
- Slug generation (canonical_name -> concept_id format)
- Stopword filtering (filter out common words)
- Alias deduplication (collapse near-duplicates)

The LLM-driven steps (semantic match, partial-match disambiguation) remain
in archiver.md as agent-prompt logic. This module handles the "boring
parts" that pure Python does better than LLM tokens.
"""

from __future__ import annotations

import re
import string
import unicodedata
from collections import Counter
from typing import Iterable

__all__ = [
    "normalize_name",
    "slug_from_name",
    "is_stopword",
    "count_candidate_frequencies",
    "filter_by_min_frequency",
    "deduplicate_aliases",
    "split_into_candidate_phrases",
    "STOPWORDS_EN",
    "STOPWORDS_ZH_BASIC",
    "STOPWORDS_JA_BASIC",
]


# ─── Stopword sets ─────────────────────────────────────────────────────────


STOPWORDS_EN: frozenset[str] = frozenset(
    {
        "a", "an", "the", "and", "or", "but", "if", "of", "in", "on",
        "at", "to", "for", "with", "from", "by", "is", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "do",
        "does", "did", "will", "would", "could", "should", "may",
        "might", "can", "shall", "this", "that", "these", "those",
        "it", "its", "we", "us", "our", "you", "your", "they", "them",
        "their", "i", "me", "my", "what", "which", "who", "when",
        "where", "why", "how", "not", "no", "yes", "so", "as", "than",
        "then", "also", "just", "only", "very", "more", "most", "less",
    }
)


STOPWORDS_ZH_BASIC: frozenset[str] = frozenset(
    {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
        "都", "一", "上", "也", "很", "到", "说", "要", "去", "你",
        "会", "着", "没有", "看", "好", "自己", "这", "那", "里", "他",
        "她", "它", "我们", "你们", "他们", "这个", "那个", "什么",
        "怎么", "为什么", "因为", "所以", "如果", "或者", "并且",
    }
)


STOPWORDS_JA_BASIC: frozenset[str] = frozenset(
    {
        "の", "に", "は", "を", "が", "と", "で", "から", "まで", "より",
        "へ", "や", "も", "か", "ね", "よ", "わ", "ぞ", "さ", "な",
        "です", "ます", "した", "ある", "いる", "なる", "する", "そう",
        "これ", "それ", "あれ", "どれ", "この", "その", "あの", "どの",
    }
)


def is_stopword(word: str, languages: Iterable[str] = ("en", "zh", "ja")) -> bool:
    """Check if `word` is a stopword in any of the given languages.

    Languages: 'en' (English), 'zh' (Chinese), 'ja' (Japanese).
    """
    word_lower = word.lower().strip()
    if not word_lower:
        return True
    sets = {
        "en": STOPWORDS_EN,
        "zh": STOPWORDS_ZH_BASIC,
        "ja": STOPWORDS_JA_BASIC,
    }
    for lang in languages:
        if word_lower in sets.get(lang, frozenset()):
            return True
    return False


# ─── Name normalization ────────────────────────────────────────────────────


_PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation + "·、。，！？；：")


def normalize_name(name: str) -> str:
    """Canonical form for name comparison.

    - Unicode NFKC normalization (full-width -> half-width, etc.)
    - Case-fold for case-insensitive comparison
    - Strip leading/trailing whitespace
    - Strip punctuation
    - Collapse internal whitespace to single space
    """
    if not name:
        return ""
    # NFKC normalisation
    name = unicodedata.normalize("NFKC", name)
    # Case fold (better than lower() for unicode)
    name = name.casefold()
    # Strip punctuation
    name = name.translate(_PUNCTUATION_TABLE)
    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()
    return name


# ─── Slug generation (concept_id format) ───────────────────────────────────


def slug_from_name(name: str, max_len: int = 60) -> str:
    """Convert a canonical_name into a slug suitable for concept_id.

    - Lowercase
    - Spaces → hyphens
    - Strip non-alphanumeric (preserving CJK characters for searchability)
    - Truncate to max_len
    """
    if not name:
        return ""
    s = unicodedata.normalize("NFKC", name)
    # Replace spaces with hyphens
    s = re.sub(r"\s+", "-", s.strip())
    # Keep alphanumeric, hyphens, and CJK characters
    # CJK Unified Ideographs: \u4e00-\u9fff
    # Hiragana: \u3040-\u309f
    # Katakana: \u30a0-\u30ff
    s = re.sub(r"[^\w\-\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]", "", s)
    # Lowercase ASCII parts
    s = s.lower()
    # Collapse multiple hyphens
    s = re.sub(r"-+", "-", s)
    # Strip leading/trailing hyphens
    s = s.strip("-")
    # Truncate
    if len(s) > max_len:
        s = s[:max_len].rstrip("-")
    return s


# ─── Phrase splitting + frequency ──────────────────────────────────────────


_PHRASE_PATTERN = re.compile(
    # Match: word characters (with hyphens/apostrophes) OR CJK characters runs
    r"\b[\w\-']{2,}\b"
    r"|[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]{2,}",
    re.UNICODE,
)


def split_into_candidate_phrases(text: str) -> list[str]:
    """Extract candidate noun phrases from raw text.

    Heuristic: word-tokens of length ≥ 2 (skips single chars / particles).
    Returns lowercased phrases for case-insensitive frequency counting.
    """
    if not text:
        return []
    matches = _PHRASE_PATTERN.findall(text)
    return [m.lower() for m in matches if not is_stopword(m)]


def count_candidate_frequencies(text: str) -> Counter:
    """Count occurrences of candidate noun phrases in `text`.

    Returns a Counter keyed by normalized phrase.
    """
    candidates = split_into_candidate_phrases(text)
    return Counter(candidates)


def filter_by_min_frequency(
    counts: Counter, min_count: int = 2
) -> Counter:
    """Keep only candidates appearing at least `min_count` times.

    Per archiver Phase 2 Step A criterion: "Is referenced ≥ 2 times in this session".
    """
    return Counter({k: v for k, v in counts.items() if v >= min_count})


# ─── Alias deduplication ───────────────────────────────────────────────────


def deduplicate_aliases(aliases: list[str]) -> list[str]:
    """Collapse near-duplicate aliases by normalized form.

    Preserves first occurrence of each normalized form. Returns ORIGINAL
    surface forms (not normalized).
    """
    seen: set[str] = set()
    out: list[str] = []
    for alias in aliases:
        normalized = normalize_name(alias)
        if normalized and normalized not in seen:
            seen.add(normalized)
            out.append(alias)
    return out

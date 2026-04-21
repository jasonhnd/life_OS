"""Tests for tools.lib.cortex.extraction — non-LLM concept extraction utilities."""

from __future__ import annotations

from collections import Counter

import pytest

from tools.lib.cortex.extraction import (
    STOPWORDS_EN,
    STOPWORDS_JA_BASIC,
    STOPWORDS_ZH_BASIC,
    count_candidate_frequencies,
    deduplicate_aliases,
    filter_by_min_frequency,
    is_stopword,
    normalize_name,
    slug_from_name,
    split_into_candidate_phrases,
)


# ─── normalize_name ─────────────────────────────────────────────────────────


class TestNormalizeName:
    def test_lowercase(self):
        assert normalize_name("PassPay") == "passpay"

    def test_strip_whitespace(self):
        assert normalize_name("  hello  ") == "hello"

    def test_collapse_internal_whitespace(self):
        assert normalize_name("hello   world") == "hello world"

    def test_strip_punctuation(self):
        assert normalize_name("Hello, World!") == "hello world"
        assert normalize_name("PassPay·Architecture") == "passpayarchitecture"

    def test_empty(self):
        assert normalize_name("") == ""
        assert normalize_name("   ") == ""

    def test_cjk_preserved(self):
        # Chinese characters should pass through (no punctuation, no case)
        assert normalize_name("三省六部") == "三省六部"

    def test_full_width_to_half_width(self):
        # NFKC normalization should convert full-width to half-width
        assert normalize_name("ＰａｓｓＰａｙ") == "passpay"


# ─── slug_from_name ─────────────────────────────────────────────────────────


class TestSlugFromName:
    def test_simple_lowercase(self):
        assert slug_from_name("PassPay Architecture") == "passpay-architecture"

    def test_cjk_preserved(self):
        assert slug_from_name("三省六部") == "三省六部"

    def test_strip_punctuation(self):
        assert slug_from_name("PassPay v0.6 — Refinement") == "passpay-v06-refinement"

    def test_empty(self):
        assert slug_from_name("") == ""

    def test_max_length_truncation(self):
        long = "a" * 100
        result = slug_from_name(long, max_len=10)
        assert len(result) <= 10

    def test_collapse_multiple_hyphens(self):
        assert slug_from_name("hello   --   world") == "hello-world"

    def test_strip_leading_trailing_hyphens(self):
        assert slug_from_name("---test---") == "test"


# ─── is_stopword ────────────────────────────────────────────────────────────


class TestIsStopword:
    @pytest.mark.parametrize("word", ["the", "and", "of", "to", "a", "an"])
    def test_english_stopwords(self, word: str):
        assert is_stopword(word)

    def test_case_insensitive(self):
        assert is_stopword("THE")
        assert is_stopword("And")

    @pytest.mark.parametrize("word", ["的", "了", "在", "是", "我"])
    def test_chinese_stopwords(self, word: str):
        assert is_stopword(word)

    @pytest.mark.parametrize("word", ["の", "は", "を", "が"])
    def test_japanese_stopwords(self, word: str):
        assert is_stopword(word)

    def test_meaningful_words_not_stopwords(self):
        assert not is_stopword("PassPay")
        assert not is_stopword("compliance")
        assert not is_stopword("三省六部")

    def test_empty_treated_as_stopword(self):
        assert is_stopword("")
        assert is_stopword("   ")

    def test_language_subset(self):
        # Only check English — Chinese stopword should not match
        assert not is_stopword("的", languages=["en"])
        # Only check Chinese — English stopword should not match
        assert not is_stopword("the", languages=["zh"])


# ─── split_into_candidate_phrases ───────────────────────────────────────────


class TestSplitPhrases:
    def test_english_text(self):
        text = "The PassPay architecture is compliance-aware"
        phrases = split_into_candidate_phrases(text)
        # Stopwords filtered: the, is
        assert "passpay" in phrases
        assert "architecture" in phrases
        assert "compliance-aware" in phrases
        assert "the" not in phrases

    def test_minimum_length_filter(self):
        # Single-char words should be excluded
        text = "I a b c PassPay"
        phrases = split_into_candidate_phrases(text)
        assert "passpay" in phrases
        assert "a" not in phrases
        assert "b" not in phrases

    def test_empty_text(self):
        assert split_into_candidate_phrases("") == []
        assert split_into_candidate_phrases("   ") == []

    def test_cjk_phrases(self):
        text = "三省六部制 是 唐朝 的 治理 制度"
        phrases = split_into_candidate_phrases(text)
        # Stopwords filtered: 是, 的
        assert "三省六部制" in phrases or "三省六部" in phrases or "三省" in phrases
        # 是 and 的 should NOT appear
        assert "是" not in phrases
        assert "的" not in phrases


# ─── count_candidate_frequencies + filter ──────────────────────────────────


class TestFrequencyCounting:
    def test_count(self):
        text = "PassPay PassPay compliance compliance compliance Other"
        counts = count_candidate_frequencies(text)
        assert counts["passpay"] == 2
        assert counts["compliance"] == 3
        assert counts["other"] == 1

    def test_filter_min_frequency(self):
        counts = Counter({"a": 5, "b": 2, "c": 1})
        filtered = filter_by_min_frequency(counts, min_count=2)
        assert filtered["a"] == 5
        assert filtered["b"] == 2
        assert "c" not in filtered

    def test_default_threshold_is_2(self):
        counts = Counter({"common": 10, "rare": 1})
        filtered = filter_by_min_frequency(counts)  # default 2
        assert "common" in filtered
        assert "rare" not in filtered


# ─── deduplicate_aliases ────────────────────────────────────────────────────


class TestDeduplicateAliases:
    def test_keep_first_occurrence(self):
        aliases = ["PassPay", "passpay", "PASSPAY"]
        result = deduplicate_aliases(aliases)
        assert result == ["PassPay"]

    def test_preserve_distinct_aliases(self):
        aliases = ["PassPay", "Pay-Pass", "passport"]
        result = deduplicate_aliases(aliases)
        assert len(result) == 3
        assert "PassPay" in result
        assert "Pay-Pass" in result
        assert "passport" in result

    def test_skip_empty_aliases(self):
        aliases = ["PassPay", "", "  ", "Compliance"]
        result = deduplicate_aliases(aliases)
        assert result == ["PassPay", "Compliance"]

    def test_unicode_dedup(self):
        # Full-width vs half-width should dedup via NFKC
        aliases = ["PassPay", "ＰａｓｓＰａｙ"]
        result = deduplicate_aliases(aliases)
        assert len(result) == 1

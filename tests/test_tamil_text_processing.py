import sys
from pathlib import Path

# Ensure project root is on sys.path for imports when running tests from tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from indic_tamil_tts import (
    TAMIL_TECH_REPLACEMENTS,
    apply_tamil_tech_replacements,
    split_tamil_text,
)


def test_apply_tamil_tech_replacements_swaps_known_terms():
    text = "We use SQL and API in this UAT script."
    cleaned = apply_tamil_tech_replacements(text)

    assert "SQL" not in cleaned
    assert "API" not in cleaned
    assert "UAT" not in cleaned
    assert "எஸ்.க்யூ.எல்." in cleaned
    assert "ஏ.பி.ஐ." in cleaned


def test_apply_tamil_tech_replacements_only_matches_whole_words():
    # "IT" should not match inside "ITEM" or similar longer words
    text = "ITEM count and IT support."
    cleaned = apply_tamil_tech_replacements(text)

    assert "ITEM" in cleaned
    assert "ஐ.டி." in cleaned


def test_apply_tamil_tech_replacements_covers_all_defined_terms():
    for original, replacement in TAMIL_TECH_REPLACEMENTS:
        text = f"Sample sentence with {original} inside it."
        cleaned = apply_tamil_tech_replacements(text)
        assert original not in cleaned
        assert replacement in cleaned


def test_split_tamil_text_respects_chunk_size():
    sentence = "இது ஒரு மாதிரி வாக்கியம். "
    paragraph = sentence * 100
    chunks = split_tamil_text(paragraph, chunk_size=200)

    assert len(chunks) > 1
    assert all(len(chunk) <= 220 for chunk in chunks)  # small buffer for join spacing


def test_split_tamil_text_splits_on_question_and_exclamation_marks():
    text = "இது என்ன? இது ஒரு சோதனை! இது முடிந்தது."
    chunks = split_tamil_text(text, chunk_size=15)

    # Each sentence-ending punctuation mark should force a split point,
    # not just '.'
    joined = " ".join(chunks)
    assert "என்ன?" in joined
    assert "சோதனை!" in joined
    assert len(chunks) >= 2


def test_split_tamil_text_handles_empty_input():
    assert split_tamil_text("", chunk_size=100) == []


def test_split_tamil_text_single_short_sentence_returns_one_chunk():
    chunks = split_tamil_text("வணக்கம்.", chunk_size=100)
    assert len(chunks) == 1
    assert chunks[0] == "வணக்கம்."

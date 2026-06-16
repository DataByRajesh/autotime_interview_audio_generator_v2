import sys
from pathlib import Path

# Ensure project root is on sys.path for imports when running tests from tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from interview_audio_generator_v2 import clean_text_for_tts, split_text


def test_clean_technical_replacements():
    text = "SQL and API -> result. INNER JOIN test."
    cleaned = clean_text_for_tts(text)

    assert "S Q L" in cleaned
    assert "A P I" in cleaned
    assert " to " in cleaned
    assert "inner join" in cleaned.lower()


def test_split_text_respects_chunk_size():
    paragraph = "Sentence. " * 500
    chunks = split_text(paragraph, max_chars=1000)

    assert isinstance(chunks, list)
    assert len(chunks) >= 1

    combined = " ".join(chunks)
    assert "Sentence." in combined

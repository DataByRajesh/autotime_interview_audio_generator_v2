import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tamil_glossary_module import apply_tamil_glossary
from tamil_transliteration_dict import transliterate_tech_terms


def test_apply_tamil_glossary_keeps_tamil_suffixes_attached():
    text = (
        "Payment reconciliation-?? simple meaning ????????, "
        "payment system-?? ????????? record-?? settlement system-?? ????????? "
        "record-?? match ?????? ????? check ????????."
    )

    cleaned = apply_tamil_glossary(text)

    assert "payment" not in cleaned.lower()
    assert "reconciliation" not in cleaned.lower()
    assert "system" not in cleaned.lower()
    assert "record" not in cleaned.lower()
    assert "settlement" not in cleaned.lower()
    assert "match" not in cleaned.lower()
    assert "check" not in cleaned.lower()
    assert "simple meaning" in cleaned
    assert "-??" in cleaned
    assert "-??" in cleaned
    assert "-??" in cleaned


def test_shared_transliteration_uses_project_glossary_entries():
    cleaned = transliterate_tech_terms("Payment reconciliation system record settlement match check")

    assert "Payment" not in cleaned
    assert "reconciliation" not in cleaned
    assert "system" not in cleaned
    assert "record" not in cleaned
    assert "settlement" not in cleaned
    assert "match" not in cleaned
    assert "check" not in cleaned

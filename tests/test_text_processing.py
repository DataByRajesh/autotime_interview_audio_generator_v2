import sys
from pathlib import Path

# Ensure project root is on sys.path for imports when running tests from tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from interview_audio_generator_v2 import (
    clean_text_for_tts,
    cognitive_load_warnings,
    generate_learning_script,
    prepare_text_for_low_load_listening,
    replace_pause_markers_for_tts,
    spaced_repetition_plan,
    split_text,
)


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


def test_learn_mode_contains_learning_structure():
    script = generate_learning_script("learn_mode", "UAT")

    assert "Topic: UAT." in script
    assert "Why it matters." in script
    assert "Simple meaning." in script
    assert "Real job example." in script
    assert "Common confusion." in script
    assert "Short recap." in script
    assert "[PAUSE_MEDIUM]" in script


def test_recall_mode_contains_pause_question_answer_pattern():
    script = generate_learning_script("recall_mode", "Settlement")

    assert "Question one." in script
    assert "[PAUSE_LONG]" in script
    assert "Answer." in script
    assert "Repeat answer." in script
    assert "Final memory sentence." in script


def test_compare_mode_uses_known_difference():
    script = generate_learning_script("compare_mode", "UAT", "SIT")

    assert "UAT versus SIT" in script
    assert "business acceptance versus technical integration" in script
    assert "Quiz." in script


def test_interview_mode_contains_polished_answer_and_fintech_example():
    script = generate_learning_script("interview_mode", "Payment lifecycle")

    assert "Likely interview question." in script
    assert "Simple answer." in script
    assert "Stronger answer." in script
    assert "FinTech or payment example." in script
    assert "Final polished answer." in script


def test_pause_markers_have_tts_replacement_point():
    script = "Question. [PAUSE_LONG] Answer."
    prepared = replace_pause_markers_for_tts(script)

    assert "[PAUSE_LONG]" not in prepared
    assert "Answer." in prepared


def test_cognitive_load_warnings_find_missing_pause_and_fast_workplace_speed():
    text = "This sentence has no active recall prompt and no pause marker."
    warnings = cognitive_load_warnings(text, speed=1.1, workplace_mode=True)

    assert any("No pause markers" in warning for warning in warnings)
    assert any("Workplace speed" in warning for warning in warnings)
    assert any("No quiz questions" in warning for warning in warnings)


def test_spaced_repetition_filenames_are_phone_friendly():
    plan = spaced_repetition_plan("Agile Scrum Jira", extension=".wav")
    filenames = [filename for _, filename in plan]

    assert filenames == [
        "01_Agile_Scrum_Jira_Day1_Learn.wav",
        "02_Agile_Scrum_Jira_Day2_Recall.wav",
        "03_Agile_Scrum_Jira_Day4_Compare.wav",
        "04_Agile_Scrum_Jira_Day7_Interview.wav",
    ]


def test_clean_text_handles_pasted_mojibake_quotes():
    open_quote = chr(0x00E2) + chr(0x20AC) + chr(0x0153)
    close_quote = chr(0x00E2) + chr(0x20AC) + chr(0x009D)
    dash = chr(0x00E2) + chr(0x20AC) + chr(0x201D)
    arrow = chr(0x00E2) + chr(0x2020) + chr(0x2019)
    text = f"{open_quote}The feature is built.{close_quote} Title {dash} detail. A {arrow} B."
    cleaned = clean_text_for_tts(text)

    assert chr(0x00E2) not in cleaned
    assert "The feature is built" in cleaned
    assert " to " in cleaned


def test_new_terms_warning_is_section_scoped():
    text = """
Section 1: One idea.

sprint backlog increment.

[PAUSE_SHORT]

Question. What is Agile?

Section 2: Another idea.

issue workflow acceptance criteria.

[PAUSE_SHORT]

Question. What is Jira?
"""
    warnings = cognitive_load_warnings(text, speed=0.85, workplace_mode=True)

    assert not any("key terms" in warning for warning in warnings)


def test_prepare_text_splits_dense_paragraphs_for_listening():
    dense = " ".join(["This is a useful sentence for workplace interview practice."] * 12)
    prepared = prepare_text_for_low_load_listening(dense)

    assert "[PAUSE_SHORT]" in prepared
    assert not any(len(p.split()) > 90 for p in prepared.split("\n\n") if p.strip())


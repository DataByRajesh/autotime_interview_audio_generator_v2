import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from script_quality_review import review_script


def test_script_quality_review_flags_dense_chatbot_text():
    text = (
        "It is important to note that UAT plays a crucial role in today's fast-paced world "
        "because various aspects of business validation must be considered by stakeholders, "
        "testers, developers, product owners, and business users before a robust solution can "
        "be released into production without unnecessary risk or confusion for operational teams."
    )

    report = review_script(text)

    assert report.score < 85
    assert any(f.category == "listenability" for f in report.findings)
    assert any(f.category == "learning design" for f in report.findings)
    assert "Return only the improved script text" in report.rewrite_prompt


def test_script_quality_review_accepts_audio_friendly_learning_script():
    text = """
Topic: UAT.

Simple meaning.
UAT means business users check whether the solution works for real business needs.

[PAUSE_MEDIUM]

Why it matters.
It reduces release risk because users confirm the workflow before production.
The team gets evidence before the change reaches customers.

Real job example.
In a payments project, operations users test failed payment investigation before sign-off.
They open a failed transaction, check the reason, add a note, and confirm the status.
This shows that the screen supports the real business process.

[PAUSE_MEDIUM]

Second example.
A finance user may test a settlement report before month end.
They check matched payments, missing payments, and totals.
The goal is not only to click buttons.
The goal is to prove the report supports a real control.

Common confusion.
UAT is not the same as SIT.
SIT checks whether systems connect correctly.
UAT checks whether business users can accept the outcome.

[PAUSE_SHORT]

Question one. What does UAT prove?

[PAUSE_LONG]

Answer. It proves the solution is acceptable for the business process.

Question two. Who should be involved in UAT?

[PAUSE_LONG]

Answer. Real business users, product owners, analysts, testers, and support teams may be involved.

Interview answer.
I support UAT by preparing scenarios, clarifying expected results, tracking defects, and collecting sign-off evidence.
If a defect appears, I explain the business impact clearly.
Then I help the team decide whether to fix, retest, or defer with approval.

Short recap.
UAT is business acceptance, not technical integration testing.
Good UAT has real scenarios, clear evidence, defect tracking, and business sign-off.
"""

    report = review_script(text)

    assert report.score >= 85
    assert report.verdict == "ready for audio"
    assert report.metrics.pause_markers == 5
    assert report.metrics.recall_prompts >= 2
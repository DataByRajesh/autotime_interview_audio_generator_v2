import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fintech_role_alignment import review_fintech_alignment
from script_quality_review import review_script


def test_fintech_alignment_rewards_eu_role_specific_script():
    text = """
As a Business Systems Analyst in an EU payments team, I would map the payment lifecycle from authorization to settlement and reconciliation.
I would clarify acceptance criteria, document the API behaviour, and validate UAT evidence with operations users.
For a SEPA instant payment scenario, I check status messages, audit trail logs, expected results, and exception reports.
If a DORA-related vendor incident affects a critical function, I support incident reporting, workaround tracking, stakeholder updates, and post incident actions.
The interview answer should explain the situation, action, result, business impact, and control evidence.
"""

    report = review_fintech_alignment(text, target="eu_fintech")

    assert report.score >= 85
    assert report.analyst_action_hits >= 2
    assert report.evidence_hits >= 2
    assert report.jurisdiction_hits["eu"] >= 1
    assert sum(1 for count in report.domain_hits.values() if count > 0) >= 2


def test_fintech_alignment_flags_missing_ireland_context():
    text = """
This lesson explains project communication in a general technology team.
The analyst writes notes, attends meetings, and helps people understand requirements.
"""

    report = review_fintech_alignment(text, target="ireland_fintech")

    assert report.score < 70
    assert any(f.category == "Ireland context" for f in report.findings)
    assert any("Dublin" in item or "Ireland" in item for item in report.rewrite_focus)


def test_script_quality_review_includes_fintech_alignment_for_netherlands_target():
    text = """
Topic: API incident in a payment platform.

As an analyst, I investigate failed webhook updates and compare logs with payment status records.
I document expected result, actual result, defect impact, and UAT evidence.

Question. What should I check first?

[PAUSE_LONG]

Answer. I check the API response, retry status, audit trail, and reconciliation report.
"""

    report = review_script(text, target="netherlands_fintech")

    assert report.fintech_alignment is not None
    assert any("Netherlands context" in f.category for f in report.findings)
    assert "EU fintech role alignment" in report.rewrite_prompt
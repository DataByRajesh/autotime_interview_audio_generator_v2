"""EU fintech role-alignment checks for learning scripts.

The goal is to help a script sound useful for Business Systems Analyst,
Product Analyst, QA/UAT, production support, and data/control roles in EU
fintech settings, especially Ireland and the Netherlands.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

EU_FINTECH_TARGETS = {"eu_fintech", "ireland_fintech", "netherlands_fintech"}

ROLE_PATTERNS = {
    "business systems analyst": (
        "requirement", "user story", "acceptance criteria", "process flow",
        "stakeholder", "traceability", "business rule", "uat", "jira",
    ),
    "product and delivery": (
        "product owner", "roadmap", "backlog", "sprint", "release",
        "priority", "scope", "dependency", "mvp", "delivery",
    ),
    "qa and uat": (
        "test scenario", "test case", "defect", "retest", "regression",
        "expected result", "sign-off", "evidence", "uat", "sit",
    ),
    "production support": (
        "incident", "root cause", "workaround", "sla", "monitoring",
        "alert", "runbook", "post incident", "service desk", "severity",
    ),
    "data and reporting": (
        "sql", "reconciliation", "data quality", "report", "dashboard",
        "control", "audit", "lineage", "csv", "json",
    ),
}

DOMAIN_PATTERNS = {
    "payments lifecycle": (
        "payment", "authorization", "capture", "clearing", "settlement",
        "reconciliation", "refund", "chargeback", "merchant", "scheme",
    ),
    "open banking and APIs": (
        "open banking", "psd2", "psd3", "psr", "api", "webhook",
        "consent", "strong customer authentication", "sca", "account information",
    ),
    "risk and compliance": (
        "aml", "kyc", "fraud", "sanction", "screening", "safeguarding",
        "consumer protection", "gdpr", "audit trail", "control evidence",
    ),
    "operational resilience": (
        "dora", "ict risk", "incident reporting", "third-party", "outsourcing",
        "business continuity", "resilience testing", "critical function", "vendor",
    ),
    "eu rails and messages": (
        "sepa", "instant payment", "iso 20022", "iban", "bic", "pacs",
        "pain", "camt", "euro", "cross-border",
    ),
}

JURISDICTION_PATTERNS = {
    "eu": ("eu", "european", "eea", "sepa", "eba", "psd2", "psd3", "psr", "dora", "gdpr"),
    "ireland": ("ireland", "irish", "central bank of ireland", "cbi", "dublin"),
    "netherlands": ("netherlands", "dutch", "de nederlandsche bank", "dnb", "amsterdam"),
}

ANALYST_ACTION_PATTERNS = (
    "i would", "as an analyst", "i check", "i map", "i document", "i clarify",
    "i validate", "i compare", "i investigate", "i escalate", "i support",
    "the analyst", "business analyst", "systems analyst",
)

EVIDENCE_PATTERNS = (
    "evidence", "audit trail", "sign-off", "traceability", "control", "log",
    "screenshot", "report", "sample record", "expected result", "reconciliation",
)

INTERVIEW_PATTERNS = (
    "interview", "answer", "example", "situation", "action", "result",
    "stakeholder", "impact", "production", "release", "business value",
)


@dataclass(frozen=True)
class FintechAlignmentFinding:
    severity: str
    category: str
    message: str
    suggestion: str


@dataclass(frozen=True)
class FintechAlignmentReport:
    target: str
    score: int
    role_hits: dict[str, int]
    domain_hits: dict[str, int]
    jurisdiction_hits: dict[str, int]
    analyst_action_hits: int
    evidence_hits: int
    interview_hits: int
    findings: list[FintechAlignmentFinding]
    rewrite_focus: list[str]


def _count_term_hits(text: str, terms: tuple[str, ...]) -> int:
    total = 0
    for term in terms:
        total += len(re.findall(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE))
    return total


def _count_group_hits(text: str, groups: dict[str, tuple[str, ...]]) -> dict[str, int]:
    return {name: _count_term_hits(text, terms) for name, terms in groups.items()}


def _add(findings: list[FintechAlignmentFinding], severity: str, category: str, message: str, suggestion: str) -> None:
    findings.append(FintechAlignmentFinding(severity, category, message, suggestion))


def _score(findings: list[FintechAlignmentFinding]) -> int:
    penalty = 0
    for finding in findings:
        if finding.severity == "high":
            penalty += 16
        elif finding.severity == "medium":
            penalty += 9
        else:
            penalty += 4
    return max(0, min(100, 100 - penalty))


def _rewrite_focus(findings: list[FintechAlignmentFinding], target: str) -> list[str]:
    focus = [finding.suggestion for finding in findings]
    if not focus:
        focus.append("Keep the EU fintech examples practical, role-specific, and evidence-based.")
    if target == "ireland_fintech":
        focus.append("Prefer Ireland examples involving Dublin-based payment, e-money, banking, or regtech teams where relevant.")
    if target == "netherlands_fintech":
        focus.append("Prefer Netherlands examples involving Dutch payment institutions, Amsterdam teams, SEPA, open banking, or DNB-supervised contexts where relevant.")
    return focus


def review_fintech_alignment(text: str, target: str = "eu_fintech") -> FintechAlignmentReport:
    role_hits = _count_group_hits(text, ROLE_PATTERNS)
    domain_hits = _count_group_hits(text, DOMAIN_PATTERNS)
    jurisdiction_hits = _count_group_hits(text, JURISDICTION_PATTERNS)
    analyst_action_hits = _count_term_hits(text, ANALYST_ACTION_PATTERNS)
    evidence_hits = _count_term_hits(text, EVIDENCE_PATTERNS)
    interview_hits = _count_term_hits(text, INTERVIEW_PATTERNS)

    findings: list[FintechAlignmentFinding] = []
    active_roles = [name for name, count in role_hits.items() if count > 0]
    active_domains = [name for name, count in domain_hits.items() if count > 0]

    if len(active_roles) < 2:
        _add(
            findings,
            "medium",
            "role relevance",
            "The script is not strongly connected to fintech analyst job activities.",
            "Add Business Systems Analyst, UAT/QA, production support, data, or product-delivery actions.",
        )
    if len(active_domains) < 2:
        _add(
            findings,
            "high",
            "domain relevance",
            "The script lacks enough fintech domain anchors.",
            "Add concrete payment, open banking/API, AML/KYC, reconciliation, SEPA, DORA, or operational resilience examples.",
        )
    if analyst_action_hits < 2:
        _add(
            findings,
            "medium",
            "analyst behaviour",
            "The listener may not learn what they personally do in the role.",
            "Use phrases like: as an analyst I clarify, map, document, validate, investigate, escalate, and evidence.",
        )
    if evidence_hits < 2:
        _add(
            findings,
            "medium",
            "evidence mindset",
            "The script does not show enough evidence, controls, or audit trail thinking.",
            "Add sign-off evidence, sample records, audit logs, expected results, reconciliation checks, or control evidence.",
        )
    if interview_hits < 2:
        _add(
            findings,
            "low",
            "interview readiness",
            "The script may not convert well into interview answers.",
            "Add one polished answer with situation, action, result, business impact, and stakeholder communication.",
        )

    if target in {"eu_fintech", "ireland_fintech", "netherlands_fintech"} and jurisdiction_hits["eu"] < 1:
        _add(
            findings,
            "medium",
            "EU context",
            "The script does not clearly signal EU fintech context.",
            "Mention EU/EEA context through SEPA, PSD2/PSD3, PSR, DORA, GDPR, EBA, or cross-border payments.",
        )
    if target == "ireland_fintech" and jurisdiction_hits["ireland"] < 1:
        _add(
            findings,
            "medium",
            "Ireland context",
            "Ireland target selected, but Ireland-specific context is missing.",
            "Add an Ireland or Dublin example, and mention Central Bank of Ireland context only when relevant.",
        )
    if target == "netherlands_fintech" and jurisdiction_hits["netherlands"] < 1:
        _add(
            findings,
            "medium",
            "Netherlands context",
            "Netherlands target selected, but Dutch context is missing.",
            "Add a Netherlands, Dutch payment institution, Amsterdam, SEPA, or DNB-supervised context where relevant.",
        )

    return FintechAlignmentReport(
        target=target,
        score=_score(findings),
        role_hits=role_hits,
        domain_hits=domain_hits,
        jurisdiction_hits=jurisdiction_hits,
        analyst_action_hits=analyst_action_hits,
        evidence_hits=evidence_hits,
        interview_hits=interview_hits,
        findings=findings,
        rewrite_focus=_rewrite_focus(findings, target),
    )
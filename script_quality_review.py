"""
Quality review tool for chatbot-produced learning scripts.

This script does not call OpenAI or Claude directly. It audits a .txt script locally,
then creates a rewrite prompt you can paste into any chatbot to improve the content
before sending it to the audio generator.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from fintech_role_alignment import EU_FINTECH_TARGETS, review_fintech_alignment

PAUSE_MARKERS = ("[PAUSE_SHORT]", "[PAUSE_MEDIUM]", "[PAUSE_LONG]")
RECALL_PATTERNS = (
    r"\bquestion\b",
    r"\bquiz\b",
    r"\bwhat\b",
    r"\bwhy\b",
    r"\bhow\b",
    r"\bwhich\b",
    r"\btry to answer\b",
    r"\bpause and answer\b",
)
EXAMPLE_PATTERNS = (
    r"\bexample\b",
    r"\bscenario\b",
    r"\bfor instance\b",
    r"\bin a real\b",
    r"\bin a project\b",
    r"\bin a fintech\b",
    r"\bin payments\b",
)
STRUCTURE_PATTERNS = (
    r"\btopic\b",
    r"\bwhy it matters\b",
    r"\bsimple meaning\b",
    r"\bcommon confusion\b",
    r"\brecap\b",
    r"\bsummary\b",
    r"\binterview answer\b",
)
FILLER_PHRASES = (
    "it is important to note that",
    "in today's fast-paced world",
    "plays a crucial role",
    "delve into",
    "comprehensive overview",
    "various aspects",
    "robust solution",
    "seamless experience",
    "leverage",
    "utilize",
)
TTS_RISK_PATTERNS = (
    r"```",
    r"`[^`]+`",
    r"https?://\S+",
    r"\|",
    r"={3,}",
    r"-{3,}",
    r"\[[xX ]\]",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    message: str
    suggestion: str


@dataclass(frozen=True)
class ScriptMetrics:
    words: int
    paragraphs: int
    sentences: int
    avg_sentence_words: float
    max_sentence_words: int
    dense_paragraphs: int
    pause_markers: int
    recall_prompts: int
    examples: int
    repeated_openings: int
    filler_hits: int
    tts_risk_hits: int


@dataclass(frozen=True)
class QualityReport:
    score: int
    verdict: str
    metrics: ScriptMetrics
    findings: list[Finding]
    rewrite_prompt: str
    fintech_alignment: object | None = None


def words_in(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_']+|[^\W\s]+", text, flags=re.UNICODE)


def split_sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [piece.strip() for piece in pieces if piece.strip()]


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


def count_matches(patterns: tuple[str, ...], text: str) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def repeated_sentence_openings(sentences: list[str]) -> int:
    openings: dict[str, int] = {}
    for sentence in sentences:
        opening = " ".join(words_in(sentence.lower())[:4])
        if len(opening.split()) >= 3:
            openings[opening] = openings.get(opening, 0) + 1
    return sum(count - 1 for count in openings.values() if count > 1)


def normalize_script_text(text: str) -> str:
    if "\\n" in text and "\n" not in text:
        text = text.replace("\\r\\n", "\n").replace("\\n", "\n")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def build_metrics(text: str) -> ScriptMetrics:
    paragraphs = split_paragraphs(text)
    sentences = split_sentences(text)
    sentence_lengths = [len(words_in(sentence)) for sentence in sentences]
    dense_paragraphs = sum(1 for paragraph in paragraphs if len(words_in(paragraph)) > 90)
    lowered = text.lower()

    return ScriptMetrics(
        words=len(words_in(text)),
        paragraphs=len(paragraphs),
        sentences=len(sentences),
        avg_sentence_words=(sum(sentence_lengths) / len(sentence_lengths)) if sentence_lengths else 0.0,
        max_sentence_words=max(sentence_lengths, default=0),
        dense_paragraphs=dense_paragraphs,
        pause_markers=sum(text.count(marker) for marker in PAUSE_MARKERS),
        recall_prompts=count_matches(RECALL_PATTERNS, text),
        examples=count_matches(EXAMPLE_PATTERNS, text),
        repeated_openings=repeated_sentence_openings(sentences),
        filler_hits=sum(lowered.count(phrase) for phrase in FILLER_PHRASES),
        tts_risk_hits=count_matches(TTS_RISK_PATTERNS, text),
    )


def add_finding(findings: list[Finding], severity: str, category: str, message: str, suggestion: str) -> None:
    findings.append(Finding(severity=severity, category=category, message=message, suggestion=suggestion))


def build_findings(metrics: ScriptMetrics, text: str, target: str) -> list[Finding]:
    findings: list[Finding] = []
    lowered = text.lower()

    if metrics.words < 250:
        add_finding(findings, "medium", "depth", "The script is short for a learning audio.", "Add one practical example, one common confusion, and a short recap.")
    if metrics.avg_sentence_words > 18:
        add_finding(findings, "high", "listenability", f"Average sentence length is {metrics.avg_sentence_words:.1f} words.", "Rewrite into shorter spoken sentences, ideally 10 to 18 words each.")
    if metrics.max_sentence_words > 35:
        add_finding(findings, "high", "listenability", f"Longest sentence is {metrics.max_sentence_words} words.", "Split long sentences before TTS so the voice has natural breathing points.")
    if metrics.dense_paragraphs:
        add_finding(findings, "high", "structure", f"Found {metrics.dense_paragraphs} dense paragraph(s).", "Break dense blocks into smaller paragraphs and insert pause markers.")
    if metrics.pause_markers == 0:
        add_finding(findings, "medium", "audio pacing", "No pause markers found.", "Add [PAUSE_SHORT], [PAUSE_MEDIUM], or [PAUSE_LONG] after important ideas and questions.")
    if metrics.recall_prompts < 2:
        add_finding(findings, "medium", "learning design", "Few active recall prompts found.", "Add question-pause-answer sections so the listener has to retrieve the idea.")
    if metrics.examples < 2:
        add_finding(findings, "medium", "practical value", "Few concrete examples found.", "Add workplace or FinTech examples that show the concept in action.")
    if metrics.repeated_openings > 4:
        add_finding(findings, "low", "style", f"Found {metrics.repeated_openings} repeated sentence openings.", "Vary sentence starts and remove copy-paste style repetition.")
    if metrics.filler_hits:
        add_finding(findings, "low", "style", f"Found {metrics.filler_hits} generic AI-style phrase(s).", "Replace vague phrases with plain job language and specific examples.")
    if metrics.tts_risk_hits:
        add_finding(findings, "medium", "tts readiness", f"Found {metrics.tts_risk_hits} TTS-risk formatting item(s).", "Remove markdown tables, code fences, URLs, and decorative separators before audio generation.")

    structure_hits = count_matches(STRUCTURE_PATTERNS, text)
    if structure_hits < 3:
        add_finding(findings, "medium", "structure", "The script does not clearly show a learning structure.", "Use sections like simple meaning, why it matters, job example, common confusion, quiz, recap.")

    if target == "interview" and "star" not in lowered and "situation" not in lowered:
        add_finding(findings, "medium", "interview quality", "Interview target selected, but no answer structure was detected.", "Add a polished answer using situation, action, result, and evidence.")
    if target == "bilingual" and not re.search(r"[^\x00-\x7F]", text):
        add_finding(findings, "low", "bilingual", "Bilingual target selected, but the text looks English-only.", "Add bilingual explanation only where it helps clarity, and keep technical terms consistent.")

    return findings


def calculate_score(findings: list[Finding]) -> int:
    penalty = 0
    for finding in findings:
        if finding.severity == "high":
            penalty += 14
        elif finding.severity == "medium":
            penalty += 8
        else:
            penalty += 3
    return max(0, min(100, 100 - penalty))


def verdict_for(score: int) -> str:
    if score >= 85:
        return "ready for audio"
    if score >= 70:
        return "good, needs light editing"
    if score >= 50:
        return "needs rewrite before audio"
    return "major rewrite recommended"


def build_rewrite_prompt(
    text: str,
    findings: list[Finding],
    target: str,
    fintech_focus: list[str] | None = None,
) -> str:
    issues = "\n".join(f"- {f.category}: {f.suggestion}" for f in findings) or "- Keep the script clear, practical, and easy to listen to."
    focus = "\n".join(f"- {item}" for item in (fintech_focus or []))
    fintech_section = f"\nEU fintech role alignment:\n{focus}\n" if focus else ""
    return f"""You are improving a learning script that will be converted to audio.

Target: {target}

Rewrite goals:
- Keep the original meaning and domain accuracy.
- Use spoken, simple, practical language.
- Keep sentences mostly under 18 words.
- Use short paragraphs for low cognitive load listening.
- Add concrete workplace or FinTech examples where useful.
- Add active recall using question, pause marker, answer.
- Add [PAUSE_SHORT], [PAUSE_MEDIUM], and [PAUSE_LONG] where they help pacing.
- Remove markdown tables, code fences, decorative separators, URLs, and generic AI filler.
- End with a short recap the listener can remember.

Specific issues to fix:
{issues}
{fintech_section}
Return only the improved script text. Do not explain your changes.

Original script:
{text.strip()}
""".strip()

def review_script(text: str, target: str = "learning") -> QualityReport:
    text = normalize_script_text(text)
    metrics = build_metrics(text)
    findings = build_findings(metrics, text, target)
    fintech_alignment = None
    fintech_focus = None
    if target in EU_FINTECH_TARGETS:
        fintech_alignment = review_fintech_alignment(text, target=target)
        fintech_focus = fintech_alignment.rewrite_focus
        for item in fintech_alignment.findings:
            findings.append(Finding(item.severity, f"fintech alignment - {item.category}", item.message, item.suggestion))
    score = calculate_score(findings)
    return QualityReport(
        score=score,
        verdict=verdict_for(score),
        metrics=metrics,
        findings=findings,
        rewrite_prompt=build_rewrite_prompt(text, findings, target, fintech_focus=fintech_focus),
        fintech_alignment=fintech_alignment,
    )

def report_as_markdown(report: QualityReport, include_prompt: bool = False) -> str:
    lines = [
        f"# Script Quality Report",
        "",
        f"Score: {report.score}/100",
        f"Verdict: {report.verdict}",
        "",
        "## Metrics",
        "",
        f"- Words: {report.metrics.words}",
        f"- Paragraphs: {report.metrics.paragraphs}",
        f"- Sentences: {report.metrics.sentences}",
        f"- Average sentence words: {report.metrics.avg_sentence_words:.1f}",
        f"- Longest sentence words: {report.metrics.max_sentence_words}",
        f"- Dense paragraphs: {report.metrics.dense_paragraphs}",
        f"- Pause markers: {report.metrics.pause_markers}",
        f"- Recall prompts: {report.metrics.recall_prompts}",
        f"- Examples: {report.metrics.examples}",
    ]

    if report.fintech_alignment:
        alignment = report.fintech_alignment
        role_coverage = sum(1 for count in alignment.role_hits.values() if count > 0)
        domain_coverage = sum(1 for count in alignment.domain_hits.values() if count > 0)
        lines.extend([
            "",
            "## EU Fintech Alignment",
            "",
            f"- Alignment score: {alignment.score}/100",
            f"- Target: {alignment.target}",
            f"- Role coverage: {role_coverage}/{len(alignment.role_hits)}",
            f"- Domain coverage: {domain_coverage}/{len(alignment.domain_hits)}",
            f"- Analyst action hits: {alignment.analyst_action_hits}",
            f"- Evidence hits: {alignment.evidence_hits}",
            f"- Interview hits: {alignment.interview_hits}",
            f"- EU hits: {alignment.jurisdiction_hits['eu']}",
            f"- Ireland hits: {alignment.jurisdiction_hits['ireland']}",
            f"- Netherlands hits: {alignment.jurisdiction_hits['netherlands']}",
        ])

    lines.extend(["", "## Findings", ""])
    if report.findings:
        for finding in report.findings:
            lines.append(f"- {finding.severity.upper()} | {finding.category}: {finding.message} {finding.suggestion}")
    else:
        lines.append("- No major issues found.")

    if include_prompt:
        lines.extend(["", "## Rewrite Prompt", "", "```text", report.rewrite_prompt, "```"])
    return "\n".join(lines) + "\n"

def main() -> None:
    parser = argparse.ArgumentParser(description="Audit chatbot-produced scripts before TTS audio generation.")
    parser.add_argument("--input", required=True, help="Input .txt script to review")
    parser.add_argument("--target", choices=("learning", "interview", "bilingual", "eu_fintech", "ireland_fintech", "netherlands_fintech"), default="learning")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output-report", help="Optional path to write the quality report")
    parser.add_argument("--rewrite-prompt", help="Optional path to write an OpenAI/Claude rewrite prompt")
    parser.add_argument("--include-prompt", action="store_true", help="Include rewrite prompt inside markdown report")
    parser.add_argument("--min-score", type=int, default=0, help="Exit with code 2 if score is below this value")
    args = parser.parse_args()

    input_path = Path(args.input)
    text = input_path.read_text(encoding="utf-8")
    report = review_script(text, target=args.target)

    if args.format == "json":
        rendered = json.dumps(asdict(report), indent=2, ensure_ascii=False) + "\n"
    else:
        rendered = report_as_markdown(report, include_prompt=args.include_prompt)

    if args.output_report:
        report_path = Path(args.output_report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if args.rewrite_prompt:
        prompt_path = Path(args.rewrite_prompt)
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(report.rewrite_prompt + "\n", encoding="utf-8")

    if args.min_score and report.score < args.min_score:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
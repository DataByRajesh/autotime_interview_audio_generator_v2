r"""
AutoTime Interview Audio Generator v2
-------------------------------------
Convert a long .txt interview/podcast script into one MP3 using local Piper TTS + FFmpeg.

Grade target: practical local production utility
- No online character limits
- No weekly quota
- Resume-safe chunk generation
- Better text cleaning for technical interview content
- Clearer error messages
- Speed and loudness post-processing

Requirements:
1) Python 3.10+
2) Piper TTS executable
3) Piper .onnx voice model
4) Optional .onnx.json voice config
5) FFmpeg executable

Typical Windows command:

python interview_audio_generator_v2.py ^
  --input "sql_theory_interview_podcast_consolidated.txt" ^
  --output "sql_interview_podcast_final.mp3" ^
  --piper "C:\tts\piper\piper.exe" ^
  --voice "C:\tts\piper\voices\en_GB-alba-medium.onnx" ^
  --config "C:\tts\piper\voices\en_GB-alba-medium.onnx.json" ^
  --speed 1.0
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


TECH_REPLACEMENTS = [
    # Longer phrases first
    ("INNER JOIN", "inner join"),
    ("LEFT JOIN", "left join"),
    ("RIGHT JOIN", "right join"),
    ("FULL JOIN", "full join"),
    ("GROUP BY", "group by"),
    ("ORDER BY", "order by"),
    ("PRIMARY KEY", "primary key"),
    ("FOREIGN KEY", "foreign key"),
    ("SQL Server", "S Q L Server"),
    ("PostgreSQL", "Postgres Q L"),
    ("MySQL", "My S Q L"),

    # Acronyms / keywords
    ("SQL", "S Q L"),
    ("UAT", "U A T"),
    ("BA", "B A"),
    ("IT", "I T"),
    ("API", "A P I"),
    ("MP3", "M P 3"),
    ("WAV", "wave"),
    ("CSV", "C S V"),
    ("JSON", "J S O N"),
    ("NULL", "null"),
    ("SELECT", "select"),
    ("WHERE", "where"),
    ("JOIN", "join"),
    ("HAVING", "having"),
    ("COUNT", "count"),
    ("DISTINCT", "distinct"),
    ("CASE", "case"),
]


PAUSE_DURATIONS_MS = {
    "[PAUSE_SHORT]": 700,
    "[PAUSE_MEDIUM]": 1200,
    "[PAUSE_LONG]": 2000,
}

LEARNING_MODES = (
    "learn_mode",
    "recall_mode",
    "compare_mode",
    "interview_mode",
    "workplace_playlist_mode",
)

TOPIC_TEMPLATES = {
    "agile": {
        "title": "Agile",
        "meaning": "Agile is a way of delivering work in small useful steps, with regular feedback.",
        "why": "It matters because many technology teams do not know everything at the start.",
        "example": "As a Business Systems Analyst, you help split a large payment feature into smaller user stories that can be reviewed each sprint.",
        "confusion": "Agile is not the same as Scrum. Agile is the mindset. Scrum is one framework that can use that mindset.",
        "interview": "How have you worked in an Agile environment?",
        "fintech": "In payments, Agile helps a team release a safer change to transaction reporting before building the whole reporting platform.",
        "terms": ["sprint", "backlog", "increment"],
    },
    "scrum": {
        "title": "Scrum",
        "meaning": "Scrum is an Agile framework with roles, events, and a sprint rhythm.",
        "why": "It gives teams a simple operating model for planning, delivery, review, and improvement.",
        "example": "You refine user stories before sprint planning, support questions during the sprint, and help prepare acceptance evidence.",
        "confusion": "Scrum is not all of Agile. It is one structured way to practice Agile.",
        "interview": "What is Scrum and how does a Business Analyst support it?",
        "fintech": "A card payment team may use Scrum to deliver dispute handling changes over several sprints.",
        "terms": ["sprint planning", "daily scrum", "retrospective"],
    },
    "jira": {
        "title": "Jira",
        "meaning": "Jira is a work tracking tool used to manage issues, user stories, tasks, and defects.",
        "why": "It keeps delivery work visible and traceable.",
        "example": "You write a user story in Jira, add acceptance criteria, link a defect, and track its status through testing.",
        "confusion": "Jira does not make a team Agile by itself. It only supports tracking and communication.",
        "interview": "How do you use Jira as a Business Analyst?",
        "fintech": "A payment operations change can be tracked from requirement to UAT sign-off using linked Jira tickets.",
        "terms": ["issue", "workflow", "acceptance criteria"],
    },
    "user stories": {
        "title": "User stories",
        "meaning": "A user story describes a need from the user's point of view.",
        "why": "It keeps delivery focused on value, not just technical activity.",
        "example": "As an operations analyst, I want to see failed payments, so that I can investigate them quickly.",
        "confusion": "A user story is not the same as acceptance criteria. The story explains the need. The criteria define how to prove it works.",
        "interview": "How do you write a good user story?",
        "fintech": "A story may describe how a merchant user views card settlement exceptions.",
        "terms": ["persona", "value", "acceptance criteria"],
    },
    "acceptance criteria": {
        "title": "Acceptance criteria",
        "meaning": "Acceptance criteria are clear conditions that show when a requirement or story is done.",
        "why": "They reduce misunderstanding between business users, developers, and testers.",
        "example": "For a reconciliation report, criteria may say that matched, unmatched, and missing transactions must be shown separately.",
        "confusion": "Acceptance criteria are not a full test script. They are the business conditions that testing should cover.",
        "interview": "What makes acceptance criteria effective?",
        "fintech": "Payment status must update to settled only after the settlement file confirms the transaction.",
        "terms": ["given when then", "done", "testable"],
    },
    "uat": {
        "title": "UAT",
        "meaning": "UAT means User Acceptance Testing. Business users check whether the solution works for real business needs.",
        "why": "It helps confirm that the system is usable and acceptable before release.",
        "example": "Operations users test whether they can investigate failed payments using the new screen.",
        "confusion": "UAT is not the same as SIT. SIT checks system integration. UAT checks business acceptance.",
        "interview": "What is your role in UAT?",
        "fintech": "A payments team may run UAT before releasing a settlement dashboard to operations.",
        "terms": ["business sign-off", "test scenario", "acceptance"],
    },
    "sit": {
        "title": "SIT",
        "meaning": "SIT means System Integration Testing. It checks whether connected systems work together.",
        "why": "Many failures happen at the boundary between systems.",
        "example": "A payment request moves from a web app to an API, then to a processor, then back with a status update.",
        "confusion": "SIT is technical integration testing. UAT is business acceptance testing.",
        "interview": "What is the difference between SIT and UAT?",
        "fintech": "SIT checks whether payment authorization messages flow correctly between internal and external systems.",
        "terms": ["interface", "API", "integration"],
    },
    "qa": {
        "title": "QA",
        "meaning": "QA means Quality Assurance. It is the practice of improving confidence that work meets expectations.",
        "why": "QA reduces production issues and protects users.",
        "example": "QA reviews test coverage for a new customer onboarding workflow.",
        "confusion": "QA is broader than testing. Testing is one activity inside quality assurance.",
        "interview": "How do you work with QA teams?",
        "fintech": "QA may verify that payment limits, audit logs, and error messages behave correctly.",
        "terms": ["test plan", "defect", "quality"],
    },
    "regression testing": {
        "title": "Regression testing",
        "meaning": "Regression testing checks that existing features still work after a change.",
        "why": "A small change can accidentally break something that already worked.",
        "example": "After changing a payment status rule, the team retests refunds, failed payments, and reporting.",
        "confusion": "Regression testing is not only retesting the new change. It protects existing behaviour.",
        "interview": "Why is regression testing important?",
        "fintech": "A settlement change must not break reconciliation or customer balance updates.",
        "terms": ["existing behaviour", "retest", "release risk"],
    },
    "sql joins": {
        "title": "SQL joins",
        "meaning": "SQL joins combine rows from tables using related columns.",
        "why": "Business Analysts often need to understand how data from different systems connects.",
        "example": "You join customers to accounts, and accounts to transactions, to investigate payment activity.",
        "confusion": "An inner join keeps matching rows. A left join keeps all rows from the left table and adds matches where they exist.",
        "interview": "Explain SQL joins in simple terms.",
        "fintech": "You may join payments, settlement files, and reconciliation exceptions to find missing transactions.",
        "terms": ["inner join", "left join", "key"],
    },
    "payment lifecycle": {
        "title": "Payment lifecycle",
        "meaning": "The payment lifecycle is the journey of a payment from initiation to final outcome.",
        "why": "It helps you understand where errors, delays, and status changes can happen.",
        "example": "A card payment can move through authorization, capture, clearing, settlement, and reconciliation.",
        "confusion": "Authorization is not the same as settlement. Authorization checks approval. Settlement moves money.",
        "interview": "Can you explain the payment lifecycle?",
        "fintech": "A Business Systems Analyst may map each payment status to system events and user messages.",
        "terms": ["authorization", "clearing", "settlement"],
    },
    "settlement": {
        "title": "Settlement",
        "meaning": "Settlement is the process where money is finally transferred between parties.",
        "why": "It confirms the financial movement behind a transaction.",
        "example": "A merchant receives funds after card transactions are settled through the payment scheme and acquirer.",
        "confusion": "Settlement is not reconciliation. Settlement moves money. Reconciliation checks records match.",
        "interview": "What does settlement mean in payments?",
        "fintech": "Settlement files help confirm which transactions should be paid to the merchant.",
        "terms": ["funds movement", "acquirer", "scheme"],
    },
    "reconciliation": {
        "title": "Reconciliation",
        "meaning": "Reconciliation checks that records from two or more sources match.",
        "why": "It finds missing, duplicated, delayed, or mismatched transactions.",
        "example": "You compare internal payment records against a settlement file from a processor.",
        "confusion": "Reconciliation does not move money. It checks whether records agree.",
        "interview": "What is reconciliation in a payments context?",
        "fintech": "Unmatched transactions may need investigation before financial close.",
        "terms": ["matched", "unmatched", "exception"],
    },
    "incident management": {
        "title": "Incident management",
        "meaning": "Incident management is the process for restoring service when something goes wrong.",
        "why": "It reduces business impact and keeps communication clear during disruption.",
        "example": "If payment status updates stop arriving, teams triage impact, communicate, fix the issue, and review the cause.",
        "confusion": "An incident is not always a defect. An incident is a live service disruption. A defect is a fault in the product.",
        "interview": "How do you support incident management?",
        "fintech": "A payment outage may require stakeholder updates, workaround tracking, and post-incident actions.",
        "terms": ["severity", "workaround", "root cause"],
    },
    "requirements gathering": {
        "title": "Requirements gathering",
        "meaning": "Requirements gathering is the process of discovering what stakeholders need and why.",
        "why": "Good requirements reduce rework and build the right solution.",
        "example": "You interview operations, compliance, and technology teams before defining a new reporting change.",
        "confusion": "Requirements gathering is not just taking notes. It includes questioning, clarifying, prioritising, and validating.",
        "interview": "How do you gather requirements?",
        "fintech": "For a payment dispute workflow, you gather needs from customer support, risk, finance, and engineering.",
        "terms": ["stakeholder", "scope", "validation"],
    },
    "stakeholder communication": {
        "title": "Stakeholder communication",
        "meaning": "Stakeholder communication is sharing the right information with the right people at the right time.",
        "why": "It prevents surprises, confusion, and misaligned expectations.",
        "example": "You summarise UAT risks for a product owner and explain technical constraints in business language.",
        "confusion": "Communication is not just sending updates. It includes listening, confirming understanding, and adapting detail.",
        "interview": "How do you manage stakeholder communication?",
        "fintech": "During a payments incident, business users need plain-language updates and realistic timelines.",
        "terms": ["alignment", "expectation", "status update"],
    },
    "business systems analyst interview answers": {
        "title": "Business Systems Analyst interview answers",
        "meaning": "Strong answers connect business need, system behaviour, evidence, and stakeholder impact.",
        "why": "Interviewers want to hear how you think in real delivery situations.",
        "example": "When asked about requirements, explain how you clarified scope, documented rules, validated with users, and supported testing.",
        "confusion": "A strong answer is not a memorised definition. It is a practical story with structure.",
        "interview": "How do you explain your Business Systems Analyst experience?",
        "fintech": "Use examples around payments, reconciliation, UAT, incidents, SQL checks, and stakeholder trade-offs.",
        "terms": ["STAR", "business rule", "traceability"],
    },
}

COMPARE_TEMPLATES = {
    ("uat", "sit"): (
        "UAT checks whether business users accept the solution.",
        "SIT checks whether connected systems work together.",
        "The key difference is business acceptance versus technical integration.",
    ),
    ("requirement", "acceptance criteria"): (
        "A requirement describes what is needed.",
        "Acceptance criteria describe how to prove the need is met.",
        "The key difference is need versus proof.",
    ),
    ("agile", "scrum"): (
        "Agile is a delivery mindset based on small steps and feedback.",
        "Scrum is a framework with roles, events, and sprints.",
        "The key difference is mindset versus framework.",
    ),
    ("incident", "defect"): (
        "An incident is a live service disruption.",
        "A defect is a fault in the product or code.",
        "The key difference is operational impact versus product fault.",
    ),
    ("settlement", "reconciliation"): (
        "Settlement is the movement of money.",
        "Reconciliation checks whether records match.",
        "The key difference is funds movement versus record checking.",
    ),
}


def require_file(path: str | Path, label: str) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{label} not found: {p}")
    return p


def require_executable(name: str, custom_path: str | None = None) -> str:
    if custom_path:
        p = Path(custom_path)
        if not p.exists():
            raise FileNotFoundError(f"Executable path not found: {p}")
        return str(p)

    found = shutil.which(name)
    if not found:
        raise FileNotFoundError(
            f"Could not find '{name}' in PATH. Install it or pass its full path."
        )
    return found


def clean_text_for_tts(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove common markdown wrappers but preserve actual words.
    text = text.replace("```sql", "")
    text = text.replace("```text", "")
    text = text.replace("```", "")
    text = text.replace("`", "")

    # Make pasted smart punctuation and symbols speak naturally.
    symbol_replacements = {
        "\u00e2\u20ac\u0153": '"',
        "\u00e2\u20ac\u009d": '"',
        "\u00e2\u20ac\u02dc": "'",
        "\u00e2\u20ac\u2122": "'",
        "\u00e2\u20ac\u201d": " - ",
        "\u00e2\u20ac\u201c": " - ",
        "\u00e2\u2020\u2019": " to ",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2014": " - ",
        "\u2013": " - ",
        "\u2192": " to ",
        "->": " to ",
        "<>": " not equal to ",
        ">=": " greater than or equal to ",
        "<=": " less than or equal to ",
        "=": " equals ",
        ">": " greater than ",
        "<": " less than ",
        "&": " and ",
    }
    for old, new in symbol_replacements.items():
        text = text.replace(old, new)

    # Case-insensitive replacements for technical terms.
    for old, new in TECH_REPLACEMENTS:
        text = re.sub(rf"\b{re.escape(old)}\b", new, text, flags=re.IGNORECASE)

    # Keep punctuation useful for TTS pauses.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()



def split_dense_paragraphs_for_listening(text: str, max_words: int = 90, target_words: int = 55) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n")]
    prepared: list[str] = []

    for paragraph in paragraphs:
        if not paragraph:
            continue
        if paragraph in PAUSE_DURATIONS_MS or len(paragraph.split()) <= max_words:
            prepared.append(paragraph)
            continue

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip()]
        block: list[str] = []
        block_words = 0
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if block and block_words + sentence_words > target_words:
                prepared.append(" ".join(block))
                prepared.append("[PAUSE_SHORT]")
                block = [sentence]
                block_words = sentence_words
            else:
                block.append(sentence)
                block_words += sentence_words
        if block:
            prepared.append(" ".join(block))

    return "\n\n".join(prepared)


def prepare_text_for_low_load_listening(text: str) -> str:
    text = clean_text_for_tts(text)
    return split_dense_paragraphs_for_listening(text)

def split_text(text: str, max_chars: int = 2200) -> list[str]:
    """Split text into safe chunks. Piper works better with moderate chunk sizes."""
    if not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        add = para + "\n\n"

        if len(current) + len(add) <= max_chars:
            current += add
            continue

        if current.strip():
            chunks.append(current.strip())
            current = ""

        if len(add) <= max_chars:
            current = add
            continue

        # Split long paragraphs by sentence.
        sentences = re.split(r"(?<=[.!?])\s+", para)
        block = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            add_sentence = sentence + " "
            if len(block) + len(add_sentence) <= max_chars:
                block += add_sentence
            else:
                if block.strip():
                    chunks.append(block.strip())

                # If one sentence itself is still too large, hard split.
                if len(add_sentence) > max_chars:
                    for i in range(0, len(add_sentence), max_chars):
                        part = add_sentence[i:i + max_chars].strip()
                        if part:
                            chunks.append(part)
                    block = ""
                else:
                    block = add_sentence

        if block.strip():
            chunks.append(block.strip())

    if current.strip():
        chunks.append(current.strip())

    return chunks


def run_command(cmd: list[str], input_text: str | None = None) -> None:
    result = subprocess.run(
        cmd,
        input=input_text,
        text=True if input_text is not None else False,
        capture_output=True,
    )

    if result.returncode != 0:
        print("\nCommand failed:")
        print(" ".join(cmd))

        stdout = result.stdout.decode(errors="ignore") if isinstance(result.stdout, bytes) else result.stdout
        stderr = result.stderr.decode(errors="ignore") if isinstance(result.stderr, bytes) else result.stderr

        if stdout:
            print("\nSTDOUT:")
            print(stdout)
        if stderr:
            print("\nSTDERR:")
            print(stderr)

        raise RuntimeError("Command failed. Check the error above.")


def generate_chunk(
    piper_exe: str,
    voice_model: Path,
    config_file: Path | None,
    text: str,
    output_wav: Path,
) -> None:
    cmd = [
        piper_exe,
        "--model",
        str(voice_model),
        "--output_file",
        str(output_wav),
    ]

    if config_file:
        cmd.extend(["--config", str(config_file)])

    run_command(cmd, input_text=text)


def merge_wavs(ffmpeg_exe: str, wav_files: list[Path], merged_wav: Path) -> None:
    concat_file = merged_wav.parent / "concat_list.txt"

    lines = []
    for wav in wav_files:
        safe_path = str(wav.resolve()).replace("\\", "/")
        lines.append(f"file '{safe_path}'")

    concat_file.write_text("\n".join(lines), encoding="utf-8")

    cmd = [
        ffmpeg_exe,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        str(merged_wav),
    ]
    run_command(cmd)

    concat_file.unlink(missing_ok=True)


def final_audio_filter(speed: float) -> str:
    # atempo accepts 0.5-2.0 in one filter, and validation keeps this in range.
    return ",".join([
        f"atempo={speed}",
        "highpass=f=90",
        "lowpass=f=8500",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
    ])


def export_mp3(
    ffmpeg_exe: str,
    input_wav: Path,
    output_mp3: Path,
    speed: float,
    bitrate: str,
) -> None:
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(input_wav),
        "-filter:a",
        final_audio_filter(speed),
        "-codec:a",
        "libmp3lame",
        "-b:a",
        bitrate,
        str(output_mp3),
    ]
    run_command(cmd)


def export_wav(
    ffmpeg_exe: str,
    input_wav: Path,
    output_wav: Path,
    speed: float,
) -> None:
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(input_wav),
        "-filter:a",
        final_audio_filter(speed),
        str(output_wav),
    ]
    run_command(cmd)



def normalize_topic(topic: str) -> str:
    return re.sub(r"\s+", " ", topic.strip().lower())


def get_topic_template(topic: str) -> dict:
    key = normalize_topic(topic)
    if key in TOPIC_TEMPLATES:
        return TOPIC_TEMPLATES[key]

    title = topic.strip() or "Workplace concept"
    return {
        "title": title,
        "meaning": f"{title} is the concept we are learning in simple workplace language.",
        "why": f"{title} matters because it can affect business decisions, systems, users, or delivery outcomes.",
        "example": f"In a Business Systems Analyst role, you may need to explain {title}, clarify it with stakeholders, and connect it to system behaviour.",
        "confusion": f"A common confusion is treating {title} as a definition only, instead of linking it to a real job situation.",
        "interview": f"Can you explain {title} in a practical workplace example?",
        "fintech": f"In a FinTech scenario, {title} may affect payments, reporting, controls, customer experience, or operational risk.",
        "terms": [],
    }


def short_title(topic: str) -> str:
    return get_topic_template(topic)["title"]


def sentence_case_list(lines: list[str]) -> str:
    return "\n\n".join(line.strip() for line in lines if line.strip())


def generate_learning_script(mode: str, topic: str, compare_topic: str | None = None) -> str:
    data = get_topic_template(topic)
    title = data["title"]

    if mode == "learn_mode":
        return sentence_case_list([
            f"Topic: {title}.",
            "Why it matters.",
            data["why"],
            "[PAUSE_SHORT]",
            "Simple meaning.",
            data["meaning"],
            "[PAUSE_MEDIUM]",
            "Real job example.",
            data["example"],
            "[PAUSE_MEDIUM]",
            "Repeat in simpler words.",
            f"In simple words, {title} helps you understand what is happening, why it matters, and what action is needed.",
            "[PAUSE_SHORT]",
            "Common confusion.",
            data["confusion"],
            "[PAUSE_MEDIUM]",
            "Short recap.",
            f"Remember this. {title} means: {data['meaning']}",
        ])

    if mode == "recall_mode":
        return sentence_case_list([
            f"Recall practice: {title}.",
            f"Question one. What does {title} mean in simple workplace language?",
            "[PAUSE_LONG]",
            f"Answer. {data['meaning']}",
            f"Repeat answer. {data['meaning']}",
            "[PAUSE_MEDIUM]",
            f"Question two. Where might you use {title} in a Business Systems Analyst or FinTech job?",
            "[PAUSE_LONG]",
            f"Answer. {data['example']} {data['fintech']}",
            "[PAUSE_SHORT]",
            f"Final memory sentence. {title} is useful when you can explain it simply and connect it to a real system or business outcome.",
        ])

    if mode == "compare_mode":
        other = compare_topic or "SIT" if normalize_topic(topic) == "uat" else compare_topic or "UAT"
        return generate_compare_script(topic, other)

    if mode == "interview_mode":
        return sentence_case_list([
            f"Interview practice: {title}.",
            f"Likely interview question. {data['interview']}",
            "[PAUSE_MEDIUM]",
            f"Simple answer. {data['meaning']} {data['why']}",
            "[PAUSE_SHORT]",
            f"Stronger answer. I would explain {title} by linking the business need, system behaviour, evidence, and stakeholder impact.",
            f"For example. {data['example']}",
            "[PAUSE_MEDIUM]",
            f"FinTech or payment example. {data['fintech']}",
            "[PAUSE_MEDIUM]",
            f"Final polished answer. {data['meaning']} In a delivery role, I use it by clarifying the business need, checking the system impact, and making sure stakeholders can see the evidence.",
        ])

    if mode == "workplace_playlist_mode":
        return generate_workplace_playlist_script([topic])

    raise ValueError(f"Unknown learning mode: {mode}")


def generate_compare_script(topic_a: str, topic_b: str) -> str:
    key_a = normalize_topic(topic_a)
    key_b = normalize_topic(topic_b)
    comparison = COMPARE_TEMPLATES.get((key_a, key_b)) or COMPARE_TEMPLATES.get((key_b, key_a))

    if comparison and (key_a, key_b) in COMPARE_TEMPLATES:
        meaning_a, meaning_b, difference = comparison
    elif comparison:
        meaning_b, meaning_a, difference = comparison
    else:
        meaning_a = get_topic_template(topic_a)["meaning"]
        meaning_b = get_topic_template(topic_b)["meaning"]
        difference = f"The key difference is the specific job purpose. {short_title(topic_a)} answers one need. {short_title(topic_b)} answers another."

    title_a = short_title(topic_a)
    title_b = short_title(topic_b)
    return sentence_case_list([
        f"Compare mode: {title_a} versus {title_b}.",
        f"{title_a} simple meaning. {meaning_a}",
        "[PAUSE_SHORT]",
        f"{title_b} simple meaning. {meaning_b}",
        "[PAUSE_SHORT]",
        f"Key difference. {difference}",
        "[PAUSE_MEDIUM]",
        f"Job example. In a project meeting, say clearly whether the issue is about {title_a}, {title_b}, or the handoff between them.",
        "Quiz. Which one is closer to business acceptance?",
        "[PAUSE_LONG]",
        f"Answer. It depends on the pair, but for UAT versus SIT, UAT is business acceptance and SIT is system integration.",
        f"Final comparison sentence. Do not memorise labels only. Remember the job purpose: {difference}",
    ])


def generate_workplace_playlist_script(topics: list[str]) -> str:
    sections = [
        "Workplace learning playlist.",
        "Target length is forty five to sixty minutes when expanded across several topics.",
        "Listen once. Do not rush. Short sentences are intentional.",
        "[PAUSE_MEDIUM]",
    ]
    for topic in topics:
        sections.append(generate_learning_script("learn_mode", topic))
        sections.append(f"Mini quiz. Say one job example for {short_title(topic)}.")
        sections.append("[PAUSE_LONG]")
        sections.append(f"Answer reminder. {get_topic_template(topic)['example']}")
        sections.append("[PAUSE_MEDIUM]")
    sections.append("End of playlist. Repeat the key points tomorrow using recall mode.")
    return sentence_case_list(sections)


def sanitize_filename_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "Learning_Topic"


def spaced_repetition_plan(topic_group: str, extension: str = ".mp3") -> list[tuple[str, str]]:
    base = sanitize_filename_part(topic_group)
    return [
        ("learn_mode", f"01_{base}_Day1_Learn{extension}"),
        ("recall_mode", f"02_{base}_Day2_Recall{extension}"),
        ("compare_mode", f"03_{base}_Day4_Compare{extension}"),
        ("interview_mode", f"04_{base}_Day7_Interview{extension}"),
    ]


def replace_pause_markers_for_tts(text: str) -> str:
    # TODO: Replace this with real FFmpeg silence insertion between generated chunks.
    # Current behaviour gives Piper punctuation and blank lines so it naturally pauses.
    for marker in PAUSE_DURATIONS_MS:
        text = text.replace(marker, ".\n\n")
    return text


def cognitive_load_warnings(text: str, speed: float, workplace_mode: bool = False) -> list[str]:
    warnings: list[str] = []
    text = split_dense_paragraphs_for_listening(text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    if sentences:
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_words > 18:
            warnings.append(f"Average sentence length is {avg_words:.1f} words. Aim for 18 or fewer for walking or noisy listening.")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    dense_paragraphs = [p for p in paragraphs if len(p.split()) > 90]
    if dense_paragraphs:
        warnings.append(f"{len(dense_paragraphs)} paragraph(s) are dense. Split them into shorter listening blocks.")

    if not any(marker in text for marker in PAUSE_DURATIONS_MS):
        warnings.append("No pause markers found. Add [PAUSE_SHORT], [PAUSE_MEDIUM], or [PAUSE_LONG].")

    glossary_terms = sorted({term.lower() for item in TOPIC_TEMPLATES.values() for term in item.get("terms", [])})
    lowered = text.lower()
    sections = re.split(r"\n\s*section\s+\d+\s*:", lowered, flags=re.IGNORECASE)
    seen_terms: set[str] = set()
    for section in sections:
        section_terms = {
            term for term in glossary_terms
            if re.search(rf"\b{re.escape(term)}\b", section)
        }
        new_terms = section_terms - seen_terms
        if len(new_terms) > 8:
            warnings.append(f"One section introduces about {len(new_terms)} new key terms. Consider splitting it into smaller sections.")
            break
        seen_terms.update(section_terms)

    if workplace_mode and speed > 1.0:
        warnings.append("Workplace speed is above 1.0. Use 0.85 to 1.0 for low cognitive load listening.")

    if not re.search(r"\b(quiz|question|what|which|why|how)\b", lowered):
        warnings.append("No quiz questions found. Add a recall question or mini quiz.")

    return warnings



def playlist_script_output_dir(script_output: str | None) -> Path:
    if not script_output:
        return Path("output")
    candidate = Path(script_output)
    if candidate.suffix:
        return candidate.parent
    return candidate

def write_script_if_requested(script: str, script_output: str | None) -> None:
    if not script_output:
        return
    out = Path(script_output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(script, encoding="utf-8")
    print(f"Learning script written to: {out.resolve()}")


def render_warnings(warnings: list[str]) -> None:
    if not warnings:
        print("Cognitive load check: passed.")
        return
    print("Cognitive load warnings:")
    for warning in warnings:
        print(f"- {warning}")


def generate_audio_file(
    raw_text: str,
    output_mp3: Path,
    voice_model: Path,
    config_file: Path | None,
    piper_exe: str,
    ffmpeg_exe: str,
    speed: float,
    bitrate: str,
    chunk_size: int,
    keep_temp: bool,
    dry_run: bool,
    input_label: str,
) -> None:
    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    prepared_text = prepare_text_for_low_load_listening(raw_text)
    tts_text = replace_pause_markers_for_tts(prepared_text)
    clean_text = clean_text_for_tts(tts_text)
    chunks = split_text(clean_text, max_chars=chunk_size)

    if not chunks:
        raise ValueError("No readable text found in input file.")

    print("Setup check passed.")
    print(f"Input: {input_label}")
    print(f"Output: {output_mp3}")
    print(f"Voice: {voice_model}")
    print(f"Config: {config_file if config_file else 'Not provided'}")
    print(f"Piper: {piper_exe}")
    print(f"FFmpeg: {ffmpeg_exe}")
    print(f"Chunks: {len(chunks)}")
    print(f"Speed: {speed}")

    if dry_run:
        print("Dry run complete. No audio generated.")
        return

    work_dir = output_mp3.parent / f"{output_mp3.stem}_temp"
    work_dir.mkdir(parents=True, exist_ok=True)

    wav_files: list[Path] = []

    for i, chunk in enumerate(chunks, start=1):
        wav_path = work_dir / f"chunk_{i:04d}.wav"
        wav_files.append(wav_path)

        if wav_path.exists() and wav_path.stat().st_size > 0:
            print(f"[{i}/{len(chunks)}] Existing chunk found, skipping")
            continue

        print(f"[{i}/{len(chunks)}] Generating WAV")
        generate_chunk(
            piper_exe=piper_exe,
            voice_model=voice_model,
            config_file=config_file,
            text=chunk,
            output_wav=wav_path,
        )

    merged_wav = work_dir / "merged.wav"

    print("Merging WAV files...")
    merge_wavs(ffmpeg_exe, wav_files, merged_wav)

    if output_mp3.suffix.lower() == ".wav":
        print("Exporting final WAV...")
        export_wav(
            ffmpeg_exe=ffmpeg_exe,
            input_wav=merged_wav,
            output_wav=output_mp3,
            speed=speed,
        )
    else:
        print("Exporting final MP3...")
        export_mp3(
            ffmpeg_exe=ffmpeg_exe,
            input_wav=merged_wav,
            output_mp3=output_mp3,
            speed=speed,
            bitrate=bitrate,
        )

    if not keep_temp:
        print("Cleaning temporary files...")
        for wav in wav_files:
            wav.unlink(missing_ok=True)
        merged_wav.unlink(missing_ok=True)
        try:
            work_dir.rmdir()
        except OSError:
            print(f"Temporary folder kept because it is not empty: {work_dir}")

    print("\nDone.")
    print(f"Final audio created at: {output_mp3.resolve()}")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a long-form interview podcast MP3 using Piper TTS."
    )

    parser.add_argument("--input", required=False, help="Input .txt file")
    parser.add_argument("--output", required=False, help="Output .mp3 file")
    parser.add_argument("--voice", required=False, help="Piper .onnx voice model")
    parser.add_argument("--config", default=None, help="Optional Piper .onnx.json config")
    parser.add_argument("--piper", default=None, help="Optional piper executable path")
    parser.add_argument("--ffmpeg", default=None, help="Optional ffmpeg executable path")
    parser.add_argument("--config-file", default=None, help="Optional JSON config file (overrides defaults)")
    parser.add_argument("--speed", type=float, default=None, help="Final MP3 speed. Use 1.0 for normal playback")
    parser.add_argument("--bitrate", default=None, help="MP3 bitrate, e.g. 96k or 128k")
    parser.add_argument("--chunk-size", type=int, default=None, help="TTS chunk size in characters")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary WAV files")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup and show chunk count only")
    parser.add_argument("--learning-mode", choices=LEARNING_MODES, default=None, help="Generate a psychology-backed learning script before TTS")
    parser.add_argument("--topic", default=None, help="Topic name for a learning mode, e.g. Agile or Payment lifecycle")
    parser.add_argument("--compare-topic", default=None, help="Second topic for compare_mode")
    parser.add_argument("--script-output", default=None, help="Optional .txt path for the generated learning script")
    parser.add_argument("--script-only", action="store_true", help="Only write/show the generated learning script; do not create audio")
    parser.add_argument("--spaced-playlist", action="store_true", help="Create Day1/Day2/Day4/Day7 spaced repetition audio files")
    parser.add_argument("--list-topic-templates", action="store_true", help="List built-in learning topic templates and exit")

    args = parser.parse_args()

    # Load JSON config file if provided. Command-line args take precedence.
    file_cfg: dict = {}
    if args.config_file:
        cfg_path = Path(args.config_file)
        if not cfg_path.exists():
            raise FileNotFoundError(f"Config file not found: {cfg_path}")
        try:
            file_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to parse config file: {exc}")

    def resolve(name: str, default=None):
        # prefer CLI value (not None), then config file, else default
        val = getattr(args, name, None)
        if val is not None:
            return val
        return file_cfg.get(name, default)

    if args.list_topic_templates:
        print("Built-in topic templates:")
        for item in sorted(TOPIC_TEMPLATES.values(), key=lambda x: x["title"].lower()):
            print(f"- {item['title']}")
        return

    learning_mode = resolve("learning_mode")
    topic_arg = resolve("topic")
    compare_topic = resolve("compare_topic")
    workplace_mode = learning_mode == "workplace_playlist_mode" or bool(args.spaced_playlist)
    default_speed = 0.85 if workplace_mode else 1.0
    speed = float(resolve("speed", default_speed))
    if not (0.8 <= speed <= 1.5):
        raise ValueError("Speed must be between 0.8 and 1.5. Use 1.0 for normal playback.")

    input_arg = resolve("input")
    output_arg = resolve("output")
    voice_arg = resolve("voice")
    config_arg = resolve("config")
    chunk_size = int(resolve("chunk_size", 2200))
    bitrate = resolve("bitrate", "128k")

    if args.spaced_playlist:
        if not topic_arg:
            raise ValueError("--spaced-playlist requires --topic, for example --topic \"Agile Scrum Jira\"")
        if args.script_only:
            base_dir = playlist_script_output_dir(args.script_output)
            for mode, filename in spaced_repetition_plan(topic_arg, extension=".txt"):
                script = generate_learning_script(mode, topic_arg, compare_topic)
                script_path = base_dir / filename
                write_script_if_requested(script, str(script_path))
                render_warnings(cognitive_load_warnings(script, speed, workplace_mode=True))
            return
        if not output_arg:
            raise ValueError("--spaced-playlist requires --output as an output folder")
        if not voice_arg:
            raise ValueError("Voice model not provided (use --voice or provide in config-file)")

        voice_model = require_file(voice_arg, "Piper voice model")
        config_file = require_file(config_arg, "Piper config") if config_arg else None
        piper_exe = require_executable("piper", resolve("piper", args.piper))
        ffmpeg_exe = require_executable("ffmpeg", resolve("ffmpeg", args.ffmpeg))
        output_dir = Path(output_arg)
        output_dir.mkdir(parents=True, exist_ok=True)

        for mode, filename in spaced_repetition_plan(topic_arg, extension=".wav"):
            script = generate_learning_script(mode, topic_arg, compare_topic)
            render_warnings(cognitive_load_warnings(script, speed, workplace_mode=True))
            script_path = output_dir / Path(filename).with_suffix(".txt").name
            write_script_if_requested(script, str(script_path))
            generate_audio_file(
                raw_text=script,
                output_mp3=output_dir / filename,
                voice_model=voice_model,
                config_file=config_file,
                piper_exe=piper_exe,
                ffmpeg_exe=ffmpeg_exe,
                speed=speed,
                bitrate=bitrate,
                chunk_size=chunk_size,
                keep_temp=args.keep_temp,
                dry_run=args.dry_run,
                input_label=f"generated {mode} script",
            )
        return

    if learning_mode:
        if not topic_arg:
            raise ValueError("Learning modes require --topic, for example --topic UAT")
        raw_text = generate_learning_script(learning_mode, topic_arg, compare_topic)
        write_script_if_requested(raw_text, args.script_output)
        render_warnings(cognitive_load_warnings(raw_text, speed, workplace_mode=workplace_mode))
        if args.script_only:
            print(raw_text)
            return
    else:
        if not input_arg:
            raise ValueError("Input script not provided (use --input, --learning-mode, or provide in config-file)")
        input_path = require_file(input_arg, "Input script")
        raw_text = input_path.read_text(encoding="utf-8")
        render_warnings(cognitive_load_warnings(raw_text, speed, workplace_mode=False))

    if not output_arg:
        raise ValueError("Output path not provided (use --output or provide in config-file)")
    if not voice_arg:
        raise ValueError("Voice model not provided (use --voice or provide in config-file)")

    voice_model = require_file(voice_arg, "Piper voice model")
    config_file = require_file(config_arg, "Piper config") if config_arg else None
    piper_exe = require_executable("piper", resolve("piper", args.piper))
    ffmpeg_exe = require_executable("ffmpeg", resolve("ffmpeg", args.ffmpeg))

    generate_audio_file(
        raw_text=raw_text,
        output_mp3=Path(output_arg),
        voice_model=voice_model,
        config_file=config_file,
        piper_exe=piper_exe,
        ffmpeg_exe=ffmpeg_exe,
        speed=speed,
        bitrate=bitrate,
        chunk_size=chunk_size,
        keep_temp=args.keep_temp,
        dry_run=args.dry_run,
        input_label=f"generated {learning_mode} script" if learning_mode else str(input_path),
    )

if __name__ == "__main__":
    main()

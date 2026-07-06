from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


DEFAULT_DETAIL_PATH = Path("glossary_full_detail_with_ipa.json")
DEFAULT_MODULE_PATH = Path("tamil_glossary_module.py")
ACRONYM_RE = re.compile(r"^[A-Z0-9][A-Z0-9.+-]*$")

LETTER_NAMES = {
    "A": "\u0b8f", "B": "\u0baa\u0bbf", "C": "\u0b9a\u0bbf", "D": "\u0b9f\u0bbf",
    "E": "\u0b88", "F": "\u0b8e\u0b83\u0baa\u0bcd", "G": "\u0b9c\u0bbf", "H": "\u0b8e\u0b9a\u0bcd",
    "I": "\u0b90", "J": "\u0b9c\u0bc7", "K": "\u0b95\u0bc7", "L": "\u0b8e\u0bb2\u0bcd",
    "M": "\u0b8e\u0bae\u0bcd", "N": "\u0b8e\u0ba9\u0bcd", "O": "\u0b93", "P": "\u0baa\u0bbf",
    "Q": "\u0b95\u0bcd\u0baf\u0bc2", "R": "\u0b86\u0bb0\u0bcd", "S": "\u0b8e\u0bb8\u0bcd", "T": "\u0b9f\u0bbf",
    "U": "\u0baf\u0bc2", "V": "\u0bb5\u0bbf", "W": "\u0b9f\u0baa\u0bbf\u0bb3\u0bcd\u0baf\u0bc2", "X": "\u0b8e\u0b95\u0bcd\u0bb8\u0bcd",
    "Y": "\u0bb5\u0bc8", "Z": "\u0b9c\u0bc6\u0b9f\u0bcd", "0": "\u0b9c\u0bc0\u0bb0\u0bcb", "1": "\u0b92\u0ba9\u0bcd",
    "2": "\u0b9f\u0bc2", "3": "\u0ba4\u0bcd\u0bb0\u0bc0", "4": "\u0b83\u0baa\u0bcb\u0bb0\u0bcd", "5": "\u0b83\u0baa\u0bc8\u0bb5\u0bcd",
    "6": "\u0b9a\u0bbf\u0b95\u0bcd\u0bb8\u0bcd", "7": "\u0b9a\u0bc6\u0bb5\u0ba9\u0bcd", "8": "\u0b8e\u0baf\u0bcd\u0b9f\u0bcd", "9": "\u0ba8\u0bc8\u0ba9\u0bcd",
}

IPA_UNITS = [
    ("t\u0361\u0283", "\u0b9a\u0bcd"), ("d\u0361\u0292", "\u0b9c\u0bcd"),
    ("e\u026a", "\u0bc7"), ("o\u028a", "\u0bcb"), ("a\u026a", "\u0bc8"), ("a\u028a", "\u0bcc"), ("\u0254\u026a", "\u0bcb\u0baf\u0bcd"),
    ("i\u02d0", "\u0bc0"), ("u\u02d0", "\u0bc2"), ("\u0251\u02d0", "\u0bbe"), ("\u025c\u02d0", "\u0bb0\u0bcd"),
    ("\u0259", "\u0b85"), ("\u028c", "\u0b85"), ("\u00e6", "\u0b8e"), ("\u0251", "\u0bbe"), ("\u0252", "\u0bbe"),
    ("\u0254", "\u0b92"), ("\u025b", "\u0bc6"), ("\u026a", "\u0bbf"), ("i", "\u0bbf"), ("u", "\u0bc1"),
    ("\u0283", "\u0bb7\u0bcd"), ("\u0292", "\u0bb7\u0bcd"), ("\u03b8", "\u0ba4\u0bcd"), ("\u00f0", "\u0ba4\u0bcd"),
    ("\u014b", "\u0b99\u0bcd"), ("\u0272", "\u0b9e\u0bcd"), ("\u0279", "\u0bb0\u0bcd"), ("\u027e", "\u0bb0"),
    ("b", "\u0baa\u0bcd"), ("d", "\u0b9f\u0bcd"), ("f", "\u0b83\u0baa\u0bcd"), ("g", "\u0b95\u0bcd"),
    ("h", "\u0bb9"), ("j", "\u0baf\u0bcd"), ("k", "\u0b95\u0bcd"), ("l", "\u0bb2\u0bcd"),
    ("m", "\u0bae\u0bcd"), ("n", "\u0ba9\u0bcd"), ("p", "\u0baa\u0bcd"), ("r", "\u0bb0\u0bcd"),
    ("s", "\u0bb8\u0bcd"), ("t", "\u0b9f\u0bcd"), ("v", "\u0bb5\u0bcd"), ("w", "\u0bb5\u0bcd"),
    ("z", "\u0bb8\u0bcd"), ("\u0294", ""), ("\u02c8", ""), ("\u02cc", ""), ("\u02d0", ""), (".", ""), (" ", " "),
]

PHONETIC_UNITS = [
    ("tion", "\u0bb7\u0ba9\u0bcd"), ("sion", "\u0bb7\u0ba9\u0bcd"), ("ment", "\u0bae\u0bc6\u0ba9\u0bcd\u0b9f\u0bcd"),
    ("ance", "\u0ba9\u0bcd\u0bb8\u0bcd"), ("ence", "\u0ba9\u0bcd\u0bb8\u0bcd"), ("ing", "\u0bbf\u0b99\u0bcd"),
    ("ph", "\u0b83\u0baa\u0bcd"), ("sh", "\u0bb7\u0bcd"), ("ch", "\u0b9a\u0bcd"), ("th", "\u0ba4\u0bcd"),
    ("ck", "\u0b95\u0bcd"), ("ng", "\u0b99\u0bcd"), ("qu", "\u0b95\u0bcd\u0bb5"),
    ("oo", "\u0bc2"), ("ee", "\u0bc0"), ("ea", "\u0bc0"), ("ai", "\u0bc7"), ("ay", "\u0bc7"),
    ("oa", "\u0bcb"), ("ow", "\u0bcc"), ("ou", "\u0bcc"),
]
CONSONANTS = {
    "b": "\u0baa", "c": "\u0b95", "d": "\u0b9f", "f": "\u0b83\u0baa", "g": "\u0b95", "h": "\u0bb9", "j": "\u0b9c",
    "k": "\u0b95", "l": "\u0bb2", "m": "\u0bae", "n": "\u0ba9", "p": "\u0baa", "q": "\u0b95", "r": "\u0bb0",
    "s": "\u0bb8", "t": "\u0b9f", "v": "\u0bb5", "w": "\u0bb5", "x": "\u0b95\u0bcd\u0bb8", "y": "\u0baf", "z": "\u0bb8",
}
VOWELS = {
    "a": ("\u0b85", ""), "e": ("\u0b8e", "\u0bc6"), "i": ("\u0b87", "\u0bbf"), "o": ("\u0b92", "\u0bca"), "u": ("\u0b85", "\u0bc1"),
}
PULLI = "\u0bcd"


def load_words(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def load_seed_details(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    items = json.loads(path.read_text(encoding="utf-8-sig"))
    details: dict[str, dict[str, Any]] = {}
    for item in items:
        word = str(item["word"])
        details[word] = dict(item)
        details.setdefault(word.casefold(), dict(item))
    return details


def find_espeak(explicit_path: str | None) -> str | None:
    if explicit_path:
        candidate = Path(explicit_path)
        return str(candidate) if candidate.is_file() else None
    for name in ("espeak-ng", "espeak-ng.exe", "espeak", "espeak.exe"):
        found = shutil.which(name)
        if found:
            return found
    return None


def espeak_ipa(word: str, espeak_exe: str, voice: str) -> str | None:
    result = subprocess.run(
        [espeak_exe, "-q", f"--ipa=3", "-v", voice, word],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    ipa = " ".join((result.stdout or result.stderr).split())
    return ipa or None


def acronym_to_tamil(word: str) -> str:
    parts = []
    for char in word:
        if char in {".", "-", "_", "+"}:
            continue
        parts.append(LETTER_NAMES.get(char.upper(), char))
    return ".".join(parts) + "." if parts else word


def ipa_to_tamil(ipa: str) -> tuple[str, list[str]]:
    out: list[str] = []
    unmapped: list[str] = []
    i = 0
    while i < len(ipa):
        for src, tamil in IPA_UNITS:
            if ipa.startswith(src, i):
                out.append(tamil)
                i += len(src)
                break
        else:
            ch = ipa[i]
            if ch not in unmapped:
                unmapped.append(ch)
            out.append(ch)
            i += 1
    return "".join(out), unmapped


def fallback_word_to_tamil(word: str) -> str:
    lower = word.lower().strip("'-")
    if not lower:
        return word

    out: list[str] = []
    i = 0
    while i < len(lower):
        for src, tamil in PHONETIC_UNITS:
            if lower.startswith(src, i):
                out.append(tamil)
                i += len(src)
                break
        else:
            ch = lower[i]
            next_ch = lower[i + 1] if i + 1 < len(lower) else ""
            if ch in CONSONANTS:
                base = CONSONANTS[ch]
                if next_ch in VOWELS:
                    _, sign = VOWELS[next_ch]
                    out.append(base + sign)
                    i += 2
                else:
                    out.append(base + PULLI)
                    i += 1
            elif ch in VOWELS:
                independent, _ = VOWELS[ch]
                out.append(independent)
                i += 1
            else:
                out.append(ch)
                i += 1
    return "".join(out)


def build_detail(
    word: str,
    seed_details: dict[str, dict[str, Any]],
    espeak_exe: str | None,
    espeak_voice: str,
    refresh_ipa: bool,
) -> dict[str, Any]:
    seeded = seed_details.get(word) or seed_details.get(word.casefold())
    if seeded and not refresh_ipa:
        return {
            "word": word,
            "ipa": seeded.get("ipa", ""),
            "tamil_draft": seeded.get("tamil_draft", ""),
            "needs_manual_review": bool(seeded.get("needs_manual_review", False)),
            "mode": seeded.get("mode", "acronym" if ACRONYM_RE.match(word) else "word"),
        }

    if ACRONYM_RE.match(word):
        return {
            "word": word,
            "ipa": "(acronym - spelled letter by letter)",
            "tamil_draft": acronym_to_tamil(word),
            "needs_manual_review": False,
            "mode": "acronym",
        }

    if espeak_exe:
        ipa = espeak_ipa(word, espeak_exe, espeak_voice)
        if ipa:
            tamil, unmapped = ipa_to_tamil(ipa)
            detail = {
                "word": word,
                "ipa": ipa,
                "tamil_draft": tamil,
                "needs_manual_review": bool(unmapped),
                "mode": "word",
            }
            if unmapped:
                detail["unmapped_ipa_symbols"] = unmapped
            return detail

    return {
        "word": word,
        "ipa": "(fallback transliteration - espeak-ng unavailable or failed)",
        "tamil_draft": fallback_word_to_tamil(word),
        "needs_manual_review": True,
        "mode": "word",
    }


def module_text(details: list[dict[str, Any]]) -> str:
    pairs = [(item["word"], item["tamil_draft"]) for item in details]
    lines = [
        "# Tamil transliteration glossary for hybrid Tamil-English TTS",
        "# Generated by ipa_to_tamil.py. Review glossary_full_detail_with_ipa.json before production use.",
        "# Format matches existing TECH_REPLACEMENTS / TAMIL_TECH_REPLACEMENTS convention.",
        "",
        "TAMIL_GLOSSARY_REPLACEMENTS = [",
    ]
    for word, tamil in pairs:
        lines.append(f"    ({word!r}, {tamil!r}),")
    lines.extend([
        "]",
        "",
        "",
        "def apply_tamil_glossary(text: str) -> str:",
        "    \"\"\"Replace English tokens with Tamil transliterations before TTS.\"\"\"",
        "    import re",
        "",
        "    for original, replacement in TAMIL_GLOSSARY_REPLACEMENTS:",
        "        text = re.sub(rf\"\\b{re.escape(original)}\\b\", replacement, text, flags=re.IGNORECASE)",
        "    return text",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Tamil glossary detail JSON and module from a source word list.")
    parser.add_argument("--file", required=True, type=Path, help="Plain text source word list, one token/phrase per line")
    parser.add_argument("--seed-detail", type=Path, default=DEFAULT_DETAIL_PATH, help="Existing detailed JSON to reuse IPA/Tamil/manual-review fields")
    parser.add_argument("--detail-output", type=Path, default=DEFAULT_DETAIL_PATH, help="Detailed JSON output path")
    parser.add_argument("--module-output", type=Path, default=DEFAULT_MODULE_PATH, help="Python glossary module output path")
    parser.add_argument("--espeak", help="Optional path to espeak-ng/espeak executable. Defaults to PATH lookup.")
    parser.add_argument("--espeak-voice", default="en-us", help="Voice passed to espeak-ng for IPA generation")
    parser.add_argument("--refresh-ipa", action="store_true", help="Regenerate non-acronym IPA/Tamil drafts with espeak-ng when available instead of reusing seed details")
    parser.add_argument("--no-module", action="store_true", help="Only write the detailed JSON")
    args = parser.parse_args()

    words = load_words(args.file)
    seed_details = load_seed_details(args.seed_detail)
    espeak_exe = find_espeak(args.espeak)
    if espeak_exe:
        print(f"Using espeak-ng for new/refreshable words: {espeak_exe}")
    else:
        print("espeak-ng not found; seed details will be reused and new words will use fallback transliteration.")

    details = [build_detail(word, seed_details, espeak_exe, args.espeak_voice, args.refresh_ipa) for word in words]

    args.detail_output.write_text(json.dumps(details, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(details)} detail records: {args.detail_output}")

    if not args.no_module:
        args.module_output.write_text(module_text(details), encoding="utf-8")
        print(f"Wrote glossary module: {args.module_output}")

    review_count = sum(1 for item in details if item.get("needs_manual_review"))
    if review_count:
        print(f"Manual review needed for {review_count} item(s).")


if __name__ == "__main__":
    main()

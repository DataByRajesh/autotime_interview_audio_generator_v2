"""
Generate a Valluvar A/B pair that matches the existing Roja A/B test.

Outputs:
    outputs/valluvar_ab_raw_no_glossary.wav
    outputs/valluvar_ab_raw_no_glossary.mp3
    outputs/valluvar_ab_glossary_applied.wav
    outputs/valluvar_ab_glossary_applied.mp3

Run from PowerShell in the project root:
    python generate_valluvar_ab_test.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tamil_transliteration_dict import transliterate_tech_terms


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
PIPER_EXE = Path("C:/tts/piper/piper.exe")
VALLUVAR_MODEL = ROOT / "voices" / "ta_IN-Valluvar-medium.onnx"
VALLUVAR_CONFIG = ROOT / "voices" / "ta_IN-Valluvar-medium.onnx.json"
FFMPEG_EXE = (
    ROOT
    / "ffmpeg-2026-06-15-git-44d082edc8-essentials_build"
    / "ffmpeg-2026-06-15-git-44d082edc8-essentials_build"
    / "bin"
    / "ffmpeg.exe"
)
INPUT_TEXT = ROOT / "tests" / "roja_test.txt"
OUTPUT_DIR = ROOT / "outputs"
LENGTH_SCALE = "1.0"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        fail(f"{label} not found: {path}")


def run_command(command: list[str], *, input_text: str | None = None) -> None:
    result = subprocess.run(
        command,
        input=input_text,
        text=input_text is not None,
        encoding="utf-8" if input_text is not None else None,
        capture_output=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        fail(f"Command failed: {' '.join(command)}")


def generate_pair(label: str, text: str) -> tuple[Path, Path]:
    wav_path = OUTPUT_DIR / f"valluvar_ab_{label}.wav"
    mp3_path = OUTPUT_DIR / f"valluvar_ab_{label}.mp3"

    run_command(
        [
            str(PIPER_EXE),
            "--model",
            str(VALLUVAR_MODEL),
            "--config",
            str(VALLUVAR_CONFIG),
            "--output_file",
            str(wav_path),
            "--length_scale",
            LENGTH_SCALE,
        ],
        input_text=text,
    )

    if not wav_path.exists() or wav_path.stat().st_size == 0:
        fail(f"Piper produced an empty WAV: {wav_path}")

    run_command(
        [
            str(FFMPEG_EXE),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "128k",
            str(mp3_path),
        ]
    )

    if not mp3_path.exists() or mp3_path.stat().st_size == 0:
        fail(f"FFmpeg produced an empty MP3: {mp3_path}")

    print(f"{label} WAV: {wav_path.resolve()} ({wav_path.stat().st_size} bytes)")
    print(f"{label} MP3: {mp3_path.resolve()} ({mp3_path.stat().st_size} bytes)")
    return wav_path, mp3_path


def main() -> None:
    require_file(PIPER_EXE, "Piper executable")
    require_file(VALLUVAR_MODEL, "Valluvar model")
    require_file(VALLUVAR_CONFIG, "Valluvar config")
    require_file(FFMPEG_EXE, "FFmpeg executable")
    require_file(INPUT_TEXT, "A/B input text")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_text = INPUT_TEXT.read_text(encoding="utf-8")
    glossary_text = transliterate_tech_terms(raw_text)

    if not raw_text.strip():
        fail(f"Input text is empty: {INPUT_TEXT}")

    print("RAW first paragraph:")
    print(raw_text.split("\n\n")[0])
    print("\nGLOSSARY first paragraph:")
    print(glossary_text.split("\n\n")[0])
    print()

    print("Generating Valluvar RAW (no glossary)...")
    generate_pair("raw_no_glossary", raw_text)

    print("\nGenerating Valluvar GLOSSARY-APPLIED...")
    generate_pair("glossary_applied", glossary_text)

    print("\nDone. Compare these with:")
    print((OUTPUT_DIR / "roja_ab_raw_no_glossary.mp3").resolve())
    print((OUTPUT_DIR / "roja_ab_glossary_applied.mp3").resolve())


if __name__ == "__main__":
    main()

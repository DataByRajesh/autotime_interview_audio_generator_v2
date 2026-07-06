from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from tamil_transliteration_dict import transliterate_tech_terms


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "tests" / "roja_test.txt"
DEFAULT_OUTPUT_DIR = ROOT / "outputs"
VOICE_FILES = {
    "roja": "ta_IN-roja-medium.onnx",
    "valluvar": "ta_IN-Valluvar-medium.onnx",
}
TEST_SAMPLE = """Payment reconciliation-ன் simple meaning என்னன்னா, payment system-ல் இருக்கும் record-ம் settlement system-ல் இருக்கும் record-ம் match ஆகிறதா என்று check பண்ணுறது.

ஒரு payment app-ல் success என்று காட்டலாம். ஆனால் bank settlement file-ல் அதே amount வரவில்லை என்றால், அது reconciliation issue.

இதில் நாம் check பண்ண வேண்டியது payment ID, amount, status, timestamp, reference number, மற்றும் settlement record.

Interview-ல் இதை சொல்லும்போது, நான் payment record-ம் settlement record-ம் compare பண்ணி, mismatch இருந்தால் logs, database, மற்றும் report values check பண்ணுவேன் என்று சொல்லலாம்.

இதை simple-ஆ நினைவில் வைக்கணும்னா, payment success மட்டும் போதாது. Payment record-ம் settlement record-ம் match ஆகணும்.
"""


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.is_file():
            return path
    return None


def find_executable(explicit: Path | None, env_name: str, names: list[str], candidates: list[Path]) -> Path | None:
    if explicit:
        return explicit if explicit.is_file() else None

    env_value = os.environ.get(env_name)
    if env_value:
        env_path = Path(env_value)
        if env_path.is_file():
            return env_path

    found = first_existing(candidates)
    if found:
        return found

    for name in names:
        on_path = shutil.which(name)
        if on_path:
            return Path(on_path)

    return None


def find_model(explicit: Path | None, voice: str) -> Path | None:
    if explicit:
        return explicit if explicit.is_file() else None

    model_name = VOICE_FILES[voice]
    env_name = f"{voice.upper()}_MODEL"
    env_value = os.environ.get(env_name)
    if env_value:
        env_path = Path(env_value)
        if env_path.is_file():
            return env_path

    candidates = [
        ROOT / "voices" / model_name,
        ROOT / model_name,
        Path("C:/tts/piper/voices") / model_name,
        Path("C:/tts/voices") / model_name,
    ]
    found = first_existing(candidates)
    if found:
        return found

    for search_root in [ROOT / "voices", Path("C:/tts/piper/voices")]:
        if search_root.is_dir():
            matches = sorted(search_root.rglob(model_name))
            if matches:
                return matches[0]

    return None


def has_phoneme_ids(config_path: Path) -> bool:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False

    phoneme_id_map = config.get("phoneme_id_map")
    return isinstance(phoneme_id_map, dict) and bool(phoneme_id_map)


def resolve_config(model_path: Path, explicit: Path | None, voice: str) -> Path:
    if explicit:
        if explicit.is_file():
            return explicit
        fail(f"{voice.title()} .json not found. Expected config file: {explicit}")

    json_path = model_path.with_suffix(model_path.suffix + ".json")
    if not json_path.is_file():
        fail(f"{voice.title()} .json not found. Expected sidecar file: {json_path}")

    if has_phoneme_ids(json_path):
        return json_path

    fallback = ROOT / "voices" / "ta_IN-Valluvar-medium.onnx.json"
    if voice == "roja" and fallback.is_file() and has_phoneme_ids(fallback):
        print(f"WARNING: Roja sidecar has no phoneme_id_map; using complete Tamil config: {fallback}")
        return fallback

    fail(f"{voice.title()} .json is not usable: phoneme_id_map is missing or empty in {json_path}")


def ensure_sample_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEST_SAMPLE, encoding="utf-8")


def ensure_output_dir(path: Path) -> None:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        fail(f"Output folder missing or cannot be created: {path} ({exc})")

    if not path.is_dir():
        fail(f"Output folder missing or cannot be created: {path}")


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a short Tamil Piper sample for Roja A/B testing.")
    parser.add_argument("--voice", choices=sorted(VOICE_FILES), default="roja", help="Piper Tamil voice to test")
    parser.add_argument("--piper", type=Path, help="Path to piper.exe")
    parser.add_argument("--model", type=Path, help="Path to the selected .onnx model")
    parser.add_argument("--config", type=Path, help="Path to a Piper .onnx.json config")
    parser.add_argument("--ffmpeg", type=Path, help="Path to ffmpeg.exe")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input text file to synthesize")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    ensure_sample_file(args.input)
    ensure_output_dir(args.output_dir)

    piper_exe = find_executable(
        args.piper,
        "PIPER_EXE",
        ["piper.exe", "piper"],
        [
            ROOT / "piper.exe",
            ROOT / "piper" / "piper.exe",
            Path("C:/tts/piper/piper.exe"),
        ],
    )
    if not piper_exe:
        fail("Piper executable not found. Pass --piper or set PIPER_EXE.")

    model_path = find_model(args.model, args.voice)
    model_name = VOICE_FILES[args.voice]
    if not model_path:
        fail(f"{args.voice.title()} .onnx not found. Expected {model_name} in voices/ or C:/tts/piper/voices.")

    config_path = resolve_config(model_path, args.config, args.voice)

    ffmpeg_exe = find_executable(
        args.ffmpeg,
        "FFMPEG_EXE",
        ["ffmpeg.exe", "ffmpeg"],
        [
            ROOT
            / "ffmpeg-2026-06-15-git-44d082edc8-essentials_build"
            / "ffmpeg-2026-06-15-git-44d082edc8-essentials_build"
            / "bin"
            / "ffmpeg.exe",
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
        ],
    )
    if not ffmpeg_exe:
        fail("FFmpeg not found. Pass --ffmpeg, set FFMPEG_EXE, or add ffmpeg.exe to PATH.")

    text = transliterate_tech_terms(args.input.read_text(encoding="utf-8"))
    stem = f"{args.voice}_test"
    wav_path = args.output_dir / f"{stem}.wav"
    mp3_path = args.output_dir / f"{stem}.mp3"

    print(f"Piper:  {piper_exe}")
    print(f"Model:  {model_path}")
    print(f"Config: {config_path}")
    print(f"FFmpeg: {ffmpeg_exe}")
    print(f"Input:  {args.input}")

    run_command(
        [str(piper_exe), "--model", str(model_path), "--config", str(config_path), "--output_file", str(wav_path)],
        input_text=text,
    )
    run_command([str(ffmpeg_exe), "-y", "-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", "128k", str(mp3_path)])

    print("Generated files:")
    print(wav_path.resolve())
    print(mp3_path.resolve())


if __name__ == "__main__":
    main()

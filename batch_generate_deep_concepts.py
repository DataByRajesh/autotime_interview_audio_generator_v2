"""Generate the deep single-concept workplace interview audio batch.

This runner is resumable: if an output MP3 already exists and has content, it skips it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = Path.home() / "Downloads"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "output" / "deep_concepts_085x"
DEFAULT_CONFIG_FILE = PROJECT_DIR / "config.real.json"
DEFAULT_SPEED = "0.85"


def discover_inputs(input_dir: Path) -> list[Path]:
    files = sorted(input_dir.glob("*_Deep_Single_Concept_Workplace_Interview*.txt"))
    return [p for p in files if p.name[:2].isdigit() and 4 <= int(p.name[:2]) <= 38]


def output_for(input_path: Path, output_dir: Path, speed: str) -> Path:
    safe_stem = input_path.stem.replace(" ", "_").replace("(", "").replace(")", "")
    speed_label = speed.replace(".", "")
    return output_dir / f"{safe_stem}_{speed_label}x.mp3"


def run_one(input_path: Path, output_dir: Path, config_file: Path, speed: str, dry_run: bool) -> None:
    output_path = output_for(input_path, output_dir, speed)
    if output_path.exists() and output_path.stat().st_size > 0 and not dry_run:
        print(f"SKIP existing: {output_path.name}")
        return

    cmd = [
        sys.executable,
        str(PROJECT_DIR / "interview_audio_generator_v2.py"),
        "--config-file",
        str(config_file),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--speed",
        speed,
    ]
    if dry_run:
        cmd.append("--dry-run")

    print(f"START: {input_path.name}")
    subprocess.run(cmd, cwd=PROJECT_DIR, check=True)
    print(f"DONE:  {output_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate all deep concept MP3 files at 0.85x.")
    parser.add_argument("--dry-run", action="store_true", help="Validate all files without generating audio")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N files")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR, help="Folder containing transcript .txt files")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Folder for generated MP3 files")
    parser.add_argument("--config-file", type=Path, default=DEFAULT_CONFIG_FILE, help="Generator config file")
    parser.add_argument("--speed", default=DEFAULT_SPEED, help="Audio speed, e.g. 0.85")
    args = parser.parse_args()

    inputs = discover_inputs(args.input_dir)
    if args.limit is not None:
        inputs = inputs[: args.limit]

    if not inputs:
        raise SystemExit("No matching deep concept transcript files found.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Files: {len(inputs)}")
    print(f"Input: {args.input_dir}")
    print(f"Output: {args.output_dir}")
    print(f"Speed: {args.speed}x")

    for input_path in inputs:
        run_one(input_path, args.output_dir, args.config_file, args.speed, dry_run=args.dry_run)

    print("Batch complete.")


if __name__ == "__main__":
    main()

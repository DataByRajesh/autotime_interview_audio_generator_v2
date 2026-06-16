"""
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
  --speed 1.12
"""

from __future__ import annotations

import argparse
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

    # Make symbols speak naturally.
    symbol_replacements = {
        "→": " to ",
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


def export_mp3(
    ffmpeg_exe: str,
    input_wav: Path,
    output_mp3: Path,
    speed: float,
    bitrate: str,
) -> None:
    # atempo accepts 0.5-2.0 in one filter, so our recommended speed range is safe.
    audio_filter = ",".join([
        f"atempo={speed}",
        "highpass=f=90",
        "lowpass=f=8500",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
    ])

    cmd = [
        ffmpeg_exe,
        "-y",
        "-i",
        str(input_wav),
        "-filter:a",
        audio_filter,
        "-codec:a",
        "libmp3lame",
        "-b:a",
        bitrate,
        str(output_mp3),
    ]
    run_command(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a long-form interview podcast MP3 using Piper TTS."
    )

    parser.add_argument("--input", required=True, help="Input .txt file")
    parser.add_argument("--output", required=True, help="Output .mp3 file")
    parser.add_argument("--voice", required=True, help="Piper .onnx voice model")
    parser.add_argument("--config", default=None, help="Optional Piper .onnx.json config")
    parser.add_argument("--piper", default=None, help="Optional piper executable path")
    parser.add_argument("--ffmpeg", default=None, help="Optional ffmpeg executable path")
    parser.add_argument("--speed", type=float, default=1.12, help="Final MP3 speed. Recommended 1.10-1.18")
    parser.add_argument("--bitrate", default="128k", help="MP3 bitrate, e.g. 96k or 128k")
    parser.add_argument("--chunk-size", type=int, default=2200, help="TTS chunk size in characters")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary WAV files")
    parser.add_argument("--dry-run", action="store_true", help="Validate setup and show chunk count only")

    args = parser.parse_args()

    if not (0.8 <= args.speed <= 1.5):
        raise ValueError("Speed must be between 0.8 and 1.5. Recommended: 1.10 to 1.18.")

    input_path = require_file(args.input, "Input script")
    voice_model = require_file(args.voice, "Piper voice model")
    config_file = require_file(args.config, "Piper config") if args.config else None

    piper_exe = require_executable("piper", args.piper)
    ffmpeg_exe = require_executable("ffmpeg", args.ffmpeg)

    output_mp3 = Path(args.output)
    output_mp3.parent.mkdir(parents=True, exist_ok=True)

    raw_text = input_path.read_text(encoding="utf-8")
    clean_text = clean_text_for_tts(raw_text)
    chunks = split_text(clean_text, max_chars=args.chunk_size)

    if not chunks:
        raise ValueError("No readable text found in input file.")

    print("Setup check passed.")
    print(f"Input: {input_path}")
    print(f"Output: {output_mp3}")
    print(f"Voice: {voice_model}")
    print(f"Config: {config_file if config_file else 'Not provided'}")
    print(f"Piper: {piper_exe}")
    print(f"FFmpeg: {ffmpeg_exe}")
    print(f"Chunks: {len(chunks)}")
    print(f"Speed: {args.speed}")

    if args.dry_run:
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

    print("Exporting final MP3...")
    export_mp3(
        ffmpeg_exe=ffmpeg_exe,
        input_wav=merged_wav,
        output_mp3=output_mp3,
        speed=args.speed,
        bitrate=args.bitrate,
    )

    if not args.keep_temp:
        print("Cleaning temporary files...")
        for wav in wav_files:
            wav.unlink(missing_ok=True)
        merged_wav.unlink(missing_ok=True)
        try:
            work_dir.rmdir()
        except OSError:
            print(f"Temporary folder kept because it is not empty: {work_dir}")

    print("\nDone.")
    print(f"Final MP3 created at: {output_mp3.resolve()}")


if __name__ == "__main__":
    main()
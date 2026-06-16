# AutoTime Interview Audio Generator v2

## Readiness grade

This is a practical local automation script for generating long interview/podcast MP3 files from `.txt` scripts.

It is designed for:
- SQL interview theory
- Business Analyst interview prep
- FinTech domain revision
- UAT/testing revision
- Any long-form learning script

## What it does

```text
TXT script
→ clean technical terms for speech
→ split into safe chunks
→ generate WAV chunks using Piper
→ merge WAV files using FFmpeg
→ normalise loudness
→ speed up slightly
→ export final MP3
```

## Why this is better than free websites

Free online TTS tools hit:
- character limits
- weekly quotas
- export limits
- inconsistent voices

This local workflow avoids those limits.

## Setup needed

Install:

1. Python 3.10+
2. FFmpeg
3. Piper TTS
4. A Piper voice model `.onnx`
5. Matching voice config `.onnx.json`

## Recommended settings

Start with:

```text
speed = 1.12
chunk size = 2200
bitrate = 128k
```

If it sounds too slow:

```text
speed = 1.15
```

If it sounds too fast:

```text
speed = 1.08
```

## Dry run first

Before generating a long file, run:

```bash
python interview_audio_generator_v2.py ^
  --input sql_theory_interview_podcast_consolidated.txt ^
  --output sql_interview_podcast_final.mp3 ^
  --piper "C:\tts\piper\piper.exe" ^
  --voice "C:\tts\piper\voices\en_GB-alba-medium.onnx" ^
  --config "C:\tts\piper\voices\en_GB-alba-medium.onnx.json" ^
  --speed 1.12 ^
  --dry-run
```

If dry run passes, remove `--dry-run`.

## Grade-level summary

Current grade: B+ / practical MVP.

Strong points:
- useful structure
- no online limits
- resume-safe chunking
- dry-run validation
- better text cleaning
- volume normalisation
- final MP3 export

Not A-grade yet because:
- voice quality depends on the Piper model
- setup still requires downloading Piper and voices
- no graphical interface
- no automatic voice download
# AutoTime Interview Audio Generator v2

Local-first Python utility for turning long interview, podcast, or revision scripts into MP3 audio using Piper TTS and FFmpeg.

It is built for long-form learning material such as SQL interview theory, Business Analyst prep, FinTech revision, UAT/testing notes, and similar text-heavy study scripts.

## Features

- Cleans technical terms so acronyms and SQL keywords sound better in speech.
- Splits long text into Piper-friendly chunks.
- Generates WAV chunks with local Piper TTS.
- Resumes safely by skipping existing generated chunks.
- Merges chunks with FFmpeg.
- Applies speed, filtering, loudness normalization, and MP3 export.
- Supports JSON config files plus command-line overrides.
- Includes demo stubs and tests so the project can be checked without real TTS binaries.

## Requirements

- Python 3.10+
- Piper TTS executable
- Piper `.onnx` voice model
- Optional matching `.onnx.json` voice config
- FFmpeg executable

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

## Quick Start

Copy the example config and edit paths for your machine:

```powershell
Copy-Item config.example.json config.json
```

Run a dry run first:

```powershell
python interview_audio_generator_v2.py --config-file config.json --dry-run
```

Generate audio:

```powershell
python interview_audio_generator_v2.py --config-file config.json
```

## Real Piper Setup

Suggested Windows layout:

- `C:\tts\piper\piper.exe`
- `C:\tts\piper\voices\your_voice.onnx`
- `C:\tts\piper\voices\your_voice.onnx.json`
- `C:\ffmpeg\bin\ffmpeg.exe`

Create a local real config from the safe template:

```powershell
Copy-Item config.real.example.json config.real.json
```

Then edit `config.real.json` with your actual paths.

Test a short sample before generating a long file:

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --input sample_sql_podcast.txt --output output/sample_test.mp3
```

## Command-Line Example

```powershell
python interview_audio_generator_v2.py `
  --input sql_theory_interview_podcast_consolidated.txt `
  --output output/sql_interview_podcast_final.mp3 `
  --piper "C:\tts\piper\piper.exe" `
  --voice "C:\tts\piper\voices\en_GB-alba-medium.onnx" `
  --config "C:\tts\piper\voices\en_GB-alba-medium.onnx.json" `
  --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" `
  --speed 1.12 `
  --bitrate 128k
```

## Demo and Tests

The repo includes stub Piper/FFmpeg helpers for development and automated checks. They produce placeholder files, not real speech.

Run tests:

```powershell
python -m pytest
```

## Configuration

Important settings:

- `input`: source `.txt` script.
- `output`: final `.mp3` path.
- `voice`: Piper `.onnx` model path.
- `config`: optional Piper `.onnx.json` config path.
- `piper`: Piper executable path.
- `ffmpeg`: FFmpeg executable path.
- `speed`: final playback speed, usually `1.08` to `1.15`.
- `bitrate`: MP3 bitrate, such as `128k` or `192k`.
- `chunk_size`: text chunk size in characters, usually around `2200`.

Local files such as `config.json`, `config.real.json`, generated audio, voice models, and downloaded FFmpeg builds are ignored by git.

## Troubleshooting

- If Piper is not found, confirm the `piper` path in your config or add Piper to `PATH`.
- If FFmpeg is not found, confirm the `ffmpeg` path or run `ffmpeg -version`.
- If the voice model is missing, check the `.onnx` path and matching `.onnx.json` path.
- If audio sounds too fast or slow, adjust `speed` closer to `1.0` or within the recommended range.
- If a long generation stops midway, rerun the same command. Existing WAV chunks are skipped.

# AutoTime Interview Audio Generator v2

Local-first Python utility for turning long interview, revision, and podcast scripts into audio files using Piper TTS and FFmpeg.

The project is built for text-heavy learning material such as SQL interview theory, Business Analyst preparation, Agile/Scrum/Jira notes, UAT/testing revision, FinTech domain study, and workplace scenario practice.

## What It Does

```text
.txt script
-> clean technical terms for speech
-> split long text into safe chunks
-> generate WAV chunks with Piper
-> merge chunks with FFmpeg
-> normalize loudness and adjust speed
-> export the final audio file
```

## Features

- Converts long `.txt` scripts into audio with local Piper TTS.
- Splits large scripts into manageable chunks for reliable generation.
- Resumes safely by skipping existing generated chunks.
- Cleans acronyms and technical terms so interview content sounds clearer.
- Supports speed control, bitrate settings, loudness normalization, and MP3 export.
- Provides JSON config files plus command-line overrides.
- Includes learning modes for concept mastery, recall, comparison, and interview answers.
- Can generate spaced repetition playlists for Day 1, Day 2, Day 4, and Day 7 review.
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

Copy an example config and edit the paths for your machine:

```powershell
Copy-Item config.example.json config.json
```

Run a dry run first. This validates the setup and shows the chunk count without generating audio:

```powershell
python interview_audio_generator_v2.py --config-file config.json --dry-run
```

Generate the audio:

```powershell
python interview_audio_generator_v2.py --config-file config.json
```

## Real Piper Setup

Suggested Windows layout:

```text
C:\tts\piper\piper.exe
C:\tts\piper\voices\your_voice.onnx
C:\tts\piper\voices\your_voice.onnx.json
C:\ffmpeg\bin\ffmpeg.exe
```

Create a real local config from the safe template:

```powershell
Copy-Item config.real.example.json config.real.json
```

Edit `config.real.json` with your actual Piper, voice model, and FFmpeg paths.

Test a short sample before generating a long file:

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --input sample_sql_podcast.txt --output output/sample_test.mp3
```

Do not start with a two-hour script. Generate a short sample first and confirm the voice, speed, and volume are comfortable.

## Command-Line Example

```powershell
python interview_audio_generator_v2.py `
  --input sql_theory_interview_podcast_consolidated.txt `
  --output output/sql_interview_podcast_final.mp3 `
  --piper "C:\tts\piper\piper.exe" `
  --voice "C:\tts\piper\voices\en_GB-alba-medium.onnx" `
  --config "C:\tts\piper\voices\en_GB-alba-medium.onnx.json" `
  --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" `
  --speed 1.0 `
  --bitrate 128k
```

## Configuration

Important config fields:

- `input`: source `.txt` script.
- `output`: final audio output path.
- `voice`: Piper `.onnx` model path.
- `config`: optional Piper `.onnx.json` config path.
- `piper`: Piper executable path.
- `ffmpeg`: FFmpeg executable path.
- `speed`: playback speed. Use `1.0` for normal speed.
- `bitrate`: MP3 bitrate, such as `128k` or `192k`.
- `chunk_size`: text chunk size in characters. `2200` is a good starting point.

## Learning Modes

The generator can create psychology-backed learning scripts before sending them through the same TTS pipeline.

Available modes:

- `learn_mode`: explains a topic, why it matters, a job example, common confusion, and a recap.
- `recall_mode`: creates question-pause-answer style recall practice.
- `compare_mode`: compares two similar concepts, such as UAT vs SIT.
- `interview_mode`: creates simple, stronger, domain-specific, and polished interview answers.
- `workplace_playlist_mode`: uses shorter sentences, pause markers, repeated key points, and quiz prompts.

List built-in topic templates:

```powershell
python interview_audio_generator_v2.py --list-topic-templates
```

Create a script only:

```powershell
python interview_audio_generator_v2.py --learning-mode learn_mode --topic "UAT" --script-output output/uat_learn.txt --script-only
```

Generate one learning audio file:

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --learning-mode interview_mode --topic "Payment lifecycle" --output output/payment_lifecycle_interview.mp3 --speed 0.85
```

Generate a spaced repetition playlist:

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --spaced-playlist --topic "Agile Scrum Jira" --compare-topic "Scrum" --output output/agile_scrum_jira_playlist
```

Example playlist outputs:

```text
01_Agile_Scrum_Jira_Day1_Learn.wav
02_Agile_Scrum_Jira_Day2_Recall.wav
03_Agile_Scrum_Jira_Day4_Compare.wav
04_Agile_Scrum_Jira_Day7_Interview.wav
```

Supported pause markers in scripts:

```text
[PAUSE_SHORT]  = short pause target
[PAUSE_MEDIUM] = medium pause target
[PAUSE_LONG]   = long pause target
```

Pause markers are currently converted into punctuation and blank lines before Piper runs. They encourage natural TTS pauses, but they are not millisecond-exact silence insertion yet.

## Batch Generation

Generate separate MP3 files for deep single-concept transcripts:

```powershell
python batch_generate_deep_concepts.py
```

By default, this searches the Downloads folder for matching deep concept transcript files and writes output to:

```text
output/deep_concepts_085x
```

Useful batch flags:

```powershell
python batch_generate_deep_concepts.py --dry-run
python batch_generate_deep_concepts.py --limit 3
python batch_generate_deep_concepts.py --input-dir "C:\Users\rajan\Downloads" --output-dir output/deep_concepts_085x --speed 0.85
```

The batch runner is resumable and skips existing non-empty MP3 files.

## Demo And Tests

The repository includes stub Piper and FFmpeg helpers for development and automated checks. They produce placeholder files, not real speech.

Run tests:

```powershell
python -m pytest
```

Run with the demo config:

```powershell
python interview_audio_generator_v2.py --config-file config.demo.json
```

## Included Study Scripts

The repository includes several long-form study scripts that can be used as inputs:

- `sql_theory_interview_podcast_consolidated.txt`
- `agile_scrum_jira_2h30_expanded_tts_script.txt`
- `ireland_eu_sql_fintech_audio_pack_parts_1_2_3_extended.txt`
- `uat_deep_learning_single_concept_mastery.txt`
- `sample_sql_podcast.txt`

## Troubleshooting

- If Piper is not found, confirm the `piper` path in your config or add Piper to `PATH`.
- If FFmpeg is not found, confirm the `ffmpeg` path or run `ffmpeg -version`.
- If the voice model is missing, check the `.onnx` path and the matching `.onnx.json` path.
- If audio sounds too fast or too slow, adjust `speed`. Start with `1.0`.
- If a long generation stops midway, rerun the same command. Existing WAV chunks are skipped.
- If generated learning scripts feel too dense, add pause markers or lower the speed to around `0.85`.

## Git Notes

Local runtime files such as `config.json`, `config.real.json`, generated audio, voice models, downloaded FFmpeg builds, and temporary output folders should stay out of git.

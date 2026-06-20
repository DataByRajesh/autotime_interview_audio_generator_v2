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

Windows quick setup (beginner-friendly):

1. Install Python 3.10+ from https://www.python.org/downloads/windows/ and ensure `python` is available in PATH.
2. Download FFmpeg static build and put `ffmpeg.exe` somewhere, e.g. `C:\ffmpeg\bin\ffmpeg.exe` and add to PATH or note the path.
3. Download Piper and a compatible ONNX voice model. Place `piper.exe` and the `.onnx` model in a folder like `C:\tts\piper\`.
4. Create `config.json` (copy `config.example.json`) and edit paths to match your system.
5. Run a dry run:

```powershell
python interview_audio_generator_v2.py --config-file config.json --dry-run
```

If the dry run passes, generate the MP3:

```powershell
python interview_audio_generator_v2.py --config-file config.json
```

## Recommended settings

Start with:

```text
speed = 1.0
chunk size = 2200
bitrate = 128k
```

If it sounds too slow:

```text
speed = 1.08
```

If it sounds too fast:

```text
speed = 0.95
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
  --speed 1.0 ^
  --dry-run
```

If dry run passes, remove `--dry-run`.

**Real Piper Setup**

This project includes demo stubs for offline testing (`piper_stub.bat` / `ffmpeg_stub.bat`). These are only for development and produce placeholder audio. To run real local generation using Piper and FFmpeg, follow the steps below.

Where to place real binaries and models on Windows (suggested paths):

- `piper.exe`: `C:\tts\piper\piper.exe` (or any folder; add to PATH or reference full path in `config.real.json`).
- Voice model `.onnx`: `C:\tts\piper\voices\your_voice.onnx`.
- Voice config `.onnx.json` (optional): `C:\tts\piper\voices\your_voice.onnx.json`.
- `ffmpeg.exe`: `C:\ffmpeg\bin\ffmpeg.exe` (or add `ffmpeg` to PATH).

Create a real configuration file from the example:

1. Copy `config.real.example.json` to `config.real.json` and edit paths to match your system.
2. Test the setup using a dry run (this will validate paths and chunking):

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --dry-run
```

3. If the dry run passes, generate a short 2-minute sample to verify voice and speed:

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --input sample_sql_podcast.txt --output output/sample_test.mp3
```

Warning: Do not generate a 2-hour file until the 2-minute sample sounds clear.

Troubleshooting
- Piper path wrong: If you see "Executable path not found" or a FileNotFoundError referencing `piper`, confirm `piper.exe` exists and the `piper` path in `config.real.json` is correct. Run `piper --help` in a terminal to verify.
- FFmpeg path wrong: If FFmpeg errors appear or the script can't find `ffmpeg`, verify `ffmpeg.exe` path and that `ffmpeg -version` works.
- Voice model missing: If the voice `.onnx` file is not found, download a compatible Piper model and ensure the `voice` path in `config.real.json` points to it.
- Output folder missing: The script will create parent folders for `output` automatically, but ensure you have write permissions.
- Audio sounds robotic: Try a different `.onnx` model or adjust `--speed` closer to `1.0`. Higher speeds may introduce artifacts.
- Audio too slow/fast: Tune the `speed` value in `config.real.json`. Use `1.0` for normal playback.

Demo vs Real
- Demo (`config.demo.json`): uses `piper_stub.bat` and `ffmpeg_stub.bat` and produces placeholder audio. Useful for offline testing and CI.
- Real (`config.real.json` from `config.real.example.json`): points to actual `piper.exe`, `.onnx` model, and `ffmpeg.exe`. Use this for production runs.

Keep this project local-first: Piper and FFmpeg are free/open-source; obtain the voice models you prefer and run everything locally — no cloud is required.


## Psychology-backed workplace learning modes

The original text-to-audio command still works. The new learning features are optional and generate phone-friendly scripts before sending them through the same Piper and FFmpeg pipeline.

Available modes:
- `learn_mode`: topic, why it matters, simple meaning, job example, simpler repeat, common confusion, recap.
- `recall_mode`: question, pause, answer, repeated answer, second question, pause, final memory sentence.
- `compare_mode`: compares two similar concepts such as UAT vs SIT or settlement vs reconciliation.
- `interview_mode`: turns a concept into simple, stronger, FinTech/payment, and polished interview answers.
- `workplace_playlist_mode`: uses shorter sentences, pause markers, repeated key points, and quiz prompts.

Pause markers supported in scripts:
- `[PAUSE_SHORT]` = 700ms target
- `[PAUSE_MEDIUM]` = 1200ms target
- `[PAUSE_LONG]` = 2000ms target

Current limitation: real FFmpeg silence insertion is marked as a TODO in `replace_pause_markers_for_tts`. For now, pause markers are converted into punctuation and blank lines before Piper runs, which encourages natural TTS pauses but is not millisecond-exact.

List built-in templates:

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

Generate a spaced repetition workplace playlist. This defaults to final `.wav` files for the Day 1, Day 2, Day 4, and Day 7 sequence:

```powershell
python interview_audio_generator_v2.py --config-file config.real.json --spaced-playlist --topic "Agile Scrum Jira" --compare-topic "Scrum" --output output/agile_scrum_jira_playlist
```

Example playlist output filenames:

```text
01_Agile_Scrum_Jira_Day1_Learn.wav
02_Agile_Scrum_Jira_Day2_Recall.wav
03_Agile_Scrum_Jira_Day4_Compare.wav
04_Agile_Scrum_Jira_Day7_Interview.wav
```

Built-in topic templates include Agile, Scrum, Jira, User stories, Acceptance criteria, UAT, SIT, QA, Regression testing, SQL joins, Payment lifecycle, Settlement, Reconciliation, Incident management, Requirements gathering, Stakeholder communication, and Business Systems Analyst interview answers.


Batch-generate separate MP3 files for deep single-concept transcripts in your Downloads folder:

```powershell
python batch_generate_deep_concepts.py
```

This creates one separate MP3 per matching `.txt` file in `output/deep_concepts_085x`. It is resumable and skips existing MP3 files.

Optional batch flags:

```powershell
python batch_generate_deep_concepts.py --input-dir "C:\Users\rajan\Downloads" --output-dir output/deep_concepts_085x --speed 0.85
```

Cognitive load checks warn when:
- average sentence length is too long
- paragraphs are too dense
- no pause markers exist
- too many new terms appear in one section
- workplace speed is above 1.0
- no quiz questions are included

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

# Tamil Audio Generation (Indic Parler-TTS)

## What changed

The Tamil voice previously used was `ta_IN-Valluvar-medium.onnx` via Piper.
That voice is Tamil-only — it has no English training data, so English
technical terms embedded in Tamil scripts (SQL, API, UAT, sprint, backlog)
came out mispronounced.

Valluvar has been removed. Tamil audio now goes through `indic_tamil_tts.py`,
using AI4Bharat's `indic-parler-tts` model, which is trained on Tamil and
English together. Mixed-language sentences sound noticeably more natural
as a result.

This is a separate script from the main Piper + FFmpeg pipeline. English
scripts still go through `interview_audio_generator_v2.py` exactly as
before — nothing changes there.

## One-time setup

```powershell
pip install --break-system-packages torch transformers soundfile
pip install --break-system-packages git+https://github.com/huggingface/parler-tts.git
```

First run downloads the model (a few GB) from Hugging Face and caches it
under `~/.cache/huggingface`. After that it runs fully offline.

CPU works but is slow. If you have a GPU, or access to a free Colab
session, use it — especially for anything longer than a short sample.

## CPU vs GPU — read this before generating a full script

Tested on a real machine: CPU-only generation ran at roughly **40x real-time**
(a 17-second clip took most of 20 minutes once the model was already
cached). For a short sample that's fine. For a full-length podcast script
it isn't — a 30-minute episode would take the better part of a day of
continuous CPU time.

For anything beyond a short sample, generate on a GPU instead:

1. Open a Google Colab notebook, select a GPU runtime (Runtime → Change
   runtime type → GPU).
2. Install the same dependencies there:
   ```
   !pip install torch transformers soundfile
   !pip install git+https://github.com/huggingface/parler-tts.git
   ```
3. Upload `indic_tamil_tts.py` and your Tamil `.txt` script to the Colab
   session (or mount Google Drive).
4. Log in with your Hugging Face token: `huggingface-cli login` or set
   `HUGGING_FACE_HUB_TOKEN` in the Colab environment.
5. Run the same command as local:
   ```
   !python indic_tamil_tts.py --input tamil_script.txt --output-dir output/tamil_chunks
   ```
   `IndicParlerTamilTTS` already auto-detects CUDA (`torch.cuda.is_available()`),
   so no code changes are needed — it'll use the Colab GPU automatically.
6. Download the generated WAV chunks (or the final MP3, if FFmpeg is
   available in the Colab session and you use `--output` instead of
   `--output-dir`) and continue locally as normal.

Free Colab GPU sessions are time-limited and can disconnect, so this is
best suited for a few chunks or one script at a time — not a fully
unattended overnight run.

## Usage

Test on a short Tamil sample first — raw WAV chunks only, no merge:

```powershell
python indic_tamil_tts.py --input tamil_sample.txt --output-dir output/tamil_test_chunks
```

For a final merged MP3 (recommended — same behaviour as the Piper
pipeline: generates chunks, merges with FFmpeg, exports MP3, cleans up
temp files):

```powershell
python indic_tamil_tts.py --input tamil_script.txt --output output/tamil_final.mp3 --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe"
```

Keep the intermediate WAV chunks and merged.wav (useful for debugging
or spot-checking individual chunks):

```powershell
python indic_tamil_tts.py --input tamil_script.txt --output output/tamil_final.mp3 --ffmpeg "C:\ffmpeg\bin\ffmpeg.exe" --keep-temp
```

Or use a config file, same pattern as the English pipeline:

```powershell
Copy-Item config.tamil.example.json config.tamil.json
python indic_tamil_tts.py --config-file config.tamil.json
```

CLI flags override config file values, so you can still do a one-off
change without editing the file:

```powershell
python indic_tamil_tts.py --config-file config.tamil.json --chunk-size 400
```

`--output` and `--output-dir` are mutually exclusive purposes: use
`--output` for a finished MP3/WAV file (recommended), or `--output-dir`
if you only want the raw WAV chunks and plan to merge them yourself.

## Tuning the voice

The voice isn't a fixed `.onnx` file — it's described in a text prompt.
Adjust `DEFAULT_DESCRIPTION` in `indic_tamil_tts.py`, or pass `--description`
on the command line, e.g.:

```powershell
python indic_tamil_tts.py --input tamil_script.txt --output-dir output/tamil_chunks --description "A male Tamil speaker delivers speech at a slightly slow pace with a calm, confident tone. The recording is studio quality with no background noise."
```

## If English words still sound off

`indic_tamil_tts.py` includes `TAMIL_TECH_REPLACEMENTS` — a small dict that
swaps known English acronyms for Tamil-script phonetic forms before
synthesis (SQL, API, UAT, etc.). If you hit a term that still comes out
wrong, add it to that list rather than typing the raw English word.

## Chunk size

Indic Parler-TTS chunks default to 600 characters (smaller than Piper's
2200), since it handles shorter chunks more reliably. Adjust with
`--chunk-size` if needed.

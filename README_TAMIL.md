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

## Usage

Test on a short Tamil sample first:

```powershell
python indic_tamil_tts.py --input tamil_sample.txt --output-dir output/tamil_test_chunks
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

Then merge the generated WAV chunks with FFmpeg, the same way the
existing Piper pipeline merges chunks — see `merge_wav_chunks` in
`interview_audio_generator_v2.py` for the reference command.

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

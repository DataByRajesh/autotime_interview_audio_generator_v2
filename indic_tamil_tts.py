r"""
AutoTime Interview Audio Generator v2 - Tamil TTS Engine
----------------------------------------------------------
Generates Tamil speech (with natural English code-switching) using
AI4Bharat's Indic Parler-TTS model. Free, open-source, fully local.

Replaces: Piper + ta_IN-Valluvar-medium.onnx
Why: Valluvar is a Tamil-only voice. It has no English training data,
so English technical terms embedded in Tamil scripts (SQL, API, UAT,
sprint, backlog) come out mispronounced. Indic Parler-TTS is trained
on Tamil AND English in the same model, so mixed-language sentences
sound far more natural.

Model: ai4bharat/indic-parler-tts (Hugging Face)
License: check the model card on Hugging Face before commercial use.

One-time install:
    pip install --break-system-packages torch transformers soundfile
    pip install --break-system-packages git+https://github.com/huggingface/parler-tts.git

First run downloads the model (a few GB) and caches it locally under
~/.cache/huggingface. After that it runs fully offline.

CPU works but is slow. A GPU (even a modest one, or a free Colab
session) is strongly recommended for anything longer than a short
sample.

Usage:
    python indic_tamil_tts.py --input tamil_script.txt --output-dir output/tamil_chunks

Then merge the WAV chunks with FFmpeg the same way the existing
Piper pipeline does (see merge_wav_chunks in interview_audio_generator_v2.py).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from interview_audio_generator_v2 import export_mp3, export_wav, merge_wavs

MODEL_NAME = "ai4bharat/indic-parler-tts"

DEFAULT_DESCRIPTION = (
    "A clear female Tamil speaker delivers speech at a moderate pace "
    "with a warm, professional tone. The recording is studio quality "
    "with no background noise."
)

# Safety-net text replacements. Even a bilingual model can stumble on
# raw acronyms with no vowel sounds. These are transliterated the way
# a Tamil speaker would actually say them, so the model reads familiar
# Tamil-script syllables instead of guessing at Latin-script letters.
# Extend this list as you find more terms that come out wrong.
TAMIL_TECH_REPLACEMENTS = [
    ("SQL", "எஸ்.க்யூ.எல்."),
    ("UAT", "யு.ஏ.டி."),
    ("API", "ஏ.பி.ஐ."),
    ("BA", "பி.ஏ."),
    ("IT", "ஐ.டி."),
    ("CSV", "சி.எஸ்.வி."),
    ("JSON", "ஜேசன்"),
    ("SIT", "எஸ்.ஐ.டி."),
]


def apply_tamil_tech_replacements(text: str) -> str:
    """Swap known English acronyms/terms for Tamil-script phonetic forms."""
    for original, replacement in TAMIL_TECH_REPLACEMENTS:
        text = re.sub(rf"\b{re.escape(original)}\b", replacement, text)
    return text


class IndicParlerTamilTTS:
    """Loads the Indic Parler-TTS model once, reused across all chunks."""

    def __init__(self, device: str | None = None, description: str = DEFAULT_DESCRIPTION):
        import torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        self.device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"Loading {MODEL_NAME} on {self.device} (first run downloads the model)...")

        self.model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL_NAME).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.description_tokenizer = AutoTokenizer.from_pretrained(
            self.model.config.text_encoder._name_or_path
        )
        self.description = description

    def synthesize_chunk(self, text: str, output_wav: Path) -> Path:
        """Synthesize a single text chunk to a WAV file."""
        import soundfile as sf

        description_ids = self.description_tokenizer(
            self.description, return_tensors="pt"
        ).to(self.device)
        prompt_ids = self.tokenizer(text, return_tensors="pt").to(self.device)

        generation = self.model.generate(
            input_ids=description_ids.input_ids,
            attention_mask=description_ids.attention_mask,
            prompt_input_ids=prompt_ids.input_ids,
            prompt_attention_mask=prompt_ids.attention_mask,
        )
        audio = generation.cpu().numpy().squeeze()
        sf.write(str(output_wav), audio, self.model.config.sampling_rate)
        return output_wav


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.?!])\s+")


def split_tamil_text(text: str, chunk_size: int = 600) -> list[str]:
    """
    Sentence-aware chunker for Tamil/mixed text. Splits on '.', '?', and
    '!' boundaries and keeps each chunk under chunk_size characters.
    Interview-style scripts are mostly questions, so '?' and '!' need to
    end a sentence just as reliably as '.' does, or they get merged into
    oversized chunks. Indic Parler-TTS handles shorter chunks more
    reliably than Piper does, so the default here is smaller than the
    Piper pipeline's chunk_size (2200).
    """
    normalised = text.replace("\n", " ")
    raw_sentences = _SENTENCE_SPLIT_RE.split(normalised)
    sentences = [s.strip() for s in raw_sentences if s.strip()]

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) > chunk_size and current:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def synthesize_tamil_script(
    input_path: Path,
    output_dir: Path,
    chunk_size: int = 600,
    description: str = DEFAULT_DESCRIPTION,
) -> list[Path]:
    """
    Splits a Tamil .txt script into chunks, applies tech-term replacements,
    and synthesizes each chunk with Indic Parler-TTS. Resume-safe: skips
    chunks that already exist, matching the Piper pipeline's behaviour.
    Returns the list of generated WAV chunk paths ready for FFmpeg merge.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_text = input_path.read_text(encoding="utf-8")
    cleaned_text = apply_tamil_tech_replacements(raw_text)
    chunks = split_tamil_text(cleaned_text, chunk_size)

    engine = IndicParlerTamilTTS(description=description)
    wav_paths = []
    for i, chunk in enumerate(chunks, start=1):
        out_path = output_dir / f"chunk_{i:04d}.wav"
        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"Skipping existing chunk {i}/{len(chunks)}")
            wav_paths.append(out_path)
            continue
        print(f"Generating chunk {i}/{len(chunks)}...")
        engine.synthesize_chunk(chunk, out_path)
        wav_paths.append(out_path)

    return wav_paths


def synthesize_tamil_audio_file(
    input_path: Path,
    output_path: Path,
    ffmpeg_exe: str,
    chunk_size: int = 600,
    description: str = DEFAULT_DESCRIPTION,
    speed: float = 1.0,
    bitrate: str = "128k",
    keep_temp: bool = False,
) -> Path:
    """
    Full pipeline: text -> WAV chunks (Indic Parler-TTS) -> merged WAV ->
    final MP3 or WAV via FFmpeg. Mirrors generate_audio_file() in
    interview_audio_generator_v2.py so Tamil output behaves the same way
    English output does (resume-safe chunks, cleanup unless --keep-temp).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    work_dir = output_path.parent / f"{output_path.stem}_temp"

    wav_files = synthesize_tamil_script(
        input_path=input_path,
        output_dir=work_dir,
        chunk_size=chunk_size,
        description=description,
    )

    if not wav_files:
        raise ValueError("No readable text found in input file.")

    merged_wav = work_dir / "merged.wav"
    print("Merging WAV chunks...")
    merge_wavs(ffmpeg_exe, wav_files, merged_wav)

    if output_path.suffix.lower() == ".wav":
        print("Exporting final WAV...")
        export_wav(
            ffmpeg_exe=ffmpeg_exe,
            input_wav=merged_wav,
            output_wav=output_path,
            speed=speed,
        )
    else:
        print("Exporting final MP3...")
        export_mp3(
            ffmpeg_exe=ffmpeg_exe,
            input_wav=merged_wav,
            output_mp3=output_path,
            speed=speed,
            bitrate=bitrate,
        )

    if not keep_temp:
        print("Cleaning temporary files...")
        for wav in wav_files:
            wav.unlink(missing_ok=True)
        merged_wav.unlink(missing_ok=True)
        try:
            work_dir.rmdir()
        except OSError:
            print(f"Temporary folder kept because it is not empty: {work_dir}")

    print("\nDone.")
    print(f"Final audio created at: {output_path.resolve()}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate Tamil speech from a .txt script using Indic Parler-TTS."
    )
    parser.add_argument("--config-file", default=None, help="Optional JSON config file")
    parser.add_argument("--input", default=None, help="Tamil .txt script")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for raw WAV chunks only (no merge/MP3 export). "
        "Use --output instead for a single final MP3/WAV file.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Final .mp3 or .wav file. If set, chunks are generated, merged, "
        "and exported automatically (same behaviour as the Piper pipeline).",
    )
    parser.add_argument("--ffmpeg", default=None, help="Path to ffmpeg executable")
    parser.add_argument("--speed", type=float, default=None, help="Playback speed, 1.0 = normal")
    parser.add_argument("--bitrate", default=None, help="MP3 bitrate, e.g. 96k or 128k")
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument(
        "--description",
        default=None,
        help="Voice style prompt (speaker, tone, pace)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary WAV chunks and merged.wav after MP3/WAV export",
    )
    args = parser.parse_args()

    config = {}
    if args.config_file:
        with open(args.config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

    def resolve(key: str, default=None):
        cli_value = getattr(args, key)
        if cli_value is not None:
            return cli_value
        return config.get(key, default)

    input_path = resolve("input")
    if not input_path:
        raise ValueError("Input script not provided (use --input or config-file 'input')")

    output_path = resolve("output")
    output_dir = resolve("output_dir")

    if output_path:
        ffmpeg_exe = resolve("ffmpeg", "ffmpeg")
        synthesize_tamil_audio_file(
            input_path=Path(input_path),
            output_path=Path(output_path),
            ffmpeg_exe=ffmpeg_exe,
            chunk_size=resolve("chunk_size", 600),
            description=resolve("description", DEFAULT_DESCRIPTION),
            speed=resolve("speed", 1.0),
            bitrate=resolve("bitrate", "128k"),
            keep_temp=args.keep_temp,
        )
    elif output_dir:
        synthesize_tamil_script(
            input_path=Path(input_path),
            output_dir=Path(output_dir),
            chunk_size=resolve("chunk_size", 600),
            description=resolve("description", DEFAULT_DESCRIPTION),
        )
        print("Done. WAV chunks only (no --output given, so no merge/MP3 export).")
    else:
        raise ValueError(
            "Provide either --output (final MP3/WAV, recommended) or "
            "--output-dir (raw WAV chunks only)."
        )


if __name__ == "__main__":
    main()

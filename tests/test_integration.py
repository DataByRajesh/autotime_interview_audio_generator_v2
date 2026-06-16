import sys
from pathlib import Path

# Ensure project root is on sys.path for imports when running tests from tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import interview_audio_generator_v2 as app


def test_small_integration(tmp_path, monkeypatch):
    # Create minimal input and model files
    input_file = tmp_path / "input.txt"
    input_file.write_text("Hello SQL API -> world.\n\nSecond paragraph.")

    voice_model = tmp_path / "voice.onnx"
    voice_model.write_text("dummy")

    config_file = tmp_path / "voice.onnx.json"
    config_file.write_text("{}")

    output_mp3 = tmp_path / "out.mp3"

    # Bypass executable checks (return provided custom path or a dummy name)
    monkeypatch.setattr(app, "require_executable", lambda name, custom_path=None: str(custom_path) if custom_path else name)

    # Fake generate_chunk to write a tiny WAV file for each chunk
    def fake_generate_chunk(piper_exe, voice_model, config_file, text, output_wav):
        output_wav = Path(output_wav)
        output_wav.parent.mkdir(parents=True, exist_ok=True)
        import wave
        # Open a binary file object and pass it to wave.open to avoid Path misuse
        with output_wav.open("wb") as f:
            with wave.open(f, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(22050)
                wf.writeframes(b"\x00\x00" * 10)

    monkeypatch.setattr(app, "generate_chunk", fake_generate_chunk)

    # Fake merge_wavs to create a merged.wav placeholder
    def fake_merge_wavs(ffmpeg_exe, wav_files, merged_wav):
        merged_wav = Path(merged_wav)
        merged_wav.parent.mkdir(parents=True, exist_ok=True)
        merged_wav.write_bytes(b"RIFF....WAVE")

    monkeypatch.setattr(app, "merge_wavs", fake_merge_wavs)

    # Fake export_mp3 to write an MP3 placeholder
    def fake_export_mp3(ffmpeg_exe, input_wav, output_mp3, speed, bitrate):
        Path(output_mp3).write_bytes(b"mp3data")

    monkeypatch.setattr(app, "export_mp3", fake_export_mp3)

    # Run the script via main() with CLI args
    monkeypatch.setattr(sys, "argv", [
        "interview_audio_generator_v2.py",
        "--input",
        str(input_file),
        "--output",
        str(output_mp3),
        "--voice",
        str(voice_model),
        "--config",
        str(config_file),
        "--piper",
        "piper",
        "--ffmpeg",
        "ffmpeg",
    ])

    app.main()

    assert output_mp3.exists()
    assert output_mp3.read_bytes() == b"mp3data"

    # Temporary work dir should be removed by cleanup
    work_dir = output_mp3.parent / f"{output_mp3.stem}_temp"
    assert not work_dir.exists()


def test_config_file_values_are_used(tmp_path, monkeypatch):
    input_file = tmp_path / "input.txt"
    input_file.write_text(("One sentence. " * 80) + "\n\nSecond paragraph.")

    voice_model = tmp_path / "voice.onnx"
    voice_model.write_text("dummy")

    output_mp3 = tmp_path / "out.mp3"
    config_file = tmp_path / "config.json"
    config_file.write_text(
        """
        {
          "input": "%s",
          "output": "%s",
          "voice": "%s",
          "piper": "piper",
          "ffmpeg": "ffmpeg",
          "speed": 1.2,
          "bitrate": "96k",
          "chunk_size": 100
        }
        """
        % (
            str(input_file).replace("\\", "\\\\"),
            str(output_mp3).replace("\\", "\\\\"),
            str(voice_model).replace("\\", "\\\\"),
        )
    )

    monkeypatch.setattr(app, "require_executable", lambda name, custom_path=None: str(custom_path) if custom_path else name)
    monkeypatch.setattr(app, "generate_chunk", lambda **kwargs: Path(kwargs["output_wav"]).write_bytes(b"wav"))
    monkeypatch.setattr(app, "merge_wavs", lambda ffmpeg_exe, wav_files, merged_wav: Path(merged_wav).write_bytes(b"merged"))

    export_call = {}

    def fake_export_mp3(ffmpeg_exe, input_wav, output_mp3, speed, bitrate):
        export_call["speed"] = speed
        export_call["bitrate"] = bitrate
        Path(output_mp3).write_bytes(b"mp3data")

    monkeypatch.setattr(app, "export_mp3", fake_export_mp3)
    monkeypatch.setattr(sys, "argv", [
        "interview_audio_generator_v2.py",
        "--config-file",
        str(config_file),
    ])

    app.main()

    assert export_call == {"speed": 1.2, "bitrate": "96k"}
    assert output_mp3.exists()

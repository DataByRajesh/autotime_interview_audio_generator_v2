import sys
from pathlib import Path

# Ensure project root is on sys.path for imports when running tests from tests/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import indic_tamil_tts as tamil


def _mock_tamil_pipeline(monkeypatch, input_file, *, expected_chunk_size=123):
    calls = {"mp3": None, "wav": None}

    def fake_synthesize_tamil_script(input_path, output_dir, chunk_size, description):
        assert input_path == input_file
        assert chunk_size == expected_chunk_size
        wav_1 = Path(output_dir) / "chunk_0001.wav"
        wav_2 = Path(output_dir) / "chunk_0002.wav"
        wav_1.parent.mkdir(parents=True, exist_ok=True)
        wav_1.write_bytes(b"wav1")
        wav_2.write_bytes(b"wav2")
        return [wav_1, wav_2]

    def fake_merge_wavs(ffmpeg_exe, wav_files, merged_wav):
        assert ffmpeg_exe == "ffmpeg"
        assert len(wav_files) == 2
        Path(merged_wav).write_bytes(b"merged")

    def fake_export_mp3(ffmpeg_exe, input_wav, output_mp3, speed, bitrate):
        calls["mp3"] = {
            "ffmpeg": ffmpeg_exe,
            "input_wav": Path(input_wav),
            "speed": speed,
            "bitrate": bitrate,
        }
        Path(output_mp3).write_bytes(b"mp3")

    def fake_export_wav(ffmpeg_exe, input_wav, output_wav, speed):
        calls["wav"] = {
            "ffmpeg": ffmpeg_exe,
            "input_wav": Path(input_wav),
            "speed": speed,
        }
        Path(output_wav).write_bytes(b"wav")

    monkeypatch.setattr(tamil, "synthesize_tamil_script", fake_synthesize_tamil_script)
    monkeypatch.setattr(tamil, "merge_wavs", fake_merge_wavs)
    monkeypatch.setattr(tamil, "export_mp3", fake_export_mp3)
    monkeypatch.setattr(tamil, "export_wav", fake_export_wav)
    return calls


def test_synthesize_tamil_audio_file_exports_mp3_and_cleans_temp(tmp_path, monkeypatch):
    input_file = tmp_path / "tamil.txt"
    input_file.write_text("Tamil fintech sample.", encoding="utf-8")
    output_mp3 = tmp_path / "final.mp3"
    calls = _mock_tamil_pipeline(monkeypatch, input_file)

    tamil.synthesize_tamil_audio_file(
        input_path=input_file,
        output_path=output_mp3,
        ffmpeg_exe="ffmpeg",
        chunk_size=123,
        speed=0.9,
        bitrate="96k",
    )

    assert output_mp3.read_bytes() == b"mp3"
    assert calls["mp3"] == {
        "ffmpeg": "ffmpeg",
        "input_wav": tmp_path / "final_temp" / "merged.wav",
        "speed": 0.9,
        "bitrate": "96k",
    }
    assert not (tmp_path / "final_temp").exists()


def test_synthesize_tamil_audio_file_keeps_temp_when_requested(tmp_path, monkeypatch):
    input_file = tmp_path / "tamil.txt"
    input_file.write_text("Tamil fintech sample.", encoding="utf-8")
    output_mp3 = tmp_path / "final.mp3"
    _mock_tamil_pipeline(monkeypatch, input_file)

    tamil.synthesize_tamil_audio_file(
        input_path=input_file,
        output_path=output_mp3,
        ffmpeg_exe="ffmpeg",
        chunk_size=123,
        keep_temp=True,
    )

    temp_dir = tmp_path / "final_temp"
    assert output_mp3.exists()
    assert (temp_dir / "chunk_0001.wav").read_bytes() == b"wav1"
    assert (temp_dir / "chunk_0002.wav").read_bytes() == b"wav2"
    assert (temp_dir / "merged.wav").read_bytes() == b"merged"


def test_synthesize_tamil_audio_file_exports_wav_when_requested(tmp_path, monkeypatch):
    input_file = tmp_path / "tamil.txt"
    input_file.write_text("Tamil fintech sample.", encoding="utf-8")
    output_wav = tmp_path / "final.wav"
    calls = _mock_tamil_pipeline(monkeypatch, input_file)

    tamil.synthesize_tamil_audio_file(
        input_path=input_file,
        output_path=output_wav,
        ffmpeg_exe="ffmpeg",
        chunk_size=123,
        speed=1.1,
    )

    assert output_wav.read_bytes() == b"wav"
    assert calls["wav"] == {
        "ffmpeg": "ffmpeg",
        "input_wav": tmp_path / "final_temp" / "merged.wav",
        "speed": 1.1,
    }
    assert calls["mp3"] is None
    assert not (tmp_path / "final_temp").exists()

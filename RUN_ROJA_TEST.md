# Roja Tamil Piper Test

Run this from PowerShell in the project root:

```powershell
python run_roja_test.py
```

The command creates or refreshes `tests/roja_test.txt`, generates `outputs/roja_test.wav` with Piper, converts it to `outputs/roja_test.mp3` with FFmpeg, and prints the final file paths.

Detected defaults:

```text
Piper:  C:\tts\piper\piper.exe
Roja:   voices\ta_IN-roja-medium.onnx or C:\tts\piper\voices\ta_IN-roja-medium.onnx
FFmpeg: PATH ffmpeg.exe, bundled repo ffmpeg.exe, or C:\ffmpeg\bin\ffmpeg.exe
```

Optional Valluvar check, if the model files exist:

```powershell
python run_roja_test.py --voice valluvar
```

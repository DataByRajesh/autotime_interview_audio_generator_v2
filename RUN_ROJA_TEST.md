# Tamil Piper Learning-Speed Test

Run this from PowerShell in the project root:

```powershell
python run_roja_test.py
```

The command creates or refreshes `tests/roja_test.txt`, generates `outputs/valluvar_test.wav` with Piper, converts it to `outputs/valluvar_test.mp3` with FFmpeg, and prints the final file paths. By default it uses Valluvar at `length_scale=1.30` for learning-phase clarity.

Detected defaults:

```text
Piper:  C:\tts\piper\piper.exe
Valluvar: voices\ta_IN-Valluvar-medium.onnx
Roja optional: voices\ta_IN-roja-medium.onnx
FFmpeg: PATH ffmpeg.exe, bundled repo ffmpeg.exe, or C:\ffmpeg\bin\ffmpeg.exe
```

Optional Roja check:

```powershell
python run_roja_test.py --voice roja
```

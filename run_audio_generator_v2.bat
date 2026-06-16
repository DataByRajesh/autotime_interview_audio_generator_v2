@echo off
REM AutoTime Interview Audio Generator v2 - Windows runner
REM 1) Put your input .txt in the same folder as this .bat
REM 2) Edit PIPER, VOICE, and CONFIG paths
REM 3) Double-click this file

set INPUT=sql_theory_interview_podcast_consolidated.txt
set OUTPUT=sql_interview_podcast_final.mp3

REM Change these paths to your actual Piper setup
set PIPER=C:\tts\piper\piper.exe
set VOICE=C:\tts\piper\voices\en_GB-alba-medium.onnx
set CONFIG=C:\tts\piper\voices\en_GB-alba-medium.onnx.json

REM First check setup without generating audio
python interview_audio_generator_v2.py ^
  --input "%INPUT%" ^
  --output "%OUTPUT%" ^
  --piper "%PIPER%" ^
  --voice "%VOICE%" ^
  --config "%CONFIG%" ^
  --speed 1.12 ^
  --dry-run

echo.
echo If dry run passed, press any key to generate the MP3.
pause

python interview_audio_generator_v2.py ^
  --input "%INPUT%" ^
  --output "%OUTPUT%" ^
  --piper "%PIPER%" ^
  --voice "%VOICE%" ^
  --config "%CONFIG%" ^
  --speed 1.12

pause
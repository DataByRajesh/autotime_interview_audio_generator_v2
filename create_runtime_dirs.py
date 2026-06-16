from pathlib import Path
for p in [Path(r'C:/tts/piper'), Path(r'C:/tts/piper/voices'), Path(r'C:/ffmpeg/bin')]:
    created = False
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
        created = True
    print(f"{'CREATED' if created else 'EXISTS'}:{p}")

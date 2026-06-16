# Free & Open Source Strategy

This project is intentionally local-first and uses only free, open-source tools.

Why avoid online TTS websites
- Online TTS sites often impose character limits, quotas, or require payment for high-quality voices.
- They may require uploading potentially sensitive content to third-party servers.
- Local workflows provide repeatability, privacy, and full control over voice models.

Why Piper + FFmpeg is the best free stack here
- Piper is an open-source, high-quality local TTS runtime supporting ONNX models.
- FFmpeg is the de facto open-source tool for audio processing (concatenation, filtering, loudness normalization, encoding).
- Together they cover everything needed to generate, merge, normalize and encode audio without cloud dependencies.

When Google Colab free tier can be used as a backup
- If a user's local machine cannot run the Piper model (e.g., no compatible CPU/GPU or insufficient RAM), a temporary Colab session can be a fallback to run Piper or other local TTS runtimes.
- Use Colab only to produce the voice model output, then download artifacts to run the rest of the pipeline locally.
- Note: Colab's free tier is transient and not a replacement for a local production workflow.

Why paid cloud/API tools are excluded
- Paid APIs often introduce costs, rate limits, and require network access.
- This project aims to be fully local and reproducible without vendor lock-in.

Security & privacy
- All processing happens locally. Users should still secure the voice models and avoid committing `config.json` with secrets.



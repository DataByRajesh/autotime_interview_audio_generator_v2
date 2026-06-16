#!/usr/bin/env python3
import sys
import argparse
import wave
import os

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True)
parser.add_argument("--output_file", required=True)
parser.add_argument("--config", default=None)
args = parser.parse_args()

text = sys.stdin.read() if not sys.stdin.isatty() else ""

out = args.output_file
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
with open(out, "wb") as f:
    # write a minimal valid WAV header+data via wave module
    with wave.open(f, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(b"\x00\x00" * 100)

print(f"[piper_stub] wrote {out}", file=sys.stderr)

#!/usr/bin/env python3
import sys
import os

args = sys.argv[1:]

if "-f" in args and "concat" in args:
    # merge mode: last arg is output
    output = args[-1]
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "wb") as f:
        f.write(b"RIFF....WAVE")
    print(f"[ffmpeg_stub] merged to {output}", file=sys.stderr)
else:
    # assume encode mode: last arg is output file
    output = args[-1]
    os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
    with open(output, "wb") as f:
        f.write(b"mp3data")
    print(f"[ffmpeg_stub] wrote {output}", file=sys.stderr)

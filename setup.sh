#!/usr/bin/env bash
# One-time setup for a fresh machine or cloud session. Safe to re-run.
set -euo pipefail
pip install --break-system-packages -q -r "$(dirname "$0")/requirements.txt" 2>/dev/null || pip install -q -r "$(dirname "$0")/requirements.txt"
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 1; }
M="${REELKIT_MODELS:-$HOME/.cache/reelkit}"; mkdir -p "$M"
R=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s "$M/kokoro-v1.0.onnx" ] || curl -sSL -o "$M/kokoro-v1.0.onnx" "$R/kokoro-v1.0.onnx"
[ -s "$M/voices-v1.0.bin" ]  || curl -sSL -o "$M/voices-v1.0.bin"  "$R/voices-v1.0.bin"
F="$HOME/.local/share/fonts"; mkdir -p "$F"
[ -s "$F/Anton-Regular.ttf" ] || curl -sSL -o "$F/Anton-Regular.ttf" https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf
[ -s "$F/Poppins-Bold.ttf" ]  || curl -sSL -o "$F/Poppins-Bold.ttf"  https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-Bold.ttf
fc-cache -f >/dev/null 2>&1 || true
echo "reelkit ready (models in $M)"

#!/usr/bin/env bash
# finish.sh "Title": frames + mix -> out/<slug>.mp4 with one linear gain to about -14 LUFS and a -1 dBFS peak limiter, then QA.
set -euo pipefail
TITLE="${1:-short}"; SLUG=$(echo "$TITLE" | tr 'A-Z ' 'a-z-' | tr -cd 'a-z0-9-')
I=$(ffmpeg -nostats -i work/mix.wav -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}')
G=$(python3 -c "print(round(-14 - ($I), 2))")
echo "integrated $I LUFS -> gain $G dB"
ffmpeg -y -loglevel error -framerate 30 -i frames/f%04d.jpg -i work/mix.wav \
  -af "volume=${G}dB,alimiter=limit=0.891:level=false" -ar 44100 -c:a aac -b:a 192k \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -shortest -movflags +faststart "out/$SLUG.mp4"
echo "== QA"
ffprobe -v error -show_entries format=duration -of csv=p=0 "out/$SLUG.mp4"
ffmpeg -nostats -i "out/$SLUG.mp4" -vf "freezedetect=n=0.001:d=0.4,blackdetect=d=0.1:pix_th=0.05" -af ebur128 -f null - 2>&1 | grep -E "freeze_start|freeze_duration|black_start|^\s+I:|Peak:" | tail -8 || true
ffmpeg -y -loglevel error -i "out/$SLUG.mp4" -vf "fps=1,scale=180:-1,tile=8x5" -frames:v 1 out/qa_sheet.jpg
echo "out/$SLUG.mp4"

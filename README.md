# What-If Reels

Automated 9:16 "What if?" explainer reels: AI voiceover with pitch modulation, big word-by-word captions,
animated infographics, music and sound effects. One reel is made per day and posted to Instagram Reels,
YouTube Shorts and Facebook Reels through Metricool after the owner approves it.

## Setup

```bash
./setup.sh
```

Installs Python packages, downloads the Kokoro voice model (~350 MB) and the Anton and Poppins fonts. Needs `ffmpeg`.

## Make a reel

```bash
python3 -m reelkit.make reels/everyone-shrank --stills 0.5 6 15 27 40   # preview frames -> build/contact_sheet.png
python3 -m reelkit.make reels/everyone-shrank                            # full build -> out/everyone-shrank.mp4
```

Add `--revoice` after editing the script lines. A full build takes about a minute on 2 CPUs.

## A reel folder

- `script.json`: the voice lines (one line per scene), title chip, timing and post text. See `reels/everyone-shrank/script.json`.
- `scenes.py`: `SCENES`, one drawing function per voice line, plus optional `BG`, `MUSIC`, `cut_times(i)` and `sfx(A)`.
- `out/<slug>.mp4`: the finished video.

## Library

- `reelkit/lib.py`: drawing helpers, text and chips, characters (`person`, `cat_side`, `cat_head`), real-size props in centimetres (`door`, `chair`, `counter`, `phone_upright` and more) and backgrounds.
- `reelkit/voice.py`: Kokoro TTS plus intonation styles (`dramatic`, `low`, `excited`, `question`, `funny`, `deadpan`, `chipmunk` and more).
- `reelkit/timeline.py`: word, caption and scene timing.
- `reelkit/audio.py`: music bed, sound effects and the final mix with voice ducking.
- `reelkit/make.py`: the build command.

See `CLAUDE.md` for the house style and the daily run procedure.

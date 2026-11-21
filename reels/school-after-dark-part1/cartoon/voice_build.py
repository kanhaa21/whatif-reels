"""Narrator v2 for 'I Stayed in School After Dark' (Part 1). Kokoro af_heart, built chunk by chunk so single words
can be whispered or stressed:
  v  = soft, intimate voiced speech (a little breath mixed in)
  e  = stressed voiced: slower, louder, wider pitch accent
  w  = whisper: the voice re-excited with noise through its own LPC envelope (real whisper source), tiny voicing kept
  we = stressed whisper: slower and louder
Chunks inside a line are joined with short gaps; each line starts at an anchor (picture is locked to these).
Breaths (inhales, a relieved exhale, shaky nervous breathing) are part of this track. Writes voice.wav + work/phrases.json."""
import json, os
import numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
from scipy.signal import butter, sosfilt
from kokoro_onnx import Kokoro
import sys; sys.path.insert(0, '/home/claude/whatif-reels')
from reelkit.voice import shape, _trim

M = os.path.expanduser('~/.cache/reelkit'); k = Kokoro(f'{M}/kokoro-v1.0.onnx', f'{M}/voices-v1.0.bin')
SR = 24000; rng = np.random.default_rng(5)
MODE = {'v': (0.12, 1.00), 'e': (0.10, 1.35), 'w': (0.95, 1.05), 'we': (0.95, 1.45)}   # whisper amount, gain
# (anchor s or None, gap before, [(text, mode, style, speed, gain, gap after)])
L = [
 (0.20, 0.0, [("Your dream...", 'v', 'warm', 0.98, 0.9, 0.08), ("finally comes true.", 'e', 'warm', 0.92, 1.0, 0)]),
 (None, 0.15, [("You're hiding in school", 'v', 'low', 0.98, 0.9, 0.05), ("after dark...", 'we', 'low', 0.84, 1.0, 0)]),
 (None, 0.08, [("and everyone is gone.", 'we', 'dramatic', 0.88, 0.95, 0)]),
 (5.99, 0.0, [("No teachers.", 'v', 'normal', 0.95, 1.0, 0.3), ("No students.", 'v', 'normal', 0.95, 1.0, 0.38), ("No noise.", 'we', 'low', 0.8, 1.0, 0)]),
 (10.45, 0.0, [("But every night,", 'v', 'low', 0.9, 0.95, 0.15), ("the guard", 'e', 'dramatic', 0.82, 1.0, 0.06), ("checks every classroom...", 'e', 'low', 0.84, 0.95, 0)]),
 (16.10, 0.0, [("He saw something...", 'w', 'low', 0.80, 1.0, 0.85), ("or maybe he saw me.", 'w', 'soft', 0.76, 0.72, 0)]),
 (20.60, 0.0, [("He walked out...", 'v', 'warm', 0.9, 0.95, 0.25), ("and locked", 'e', 'low', 0.86, 1.0, 0.04), ("the classroom door.", 'w', 'low', 0.84, 0.8, 0)]),
 (29.30, 0.0, [("The guard had", 'w', 'low', 0.82, 0.95, 0.05), ("already left.", 'we', 'low', 0.78, 1.0, 0)]),
 (None, 1.0, [("Then who", 'w', 'question', 0.78, 0.9, 0.2), ("knocked?", 'we', 'question', 0.72, 1.0, 0)]),
]
# (time, kind, level): in = soft inhale, shaky = nervous trembling inhale, out = relieved exhale
BREATHS = [(15.45, 'in', 0.8), (20.05, 'out', 0.9), (24.5, 'shaky', 0.9), (25.5, 'shaky', 1.0), (26.85, 'shaky', 1.0),
           (28.75, 'shaky', 1.1), (31.85, 'in', 1.0)]
TOTAL = 35.5

def bpf(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def env_rms(x, hop=120):
    n = len(x) // hop + 1; r = np.sqrt(np.array([np.mean(x[i*hop:(i+1)*hop]**2) if len(x[i*hop:(i+1)*hop]) else 0 for i in range(n)]) + 1e-12)
    return np.repeat(np.convolve(r, np.ones(3) / 3, mode='same'), hop)[:len(x)]

def whisperize(x, amt):
    snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=SR)
    lpc = call(snd, "To LPC (burg)", 18, 0.025, 0.005, 50.0)
    noise = parselmouth.Sound(rng.standard_normal(len(x)) * 0.1, sampling_frequency=SR)
    w = call([lpc, noise], "Filter", "no").values[0][:len(x)]
    w = sosfilt(butter(2, 300, 'highpass', fs=SR, output='sos'), w)
    w = w + 0.6 * bpf(w, 2000, 5500)                  # presence: keeps whispered consonants clear
    w = w * np.minimum(env_rms(x) / (env_rms(w) + 1e-6), 20)
    return (1 - amt) * x + amt * w + (0.08 * x if amt > 0.5 else 0)

def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 0.02 * np.abs(x).max()] ** 2))

out = np.zeros(int(TOTAL * SR)); meta = []; prev_end = 0.0
for anchor, gap0, chunks in L:
    t = max(anchor or 0.0, prev_end + gap0); t0 = t; words = []
    for text, mode, style, sp, g, gap in chunks:
        amt, mg = MODE[mode]
        s, sr = k.create(text, voice='af_heart', speed=sp, lang='en-us')
        s = shape(_trim(s, sr), sr, style, 100, 600)
        s = whisperize(s, amt)
        s = s / rms(s) * 0.075 * mg * g                 # loudness by RMS, so whispers and stresses sit where intended
        n = int((0.25 if text.endswith(('.', '?')) and mode == 'w' else 0.06) * SR); s[-n:] *= np.linspace(1, 0, n) ** 1.5
        i = int(t * SR); j = min(len(out), i + len(s)); out[i:j] += s[:j - i]
        words.append(f"{text}[{mode}]"); t += len(s) / SR + gap
    prev_end = t
    full = " ".join(c[0] for c in chunks)
    meta.append({"text": full, "s": round(t0, 3), "e": round(t, 3)})
    print(f"{t0:6.2f} -> {t:6.2f}  {' '.join(words)}")

def breath(kind, d=None):
    d = d or {'in': 0.6, 'out': 0.75, 'shaky': 0.85}[kind]; n = int(d * SR); x = rng.standard_normal(n); u = np.linspace(0, 1, n)
    if kind == 'out': x = bpf(x, 250, 1800); e = np.minimum(1, u / 0.12) * (1 - u) ** 1.3
    else: x = bpf(x, 500, 3200) + 0.4 * bpf(x, 3500, 6000); e = np.sin(np.pi * u) ** 1.2
    if kind == 'shaky': e = e * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 6.5 * u * d)))   # trembling inhale
    return x * e
for t, kind, lv in BREATHS:
    b = breath(kind); i = int(t * SR); b = b / np.abs(b).max() * 0.09 * lv; out[i:i + len(b)] += b
out[int((TOTAL - 0.5) * SR):] = 0
out = out / max(1.0, np.abs(out).max() / 0.95)
sf.write('voice.wav', out.astype(np.float32), SR)
json.dump({"duration": TOTAL, "phrases": meta}, open('work/phrases.json', 'w'), indent=1)

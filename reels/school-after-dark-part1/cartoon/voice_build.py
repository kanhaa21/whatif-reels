"""Narrator for 'I Stayed in School After Dark' (Part 1). Kokoro af_heart, then:
- pitch/intonation shaping from reelkit.voice styles (lower, slower, never flat)
- breathy/whisper treatment: the voice is re-excited with noise through its own LPC envelope (a real whisper source),
  blended with the voiced original so words stay clear (whisper lines are mostly noise-excited)
- quiet breaths before key lines
Each phrase is placed at an absolute time chosen from the brief's timeline. Writes voice.wav + work/phrases.json."""
import json, os
import numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
from scipy.signal import butter, sosfilt
from kokoro_onnx import Kokoro
import sys; sys.path.insert(0, '/home/claude/whatif-reels')
from reelkit.voice import shape, _trim

M = os.path.expanduser('~/.cache/reelkit'); k = Kokoro(f'{M}/kokoro-v1.0.onnx', f'{M}/voices-v1.0.bin')
SR = 24000; rng = np.random.default_rng(5)
# (start s, text, style, speed, whisper amount 0..1, gain)
# (anchor s or None, gap after previous, text, style, speed, whisper amount, gain)
P = [
 (0.20, 0, "Your dream finally comes true.", "warm", 0.92, 0.30, 1.0),
 (None, 0.22, "You're hiding in school after dark...", "low", 0.90, 0.35, 1.0),
 (None, 0.12, "and everyone is gone.", "dramatic", 0.86, 0.40, 0.95),
 (None, 0.38, "No teachers.", "normal", 0.9, 0.25, 1.0),
 (None, 0.38, "No students.", "normal", 0.9, 0.25, 1.0),
 (None, 0.45, "No noise.", "low", 0.80, 0.45, 0.9),
 (None, 0.6, "But every night,", "low", 0.84, 0.35, 0.95),
 (None, 0.2, "the guard checks every classroom...", "dramatic", 0.78, 0.40, 0.95),
 (16.10, 0, "He saw something...", "low", 0.78, 0.80, 0.9),
 (None, 0.85, "or maybe he saw me.", "soft", 0.76, 0.85, 0.7),
 (20.60, 0, "He walked out...", "warm", 0.84, 0.45, 0.9),
 (None, 0.3, "and locked the classroom door.", "low", 0.80, 0.55, 0.85),
 (29.30, 0, "The guard had already left.", "low", 0.80, 0.85, 0.9),
 (None, 1.0, "Then who knocked?", "question", 0.70, 0.90, 0.8),
]
BREATHS = [0.0, 15.55, 25.4, 26.9, 28.6, 31.6]          # quiet inhales (seconds)
TOTAL = 35.5

def env_rms(x, hop=120):
    n = len(x) // hop + 1; r = np.sqrt(np.array([np.mean(x[i*hop:(i+1)*hop]**2) if len(x[i*hop:(i+1)*hop]) else 0 for i in range(n)]) + 1e-12)
    r = np.convolve(r, np.ones(3) / 3, mode='same')
    return np.repeat(r, hop)[:len(x)]

def whisperize(x, amt):
    if amt <= 0: return x
    snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=SR)
    lpc = call(snd, "To LPC (burg)", 18, 0.025, 0.005, 50.0)
    noise = parselmouth.Sound(rng.standard_normal(len(x)) * 0.1, sampling_frequency=SR)
    w = call([lpc, noise], "Filter", "no").values[0][:len(x)]
    w = sosfilt(butter(2, 300, 'highpass', fs=SR, output='sos'), w)
    ex, ew = env_rms(x), env_rms(w)
    w = w * np.minimum(ex / (ew + 1e-6), 20)
    # keep some voicing for clarity; voiced part softened a little
    return (1 - amt) * x + amt * w * 0.9 + 0.15 * amt * x

out = np.zeros(int(TOTAL * SR)); meta = []; prev_end = 0.0
for (anchor, gap, text, style, sp, wamt, g) in P:
    s, sr = k.create(text, voice='af_heart', speed=sp, lang='en-us')
    s = shape(_trim(s, sr), sr, style, 100, 600)
    s = whisperize(s, wamt)
    s = s / (np.max(np.abs(s)) + 1e-9) * 0.6 * g
    # soft fade-out tail (final words fade naturally)
    n = int(0.08 * SR); s[-n:] *= np.linspace(1, 0, n)
    t = max(anchor or 0.0, prev_end + gap); prev_end = t + len(s) / SR
    i = int(t * SR); j = min(len(out), i + len(s)); out[i:j] += s[:j - i]
    meta.append({"text": text, "s": round(t, 3), "e": round(t + len(s) / SR, 3)})
    print(f"{t:6.2f} -> {t + len(s)/SR:6.2f}  {text}")
# breaths
for t in BREATHS:
    d = 0.55; x = rng.standard_normal(int(d * SR))
    x = sosfilt(butter(2, [450, 2600], 'bandpass', fs=SR, output='sos'), x)
    e = np.sin(np.pi * np.linspace(0, 1, len(x))) ** 1.5
    i = int(t * SR); out[i:i + len(x)] += x * e * 0.035
out[int((TOTAL - 0.5) * SR):] = 0
sf.write('voice.wav', out.astype(np.float32), SR)
json.dump({"duration": TOTAL, "phrases": meta}, open('work/phrases.json', 'w'), indent=1)

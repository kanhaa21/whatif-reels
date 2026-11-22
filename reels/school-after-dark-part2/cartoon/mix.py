"""mix.py voice.wav music.wav sfx.wav out.wav
Part 1's level-lock: music at 18 % of the voice's gated RMS, SFX scaled so the loudest hit sits at 0.9x the voice peak.
No ducking or compression. Last 0.5 s forced to digital silence."""
import sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
SR = 44100
def load(p):
    x, sr = sf.read(p)
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = resample_poly(x, SR, sr)
    return x
def gated_rms(x, gate_db=-40):
    hop = int(0.05 * SR); r = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    keep = r[r > r.max() * 10 ** (gate_db / 20)]; return np.sqrt(np.mean(keep ** 2))
v, m, s = (load(p) for p in sys.argv[1:4])
n = max(len(v), len(m), len(s)); v, m, s = (np.pad(a, (0, n - len(a))) for a in (v, m, s))
m *= 0.18 * gated_rms(v) / gated_rms(m)
s *= 0.9 * np.abs(v).max()
db = lambda a, b: 20 * np.log10(gated_rms(a) / gated_rms(b))
print(f"music vs voice: {db(m, v):+.1f} dB   sfx vs voice: {db(s, v):+.1f} dB")
mix = v + m + s
mix[int((n / SR - 0.5) * SR):] = 0
sf.write(sys.argv[4], mix.astype(np.float32), SR)

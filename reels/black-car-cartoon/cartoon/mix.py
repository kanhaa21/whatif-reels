"""mix.py voice.wav music.wav sfx.wav out.wav
Music at exactly 50 % of the voice's gated RMS (-6 dB); SFX at 50 % gated RMS with peaks capped at 0.7x the voice peak.
No ducking or compression: the only processing on the sum is one linear gain + a peak limiter (in finish.sh)."""
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
    hop = int(0.05 * SR); fr = [x[i:i + hop] for i in range(0, len(x) - hop, hop)]
    r = np.array([np.sqrt(np.mean(f ** 2)) for f in fr]); top = r.max()
    keep = r[r > top * 10 ** (gate_db / 20)]
    return np.sqrt(np.mean(keep ** 2))

v, m, s = (load(p) for p in sys.argv[1:4])
n = max(len(v), len(m), len(s)); v, m, s = (np.pad(a, (0, n - len(a))) for a in (v, m, s))
rv = gated_rms(v)
m *= 0.5 * rv / gated_rms(m)
s *= 0.5 * rv / gated_rms(s)
cap = 0.7 * np.abs(v).max()
if np.abs(s).max() > cap: s *= cap / np.abs(s).max()
db = lambda a, b: 20 * np.log10(gated_rms(a) / gated_rms(b))
print(f"music vs voice: {db(m, v):+.1f} dB   sfx vs voice: {db(s, v):+.1f} dB   sfx peak/voice peak: {np.abs(s).max() / np.abs(v).max():.2f}")
mix = v + m + s
sf.write(sys.argv[4], mix.astype(np.float32), SR)

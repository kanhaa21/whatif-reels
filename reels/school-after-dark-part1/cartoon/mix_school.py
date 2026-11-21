"""mix_school.py voice.wav music.wav sfx.wav out.wav
Same level-lock as mix.py, but this reel asks for music "very subtle beneath the narration":
music at 16 % of the voice's gated RMS (-16 dB), SFX at 50 % (-6 dB) with peaks capped at 0.7x the voice peak.
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
rv = gated_rms(v)
m *= 0.16 * rv / gated_rms(m)
s *= 0.50 * rv / gated_rms(s)
cap = 0.7 * np.abs(v).max()
if np.abs(s).max() > cap: s *= cap / np.abs(s).max()
db = lambda a, b: 20 * np.log10(gated_rms(a) / gated_rms(b))
print(f"music vs voice: {db(m, v):+.1f} dB   sfx vs voice: {db(s, v):+.1f} dB   sfx peak/voice peak: {np.abs(s).max() / np.abs(v).max():.2f}")
mix = v + m + s
mix[int((n / SR - 0.5) * SR):] = 0
seg = lambda a, t0, t1: 20 * np.log10(np.sqrt(np.mean(a[int(t0 * SR):int(t1 * SR)] ** 2)) + 1e-12)
print("music after 25 s (dB):", round(seg(m, 25.0, 35.5), 1), "  last 0.5 s mix peak:", np.abs(mix[-int(0.5 * SR):]).max())
for name, t0, t1 in (("knock1", 26.2, 26.5), ("knock3", 28.1, 28.4), ("impact", 31.43, 31.9), ("voice 'already left'", 29.3, 31.1)):
    print(f"  {name}: peak {20*np.log10(np.abs(mix[int(t0*SR):int(t1*SR)]).max()):.1f} dBFS")
sf.write(sys.argv[4], mix.astype(np.float32), SR)

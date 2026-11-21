"""mix_vo3.py voice.wav sfx.wav out.wav
The owner's recording (voice + its own drone bed + knocks) is untouched. Our SFX stem is in peak units and is scaled
so its loudest hit (the third knock body) sits at 0.6x the recording's peak. No music added, no ducking/compression.
Output is 48.5 s; the last 0.5 s is digital silence."""
import sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
SR = 44100; DUR = 48.5
def load(p):
    x, sr = sf.read(p)
    if x.ndim > 1: x = x.mean(1)
    if sr != SR: x = resample_poly(x, SR, sr)
    return x
v, s = load(sys.argv[1]), load(sys.argv[2])
n = int(DUR * SR); v = np.pad(v, (0, max(0, n - len(v))))[:n]; s = np.pad(s, (0, max(0, n - len(s))))[:n]
s *= 0.6 * np.abs(v).max()
mix = v + s
f = int(0.3 * SR); e = n - int(0.5 * SR); mix[e - f:e] *= np.linspace(1, 0, f); mix[e:] = 0
print(f"recording peak {20*np.log10(np.abs(v).max()):.1f} dBFS, sfx peak {20*np.log10(np.abs(s).max()):.1f} dBFS")
sf.write(sys.argv[3], mix.astype(np.float32), SR)

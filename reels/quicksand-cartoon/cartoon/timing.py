"""Phrase timing without ASR: speech segments from energy, syllable nuclei from band envelope peaks,
then phrases (script split at punctuation) placed by cumulative syllable count, with phrase starts
snapped to segment starts when one is near. Writes work/phrases.json."""
import json, re, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfiltfilt, find_peaks

voice, script = sys.argv[1], sys.argv[2]
x, sr = sf.read(voice)
if x.ndim > 1: x = x.mean(1)
hop = int(0.01 * sr)
db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)]) + 1e-9)
sp = db > db.max() - 38
segs = []; i = 0; n = len(sp)
while i < n:
    if sp[i]:
        j = i
        while j < n and (sp[j] or sp[j:j + 15].any()): j += 1
        if (j - i) > 8: segs.append([i / 100, j / 100])
        i = j
    else: i += 1
# syllable nuclei
b = sosfiltfilt(butter(2, [300, 2500], "bandpass", fs=sr, output="sos"), x)
env = np.array([np.sqrt(np.mean(b[i:i + hop] ** 2)) for i in range(0, len(b) - hop, hop)])
env = np.convolve(env, np.hanning(9) / np.hanning(9).sum(), mode="same")
edb = 20 * np.log10(env + 1e-9)
pk, _ = find_peaks(edb, prominence=4, distance=9, height=edb.max() - 30)
nuc = pk / 100.0


def syl(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w: return 0
    c = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and c > 1: c -= 1
    return max(1, c)

text = open(script).read()
phr = [p.strip() for p in re.findall(r"[^,.?!:]+[,.?!:]?", text.replace("\n", " ")) if p.strip()]
ps = [sum(syl(w) for w in p.split()) for p in phr]
tot_s = sum(ps); tot_n = len(nuc)
print(f"{len(segs)} segments, {tot_n} nuclei vs {tot_s} script syllables")
# map cumulative script syllables -> nucleus times (scaled)
cum = np.concatenate([[0], np.cumsum(ps)])
out = []
for k, p in enumerate(phr):
    a = cum[k] / tot_s * tot_n; bnd = cum[k + 1] / tot_s * tot_n
    ia = min(tot_n - 1, int(round(a))); ib = max(ia, min(tot_n - 1, int(round(bnd)) - 1))
    s = nuc[ia] - 0.12; e = nuc[ib] + 0.2
    # snap start to a segment start within 0.45 s
    near = min(segs, key=lambda g: abs(g[0] - s))
    if abs(near[0] - s) < 0.45: s = near[0]
    out.append({"text": p, "s": round(max(0, s), 2), "e": round(e, 2), "syl": ps[k]})
for k in range(len(out) - 1):
    out[k]["e"] = min(out[k]["e"], out[k + 1]["s"])
    # end at segment end if inside a gap
json.dump({"duration": len(x) / sr, "segments": segs, "phrases": out}, open("work/phrases.json", "w"), indent=1)
for o in out: print(f'{o["s"]:6.2f} {o["e"]:6.2f}  {o["text"]}')

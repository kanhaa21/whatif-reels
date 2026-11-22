"""Tense whisper, v2 (owner's reference: work/ref_tensed_whisper.wav, 23 Nov 2026).

The v1 whisper (LPC filter re-excited with noise) was 100 % unvoiced and thin: no body under 300 Hz, a boxy
600-1200 Hz hump and little air. The reference is a close-mic stage whisper: about a quarter of its active frames still
carry a little voicing (median about 166 Hz), strong chest/proximity energy at 150-300 Hz and an airy top.

Method (WORLD vocoder, so timing is sample-for-sample the same as the Kokoro take):
  1. harvest/cheaptrick/d4c analysis of the Kokoro line
  2. whisper  = resynthesis with f0 = 0 everywhere (noise through the speaker's own spectral envelope)
  3. breath-voice = resynthesis with f0 x 1.3 (tense whispers rise) and aperiodicity floored at 0.55
  4. the breath-voice is let through only on the strongest voiced frames (about the reference's voiced share), smoothed
  5. a long-term-spectrum EQ (work/whisper_eq.npy) pulls the result towards the reference's spectrum
"""
import numpy as np, pyworld as pw
from scipy.signal import fftconvolve, firwin2

FP = 5.0  # ms

def raw(x, sr, stress=False):
    x = np.ascontiguousarray(x, dtype=np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=60, f0_ceil=400, frame_period=FP)
    sp = pw.cheaptrick(x, f0, t, sr); ap = pw.d4c(x, f0, t, sr)
    w = pw.synthesize(np.zeros_like(f0), sp, ap, sr, FP)
    b = pw.synthesize(f0 * 1.3, sp, np.maximum(ap, 0.55), sr, FP)
    # voicing mask: voiced frames whose energy is in the top part of this line's voiced frames
    en = np.log(sp.sum(1) + 1e-12); vo = f0 > 0
    m = np.zeros_like(f0)
    if vo.sum() > 3:
        th = np.percentile(en[vo], 20); m[vo & (en > th)] = 1.0
    k = np.hanning(9); k /= k.sum(); m = np.convolve(m, k, mode='same')     # ~40 ms crossfades
    hop = int(sr * FP / 1000); mm = np.repeat(m, hop)
    n = len(x); w = np.pad(w, (0, max(0, n - len(w))))[:n]; b = np.pad(b, (0, max(0, n - len(b))))[:n]; mm = np.pad(mm, (0, max(0, n - len(mm))))[:n]
    rw = np.sqrt(np.mean(w ** 2)) + 1e-9; rb = np.sqrt(np.mean(b ** 2)) + 1e-9
    gv = 0.0                                                                  # owner (23 Nov): pure whisper, no voice leaking through
    return w / rw + gv * mm * b / rb

def ltas(x, sr, N=1024):
    e = np.sqrt(np.convolve(x ** 2, np.ones(N) / N, mode='same')); thr = e.max() * 0.1
    S = [np.abs(np.fft.rfft(x[i:i + N] * np.hanning(N))) ** 2 for i in range(0, len(x) - N, N // 2) if e[i + N // 2] > thr]
    return np.mean(S, 0), np.fft.rfftfreq(N, 1 / sr)

def design_eq(ref, ours, sr, max_db=12.0):
    (Lr, f), (Lo, _) = ltas(ref, sr), ltas(ours, sr)
    g = 10 * np.log10(Lr / Lr.sum() + 1e-15) - 10 * np.log10(Lo / Lo.sum() + 1e-15)
    # smooth over 1/3 octave, limit, roll the correction off below 70 Hz and above 11 kHz
    sm = np.array([g[(f >= fc / 2 ** 0.5) & (f <= fc * 2 ** 0.5)].mean() if fc > 0 else g[0] for fc in f])   # 1-octave smoothing
    sm = np.clip(sm, -max_db, max_db); sm[f < 70] = np.minimum(sm[f < 70], -6); sm[f > 11000] = np.minimum(sm[f > 11000], 0)
    # the reference's 150-300 Hz energy is its own voicing; boosting it here put a pitched hum back into the whisper
    # (owner, 23 Nov: "too voiced"), so nothing below 350 Hz is ever boosted, and boosts are capped at +8 dB
    sm[f < 350] = np.minimum(sm[f < 350], 0); sm = np.minimum(sm, 8.0)
    return firwin2(511, f / (sr / 2), 10 ** (sm / 20))

def apply_eq(x, fir):
    y = fftconvolve(x, fir)[255:255 + len(x)]
    return y

"""Music bed, sound effects and final mix. A reel's scenes module may define sfx(A) and MUSIC."""
import json, os
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt

SR = 44100


class Mixer:
    def __init__(self, tl, voice_dir, seed=3):
        self.tl = tl
        self.N = int((tl["total"] + 0.3) * SR)
        self.rng = np.random.default_rng(seed)
        self.voice = np.zeros(self.N); self.vmask = np.zeros(self.N)
        self.music = np.zeros(self.N); self.sfx_buf = np.zeros(self.N)
        self.mgain = np.ones(self.N)
        self._plucks = {}
        for ln in tl["lines"]:
            x, sr = sf.read(os.path.join(voice_dir, f"line{ln['i']}.wav"))
            x = resample_poly(x, SR, sr)
            self.add(self.voice, x, ln["start"])
            self.vmask[self.at(ln["start"]): self.at(ln["start"]) + len(x)] = 1

    # ---- basics
    def at(self, t): return int(t * SR)
    def add(self, buf, x, t, g=1.0):
        i = max(0, self.at(t)); j = min(len(buf), i + len(x))
        if j > i: buf[i:j] += x[: j - i] * g
    def S(self, i): return self.tl["scenes"][i]["t0"]
    def W(self, i, sub, nth=0):
        k = 0
        for w in self.tl["lines"][i]["words"]:
            if sub.lower() in w["w"].lower():
                if k == nth: return w["s"]
                k += 1
        raise KeyError((i, sub))
    def env(self, n, a, d):
        e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
        return e * np.exp(-np.arange(n) / (d * SR))
    def bp(self, x, lo, hi): return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)
    def lp(self, x, f): return sosfilt(butter(2, f, "lowpass", fs=SR, output="sos"), x)
    def hp(self, x, f): return sosfilt(butter(2, f, "highpass", fs=SR, output="sos"), x)
    def noise(self, d): return self.rng.standard_normal(int(d * SR))
    @staticmethod
    def note(m): return 440 * 2 ** ((m - 69) / 12)

    # ---- sound effects (all go to the sfx bus)
    def whoosh(self, t, g=0.15, d=0.32):
        n = int(d * SR); w = self.bp(self.noise(d), 700, 6000)
        e = np.linspace(0, 1, n) ** 2.5; e[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
        self.add(self.sfx_buf, w * e, t - d + 0.04, g)
    def pop(self, t, g=0.25):
        n = int(0.08 * SR); tt = np.arange(n) / SR
        self.add(self.sfx_buf, np.sin(2 * np.pi * np.cumsum(900 - 6000 * tt) / SR) * np.exp(-tt * 40), t, g)
    def ding(self, t, g=0.1, f=1046.5, d=1.0):
        n = int(d * SR); tt = np.arange(n) / SR
        self.add(self.sfx_buf, (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.5 * tt)) * np.exp(-tt * 4), t, g)
    def thump(self, t, g=0.4, f=80):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        self.add(self.sfx_buf, np.sin(2 * np.pi * f * tt) * np.exp(-tt * 18), t, g)
    def zap_down(self, t, g=0.22, d=1.0):
        n = int(d * SR); tt = np.arange(n) / SR
        self.add(self.sfx_buf, np.sin(2 * np.pi * np.cumsum(1400 * np.exp(-tt * 3.5) + 120) / SR) * np.exp(-tt * 2.5), t, g)
    def boing(self, t, g=0.2, f=300, d=0.5):
        n = int(d * SR); tt = np.arange(n) / SR
        self.add(self.sfx_buf, np.sin(2 * np.pi * np.cumsum(f + f / 2 * np.sin(2 * np.pi * 9 * tt)) / SR) * np.exp(-tt * 5), t, g)
    def scratch(self, t, g=0.3, d=0.3):
        n = int(d * SR); tt = np.arange(n) / SR
        self.add(self.sfx_buf, self.bp(self.noise(d), 300, 3000) * np.sin(np.pi * tt / d) * (0.5 + 0.5 * np.sin(2 * np.pi * 16 * tt)), t, g)
    def growl(self, t, g=0.5, d=1.6):
        n = int(d * SR); tt = np.arange(n) / SR
        x = self.lp(self.noise(d), 300) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt)) * np.minimum(1, tt / 0.3) * np.exp(-tt * 1.2)
        self.add(self.sfx_buf, x, t, g)
    def wind_rain(self, t, d, g=0.3):
        n = int(d * SR); tt = np.arange(n) / SR
        x = self.bp(self.noise(d), 250, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.35 * tt)) + self.hp(self.noise(d), 3500) * 0.35
        self.add(self.sfx_buf, x * np.minimum(1, tt / 0.6), t, g)
    def horn(self, t, g=0.05):
        for t0, f1, f2, d in [(0, 415, 520, .16), (.22, 440, 554, .12), (.45, 392, 494, .25)]:
            n = int(d * SR); tt = np.arange(n) / SR
            h = np.sign(np.sin(2 * np.pi * f1 * tt)) + np.sign(np.sin(2 * np.pi * f2 * tt))
            self.add(self.sfx_buf, self.lp(h, 2500) * self.env(n, 0.01, d * 3), t + t0, g)

    # ---- music
    def _pluck(self, m, d=0.45, bright=0.5):
        if m in self._plucks: return self._plucks[m]
        f = self.note(m); n = int(d * SR); L = max(2, int(SR / f))
        buf = self.rng.uniform(-1, 1, L); out = np.zeros(n)
        for k in range(n):
            out[k] = buf[k % L]
            buf[k % L] = bright * 0.5 * (buf[k % L] + buf[(k + 1) % L]) + (1 - bright) * buf[k % L] * 0.996
        out *= np.exp(-np.arange(n) / (d * SR * 0.5)); self._plucks[m] = out; return out

    def drone(self, t0, t1, freqs=(55, 82.4, 110.0), g=0.5, cutoff=600):
        n = self.at(t1 - t0); tt = np.arange(n) / SR
        x = sum(np.sin(2 * np.pi * f * tt + 0.3 * np.sin(2 * np.pi * 0.2 * tt)) for f in freqs) / len(freqs)
        self.add(self.music, self.lp(x * np.minimum(1, tt / 1.0), cutoff), t0, g)

    def beat(self, t0, t1, bpm=112, prog=((60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)), g=1.0):
        beat = 60 / bpm
        tk = np.arange(int(0.25 * SR)) / SR
        kick = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-tk * 35)) / SR) * np.exp(-tk * 12)
        clap = self.bp(self.noise(0.12), 900, 4000) * self.env(int(0.12 * SR), 0.002, 0.04)
        hat = self.hp(self.noise(0.04), 8000) * self.env(int(0.04 * SR), 0.001, 0.01)
        pat = [0, 2, 1, 2, 0, 2, 1, 2]
        t = t0; b = 0
        while t < t1:
            ch = prog[(b // 4) % len(prog)]
            if b % 4 in (0, 2): self.add(self.music, kick, t, 0.7 * g)
            if b % 2 == 1: self.add(self.music, clap, t, 0.35 * g)
            self.add(self.music, hat, t + beat / 2, 0.15 * g)
            for h in range(2):
                self.add(self.music, self._pluck(ch[pat[(b * 2 + h) % 8]] + 12), t + h * beat / 2, 0.22 * g)
            if b % 2 == 0:
                n2 = int(beat * 1.8 * SR); tt = np.arange(n2) / SR
                self.add(self.music, np.sin(2 * np.pi * self.note(ch[0] - 24) * tt) * self.env(n2, 0.005, 0.35), t, 0.35 * g)
            t += beat; b += 1

    def drums(self, t0, t1, step, level=1.0, root=45):
        """light drum loop on an 8th-note grid of `step` seconds: soft kick on every beat, clap on 2 and 4,
        closed hat on the off-beats, a short sub note on beat 1 of each bar"""
        tk = np.arange(int(0.3 * SR)) / SR
        kick = np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 9)
        clap = self.bp(self.noise(0.14), 900, 5000) * self.env(int(0.14 * SR), 0.002, 0.045)
        hat = self.hp(self.noise(0.05), 7000) * self.env(int(0.05 * SR), 0.001, 0.012)
        n = 0; t = t0
        while t < t1:
            beat, on = divmod(n, 2)
            if on == 0:
                self.add(self.music, kick, t, 0.95 * level)
                if beat % 2 == 1: self.add(self.music, clap, t, 0.28 * level)
                if beat % 4 == 0:
                    n2 = int(step * 3.5 * SR); tt = np.arange(n2) / SR
                    f = self.note(root + (0, 0, -2, -4)[(beat // 4) % 4])
                    self.add(self.music, np.sin(2 * np.pi * f * tt) * self.env(n2, 0.005, 0.5), t, 0.3 * level)
            else:
                self.add(self.music, hat, t, 0.22 * level)
            n += 1; t = t0 + n * step

    def music_level(self, t0, t1, level):
        self.mgain[self.at(t0):self.at(t1)] = level

    # ---- mixdown
    def mixdown(self, out_wav):
        g = np.convolve(self.mgain, np.ones(2000) / 2000, mode="same")
        end = self.at(self.tl["total"] - 1.0)
        g[end:] *= np.linspace(1, 0, len(g) - end) ** 1.5
        k = int(0.12 * SR)
        duck = np.convolve(self.vmask, np.ones(k) / k, mode="same")
        hi, depth = getattr(self, "music_mix", (0.32, 0.17))
        mix = self.voice + self.music * g * (hi - depth * duck) + self.sfx_buf
        mix = np.tanh(mix * 1.1) / np.tanh(1.1)
        mix /= np.max(np.abs(mix)) / 0.95
        sf.write(out_wav, np.stack([mix, mix], 1).astype(np.float32), SR)


def build(tl, voice_dir, scenes_mod, out_wav):
    A = Mixer(tl, voice_dir)
    cfg = getattr(scenes_mod, "MUSIC", {})
    if tl.get("grid"):
        # voice is snapped to an 8th-note grid (timing "grid"): a light kick/drum loop on the same grid from frame 0
        A.drums(tl["grid0"], tl["total"] - 0.6, tl["grid"], level=cfg.get("drums", 1.0))
        A.music_mix = (0.34, 0.12)    # duck less, so the kick stays audible under the voice
    else:
        beat_from = A.S(cfg.get("beat_from_scene", 1))
        A.drone(0, beat_from + 0.3)
        A.beat(beat_from, tl["total"] - 0.8, bpm=cfg.get("bpm", 112))
    if cfg.get("whoosh_on_cuts", True):
        for s in tl["scenes"][1:]:
            A.whoosh(s["t0"])
    if hasattr(scenes_mod, "sfx"):
        scenes_mod.sfx(A)
    A.mixdown(out_wav)

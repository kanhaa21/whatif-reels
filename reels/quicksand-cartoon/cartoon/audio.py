"""Music and SFX stems for the quicksand short (44.1 kHz mono). The voice is not touched.
Music: soft kick/clap/hat loop + plucked synth bass and a light arp at 120.5 bpm, phase 0.09 s, so the
phrase starts fall on the 8th-note grid. Stops on "But here's the secret", drone during the explanation,
comes back lighter on "So stop pulling", stops for the last line, sting on the shoe landing."""
import json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR = 44100
J = json.load(open('work/phrases.json'))
DUR = J['duration'] + 0.4
N = int(DUR * SR)
rng = np.random.default_rng(7)
music = np.zeros(N); sfx = np.zeros(N)
BPM, PH = 120.5, 0.09
Q = 60 / BPM; E = Q / 2


def at(t): return int(t * SR)
def add(buf, x, t, g=1.0):
    i = max(0, at(t)); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i] * g
def noise(d): return rng.standard_normal(int(d * SR))
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'highpass', fs=SR, output='sos'), x)
def env(n, a, d): e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); return e * np.exp(-np.arange(n) / (d * SR))
def note(m): return 440 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR

kick = (lambda t: np.sin(2 * np.pi * np.cumsum(48 + 120 * np.exp(-t * 28)) / SR) * np.exp(-t * 9))(tt(0.35))
clap = bp(noise(0.15), 900, 5000) * env(int(0.15 * SR), 0.002, 0.05)
hat = hp(noise(0.05), 7500) * env(int(0.05 * SR), 0.001, 0.012)
def pluck(m, d=0.3, bright=0.6):
    t = tt(d); f = note(m)
    x = (np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * t)) * np.exp(-t * 9)
    return lp(x, 1200 + 3000 * bright)
def pad(m, d):
    t = tt(d); x = sum(np.sin(2 * np.pi * note(m + k) * t * (1 + 0.002 * j)) for j, k in enumerate((0, 7, 12)))
    return lp(x / 3, 1500) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)

# chord roots (A minor-ish, playful): Am F C G
PROG = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
def groove(t0, t1, level=1.0, arp=True):
    n = int(round((t0 - PH) / E)); t = PH + n * E
    while t < t1:
        beat, half = divmod(n, 2); bar = beat // 4; ch = PROG[bar % 4]
        if t >= t0:
            if half == 0:
                add(music, kick, t, 0.9 * level)
                if beat % 2 == 1: add(music, clap, t, 0.3 * level)
                if beat % 4 == 0: add(music, pluck(ch[0] - 24, Q * 1.8, 0.2), t, 0.55 * level)
                if beat % 4 == 2: add(music, pluck(ch[0] - 24, Q * 0.9, 0.2), t, 0.45 * level)
            add(music, hat, t + 0.0, (0.18 if half else 0.08) * level)
            if arp:
                m = ch[(n * 3) % 3] + 12 + (12 if n % 8 == 7 else 0)
                add(music, pluck(m, 0.22, 0.7), t, 0.12 * level)
        n += 1; t = PH + n * E

S = {p['text']: p['s'] for p in J['phrases']}
t_secret = S["But here's the secret:"]; t_stop = S["So stop pulling."]; t_panic = S["Panic can."]
groove(0.0, t_secret - 0.05, 1.0)
add(music, pad(57, t_secret), 0.0, 0.25)
# explanation: low drone + gentle bell pad
add(music, pad(45, t_stop - t_secret + 0.4), t_secret, 0.45)
groove(t_stop, t_panic - 0.05, 0.75, arp=True)
add(music, pad(60, t_panic - t_stop), t_stop, 0.18)

# ---------- SFX (times in seconds = frames / 30) ----------
F = lambda f: f / 30
def thunk(t, g=0.6, f=70): x = tt(0.3); add(sfx, np.sin(2 * np.pi * f * x) * np.exp(-x * 14), t, g)
def whoosh(t, g=0.25, d=0.4):
    n = int(d * SR); w = bp(noise(d), 600, 5000) * np.linspace(0, 1, n) ** 2.2; w[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR)); add(sfx, w, t - d + 0.05, g)
def ting(t, g=0.18, f=1568): x = tt(1.0); add(sfx, (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(2 * np.pi * f * 2.01 * x)) * np.exp(-x * 4), t, g)
def boing(t, g=0.25, f=220, d=0.5): x = tt(d); add(sfx, np.sin(2 * np.pi * np.cumsum(f + f * 0.6 * np.sin(2 * np.pi * 10 * x)) / SR) * np.exp(-x * 5), t, g)
def squelch(t, g=0.35, d=0.25):
    x = tt(d); w = lp(noise(d), 900) * np.sin(np.pi * x / d) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * x)); add(sfx, w, t, g)
def glorp(t, g=0.25): x = tt(0.18); add(sfx, np.sin(2 * np.pi * np.cumsum(180 + 500 * x / 0.18) / SR) * np.sin(np.pi * x / 0.18), t, g)
def rumble(t, d, g=0.2): x = tt(d); add(sfx, lp(noise(d), 160) * np.minimum(1, x / 0.3) * np.minimum(1, (d - x) / 0.3), t, g)
def ambience(t0, t1, g=0.05):
    d = t1 - t0; x = tt(d); w = bp(noise(d), 300, 1400) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * x)) + hp(noise(d), 4000) * 0.3
    add(sfx, w * np.minimum(1, x / 0.5) * np.minimum(1, (d - x) / 0.5), t0, g)

ambience(0, F(503), 0.05); ambience(F(778), F(824), 0.04); ambience(F(874), DUR - 0.5, 0.05)
squelch(F(8), 0.35); squelch(F(30), 0.3)
squelch(F(58), 0.5, 0.4); thunk(F(60), 0.6, 60)
for k in range(5): add(sfx, bp(noise(0.06), 2000, 6000) * env(int(0.06 * SR), 0.002, 0.02), F(132 + k * 3), 0.15)  # wing flaps
for k in range(9): glorp(F(168 + k * 6 + (k % 3)), 0.22)
whoosh(F(232), 0.2, 0.3); squelch(F(240), 0.3); squelch(F(262), 0.3)
for f in (285, 298, 311): boing(F(f), 0.22, 180, 0.35)
whoosh(F(345), 0.3, 0.8)
ting(F(362), 0.15, 1318); thunk(F(368), 0.5, 55); boing(F(406), 0.18, 140, 0.4)
for f in (442, 474, 500): squelch(F(f), 0.45, 0.3); thunk(F(f) + 0.05, 0.35, 75)
# movie: projector rattle + organ sting
x = tt(F(565) - F(503)); add(sfx, hp(noise(len(x) / SR), 1500) * (0.5 + 0.5 * (np.sin(2 * np.pi * 24 * x) > 0)) * 0.5, F(503), 0.08)
add(sfx, sum(np.sin(2 * np.pi * note(m) * tt(1.4)) for m in (50, 53, 56, 62)) / 4 * env(int(1.4 * SR), 0.01, 0.6), F(505), 0.3)
thunk(t_secret, 0.7, 45); rumble(t_secret, 1.2, 0.25)
ting(F(648), 0.2, 1760); thunk(F(652), 0.45, 90)
glorp(F(760), 0.3); ting(F(766), 0.12, 2093)
for f in (503, 612, 705, 778, 824, 874): whoosh(F(f), 0.18, 0.3)
for k in range(5): squelch(F(830 + k * 9), 0.22, 0.3)
whoosh(F(905), 0.25, 0.9); add(sfx, np.sin(2 * np.pi * np.cumsum(400 + 900 * tt(0.12) / 0.12) / SR) * np.exp(-tt(0.12) * 20), F(926), 0.3)
x = tt(1.2); add(sfx, lp(noise(1.2), 220) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * x)) * np.sin(np.pi * x / 1.2), F(955), 0.35)  # grumble
x = tt(0.45); add(sfx, lp(noise(0.45), 300) * np.sin(np.pi * x / 0.45) * (0.6 + 0.4 * np.sin(2 * np.pi * 40 * x)), F(1042), 0.55)  # burp
whoosh(F(1062), 0.2, 0.5); boing(F(1066), 0.3, 300, 0.6); thunk(F(1066), 0.3, 120)
for k, m in enumerate((72, 76, 79, 84)): ting(F(1068) + k * 0.07, 0.08, note(m))

sf.write('work/music.wav', music, SR); sf.write('work/sfx.wav', sfx, SR)
print('stems written', DUR)

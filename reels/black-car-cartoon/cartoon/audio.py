"""Music and SFX stems for the quicksand short (44.1 kHz mono). The voice is not touched.
Music: soft kick/clap/hat loop + plucked synth bass and a light arp at 120.5 bpm, phase 0.09 s, so the
phrase starts fall on the 8th-note grid. Stops on "But here's the secret", drone during the explanation,
comes back lighter on "So stop pulling", stops for the last line, sting on the shoe landing."""
import json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

SR = 44100
TL = json.load(open('work/timeline.json'))
DUR = TL['total'] + 0.3
N = int(DUR * SR)
rng = np.random.default_rng(7)
music = np.zeros(N); sfx = np.zeros(N)
BPM, PH = 100.0, 0.15   # grid 0.3 s = 8th note at 100 bpm, starting at the voice lead
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

# hip-hop-ish groove under the whole reel; drops out for the punchline, back for the CTA
PROG = [(57, 60, 64), (53, 57, 60), (50, 53, 57), (52, 56, 59)]
LS = [l['start'] for l in TL['lines']]
t_punch = TL['lines'][5]['start']
groove(0.0, t_punch - 0.05, 1.0)
add(music, pad(57, t_punch), 0.0, 0.2)
add(music, pad(45, 1.6), t_punch, 0.4)
groove(t_punch + 1.8, DUR - 0.6, 0.9)

# ---------- SFX (frames / 30) ----------
F = lambda f: f / 30
def thunk(t, g=0.6, f=70): x = tt(0.3); add(sfx, np.sin(2 * np.pi * f * x) * np.exp(-x * 14), t, g)
def whoosh(t, g=0.25, d=0.4):
    n = int(d * SR); w = bp(noise(d), 600, 5000) * np.linspace(0, 1, n) ** 2.2; w[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR)); add(sfx, w, t - d + 0.05, g)
def ting(t, g=0.18, f=1568): x = tt(1.0); add(sfx, (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(2 * np.pi * f * 2.01 * x)) * np.exp(-x * 4), t, g)
def boing(t, g=0.25, f=220, d=0.5): x = tt(d); add(sfx, np.sin(2 * np.pi * np.cumsum(f + f * 0.6 * np.sin(2 * np.pi * 10 * x)) / SR) * np.exp(-x * 5), t, g)
def sizzle(t, d, g=0.12): x = tt(d); add(sfx, hp(noise(d), 3500) * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * x)) * np.minimum(1, x / 0.2) * np.minimum(1, (d - x) / 0.2), t, g)
def squeak(t, g=0.15): x = tt(0.18); add(sfx, np.sin(2 * np.pi * np.cumsum(1800 + 900 * np.sin(2 * np.pi * 6 * x)) / SR) * np.sin(np.pi * x / 0.18), t, g)
def screech(t, d=0.7, g=0.18):
    x = tt(d); f = 2400 + 300 * np.sin(2 * np.pi * 23 * x); add(sfx, (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * bp(noise(d), 2000, 6000)) * np.minimum(1, x / 0.03) * np.exp(-x * 2.5), t, g)
def horn(t, g=0.12):
    for t0, f1, f2, d in [(0, 415, 520, .18), (.24, 415, 520, .32)]:
        x = tt(d); h = np.sign(np.sin(2 * np.pi * f1 * x)) + np.sign(np.sin(2 * np.pi * f2 * x)); add(sfx, lp(h, 2500) * env(len(x), 0.01, d * 3), t + t0, g)
def slap(t, g=0.4): x = tt(0.15); add(sfx, bp(noise(0.15), 400, 3000) * np.exp(-x * 40), t, g)
for k in range(5): ting(F(6 + k * 18), 0.08, note(84 + (k % 3) * 3))           # sparkles
thunk(F(58), 0.5, 60); whoosh(F(60), 0.25, 0.35)
for k in range(4): ting(F(105 + k * 10), 0.07, note(88 + k))
add(sfx, -bp(noise(0.35), 300, 1500) * np.exp(-tt(0.35) * 10), F(150), 0.2)   # sparkle fizzles out
for f in (193, 418, 625): whoosh(F(f), 0.25, 0.35); thunk(F(f) + 0.05, 0.4, 90)
sizzle(F(238), (346 - 238) / 30, 0.08)
for k in range(10): ting(F(250 + k * 5), 0.03, 900 + 120 * k)                 # thermometer rising
ting(F(295), 0.18, 1760)
sizzle(F(346), (418 - 346) / 30, 0.14); slap(F(373), 0.45); boing(F(380), 0.15, 300)
for k in range(5): squeak(F(450 + k * 15), 0.12)
ting(F(562), 0.18, 2093); ting(F(570), 0.1, 2637)
whoosh(F(650), 0.2, 0.4)
add(sfx, lp(noise((785 - 660) / 30), 200) * 0.6, F(660), 0.18)                # traffic hum
screech(F(784), 0.8, 0.2); horn(F(788), 0.1)
ting(F(750), 0.15, 1318)
ting(F(840), 0.1, 2093)
sizzle(F(895), 1.2, 0.2); boing(F(897), 0.25, 260, 0.6); thunk(F(895), 0.5, 55)
whoosh(F(940), 0.2, 0.4)
for k, m in enumerate((79, 84, 88)): ting(F(1000) + k * 0.1, 0.07, note(m))

sf.write('work/music.wav', music, SR); sf.write('work/sfx.wav', sfx, SR)
print('stems written', DUR)

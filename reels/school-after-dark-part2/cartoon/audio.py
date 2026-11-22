"""Music and SFX stems for "I Stayed in School After Dark" Part 2 (44.1 kHz mono), same palette as Part 1
(room tone, door creak, handle, latch, heartbeat, floorboard groan, fluorescent buzz + relay clunks, wooden knocks,
riser + low impact), plus new beats for this part: frosty barefoot steps, a running sprint, stingers when the thing
appears and when its head snaps, a locker clang, phone buzzes, locker rattles and a final three knocks on the locker
(the Part 1 knock, now on metal). Times come from work/phrases.json, the same anchors the picture uses.
Writes work/music.wav and work/sfx.wav; SFX in peak units (1.0 = the loudest hit), mix.py sets levels."""
import json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

PH = json.load(open('work/phrases.json'))
from types import SimpleNamespace as NS
P = lambda i: NS(**PH['phrases'][i]); C = lambda i, j: NS(**PH['phrases'][i]['chunks'][j])
SR = 44100; DUR = PH['duration']; N = int(DUR * SR)
rng = np.random.default_rng(23)
music = np.zeros(N); sfx = np.zeros(N)

def at(t): return int(round(t * SR))
def add(buf, x, t, g=1.0):
    i = max(0, at(t)); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i] * g
def noise(d): return rng.standard_normal(int(d * SR))
def tt(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def note(m): return 440 * 2 ** ((m - 69) / 12)
IR2 = lp(noise(1.6), 6000) * np.exp(-tt(1.6) * 3.6); IR2[0] = 0; IR2 /= np.sqrt(np.sum(IR2 ** 2))
def hall(x, wet=0.5): y = fftconvolve(x, IR2); z = np.zeros(len(y)); z[:len(x)] = x; return z + wet * y
def imp(d, n=0.003): return np.r_[noise(n), np.zeros(int(d * SR) - int(n * SR))]
def modes(ex, fr):
    x = tt(len(ex) / SR); out = np.zeros(len(ex))
    for f, a, d in fr: out += a * fftconvolve(ex, np.sin(2 * np.pi * f * x) * np.exp(-x * d))[:len(ex)]
    return out
def hit(x, t, pk): add(sfx, x / (np.abs(x).max() + 1e-12) * pk, t)

# ---------------- music: low drone bed with a slow pulse, dropping out before each scare ----------------
def pad(m, d, cut=600):
    t = tt(d); x = sum(np.sin(2 * np.pi * note(m + k) * t * (1 + 0.003 * j)) for j, k in enumerate((0, 1, 7, 12)))  # minor second rub
    return lp(x / 4, cut) * np.minimum(1, t / 2.0) * np.minimum(1, (d - t) / 1.5)
add(music, pad(33, DUR, 380), 0.0, 1.0)
add(music, pad(45, DUR - 24, 900), 23.0, 0.35)                       # a higher layer joins for the hallway chase
def beat(g):
    x = tt(0.25); return np.sin(2 * np.pi * np.cumsum(55 + 25 * np.exp(-x * 30)) / SR) * np.exp(-x * 14) * g
t = P(4).e + 0.3
while t < P(6).s:                                                     # heartbeat after the guard's voice
    add(music, beat(1.4), t); add(music, beat(0.8), t + 0.24); t += 0.78
t = P(9).s + 0.3
while t < P(12).s:                                                    # faster heartbeat inside the locker
    add(music, beat(1.2), t); add(music, beat(0.7), t + 0.2); t += 0.62
# drop-outs: the bed dips to near nothing right before each scare and comes back after
env = np.ones(N)
for a, b in ((C(3, 0).s - 0.1, P(4).s - 0.1), (C(7, 1).s - 0.4, C(7, 1).s + 0.15), (C(11, 1).s - 0.5, C(11, 1).s), (P(12).e, DUR)):
    i, j = at(a), at(b); r = at(0.15); env[i:j] = 0.12; env[max(0, i - r):i] = np.linspace(1, 0.12, i - max(0, i - r))
music *= env
music[at(DUR - 0.6):] *= np.linspace(1, 0, N - at(DUR - 0.6))

# ---------------- SFX ----------------
# room tone
x = tt(DUR); tone = lp(noise(DUR), 400) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * x)) + 0.2 * hp(noise(DUR), 4000)
hit(tone * np.minimum(1, x / 0.6), 0.0, 0.03)
# the lever turns from the other side, the latch gives
def creak(d, f0a, f0b, rate, lo=250, hi=3000):
    x = tt(d); u = x / d; f0 = f0a + (f0b - f0a) * u + 25 * np.sin(2 * np.pi * 2.1 * x)
    sq = sum(np.sin(2 * np.pi * h * np.cumsum(f0) / SR) / h for h in (1, 2, 3, 5))
    slip = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(rate + 10 * np.sin(np.pi * u)) / SR))
    return bp(sq * slip, lo, hi) * np.sin(np.pi * u) ** 0.5
hit(hall(creak(1.1, 820, 1240, 28, 600, 4000), 0.4), 0.25, 0.22)
latch = modes(imp(0.3), ((160, 1, 40), (2100, 0.6, 60), (3300, 0.4, 80)))
hit(hall(latch, 0.4), 1.4, 0.45)
# the door swings open, slow and long
hit(hall(creak(2.3, 300, 480, 14), 0.55), C(0, 2).s - 0.2, 0.45)
# "Nobody was there": cold air from the corridor
d = 2.2; x = tt(d); hit(bp(noise(d), 300, 1800) * np.sin(np.pi * x / d) ** 2, P(1).s - 0.3, 0.07)
# frosty barefoot steps on each print (soft heel thud + a faint crackle of frost), same times as the picture
t0, t1 = P(2).s + 0.45, C(2, 2).e - 0.05
steps = [t0 + (t1 - t0) * k / 7 for k in range(8)] + [C(3, 0).s + 0.05, C(3, 0).s + 0.27]
def bare(force=1.0):
    d = 0.35; x = tt(d)
    thud = modes(imp(d, 0.006), ((70, 1, 30), (140, 0.6, 45), (300, 0.3, 70))) * force
    frost = bp(noise(d), 3000, 9000) * np.exp(-x * 40) * (np.abs(np.sin(2 * np.pi * 37 * x)) > 0.7) * 0.25 * np.abs(thud).max()
    return hall(thud + frost, 0.5)
for k, ts in enumerate(steps): hit(bare(1.0 + 0.4 * (k >= 8)), ts, 0.30 + 0.25 * k / 9)
# they stop: a floorboard groans under weight that isn't there
dd = 0.9; x = tt(dd); u = x / dd
groan = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(90 + 30 * u + 8 * np.sin(2 * np.pi * 3 * x)) / SR)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(26 + 18 * u) / SR)))
hit(hall(bp(groan, 120, 1800) * np.sin(np.pi * u) ** 0.8, 0.6), C(3, 1).s + 0.2, 0.25)
# the voice: a sub swell under it
d = P(4).e - P(4).s + 1.2; x = tt(d)
hit(np.sin(2 * np.pi * 36 * x) * np.sin(np.pi * x / d) ** 2 + 0.3 * lp(noise(d), 120) * np.sin(np.pi * x / d), P(4).s - 0.4, 0.12)
# "...gone home": empty corridor whoosh
x = tt(1.2); hit(bp(noise(1.2), 400, 3000) * (x / 1.2) ** 2 * np.minimum(1, (1.2 - x) / 0.05), C(5, 1).s - 1.1, 0.18)
# I ran: sprinting shoes and a whoosh past camera
def step():
    d = 0.18; x = tt(d)
    heel = bp(noise(d), 1800, 6500) * np.exp(-x * 160) + 0.9 * modes(imp(d), ((110, 1, 45), (420, 0.5, 80)))
    return hall(heel, 0.55)
for k in range(9): hit(step(), P(6).s - 0.25 + k * 0.17, 0.25 + 0.3 * k / 8)
x = tt(0.6); hit(bp(noise(0.6), 500, 5000) * np.sin(np.pi * x / 0.6) ** 3, P(6).e - 0.1, 0.3)
# fluorescent buzz in the hallway (flickers), relay clunks when the lights die
d = P(9).s - P(7).s + 0.5; x = tt(d)
hum = sum(np.sin(2 * np.pi * 100 * h * x) / h ** 0.6 for h in (1, 2, 3, 4, 5, 7, 9))
flick = (np.sin(2 * np.pi * np.cumsum(9 + 6 * np.sin(2 * np.pi * 0.7 * x)) / SR) > -0.6).astype(float)
hit(bp(np.tanh(2.5 * hum), 180, 4000) * (0.4 + 0.6 * flick) * np.minimum(1, x / 0.3) * np.minimum(1, (d - x) / 0.3), P(7).s - 0.1, 0.05)
def clunk(g=1.0):
    c = modes(imp(0.25, 0.004), ((140, 1, 40), (620, 0.6, 70), (1900, 0.4, 120)))
    return hall(c + bp(noise(0.25), 2000, 7000) * np.exp(-tt(0.25) * 220) * 0.5 * np.abs(c).max(), 0.6)
tl0 = P(8).s - 0.1
for k in range(12):
    tk = tl0 + 0.45 + (11 - k) * ((C(8, 1).e - tl0 - 0.6) / 11)
    hit(clunk(), tk, 0.18 + 0.30 * (11 - k) / 11)
# stingers
def sting(d=1.6, base=63):
    x = tt(d); s = np.zeros(len(x))
    for m in (base, base + 1, base + 6, base + 13):                      # dissonant string cluster
        f = note(m) * (1 + 0.004 * np.sin(2 * np.pi * 6 * x))
        saw = 2 * ((np.cumsum(f) / SR) % 1) - 1; s += saw
    s = bp(s, 400, 6000) * np.exp(-x * 2.2) * np.minimum(1, x / 0.01)
    boom = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-x * 6)) / SR) * np.exp(-x * 4.0))
    return hall(s + 1.2 * boom, 0.4)
hit(sting(1.8, 63), C(7, 1).s + 0.15, 0.85)        # it appears under the exit sign
x = tt(0.25); snap = bp(noise(0.25), 1500, 7000) * np.exp(-x * 60) + modes(imp(0.25), ((230, 1, 50), (900, 0.6, 80)))
hit(hall(snap, 0.3), P(7).e + 0.2, 0.55)            # the head snaps sideways
hit(sting(1.4, 66), P(7).e + 0.22, 0.55)
# the last light dies: riser into the big low impact
x = tt(1.4); hit(bp(noise(1.4), 300, 3000) * (x / 1.4) ** 3, C(8, 1).s - 0.8, 0.25)
x = tt(1.6); boom = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(36 + 70 * np.exp(-x * 6)) / SR) * np.exp(-x * 3.5))
boom = boom + 0.6 * lp(noise(1.6), 400) * np.exp(-x * 7.0)
hit(hall(boom, 0.25), C(8, 1).e + 0.05, 1.0)
# the locker door pulled shut from inside: metal clang + latch
def metal(force=1.0, d=1.0):
    ex = imp(d, 0.003)
    m = modes(ex, ((180, 1, 6), (431, 0.8, 8), (697, 0.7, 10), (1183, 0.5, 14), (1720, 0.4, 18), (2650, 0.3 * force, 25)))
    return hall(m + bp(noise(d), 2000, 8000) * np.exp(-tt(d) * 120) * 0.4 * np.abs(m).max(), 0.35)
Ph9 = P(9).s - 0.05
hit(metal(1.0), Ph9, 0.45)
hit(latch, Ph9 + 0.25, 0.3)
# phone buzzes (twice, a second message later)
def buzz(d=0.38):
    x = tt(d); return (np.sin(2 * np.pi * 165 * x) + 0.6 * np.sign(np.sin(2 * np.pi * 165 * x))) * (np.sin(2 * np.pi * 22 * x) > 0) * np.minimum(1, x / 0.01) * np.minimum(1, (d - x) / 0.02)
for k in range(2): hit(lp(buzz(), 2500), C(9, 1).s - 0.1 + k * 0.5, 0.22)
for k in range(2): hit(lp(buzz(), 2500), C(11, 1).s - 0.05 + k * 0.5, 0.28)
# slow steps outside the locker before Mom's voice, then a low swell as the face comes to the slits
for k in range(4): hit(bare(0.9), P(10).s - 1.5 + k * 0.42, 0.2 + 0.1 * k)
d = 1.6; x = tt(d); hit(np.sin(2 * np.pi * 41 * x) * np.sin(np.pi * x / d) ** 2 + 0.2 * bp(noise(d), 200, 1200) * np.sin(np.pi * x / d), C(10, 1).s - 0.5, 0.15)
hit(sting(1.5, 61), C(11, 1).s, 0.4)               # "...still at the gate"
# the locker is shaken from outside while the slits go dark, then the cut to black
for k, ts in enumerate(np.arange(P(12).s + 0.2, P(12).e, 0.2)): hit(metal(0.6, 0.4), ts + 0.03 * rng.standard_normal(), 0.07 + 0.012 * k)
hit(hall(boom, 0.25), P(12).e + 0.05, 0.85)
# three knocks on the locker under the Part 3 card: the Part 1 knock, now on metal
for k, g in enumerate((0.45, 0.55, 0.7)): hit(metal(1.2, 0.8), P(12).e + 0.75 + k * 0.44, g)

i = at(DUR - 0.5); j = at(DUR - 0.9); sfx[j:i] *= np.linspace(1, 0, i - j); sfx[i:] = 0; music[i:] = 0
sf.write('work/music.wav', music.astype(np.float32), SR); sf.write('work/sfx.wav', sfx.astype(np.float32), SR)
print('stems written', DUR)

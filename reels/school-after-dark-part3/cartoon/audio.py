"""Music and SFX stems for "I Stayed in School After Dark" Part 3 (v2, after the owner's notes; 44.1 kHz mono).
Same palette as Parts 1-2 (room tone, drone bed + heartbeat, creaks, latch, frost steps, metal locker knocks, stings,
low booms, phone buzzes, Part 1's wooden knock), plus: the alarm (an old electric school bell with a buzzer under it,
red light in the picture), the clock into a midnight chime, the loudspeaker (click, feedback, static), room 109's door
creaking open on its own, chalk ticks on the attendance board, the class's heads creaking round on "Jimmy", a roar on
the third "Jimmy!", Mom's text buzz, and an unknown caller's ringtone that keeps ringing into the end card.
Times come from work/phrases.json, the same anchors the picture uses.
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


# ---------------- shared sound makers (same as Part 2) ----------------
def pad(m, d, cut=600):
    t = tt(d); x = sum(np.sin(2 * np.pi * note(m + k) * t * (1 + 0.003 * j)) for j, k in enumerate((0, 1, 7, 12)))
    return lp(x / 4, cut) * np.minimum(1, t / 2.0) * np.minimum(1, (d - t) / 1.5)
def beat(g):
    x = tt(0.25); return np.sin(2 * np.pi * np.cumsum(55 + 25 * np.exp(-x * 30)) / SR) * np.exp(-x * 14) * g
def creak(d, f0a, f0b, rate, lo=250, hi=3000):
    x = tt(d); u = x / d; f0 = f0a + (f0b - f0a) * u + 25 * np.sin(2 * np.pi * 2.1 * x)
    sq = sum(np.sin(2 * np.pi * h * np.cumsum(f0) / SR) / h for h in (1, 2, 3, 5))
    slip = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(rate + 10 * np.sin(np.pi * u)) / SR))
    return bp(sq * slip, lo, hi) * np.sin(np.pi * u) ** 0.5
latch = modes(imp(0.3), ((160, 1, 40), (2100, 0.6, 60), (3300, 0.4, 80)))
def bare(force=1.0):
    d = 0.35; x = tt(d)
    thud = modes(imp(d, 0.006), ((70, 1, 30), (140, 0.6, 45), (300, 0.3, 70))) * force
    frost = bp(noise(d), 3000, 9000) * np.exp(-x * 40) * (np.abs(np.sin(2 * np.pi * 37 * x)) > 0.7) * 0.25 * np.abs(thud).max()
    return hall(thud + frost, 0.5)
def step():
    d = 0.18; x = tt(d)
    return hall(bp(noise(d), 1800, 6500) * np.exp(-x * 160) + 0.9 * modes(imp(d), ((110, 1, 45), (420, 0.5, 80))), 0.55)
def sting(d=1.6, base=63):
    x = tt(d); s = np.zeros(len(x))
    for m in (base, base + 1, base + 6, base + 13):
        f = note(m) * (1 + 0.004 * np.sin(2 * np.pi * 6 * x)); s += 2 * ((np.cumsum(f) / SR) % 1) - 1
    s = bp(s, 400, 6000) * np.exp(-x * 2.2) * np.minimum(1, x / 0.01)
    boom = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-x * 6)) / SR) * np.exp(-x * 4.0))
    return hall(s + 1.2 * boom, 0.4)
def metal(force=1.0, d=1.0):
    m = modes(imp(d, 0.003), ((180, 1, 6), (431, 0.8, 8), (697, 0.7, 10), (1183, 0.5, 14), (1720, 0.4, 18), (2650, 0.3 * force, 25)))
    return hall(m + bp(noise(d), 2000, 8000) * np.exp(-tt(d) * 120) * 0.4 * np.abs(m).max(), 0.35)
def knock(force):   # Part 1's wooden door knock
    d = 0.6; ex = np.r_[noise(0.0025) * np.hanning(int(0.0025 * SR)), np.zeros(int(d * SR) - int(0.0025 * SR))]
    m = modes(ex, ((92, 1.0, 18), (138, 0.9, 22), (205, 0.8, 26), (310, 0.6, 34), (455, 0.45, 45), (690, 0.35 * force, 60), (1040, 0.25 * force, 80), (1600, 0.18 * force, 110)))
    kn = bp(noise(d), 1200, 5000) * np.exp(-tt(d) * 260) * 0.35 * force * np.abs(m).max()
    return hall(np.tanh(1.5 * (m + kn) / np.abs(m + kn).max()), 0.75)
def buzz(d=0.38):
    x = tt(d); return lp((np.sin(2 * np.pi * 165 * x) + 0.6 * np.sign(np.sin(2 * np.pi * 165 * x))) * (np.sin(2 * np.pi * 22 * x) > 0) * np.minimum(1, x / 0.01) * np.minimum(1, (d - x) / 0.02), 2500)
def low_boom(d=1.6, decay=3.5):
    x = tt(d); b = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(36 + 70 * np.exp(-x * 6)) / SR) * np.exp(-x * decay))
    return hall(b + 0.6 * lp(noise(d), 400) * np.exp(-x * 7.0), 0.25)
def riser(d=1.2): x = tt(d); return bp(noise(d), 300, 3000) * (x / d) ** 3

# ---------------- music: same low drone bed and heartbeat, dropping out before each scare ----------------
ALARM0 = P(3).e + 0.4
add(music, pad(33, DUR, 380), 0.0, 1.0)
add(music, pad(45, DUR - ALARM0, 900), ALARM0, 0.35)
t = 0.0
while t < P(3).e:                                                     # fast heartbeat in the locker
    add(music, beat(1.2), t); add(music, beat(0.7), t + 0.2); t += 0.62
t = P(8).s
while t < P(13).s:                                                    # and through the attendance
    add(music, beat(1.3), t); add(music, beat(0.75), t + 0.2); t += 0.58
env = np.ones(N)
for a_, b_ in ((C(1, 0).s - 0.5, C(1, 0).s), (ALARM0 - 0.5, ALARM0), (C(6, 1).s - 0.4, C(6, 1).s), (C(12, 0).s - 0.6, C(12, 0).s),
               (C(14, 2).s - 0.4, C(14, 2).s), (P(15).e, DUR)):
    i, j = at(a_), at(b_); r = at(0.15); env[i:j] = 0.12; env[max(0, i - r):i] = np.linspace(1, 0.12, i - max(0, i - r))
music *= env
music[at(DUR - 0.6):] *= np.linspace(1, 0, N - at(DUR - 0.6))

# ---------------- SFX ----------------
x = tt(DUR); tone = lp(noise(DUR), 400) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * x)) + 0.2 * hp(noise(DUR), 4000)
hit(tone * np.minimum(1, x / 0.3), 0.0, 0.03)
# three knocks on the locker, harder each time
for k, (ts, g) in enumerate(((0.25, 0.55), (0.65, 0.7), (1.05, 0.9))): hit(metal(1.0 + 0.2 * k, 0.8), ts, g)
# breath against the vents between the two "Jimmy"s
d = 0.7; x = tt(d); hit(bp(noise(d), 500, 3000) * np.sin(np.pi * x / d) ** 1.2, C(1, 0).e + 0.15, 0.08)
# it walks away; the locker door opens
for k in range(6): hit(lp(bare(0.9), 3000 - 350 * k), P(3).s - 0.2 + k * 0.38, 0.28 * (1 - k / 6) ** 1.3)
hit(latch, C(3, 1).s - 0.25, 0.3)
hit(hall(creak(0.9, 900, 1400, 30, 600, 4500), 0.4), C(3, 1).s - 0.15, 0.25)
# THE ALARM: old electric school bell + a harsh buzzer under it; loud in the gap, rings on under the line
d = P(4).e - ALARM0 + 0.3; x = tt(d)
env_a = np.minimum(1, x / 0.01) * np.where(x < 1.6, 1.0, np.maximum(0.12, np.exp(-(x - 1.6) * 1.4)))
bell = modes(imp(d, 0.002), ((2093, 1, 0.5), (3250, 0.6, 0.7), (4700, 0.35, 1.0), (1046, 0.4, 0.4)))
bell = bell / (np.abs(bell).max() + 1e-9) * (0.5 + 0.5 * (np.sin(2 * np.pi * 24 * x) > 0))
buzz_a = bp(np.sign(np.sin(2 * np.pi * 120 * x)) + 0.5 * np.sign(np.sin(2 * np.pi * 180 * x)), 200, 3000)
alarm = (bell + 0.35 * buzz_a / (np.abs(buzz_a).max() + 1e-9)) * env_a
alarm[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))
hit(hall(alarm, 0.5), ALARM0, 0.8)
# "at midnight": ticks, then one deep chime
for k in range(3): hit(modes(imp(0.08, 0.001), ((3000, 1, 90), (5200, 0.5, 120))), C(4, 1).s - 0.2 + k * 0.33, 0.06)
d = 3.0; x = tt(d); chime = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * dc) for f, a, dc in ((98, 1, 1.0), (196.5, 0.5, 1.4), (293, 0.35, 2.0), (523, 0.15, 3.0)))
hit(hall(chime * np.minimum(1, x / 0.005), 0.5), C(4, 1).e + 0.05, 0.45)
# the loudspeaker: click on, feedback whine, static under the voice, click off
click = modes(imp(0.12, 0.002), ((200, 1, 60), (1800, 0.5, 90)))
hit(click, P(5).s - 0.55, 0.3)
d = 0.5; x = tt(d); hit(np.sin(2 * np.pi * (2400 + 300 * x / d) * x) * np.sin(np.pi * x / d) ** 2, P(5).s - 0.5, 0.08)
d = P(5).e - P(5).s + 0.8; x = tt(d); hit(bp(noise(d), 1500, 5000) * np.minimum(1, x / 0.1) * np.minimum(1, (d - x) / 0.1), P(5).s - 0.4, 0.035)
hit(click, P(5).e + 0.4, 0.3)
# room 109 opens by itself: one long slow creak, cold air, a sting on "Room 109"
hit(hall(creak(1.8, 260, 420, 13), 0.55), P(6).s + 0.3, 0.4)
d = 2.0; x = tt(d); hit(bp(noise(d), 300, 1800) * np.sin(np.pi * x / d) ** 2, P(6).s + 0.6, 0.06)
hit(sting(1.6, 62), C(6, 1).s, 0.4)
# attendance: chalk ticks on the board as each one answers
def chalk(d=0.35):
    x = tt(d); return bp(noise(d), 1500, 7000) * (0.4 + 0.6 * (np.sin(2 * np.pi * 45 * x) > 0)) * np.sin(np.pi * x / d) ** 0.5
hit(chalk(), P(9).e + 0.05, 0.12); hit(chalk(), P(11).e + 0.05, 0.12)
# "Jimmy." (1): every head creaks round + sting; (2) heavier sting + chalk circling the name; (3) roar, boom, screech
for k in range(8): hit(bp(creak(0.2, 600 + 50 * k, 500, 40 + 3 * k, 500, 4000), 500, 4000), C(12, 0).s + 0.1 + 0.02 * k, 0.06)
hit(sting(1.5, 63), C(12, 0).s, 0.25)
hit(chalk(0.6), C(12, 0).e + 0.05, 0.12)
hit(sting(1.5, 65), C(12, 1).s, 0.3); hit(chalk(0.6), C(12, 1).e + 0.05, 0.14)
hit(low_boom(1.8, 3.0), C(12, 2).s - 0.02, 0.4); hit(sting(1.8, 61), C(12, 2).s, 0.35)
# Mom's text
for k in range(2): hit(buzz(), C(13, 1).s - 0.3 + k * 0.5, 0.2)
# the unknown caller: an old two-tone ring that keeps going into the end card, then stops dead
t0 = P(14).s - 0.35; t1 = DUR - 0.9
def ring(d=2.0):
    x = tt(d); on = (x < 1.0); s_ = (np.sin(2 * np.pi * 440 * x) + np.sin(2 * np.pi * 480 * x)) * (np.sin(2 * np.pi * 20 * x) > -0.2)
    return bp(s_ * on, 300, 3000)
t = t0
while t < t1:
    r = ring(); r[max(0, min(len(r), at(t1 - t))):] = 0; hit(r, t, 0.08); t += 2.0
for k in range(2): hit(buzz(), C(14, 2).s - 0.2 + k * 0.5, 0.18)
x = tt(0.3); hit(np.sin(2 * np.pi * 1320 * x) * np.exp(-x * 14), C(14, 2).s - 0.15, 0.08)   # message ping
# cut to the end card: a low hit; the ring carries on; three knocks on the door behind him under PART 4
hit(low_boom(1.6, 3.5), P(15).s - 0.15, 0.3)
for k, g in enumerate((0.45, 0.6, 0.8)): hit(knock(0.8 + 0.25 * k), P(15).e + 0.55 + k * 0.44, g)

i = at(DUR - 0.5); j = at(DUR - 0.9); sfx[j:i] *= np.linspace(1, 0, i - j); sfx[i:] = 0; music[i:] = 0
sf.write('work/music.wav', music.astype(np.float32), SR); sf.write('work/sfx.wav', sfx.astype(np.float32), SR)
print('stems written', DUR)

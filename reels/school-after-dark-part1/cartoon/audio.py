"""Music and SFX stems for "I Stayed in School After Dark" Part 1 (44.1 kHz mono). The voice is not touched.
Music: a very quiet dreamy music-box motif over a low pad (0-10 s), then a low drone with a slow heartbeat
pulse under the guard (10-24 s). It fades out at 24-25 s and never comes back: nothing before or under the knocks.
SFX: room tone, fluorescent buzz and relay clicks, one distant bell, footsteps, torch click, bass swell when the
torch stops, door shut + lock click, footsteps fading behind the door, three knocks (rising), handle creak,
latch, one low impact before black. Everything is zero for the last 0.5 s."""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 35.5
N = int(DUR * SR)
rng = np.random.default_rng(11)
music = np.zeros(N); sfx = np.zeros(N)
F = lambda f: f / 30


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
def fade(x, a=0.01, r=0.01):
    na, nr = max(1, int(a * SR)), max(1, int(r * SR)); x = x.copy()
    x[:na] *= np.linspace(0, 1, na); x[-nr:] *= np.linspace(1, 0, nr); return x
# small empty-classroom reverb: decaying filtered noise impulse
IR = lp(noise(1.1), 5000) * np.exp(-tt(1.1) * 6.0); IR[0] = 0; IR /= np.sqrt(np.sum(IR ** 2))
def room(x, wet=0.35): y = fftconvolve(x, IR)[:len(x) + len(IR) - 1]; z = np.zeros(len(y)); z[:len(x)] = x; return z + wet * y

# ---------------- music (very subtle) ----------------
def pad(m, d, cut=900):
    t = tt(d); x = sum(np.sin(2 * np.pi * note(m + k) * t * (1 + 0.003 * j)) for j, k in enumerate((0, 7, 12, 15)))
    return lp(x / 4, cut) * np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 1.2)
def mbox(m, d=1.6):  # music-box note: sine + inharmonic partial, fast decay
    t = tt(d); f = note(m)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t * 9)) * np.exp(-t * 2.6) * np.minimum(1, t / 0.004)
add(music, pad(45, 10.6, 700), 0.0, 0.5)
for k, m in enumerate((76, 72, 69, 71, 72, 64, 69, 67)):  # slow, a little sad, "dream" motif in A minor
    add(music, room(mbox(m), 0.5), 0.35 + k * 1.15, 0.22)
# guard section: low drone + slow heartbeat (lub-dub), slightly faster as he comes in
add(music, pad(33, 15.2, 300), 9.9, 0.9)
def beat(g):
    x = tt(0.25); return np.sin(2 * np.pi * np.cumsum(55 + 25 * np.exp(-x * 30)) / SR) * np.exp(-x * 14) * g
t = 10.4
while t < 23.9:
    add(music, beat(1.0), t); add(music, beat(0.6), t + 0.24)
    t += 1.05 if t < 16 else 0.92
fo = np.ones(N); i0, i1 = at(23.9), at(25.0); fo[i0:i1] = np.linspace(1, 0, i1 - i0) ** 2; fo[i1:] = 0
music *= fo

# ---------------- SFX ----------------
# Every event is normalised to its own peak (1.0 = the loudest knock); mix_school.py sets knock 3 just under the voice peak.
def hit(x, t, pk): add(sfx, x / (np.abs(x).max() + 1e-12) * pk, t)
IR2 = lp(noise(1.6), 6000) * np.exp(-tt(1.6) * 3.6); IR2[0] = 0; IR2 /= np.sqrt(np.sum(IR2 ** 2))
def hall(x, wet=0.5): y = fftconvolve(x, IR2); z = np.zeros(len(y)); z[:len(x)] = x; return z + wet * y
def modes(ex, fr):  # excitation through a bank of decaying resonances
    x = tt(len(ex) / SR); out = np.zeros(len(ex))
    for f, a, d in fr: out += a * fftconvolve(ex, np.sin(2 * np.pi * f * x) * np.exp(-x * d))[:len(ex)]
    return out
# room tone (quiet but present)
x = tt(35.0); tone = lp(noise(35.0), 400) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * x)) + 0.2 * hp(noise(35.0), 4000)
hit(tone * np.minimum(1, x / 0.6), 0.0, 0.035)
# fluorescent buzz with audible harmonics (phones don't play 100 Hz), dying as the panels go off
x = tt(9.5); hum = sum(np.sin(2 * np.pi * 100 * h * x) / h ** 0.6 for h in (1, 2, 3, 4, 5, 6, 7, 9, 11))
hum = np.tanh(2.5 * hum) * (1 + 0.3 * np.sin(2 * np.pi * 0.7 * x))
lit = np.clip(1 - np.maximum(0, x - F(12)) / (F(140) - F(12)), 0, 1) ** 0.7
hit(bp(hum, 180, 4000) * (0.08 + 0.92 * lit) * np.minimum(1, (9.5 - x) / 2), 0.0, 0.08)
for k in range(12):  # heavy relay clunk as each panel dies (near ones louder)
    off = 12 + (11 - k) * 11; d = 0.25; x = tt(d)
    c = modes(np.r_[noise(0.004), np.zeros(int(d * SR) - int(0.004 * SR))], ((140, 1, 40), (620, 0.6, 70), (1900, 0.4, 120)))
    c += bp(noise(d), 2000, 7000) * np.exp(-x * 220) * 0.5 * np.abs(c).max()
    hit(hall(c, 0.6), F(off), 0.16 + 0.24 * k / 11)
# one distant school bell (single electric ring burst, about 0.9 s, carried down the hallway)
x = tt(0.9); bell = sum(a * np.sin(2 * np.pi * 1050 * r * x) for a, r in ((1, 1), (0.6, 2.71), (0.4, 4.1), (0.25, 5.9)))
bell *= (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 22 * x))) * np.minimum(1, x / 0.01) * np.minimum(1, (0.9 - x) / 0.15)
hit(lp(hall(bell, 1.2), 3800), 9.75, 0.38)
# footsteps: hard heel click + thud, then a softer toe 60 ms later; hallway reverb
def step(br=1.0):
    d = 0.18; x = tt(d)
    heel = bp(noise(d), 1800, 6500) * np.exp(-x * 160) * br + 0.9 * modes(np.r_[noise(0.003), np.zeros(int(d * SR) - int(0.003 * SR))], ((110, 1, 45), (420, 0.5, 80)))
    toe = np.zeros(len(heel)); n = int(0.06 * SR); toe[n:] = 0.35 * bp(noise(d), 1500, 5000)[:len(heel) - n] * np.exp(-x[:len(heel) - n] * 200)
    return hall(heel + toe, 0.55)
for k in range(10): hit(step(), F(310 + 11.2 * k + 3), 0.14 + 0.34 * k / 9)
for f in (473, 484, 495): hit(step(), F(f), 0.5)
# flashlight: two-stage plastic switch click
c = np.r_[bp(noise(0.012), 3000, 9000) * np.exp(-tt(0.012) * 500), np.zeros(int(0.03 * SR)), 0.7 * bp(noise(0.015), 2000, 7000) * np.exp(-tt(0.015) * 400)]
hit(hall(c, 0.3), F(311) - 0.1, 0.5)
# tension when the torch stops on the desk: saturated low drone + high dissonant whine, so phones hear it too
x = tt(3.4); sw = np.tanh(3 * (np.sin(2 * np.pi * np.cumsum(41 + 5 * x / 3.4) / SR) + 0.5 * np.sin(2 * np.pi * 61.5 * x)))
whine = 0.05 * (np.sin(2 * np.pi * 1480 * x) + np.sin(2 * np.pi * 1568 * x))
sw = (bp(sw, 40, 900) + whine) * np.minimum(1, x / 0.5) ** 2 * np.minimum(1, (3.4 - x) / 0.9)
hit(sw, F(508), 0.11)
# guard leaves: steps out, door slams shut, key turns, bolt clacks
for f in (618, 630, 642, 654): hit(step(), F(f), 0.34)
d = 0.7; x = tt(d)
thud = modes(np.r_[noise(0.006), np.zeros(int(d * SR) - int(0.006 * SR))], ((72, 1, 12), (150, 0.8, 20), (310, 0.5, 30), (900, 0.25, 60)))
thud += np.r_[np.zeros(int(0.03 * SR)), bp(noise(d - 0.03), 1500, 6000) * np.exp(-tt(d - 0.03) * 120) * 0.6 * np.abs(thud).max()][:len(thud)]
hit(hall(thud, 0.6), F(668), 0.62)
scrape = bp(noise(0.16), 1200, 4500) * np.sin(np.pi * tt(0.16) / 0.16) * (0.6 + 0.4 * np.sin(2 * np.pi * 45 * tt(0.16)))
hit(hall(scrape, 0.3), F(676), 0.3)
d = 0.35; x = tt(d)
clack = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * dc) for f, a, dc in ((2350, 1, 40), (3720, 0.7, 55), (5150, 0.5, 70), (180, 0.8, 35)))
clack = clack * np.minimum(1, x / 0.001) + bp(noise(d), 2000, 8000) * np.exp(-x * 300) * 1.5
hit(hall(clack, 0.4), F(676) + 0.17, 0.6)
# his footsteps fading down the hallway, muffled through the door
for k in range(9): hit(lp(step(), 1400 - 110 * k), F(690) + k * 0.43, 0.42 * (1 - k / 9) ** 1.4)
# three knocks on the wooden classroom door, each harder: 786 (one) ... 828, 843 (two)
def knock(force):
    d = 0.6; ex = np.r_[noise(0.0025) * np.hanning(int(0.0025 * SR)), np.zeros(int(d * SR) - int(0.0025 * SR))]
    m = modes(ex, ((92, 1.0, 18), (138, 0.9, 22), (205, 0.8, 26), (310, 0.6, 34), (455, 0.45, 45),
                   (690, 0.35 * force, 60), (1040, 0.25 * force, 80), (1600, 0.18 * force, 110)))
    knuckle = bp(noise(d), 1200, 5000) * np.exp(-tt(d) * 260) * 0.35 * force * np.abs(m).max()
    return hall(np.tanh(1.5 * (m + knuckle) / np.abs(m + knuckle).max()), 0.75)
hit(knock(0.8), F(786), 0.72)
hit(knock(1.0), F(828), 0.86)
hit(knock(1.3), F(843), 1.0)
# door handle turning from the other side: stick-slip metal squeak + spring groan, then the latch clunk
d = F(940) - F(885); x = tt(d); u = x / d
f0 = 820 + 420 * u + 60 * np.sin(2 * np.pi * 1.3 * x)
sq = sum(np.sin(2 * np.pi * h * np.cumsum(f0) / SR) / h for h in (1, 2, 3, 4))
slip = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(28 + 14 * np.sin(np.pi * u)) / SR))
groan = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(140 + 30 * u) / SR)) * 0.4
cr = (bp(sq * slip, 600, 4000) + bp(groan, 100, 900)) * np.sin(np.pi * u) ** 0.4
hit(hall(cr, 0.4), F(885), 0.24)
latch = modes(np.r_[noise(0.003), np.zeros(int(0.3 * SR) - int(0.003 * SR))], ((160, 1, 40), (2100, 0.6, 60), (3300, 0.4, 80)))
hit(hall(latch, 0.4), F(938), 0.5)
# riser into one low cinematic impact before black (f943); mid-range body so phones hear it
x = tt(1.0); riser = bp(noise(1.0), 300, 3000) * (x / 1.0) ** 3 * np.minimum(1, (1.0 - x) / 0.03)
hit(riser, F(943) - 1.0, 0.25)
x = tt(2.6); boom = np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-x * 6)) / SR) * np.exp(-x * 1.9)
boom = np.tanh(2.2 * boom) + 0.7 * lp(noise(2.6), 400) * np.exp(-x * 4.0) + 0.5 * bp(noise(2.6), 300, 2500) * np.exp(-x * 18)
hit(hall(boom * np.minimum(1, x / 0.002), 0.5), F(943), 0.95)

# hard silence for the last 0.5 s
for b in (music, sfx):
    i = at(DUR - 0.5); j = at(DUR - 0.8); b[j:i] *= np.linspace(1, 0, i - j); b[i:] = 0
music /= np.abs(music).max() / 0.9  # music is level-locked in mix_school.py; sfx keeps its peak units
sf.write('work/music.wav', music, SR, subtype='FLOAT'); sf.write('work/sfx.wav', sfx, SR, subtype='FLOAT')
print('stems written', DUR)

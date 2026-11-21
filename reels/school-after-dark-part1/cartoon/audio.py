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
# room tone through the whole piece (very quiet), slow breathing air movement
x = tt(35.0); tone = lp(noise(35.0), 380) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * x)) + 0.15 * hp(noise(35.0), 5000)
add(sfx, tone * np.minimum(1, x / 0.6), 0.0, 0.05)
# fluorescent buzz: 100 Hz + harmonics, quieter as the 12 panels go off (frames 12..133), then a tiny residue
x = tt(10.0); hum = sum(np.sin(2 * np.pi * 100 * h * x) / h for h in (1, 2, 3, 5, 7))
lit = np.clip(1 - np.maximum(0, x - F(12)) / (F(133) - F(12)), 0, 1)
add(sfx, hp(hum, 150) * (0.15 + 0.85 * lit) * np.minimum(1, (10 - x) / 2), 0.0, 0.035)
for k in range(12):  # relay clunk for each panel, far ones quieter
    off = 12 + (11 - k) * 11; c = bp(noise(0.05), 600, 3000) * np.exp(-tt(0.05) * 90) + 0.6 * np.sin(2 * np.pi * 90 * tt(0.05)) * np.exp(-tt(0.05) * 60)
    add(sfx, room(c, 0.6), F(off), 0.10 + 0.25 * k / 11)
# one distant school bell, after "No noise."
x = tt(3.0); bell = sum(a * np.sin(2 * np.pi * 880 * r * x) * np.exp(-x * d) for a, r, d in ((1, 1, 1.4), (0.5, 2.76, 2.4), (0.3, 5.4, 4), (0.2, 0.5, 1.0)))
bell *= (1 + 0.5 * np.sin(2 * np.pi * 7 * x)) * np.minimum(1, x / 0.01)  # one short ring burst, trembling
bell = lp(room(bell, 0.9), 2200)
add(sfx, bell, 9.95, 0.09)
# footsteps: heel + scuff on tiles, louder as the guard approaches (corridor f310-414, inside f470-495)
def step(g):
    h = lp(noise(0.12), 900) * np.exp(-tt(0.12) * 55) + 0.8 * np.sin(2 * np.pi * 75 * tt(0.12)) * np.exp(-tt(0.12) * 40)
    s = bp(noise(0.12), 1500, 5000) * np.exp(-tt(0.12) * 30) * 0.25
    return room(h + s, 0.6) * g
for k in range(10):
    f = 310 + 11.2 * k + 3; add(sfx, step(1), F(f), 0.10 + 0.30 * k / 9)
for f in (473, 484, 495): add(sfx, step(1), F(f), 0.45)
# flashlight click on
c = bp(noise(0.02), 2500, 8000) * np.exp(-tt(0.02) * 300); add(sfx, c, F(311), 0.35); add(sfx, c, F(311) + 0.035, 0.25)
# low bass tension when the torch stops on the desk (f520) and he looks (to f594)
x = tt(3.4); sw = np.sin(2 * np.pi * np.cumsum(38 + 4 * x / 3.4) / SR) + 0.5 * np.sin(2 * np.pi * 57 * x)
sw = lp(sw + 0.4 * lp(noise(3.4), 120), 160) * np.minimum(1, x / 0.6) ** 2 * np.minimum(1, (3.4 - x) / 0.9)
add(sfx, sw, F(510), 0.15)
# guard turns to leave: steps out
for f in (618, 630, 642, 654): add(sfx, step(1), F(f), 0.38)
# door shuts (f670) + lock click (f678)
x = tt(0.6); thud = lp(noise(0.6), 300) * np.exp(-x * 14) + np.sin(2 * np.pi * 62 * x) * np.exp(-x * 11)
add(sfx, room(thud, 0.7), F(669), 0.6)
k1 = bp(noise(0.03), 2000, 7000) * np.exp(-tt(0.03) * 200); k2 = bp(noise(0.05), 1200, 5000) * np.exp(-tt(0.05) * 120)
add(sfx, room(k1, 0.4), F(678), 0.55); add(sfx, room(k2, 0.4), F(678) + 0.09, 0.7)
# footsteps fading behind the door, slower and further
for k in range(9):
    add(sfx, lp(step(1), 700 - 50 * k), F(690) + k * 0.42, 0.30 * (1 - k / 9) ** 1.5)
# three knocks on the wooden door, getting harder: 786 (one), 828 + 843 (two)
def knock(g):
    d = 0.35; x = tt(d)
    body = sum(a * np.sin(2 * np.pi * fr * x) * np.exp(-x * dc) for a, fr, dc in ((1, 160, 28), (0.6, 245, 34), (0.4, 380, 45)))
    click = bp(noise(d), 1500, 4500) * np.exp(-x * 160) * 0.7
    thump = lp(noise(d), 250) * np.exp(-x * 50)
    return room((body + click + thump) * np.minimum(1, x / 0.0015), 0.45) * g
add(sfx, knock(1.0), F(786), 0.9)
add(sfx, knock(1.0), F(828), 1.2)
add(sfx, knock(1.0), F(843), 1.5)
# slow door-handle creak (f885-940) + latch at the end of the turn
d = F(940) - F(885); x = tt(d)
rate = 22 + 18 * np.sin(np.pi * x / d) + 4 * rng.standard_normal(len(x)).cumsum() / np.sqrt(SR) * 3
ph = np.cumsum(rate) / SR; pulses = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)
cr = bp(np.convolve(pulses, np.exp(-tt(0.004) * 900), 'same') + 0.05 * noise(d), 700, 2600)
add(sfx, room(cr * np.sin(np.pi * x / d) ** 0.5, 0.5), F(885), 2.2)
add(sfx, room(bp(noise(0.04), 1500, 6000) * np.exp(-tt(0.04) * 150), 0.5), F(938), 0.5)
# one low cinematic impact right before the cut to black (f943)
x = tt(2.6); boom = np.sin(2 * np.pi * np.cumsum(30 + 45 * np.exp(-x * 6)) / SR) * np.exp(-x * 1.9)
boom += 0.6 * lp(noise(2.6), 140) * np.exp(-x * 3.0) + 0.3 * bp(noise(2.6), 200, 1200) * np.exp(-x * 20)
add(sfx, boom * np.minimum(1, x / 0.003), F(943), 1.3)

# hard silence for the last 0.5 s
for b in (music, sfx):
    i = at(DUR - 0.5); j = at(DUR - 0.8); b[j:i] *= np.linspace(1, 0, i - j); b[i:] = 0
for b in (music, sfx): b /= np.abs(b).max() / 0.9  # stems are level-locked later in mix_school.py
sf.write('work/music.wav', music, SR, subtype='FLOAT'); sf.write('work/sfx.wav', sfx, SR, subtype='FLOAT')
print('stems written', DUR)

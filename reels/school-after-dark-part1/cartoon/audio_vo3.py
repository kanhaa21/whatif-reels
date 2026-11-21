"""v4: SFX stem for "I Stayed in School After Dark" Part 1 with the owner's 'who was standing outside' recording (48.5 s).
The recording already carries its own low drone bed, a whoosh (10.5 s), a torch click (11.48 s) and three knocks
(37.61 / 38.05 / 38.49 s), so there is NO extra music here and those sounds are not doubled; the knocks only get a
wooden-door body layered exactly on their onsets. Everything else is added in the pauses between lines.
Picture frames come from main.js REMAP (old animation frame -> new frame); O() is the same table.
SFX are in peak units (1.0 = the third knock body); mix_vo3.py scales them against the recording."""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 48.5
N = int(DUR * SR)
rng = np.random.default_rng(11)
sfx = np.zeros(N)
REMAP = [[0, 0], [200, 180], [291, 266], [343, 310], [486, 414], [525, 470], [594, 500], [691, 520], [726, 560],
         [855, 594], [866, 610], [920, 662], [940, 670], [990, 750], [1127, 786], [1141, 828], [1154, 843], [1265, 875], [1345, 940], [1350, 945]]
def O(old_f):
    for (a, oa), (b, ob) in zip(REMAP, REMAP[1:]):
        if old_f <= ob: return (a + (b - a) * (old_f - oa) / (ob - oa)) / 30
    return REMAP[-1][0] / 30

def at(t): return int(round(t * SR))
def add(buf, x, t, g=1.0):
    i = max(0, at(t)); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += x[:j - i] * g
def noise(d): return rng.standard_normal(int(d * SR))
def tt(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
IR2 = lp(noise(1.6), 6000) * np.exp(-tt(1.6) * 3.6); IR2[0] = 0; IR2 /= np.sqrt(np.sum(IR2 ** 2))
def hall(x, wet=0.5): y = fftconvolve(x, IR2); z = np.zeros(len(y)); z[:len(x)] = x; return z + wet * y
def imp(d, n=0.003): return np.r_[noise(n), np.zeros(int(d * SR) - int(n * SR))]
def modes(ex, fr):
    x = tt(len(ex) / SR); out = np.zeros(len(ex))
    for f, a, d in fr: out += a * fftconvolve(ex, np.sin(2 * np.pi * f * x) * np.exp(-x * d))[:len(ex)]
    return out
def hit(x, t, pk): add(sfx, x / (np.abs(x).max() + 1e-12) * pk, t)

# empty-building room tone, dipping to near nothing around the knocks
x = tt(48.0); tone = lp(noise(48.0), 400) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.09 * x)) + 0.2 * hp(noise(48.0), 4000)
duck = np.ones(len(x)); a, b = at(37.2), at(37.5); duck[a:b] = np.linspace(1, 0.2, b - a); duck[b:at(41.5)] = 0.2
duck[at(41.5):at(42.5)] = np.linspace(0.2, 1, at(42.5) - at(41.5))
hit(tone * np.minimum(1, x / 0.6) * duck, 0.0, 0.03)
# hook: fluorescent buzz and a relay clunk as each hallway panel dies
d = 10.0; x = tt(d); hum = sum(np.sin(2 * np.pi * 100 * h * x) / h ** 0.6 for h in (1, 2, 3, 4, 5, 6, 7, 9, 11))
hum = np.tanh(2.5 * hum) * (1 + 0.3 * np.sin(2 * np.pi * 0.7 * x))
lit = np.clip(1 - np.maximum(0, x - O(12)) / (O(140) - O(12)), 0, 1) ** 0.7
hit(bp(hum, 180, 4000) * (0.08 + 0.92 * lit) * np.minimum(1, (d - x) / 2), 0.0, 0.06)
for k in range(12):
    off = 12 + (11 - k) * 11
    c = modes(imp(0.25, 0.004), ((140, 1, 40), (620, 0.6, 70), (1900, 0.4, 120)))
    c += bp(noise(0.25), 2000, 7000) * np.exp(-tt(0.25) * 220) * 0.5 * np.abs(c).max()
    hit(hall(c, 0.6), O(off), 0.10 + 0.16 * k / 11)
# the guard's slow footsteps and key ring coming down the corridor
def step():
    d = 0.18; x = tt(d)
    heel = bp(noise(d), 1800, 6500) * np.exp(-x * 160) + 0.9 * modes(imp(d), ((110, 1, 45), (420, 0.5, 80)))
    toe = np.zeros(len(heel)); n = int(0.06 * SR); toe[n:] = 0.35 * bp(noise(d), 1500, 5000)[:len(heel) - n] * np.exp(-x[:len(heel) - n] * 200)
    return hall(heel + toe, 0.55)
def keys():
    d = 0.35; out = np.zeros(int(d * SR))
    for k in range(5):
        x = tt(d); f = 3000 + 2500 * rng.random(); j = int(rng.random() * 0.12 * SR)
        out[j:] += (np.sin(2 * np.pi * f * x) * np.exp(-x * 45))[:len(out) - j] * (0.5 + rng.random())
    return out
for k in range(10):
    t = O(313 + 11.2 * k); hit(step(), t, 0.12 + 0.28 * k / 9); hit(hall(keys(), 0.4), t + 0.02, 0.05 + 0.08 * k / 9)
# "That night..." : the classroom door creaks open in the pause
d = 0.85; x = tt(d); u = x / d
f0 = 380 + 160 * u + 25 * np.sin(2 * np.pi * 2.1 * x)
sq = sum(np.sin(2 * np.pi * h * np.cumsum(f0) / SR) / h for h in (1, 2, 3, 5))
slip = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(18 + 10 * np.sin(np.pi * u)) / SR))
hit(hall(bp(sq * slip, 250, 3000) * np.sin(np.pi * u) ** 0.6, 0.5), 15.48, 0.32)
for f in (473, 484, 495): hit(step(), O(f), 0.36)
# "His flashlight passed over my desk... and stopped.": an airy glide with the beam, a sharp swipe, a dead stop
d = 23.0 - 19.8; x = tt(d); u = x / d
glide = bp(noise(d), 500, 3500) * (0.3 + 0.7 * u ** 2) + 0.25 * (np.sin(2 * np.pi * (1480 + 120 * u) * x) + np.sin(2 * np.pi * (1568 - 60 * u) * x)) * u ** 2
glide[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
hit(glide, 19.8, 0.10)
d = 0.35; x = tt(d); sw = bp(noise(d), 800, 7000) * (x / d) ** 3; sw[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
hit(sw, 22.65, 0.32)
x = tt(1.6); thump = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(46 + 50 * np.exp(-x * 10)) / SR)) * np.exp(-x * 3.0)
thump += 0.4 * bp(noise(1.6), 200, 1500) * np.exp(-x * 25)
hit(hall(thump, 0.3), 23.55, 0.55)
# "For one terrifying second...": a held heartbeat while he stares
def beat():
    x = tt(0.3); return np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(52 + 40 * np.exp(-x * 30)) / SR)) * np.exp(-x * 16)
t = 24.3
while t < 27.8:
    hit(lp(beat(), 600), t, 0.22); hit(lp(beat(), 600), t + 0.22, 0.14); t += 0.74
# he turns and walks out; the door slams, the key turns, the bolt clacks
x = tt(0.25); hit(hall(bp(noise(0.25), 800, 4000) * np.sin(np.pi * x / 0.25) ** 2, 0.4), 28.3, 0.18)
for f in (618, 630, 642, 654): hit(step(), O(f), 0.28)
d = 0.7; x = tt(d)
thud = modes(imp(d, 0.006), ((72, 1, 12), (150, 0.8, 20), (310, 0.5, 30), (900, 0.25, 60)))
thud += np.r_[np.zeros(int(0.03 * SR)), bp(noise(d - 0.03), 1500, 6000) * np.exp(-tt(d - 0.03) * 120) * 0.6 * np.abs(thud).max()][:len(thud)]
hit(hall(thud, 0.6), 31.36, 0.8)
scrape = bp(noise(0.16), 1200, 4500) * np.sin(np.pi * tt(0.16) / 0.16) * (0.6 + 0.4 * np.sin(2 * np.pi * 45 * tt(0.16)))
hit(hall(scrape, 0.3), 31.95, 0.38)
d = 0.35; x = tt(d)
clack = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * dc) for f, a, dc in ((2350, 1, 40), (3720, 0.7, 55), (5150, 0.5, 70), (180, 0.8, 35)))
clack = clack * np.minimum(1, x / 0.001) + bp(noise(d), 2000, 8000) * np.exp(-x * 300) * 1.5
hit(hall(clack, 0.4), 32.12, 0.7)
# "His footsteps slowly disappeared": muffled steps going away
for k in range(9): hit(lp(step(), 1400 - 110 * k), 32.5 + k * 0.5, 0.30 * (1 - k / 9) ** 1.4)
# the recording's three knocks get a wooden-door body on their exact onsets, each a little heavier
def knock(force):
    d = 0.6; ex = np.r_[noise(0.0025) * np.hanning(int(0.0025 * SR)), np.zeros(int(d * SR) - int(0.0025 * SR))]
    m = modes(ex, ((92, 1.0, 18), (138, 0.9, 22), (205, 0.8, 26), (310, 0.6, 34), (455, 0.45, 45),
                   (690, 0.35 * force, 60), (1040, 0.25 * force, 80), (1600, 0.18 * force, 110)))
    knuckle = bp(noise(d), 1200, 5000) * np.exp(-tt(d) * 260) * 0.35 * force * np.abs(m).max()
    return hall(np.tanh(1.5 * (m + knuckle) / np.abs(m + knuckle).max()), 0.75)
for t, g, fz in ((37.607, 0.7, 0.8), (38.047, 0.85, 1.0), (38.487, 1.0, 1.3)): hit(knock(fz), t, g)
# someone outside shifts their weight: floorboard groan as the shadow moves under the door
d = 0.7; x = tt(d); u = x / d
groan = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(95 + 40 * u + 8 * np.sin(2 * np.pi * 3 * x)) / SR)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(30 + 20 * u) / SR)))
hit(hall(bp(groan, 120, 1800) * np.sin(np.pi * u) ** 0.8, 0.6), 41.72, 0.3)
# the handle turns from the other side (quiet under the line), the latch lands in the pause
d = O(940) - O(885); x = tt(d); u = x / d
f0 = 820 + 420 * u + 60 * np.sin(2 * np.pi * 1.3 * x)
sq = sum(np.sin(2 * np.pi * h * np.cumsum(f0) / SR) / h for h in (1, 2, 3, 4))
slip = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * np.cumsum(28 + 14 * np.sin(np.pi * u)) / SR))
gr = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(140 + 30 * u) / SR)) * 0.4
hit(hall((bp(sq * slip, 600, 4000) + bp(gr, 100, 900)) * np.sin(np.pi * u) ** 0.4, 0.4), O(885), 0.18)
latch = modes(imp(0.3), ((160, 1, 40), (2100, 0.6, 60), (3300, 0.4, 80)))
hit(hall(latch, 0.4), 44.1, 0.5)
# riser into a short low impact on the cut to black; it dies away before the final whisper
x = tt(0.9); hit(bp(noise(0.9), 300, 3000) * (x / 0.9) ** 3 * np.minimum(1, (0.9 - x) / 0.03), 44.05, 0.2)
x = tt(1.2); boom = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(38 + 70 * np.exp(-x * 6)) / SR) * np.exp(-x * 5.5))
boom = boom + 0.6 * lp(noise(1.2), 400) * np.exp(-x * 9.0) + 0.4 * bp(noise(1.2), 300, 2500) * np.exp(-x * 22)
hit(hall(boom * np.minimum(1, x / 0.002), 0.2), 44.95, 0.8)
# one last, quieter knock under the Part 2 card
hit(knock(0.9), 47.25, 0.5)

i = at(DUR - 0.5); j = at(DUR - 0.8); sfx[j:i] *= np.linspace(1, 0, i - j); sfx[i:] = 0
sf.write('work/sfx_vo3.wav', sfx, SR, subtype='FLOAT')
print('sfx stem written', DUR)

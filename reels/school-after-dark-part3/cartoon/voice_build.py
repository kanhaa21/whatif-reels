"""Narration for 'I Stayed in School After Dark' (Part 3, v2 after the owner's notes, 23 Nov 2026).
Same narrator, same pure-whisper treatment (whisper2.py with Part 2's EQ, work/whisper_eq.npy) and chunk method as Part 2.
Voices:
  n        = Jimmy, the narrator (am_michael; v / e voiced, w / we pure whisper)
  ent      = the thing at the locker vents whispering "Jimmy...": a deep, slow, pure whisper, doubled, very close
  pa       = the school loudspeaker at midnight: thin speaker band, pushed, long hall echo; the mimic's octave-down
             shadow slips in on the last words
  teacher  = whatever is taking attendance in room 109: the guard-mimic voice (very low, doubled), heard from the door
  chorus   = the faceless class answering "Present.": six flat young voices in unison, half whispered
Writes voice.wav + work/phrases.json (phrase and chunk start/end; picture and captions lock to these).
A chunk's caption can differ from its spoken text (CAP below, e.g. "one oh nine" is shown as 109)."""
import json, os, sys
import numpy as np, soundfile as sf, parselmouth
from parselmouth.praat import call
from scipy.signal import butter, sosfilt, fftconvolve
from kokoro_onnx import Kokoro
sys.path.insert(0, '/home/claude/whatif-reels')
from reelkit.voice import shape, _trim
import whisper2 as W2   # v2 tense whisper for the w / we chunks (owner's reference, 23 Nov 2026)

M = os.path.expanduser('~/.cache/reelkit'); k = Kokoro(f'{M}/kokoro-v1.0.onnx', f'{M}/voices-v1.0.bin')
SR = 24000; rng = np.random.default_rng(7)
NARR = 'am_michael'
MODE = {'v': (0.12, 1.00), 'e': (0.10, 1.35), 'w': (0.95, 1.05), 'we': (0.95, 1.45)}
# (gap before, [(text, mode, style, speed, gain, gap after)], who)
L = [
 (1.55, [("Three knocks...", 'w', 'low', 0.82, 1.0, 0.35), ("then a whisper.", 'we', 'dramatic', 0.8, 1.0, 0)], 'n'),
 (0.7, [("Jimmy...", None, None, 0.7, 0.9, 1.0), ("Jimmy...", None, None, 0.66, 1.1, 0)], 'ent'),
 (0.7, [("It knew my name.", 'we', 'dramatic', 0.8, 1.05, 0)], 'n'),
 (0.8, [("When its footsteps faded...", 'v', 'low', 0.9, 0.95, 0.2), ("I slipped out.", 'w', 'low', 0.84, 0.95, 0)], 'n'),
 (1.7, [("Then the school bell rang...", 'e', 'dramatic', 0.88, 1.05, 0.3), ("at midnight.", 'we', 'low', 0.78, 1.05, 0)], 'n'),
 (1.0, [("Attention, students.", None, None, 0.8, 1.0, 0.4), ("Please return to room one oh nine.", None, None, 0.78, 1.0, 0)], 'pa'),
 (0.8, [("Only one door opened...", 'v', 'low', 0.88, 0.95, 0.3), ("Room one oh nine.", 'we', 'dramatic', 0.8, 1.05, 0)], 'n'),
 (0.8, [("Someone inside was taking attendance.", 'w', 'low', 0.86, 1.0, 0)], 'n'),
 (0.7, [("Aarav.", None, None, 0.8, 1.0, 0)], 'teacher'),
 (0.35, [("Present.", None, None, 0.85, 1.0, 0)], 'chorus'),
 (0.5, [("Meera.", None, None, 0.8, 1.0, 0)], 'teacher'),
 (0.35, [("Present.", None, None, 0.85, 1.0, 0)], 'chorus'),
 (0.6, [("Jimmy.", None, None, 0.78, 1.0, 1.3), ("Jimmy.", None, None, 0.74, 1.15, 0.9), ("Jimmy!", None, None, 0.72, 1.45, 0)], 'teacher'),
 (1.0, [("Then Mom texted...", 'v', 'low', 0.9, 0.95, 0.25), ("Don't answer anyone.", 'we', 'dramatic', 0.8, 1.05, 0)], 'n'),
 (1.2, [("But an unknown number was calling...", 'v', 'low', 0.9, 0.95, 0.3), ("and it texted:", 'w', 'low', 0.84, 0.95, 0.2),
        ("Answer it.", 'we', 'dramatic', 0.76, 1.1, 0)], 'n'),
 (1.3, [("What will you do?", 'w', 'question', 0.8, 1.05, 0)], 'n'),
]
CAP = {"Please return to room one oh nine.": "Please return to room 109.", "Room one oh nine.": "Room 109."}
BREATHS_AFTER = {0: [('shaky', 0.15, 1.0)], 2: [('shaky', 0.2, 1.1)], 3: [('in', 0.3, 0.9)], 6: [('shaky', 0.25, 1.0)],
                 12: [('shaky', 0.3, 1.2)], 14: [('shaky', 0.3, 1.0)]}
TAIL = 3.2   # end card hold after the last word

def bpf(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lpf(x, f): return sosfilt(butter(2, f, 'lowpass', fs=SR, output='sos'), x)
def env_rms(x, hop=120):
    n = len(x) // hop + 1; r = np.sqrt(np.array([np.mean(x[i*hop:(i+1)*hop]**2) if len(x[i*hop:(i+1)*hop]) else 0 for i in range(n)]) + 1e-12)
    return np.repeat(np.convolve(r, np.ones(3) / 3, mode='same'), hop)[:len(x)]
def whisperize(x, amt):
    snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=SR)
    lpc = call(snd, "To LPC (burg)", 18, 0.025, 0.005, 50.0)
    noise = parselmouth.Sound(rng.standard_normal(len(x)) * 0.1, sampling_frequency=SR)
    w = call([lpc, noise], "Filter", "no").values[0][:len(x)]
    w = sosfilt(butter(2, 300, 'highpass', fs=SR, output='sos'), w)
    w = w + 0.6 * bpf(w, 2000, 5500)
    w = w * np.minimum(env_rms(x) / (env_rms(w) + 1e-6), 20)
    return (1 - amt) * x + amt * w + (0.08 * x if amt > 0.5 else 0)
def rms(x): return np.sqrt(np.mean(x[np.abs(x) > 0.02 * np.abs(x).max()] ** 2))
def regender(x, pitch, formant=1.0, rng_=1.0):
    snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=SR)
    return call(snd, "Change gender", 60, 600, formant, pitch, rng_, 1.0).values[0]
IR = lpf(rng.standard_normal(int(1.8 * SR)), 5000) * np.exp(-np.arange(int(1.8 * SR)) / SR * 3.2); IR[0] = 0; IR /= np.sqrt(np.sum(IR ** 2))
def verb(x, wet): y = fftconvolve(x, IR); z = np.zeros(len(y)); z[:len(x)] = x; return z + wet * y

def guard_voice(text, sp):
    s, sr = k.create(text, voice='am_onyx', speed=sp, lang='en-us'); s = _trim(s, sr)
    a = regender(s, 72, 0.88, 0.5)                      # lower and flatter than any real guard
    b = regender(s, 68, 0.84, 0.5)                      # second copy, a semitone under: two throats, one voice
    n = int(0.022 * SR); b = np.r_[np.zeros(n), b][:len(a)]
    x = a + 0.55 * b + 0.25 * whisperize(a, 1.0)
    x = lpf(x, 3800)                                    # heard through a door
    return verb(x, 0.45)
def mom_voice(text, sp, last):
    s, sr = k.create(text, voice='af_bella', speed=sp, lang='en-us'); s = _trim(s, sr)
    s = whisperize(shape(s, sr, 'soft', 100, 600), 0.35)
    if last:                                            # the copy slips: an octave-down shadow under "It's me."
        sh = regender(s, 95, 0.8, 0.6); s = s + 0.35 * sh[:len(s)]
    return verb(lpf(s, 5000), 0.18)

def pa_voice(text, sp, last):
    s, sr = k.create(text, voice='bf_emma', speed=sp, lang='en-us'); s = _trim(s, sr)
    s = shape(s, sr, 'deadpan', 100, 600)
    if last:                                            # the copy slips on the room number: an octave-down shadow
        sh = regender(s, 90, 0.82, 0.5); n = len(s); m = np.zeros(n); m[int(n * 0.55):] = 1
        m = np.convolve(m, np.hanning(4801) / np.hanning(4801).sum(), mode='same'); s = s + 0.6 * m * sh[:n]
    x = bpf(s, 450, 3400); x = np.tanh(3.0 * x / (np.abs(x).max() + 1e-9))   # small loudspeaker, pushed
    return verb(verb(x, 0.6), 0.5)                       # long empty-hallway echo
def ent_voice(text, sp):
    s, sr = k.create(text, voice='am_onyx', speed=sp, lang='en-us'); s = _trim(s, sr)
    a = regender(s, 70, 0.86, 0.4)
    w1 = W2.apply_eq(W2.raw(a, SR, True), FIR)          # pure whisper, same treatment as the narrator's
    w2 = W2.apply_eq(W2.raw(regender(s, 64, 0.8, 0.4), SR, True), FIR)
    n = int(0.03 * SR); w2 = np.r_[np.zeros(n), w2][:len(w1)]
    return w1 + 0.6 * w2                                 # two breaths, one name, right at the vents (dry, close)
def teacher_voice(text, sp, g):
    x = guard_voice(text, sp)
    if g > 1.3: x = np.tanh(2.2 * x / (np.abs(x).max() + 1e-9))   # the third call cracks into a roar
    return x
def chorus_voice(text, sp):
    parts = []
    for j, (v, p) in enumerate((('af_sky', 1.0), ('am_puck', 1.0), ('af_nicole', 0.97), ('am_echo', 1.03), ('af_river', 1.0), ('am_liam', 0.98))):
        y, sr = k.create(text, voice=v, speed=sp * p, lang='en-us'); y = _trim(y, sr)
        y = whisperize(shape(y, sr, 'deadpan', 100, 600), 0.5); y = y / (rms(y) + 1e-9)
        parts.append(np.r_[np.zeros(int(0.012 * j * SR)), y])
    n = max(len(p) for p in parts); x = sum(np.pad(p, (0, n - len(p))) for p in parts)
    return verb(lpf(x, 4500), 0.4)

# EQ towards the owner's reference whisper, designed once from all the w / we lines
EQ = 'work/whisper_eq.npy'
if not os.path.exists(EQ):
    parts = []
    for gap0, chunks, who in L:
        if who != 'n': continue
        for text, mode, style, sp, g, gap in chunks:
            if mode in ('w', 'we'):
                y, sr = k.create(text, voice=NARR, speed=sp, lang='en-us')
                parts.append(W2.raw(shape(_trim(y, sr), sr, style, 100, 600), sr, mode == 'we'))
    ref, rsr = sf.read('work/ref_tensed_whisper.wav'); assert rsr == SR
    np.save(EQ, W2.design_eq(ref if ref.ndim == 1 else ref.mean(1), np.concatenate(parts), SR))
FIR = np.load(EQ)

# the picture is locked to the v1 timings: place every chunk at its v1 start (work/phrases_lock.json)
LOCK = json.load(open('work/phrases_lock.json')) if os.path.exists('work/phrases_lock.json') else None
out = np.zeros(int(90 * SR)); meta = []; prev_end = 0.0; breaths = []
for li, (gap0, chunks, who) in enumerate(L):
    t = LOCK['phrases'][li]['s'] if LOCK else prev_end + gap0; t0 = t; ch_meta = []
    for ci, (text, mode, style, sp, g, gap) in enumerate(chunks):
        if who == 'guard': s = guard_voice(text, sp); s = s / rms(s) * 0.085 * g
        elif who == 'mom': s = mom_voice(text, sp, ci == len(chunks) - 1); s = s / rms(s) * 0.07 * g
        elif who == 'pa': s = pa_voice(text, sp, ci == len(chunks) - 1); s = s / rms(s) * 0.06 * g
        elif who == 'ent': s = ent_voice(text, sp); s = s / rms(s) * 0.08 * g
        elif who == 'teacher': s = teacher_voice(text, sp, g); s = s / rms(s) * 0.08 * g
        elif who == 'chorus': s = chorus_voice(text, sp); s = s / rms(s) * 0.06 * g
        else:
            amt, mg = MODE[mode]
            s, sr = k.create(text, voice=NARR, speed=sp, lang='en-us')
            dry = shape(_trim(s, sr), sr, style, 100, 600)
            s = whisperize(dry, amt)                       # v1 path (also keeps the noise generator in step)
            if mode in ('w', 'we'): s = W2.apply_eq(W2.raw(dry, sr, mode == 'we'), FIR)
            s = s / rms(s) * 0.075 * mg * g
            n = int((0.25 if text.endswith(('.', '?')) and mode == 'w' else 0.06) * SR); s[-n:] *= np.linspace(1, 0, n) ** 1.5
        if LOCK: t = LOCK['phrases'][li]['chunks'][ci]['s']
        i = int(t * SR); out[i:i + len(s)] += s
        # chunk end = where the speech energy ends (ignores reverb tails)
        e = env_rms(s); spoken = np.nonzero(e > 0.08 * e.max())[0]; dur = (spoken[-1] + 1) / SR if len(spoken) else len(s) / SR
        ch_meta.append(LOCK['phrases'][li]['chunks'][ci] if LOCK else {"text": CAP.get(text, text), "s": round(t, 3), "e": round(t + dur, 3)})
        t += dur + gap
    if LOCK: t = LOCK['phrases'][li]['e']
    prev_end = t
    meta.append({"text": " ".join(CAP.get(c[0], c[0]) for c in chunks), "who": who, "s": round(t0, 3), "e": round(t, 3), "chunks": ch_meta})
    for kind, off, lv in BREATHS_AFTER.get(li, []): breaths.append((t + off, kind, lv))
    print(f"{li:2d} {t0:6.2f} -> {t:6.2f}  [{who}] {' | '.join(c[0] for c in chunks)}")

def breath(kind):
    d = {'in': 0.6, 'out': 0.75, 'shaky': 0.85}[kind]; n = int(d * SR); x = rng.standard_normal(n); u = np.linspace(0, 1, n)
    if kind == 'out': x = bpf(x, 250, 1800); e = np.minimum(1, u / 0.12) * (1 - u) ** 1.3
    else: x = bpf(x, 500, 3200) + 0.4 * bpf(x, 3500, 6000); e = np.sin(np.pi * u) ** 1.2
    if kind == 'shaky': e = e * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 6.5 * u * d)))
    return x * e
for t, kind, lv in breaths:
    b = breath(kind); i = int(t * SR); b = b / np.abs(b).max() * 0.085 * lv; out[i:i + len(b)] += b
TOTAL = LOCK['duration'] if LOCK else round(prev_end + TAIL, 2)
out = out[:int(TOTAL * SR)]; out[int((TOTAL - 0.5) * SR):] = 0
out = out / max(1.0, np.abs(out).max() / 0.95)
sf.write('voice.wav', out.astype(np.float32), SR)
json.dump({"duration": TOTAL, "phrases": meta}, open('work/phrases.json', 'w'), indent=1)
print("total", TOTAL)

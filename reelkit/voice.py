"""Kokoro TTS + Praat (PSOLA) intonation shaping.

script.json "lines": list of lines; each line is a list of phrases
[spoken_text, style, pause_after_s, speed, caption_text_or_null, voice_or_omitted].
One line = one scene. Styles below change pitch, pitch range, end-rise and loudness."""
import json, os
import numpy as np, soundfile as sf
import parselmouth
from parselmouth.praat import call

MODELS = os.environ.get("REELKIT_MODELS", os.path.expanduser("~/.cache/reelkit"))
VOICE = "am_michael"
# style: (semitone shift, pitch-range factor, end-rise semitones, gain dB); None = special
STYLES = {
    "normal":   (0.0, 1.45, 0.0, 0.0),
    "dramatic": (-2.0, 1.5, -1.5, 0.5),
    "low":      (-3.0, 1.25, -2.0, -1.0),
    "build":    (0.5, 1.6, 1.5, 0.5),
    "excited":  (1.8, 1.75, 0.0, 1.5),
    "question": (0.8, 1.6, 4.0, 0.5),
    "funny":    (2.2, 1.9, 0.0, 1.0),
    "deadpan":  (-1.5, 0.55, -1.0, 0.0),
    "warm":     (0.5, 1.5, 0.0, 0.0),
    "soft":     (1.0, 1.1, 0.8, -3.0),   # light, gentle, quieter (e.g. a calm second character)
    "chipmunk": None,
}


def _trim(s, sr):
    idx = np.where(np.abs(s) > 0.01)[0]
    return s[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]


def shape(s, sr, style):
    snd = parselmouth.Sound(s.astype(np.float64), sampling_frequency=sr)
    if style == "chipmunk":
        out = call(snd, "Change gender", 75, 400, 1.22, 260, 1.6, 1.0)
        v = out.values[0]
        return v / max(1e-6, np.max(np.abs(v))) * np.max(np.abs(s))
    st, rf, rise, gain = STYLES[style]
    manip = call(snd, "To Manipulation", 0.01, 70, 350)
    pt = call(manip, "Extract pitch tier")
    if call(pt, "Get number of points") > 2:
        mean = call(pt, "Get mean (curve)", 0, 0)
        dur = snd.duration
        win = min(0.45, dur * 0.5)
        call(pt, "Formula", f"{mean} * (self/{mean})^{rf} * 2^(({st} + {rise}*max(0, (x - {dur - win})/{win}))/12)")
        call([pt, manip], "Replace pitch tier")
        snd = call(manip, "Get resynthesis (overlap-add)")
    return snd.values[0] * 10 ** (gain / 20)


def generate(lines, outdir, voice=VOICE):
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(MODELS, "kokoro-v1.0.onnx"), os.path.join(MODELS, "voices-v1.0.bin"))
    os.makedirs(outdir, exist_ok=True)
    meta = []
    for i, segs in enumerate(lines):
        parts, smeta, off = [], [], 0.0
        for seg in segs:
            text, style, pause, sp, cap = seg[:5]
            v = seg[5] if len(seg) > 5 and seg[5] else voice     # optional 6th field: per-phrase voice
            s, sr = k.create(text, voice=v, speed=sp, lang="en-us")
            s = shape(_trim(s, sr), sr, style)
            d = len(s) / sr
            smeta.append({"text": cap or text, "off": off, "dur": d, "style": style})
            parts += [s, np.zeros(int(pause * sr))]
            off += d + pause
        line = np.clip(np.concatenate(parts), -0.99, 0.99)
        sf.write(os.path.join(outdir, f"line{i}.wav"), line, sr)
        meta.append({"text": " ".join(x["text"] for x in smeta), "dur": len(line) / sr, "segs": smeta})
    json.dump({"sr": sr, "lines": meta}, open(os.path.join(outdir, "lines.json"), "w"), indent=1)
    return meta

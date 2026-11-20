"""Word, caption-chunk and scene timing from voice lines.json (one scene per voice line)."""
import json, math, re

FPS = 30
W, H = 1080, 1920
LEAD, GAP, TAIL, PRECUT = 0.25, 0.2, 1.3, 0.12

_spoken = {"28": "twentyeight"}


def _weight(w):
    core = re.sub(r"[^A-Za-z0-9']", "", w)
    core = _spoken.get(core, core)
    return 1.6 + len(core)


def _pause(w):
    if w.endswith((".", "?", "!")):
        return 4.0
    if w.endswith(","):
        return 2.2
    return 0.0


def build(src, lead=None, gap=None, tail=None, precut=None, grid=None):
    """grid: snap every line start to lead + k * grid (the drum grid) so the voice lands on the beat"""
    global LEAD, GAP, TAIL, PRECUT
    LEAD = LEAD if lead is None else lead; GAP = GAP if gap is None else gap
    TAIL = TAIL if tail is None else tail; PRECUT = PRECUT if precut is None else precut
    meta = json.load(open(src))
    lines = meta["lines"]
    t = LEAD
    out = []
    for i, ln in enumerate(lines):
        if grid and i > 0:
            t = LEAD + math.ceil((t - LEAD) / grid - 1e-6) * grid
        wl = []
        for sg in ln["segs"]:
            words = sg["text"].split()
            ws = [_weight(w) for w in words]
            ps = [_pause(w) for w in words[:-1]] + [0.0]
            tot = sum(ws) + sum(ps)
            k = (sg["dur"] - 0.06) / tot
            cur = t + sg["off"]
            for j, (w, a, p) in enumerate(zip(words, ws, ps)):
                wl.append({"w": w.replace("...", ""), "s": cur, "e": cur + a * k, "segend": j == len(words) - 1})
                cur += (a + p) * k
        out.append({"i": i, "text": ln["text"], "start": t, "end": t + ln["dur"], "words": wl})
        t += ln["dur"] + GAP
    # scene boundaries on frame grid
    bounds = [0]
    for ln in out[1:]:
        bounds.append(round((ln["start"] - PRECUT) * FPS))
    total = round((out[-1]["end"] + TAIL) * FPS)
    bounds.append(total)
    scenes = []
    for i in range(len(out)):
        scenes.append({"i": i, "f0": bounds[i], "f1": bounds[i + 1],
                       "t0": bounds[i] / FPS, "t1": bounds[i + 1] / FPS})
    # caption chunks
    chunks = []
    for ln in out:
        cur = []
        for j, w in enumerate(ln["words"]):
            cur.append(w)
            clean = " ".join(x["w"] for x in cur)
            brk = w["w"].endswith((".", "?", ",", "!")) or w["segend"] or len(cur) >= 3 or len(clean) >= 15
            if j + 1 < len(ln["words"]):
                nxt = clean + " " + ln["words"][j + 1]["w"]
                if len(nxt) > 17:
                    brk = True
            if brk:
                chunks.append({"line": ln["i"], "words": cur})
                cur = []
        if cur:
            chunks.append({"line": ln["i"], "words": cur})
    for c in chunks:
        c["s"] = c["words"][0]["s"] - 0.03
    for k, c in enumerate(chunks):
        if k + 1 < len(chunks) and chunks[k + 1]["line"] == c["line"]:
            c["e"] = chunks[k + 1]["s"]
        elif k + 1 < len(chunks):
            c["e"] = min(chunks[k + 1]["s"], c["words"][-1]["e"] + 0.3)
        else:
            c["e"] = c["words"][-1]["e"] + 0.9
    return {"lines": out, "scenes": scenes, "chunks": chunks, "total": total / FPS, "grid": grid, "grid0": LEAD}



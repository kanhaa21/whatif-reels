"""Build a reel:  python -m reelkit.make reels/<slug> [--stills 1.5 9.0 ...] [--revoice] [--jobs 2]

reels/<slug>/script.json  -> voice lines, title, captions, hashtags, timing options
reels/<slug>/scenes.py    -> SCENES = [fn(ctx, tg, tl, T), ...]  one function per voice line
Output: reels/<slug>/out/<slug>.mp4 (+ stills/contact sheet with --stills)."""
import argparse, importlib.util, json, math, os, subprocess, sys
from multiprocessing import Pool
import cairo

from . import voice as V, timeline as TLmod, audio as AU
from . import lib as L

FPS, W, H = 30, 1080, 1920


def load_scenes(reel_dir, tl, script):
    spec = importlib.util.spec_from_file_location("scenes", os.path.join(reel_dir, "scenes.py"))
    mod = importlib.util.module_from_spec(spec)
    sc, lines = tl["scenes"], tl["lines"]

    def wt(i, sub, nth=0):
        """start time of a word in line i, relative to scene i's start"""
        k = 0
        for w in lines[i]["words"]:
            if sub.lower() in w["w"].lower():
                if k == nth: return w["s"] - sc[i]["t0"]
                k += 1
        raise KeyError((i, sub))
    mod.wt, mod.TL, mod.SCRIPT = wt, tl, script
    spec.loader.exec_module(mod)
    return mod


def scene_of(tl, tg):
    for s in tl["scenes"]:
        if s["t0"] <= tg < s["t1"]: return s["i"]
    return tl["scenes"][-1]["i"]


def draw_title(ctx, s):
    w = L.text_w(ctx, s, L.DISPLAY, 72)
    x0 = 540 - w / 2 - 34
    g = cairo.LinearGradient(x0, 0, x0 + w + 68, 0)
    g.add_color_stop_rgb(0, 0.15, 0.55, 1.0); g.add_color_stop_rgb(1, 0.95, 0.25, 0.6)
    L.rrect(ctx, x0, 248, w + 68, 108, 22); ctx.set_source(g); ctx.fill()
    L.text(ctx, s, 540, 302, 72, L.WHT, shadow=False)


def draw_captions(ctx, tg, chunks, cy=1400):
    cur = next((c for c in chunks if c["s"] <= tg < c["e"]), None)
    if not cur: return
    words = [w["w"].upper() for w in cur["words"]]
    size, spc = 128, 34
    widths = [L.text_w(ctx, w, L.DISPLAY, size) * 1.1 for w in words]
    tot = sum(widths) + spc * (len(words) - 1)
    sc = min(1.0, 960 / tot); size *= sc; widths = [w * sc for w in widths]
    tot = sum(widths) + spc * (len(words) - 1)
    chunk_pop = 0.85 + 0.15 * L.ease_back((tg - cur["s"]) / 0.16)
    x = 540 - tot / 2
    for w, wd, wi in zip(words, widths, cur["words"]):
        active = wi["s"] - 0.03 <= tg < wi["e"] + 0.02 or (wi is cur["words"][-1] and tg >= wi["s"])
        said = tg >= wi["s"] - 0.03
        s = (1.06 + 0.12 * (1 - L.ease_out((tg - wi["s"]) / 0.18)) if active else 1.0) * chunk_pop
        ctx.save(); ctx.translate(x + wd / 2, cy); ctx.scale(s, s)
        L.text(ctx, w, 0, 0, size, L.YEL if active else L.WHT, stroke=11, alpha=1.0 if said else 0.6)
        ctx.restore(); x += wd + spc


class Frame:
    def __init__(self, reel_dir):
        self.dir = reel_dir
        self.script = json.load(open(os.path.join(reel_dir, "script.json")))
        self.tl = json.load(open(os.path.join(reel_dir, "build", "timeline.json")))
        self.mod = load_scenes(reel_dir, self.tl, self.script)

    def cut_times(self, i):
        f = getattr(self.mod, "cut_times", None)
        return f(i) if f else [0]

    def draw_hook(self, ctx, tg):
        """script.json "hook": {"text": ["LINE 1", "LINE 2"], "until": 2.2}: huge text on the very first frame."""
        h = self.script.get("hook")
        if not h or tg >= h.get("until", 2.2): return
        until = h.get("until", 2.2)
        a = 1.0 if tg < until - 0.3 else (until - tg) / 0.3
        lines = h["text"] if isinstance(h["text"], list) else [h["text"]]
        size = h.get("size", 118)
        pulse = 1 + 0.03 * math.sin(tg * 9)
        y0 = h.get("y", 1120) - (len(lines) - 1) * size * 0.55
        for k, ln in enumerate(lines):
            w = L.text_w(ctx, ln, L.DISPLAY, size)
            sc = min(1.0, 980 / (w + 60)) * pulse
            ctx.save(); ctx.translate(540, y0 + k * size * 1.1); ctx.scale(sc, sc)
            L.rrect(ctx, -w / 2 - 28, -size * 0.58, w + 56, size * 1.16, 18)
            ctx.set_source_rgba(*(L.RED if k == 0 else (0.05, 0.05, 0.12)), 0.92 * a); ctx.fill()
            L.text(ctx, ln, 0, 0, size, L.YEL if k else L.WHT, alpha=a, shadow=False)
            ctx.restore()

    def draw_end_cta(self, ctx, tg):
        """script.json "end_cta": "SEND THIS TO ...": a share prompt over the last 3 seconds of voice."""
        txt = self.script.get("end_cta")
        if not txt: return
        t0 = self.tl["lines"][-1]["end"] - 2.6
        if tg < t0: return
        s = L.pop(tg - t0, 0.25) * (1 + 0.04 * math.sin((tg - t0) * 8))
        ctx.save(); ctx.translate(540, 1235); ctx.scale(s, s)
        w = L.text_w(ctx, txt, L.DISPLAY, 50)
        L.rrect(ctx, -w / 2 - 70, -40, w + 110, 80, 40); ctx.set_source_rgb(*L.GRN); ctx.fill()
        # paper-plane icon
        ctx.save(); ctx.translate(-w / 2 - 30, 0); ctx.scale(0.22, 0.22)
        ctx.move_to(-120, 10); ctx.line_to(130, -90); ctx.line_to(40, 110); ctx.line_to(10, 40); ctx.close_path()
        ctx.set_source_rgb(0, 0, 0); ctx.fill(); ctx.restore()
        L.text(ctx, txt, 20, 0, 50, (0, 0, 0), shadow=False)
        ctx.restore()

    def draw(self, ctx, tg):
        tl = self.tl; i = scene_of(tl, tg); s = tl["scenes"][i]
        loc = tg - s["t0"]; T = s["t1"] - s["t0"]
        bt = loc - max(c for c in self.cut_times(i) if c <= loc) if any(c <= loc for c in self.cut_times(i)) else loc
        bg = getattr(self.mod, "BG", None)
        if bg: bg(ctx, tg, i)
        pz = 1 + 0.06 * math.exp(-bt / 0.09)
        ctx.save(); ctx.translate(540, 880); ctx.scale(pz, pz); ctx.translate(-540, -880)
        self.mod.SCENES[i](ctx, tg, loc, T)
        ctx.restore()
        if self.script.get("style") == "card":
            # card style (owner's reference, 20 Nov 2026): scenes draw their own headline; small captions, no title chip
            from . import cards as C
            C.draw_end_cta(ctx, tg, self.script.get("end_cta"), self.tl["lines"][-1]["end"])
            C.draw_captions(ctx, tg, tl["chunks"])
            return
        self.draw_hook(ctx, tg)
        self.draw_end_cta(ctx, tg)
        draw_title(ctx, self.script.get("title_chip", "WHAT IF?"))
        draw_captions(ctx, tg, tl["chunks"])
        if i > 0 and bt < 0.08 and i not in getattr(self.mod, "NO_FLASH", ()):
            ctx.set_source_rgba(1, 1, 1, 0.3 * (1 - bt / 0.08)); ctx.paint()


def _render(args):
    reel_dir, idxs = args
    F = Frame(reel_dir)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for i in idxs:
        s = F.tl["scenes"][i]
        out = os.path.join(reel_dir, "build", f"scene{i:02d}.mp4"); tmp = out[:-4] + ".part.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                              "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                              "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
        for f in range(s["f0"], s["f1"]):
            ctx = cairo.Context(surf); ctx.set_source_rgb(0, 0, 0); ctx.paint()
            F.draw(ctx, f / FPS); surf.flush(); p.stdin.write(bytes(surf.get_data()))
        p.stdin.close()
        if p.wait() == 0: os.replace(tmp, out)
        else: raise RuntimeError(f"ffmpeg failed on scene {i}")
    return idxs


def stills(reel_dir, times):
    from PIL import Image
    F = Frame(reel_dir)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    paths = []
    for t in times:
        ctx = cairo.Context(surf); ctx.set_source_rgb(0, 0, 0); ctx.paint(); F.draw(ctx, t)
        p = os.path.join(reel_dir, "build", f"still_{t:05.2f}.png"); surf.write_to_png(p); paths.append(p)
    sheet = Image.new("RGB", (270 * len(paths), 480))
    for k, p in enumerate(paths): sheet.paste(Image.open(p).resize((270, 480)), (k * 270, 0))
    sheet.save(os.path.join(reel_dir, "build", "contact_sheet.png"))
    return os.path.join(reel_dir, "build", "contact_sheet.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel_dir"); ap.add_argument("--stills", nargs="*", type=float)
    ap.add_argument("--revoice", action="store_true"); ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    a = ap.parse_args()
    d = a.reel_dir.rstrip("/"); slug = os.path.basename(d)
    script = json.load(open(os.path.join(d, "script.json")))
    b = os.path.join(d, "build"); os.makedirs(b, exist_ok=True)
    vdir = os.path.join(b, "voice")
    if a.revoice or not os.path.exists(os.path.join(vdir, "lines.json")):
        V.generate(script["lines"], vdir, script.get("voice", V.VOICE), script.get("lang", "en-us"),
                   script.get("timing", {}).get("grid"))
    t = script.get("timing", {})
    tl = TLmod.build(os.path.join(vdir, "lines.json"), t.get("lead"), t.get("gap"), t.get("tail"), t.get("precut"), t.get("grid"))
    json.dump(tl, open(os.path.join(b, "timeline.json"), "w"), indent=1)
    print(f"timeline: {tl['total']:.2f}s, {len(tl['scenes'])} scenes", flush=True)
    if a.stills is not None:
        print(stills(d, a.stills)); return
    # balance scenes over workers by duration
    jobs = max(1, a.jobs); buckets = [[] for _ in range(jobs)]; load = [0.0] * jobs
    for s in sorted(tl["scenes"], key=lambda s: s["t0"] - s["t1"]):
        k = load.index(min(load)); buckets[k].append(s["i"]); load[k] += s["t1"] - s["t0"]
    with Pool(jobs) as pool:
        pool.map(_render, [(d, bk) for bk in buckets if bk])
    F = Frame(d)
    AU.build(tl, vdir, F.mod, os.path.join(b, "mix.wav"))
    lst = os.path.join(b, "list.txt")
    open(lst, "w").write("".join(f"file 'scene{s['i']:02d}.mp4'\n" for s in tl["scenes"]))
    os.makedirs(os.path.join(d, "out"), exist_ok=True)
    final = os.path.join(d, "out", f"{slug}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(b, "video.mp4")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(b, "video.mp4"), "-i", os.path.join(b, "mix.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("final:", final)


if __name__ == "__main__":
    main()

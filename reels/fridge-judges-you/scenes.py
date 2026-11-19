"""Scenes for "What if your fridge judged everything you ate?" (one-off Gen Z brainrot reel).
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
Fridge (about 180 cm) and the narrator (about 160 cm) keep roughly true size in wide shots.
Fridge lines are shown in soft lowercase bubbles to match its soft voice."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

MUSIC = {"beat_from_scene": 1, "bpm": 128}
NO_FLASH = ()

HOOD = (1.0, 0.42, 0.68)       # narrator's hoodie
HAIR = (0.16, 0.09, 0.08)
FR = (0.86, 0.93, 1.0)         # fridge body
FR_D = (0.62, 0.72, 0.88)
LAV = (0.97, 0.86, 1.0)
PURP = (0.45, 0.16, 0.6)
CHOC = (0.42, 0.22, 0.12)


def wi(i, k):
    return TL["lines"][i]["words"][k]["s"] - TL["scenes"][i]["t0"]


def seg_starts(i):
    """scene-local start of each phrase of line i"""
    ln = TL["lines"][i]; t0 = TL["scenes"][i]["t0"]
    return [ln["start"] + sg["off"] - t0 for sg in json_segs(i)]


def json_segs(i):
    import json, os
    if not hasattr(json_segs, "m"):
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "voice", "lines.json")
        json_segs.m = json.load(open(p))["lines"]
    return json_segs.m[i]["segs"]


def cut_times(i):
    return [0] + [max(0, s - 0.06) for s in seg_starts(i)[1:]]


# ---------------------------------------------------------------- background
def BG(ctx, tg, i):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.04, 0.03, 0.14); g.add_color_stop_rgb(0.6, 0.12, 0.06, 0.3); g.add_color_stop_rgb(1, 0.08, 0.03, 0.16)
    ctx.set_source(g); ctx.paint()
    # kitchen tiles
    ctx.set_source_rgba(1, 1, 1, 0.035); ctx.set_line_width(2)
    for k in range(13):
        ctx.move_to(k * 90, 380); ctx.line_to(k * 90, 1250)
    for k in range(11):
        ctx.move_to(0, 380 + k * 90); ctx.line_to(W, 380 + k * 90)
    ctx.stroke()
    ctx.rectangle(0, 1250, W, H - 1250); ctx.set_source_rgb(0.1, 0.05, 0.16); ctx.fill()
    # clock on the wall
    ctx.arc(140, 520, 62, 0, 6.3); ctx.set_source_rgb(0.2, 0.12, 0.35); ctx.fill()
    text(ctx, "2:0" + str(min(9, 1 + i)), 140, 520, 44, (1, 0.3, 0.45), SANS, shadow=False)


# ---------------------------------------------------------------- characters
def gal(ctx, x, y, h, expr="smile", arms="down", t=0.0, look=0.0, lids=0.0, blush=False):
    """narrator: long hair, messy bun, pink hoodie. lids 0..1 = half-closed deadpan eyes"""
    u = h / 100
    ctx.save()
    ellipse(ctx, x, y - 80 * u, 19 * u, 22 * u); ctx.set_source_rgb(*HAIR); ctx.fill()           # hair behind
    ctx.restore()
    person(ctx, x, y, h, HOOD, expr, arms, t, look=look)
    ctx.arc(x + 3 * u, y - 104 * u, 9 * u, 0, 6.3); ctx.set_source_rgb(*HAIR); ctx.fill()        # messy bun
    ctx.arc(x - 6 * u, y - 108 * u, 4 * u, 0, 6.3); ctx.fill()
    # hood strings
    ctx.set_line_width(1.4 * u); ctx.set_source_rgb(1, 1, 1)
    for s in (-1, 1):
        ctx.move_to(x + s * 4 * u, y - 70 * u); ctx.line_to(x + s * 4.5 * u, y - 58 * u)
    ctx.stroke()
    if lids > 0:
        ex = look * 3 * u
        for s in (-1, 1):
            cx_, cy_ = x + s * 5.5 * u + ex, y - 85 * u
            ctx.rectangle(cx_ - 4 * u, cy_ - 4.5 * u, 8 * u, 4.5 * u * lids + 0.6 * u); ctx.set_source_rgb(*SKIN); ctx.fill()
            ctx.move_to(cx_ - 3.6 * u, cy_ - 4.5 * u + 4.5 * u * lids); ctx.line_to(cx_ + 3.6 * u, cy_ - 4.5 * u + 4.5 * u * lids)
            ctx.set_line_width(1.2 * u); ctx.set_source_rgb(0.1, 0.06, 0.08); ctx.stroke()
    if blush:
        for s in (-1, 1):
            ctx.arc(x + s * 10 * u, y - 80 * u, 3.5 * u, 0, 6.3); ctx.set_source_rgba(1, 0.45, 0.55, 0.6); ctx.fill()


def ellipse(ctx, x, y, rx, ry, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(rx, ry); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore()


def fridge(ctx, cx, by, s, t, open_=0.0, lid=0.45, brow=0.0, mouth="smirk", glow=0.0, dark=0.0, blink=None,
           tally=0, items=("pizza", "choc", "dal"), look=0.0, eyeglow=0.0):
    """talking fridge, 360 x 800 px at s=1 (about 180 cm tall at 4.4 px/cm), bottom centre at (cx, by).
    lid: eyelid closure 0..1 (0.45 = judging), brow: -1 angry .. +1 raised, open_: main door 0..1"""
    ctx.save(); ctx.translate(cx, by); ctx.scale(s, s)
    w, h = 360, 800; x0, y0 = -w / 2, -h
    fy = y0 + 250                                   # freezer / main door split
    if glow > 0:
        glow_circle(ctx, 0, -350, 700, (1, 0.9, 0.55), 0.5 * glow)
    # body
    g = cairo.LinearGradient(x0, 0, x0 + w, 0)
    g.add_color_stop_rgb(0, *FR); g.add_color_stop_rgb(1, *FR_D)
    rrect(ctx, x0, y0, w, h, 34); ctx.set_source(g); ctx.fill()
    # interior when the main door opens
    if open_ > 0:
        rrect(ctx, x0 + 18, fy + 14, w - 36, h - (fy - y0) - 30, 18)
        ig = cairo.LinearGradient(0, fy, 0, -10); ig.add_color_stop_rgb(0, 1, 0.97, 0.8); ig.add_color_stop_rgb(1, 0.9, 0.85, 0.6)
        ctx.set_source(ig); ctx.fill()
        for k in range(3):
            ctx.rectangle(x0 + 24, fy + 150 + k * 140, w - 48, 8); ctx.set_source_rgba(0.6, 0.75, 0.9, 0.8); ctx.fill()
        if "pizza" in items:
            ctx.move_to(-130, fy + 150); ctx.line_to(-30, fy + 150); ctx.line_to(-80, fy + 70); ctx.close_path()
            ctx.set_source_rgb(1, 0.75, 0.3); ctx.fill()
            for k in range(3):
                ctx.arc(-95 + k * 18, fy + 130 - (k % 2) * 25, 7, 0, 6.3); ctx.set_source_rgb(0.85, 0.15, 0.15); ctx.fill()
        if "choc" in items:
            choc(ctx, 70, fy + 120, 0.6, 0)
        if "dal" in items:
            dal_bowl(ctx, -60, fy + 285, 0.75)
        ctx.rectangle(x0 + 30, fy + 420, 90, 6); ctx.set_source_rgba(0.6, 0.75, 0.9, 0.8); ctx.fill()
        # swung door (thin, seen edge-on) on the right
        dx = x0 + w
        ctx.move_to(dx, fy + 6); ctx.line_to(dx + 150 * open_, fy - 40 * open_); ctx.line_to(dx + 150 * open_, -6 + 40 * open_); ctx.line_to(dx, -6)
        ctx.close_path(); ctx.set_source_rgb(*FR_D); ctx.fill()
    else:
        rrect(ctx, x0 + w - 42, fy + 60, 16, 200, 8); ctx.set_source_rgb(0.55, 0.62, 0.78); ctx.fill()   # handle
    rrect(ctx, x0 + w - 42, y0 + 70, 16, 120, 8); ctx.set_source_rgb(0.55, 0.62, 0.78); ctx.fill()
    ctx.rectangle(x0, fy - 4, w, 8); ctx.set_source_rgb(0.5, 0.58, 0.75); ctx.fill()
    if open_ <= 0:
        # mouth on the main door
        my = fy + 120
        ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(*PURP)
        if mouth == "smirk":
            ctx.move_to(-60, my); ctx.curve_to(-20, my + 18, 30, my + 10, 60, my - 18); ctx.stroke()
        elif mouth == "o":
            ctx.arc(0, my, 22, 0, 6.3); ctx.fill()
        elif mouth == "smile":
            ctx.arc(0, my - 30, 55, 0.2 * math.pi, 0.8 * math.pi); ctx.stroke()
        else:
            ctx.move_to(-50, my); ctx.line_to(50, my); ctx.stroke()
        for k in range(tally):    # tally marks: 2 a.m. visits
            ctx.move_to(-60 + k * 40, fy + 230); ctx.line_to(-50 + k * 40, fy + 330)
            ctx.set_line_width(12); ctx.set_source_rgb(*RED); ctx.stroke()
    # eyes on the freezer door
    if blink is not None:
        lid = max(lid, blink)
    for sx in (-1, 1):
        ex, ey = sx * 72, y0 + 135
        if eyeglow > 0:
            glow_circle(ctx, ex, ey, 110, (1, 0.95, 0.5), 0.7 * eyeglow)
        ellipse(ctx, ex, ey, 50, 56); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        ctx.arc(ex + look * 16, ey + 10, 24, 0, 6.3); ctx.set_source_rgb(0.15, 0.1, 0.3); ctx.fill()
        ctx.arc(ex + look * 16 - 8, ey + 2, 7, 0, 6.3); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        # eyelid
        ctx.save(); ellipse(ctx, ex, ey, 50, 56); ctx.clip()
        ctx.rectangle(ex - 60, ey - 60, 120, 120 * lid); ctx.set_source_rgb(*FR); ctx.fill()
        ctx.restore()
        ctx.move_to(ex - 52, ey - 56 + 112 * lid); ctx.line_to(ex + 52, ey - 56 + 112 * lid)
        ctx.set_line_width(7); ctx.set_source_rgb(*PURP); ctx.stroke()
        # brow
        by_ = ey - 82 - 18 * max(0, brow)
        tilt = (brow if brow < 0 else -brow * 0.3) * 22
        ctx.move_to(ex - 46, by_ - sx * tilt); ctx.line_to(ex + 46, by_ + sx * tilt)
        ctx.set_line_width(13); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(*PURP); ctx.stroke()
    if dark > 0:
        rrect(ctx, x0 - 4, y0 - 4, w + 8, h + 8, 36); ctx.set_source_rgba(0.02, 0.01, 0.06, dark); ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- props
def choc(ctx, x, y, s, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rrect(ctx, -70, -110, 140, 220, 14); ctx.set_source_rgb(*CHOC); ctx.fill()
    for r_ in range(3):
        for c in range(2):
            rrect(ctx, -58 + c * 62, -98 + r_ * 50, 54, 42, 8); ctx.set_source_rgb(0.5, 0.28, 0.16); ctx.fill()
    ctx.rectangle(-72, 40, 144, 72); ctx.set_source_rgb(0.85, 0.15, 0.4); ctx.fill()
    text(ctx, "CHOCO", 0, 76, 34, WHT, shadow=False)
    ctx.restore()


def dal_bowl(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ellipse(ctx, 0, -60, 110, 24); ctx.set_source_rgb(1, 0.78, 0.2); ctx.fill()
    ctx.move_to(-112, -62); ctx.curve_to(-100, 10, 100, 10, 112, -62); ctx.close_path()
    g = cairo.LinearGradient(-110, 0, 110, 0); g.add_color_stop_rgb(0, 0.65, 0.68, 0.75); g.add_color_stop_rgb(0.5, 0.95, 0.96, 1); g.add_color_stop_rgb(1, 0.6, 0.63, 0.7)
    ctx.set_source(g); ctx.fill()
    ellipse(ctx, 0, -60, 112, 26); ctx.set_source_rgba(0.85, 0.95, 1, 0.35); ctx.fill()   # cling film
    ctx.arc(-30, -64, 6, 0, 6.3); ctx.arc(20, -58, 5, 0, 6.3); ctx.set_source_rgb(0.3, 0.6, 0.2); ctx.fill()
    ctx.restore()


def slice_(ctx, x, y, s, rot=0.0, bite=False):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    ctx.move_to(-90, -120); ctx.line_to(90, -120); ctx.line_to(0, 130); ctx.close_path()
    ctx.set_source_rgb(1, 0.78, 0.32); ctx.fill()
    rrect(ctx, -100, -150, 200, 44, 20); ctx.set_source_rgb(0.85, 0.5, 0.2); ctx.fill()
    for k, (px, py) in enumerate(((-40, -70), (30, -60), (-5, 0), (10, 60))):
        ctx.arc(px, py, 18, 0, 6.3); ctx.set_source_rgb(0.85, 0.15, 0.15); ctx.fill()
    if bite:
        ctx.arc(0, 130, 34, 0, 6.3); ctx.set_operator(cairo.OPERATOR_CLEAR); ctx.fill(); ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.restore()


def cereal_box(ctx, x, y, s, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rrect(ctx, -90, -150, 180, 300, 12); ctx.set_source_rgb(1, 0.75, 0.15); ctx.fill()
    rrect(ctx, -75, -120, 150, 70, 10); ctx.set_source_rgb(*RED); ctx.fill()
    text(ctx, "CRUNCH", 0, -85, 40, WHT, shadow=False)
    for k in range(7):
        ctx.arc(-50 + (k % 4) * 33, 10 + (k // 4) * 45, 14, 0, 6.3); ctx.set_source_rgb(0.85, 0.5, 0.15); ctx.fill()
    ctx.restore()


def flag(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.rectangle(-6, -320, 12, 320); ctx.set_source_rgb(0.85, 0.85, 0.9); ctx.fill()
    ctx.move_to(6, -310)
    for k in range(11):
        ctx.line_to(6 + k * 22, -310 + 12 * math.sin(t * 8 - k * 0.6))
    for k in range(10, -1, -1):
        ctx.line_to(6 + k * 22, -170 + 12 * math.sin(t * 8 - k * 0.6))
    ctx.close_path(); ctx.set_source_rgb(*GRN); ctx.fill()
    ctx.restore()


def receipt(ctx, x, y, L_, rows, t):
    """paper strip printing downward from (x, y), length L_ px"""
    if L_ <= 0: return
    ctx.save()
    ctx.rectangle(x - 150, y, 300, L_); ctx.set_source_rgb(1, 1, 0.97); ctx.fill()
    for k in range(int(L_ / 24)):
        ctx.move_to(x - 150 + (k % 2) * 12, y + L_); ctx.line_to(x - 138 + (k % 2) * 12, y + L_ + 12)
    ctx.clip_preserve(); ctx.restore()
    ctx.save(); ctx.rectangle(x - 150, y, 300, L_); ctx.clip()
    text(ctx, "2 A.M. LOG", x, y + 40, 40, (0.1, 0.1, 0.15), shadow=False)
    for k, (a, b, col) in enumerate(rows):
        yy = y + 100 + k * 64
        text(ctx, a, x - 125, yy, 34, (0.15, 0.15, 0.2), SANS, align="l", shadow=False)
        text(ctx, b, x + 125, yy, 40, col, align="r", shadow=False)
    ctx.restore()


def fbubble(ctx, x, y, txt, tt, size=56, maxw=560, tail=(0, 1)):
    """the fridge's soft, lowercase speech bubble"""
    if tt < 0: return
    sc = 0.6 + 0.4 * ease_out(tt / 0.25)
    words = txt.split(); rows = [""]
    for w_ in words:
        cand = (rows[-1] + " " + w_).strip()
        if text_w(ctx, cand, SANS, size) > maxw and rows[-1]:
            rows.append(w_)
        else:
            rows[-1] = cand
    bw = max(text_w(ctx, r, SANS, size) for r in rows) + 70
    bh = len(rows) * size * 1.25 + 44
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    a = clamp(tt / 0.15)
    rrect(ctx, -bw / 2, -bh / 2, bw, bh, 40); ctx.set_source_rgba(*LAV, 0.96 * a); ctx.fill()
    tx, ty = tail
    ctx.move_to(-28 + tx * 60, bh / 2 - 4 if ty > 0 else -bh / 2 + 4); ctx.line_to(tx * 120, (bh / 2 + 46) * ty); ctx.line_to(28 + tx * 60, bh / 2 - 4 if ty > 0 else -bh / 2 + 4)
    ctx.close_path(); ctx.fill()
    for k, r in enumerate(rows):
        text(ctx, r, 0, -bh / 2 + 22 + size * 0.62 + k * size * 1.25, size, PURP, SANS, shadow=False, alpha=a)
    ctx.restore()


def meme(ctx, txt, x, y, tt, col=RED, size=96, rot=-0.08, shake=True):
    """slammed meme stamp with a short shake"""
    if tt < 0: return
    sx = (10 * math.sin(tt * 70) * math.exp(-tt * 6)) if shake else 0
    stamp(ctx, txt, x + sx, y, tt, col, size, rot)


def skull(ctx, x, y, s, tt):
    if tt < 0: return
    sc = pop(tt, 0.2) * s
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate(0.15 * math.sin(tt * 10))
    ctx.arc(0, -10, 60, 0, 6.3); ctx.set_source_rgb(0.97, 0.97, 1); ctx.fill()
    rrect(ctx, -34, 30, 68, 46, 12); ctx.fill()
    for sx in (-1, 1):
        ellipse(ctx, sx * 24, -10, 17, 20); ctx.set_source_rgb(0.1, 0.05, 0.15); ctx.fill()
    for k in range(3):
        ctx.rectangle(-22 + k * 18, 52, 6, 22); ctx.fill()
    ctx.restore()


def speed_lines(ctx, cx, cy, t, n=24, a=0.5):
    for k in range(n):
        ang = hrand("sl", k) * 6.3
        r0 = 380 + 200 * hrand("sr", k) + (t * 900) % 200
        ctx.move_to(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0)
        ctx.line_to(cx + math.cos(ang) * (r0 + 260), cy + math.sin(ang) * (r0 + 260))
    ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, a); ctx.stroke()


def zoom(ctx, cx, cy, z):
    ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tfr = wt(0, "fridge"); tag = wt(0, "Again")
    op = ease_out((tl - tfr) / 0.35) if tl > tfr else 0
    ctx.set_source_rgba(0, 0, 0.05, 0.45 * (1 - op)); ctx.paint()
    ctx.save()
    if tl > tag - 0.05:
        zoom(ctx, 700, 560, 1 + 0.35 * ease_out((tl - tag + 0.05) / 0.25))
    fridge(ctx, 720, 1250, 1.0, tl, open_=op, glow=op, lid=0.45 if tl > tag - 0.1 else 1.0, brow=0.6, eyeglow=0)
    walk = ease_io(tl / 1.0)
    gal(ctx, 180 + 160 * walk, 1250 - abs(math.sin(tl * 8)) * 10 * (1 - walk), 700, "smile" if tl < tag else "shock",
        "down", tl, look=1)
    ctx.restore()
    if tl > tag - 0.05:
        fbubble(ctx, 720, 400 + 60, "again?", tl - tag + 0.05, 60, tail=(0, 1))


def s1(ctx, tg, tl, T):
    tbro = 0; tju = wt(1, "judging"); tth = wt(1, "Third")
    if tl < tth - 0.06:
        z = 1 + 0.08 * tl
        ctx.save(); zoom(ctx, 540, 800, z)
        gal(ctx, 540, 2150, 1600, "shock", "cheeks", tl, look=0)
        ctx.restore()
        meme(ctx, "BRO.", 540, 1150, tl - 0.05, YEL, 120, -0.06)
        if tl > tju - 0.05:
            meme(ctx, "JUDGING ME?!", 540, 560, tl - tju + 0.05, RED, 96, 0.05)
    else:
        tt = tl - tth + 0.06
        ctx.save(); zoom(ctx, 540, 700, 1.25 + 0.05 * tt)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.5, brow=0.9, mouth="smirk", tally=min(3, int(tt / 0.25) + 1))
        ctx.restore()
        fbubble(ctx, 540, 490, "third time tonight, bestie.", tt, 56)
        popchip(ctx, "3 VISITS", 820, 1150, tt - 0.6, RED, WHT, 52)


def s2(ctx, tg, tl, T):
    ss = seg_starts(2); tdm = wt(2, "damage"); tma = ss[2]
    if tl < ss[1] - 0.06:
        fridge(ctx, 780, 1250, 0.95, tl, open_=1, glow=1, items=("choc", "dal"), lid=0.45, brow=0.4)
        gal(ctx, 250, 1250, 700, "cheeks", "up", tl, look=1, blush=True)
        slice_(ctx, 470, 620, 0.9 + 0.1 * math.sin(tl * 6), -0.2)
        popchip(ctx, "COLD PIZZA", 300, 1120, tl - 0.15, YEL, (0, 0, 0), 56)
    elif tl < tma - 0.06:
        tt = tl - ss[1] + 0.06
        ctx.save(); zoom(ctx, 540, 700, 1.2)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.6, brow=-0.2, mouth="flat")
        ctx.restore()
        fbubble(ctx, 540, 490, "it's giving... emotional damage.", tt, 56)
        if tl > tdm - 0.05:
            meme(ctx, "EMOTIONAL DAMAGE", 540, 1130, tl - tdm + 0.05, RED, 84, -0.07)
            skull(ctx, 900, 980, 1.0, tl - tdm - 0.1)
    else:
        tt = tl - tma + 0.06
        ctx.save(); zoom(ctx, 540, 760, 1 + 0.06 * tt)
        gal(ctx, 540, 2150, 1600, "smile", "down", tl, look=0.6, lids=0.55)
        slice_(ctx, 860, 1050, 0.8, 0.3, bite=True)
        ctx.restore()
        meme(ctx, "MA'AM.", 540, 560, tt - 0.05, PNK, 110, -0.05)
        popchip(ctx, "YOU'RE A FRIDGE", 540, 1180, tl - wt(2, "fridge") + 0.05, CYN, (0, 0, 0), 60)


def s3(ctx, tg, tl, T):
    ss = seg_starts(3); the = wt(3, "healthy"); tau = ss[2]
    if tl < ss[1] - 0.06:
        fridge(ctx, 780, 1250, 0.95, tl, open_=1, glow=1, items=("dal",), lid=0.45, brow=0.4, look=-0.5)
        gal(ctx, 250, 1250, 700, "smile", "up", tl, look=1)
        choc(ctx, 480, 640, 1.0 + 0.08 * math.sin(tl * 7), -0.25)
        popchip(ctx, "FINE.", 250, 1120, tl - 0.05, YEL, (0, 0, 0), 60)
    elif tl < tau - 0.06:
        tt = tl - ss[1] + 0.06
        ctx.save(); zoom(ctx, 540, 700, 1.2)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.35, brow=1.0, mouth="o")
        ctx.restore()
        fbubble(ctx, 540, 490, "wasn't this your healthy era?", tt, 56)
        if tl > the - 0.05:
            # sticky note on the fridge
            sc = pop(tl - the + 0.05, 0.2)
            ctx.save(); ctx.translate(780, 1030); ctx.rotate(0.12); ctx.scale(sc, sc)
            rrect(ctx, -130, -100, 260, 200, 8); ctx.set_source_rgb(1, 0.95, 0.4); ctx.fill()
            text(ctx, "HEALTHY", 0, -35, 52, (0.85, 0.2, 0.45), shadow=False)
            text(ctx, "ERA", 0, 30, 52, (0.85, 0.2, 0.45), shadow=False)
            text(ctx, "day 1", 0, 78, 30, (0.3, 0.3, 0.3), SANS, shadow=False)
            ctx.restore()
    else:
        tt = tl - tau + 0.06
        z = 1 + 0.6 * ease_out(tt / 0.5)
        ctx.save(); zoom(ctx, 540, 740, z)
        gal(ctx, 540, 2150, 1600, "worry", "down", tl, look=0, lids=0.6)
        ctx.restore()
        speed_lines(ctx, 540, 760, tl, 26, 0.35)
        meme(ctx, "THE AUDACITY", 540, 1150, tt - 0.05, RED, 104, -0.06)


def s4(ctx, tg, tl, T):
    ss = seg_starts(4); tgr = wt(4, "Green"); tcl = ss[2]; tfa = wt(4, "fast")
    if tl < ss[1] - 0.06:
        fridge(ctx, 780, 1250, 0.95, tl, open_=1, glow=1, items=(), lid=0.45, brow=0.2, look=-0.5)
        gal(ctx, 250, 1250, 700, "worry", "up", tl, look=1)
        dal_bowl(ctx, 470, 640, 1.2)
        popchip(ctx, "MOM'S DAL", 360, 1120, tl - 0.1, YEL, (0, 0, 0), 56)
    elif tl < tcl - 0.06:
        tt = tl - ss[1] + 0.06
        ctx.save(); zoom(ctx, 540, 700, 1.2)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.1, brow=0.6, mouth="smile")
        ctx.restore()
        fbubble(ctx, 540, 490, "finally. green flag.", tt, 56)
        if tl > tgr - 0.05:
            flag(ctx, 860, 1180, pop(tl - tgr + 0.05, 0.25) * 1.2, tl)
            sparkles(ctx, 540, 820, 380, tl, 16, GRN, "gf")
    else:
        tt = tl - tcl + 0.06
        sh = 18 * math.exp(-max(0, tl - tfa) * 8) * math.sin(tl * 80) if tl > tfa else 0
        ctx.save(); ctx.translate(sh, 0)
        slam = 1 - ease_out((tl - tcl) / 0.35) if tl > tcl else 1
        fridge(ctx, 780, 1250, 0.95, tl, open_=max(0, slam), glow=slam, items=(), lid=0.8 if slam < 0.1 else 0.3, brow=-0.6, mouth="o")
        gal(ctx, 300 - 120 * ease_out(tt / 0.6), 1250, 700, "shock", "run", tl, look=-1)
        ctx.restore()
        if tl > tcl + 0.3:
            meme(ctx, "SLAM!", 760, 560, tl - tcl - 0.3, YEL, 120, 0.08)
        if tl > tfa - 0.05:
            popchip(ctx, "NOT THAT ERA", 360, 1150, tl - tfa + 0.05, PNK, WHT, 56)


def s5(ctx, tg, tl, T):
    ss = seg_starts(5); tli = wt(5, "light"); tre = wt(5, "receipts")
    ctx.set_source_rgba(0, 0, 0.04, 0.6); ctx.paint()
    if tl < ss[1] - 0.06:
        ctx.save(); zoom(ctx, 540, 760, 1.3 + 0.08 * tl)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.55, brow=-0.5, mouth="flat", dark=0.55, eyeglow=0.8)
        ctx.restore()
        fbubble(ctx, 540, 490, "i saw that.", tl - 0.05, 60)
    else:
        tt = tl - ss[1] + 0.06
        fridge(ctx, 700, 1250, 0.95, tl, lid=0.5, brow=-0.3, mouth="smirk", dark=0.4, eyeglow=0.6,
               glow=0.7 if tl > tli - 0.1 else 0)
        if tl > tli - 0.1:
            # the light flicks on through the door gap
            ctx.rectangle(700 + 171 * 0.95 - 4, 1250 - 560 * 0.95, 10, 540 * 0.95)
            ctx.set_source_rgba(1, 0.95, 0.6, 0.9); ctx.fill()
        L_ = clamp((tl - tre + 0.3) / 0.8) * 420 if tl > tre - 0.3 else 0
        receipt(ctx, 300, 560, L_, [("2:03", "PIZZA", RED), ("2:04", "CHOCO", RED), ("2:05", "DAL?? NO", ORG), ("2:06", "SUS", PURP)], tl)
        if tl > tre - 0.05:
            meme(ctx, "IT HAS RECEIPTS", 540, 1150, tl - tre + 0.05, RED, 84, -0.05)


def s6(ctx, tg, tl, T):
    ss = seg_starts(6); tgr = wt(6, "gremlin")
    ctx.set_source_rgba(0, 0, 0.03, 0.82); ctx.paint()
    if tl < ss[1] - 0.06:
        hop = abs(math.sin(tl * 9)) * 6
        ctx.save(); zoom(ctx, 540, 900, 1.15)
        gal(ctx, 540, 1300 - hop, 900, "cheeks", "cheeks", tl, look=0.3)
        cereal_box(ctx, 720, 980, 1.05, 0.25)
        ctx.restore()
        # glowing gremlin eyes
        for sx in (-1, 1):
            glow_circle(ctx, 540 + sx * 57, 480, 50, YEL, 0.5 + 0.3 * math.sin(tl * 9))
        for k in range(4):
            popchip(ctx, "CRUNCH", 300 + (k % 2) * 480, 560 + k * 140, tl - 0.25 - k * 0.3, YEL, (0, 0, 0), 46)
        if tl > tgr - 0.05:
            meme(ctx, "GREMLIN MODE", 540, 1150, tl - tgr + 0.05, GRN, 96, -0.06)
    else:
        tt = tl - ss[1] + 0.06
        fridge(ctx, 820, 1250, 0.8, tl, lid=0.4, brow=0.8, mouth="smirk", dark=0.8, eyeglow=1.0, look=-1)
        gal(ctx, 300, 1250, 640, "shock", "up", tl, look=1)
        cereal_box(ctx, 420, 1050, 0.6, 0.6 + 0.3 * math.sin(tl * 20))
        fbubble(ctx, 680, 520, "i can still hear you.", tt, 46, maxw=480, tail=(1, 1))
        skull(ctx, 220, 600, 0.9, tt - 0.6)


def s7(ctx, tg, tl, T):
    ss = seg_starts(7); tye = wt(7, "Yes"); tno = wt(7, "no?"); tse = ss[1]
    fridge(ctx, 800, 1250, 0.8, tl, lid=0.35 if (tl * 0.8) % 2 > 0.2 else 1.0, brow=0.8, mouth="smile")
    gal(ctx, 280, 1250, 600, "smile" if tl < tse else "cheeks", "wave" if tl > tse else "down", tl, look=1)
    if tl < tse - 0.06:
        popchip(ctx, "WOULD YOURS ROAST YOU?", 540, 520, tl - 0.05, PNK, WHT, 56)
        for k, (txt, x, col, t0) in enumerate((("YES", 300, GRN, tye), ("NO", 780, RED, tno))):
            s = pop(tl - t0 + 0.05, 0.22) * (1 + 0.04 * math.sin(tl * 7 + k))
            ctx.save(); ctx.translate(x, 760); ctx.scale(s, s)
            glow_circle(ctx, 0, 0, 200, col, 0.4)
            rrect(ctx, -130, -80, 260, 160, 50); ctx.set_source_rgb(*col); ctx.fill()
            text(ctx, txt, 0, 0, 100, (0, 0, 0) if k == 0 else WHT, shadow=False)
            ctx.restore()
    else:
        tt = tl - tse + 0.06
        f = ease_io(tt / 1.0)
        px = 330 + 420 * f; py = 720 - 200 * math.sin(f * math.pi)
        ctx.save(); ctx.translate(px, py); ctx.rotate(-0.4 + 0.8 * f); ctx.scale(0.8, 0.8)
        ctx.move_to(-120, 10); ctx.line_to(130, -90); ctx.line_to(40, 110); ctx.line_to(10, 40); ctx.close_path()
        ctx.set_source_rgb(*WHT); ctx.fill(); ctx.restore()
        popchip(ctx, "2 A.M. SNACK BUDDY", 540, 520, tt - 0.4, YEL, (0, 0, 0), 56)


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7]


# ---------------------------------------------------------------- sound
def _boom(A, t, g=0.55):
    """deep meme boom"""
    import numpy as np
    n = int(1.2 * 44100); tt = np.arange(n) / 44100
    x = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 1.2) + 35) / 44100) * np.exp(-tt * 3)
    x += 0.4 * A.lp(A.noise(1.2), 300) * np.exp(-tt * 10)
    A.add(A.sfx_buf, x, t, g)


def _crunch(A, t, g=0.2):
    import numpy as np
    for k in range(5):
        n = int(0.05 * 44100)
        A.add(A.sfx_buf, A.hp(A.noise(0.05), 1500) * np.exp(-np.arange(n) / 44100 * 60), t + k * 0.045, g)


def _hum(A, t0, t1, g=0.12):
    import numpy as np
    n = int((t1 - t0) * 44100); tt = np.arange(n) / 44100
    A.add(A.sfx_buf, (np.sin(2 * np.pi * 60 * tt) + 0.5 * np.sin(2 * np.pi * 120 * tt)) * np.minimum(1, tt / 0.3), t0, g)


def sfx(A):
    _hum(A, 0.0, A.S(1), 0.05)
    A.ding(A.W(0, "fridge") + 0.1, 0.06, 1760, 0.6)                     # fridge light
    A.scratch(A.W(0, "Again") - 0.08, 0.3)
    _boom(A, A.W(0, "Again") + 0.05, 0.5)
    _boom(A, A.W(1, "Bro"), 0.45)
    A.pop(A.W(1, "Third"), 0.3)
    for k in range(3):
        A.pop(A.W(1, "Third") + 0.25 + k * 0.25, 0.2)
    A.boing(A.W(2, "pizza"), 0.15, 420)
    _boom(A, A.W(2, "damage"), 0.6)
    A.scratch(A.W(2, "Ma'am") - 0.05, 0.25)
    A.pop(A.W(3, "Chocolate"), 0.3)
    A.ding(A.W(3, "healthy"), 0.06, 1318.5)
    _boom(A, A.W(3, "audacity"), 0.6)
    A.ding(A.W(4, "Green"), 0.08, 1568); A.ding(A.W(4, "Green") + 0.1, 0.08, 2093)
    A.thump(A.W(4, "Closed") + 0.3, 0.8, 60)                              # door slam
    A.whoosh(A.W(4, "fast"), 0.2, 0.4)
    A.music_level(A.S(5), A.S(5) + 1.3, 0.2)                               # beat dips for "i saw that"
    A.thump(A.W(5, "light") - 0.05, 0.4, 120)
    for k in range(10):
        A.ding(A.W(5, "receipts") - 0.25 + k * 0.07, 0.025, 2600, 0.15)  # printer
    for k in range(4):
        _crunch(A, A.S(6) + 0.3 + k * 0.3, 0.18)
    _boom(A, A.W(6, "gremlin"), 0.45)
    A.scratch(A.W(6, "hear") - 0.3, 0.25)
    A.pop(A.W(7, "Yes"), 0.35); A.pop(A.W(7, "no?"), 0.35)
    A.whoosh(A.W(7, "Send") + 0.1, 0.2, 0.6)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(7, "snack") + 0.1 + k * 0.1, 0.07, A.note(m))

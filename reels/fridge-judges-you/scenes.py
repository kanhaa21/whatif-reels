"""Scenes for "What if your fridge judged everything you ate?" (one-off Gen Z brainrot reel).
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
Fridge (about 180 cm) and the narrator (about 160 cm) keep roughly true size in wide shots.
Fridge lines are shown in soft lowercase bubbles to match its soft voice."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

MUSIC = {"beat_from_scene": 1, "bpm": 128}
CLOCK = ["2:00", "2:01", "2:03", "2:07", "2:09", "2:11", "2:14", "2:15"]
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
    text(ctx, CLOCK[min(i, len(CLOCK) - 1)], 140, 520, 44, (1, 0.3, 0.45), SANS, shadow=False)


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


def dal_box(ctx, x, y, s, lid=0.0, t=0.0):
    """clear takeaway container of dal; lid 0 = off (floating above), 1 = shut"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -120, -90, 240, 110, 18); ctx.set_source_rgba(0.85, 0.95, 1, 0.45); ctx.fill()
    rrect(ctx, -108, -70, 216, 82, 14); ctx.set_source_rgb(1, 0.78, 0.2); ctx.fill()
    for k in range(5):
        ctx.arc(-70 + k * 35, -50 + 10 * (k % 2), 6, 0, 6.3); ctx.set_source_rgb(0.3, 0.6, 0.2); ctx.fill()
    ly = -96 - 150 * (1 - ease_out(lid))
    rrect(ctx, -132, ly - 22, 264, 26, 10); ctx.set_source_rgba(0.75, 0.88, 1, 0.9); ctx.fill()
    if lid < 0.95:
        for k in range(3):   # steam
            ctx.move_to(-40 + k * 40, -100)
            ctx.curve_to(-60 + k * 40, -140, -20 + k * 40, -160, -40 + k * 40, -200 - 10 * math.sin(t * 4 + k))
            ctx.set_line_width(6); ctx.set_source_rgba(1, 1, 1, 0.4 * (1 - lid)); ctx.stroke()
    ctx.restore()


def droopy_slice(ctx, x, y, s, t, droop=1.0):
    """cold pizza slice with sad, drooping cheese"""
    slice_(ctx, x, y, s, -0.15)
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.15); ctx.scale(s, s)
    for k in range(3):
        L_ = 40 + 70 * droop * (0.6 + 0.4 * math.sin(t * 2 + k))
        rrect(ctx, -30 + k * 25, 60, 14, L_, 7); ctx.set_source_rgb(1, 0.9, 0.5); ctx.fill()
    ctx.restore()


def halo_rays(ctx, cx, cy, t, a):
    if a <= 0: return
    ctx.save(); ctx.translate(cx, cy)
    for k in range(16):
        ang = k * math.pi / 8 + t * 0.4
        ctx.move_to(0, 0); ctx.line_to(math.cos(ang - 0.08) * 1400, math.sin(ang - 0.08) * 1400)
        ctx.line_to(math.cos(ang + 0.08) * 1400, math.sin(ang + 0.08) * 1400); ctx.close_path()
        ctx.set_source_rgba(1, 0.92, 0.55, 0.12 * a); ctx.fill()
    ctx.restore()
    glow_circle(ctx, cx, cy, 520, (1, 0.9, 0.6), 0.5 * a)


def halo(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y + 6 * math.sin(t * 3)); ctx.scale(s, s)
    ellipse(ctx, 0, 0, 130, 30); ctx.set_line_width(16); ctx.set_source_rgb(1, 0.88, 0.3); ctx.stroke()
    ctx.restore()


def receipt2(ctx, x, y, L_, rows):
    """long receipt printing downward from the fridge slot at (x, y)"""
    if L_ <= 0: return
    w = 560
    ctx.save()
    ctx.rectangle(x - w / 2, y, w, L_); ctx.set_source_rgb(1, 1, 0.96); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.12)
    ctx.rectangle(x - w / 2, y, 10, L_); ctx.fill()
    ctx.rectangle(x - w / 2, y, w, L_); ctx.clip()
    text(ctx, "FRIDGE RECEIPT", x, y + 48, 48, (0.1, 0.1, 0.15), shadow=False)
    ctx.set_dash([10, 8]); ctx.move_to(x - w / 2 + 20, y + 90); ctx.line_to(x + w / 2 - 20, y + 90)
    ctx.set_line_width(3); ctx.set_source_rgb(0.4, 0.4, 0.45); ctx.stroke(); ctx.set_dash([])
    for k, (a, b, col) in enumerate(rows):
        yy = y + 140 + k * 74
        aw = text(ctx, a, x - w / 2 + 28, yy, 30, (0.25, 0.25, 0.3), SANS, align="l", shadow=False)
        room_ = w - 56 - aw - 24
        sz = min(42, 42 * room_ / max(1, text_w(ctx, b, DISPLAY, 42)))
        text(ctx, b, x + w / 2 - 28, yy, sz, col, align="r", shadow=False)
    ctx.restore()


def sitting_gal(ctx, x, floor_y, h, expr, t, look=0.0, lids=0.0):
    """narrator sitting on the floor: legs hidden behind knees at floor level"""
    u = h / 100
    gal(ctx, x, floor_y + 38 * u, h, expr, "cheeks", t, look=look, lids=lids)
    ctx.rectangle(0, floor_y, W, 40 * u); ctx.set_source_rgb(0.1, 0.05, 0.16); ctx.fill()
    for s in (-1, 1):
        ellipse(ctx, x + s * 16 * u, floor_y - 6 * u, 14 * u, 10 * u); ctx.set_source_rgb(0.15, 0.17, 0.3); ctx.fill()


def frozen(ctx, a):
    """freeze-frame tint: icy overlay + frame lines"""
    if a <= 0: return
    ctx.set_source_rgba(0.55, 0.85, 1, 0.22 * a); ctx.paint()
    ctx.set_line_width(14); ctx.set_source_rgba(0.75, 0.95, 1, 0.8 * a)
    rrect(ctx, 40, 400, 1000, 880, 30); ctx.stroke()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tag = wt(0, "Again")
    ton = 0.35                                        # light snaps on
    op = ease_out((tl - 0.1) / 0.3) if tl > 0.1 else 0
    lit = tl > ton
    if not lit:
        ctx.set_source_rgba(0, 0, 0.04, 0.75); ctx.paint()
    ctx.save()
    if tl > tag - 0.05:
        zoom(ctx, 720, 560, 1 + 0.3 * ease_out((tl - tag + 0.05) / 0.25))
    if lit:
        halo_rays(ctx, 720, 800, tl, 0.6 * math.exp(-(tl - ton) * 1.5) + 0.25)
    fridge(ctx, 720, 1250, 1.0, tl, open_=op, glow=1.0 if lit else 0, lid=0.45 if tl > tag - 0.1 else 1.0, brow=0.6,
           items=("pizza", "choc"))
    gal(ctx, 330, 1250 - (abs(math.sin(tl * 7)) * 8 if tl < ton else 0), 700,
        "worry" if tl < ton else ("cheeks" if tl < tag else "shock"), "down" if tl < tag else "up", tl, look=1)
    ctx.restore()
    if lit and tl < ton + 0.12:
        ctx.set_source_rgba(1, 0.95, 0.8, 0.55 * (1 - (tl - ton) / 0.12)); ctx.paint()
    if tl > tag - 0.05:
        fbubble(ctx, 720, 470, "again?", tl - tag + 0.05, 64)


def s1(ctx, tg, tl, T):
    tth = wt(1, "Third")
    if tl < tth - 0.06:
        ctx.save(); zoom(ctx, 540, 800, 1 + 0.08 * tl)
        gal(ctx, 540, 2150, 1600, "worry", "down", tl, look=0, lids=0.5)
        ctx.restore()
        meme(ctx, "BRO.", 540, 1150, tl - 0.05, YEL, 120, -0.06)
        popchip(ctx, "DON'T JUDGE ME", 540, 560, tl - wt(1, "judge") + 0.05, PNK, WHT, 70)
    else:
        tt = tl - tth + 0.06
        ctx.save(); zoom(ctx, 540, 700, 1.25 + 0.05 * tt)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.5, brow=0.9, mouth="smirk", tally=min(3, int(tt / 0.25) + 1))
        ctx.restore()
        fbubble(ctx, 540, 490, "third visit tonight, bestie.", tt)
        s = pop(tt - 0.4, 0.22)
        ctx.save(); ctx.translate(540, 1170); ctx.scale(s, s); ctx.rotate(-0.04)
        rrect(ctx, -300, -62, 600, 124, 30); ctx.set_source_rgb(0.05, 0.05, 0.1); ctx.fill()
        text(ctx, "FRIDGE VISITS:", -50, 0, 64, WHT, shadow=False)
        text(ctx, "3", 215, 0, 92, RED, shadow=False)
        ctx.restore()


def s2(ctx, tg, tl, T):
    ss = seg_starts(2); tch = wt(2, "cheese"); tgu = wt(2, "gave"); tun = ss[1]; tle = ss[2]
    if tl < tun - 0.06:
        fridge(ctx, 780, 1250, 0.95, tl, open_=1, glow=1, items=("choc", "dal"), lid=0.5, brow=0.5, look=-0.6)
        gal(ctx, 250, 1250, 700, "cheeks", "up", tl, look=1, blush=True)
        pk = pop(tl - 0.05, 0.2)
        droopy_slice(ctx, 470, 620, 0.9 * pk, tl, droop=clamp((tl - tch) / 0.6) if tl > tch else 0.2)
        fbubble(ctx, 760, 520, "cold pizza? even the cheese gave up.", tl - 0.05, 50, maxw=460, tail=(0.4, 1))
        if tl > tgu - 0.05:
            meme(ctx, "RIP CHEESE", 330, 1150, tl - tgu + 0.05, ORG, 80, -0.06)
    elif tl < tle - 0.06:
        tt = tl - tun + 0.06
        ctx.save(); zoom(ctx, 540, 760, 1 + 0.1 * tt)
        gal(ctx, 540, 2150, 1600, "worry", "cheeks", tl, look=0.0)
        ctx.restore()
        # dramatic tear + spotlight
        g = cairo.RadialGradient(540, 760, 200, 540, 760, 900)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.1, 0, 0.2, 0.7); ctx.set_source(g); ctx.paint()
        ty = 700 + ((tt * 300) % 200)
        ellipse(ctx, 600, ty, 12, 18); ctx.set_source_rgb(*CYN); ctx.fill()
        meme(ctx, "MAIN CHARACTER MOMENT", 540, 1150, tt - 0.3, PNK, 66, -0.04, shake=False)
    else:
        tt = tl - tle + 0.06
        fridge(ctx, 620, 1250, 0.95, tl, open_=1, glow=1, items=("pizza", "dal"), lid=0.4, brow=0.9, look=-0.8)
        fbubble(ctx, 560, 490, "i literally keep your leftovers.", tt, 52)
        # leftovers piling out of the fridge
        for k in range(4):
            f = ease_out((tt - 0.3 - k * 0.15) / 0.3)
            if f <= 0: continue
            bx, by = 180 + (k % 2) * 140, 1180 - (k // 2) * 110
            rrect(ctx, bx - 60, by - 45 - 60 * (1 - f), 120, 90, 14)
            ctx.set_source_rgb(*[(1, 0.6, 0.2), (0.9, 0.3, 0.3), (0.95, 0.85, 0.3), (0.5, 0.8, 0.4)][k]); ctx.fill()
        popchip(ctx, "LEFTOVER ARCHIVE", 250, 900, tt - 0.6, YEL, (0, 0, 0), 46)


def s3(ctx, tg, tl, T):
    ss = seg_starts(3); tera = wt(3, "era"); tau = ss[1]
    frz = tl > tera + 0.15
    reach = ease_io(tl / 1.6)
    ctx.save()
    if tl > tau - 0.06:
        zoom(ctx, 540, 700, 1 + 0.25 * ease_out((tl - tau + 0.06) / 0.3))
    fridge(ctx, 780, 1250, 0.95, tl if not frz else tera, open_=1, glow=1, items=("dal",), lid=0.35, brow=1.0, look=-0.6)
    gal(ctx, 250 + 60 * reach, 1250, 700, "shock" if frz else "smile", "up" if reach > 0.5 else "down",
        tl if not frz else tera + 0.15, look=1)
    choc(ctx, 600 - 60 * (1 - reach), 760 - 120 * reach, 0.85, -0.25)
    ctx.restore()
    if tl < tau - 0.06:
        fbubble(ctx, 540, 490, "wasn't this your healthy era?", tl - 0.05, 52)
    else:
        fbubble(ctx, 540, 490, "the audacity.", tl - tau + 0.06, 64)
    if frz:
        frozen(ctx, ease_out((tl - tera - 0.15) / 0.15))
        s = pop(tl - tera - 0.2, 0.22)
        ctx.save(); ctx.translate(540, 1140); ctx.scale(s, s); ctx.rotate(-0.04)
        rrect(ctx, -330, -70, 660, 140, 30); ctx.set_source_rgb(0.05, 0.05, 0.1); ctx.fill()
        text(ctx, "HEALTHY ERA:", -110, 0, 62, GRN, shadow=False)
        text(ctx, "4 HOURS OLD", 200, 0, 50, WHT, shadow=False)
        ctx.restore()


def s4(ctx, tg, tl, T):
    ss = seg_starts(4); tgf = wt(4, "green"); tdp = ss[1]
    ang = clamp((tl - 0.9) / 0.15) * (1 - clamp((tl - tdp + 0.4) / 0.3))   # angelic window
    lid = ease_out((tl - tdp + 0.55) / 0.3) if tl > tdp - 0.55 else 0
    if tl < tdp - 0.06:
        halo_rays(ctx, 760, 760, tl, 0.3 + 0.7 * ang)
        fridge(ctx, 780, 1250, 0.95, tl, open_=1, glow=1, items=(), lid=0.05, brow=0.8, look=-0.6)
        halo(ctx, 780, 430 + 30, 1.0, tl)
        gal(ctx, 260, 1250, 700, "shock" if tl < 0.9 else "smile", "down", tl, look=1)
        dal_box(ctx, 470, 840, 1.0, lid, tl)
        fbubble(ctx, 560, 470 + 60, "finally. a green flag.", tl - 0.05, 54)
        if tl > tgf - 0.05:
            flag(ctx, 600, 1250, pop(tl - tgf + 0.05, 0.25) * 1.15, tl)
            sparkles(ctx, 600, 820, 420, tl, 18, (1, 0.95, 0.6), "ang")
    else:
        tt = tl - tdp + 0.06
        ctx.save(); zoom(ctx, 540, 700, 1.22)
        fridge(ctx, 540, 1350, 1.05, tl, lid=0.55, brow=-0.9, mouth="flat")
        ctx.restore()
        dal_box(ctx, 780, 1120, 0.7, 1.0, tl)
        fbubble(ctx, 540, 490, "don't pretend you're better than me.", tt, 50)
        meme(ctx, "BETRAYAL", 300, 1140, tt - 1.0, RED, 84, -0.08)


def s5(ctx, tg, tl, T):
    trc = wt(5, "receipts")
    ctx.set_source_rgba(0, 0, 0.04, 0.35); ctx.paint()
    sh = 6 * math.sin(tl * 60) if tl < 1.6 else 0
    fridge(ctx, 540 + sh, 1250, 0.95, tl, lid=0.3, brow=0.9, mouth="smirk")
    # print slot on the freezer door
    rrect(ctx, 540 - 180, 1250 - 0.95 * 640, 360, 16, 6); ctx.set_source_rgb(0.1, 0.1, 0.15); ctx.fill()
    L_ = 640 * ease_io((tl - 0.05) / 1.3)
    rows = [("2:03 A.M.", "COLD PIZZA", RED), ("2:07 A.M.", "CHOCOLATE", RED),
            ("2:11 A.M.", "EMOTIONAL SUPPORT CEREAL", ORG), ("2:14 A.M.", "REGRET", PURP)]
    receipt2(ctx, 540, 1250 - 0.95 * 640 + 8, L_, rows)
    fbubble(ctx, 540, 470, "i have receipts.", tl - trc + 0.15, 60)
    if tl > 1.5:
        meme(ctx, "KA-CHING!", 790, 1150, tl - 1.5, GRN, 90, 0.07)


def s6(ctx, tg, tl, T):
    trg = wt(6, "right")
    ctx.set_source_rgba(0, 0, 0.03, 0.8); ctx.paint()
    lookf = ease_io((tl - trg - 0.2) / 0.8) if tl > trg - 0.2 else 0
    fridge(ctx, 860, 1250, 0.7, tl, lid=0.4, brow=0.8, mouth="smirk", dark=0.75, eyeglow=1.0, look=-1)
    chew = abs(math.sin(tl * 14)) if lookf < 0.3 else 0
    sitting_gal(ctx, 360, 1250, 800 + 6 * chew, "cheeks" if lookf < 0.5 else "worry", tl, look=lookf, lids=0.5 * lookf)
    cereal_box(ctx, 530, 1080, 0.75, 0.25 + 0.05 * math.sin(tl * 14))
    if lookf < 0.3:
        for k in range(3):
            popchip(ctx, "CRUNCH", 170 + k * 170, 560 + (k % 2) * 90, tl - 0.15 - k * 0.35, YEL, (0, 0, 0), 46)
    fbubble(ctx, 700, 520, "you know i can still hear you chewing, right?", tl - 0.05, 46, maxw=520, tail=(1, 1))
    if lookf > 0.3:
        popchip(ctx, "*SLOWLY TURNS*", 360, 1150, tl - trg - 0.5, WHT, (0, 0, 0), 52)


def s7(ctx, tg, tl, T):
    tq = wt(7, "Would")
    fridge(ctx, 800, 1250, 0.8, tl, lid=0.35 if (tl * 0.8) % 2 > 0.2 else 1.0, brow=0.8, mouth="smile")
    gal(ctx, 280, 1250, 600, "smile", "down", tl, look=1)
    s = pop(tl - 0.05, 0.22)
    ctx.save(); ctx.translate(540, 540); ctx.scale(s, s)
    rrect(ctx, -440, -70, 880, 140, 40); ctx.set_source_rgb(*PNK); ctx.fill()
    text(ctx, "WOULD YOUR FRIDGE ROAST YOU?", 0, 0, 64, WHT, shadow=False)
    ctx.restore()
    for k, (txt, x, col, t0) in enumerate((("YES", 300, GRN, 0.5), ("NO", 780, RED, 0.75))):
        s = pop(tl - t0, 0.22) * (1 + 0.04 * math.sin(tl * 7 + k))
        ctx.save(); ctx.translate(x, 780); ctx.scale(s, s)
        glow_circle(ctx, 0, 0, 200, col, 0.4)
        rrect(ctx, -130, -80, 260, 160, 50); ctx.set_source_rgb(*col); ctx.fill()
        text(ctx, txt, 0, 0, 100, (0, 0, 0) if k == 0 else WHT, shadow=False)
        ctx.restore()


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7]


# ---------------------------------------------------------------- sound
def _boom(A, t, g=0.55):
    import numpy as np
    n = int(1.2 * 44100); tt = np.arange(n) / 44100
    x = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 1.2) + 35) / 44100) * np.exp(-tt * 3)
    x += 0.4 * A.lp(A.noise(1.2), 300) * np.exp(-tt * 10)
    A.add(A.sfx_buf, x, t, g)


def _crunch(A, t, g=0.2, n_=5):
    import numpy as np
    for k in range(n_):
        n = int(0.05 * 44100)
        A.add(A.sfx_buf, A.hp(A.noise(0.05), 1500) * np.exp(-np.arange(n) / 44100 * 60), t + k * 0.045, g)


def _hum(A, t0, t1, g=0.12):
    import numpy as np
    n = int((t1 - t0) * 44100); tt = np.arange(n) / 44100
    A.add(A.sfx_buf, (np.sin(2 * np.pi * 60 * tt) + 0.5 * np.sin(2 * np.pi * 120 * tt)) * np.minimum(1, tt / 0.3), t0, g)


def _light_on(A, t):
    """dramatic light-on: clunk, then a rising shimmer"""
    import numpy as np
    A.thump(t, 0.7, 70)
    A.add(A.sfx_buf, A.hp(A.noise(0.08), 2000) * np.exp(-np.arange(int(0.08 * 44100)) / 44100 * 50), t, 0.3)
    n = int(0.9 * 44100); tt = np.arange(n) / 44100
    x = sum(np.sin(2 * np.pi * f * tt * (1 + 0.5 * tt)) for f in (880, 1320, 1760)) / 3
    A.add(A.sfx_buf, x * np.minimum(1, tt / 0.05) * np.exp(-tt * 3), t + 0.02, 0.12)


def _angel(A, t, d=1.1, g=0.22):
    """one-second angelic 'aah' chord"""
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * tt)
    x = 0
    for m in (72, 76, 79, 84):
        f = A.note(m)
        x = x + np.sin(2 * np.pi * f * np.cumsum(vib) / 44100) + 0.3 * np.sin(2 * np.pi * 2 * f * np.cumsum(vib) / 44100)
    env = np.minimum(1, tt / 0.15) * np.minimum(1, (d - tt) / 0.3)
    A.add(A.sfx_buf, A.lp(x / 4, 3500) * env, t, g)


def _printer(A, t, d=1.3, g=0.16):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    buzz = A.bp(A.noise(d), 1500, 5000) * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 28 * tt)))
    A.add(A.sfx_buf, buzz * np.minimum(1, (d - tt) / 0.05), t, g)


def _kaching(A, t, g=0.4):
    import numpy as np
    n = int(0.15 * 44100)
    A.add(A.sfx_buf, A.bp(A.noise(0.15), 400, 3000) * np.exp(-np.arange(n) / 44100 * 25), t, 0.5 * g)   # drawer
    A.ding(t + 0.05, 0.25 * g / 0.4, 2637, 1.0)
    A.ding(t + 0.16, 0.25 * g / 0.4, 3520, 1.2)


def sfx(A):
    _hum(A, 0.0, A.S(1), 0.04)
    _light_on(A, 0.35)
    A.scratch(A.W(0, "Again") - 0.08, 0.25)
    _boom(A, A.W(0, "Again") + 0.05, 0.5)
    _boom(A, A.W(1, "Bro"), 0.4)
    for k in range(3):
        A.pop(A.W(1, "Third") + 0.4 + k * 0.25, 0.2)
    A.pop(A.S(2) + 0.12, 0.45)                                          # tiny pop: pizza picked up
    A.boing(A.W(2, "gave"), 0.15, 260)
    A.drone(A.W(2, "You"), A.W(2, "You") + 1.1, (220, 277.2, 329.6), 0.25, 1200)   # sad violin-ish pad
    A.pop(A.W(2, "literally") - 0.1, 0.25)
    A.scratch(A.S(3) + 0.05, 0.4)                                        # record scratch on the chocolate reach
    _boom(A, A.W(3, "era") + 0.2, 0.45)
    _boom(A, A.W(3, "audacity"), 0.55)
    A.music_level(A.S(4) + 0.8, A.S(4) + 2.1, 0.15)                     # beat dips for the angels
    _angel(A, A.S(4) + 0.95, 1.1, 0.25)
    A.ding(A.W(4, "green"), 0.06, 1568)
    A.thump(A.W(4, "Don't") - 0.45, 0.35, 140)                          # lid snaps shut
    _boom(A, A.W(4, "Don't"), 0.35)
    _printer(A, A.S(5) + 0.05, 1.35, 0.16)
    _kaching(A, A.S(5) + 1.5, 0.55)
    for k in range(4):
        _crunch(A, A.S(6) + 0.15 + k * 0.35, 0.32, 6)                   # loud cereal crunch
    A.scratch(A.W(6, "right") + 0.3, 0.2)
    A.pop(A.S(7) + 0.5, 0.35); A.pop(A.S(7) + 0.75, 0.35)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.S(7) + 1.9 + k * 0.1, 0.07, A.note(m))

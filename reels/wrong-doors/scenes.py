"""Scenes for "What if every door opened to the wrong place?" Part 1. One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
Everything is drawn in screen pixels; the hero (blue striped pyjamas) stays the same size class (h 640-760)."""
import math
import cairo
import numpy as np
from reelkit.lib import *  # noqa: F401,F403

SR = 44100
BG = lambda ctx, tg, i: bg_glow(ctx, tg, i, dark_scenes=(0, 5, 6))
MUSIC = {"beat_from_scene": 2, "bpm": 124}
NO_FLASH = (6,)

PJ = (0.3, 0.6, 1.0)
WOOD = (0.55, 0.32, 0.2)
OCEAN_GLOW = (0.45, 0.8, 1.0); WARM = (1.0, 0.78, 0.4)


# ---------------------------------------------------------------- people
def hero(ctx, x, fy, h, expr="smile", arms="down", t=0.0, look=0.0):
    person(ctx, x, fy, h, PJ, expr, arms, t, look=look)
    u = h / 100
    ctx.save(); rrect(ctx, x - 19 * u, fy - 72 * u, 38 * u, 36 * u, 12 * u); ctx.clip()
    for k in range(-3, 4):
        ctx.rectangle(x + k * 10 * u - 2 * u, fy - 72 * u, 4 * u, 36 * u)
    ctx.set_source_rgba(1, 1, 1, 0.45); ctx.fill(); ctx.restore()


def mustache(ctx, x, fy, h, look=0.0):
    u = h / 100; hy = fy - 86 * u
    for s in (-1, 1):
        ctx.save(); ctx.translate(x + look * 3 * u + s * 3.5 * u, hy + 4.5 * u); ctx.rotate(s * 0.25); ctx.scale(1, 0.45)
        ctx.arc(0, 0, 4.2 * u, 0, 6.3); ctx.restore()
    ctx.set_source_rgb(0.15, 0.1, 0.08); ctx.fill()


# ---------------------------------------------------------------- doors
def door(ctx, cx, fy, w, h, op, portal=None, t=0.0, glow=None, shake=0.0, leaf=WOOD, leak=None, number=None):
    """op: 0 closed .. 1 wide open (leaf hinged left, swinging toward us). portal(ctx, x, y, w, h, t) fills the opening."""
    x0, y0 = cx - w / 2 + shake, fy - h
    if glow and op > 0.05:
        ctx.move_to(x0, fy); ctx.line_to(x0 + w, fy); ctx.line_to(x0 + w + 280 * op, fy + 320); ctx.line_to(x0 - 160 * op, fy + 320)
        ctx.close_path(); ctx.set_source_rgba(*glow, 0.3 * op); ctx.fill()
        glow_circle(ctx, x0 + w / 2, y0 + h / 2, w * 1.1, glow, 0.35 * op)
    ctx.rectangle(x0, y0, w, h); ctx.set_source_rgb(0.02, 0.02, 0.05); ctx.fill()
    if portal and op > 0.01:
        ctx.save(); ctx.rectangle(x0, y0, w, h); ctx.clip(); portal(ctx, x0, y0, w, h, t); ctx.restore()
    ctx.set_line_width(22); ctx.set_source_rgb(0.9, 0.88, 0.96)
    ctx.move_to(x0 - 11, fy); ctx.line_to(x0 - 11, y0 - 11); ctx.line_to(x0 + w + 11, y0 - 11); ctx.line_to(x0 + w + 11, fy); ctx.stroke()
    lw = w * (1 - 0.84 * op); sk = 0.1 * h * op
    if lw > 2:
        ctx.move_to(x0, y0); ctx.line_to(x0 + lw, y0 - sk); ctx.line_to(x0 + lw, fy + sk); ctx.line_to(x0, fy); ctx.close_path()
        ctx.set_source_rgb(*leaf); ctx.fill()
        ctx.set_source_rgba(0, 0, 0, 0.22); ctx.set_line_width(max(2, 5 * lw / w))
        for py, ph in ((0.08, 0.38), (0.54, 0.38)):
            ctx.rectangle(x0 + lw * 0.15, y0 + h * py, lw * 0.7, h * ph); ctx.stroke()
        ctx.arc(x0 + lw * 0.86, y0 + h * 0.55, max(3, 11 * lw / w), 0, 6.3); ctx.set_source_rgb(0.95, 0.8, 0.3); ctx.fill()
        if number is not None:
            ctx.arc(x0 + lw / 2, y0 + h * 0.33, 62 * lw / w, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()
            text(ctx, str(number), x0 + lw / 2, y0 + h * 0.33, 90 * lw / w, (0.05, 0.05, 0.15), shadow=False)
    if leak:
        a, col = leak
        ctx.rectangle(x0, fy - 8, w, 8); ctx.set_source_rgba(*col, a); ctx.fill()
        ctx.move_to(x0, fy); ctx.line_to(x0 + w, fy); ctx.line_to(x0 + w + 120, fy + 120); ctx.line_to(x0 - 120, fy + 120); ctx.close_path()
        ctx.set_source_rgba(*col, 0.35 * a); ctx.fill()


def bricks(ctx, x0, y0, w, h, frac, col=(0.72, 0.3, 0.22)):
    rows = 12; bh = h / rows; bw = w / 4
    n = frac * rows
    ctx.save(); ctx.rectangle(x0, y0, w, h); ctx.clip()
    for r in range(rows):
        if r >= n: break
        y = y0 + h - (r + 1) * bh
        off = (r % 2) * bw / 2
        for c in range(-1, 5):
            rrect(ctx, x0 + c * bw + off + 3, y + 3, bw - 6, bh - 6, 4)
            shade = 0.85 + 0.15 * hrand("br", r, c)
            ctx.set_source_rgb(col[0] * shade, col[1] * shade, col[2] * shade); ctx.fill()
    ctx.restore()


def tape(ctx, cx, cy, length, rot, a=1.0):
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot)
    ctx.rectangle(-length / 2, -24, length, 48); ctx.set_source_rgba(*YEL, a); ctx.fill()
    for k in range(-3, 4):
        text(ctx, "DO NOT OPEN", k * 230, 0, 30, (0.05, 0.05, 0.1), shadow=False, alpha=a)
    ctx.restore()


# ---------------------------------------------------------------- what's behind the doors
def p_ocean(ctx, x, y, w, h, t):
    hz = y + h * 0.42
    g = cairo.LinearGradient(0, y, 0, hz); g.add_color_stop_rgb(0, 0.3, 0.65, 1.0); g.add_color_stop_rgb(1, 0.85, 0.92, 1.0)
    ctx.set_source(g); ctx.rectangle(x, y, w, hz - y); ctx.fill()
    glow_circle(ctx, x + w * 0.7, y + h * 0.18, w * 0.35, (1, 0.95, 0.6), 0.6)
    ctx.arc(x + w * 0.7, y + h * 0.18, w * 0.08, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.6); ctx.fill()
    g = cairo.LinearGradient(0, hz, 0, y + h); g.add_color_stop_rgb(0, 0.05, 0.4, 0.8); g.add_color_stop_rgb(1, 0.02, 0.12, 0.42)
    ctx.set_source(g); ctx.rectangle(x, hz, w, y + h - hz); ctx.fill()
    for k in range(9):
        yy = hz + 12 + k * (h * 0.58) / 9
        ctx.move_to(x, yy)
        xx = x
        while xx <= x + w:
            ctx.line_to(xx, yy + (4 + k) * math.sin(xx * 0.03 + t * (2 + k * 0.3) + k)); xx += 12
        ctx.set_source_rgba(1, 1, 1, 0.25 + 0.04 * k); ctx.set_line_width(2 + k * 0.6); ctx.stroke()
    # a big wave rolling toward the doorway
    cy = y + h * 0.82
    ctx.move_to(x, y + h); xx = x
    while xx <= x + w:
        ctx.line_to(xx, cy - 28 * math.sin(xx * 0.02 + t * 3)); xx += 10
    ctx.line_to(x + w, y + h); ctx.close_path(); ctx.set_source_rgba(0.1, 0.5, 0.9, 0.9); ctx.fill()
    ctx.move_to(x, cy); xx = x
    while xx <= x + w:
        ctx.line_to(xx, cy - 28 * math.sin(xx * 0.02 + t * 3)); xx += 10
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(9); ctx.stroke()


def p_kitchen(ctx, x, y, w, h, t, freeze=False):
    ctx.set_source_rgb(1.0, 0.86, 0.55); ctx.rectangle(x, y, w, h); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(2)
    for k in range(12):
        ctx.move_to(x, y + k * h / 12); ctx.line_to(x + w, y + k * h / 12); ctx.stroke()
    rrect(ctx, x + w * 0.62, y + h * 0.08, w * 0.3, h * 0.28, 10); ctx.set_source_rgb(0.6, 0.85, 1.0); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(6); ctx.rectangle(x + w * 0.62, y + h * 0.08, w * 0.3, h * 0.28); ctx.stroke()
    ph = h * 0.8
    px, pfy = x + w * 0.5, y + h * 0.98
    person(ctx, px, pfy, ph, GRN, "shock" if freeze else "smile", "down", t, look=-0.6 if freeze else 0)
    mustache(ctx, px, pfy, ph, -0.6 if freeze else 0)
    u = ph / 100
    ty = y + h * 0.72
    ctx.rectangle(x - 10, ty, w + 20, h * 0.06); ctx.set_source_rgb(0.65, 0.4, 0.22); ctx.fill()
    # cereal box
    bx = x + w * 0.16
    rrect(ctx, bx - w * 0.08, ty - h * 0.3, w * 0.16, h * 0.3, 6); ctx.set_source_rgb(*RED); ctx.fill()
    ctx.save(); ctx.translate(bx, ty - h * 0.15); ctx.rotate(-math.pi / 2)
    text(ctx, "CEREAL", 0, 0, w * 0.06, WHT, shadow=False); ctx.restore()
    # bowl + spoon going to the mouth
    bwx = px + 4 * u
    ctx.save(); ctx.translate(bwx, ty); ctx.scale(1, 0.5); ctx.arc(0, 0, 16 * u, 0, math.pi); ctx.restore()
    ctx.set_source_rgb(1, 1, 1); ctx.fill()
    for k in range(7):
        ctx.arc(bwx - 11 * u + k * 3.6 * u, ty - 1.5 * u, 2 * u, 0, 6.3); ctx.set_source_rgb(0.95, 0.65, 0.2); ctx.fill()
    ph_ = 0.5 if freeze else 0.5 + 0.5 * math.sin(t * 7)
    sx, sy = px + 14 * u, ty - 6 * u - ph_ * 20 * u
    ctx.set_line_width(2.5 * u); ctx.set_source_rgb(0.8, 0.82, 0.88)
    ctx.move_to(px + 22 * u, ty - 2 * u); ctx.line_to(sx, sy); ctx.stroke()
    ctx.set_line_width(7 * u); ctx.set_source_rgb(*SKIN); ctx.move_to(px + 17 * u, pfy - 66 * u); ctx.line_to(sx + 3 * u, sy + 4 * u); ctx.stroke()


def p_roof(ctx, x, y, w, h, t):
    g = cairo.LinearGradient(0, y, 0, y + h); g.add_color_stop_rgb(0, 0.02, 0.03, 0.15); g.add_color_stop_rgb(1, 0.25, 0.12, 0.4)
    ctx.set_source(g); ctx.rectangle(x, y, w, h); ctx.fill()
    for k in range(25):
        ctx.arc(x + hrand("rs", k) * w, y + hrand("ry", k) * h * 0.4, 2, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.7); ctx.fill()
    ctx.arc(x + w * 0.25, y + h * 0.15, w * 0.07, 0, 6.3); ctx.set_source_rgb(1, 0.96, 0.8); ctx.fill()
    for k in range(9):
        bx = x + k * w / 8 - 20; bw = w / 8 - 6; bh = h * (0.25 + 0.2 * hrand("bh", k)); by = y + h * 0.95 - bh
        ctx.rectangle(bx, by, bw, bh); ctx.set_source_rgb(0.08, 0.06, 0.18); ctx.fill()
        for r in range(int(bh / 26)):
            for c in range(3):
                if hrand("w", k, r, c) > 0.45:
                    ctx.rectangle(bx + 8 + c * bw / 3.3, by + 10 + r * 26, 10, 12); ctx.set_source_rgba(1, 0.85, 0.4, 0.9); ctx.fill()
    ctx.rectangle(x, y + h * 0.9, w, h * 0.1); ctx.set_source_rgb(0.45, 0.45, 0.55); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(3)
    for k in range(10):
        lx = x + ((hrand("wl", k) * w + t * 900) % (w + 200)) - 100
        ly = y + h * (0.2 + 0.6 * hrand("wy", k))
        ctx.move_to(lx, ly); ctx.line_to(lx - 90, ly); ctx.stroke()


def p_hospital(ctx, x, y, w, h, t):
    ctx.set_source_rgb(0.82, 0.95, 0.95); ctx.rectangle(x, y, w, h); ctx.fill()
    ctx.set_source_rgb(0.7, 0.85, 0.88); ctx.rectangle(x, y + h * 0.78, w, h * 0.22); ctx.fill()
    ctx.set_source_rgb(*RED)
    ctx.rectangle(x + w * 0.12, y + h * 0.12, w * 0.16, w * 0.05); ctx.fill(); ctx.rectangle(x + w * 0.175, y + h * 0.12 - w * 0.055, w * 0.05, w * 0.16); ctx.fill()
    rrect(ctx, x + w * 0.1, y + h * 0.62, w * 0.6, h * 0.12, 10); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.arc(x + w * 0.2, y + h * 0.6, w * 0.07, 0, 6.3); ctx.set_source_rgb(*SKIN); ctx.fill()
    for s in (-1, 1):
        ctx.arc(x + w * 0.2 + s * w * 0.025, y + h * 0.595, w * 0.012, 0, 6.3); ctx.set_source_rgb(0.1, 0.1, 0.1); ctx.fill()
    rrect(ctx, x + w * 0.6, y + h * 0.25, w * 0.32, h * 0.2, 12); ctx.set_source_rgb(0.08, 0.1, 0.12); ctx.fill()
    ctx.set_source_rgb(*GRN); ctx.set_line_width(4)
    mx0, my = x + w * 0.62, y + h * 0.35
    ctx.move_to(mx0, my)
    for k in range(40):
        xx = mx0 + k * w * 0.007
        ph = (k * 0.1 - t * 2) % 1
        yy = my - (h * 0.06 if 0.45 < ph < 0.5 else 0) + (h * 0.03 if 0.5 < ph < 0.55 else 0)
        ctx.line_to(xx, yy)
    ctx.stroke()


def p_forest(ctx, x, y, w, h, t):
    g = cairo.LinearGradient(0, y, 0, y + h); g.add_color_stop_rgb(0, 0.02, 0.08, 0.06); g.add_color_stop_rgb(1, 0.05, 0.2, 0.12)
    ctx.set_source(g); ctx.rectangle(x, y, w, h); ctx.fill()
    for layer, (sc, col) in enumerate(((0.6, (0.06, 0.2, 0.12)), (0.85, (0.03, 0.13, 0.08)), (1.1, (0.01, 0.06, 0.04)))):
        for k in range(5):
            tx = x + (k + 0.5 * layer) * w / 4 - 30
            th = h * 0.55 * sc
            ctx.move_to(tx, y + h - th - 60 * sc); ctx.line_to(tx + 70 * sc, y + h); ctx.line_to(tx - 70 * sc, y + h); ctx.close_path()
            ctx.set_source_rgb(*col); ctx.fill()
    blink = (t * 0.9) % 1 < 0.9
    if blink:
        for s in (-1, 1):
            glow_circle(ctx, x + w * 0.55 + s * 22, y + h * 0.48, 30, YEL, 0.6)
            ctx.arc(x + w * 0.55 + s * 22, y + h * 0.48, 8, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()
    ctx.set_source_rgba(0.7, 0.85, 0.8, 0.12); ctx.rectangle(x, y + h * 0.7, w, h * 0.3); ctx.fill()


# ---------------------------------------------------------------- scenes
def flood(ctx, f, t):
    if f <= 0: return
    top = 1250 - 40 * f
    ctx.move_to(0, top)
    for xx in range(0, W + 20, 20):
        ctx.line_to(xx, top + 6 * math.sin(xx * 0.03 + t * 5))
    ctx.line_to(W, H); ctx.line_to(0, H); ctx.close_path()
    ctx.set_source_rgba(0.2, 0.55, 1.0, 0.55); ctx.fill()


def s0(ctx, tg, tl, T):
    """hook: bedroom door already ajar on blue light; it swings open onto the ocean, water pours in"""
    top = wt(0, "open"); toc = wt(0, "ocean")
    z = 1 + 0.1 * ease_io(tl / T)
    ctx.translate(540, 860); ctx.scale(z, z); ctx.translate(-540, -860)
    room(ctx, dark=0.3)
    # bed in the corner
    rrect(ctx, -40, 1080, 260, 170, 20); ctx.set_source_rgb(0.25, 0.3, 0.7); ctx.fill()
    rrect(ctx, -40, 1040, 200, 70, 25); ctx.set_source_rgb(0.9, 0.9, 1); ctx.fill()
    op = 0.45 + 0.55 * ease_out((tl - top) / 0.35) if tl > top else 0.45
    door(ctx, 700, 1250, 400, 740, op, p_ocean, tg, glow=OCEAN_GLOW)
    flood(ctx, 0.25 if tl < toc - 0.5 else 0, tl)
    if tl > toc - 0.5:
        f = ease_out((tl - toc + 0.5) / 0.7)
        # water spilling over the threshold
        for k in range(30):
            ph = ((tl * 1.8) + hrand("sp", k)) % 1
            px = 520 + 360 * hrand("sx", k) + (hrand("sv", k) - 0.5) * 500 * ph
            py = 1250 - 200 * math.sin(ph * math.pi) * hrand("sh", k)
            ctx.arc(px, py, 6 + 8 * hrand("sr", k), 0, 6.3); ctx.set_source_rgba(0.75, 0.92, 1, 0.85 * f); ctx.fill()
        flood(ctx, f, tl)
    awake = tl > top - 0.05
    lean = 12 * math.sin(tl * 30) * math.exp(-(tl - top) * 3) if awake else 0
    hero(ctx, 270 + lean, 1300, 740, "shock" if awake else "worry", "up" if awake else "down", tl, look=1.0)
    if awake:
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(4)
        for k in range(6):
            lx = 500 - ((tl * 700 + k * 130) % 520); ly = 600 + k * 90
            ctx.move_to(lx, ly); ctx.line_to(lx - 70, ly); ctx.stroke()
    if tl > toc - 0.05:
        stamp(ctx, "SPLASH!", 720, 560, tl - toc + 0.05, CYN, 92, -0.1, fg=(0, 0, 0))


def s1(ctx, tg, tl, T):
    """slam it, open again: a stranger's kitchen. He's eating your cereal."""
    tsl = wt(1, "Slam"); top = wt(1, "Open"); tki = wt(1, "kitchen"); thes = wt(1, "He's"); tce = wt(1, "cereal")
    if tl < thes - 0.12:
        room(ctx, dark=0.2)
        shake = 0
        if tl < tsl + 0.14:
            op = 1 - clamp((tl - tsl) / 0.14); portal = p_ocean; glow = OCEAN_GLOW
        elif tl < top:
            op = 0; portal = None; glow = None
            shake = 16 * math.exp(-(tl - tsl - 0.14) * 10) * math.sin(tl * 80)
        else:
            op = ease_out((tl - top) / 0.3); portal = p_kitchen; glow = WARM
        door(ctx, 700, 1250, 400, 740, op, portal, tg, glow=glow, shake=shake)
        flood(ctx, 1 - clamp((tl - 0.3) / 0.8), tl)
        pushing = tl < top
        hero(ctx, 300 + (40 if pushing else 0), 1300, 740, "worry" if pushing else "shock", "run" if pushing else "cheeks", tl, look=1.0)
        if tsl + 0.12 < tl < top + 0.1:
            stamp(ctx, "SLAM!", 700, 560, tl - tsl - 0.12, RED, 120, -0.1)
        if tl > tki - 0.05:
            popchip(ctx, "WRONG HOUSE", 700, 520, tl - tki + 0.05, YEL, (0, 0, 0), 70)
    else:
        tt = tl - thes + 0.12
        s = 1.0 + 0.06 * ease_out(tt / 0.3)
        ctx.save(); ctx.translate(540, 860); ctx.scale(s, s); ctx.translate(-540, -860)
        p_kitchen(ctx, 0, 440, 1080, 820, tg, freeze=tl > tce - 0.1)
        ctx.restore()
        # you, peeking in from the doorway on the left
        ctx.save(); ctx.rectangle(0, 440, 1080, 900); ctx.clip()
        ctx.set_source_rgb(*WOOD); ctx.rectangle(0, 440, 90, 820); ctx.fill()
        hero(ctx, 30, 1420, 900, "worry", "down", tl, look=1.0)
        ctx.restore()
        if tl > tce - 0.05:
            stamp(ctx, "THAT'S YOUR CEREAL", 600, 540, tl - tce + 0.05, RED, 70, -0.06)


def s2(ctx, tg, tl, T):
    """every door on Earth broke, then whip-cuts: rooftop, hospital, forest"""
    tev = wt(2, "Every"); tbr = wt(2, "broke"); tro = wt(2, "Rooftops"); tho = wt(2, "Hospitals"); tfo = wt(2, "Forests")
    if tl < tro - 0.08:
        s = pop(tl, 0.3)
        ctx.save(); ctx.translate(540, 830); ctx.scale(s, s); ctx.translate(-540, -830)
        earth(ctx, 540, 830, 290, tl)
        cols = [OCEAN_GLOW, WARM, GRN, PNK, CYN, YEL]
        for k in range(12):
            t0 = tev + 0.08 * k
            if tl < t0: continue
            a = k * 2.4
            r = 290 * (0.35 + 0.6 * hrand("dr", k))
            dx, dy = 540 + math.cos(a) * r, 830 + math.sin(a) * r
            ps = pop(tl - t0, 0.18)
            ctx.save(); ctx.translate(dx, dy); ctx.scale(ps, ps)
            glow_circle(ctx, 0, 0, 60, cols[k % 6], 0.5)
            rrect(ctx, -22, -36, 44, 72, 4); ctx.set_source_rgb(*cols[k % 6]); ctx.fill()
            ctx.rectangle(-22, -36, 14, 72); ctx.set_source_rgb(*WOOD); ctx.fill()
            ctx.restore()
        if tl > tbr:
            f = ease_out((tl - tbr) / 0.2)
            ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(6)
            for k in range(5):
                a = k * 1.25 + 0.3
                ctx.move_to(540, 830)
                for j in range(1, 6):
                    rr = 300 * f * j / 5
                    ctx.line_to(540 + math.cos(a + (hrand("ck", k, j) - 0.5) * 0.5) * rr, 830 + math.sin(a + (hrand("ck2", k, j) - 0.5) * 0.5) * rr)
                ctx.stroke()
        ctx.restore()
        stamp(ctx, "BROKEN", 540, 1180, tl - tbr, RED, 110, -0.08)
    else:
        if tl < tho - 0.08:
            t0, portal, glow, lab, ex = tro, p_roof, (0.6, 0.5, 1.0), "ROOFTOP", "shock"
        elif tl < tfo - 0.08:
            t0, portal, glow, lab, ex = tho, p_hospital, (0.7, 1.0, 1.0), "HOSPITAL", "worry"
        else:
            t0, portal, glow, lab, ex = tfo, p_forest, GRN, "FOREST", "shock"
        tt = tl - t0 + 0.08
        room(ctx, dark=0.2)
        door(ctx, 600, 1250, 600, 790, ease_out(tt / 0.18), portal, tg, glow=glow)
        hero(ctx, 150, 1330, 700, ex, "up" if lab != "HOSPITAL" else "cheeks", tl, look=1.0)
        popchip(ctx, lab, 640, 520, tt - 0.05, WHT, (0, 0, 0), 66)


def s3(ctx, tg, tl, T):
    """day three: every door taped shut; you back away"""
    tda = wt(3, "Day"); tno = wt(3, "nobody")
    room(ctx, dark=0.15)
    for k, cx in enumerate((210, 540, 870)):
        door(ctx, cx, 1200, 270, 560, 0)
        for j, rot in enumerate((0.55, -0.55)):
            t0 = 0.15 + k * 0.18 + j * 0.09
            if tl > t0:
                ln = 420 * ease_out((tl - t0) / 0.18)
                ctx.save(); ctx.rectangle(cx - 150, 600, 300, 620); ctx.clip()
                tape(ctx, cx, 920, ln, rot)
                ctx.restore()
    # day counter flipping 1 -> 3
    n = 1 + min(2, int(clamp((tl - tda) / 0.5) * 3)) if tl > tda else 1
    s = pop(tl - tda, 0.2)
    ctx.save(); ctx.translate(540, 525); ctx.scale(s, s)
    rrect(ctx, -170, -95, 340, 190, 26); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    rrect(ctx, -170, -95, 340, 60, 26); ctx.set_source_rgb(*RED); ctx.fill()
    ctx.rectangle(-170, -55, 340, 20); ctx.fill()
    text(ctx, f"DAY {n}", 0, 30, 110, (0.1, 0.1, 0.2), shadow=False)
    ctx.restore()
    back = ease_out((tl - tno + 0.2) / 0.6) if tl > tno - 0.2 else 0
    hero(ctx, 540 - 30 * back, 1420 + 30 * back, 760, "worry", "cheeks" if tl > tno else "down", tl, look=math.sin(tl * 8) if tl > tno else 0)
    if tl > tno:
        popchip(ctx, "NOPE.", 840, 1150, tl - tno, YEL, (0, 0, 0), 80)


def skyline_bg(ctx, tg):
    g = cairo.LinearGradient(0, 440, 0, 1300); g.add_color_stop_rgb(0, 0.04, 0.05, 0.2); g.add_color_stop_rgb(1, 0.25, 0.1, 0.35)
    ctx.set_source(g); ctx.rectangle(0, 440, W, 900); ctx.fill()
    for k in range(11):
        bx = k * 105 - 30; bh = 260 + 280 * hrand("sk", k)
        ctx.rectangle(bx, 1250 - bh, 95, bh); ctx.set_source_rgb(0.1, 0.08, 0.22); ctx.fill()
        for r in range(int(bh / 40)):
            for c in range(3):
                if hrand("sw", k, r, c) > 0.5:
                    ctx.rectangle(bx + 12 + c * 28, 1250 - bh + 16 + r * 40, 14, 18); ctx.set_source_rgba(1, 0.85, 0.4, 0.8); ctx.fill()


def s4(ctx, tg, tl, T):
    """cities brick up every door; we use windows now"""
    tbr = wt(4, "brick"); twe = wt(4, "We")
    if tl < twe - 0.1:
        skyline_bg(ctx, tg)
        rrect(ctx, 220, 560, 640, 760, 10); ctx.set_source_rgb(0.3, 0.22, 0.38); ctx.fill()
        door(ctx, 540, 1250, 400, 600, 0)
        f = clamp((tl - tbr + 0.15) / 1.0)
        bricks(ctx, 340, 650, 400, 600, f)
        if f >= 1:
            stamp(ctx, "SEALED", 540, 900, tl - (tbr + 0.85), RED, 110, -0.1)
        for k, x in enumerate((60, 1000)):
            ctx.save(); ctx.translate(x, 1250); ctx.scale(0.6, 0.6)
            ctx.rectangle(-60, -300, 120, 300); ctx.set_source_rgb(0.2, 0.15, 0.3); ctx.fill()
            ctx.restore()
            bricks(ctx, x - 36, 1070, 72, 180, 1.0)
    else:
        tt = tl - twe + 0.1
        ctx.set_source_rgb(0.3, 0.22, 0.38); ctx.rectangle(0, 440, W, 900); ctx.fill()
        for r in range(9):
            for c in range(6):
                ctx.rectangle(c * 190 + (r % 2) * 95 - 40, 440 + r * 100, 180, 92); ctx.set_source_rgba(1, 1, 1, 0.03); ctx.fill()
        # window with you climbing through
        wx, wy, ww, wh = 330, 560, 520, 470
        ctx.rectangle(wx, wy, ww, wh); ctx.set_source_rgb(0.95, 0.85, 0.55); ctx.fill()
        ctx.save(); ctx.rectangle(wx, wy, ww, wh + 400); ctx.clip()
        ctx.save(); ctx.translate(560, 1180); ctx.rotate(0.35 - 0.1 * ease_out(tt / 0.6)); ctx.translate(-560, -1180)
        hero(ctx, 560, 1180, 720, "cheeks", "up", tl, look=-0.5)
        ctx.restore(); ctx.restore()
        ctx.set_source_rgb(0.92, 0.9, 0.96); ctx.set_line_width(26); ctx.rectangle(wx, wy, ww, wh); ctx.stroke()
        ctx.set_line_width(12); ctx.move_to(wx + ww / 2, wy); ctx.line_to(wx + ww / 2, wy + wh * 0.45); ctx.stroke()
        rrect(ctx, wx - 40, wy + wh, ww + 80, 40, 8); ctx.set_source_rgb(0.95, 0.93, 0.98); ctx.fill()
        # a leg over the sill
        ctx.set_line_width(65); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(0.15, 0.17, 0.3)
        ctx.move_to(640, wy + wh - 30); ctx.line_to(760, wy + wh + 160); ctx.stroke()
        door(ctx, 140, 1250, 200, 360, 0)
        bricks(ctx, 40, 890, 200, 360, 1.0)
        popchip(ctx, "WINDOWS ONLY", 600, 1180, tt - 0.25, YEL, (0, 0, 0), 70)


def street(ctx, tg, z):
    """a long street of bricked doors with one glowing door at the end"""
    ctx.save(); ctx.translate(540, 820); ctx.scale(z, z); ctx.translate(-540, -820)
    g = cairo.LinearGradient(0, 440, 0, 1300); g.add_color_stop_rgb(0, 0.03, 0.03, 0.12); g.add_color_stop_rgb(1, 0.12, 0.06, 0.2)
    ctx.set_source(g); ctx.rectangle(-500, 0, 2100, 2000); ctx.fill()
    vx, vy = 540, 800
    ctx.move_to(-500, 1700); ctx.line_to(vx - 60, vy + 120); ctx.line_to(vx + 60, vy + 120); ctx.line_to(1600, 1700); ctx.close_path()
    ctx.set_source_rgb(0.1, 0.08, 0.16); ctx.fill()
    for k in range(7, -1, -1):
        s = 1.0 / (1 + k * 0.55)
        for side in (-1, 1):
            cx = vx + side * 470 * s; fy = vy + 120 + 560 * s
            w, h = 170 * s, 330 * s
            ctx.rectangle(cx - w / 2 - 14 * s, fy - h - 14 * s, w + 28 * s, h + 14 * s); ctx.set_source_rgb(0.3, 0.26, 0.38); ctx.fill()
            bricks(ctx, cx - w / 2, fy - h, w, h, 1.0, col=(0.5, 0.22, 0.2))
    # the one door that still leads home
    fy = vy + 120; w, h = 120, 230
    glow_circle(ctx, vx, fy - h / 2, 300, WARM, 0.55 + 0.1 * math.sin(tg * 6))
    door(ctx, vx, fy, w, h, 0, leak=(0.9, WARM), leaf=(0.42, 0.25, 0.16))
    ctx.restore()


def s5(ctx, tg, tl, T):
    """one door still leads home; everyone's too scared to open it"""
    tho = wt(5, "home"); tev = wt(5, "Everyone"); tsc = wt(5, "scared")
    z = 1 + 0.35 * ease_io(tl / T)
    street(ctx, tg, z)
    if tl > tho - 0.05:
        popchip(ctx, "IT LEADS HOME", 540, 520, tl - tho + 0.05, GRN, (0, 0, 0), 70)
    if tl > tev - 0.1:
        tt = tl - tev + 0.1
        for k in range(7):
            x = 90 + k * 150; tr = 4 * math.sin(tl * 30 + k)
            person(ctx, x + tr, 1330 + 40 * (k % 2), 430, SHIRTS[k % 6], "worry" if k % 2 else "shock", "cheeks" if k % 3 == 0 else "down", tl, look=0)
        ctx.set_source_rgba(0.02, 0.0, 0.08, 0.35); ctx.rectangle(0, 900, W, 500); ctx.fill()
    if tl > tsc - 0.05:
        stamp(ctx, "NOBODY OPENS IT", 540, 680, tl - tsc + 0.05, RED, 84, -0.06)


def s6(ctx, tg, tl, T):
    """tonight it's in your house... and it just knocked"""
    tho = wt(6, "house"); tkn = wt(6, "knocked")
    room(ctx, dark=0.65)
    knocks = [tkn - 0.05, tkn + 0.22, tkn + 0.49]
    sh = sum(14 * math.exp(-(tl - k) * 14) * math.sin((tl - k) * 90) for k in knocks if tl > k)
    appear = ease_out((tl - tho + 0.3) / 0.6) if tl > tho - 0.3 else 0
    leak_a = 0.0 if tl > knocks[-1] + 0.15 else 0.9 * appear * (0.8 + 0.2 * math.sin(tl * 9))
    if appear > 0:
        ctx.save(); ctx.push_group()
        glow_circle(ctx, 760, 900, 380, WARM, 0.35 * (leak_a / 0.9 if appear else 0))
        door(ctx, 760, 1250, 330, 640, 0, shake=sh, leak=(leak_a, WARM), leaf=(0.42, 0.25, 0.16))
        ctx.pop_group_to_source(); ctx.paint_with_alpha(appear); ctx.restore()
    # you, with a phone torch
    hx = 260
    ctx.move_to(hx + 90, 950); ctx.line_to(1000, 760); ctx.line_to(1000, 1180); ctx.close_path()
    ctx.set_source_rgba(1, 1, 0.85, 0.12); ctx.fill()
    scared = tl > knocks[0]
    hero(ctx, hx, 1330, 760, "shock" if scared else "worry", "up" if scared else "down", tl, look=1.0)
    rrect(ctx, hx + 70, 930, 34, 56, 6); ctx.set_source_rgb(0.1, 0.1, 0.12); ctx.fill()
    for j, k in enumerate(knocks):
        if tl > k:
            stamp(ctx, "KNOCK", 760 + (j - 1) * 150, 560 + j * 70, tl - k, RED, 80, -0.12 + j * 0.1)
    g = cairo.RadialGradient(540, 860, 300, 540, 860, 1100)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.4, 0, 0.05, 0.5)
    ctx.set_source(g); ctx.paint()


def s7(ctx, tg, tl, T):
    """door one, two or three? follow for part two"""
    tfo = wt(7, "Follow")
    room(ctx, dark=0.25)
    sh3 = 5 * math.sin(tl * 40) * (math.sin(tl * 3) > 0.3)
    specs = [(205, p_ocean, OCEAN_GLOW, 0.32, None), (540, p_kitchen, WARM, 0.32, None), (875, None, None, 0.0, (0.9, WARM))]
    for k, (cx, portal, glow, op, leak) in enumerate(specs):
        t0 = 0.1 + 0.25 * k
        ps = pop(tl - t0, 0.2)
        ctx.save(); ctx.translate(cx, 1150); ctx.scale(ps, ps); ctx.translate(-cx, -1150)
        door(ctx, cx, 1150, 270, 560, op, portal, tg, glow=glow, shake=sh3 if k == 2 else 0, leak=leak,
             leaf=(0.42, 0.25, 0.16) if k == 2 else WOOD)
        ctx.arc(cx, 590, 52 * ps, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()
        if ps > 0.3: text(ctx, str(k + 1), cx, 590, 72 * ps, (0.05, 0.05, 0.15), shadow=False)
        ctx.restore()
    if tl < tfo - 0.1:
        pass
    else:
        sc = pop(tl - tfo + 0.1, 0.25) * (1 + 0.04 * math.sin(tl * 8))
        ctx.save(); ctx.translate(540, 455); ctx.scale(sc, sc)
        g = cairo.LinearGradient(-330, 0, 330, 0)
        g.add_color_stop_rgb(0, 0.15, 0.55, 1.0); g.add_color_stop_rgb(1, 0.95, 0.25, 0.6)
        tw = text_w(ctx, "FOLLOW FOR PART 2", DISPLAY, 84)
        rrect(ctx, -tw / 2 - 50, -66, tw + 100, 132, 66); ctx.set_source(g); ctx.fill()
        text(ctx, "FOLLOW FOR PART 2", 0, 0, 84, WHT, shadow=False)
        ctx.restore()


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7]


# ---------------------------------------------------------------- sound
def _waves(A, t0, t1, g=0.25):
    d = t1 - t0; n = int(d * SR); tt = np.arange(n) / SR
    x = A.lp(A.noise(d), 900) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.35 * tt) ** 2)
    e = np.ones(n); f = int(0.15 * SR); e[:f] = np.linspace(0, 1, f); e[-f:] = np.linspace(1, 0, f)
    A.add(A.sfx_buf, x * e * 2.5, t0, g)


def _crash(A, t, g=0.5, d=1.4):
    n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.lp(A.noise(d), 2500) * np.exp(-tt * 2.5) * 2, t, g)


def _creak(A, t, d=0.45, g=0.12):
    n = int(d * SR); tt = np.arange(n) / SR
    f = 380 + 260 * tt / d
    A.add(A.sfx_buf, np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * tt)) * np.sin(np.pi * tt / d), t, g)


def _crunch(A, t, g=0.12):
    d = 0.09; n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.hp(A.noise(d), 2000) * np.exp(-tt * 40), t, g)


def _knock(A, t, g=0.8):
    d = 0.25; n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 28) + A.lp(A.noise(d), 1200) * np.exp(-tt * 45), t, g)


def _wind(A, t, d=0.7, g=0.18):
    n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.bp(A.noise(d), 300, 1800) * np.sin(np.pi * tt / d) * 2, t, g)


def _murmur(A, t, d=1.8, g=0.12):
    n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.bp(A.noise(d), 200, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * tt)) * np.sin(np.pi * tt / d) * 2, t, g)


def sfx(A):
    W_, S = A.W, A.S
    A.whoosh(0.15, 0.2, 0.4)
    _waves(A, 0.0, S(1) + 0.3, 0.22)
    _creak(A, W_(0, "open") - 0.05, 0.4, 0.15)
    _crash(A, W_(0, "ocean") - 0.1, 0.55)
    A.thump(W_(1, "Slam") + 0.14, 0.9, 60); A.scratch(W_(1, "Slam") + 0.12, 0.3, 0.2)
    _creak(A, W_(1, "Open"), 0.35, 0.12)
    for k in range(6):
        _crunch(A, W_(1, "Now") + 0.3 + k * 0.32, 0.14)
    A.scratch(W_(1, "He's") - 0.15, 0.3)
    A.boing(W_(1, "cereal") + 0.1, 0.15, 260, 0.45)
    for k in range(12):
        A.pop(W_(2, "Every") + 0.08 * k, 0.12)
    A.zap_down(W_(2, "broke"), 0.25, 0.8)
    A.thump(W_(2, "broke"), 0.6, 50)
    _wind(A, W_(2, "Rooftops") - 0.05, 0.7, 0.2)
    for k in range(3):
        A.ding(W_(2, "Hospitals") + k * 0.22, 0.08, 1000, 0.15)
    A.boing(W_(2, "Forests"), 0.12, 160, 0.6)
    for k in range(3):
        A.pop(W_(3, "Day") + k * 0.17, 0.2)
    A.thump(W_(3, "nobody"), 0.5, 70)
    for k in range(12):
        A.thump(W_(4, "brick") - 0.15 + k * 0.085, 0.3, 100 + 10 * (k % 3))
    A.thump(W_(4, "door") + 0.35, 0.7, 55)
    _creak(A, W_(4, "We") - 0.05, 0.5, 0.12)
    A.thump(S(5), 0.6, 45)
    _murmur(A, W_(5, "Everyone") - 0.1, 1.9, 0.12)
    A.thump(W_(5, "scared"), 0.6, 50)
    for k in range(4):
        A.thump(S(6) + 0.3 + k * 0.62, 0.35, 48)            # slow heartbeat
    t_k = W_(6, "knocked")
    for k, dt in enumerate((-0.05, 0.22, 0.49)):
        _knock(A, t_k + dt, 0.9)
    A.music_level(W_(6, "house") + 0.3, t_k + 0.9, 0.0)
    for k in range(3):
        A.pop(S(7) + 0.1 + 0.25 * k, 0.3)
    for k, m in enumerate((76, 79, 84)):
        A.ding(W_(7, "Follow") + 0.05 + k * 0.1, 0.07, A.note(m))

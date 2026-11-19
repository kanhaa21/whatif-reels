"""Scenes for "What if you became invisible for a day?". One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
The invisible hero is drawn see-through (faint body + dashed glowing outline) so the face stays readable."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

BG = lambda ctx, tg, i: bg_glow(ctx, tg, i, dark_scenes=(0, 4))
MUSIC = {"beat_from_scene": 2, "bpm": 112}   # tense drone for the hook and the promise, beat from problem one

HERO_SHIRT = SHIRTS[1]
DOGC = [(0.85, 0.6, 0.3), (0.55, 0.38, 0.22), (0.92, 0.88, 0.8)]


def wi(i, k):
    """scene-local start time of the k-th word of line i"""
    return TL["lines"][i]["words"][k]["s"] - TL["scenes"][i]["t0"]


CUTS = {}


def cut_times(i):
    if not CUTS:
        CUTS.update({
            2: [0, wt(2, "Invisible") - 0.08, wt(2, "Not") - 0.08],
            3: [0, wt(3, "Every") - 0.08],
            4: [0, wt(4, "You") - 0.1],
            5: [0, wt(5, "Invisible") - 0.1, wt(5, "You're") - 0.08],
            6: [0, wt(6, "Can't") - 0.08],
            7: [0, wt(7, "Send") - 0.08],
        })
    return CUTS.get(i, [0])


# ---------------------------------------------------------------- characters
def ellipse(ctx, x, y, rx, ry, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(rx, ry); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore()


def ghost(ctx, x, y, h, expr="smile", arms="down", t=0.0, vis=0.0, look=0.0, shirt=HERO_SHIRT):
    """the invisible hero: vis=1 fully visible, vis=0 see-through (faint body, glowing dashed outline)"""
    a = 0.45 + 0.55 * vis
    ctx.push_group()
    person(ctx, x, y, h, shirt, expr, arms, t, look=look)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    oa = 1 - vis
    if oa <= 0.01: return
    u = h / 100
    ctx.save()
    ctx.set_dash([5 * u, 3.5 * u], (t * 30 * u) % (8.5 * u))
    ctx.set_line_width(1.6 * u); ctx.set_source_rgba(*CYN, 0.9 * oa)
    ctx.arc(x, y - 86 * u, 16.5 * u, 0, 6.3); ctx.stroke()
    rrect(ctx, x - 20.5 * u, y - 73.5 * u, 41 * u, 39 * u, 13 * u); ctx.stroke()
    ctx.restore()
    for k in range(8):
        ph = (t * 0.7 + hrand("gs", k)) % 1
        sx = x + (hrand("gx", k) - 0.5) * 70 * u; sy = y - 20 * u - ph * 90 * u
        ctx.arc(sx, sy, (1 + 1.5 * hrand("gr", k)) * u * 0.6, 0, 6.3)
        ctx.set_source_rgba(0.8, 0.95, 1, 0.8 * oa * math.sin(ph * math.pi)); ctx.fill()


def boss(ctx, x, y, h, t, look=0.0, expr="worry"):
    person(ctx, x, y, h, (0.2, 0.22, 0.3), expr, "down", t, look=look)
    u = h / 100
    ctx.move_to(x - 3 * u, y - 71 * u); ctx.line_to(x + 3 * u, y - 71 * u); ctx.line_to(x + 4 * u, y - 52 * u)
    ctx.line_to(x, y - 48 * u); ctx.line_to(x - 4 * u, y - 52 * u); ctx.close_path(); ctx.set_source_rgb(*RED); ctx.fill()
    ctx.set_line_width(1.2 * u); ctx.set_source_rgb(0.1, 0.1, 0.12)
    for s in (-1, 1):
        ctx.arc(x + s * 5.5 * u + look * 3 * u, y - 85 * u, 4.2 * u, 0, 6.3); ctx.stroke()


def checker(ctx, x, y, h, t, look=0.0, expr="worry"):
    person(ctx, x, y, h, (0.85, 0.2, 0.3), expr, "down", t, look=look)
    u = h / 100
    rrect(ctx, x - 16 * u, y - 104 * u, 32 * u, 9 * u, 3 * u); ctx.set_source_rgb(0.85, 0.2, 0.3); ctx.fill()
    rrect(ctx, x - 4 * u + look * 14 * u, y - 97 * u, 22 * u, 4 * u, 2 * u); ctx.fill()


def mosquito(ctx, x, y, s, t, rot=0.0, seed=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    fl = 0.35 + 0.65 * abs(math.sin(t * 70 + seed))
    for sx in (-1, 1):
        ctx.save(); ctx.translate(2, -6); ctx.rotate(sx * 0.5 - 0.3); ctx.scale(1, fl)
        ellipse(ctx, -6, -16, 9, 20, 0); ctx.set_source_rgba(0.85, 0.95, 1, 0.55); ctx.fill()
        ctx.restore()
    ctx.set_line_width(2); ctx.set_source_rgb(0.12, 0.1, 0.15)
    for k in range(3):
        ctx.move_to(-2 + k * 6, 2); ctx.line_to(-10 + k * 8, 18); ctx.line_to(-14 + k * 9, 24)
    ctx.stroke()
    ellipse(ctx, -16, 2, 17, 6, 0.15); ctx.set_source_rgb(0.25, 0.22, 0.3); ctx.fill()
    for k in range(3):
        ctx.rectangle(-26 + k * 7, -3, 2.5, 9); ctx.set_source_rgba(0.95, 0.95, 1, 0.8); ctx.fill()
    ctx.arc(4, 0, 6.5, 0, 6.3); ctx.set_source_rgb(0.2, 0.18, 0.25); ctx.fill()
    ctx.arc(13, -1, 4.5, 0, 6.3); ctx.fill()
    ctx.arc(14.5, -2.5, 1.6, 0, 6.3); ctx.set_source_rgb(*RED); ctx.fill()
    ctx.move_to(16, 0); ctx.line_to(30, 6); ctx.set_line_width(1.6); ctx.set_source_rgb(0.12, 0.1, 0.15); ctx.stroke()
    ctx.restore()


def dog(ctx, x, y, s, t, col=DOGC[0], bark=False, sniff=False, face=-1):
    """sitting street dog, feet centre at (x, y); face=-1 looks left, +1 right. ~260*s px tall"""
    ctx.save(); ctx.translate(x, y); ctx.scale(-face * s, s)   # drawn facing left (-x)
    dark = tuple(c * 0.6 for c in col)
    # tail
    w = math.sin(t * 12) * 0.4
    ctx.move_to(60, -50); ctx.curve_to(110, -70, 100 + 20 * w, -130, 90 + 30 * w, -150)
    ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(*col); ctx.stroke()
    # body + haunch
    ellipse(ctx, 15, -75, 62, 78, -0.25); ctx.set_source_rgb(*col); ctx.fill()
    ellipse(ctx, 40, -35, 45, 38); ctx.fill()
    # front legs
    for lx in (-38, -12):
        rrect(ctx, lx - 11, -95, 22, 95, 10); ctx.set_source_rgb(*col); ctx.fill()
        ellipse(ctx, lx - 6, -4, 17, 8); ctx.set_source_rgb(*dark); ctx.fill()
    # head
    bob = 3 * math.sin(t * 20) if sniff else 0
    hy = -175 + bob
    ctx.arc(-35, hy, 52, 0, 6.3); ctx.set_source_rgb(*col); ctx.fill()
    rrect(ctx, -128, hy - 12, 90, 46, 20); ctx.fill()
    ctx.arc(-126, hy - 2, 13, 0, 6.3); ctx.set_source_rgb(0.08, 0.06, 0.06); ctx.fill()
    ctx.arc(-130, hy - 6, 4, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    if bark:
        op = 0.5 + 0.5 * abs(math.sin(t * 14))
        ctx.move_to(-122, hy + 22); ctx.line_to(-50, hy + 22); ctx.line_to(-118, hy + 22 + 34 * op); ctx.close_path()
        ctx.set_source_rgb(0.45, 0.05, 0.1); ctx.fill()
        ellipse(ctx, -100, hy + 22 + 22 * op, 10, 7); ctx.set_source_rgb(1, 0.45, 0.55); ctx.fill()
    else:
        ctx.move_to(-120, hy + 26); ctx.line_to(-70, hy + 26); ctx.set_line_width(4); ctx.set_source_rgb(*dark); ctx.stroke()
    # eye + brow
    ctx.arc(-58, hy - 18, 9, 0, 6.3); ctx.set_source_rgb(0.08, 0.06, 0.06); ctx.fill()
    ctx.arc(-61, hy - 21, 3, 0, 6.3); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.move_to(-74, hy - 38 + (8 if bark else 0)); ctx.line_to(-44, hy - 32 - (6 if bark else 0))
    ctx.set_line_width(6); ctx.set_source_rgb(*dark); ctx.stroke()
    # floppy ear
    ellipse(ctx, -5, hy - 10, 20, 42, 0.35 + 0.1 * math.sin(t * 8)); ctx.set_source_rgb(*dark); ctx.fill()
    ctx.restore()


def bubble(ctx, x, y, s, txt, tt, col=PNK, tail=1):
    if tt < 0: return
    sc = pop(tt, 0.2)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    w = text_w(ctx, txt, DISPLAY, s) + 60
    rrect(ctx, -w / 2, -s * 0.75, w, s * 1.5, s * 0.5); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.move_to(tail * w * 0.12, s * 0.6); ctx.line_to(tail * w * 0.28, s * 1.4); ctx.line_to(tail * w * 0.3, s * 0.6); ctx.close_path(); ctx.fill()
    text(ctx, txt, 0, 0, s, col, shadow=False)
    ctx.restore()


def tiles(ctx, cur, tt):
    """1 2 3 progress row at the top; cur = active problem (0..2); slot 3 is the red one"""
    cols = [YEL, CYN, RED]
    for k in range(3):
        x = 540 + (k - 1) * 150
        on = k == cur
        s = (1.0 + 0.25 * (1 - ease_out(tt / 0.3))) if on else 0.8
        ctx.save(); ctx.translate(x, 455); ctx.scale(s * 0.85, s * 0.85)
        if on: glow_circle(ctx, 0, 0, 110, cols[k], 0.5)
        rrect(ctx, -55, -55, 110, 110, 22)
        ctx.set_source_rgb(*(cols[k] if k <= cur else (0.25, 0.25, 0.4))); ctx.fill()
        text(ctx, str(k + 1), 0, 0, 80, (0, 0, 0) if k <= cur else (0.6, 0.6, 0.75), shadow=False)
        ctx.restore()


# ---------------------------------------------------------------- props
def bedroom(ctx, tg, dark=0.0):
    room(ctx, dark=dark)
    rrect(ctx, 700, 520, 260, 300, 14); ctx.set_source_rgb(0.95, 0.75, 0.35); ctx.fill()      # window, morning sun
    ctx.set_source_rgb(0.45, 0.25, 0.5); ctx.set_line_width(12); ctx.rectangle(700, 520, 260, 300); ctx.stroke()
    ctx.move_to(830, 520); ctx.line_to(830, 820); ctx.move_to(700, 670); ctx.line_to(960, 670); ctx.stroke()
    glow_circle(ctx, 830, 670, 260, (1, 0.85, 0.4), 0.35)
    rrect(ctx, 40, 1040, 1000, 120, 30); ctx.set_source_rgb(0.95, 0.36, 0.62); ctx.fill()      # bed
    rrect(ctx, 60, 980, 260, 90, 30); ctx.set_source_rgb(1, 1, 1); ctx.fill()                 # pillow


def eye_xs(ctx, cx, cy, r, clear=0.0, lit=0.0, t=0.0):
    """eye cross-section, light enters on the left, retina at the back (right)"""
    a = 1 - 0.8 * clear
    ctx.arc(cx, cy, r, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.92 * a); ctx.fill()
    ctx.arc(cx - r * 0.86, cy, r * 0.42, math.pi * 0.62, math.pi * 1.38); ctx.set_source_rgba(0.75, 0.95, 1, 0.8 * a); ctx.fill()
    for s in (-1, 1):
        rrect(ctx, cx - r * 0.83, cy + s * r * 0.17 - (r * 0.38 if s < 0 else 0), r * 0.08, r * 0.38, 6)
        ctx.set_source_rgba(0.2, 0.45, 0.95, a); ctx.fill()
    ellipse(ctx, cx - r * 0.66, cy, r * 0.12, r * 0.3); ctx.set_source_rgba(0.6, 0.9, 1, 0.9 * a); ctx.fill()
    # retina
    ctx.set_line_width(r * 0.11); ctx.set_source_rgba(*(PNK if lit < 0.5 else YEL), a)
    ctx.arc(cx, cy, r * 0.93, -1.1, 1.1); ctx.stroke()
    if lit > 0:
        glow_circle(ctx, cx + r * 0.93, cy, r * 0.6, YEL, 0.8 * lit)
    # optic nerve
    rrect(ctx, cx + r * 0.9, cy + r * 0.12, r * 0.6, r * 0.2, 10); ctx.set_source_rgba(1, 0.75, 0.4, a); ctx.fill()
    if clear > 0:
        ctx.save(); ctx.set_dash([18, 12], (t * 60) % 30); ctx.set_line_width(7); ctx.set_source_rgba(*CYN, clear)
        ctx.arc(cx, cy, r, 0, 6.3); ctx.stroke(); ctx.restore()
    else:
        ctx.arc(cx, cy, r, 0, 6.3); ctx.set_line_width(6); ctx.set_source_rgb(0.75, 0.8, 0.95); ctx.stroke()


def ray(ctx, x0, y, x1, col=YEL, a=1.0, w=22):
    if x1 <= x0: return
    g = cairo.LinearGradient(x0, 0, x1, 0)
    g.add_color_stop_rgba(0, *col, 0.2 * a); g.add_color_stop_rgba(1, *col, a)
    ctx.rectangle(x0, y - w / 2, x1 - x0, w); ctx.set_source(g); ctx.fill()
    glow_circle(ctx, x1, y, w * 2.2, col, 0.9 * a)


def lamp(ctx, x, y, t):
    glow_circle(ctx, x, y, 120, YEL, 0.6 + 0.1 * math.sin(t * 8))
    ctx.arc(x, y, 42, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.6); ctx.fill()


def cinema(ctx, tg, bright=1.0):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.05, 0.03, 0.12); g.add_color_stop_rgb(1, 0.12, 0.04, 0.16)
    ctx.set_source(g); ctx.paint()
    # screen
    g = cairo.LinearGradient(100, 450, 980, 760)
    g.add_color_stop_rgb(0, 0.15 + 0.6 * bright, 0.5 * bright, 0.95 * bright); g.add_color_stop_rgb(1, 0.95 * bright, 0.3 * bright, 0.6 * bright)
    rrect(ctx, 100, 450, 880, 330, 16); ctx.set_source(g); ctx.fill()
    if bright > 0.05:
        glow_circle(ctx, 540, 615, 560, (0.6, 0.7, 1), 0.25 * bright)
        sparkles(ctx, 540, 615, 330, tg, 16, WHT)
        for k in range(2):   # two generic dancers on the screen
            px = 430 + k * 220; hop = abs(math.sin(tg * 6 + k)) * 14
            person(ctx, px, 760 - hop, 260, SHIRTS[k * 2 + 2], "smile", "up", tg + k)
    # seat rows
    for r_ in range(2):
        for c in range(7):
            rrect(ctx, 30 + c * 150, 1120 + r_ * 90, 130, 110, 26); ctx.set_source_rgb(0.55 - 0.15 * r_, 0.1, 0.2); ctx.fill()


def popcorn(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y + 6 * math.sin(t * 3)); ctx.scale(s, s)
    for k in range(9):
        ctx.arc(-40 + (k % 5) * 20 + (k // 5) * 10, -78 - (k // 5) * 18, 16, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.75); ctx.fill()
    ctx.move_to(-50, -70); ctx.line_to(50, -70); ctx.line_to(38, 40); ctx.line_to(-38, 40); ctx.close_path()
    ctx.set_source_rgb(1, 1, 1); ctx.fill()
    for k in range(3):
        ctx.move_to(-34 + k * 30, -70); ctx.line_to(-26 + k * 26, 40); ctx.line_to(-16 + k * 26, 40); ctx.line_to(-20 + k * 30, -70); ctx.close_path()
        ctx.set_source_rgb(*RED); ctx.fill()
    ctx.restore()


def scent(ctx, x0, y0, x1, y1, t, col=PNK, n=3, a=0.8):
    for k in range(n):
        ctx.move_to(x0, y0 + (k - 1) * 30)
        for j in range(1, 21):
            f = j / 20
            ctx.line_to(x0 + (x1 - x0) * f, y0 + (y1 - y0) * f + (k - 1) * 30 * (1 - f) + 14 * math.sin(f * 12 - t * 8 + k))
        ctx.set_line_width(6); ctx.set_source_rgba(*col, a * (0.6 + 0.4 * math.sin(t * 5 + k))); ctx.stroke()


def puff(ctx, x, y, r, a):
    for k, (dx, dy, rr) in enumerate(((0, 0, 1), (0.8, -0.3, 0.8), (-0.7, -0.2, 0.7), (0.2, -0.7, 0.75))):
        ctx.arc(x + dx * r, y + dy * r, rr * r, 0, 6.3)
    ctx.set_source_rgba(0.75, 0.95, 1, a); ctx.fill()


def swarm(ctx, cx, cy, rad, t, n, upto=1.0, s=1.0):
    for k in range(n):
        if hrand("sw", k) > upto: continue
        a = t * (1.5 + hrand("sv", k)) * (1 if k % 2 else -1) + hrand("sa", k) * 6.3
        rr = rad * (0.6 + 0.5 * hrand("sr", k))
        x = cx + math.cos(a) * rr; y = cy + math.sin(a) * rr * 0.8
        mosquito(ctx, x, y, s * (0.8 + 0.4 * hrand("ss", k)), t, a + (math.pi / 2 if k % 2 else -math.pi / 2), k)


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    ti = wt(0, "invisible")
    bedroom(ctx, tg)
    vis = 1 - ease_io((tl - ti + 0.35) / 0.8)
    s = pop(tl + 0.15, 0.25)
    ctx.save(); ctx.translate(430, 1250); ctx.scale(s, s)
    ghost(ctx, 0, 0, 800, "smile" if tl < 0.45 else "shock", "down" if tl < ti else "up", tl, vis=vis, look=0.6)
    ctx.restore()
    if vis < 0.9:
        sparkles(ctx, 430, 760, 380, tl, 22, CYN, "s0")
    if tl > ti - 0.3 and tl < ti + 0.05:
        ctx.set_source_rgba(1, 1, 1, 0.35 * (1 - (tl - ti + 0.3) / 0.35)); ctx.paint()


def s1(ctx, tg, tl, T):
    tth = wt(1, "Three"); tla = wt(1, "last"); tru = wt(1, "ruins")
    if tl < tth - 0.1:
        bedroom(ctx, tg)
        ghost(ctx, 540, 1250, 780, "smile", "wave", tl, vis=0, look=-0.4)
        for k, (txt, x, y, col) in enumerate((("SKIP OFFICE", 250, 600, YEL), ("FREE SNACKS", 820, 560, CYN), ("PRANKS!", 830, 900, PNK))):
            popchip(ctx, txt, x, y, tl - 0.1 - k * 0.22, col, (0, 0, 0), 52)
    else:
        tt = tl - tth + 0.1
        dim = tl > tla - 0.1
        for k in range(3):
            t0 = k * 0.22
            s = pop(tt - t0, 0.22)
            x = 540 + (k - 1) * 300; y = 820
            big = k == 2 and dim
            if big:
                s *= 1 + 0.25 * ease_out((tl - tla + 0.1) / 0.3) + 0.04 * math.sin(tl * 10)
            ctx.save(); ctx.translate(x + (6 * math.sin(tl * 40) if big and tl > tru else 0), y); ctx.scale(s, s)
            col = [YEL, CYN, RED][k]
            if big: glow_circle(ctx, 0, 0, 300, RED, 0.6)
            rrect(ctx, -120, -170, 240, 340, 34)
            ctx.set_source_rgba(*col, 0.35 if dim and k < 2 else 1); ctx.fill()
            text(ctx, str(k + 1), 0, -40, 170, (0, 0, 0), shadow=False, alpha=0.4 if dim and k < 2 else 1)
            text(ctx, "!" if k == 2 else "?", 0, 110, 90, WHT if k == 2 else (0, 0, 0), shadow=False, alpha=0.4 if dim and k < 2 else 1)
            ctx.restore()
        if tl > tla - 0.1:
            popchip(ctx, "THE LAST ONE...", 540, 1120, tl - tla + 0.1, RED, WHT, 60)


def s2(ctx, tg, tl, T):
    tm = wt(2, "Mosquitoes"); tb = wt(2, "breath"); tsm = wt(2, "smell")
    tinv = wt(2, "Invisible"); tnot = wt(2, "Not"); tde = wt(2, "Delhi")
    if tl < tinv - 0.08:
        tiles(ctx, 0, tl)
        hx, hy, h = 330, 1250, 700
        ghost(ctx, hx, hy, h, "smile" if tl < tm + 1.2 else "worry", "down", tl, vis=0, look=0.8)
        mx, my = hx + 25, hy - 0.79 * h
        # breath puffs drifting right
        if tl > tb - 0.5:
            for k in range(4):
                ph = ((tl - tb + 0.5) * 0.6 + k * 0.25) % 1
                puff(ctx, mx + 60 + ph * 520, my - 10 - ph * 60, 26 + 30 * ph, 0.6 * (1 - ph))
        if tl > tsm - 0.2:
            scent(ctx, hx + 80, hy - 0.5 * h, 1000, 780, tl, PNK, 3, ease_out((tl - tsm + 0.2) / 0.3))
        # mosquitoes fly in from the right, following the trail
        for k in range(6):
            f = ease_io((tl - tm - k * 0.18) / 1.6)
            if f <= 0: continue
            x = 1150 - (1150 - (mx + 70 + 40 * (k % 3))) * f + 12 * math.sin(tl * 9 + k)
            y = 650 + 70 * (k % 3) + ((my - 40 + 30 * (k // 2)) - (650 + 70 * (k % 3))) * f + 10 * math.cos(tl * 11 + k)
            mosquito(ctx, x, y, 1.6, tl, math.pi, k)
        if tl > tb - 0.05:
            popchip(ctx, "BREATH", 780, 640, tl - tb + 0.05, CYN, (0, 0, 0), 56)
        if tl > tsm - 0.05:
            popchip(ctx, "SMELL", 840, 1000, tl - tsm + 0.05, PNK, (0, 0, 0), 56)
    elif tl < tnot - 0.08:
        tt = tl - tinv + 0.08
        tiles(ctx, 0, 1)
        # office: confused boss, the hero tiptoes past
        rrect(ctx, 60, 1000, 600, 40, 10); ctx.set_source_rgb(0.55, 0.35, 0.25); ctx.fill()
        rrect(ctx, 90, 1040, 30, 210, 8); ctx.fill(); rrect(ctx, 600, 1040, 30, 210, 8); ctx.fill()
        rrect(ctx, 380, 880, 200, 125, 10); ctx.set_source_rgb(0.15, 0.15, 0.22); ctx.fill()
        rrect(ctx, 392, 892, 176, 100, 6); ctx.set_source_rgb(0.3, 0.6, 1); ctx.fill()
        look = math.sin(tl * 5)
        boss(ctx, 270, 1250, 720, tl, look=look)
        bubble(ctx, 300, 600, 60, "WHERE IS HE?", tt - 0.15, PNK)
        gx = 760 + 120 * ease_io(tt / 1.6)
        ghost(ctx, gx, 1250 - abs(math.sin(tl * 7)) * 12, 720, "smile", "wave", tl, vis=0, look=1)
    else:
        tt = tl - tnot + 0.08
        tiles(ctx, 0, 1)
        s = pop(tt, 0.2)
        ctx.save(); ctx.translate(540, 1250); ctx.scale(s, s)
        ghost(ctx, 0, 0, 760, "shock", "up", tl, vis=0, look=math.sin(tl * 6))
        ctx.restore()
        swarm(ctx, 540, 820, 320, tl, 18, upto=clamp(tt / 0.6), s=1.5)
        if tl > tde - 0.05:
            stamp(ctx, "DELHI MOSQUITOES", 540, 1130, tl - tde + 0.05, RED, 72, -0.06)
        popchip(ctx, "BZZZ", 210, 640, tt - 0.1, YEL, (0, 0, 0), 50)
        popchip(ctx, "BZZZ", 880, 700, tt - 0.35, YEL, (0, 0, 0), 44)


def s3(ctx, tg, tl, T):
    tdo = wt(3, "Dogs"); tn = wt(3, "10,000"); tev = wt(3, "Every"); tga = wt(3, "gali")
    if tl < tev - 0.08:
        tiles(ctx, 1, tl)
        ghost(ctx, 190, 1250, 600, "worry", "down", tl, vis=0, look=1)
        s = pop(tl - tdo + 0.15, 0.25)
        ctx.save(); ctx.translate(800, 1250); ctx.scale(s, s)
        dog(ctx, 0, 0, 2.3, tl, DOGC[0], sniff=True, face=-1)
        ctx.restore()
        if tl > tdo:
            scent(ctx, 260, 900, 560, 760, tl, PNK, 3, ease_out((tl - tdo) / 0.3))
        if tl > tn - 0.1:
            f = ease_out((tl - tn + 0.1) / 0.6)
            sc = pop(tl - tn + 0.1, 0.22)
            ctx.save(); ctx.translate(610, 660); ctx.scale(sc, sc)
            rrect(ctx, -260, -95, 520, 190, 40); ctx.set_source_rgba(0, 0, 0, 0.6); ctx.fill()
            text(ctx, f"{int(round(10000 * f / 100) * 100):,}x", 0, -8, 140, YEL, stroke=6)
            text(ctx, "AT LEAST", 0, -118, 44, WHT, SANS, stroke=3)
            ctx.restore()
            popchip(ctx, "BETTER NOSE", 610, 800, tl - tn - 0.4, PNK, (0, 0, 0), 50)
    else:
        tt = tl - tev + 0.08
        tiles(ctx, 1, 1)
        # street: gali dogs arrive one by one and bark at the "empty" spot
        ctx.rectangle(0, 1180, W, 200); ctx.set_source_rgba(0.3, 0.25, 0.4, 0.6); ctx.fill()
        ghost(ctx, 250, 1250, 660, "shock", "up", tl, vis=0, look=1)
        for k in range(3):
            f = ease_out((tt - k * 0.35) / 0.4)
            if f <= 0: continue
            x = 1250 - (1250 - (560 + k * 170)) * f
            dog(ctx, x, 1250 - 12 * k, 1.85 - 0.15 * k, tl + k, DOGC[k], bark=tt > k * 0.35 + 0.3, face=-1)
            if tt > k * 0.35 + 0.35:
                popchip(ctx, "WOOF!", x - 40, 760 + k * 45, tt - k * 0.35 - 0.35, [YEL, CYN, PNK][k], (0, 0, 0), 48)
        if tl > tga - 0.05:
            popchip(ctx, "GALI SQUAD", 720, 640, tl - tga + 0.05, GRN, (0, 0, 0), 56)


def s4(ctx, tg, tl, T):
    tyo = wt(4, "You"); tey = wt(4, "eyes"); tse = wt(4, "see")
    if tl < tyo - 0.1:
        tiles(ctx, 2, tl)
        s = pop(tl - 0.05, 0.25)
        ctx.save(); ctx.translate(540, 860); ctx.scale(s, s)
        glow_circle(ctx, 0, 0, 420, RED, 0.5 + 0.15 * math.sin(tl * 12))
        text(ctx, "3", 0, 0, 440, WHT, stroke=10, scol=RED)
        ctx.restore()
    else:
        # giant see-through eyes open... onto darkness
        op = ease_io((tl - tey + 0.4) / 0.6)
        ctx.set_source_rgba(0, 0, 0, 0.5); ctx.paint()
        for sx in (-1, 1):
            cx, cy = 540 + sx * 230, 820
            ctx.save(); ctx.translate(cx, cy); ctx.scale(1, max(0.04, op))
            ctx.arc(0, 0, 170, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.22); ctx.fill()
            ctx.arc(0, 0, 70, 0, 6.3); ctx.set_source_rgba(0.3, 0.6, 1, 0.35); ctx.fill()
            ctx.arc(0, 0, 32, 0, 6.3); ctx.set_source_rgba(0.05, 0.05, 0.1, 0.4); ctx.fill()
            ctx.restore()
            ctx.save(); ctx.set_dash([16, 10], (tl * 50) % 26); ctx.set_line_width(7); ctx.set_source_rgba(*CYN, 0.9)
            ctx.save(); ctx.translate(cx, cy); ctx.scale(1, max(0.04, op)); ctx.arc(0, 0, 170, 0, 6.3); ctx.restore(); ctx.stroke()
            ctx.restore()
        if tl > tse - 0.05:
            # vision goes black from the edges in
            f = ease_io((tl - tse + 0.05) / 0.45)
            ctx.set_source_rgba(0, 0, 0, 0.92 * f); ctx.paint()
            ctx.save(); ctx.translate(540, 820); ctx.scale(pop(tl - tse - 0.15, 0.25), pop(tl - tse - 0.15, 0.25))
            text(ctx, "?", 0, 0, 260, (0.3, 0.3, 0.5), alpha=f)
            ctx.restore()


def s5(ctx, tg, tl, T):
    tca = wt(5, "catching"); tli = wt(5, "light"); tinv = wt(5, "Invisible"); tpa = wt(5, "pass"); tyo = wt(5, "You're")
    cx, cy, r = 500, 820, 260
    if tl < tinv - 0.1:
        lamp(ctx, 90, cy, tl)
        eye_xs(ctx, cx, cy, r, 0, lit=clamp((tl - tli) / 0.15) if tl > tli else 0, t=tl)
        f = ease_out((tl - tca + 0.3) / 0.6)
        ray(ctx, 130, cy, 130 + (cx + r * 0.88 - 130) * f)
        if tl > tli:
            # signal to the brain
            ph = ((tl - tli) * 2.5) % 1
            ctx.arc(cx + r * 0.95 + ph * 160, cy + r * 0.22, 14, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()
            popchip(ctx, "RETINA CATCHES IT", 540, 520, tl - tli, YEL, (0, 0, 0), 54)
            check(ctx, 900, 1150, 110, GRN)
    elif tl < tyo - 0.08:
        tt = tl - tinv + 0.1
        lamp(ctx, 90, cy, tl)
        cl = ease_io(tt / 0.4)
        eye_xs(ctx, cx, cy, r, cl, 0, tl)
        f = ease_out((tl - tpa + 0.4) / 0.7) if tl > tpa - 0.4 else 0
        ray(ctx, 130, cy, 130 + (1150 - 130) * f, YEL, 0.9)
        popchip(ctx, "INVISIBLE EYE", 540, 520, tt - 0.05, CYN, (0, 0, 0), 54)
        if f > 0.7:
            popchip(ctx, "NOTHING CAUGHT", 540, 1140, tl - tpa - 0.2, RED, WHT, 54)
    else:
        tt = tl - tyo + 0.08
        ctx.set_source_rgb(0.01, 0.01, 0.03); ctx.paint()
        s = pop(tt, 0.22)
        ctx.save(); ctx.translate(540, 1300); ctx.scale(s, s)
        ghost(ctx, 0, 0, 900, "shock", "up", tl, vis=0, look=math.sin(tl * 7) * 0.8)
        ctx.restore()
        stamp(ctx, "BLIND!", 540, 1110, tt - 0.4, RED, 150, -0.08)


def s6(ctx, tg, tl, T):
    tfr = wt(6, "Free"); tca = wt(6, "Can't"); tsi = wt(6, "single")
    if tl < tca - 0.08:
        cinema(ctx, tl)
        checker(ctx, 820, 1250, 640, tl, look=math.sin(tl * 4) * 0.8)
        bubble(ctx, 820, 600, 60, "TICKET?", tl - 0.5, RED, -1)
        gx = 200 + 300 * ease_io(tl / 1.8)
        ghost(ctx, gx, 1250 - abs(math.sin(tl * 7)) * 12, 660, "smile", "wave", tl, vis=0, look=1)
        popchip(ctx, "FREE ENTRY!", 330, 1110, tl - tfr, GRN, (0, 0, 0), 60)
    else:
        tt = tl - tca + 0.08
        dark = ease_io((tl - tsi + 0.3) / 0.4) if tl > tsi - 0.3 else 0
        cinema(ctx, tl, bright=1.0)
        ghost(ctx, 540, 1330, 820, "worry", "down", tl, vis=0, look=0)
        popcorn(ctx, 760, 980, 1.0, tl)
        for sx in (-1, 1):
            rrect(ctx, 540 + sx * 230 - 60, 1060, 120, 200, 30); ctx.set_source_rgb(0.5, 0.08, 0.18); ctx.fill()
        if dark > 0:
            ctx.set_source_rgba(0, 0, 0, 0.9 * dark); ctx.paint()
            popcorn(ctx, 760, 980, 1.0, tl)       # the popcorn is still visible. You aren't. Neither is the film.
        stamp(ctx, "CAN'T SEE IT!", 540, 600, tt - 0.25, RED, 92, -0.08)


def s7(ctx, tg, tl, T):
    tye = wt(7, "Yes"); tno = wt(7, "no?"); tse = wt(7, "Send"); tsn = wt(7, "sneakiest")
    if tl < tse - 0.08:
        ghost(ctx, 540, 1250, 640, "smile", "cheeks", tl, vis=0, look=0)
        bubble(ctx, 540, 520, 70, "STILL WANT IT?", tl - 0.05, PNK)
        for k, (txt, x, col, t0) in enumerate((("YES", 250, GRN, tye), ("NO", 830, RED, tno))):
            s = pop(tl - t0 + 0.05, 0.22) * (1 + 0.04 * math.sin(tl * 7 + k))
            ctx.save(); ctx.translate(x, 860); ctx.scale(s, s)
            glow_circle(ctx, 0, 0, 200, col, 0.4)
            rrect(ctx, -130, -80, 260, 160, 50); ctx.set_source_rgb(*col); ctx.fill()
            text(ctx, txt, 0, 0, 100, (0, 0, 0) if k == 0 else WHT, shadow=False)
            ctx.restore()
    else:
        tt = tl - tse + 0.08
        ghost(ctx, 270, 1180, 600, "smile", "wave", tl, vis=0, look=1)
        person(ctx, 820, 1180, 620, SHIRTS[2], "shock" if tl > tsn else "smile", "up" if tl > tsn else "down", tl, look=-1)
        # paper plane from the hero to the friend
        f = ease_io(tt / 1.1)
        px = 350 + 360 * f; py = 700 - 160 * math.sin(f * math.pi)
        ctx.save(); ctx.translate(px, py); ctx.rotate(-0.4 + 0.8 * f); ctx.scale(0.8, 0.8)
        ctx.move_to(-120, 10); ctx.line_to(130, -90); ctx.line_to(40, 110); ctx.line_to(10, 40); ctx.close_path()
        ctx.set_source_rgb(*WHT); ctx.fill(); ctx.restore()
        if tl > tsn - 0.05:
            popchip(ctx, "SNEAKIEST FRIEND", 820, 520, tl - tsn + 0.05, YEL, (0, 0, 0), 52)


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7]


def _buzz(A, t, d=0.8, g=0.08):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    f = 560 + 40 * np.sin(2 * np.pi * 5 * tt)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / 44100)) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * tt))
    x = A.lp(x, 2500) * np.minimum(1, tt / 0.1) * np.minimum(1, (d - tt) / 0.15)
    A.add(A.sfx_buf, x, t, g)


def _woof(A, t, g=0.35):
    import numpy as np
    n = int(0.22 * 44100); tt = np.arange(n) / 44100
    f = 260 - 120 * tt / 0.22
    x = np.sin(2 * np.pi * np.cumsum(f) / 44100) + 0.4 * A.bp(A.noise(0.22), 300, 1500)
    A.add(A.sfx_buf, A.lp(x, 1400) * np.exp(-tt * 9), t, g)


def sfx(A):
    for k in range(int(A.S(2) / 0.8)):
        A.thump(0.5 + k * 0.8, 0.4, 50)                     # heartbeat under the hook and the promise
    ti = A.W(0, "invisible")
    for k in range(6):
        A.ding(ti - 0.3 + k * 0.07, 0.05, A.note(76 + [0, 4, 7, 12, 16, 19][k]), 0.6)   # shimmer as you vanish
    A.boing(A.W(1, "fun?"), 0.12, 420, 0.35)
    for k in range(3):
        A.thump(A.W(1, "Three") + k * 0.22, 0.45, 70 + 10 * k)
    A.thump(A.W(1, "ruins"), 0.6, 45)
    A.pop(A.W(2, "One."), 0.35)
    _buzz(A, A.W(2, "Mosquitoes") + 0.3, 2.2, 0.06)
    A.pop(A.W(2, "breath"), 0.25); A.pop(A.W(2, "smell"), 0.25)
    A.boing(A.W(2, "Delhi"), 0.15, 330)
    _buzz(A, A.W(2, "Not") + 0.05, 1.4, 0.1)
    A.pop(A.W(3, "Two."), 0.35)
    for k in range(5):
        A.ding(A.W(3, "10,000") + k * 0.1, 0.05, A.note(72 + 2 * k), 0.4)
    for k in range(3):
        _woof(A, A.W(3, "Every") + 0.3 + k * 0.35, 0.3)
        _woof(A, A.W(3, "Every") + 0.5 + k * 0.35, 0.22)
    A.music_level(A.S(4) - 0.1, A.S(5) + 0.3, 0.25)      # music drops away for the big one
    A.thump(A.W(4, "Three.") - 0.02, 0.7, 50)
    A.thump(A.W(4, "nothing") - 0.05, 0.6, 40)
    A.zap_down(A.W(4, "see"), 0.15, 0.8)
    A.ding(A.W(5, "light"), 0.1, 1568)
    A.whoosh(A.W(5, "pass"), 0.2, 0.5)
    A.thump(A.W(5, "blind"), 0.7, 45)
    A.pop(A.W(6, "Free"), 0.35); A.ding(A.W(6, "Free") + 0.1, 0.07, 1318.5)
    A.scratch(A.W(6, "Can't") - 0.05, 0.3)
    A.pop(A.W(7, "Yes"), 0.35); A.pop(A.W(7, "no?"), 0.35)
    A.whoosh(A.W(7, "Send") + 0.1, 0.2, 0.6)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(7, "sneakiest") + 0.1 + k * 0.1, 0.07, A.note(m))

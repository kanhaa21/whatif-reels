"""Scenes for "What if your phone caught fire while charging?" (card style, Hinglish, female voice).
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT."""
import math
import cairo
from reelkit.lib import clamp, ease_out, ease_io, pop, rrect, hrand, W, H
from reelkit.cards import *  # noqa: F401,F403

MUSIC = {"beat_from_scene": 2, "bpm": 108}
NO_FLASH = tuple(range(10))


def cut_times(i):
    try:
        return {1: [0, wt(1, "pillow") - 0.1], 2: [0, wt(2, "catch") - 0.1],
                3: [0, wt(3, "No") - 0.05], 5: [0, wt(5, "Original") - 0.1]}.get(i, [0])
    except KeyError:
        return [0]


# ---------------------------------------------------------------- props (screen px)
def phone(ctx, x, y, s, t, state="ok", swell=0.0, rot=0.0):
    """phone mockup: state ok / hot / fire; swell bulges the body"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s * (1 + 0.08 * swell), s)
    w, h = 180, 340
    rrect(ctx, -w / 2, -h / 2, w, h, 30); ctx.set_source_rgb(0.12, 0.12, 0.16); ctx.fill_preserve()
    ctx.set_source_rgb(*(RED if state != "ok" else (0.35, 0.37, 0.45))); ctx.set_line_width(5); ctx.stroke()
    rrect(ctx, -w / 2 + 12, -h / 2 + 14, w - 24, h - 28, 22)
    g = cairo.LinearGradient(0, -h / 2, 0, h / 2)
    if state == "ok":
        g.add_color_stop_rgb(0, 0.1, 0.15, 0.35); g.add_color_stop_rgb(1, 0.15, 0.1, 0.3)
    else:
        g.add_color_stop_rgb(0, 0.45, 0.06, 0.08); g.add_color_stop_rgb(1, 0.2, 0.03, 0.05)
    ctx.set_source(g); ctx.fill()
    # battery icon
    bw = 90
    rrect(ctx, -bw / 2, -30, bw, 50, 8); ctx.set_source_rgb(*WHT); ctx.set_line_width(5); ctx.stroke()
    ctx.rectangle(bw / 2, -14, 8, 18); ctx.fill()
    lvl = 0.9 if state == "ok" else 0.25
    ctx.rectangle(-bw / 2 + 7, -23, (bw - 14) * lvl, 36); ctx.set_source_rgb(*(GRN if state == "ok" else RED)); ctx.fill()
    if state != "ok":
        say(ctx, "!", 0, 70, 70, YEL)
    ctx.restore()
    # charging cable
    ctx.move_to(x, y + 170 * s); ctx.curve_to(x, y + 260 * s, x + 120, y + 240 * s, x + 160, y + 330 * s)
    ctx.set_source_rgb(0.85, 0.85, 0.9); ctx.set_line_width(6); ctx.stroke()


def pillow(ctx, x, y, w, h, a=1.0):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(-w / 2 + 30, -h / 2); ctx.curve_to(0, -h / 2 - 30, 0, -h / 2 - 30, w / 2 - 30, -h / 2)
    ctx.curve_to(w / 2 + 20, 0, w / 2 + 20, 0, w / 2 - 30, h / 2)
    ctx.curve_to(0, h / 2 + 30, 0, h / 2 + 30, -w / 2 + 30, h / 2)
    ctx.curve_to(-w / 2 - 20, 0, -w / 2 - 20, 0, -w / 2 + 30, -h / 2); ctx.close_path()
    ctx.set_source_rgba(0.88, 0.89, 0.95, a); ctx.fill()
    ctx.restore()


def smoke(ctx, x, y, t, n=8, a=0.6, spread=60):
    for k in range(n):
        ph = (t * 0.6 + k / n) % 1
        px = x + math.sin(t * 2 + k) * spread * ph
        py = y - ph * 300
        ctx.arc(px, py, 26 + 50 * ph, 0, 6.3); ctx.set_source_rgba(0.6, 0.6, 0.65, a * (1 - ph)); ctx.fill()


def flame(ctx, x, y, s, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s * (1 + 0.06 * math.sin(t * 20)))
    for k, (col, sc) in enumerate(((ORG, 1.0), (YEL, 0.6))):
        ctx.save(); ctx.scale(sc, sc)
        ctx.move_to(0, -90); ctx.curve_to(40, -40, 50, 0, 40, 30); ctx.curve_to(30, 60, -30, 60, -40, 30)
        ctx.curve_to(-50, 0, -20, -30, 0, -90); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.fill(); ctx.restore()
    ctx.restore()


def thermo(ctx, x, y, lvl):
    rrect(ctx, x - 22, y - 160, 44, 260, 22); ctx.set_source_rgb(0.2, 0.21, 0.28); ctx.fill()
    ctx.arc(x, y + 110, 40, 0, 6.3); ctx.set_source_rgb(*RED); ctx.fill()
    hgt = 240 * lvl
    rrect(ctx, x - 12, y + 100 - hgt, 24, hgt + 10, 12); ctx.fill()


def phone_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    rrect(ctx, -26, -46, 52, 92, 10); ctx.set_source_rgb(*col); ctx.set_line_width(8); ctx.stroke()
    ctx.arc(0, 32, 5, 0, 6.3); ctx.fill(); ctx.restore()


def run_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col)
    ctx.arc(10, -38, 12, 0, 6.3); ctx.fill()
    ctx.set_line_width(11); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(4, -20); ctx.line_to(-6, 12); ctx.line_to(14, 44)
    ctx.move_to(-6, 12); ctx.line_to(-30, 38); ctx.move_to(0, -12); ctx.line_to(28, 0); ctx.move_to(0, -12); ctx.line_to(-26, -2)
    ctx.stroke(); ctx.restore()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tt_ = wt(0, "Your"); td = wt(0, "smoking")
    bg(ctx, tg, RED, 0.12 + 0.08 * clamp(tl / 3))
    headline(ctx, "2 a.m., beside your pillow", [("Your phone is", WHT), ("SMOKING", RED)], 1.0)
    card(ctx, 540, 840, 760, 640, RED if tl > td else (0.25, 0.27, 0.35), 1.0, glow=0.7)
    pillow(ctx, 430, 860, 420, 260)
    phone(ctx, 740, 820, 0.95, tl, "hot" if tl > 1.0 else "ok", rot=0.12)
    smoke(ctx, 740, 680, tl, a=0.25 + 0.5 * clamp(tl / 1.5))
    pill(ctx, "2:00 AM", 300, 600, 0.3, BLU, 40)
    if tl > td - 0.1:
        stamp(ctx, "SMOKE!", 540, 1120, tl - td + 0.1, RED, 70, -0.08)


def s1(ctx, tg, tl, T):
    tp = wt(1, "pop"); tb = wt(1, "battery"); tk = wt(1, "pillow")
    if tl < tk - 0.1:
        bg(ctx, tg, RED, 0.2)
        headline(ctx, "hiss... pop!", [("The battery is", WHT), ("swelling", RED)], tl)
        sw = clamp((tl - tb + 0.1) / 0.8)
        card(ctx, 540, 840, 560, 640, RED, 1.0, glow=0.8)
        phone(ctx, 540, 800, 1.3, tl, "hot", swell=sw)
        smoke(ctx, 540, 600, tl, a=0.35)
        stamp(ctx, "POP!", 820, 600, tl - tp + 0.05, ORG, 64, 0.12)
        pill(ctx, "swelling = danger", 540, 1180, tl - tb - 0.4, RED, 40)
    else:
        tt = tl - tk + 0.1
        bg(ctx, tg, ORG, 0.18)
        headline(ctx, "under the pillow", [("The heat is", WHT), ("trapped", ORG)], tt)
        card(ctx, 540, 840, 760, 640, ORG, tt, glow=0.7)
        phone(ctx, 540, 880, 0.75, tl, "hot", rot=1.5708)
        pillow(ctx, 540, 760, 560, 200, 0.95)
        # heat arrows bouncing back down
        for k in range(4):
            x = 380 + k * 105
            ph = (tl * 1.4 + k * 0.25) % 1
            yy = 1000 - 200 * ph
            ctx.move_to(x, yy); ctx.line_to(x, yy - 60); ctx.set_source_rgba(*RED, 1 - ph); ctx.set_line_width(8); ctx.stroke()
            ctx.move_to(x - 16, yy - 50); ctx.line_to(x, yy - 72); ctx.line_to(x + 16, yy - 50); ctx.stroke()
        pill(ctx, "heat can't escape", 540, 1180, tt - 0.3, ORG, 40)


def s2(ctx, tg, tl, T):
    tth = wt(2, "thermal"); tbn = wt(2, "catch"); tag = wt(2, "fire")
    if tl < tbn - 0.1:
        bg(ctx, tg, ORG, 0.18)
        headline(ctx, "the heat keeps building", [("Thermal", ORG), ("runaway", WHT)], tl)
        card(ctx, 540, 840, 640, 640, ORG, tl, glow=0.8)
        lvl = clamp(0.3 + tl / 2.6)
        thermo(ctx, 380, 820, lvl)
        say(ctx, "HEAT", 650, 760, 96, RED)
        # circular arrows: heat makes more heat
        ctx.save(); ctx.translate(650, 920); ctx.rotate(tl * 3)
        ctx.arc(0, 0, 70, 0.3, 5.6); ctx.set_source_rgb(*ORG); ctx.set_line_width(10); ctx.stroke()
        ctx.move_to(70 * math.cos(5.6) + 18, 70 * math.sin(5.6) - 10); ctx.line_to(70 * math.cos(5.6) - 18, 70 * math.sin(5.6) - 18)
        ctx.line_to(70 * math.cos(5.6), 70 * math.sin(5.6) + 18); ctx.close_path(); ctx.fill()
        ctx.restore()
        pill(ctx, "heat in > heat out", 540, 1180, tl - tth, ORG, 40)
    else:
        tt = tl - tbn + 0.1
        bg(ctx, tg, RED, 0.25)
        headline(ctx, "without warning", [("It can catch", WHT), ("fire", RED)], tt)
        card(ctx, 540, 840, 560, 640, RED, 1.0, glow=1.0)
        phone(ctx, 540, 840, 1.2, tl, "fire")
        if tl > tag - 0.15:
            fs = pop(tl - tag + 0.15, 0.25)
            flame(ctx, 540, 640, 1.4 * fs, tl)
            flame(ctx, 470, 680, 0.8 * fs, tl + 1); flame(ctx, 610, 690, 0.9 * fs, tl + 2)


def s3(ctx, tg, tl, T):
    tn = wt(3, "No"); tz = wt(3, "toxic"); ts = wt(3, "Selfies")
    bg(ctx, tg, YEL if tl < tn - 0.05 else RED, 0.15)
    headline(ctx, "your first instinct?", [("Grab", WHT), ("it?", YEL)], tl if tl < tn - 0.05 else 1.0)
    card(ctx, 540, 840, 560, 640, YEL if tl < tn - 0.05 else RED, 1.0, glow=0.6)
    phone(ctx, 540, 880, 1.0, tl, "hot")
    smoke(ctx, 540, 700, tl, a=0.4)
    if tl < tn - 0.05:
        # hand reaching in from the right
        hx = 960 - 260 * ease_out(clamp(tl / 1.2))
        rrect(ctx, hx, 840, 300, 90, 45); ctx.set_source_rgb(0.93, 0.72, 0.56); ctx.fill()
        for k in range(3):
            rrect(ctx, hx - 50, 830 + k * 30, 80, 26, 13); ctx.fill()
    else:
        stamp(ctx, "NO!", 540, 760, tl - tn + 0.05, RED, 120, -0.12)
        pill(ctx, "the smoke is toxic", 540, 1195, tl - tz + 0.1, PUR, 40, icon=xmark)
        if tl > ts - 0.1:
            stamp(ctx, "selfies can wait", 540, 600, tl - ts + 0.1, ORG, 44, 0.06)


def s4(ctx, tg, tl, T):
    tb = wt(4, "out"); td = wt(4, "Close"); tc = wt(4, "112")
    bg(ctx, tg, GRN, 0.14)
    headline(ctx, "do this", [("3", GRN), ("steps", WHT)], tl)
    steps = [("Get out", run_icon, tb), ("Close the door", door, td), ("Call 112 from outside", phone_icon, tc)]
    for k, (lab, ic, t0) in enumerate(steps):
        on = t0 - 0.15 <= tl < (steps[k + 1][2] - 0.15 if k < 2 else 99)
        numcard(ctx, 540, 560 + k * 215, 660, 185, k + 1, lab, tl - t0 + 0.45, on=on, col=GRN, icon=ic, done=tl > t0 + 0.6)


def s5(ctx, tg, tl, T):
    tbd = wt(5, "bed"); ttb = wt(5, "table"); to = wt(5, "Original"); tsw = wt(5, "never")
    if tl < to - 0.1:
        bg(ctx, tg, GRN, 0.12)
        headline(ctx, "from now on", [("Table,", GRN), ("not", WHT), ("bed", RED)], tl)
        card(ctx, 330, 840, 380, 480, RED if tl > tbd - 0.2 else (0.25, 0.27, 0.35), tl - 0.1, glow=0.6)
        pillow(ctx, 330, 800, 260, 160, clamp(tl / 0.2))
        say(ctx, "BED", 330, 960, 64, RED, alpha=clamp(tl / 0.2))
        if tl > tbd - 0.2:
            xmark(ctx, 330, 650, 90, RED)
        card(ctx, 750, 840, 380, 480, GRN if tl > ttb - 0.2 else (0.25, 0.27, 0.35), tl - 0.25, glow=0.8)
        if tl > 0.25:
            rrect(ctx, 600, 820, 300, 24, 8); ctx.set_source_rgb(0.6, 0.45, 0.3); ctx.fill()
            ctx.rectangle(620, 844, 16, 90); ctx.rectangle(864, 844, 16, 90); ctx.fill()
            rrect(ctx, 710, 790, 80, 30, 6); ctx.set_source_rgb(0.2, 0.2, 0.26); ctx.fill()
            say(ctx, "TABLE", 750, 960, 64, GRN)
            if tl > ttb - 0.2:
                tick(ctx, 750, 650, 100, GRN)
    else:
        bg(ctx, tg, BLU, 0.12)
        headline(ctx, "and", [("2 habits", BLU)], tl - to + 0.1)
        numcard(ctx, 540, 620, 660, 200, 1, "Original charger", tl - to + 0.2, on=tl < tsw - 0.1, col=GRN, icon=bolt, done=True)
        numcard(ctx, 540, 860, 660, 200, 2, "Never while you sleep", tl - tsw + 0.2, on=tl > tsw - 0.1, col=RED, icon=clock)


def s6(ctx, tg, tl, T):
    tbd = wt(6, "Bed"); ttb = wt(6, "table")
    bg(ctx, tg, BLU, 0.14)
    headline(ctx, "comment below", [("Where is it", WHT), ("charging now?", YEL)], tl)
    phone(ctx, 540, 660, 0.7, tl, "ok")
    for k, (lab, col, t0) in enumerate((("BED", RED, tbd), ("TABLE", GRN, ttb))):
        x = 330 + k * 420
        card(ctx, x, 1000, 340, 180, col, tl - t0 + 0.2, glow=0.9)
        if tl > t0 - 0.2:
            say(ctx, lab, x, 1000, 84, col)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def _hiss(A, t, d=1.0, g=0.12):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.hp(A.noise(d), 4000) * np.minimum(1, tt / 0.2) * np.minimum(1, (d - tt) / 0.2)
    A.add(A.sfx_buf, x, t, g)


def _crackle(A, t, d=1.2, g=0.25):
    import numpy as np
    for k in range(int(d * 25)):
        tk = t + A.rng.uniform(0, d)
        n = int(0.01 * 44100)
        A.add(A.sfx_buf, A.hp(A.noise(0.01), 1500) * np.exp(-np.arange(n) / 44100 * 400), tk, g * A.rng.uniform(0.3, 1))


def sfx(A):
    _hiss(A, 0.4, 3.0, 0.08)
    A.ding(A.W(0, "smoking"), 0.06, 1318.5)
    _hiss(A, A.S(1), 0.8, 0.18)
    A.thump(A.W(1, "pop"), 0.6, 70); A.pop(A.W(1, "pop"), 0.4)
    A.whoosh(A.W(1, "pillow") - 0.05, 0.15, 0.3)
    A.whoosh(A.S(2), 0.15, 0.3)
    A.ding(A.W(2, "thermal"), 0.06, A.note(76))
    _crackle(A, A.W(2, "fire") - 0.1, 1.4, 0.3)
    A.thump(A.W(2, "fire") - 0.1, 0.5, 60)
    A.whoosh(A.S(3) + 0.1, 0.15, 0.4)
    A.thump(A.W(3, "No") - 0.03, 0.6, 60)
    A.pop(A.W(3, "toxic"), 0.25); A.boing(A.W(3, "Selfies"), 0.12, 300)
    for w in ("out", "Close", "112"):
        A.pop(A.W(4, w), 0.3)
    A.ding(A.W(4, "112") + 0.3, 0.07, A.note(84))
    A.pop(A.W(5, "bed"), 0.25); A.ding(A.W(5, "table"), 0.07, A.note(79))
    A.whoosh(A.W(5, "Original") - 0.05, 0.15, 0.3)
    A.pop(A.W(5, "never"), 0.25)
    A.pop(A.W(6, "Bed"), 0.3); A.pop(A.W(6, "table"), 0.3)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(6, "table") + 0.3 + k * 0.1, 0.06, A.note(m))

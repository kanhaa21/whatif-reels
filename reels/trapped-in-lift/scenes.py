"""Scenes for "What if you got trapped in a lift with no signal?" (card style, English, female voice).
Everyday-emergencies queue, topic 2. Injected by reelkit.make before this runs: wt(line_i, word), TL, SCRIPT."""
import math
import cairo
from reelkit.lib import clamp, ease_out, ease_io, pop, rrect, hrand, W, H
from reelkit.cards import *  # noqa: F401,F403

NO_FLASH = tuple(range(10))
STEEL = (0.16, 0.17, 0.23)
DARK = (0.01, 0.01, 0.02)


def cut_times(i):
    try:
        return {0: [0, wt(0, "phone") - 0.1], 1: [0, wt(1, "Don") - 0.05, wt(1, "Four") - 0.1],
                2: [0, wt(2, "Sometimes") - 0.1], 3: [0, wt(3, "lift") - 0.1],
                4: [0, wt(4, "not") - 0.1, wt(4, "Lifts") - 0.1],
                5: [0, wt(5, "moving") - 0.3, wt(5, "hatch") - 0.3]}.get(i, [0])
    except KeyError:
        return [0]


# ---------------------------------------------------------------- props (screen px)
def lift_box(ctx, x, y, w, h, tt, border=BLU, open_=0.0, label="STUCK", light=1.0, shake=0.0, t=0.0):
    """front view of a lift car as a UI card: header, floor display, two doors"""
    sx = shake * math.sin(t * 60)
    ctx.save(); ctx.translate(sx, 0)
    card(ctx, x, y, w, h, border, tt, glow=0.8)
    if tt >= 0:
        rrect(ctx, x - w / 2 + 14, y - h / 2 + 14, w - 28, 66, 20); ctx.set_source_rgb(*border); ctx.fill()
        say(ctx, "LIFT", x - w / 2 + 40, y - h / 2 + 47, 32, BLACK, align="l")
        say(ctx, label, x + w / 2 - 40, y - h / 2 + 47, 26, BLACK, align="r")
        # floor display
        rrect(ctx, x - 110, y - h / 2 + 100, 220, 96, 18); ctx.set_source_rgb(*DARK); ctx.fill()
        say(ctx, "- -", x, y - h / 2 + 148, 64, RED if label == "STUCK" else YEL)
        # doorway and doors
        dx0, dw, dy0, dh = x - 150, 300, y - h / 2 + 220, h - 250
        rrect(ctx, dx0, dy0, dw, dh, 8); ctx.set_source_rgb(0.92, 0.9, 0.8) if open_ > 0 else ctx.set_source_rgb(*DARK); ctx.fill()
        g = dw / 2 * open_
        for d in (-1, 1):
            px = x - 148 - g if d < 0 else x + 2 + g
            ctx.rectangle(px, dy0 + 2, 146, dh - 4); ctx.set_source_rgb(*STEEL); ctx.fill()
        # ceiling light flicker
        ctx.set_source_rgba(1, 1, 0.85, 0.12 * light); ctx.rectangle(x - w / 2 + 14, y - h / 2 + 84, w - 28, h - 98); ctx.fill()
    ctx.restore()


def phone(ctx, x, y, s, t, bars=0, tt=1.0):
    """phone mockup with signal bars and 'No service'"""
    if tt < 0: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    w, h = 220, 400
    rrect(ctx, -w / 2, -h / 2, w, h, 34); ctx.set_source_rgb(0.12, 0.12, 0.16); ctx.fill_preserve()
    ctx.set_source_rgb(*(RED if bars == 0 else GRN)); ctx.set_line_width(5); ctx.stroke()
    rrect(ctx, -w / 2 + 12, -h / 2 + 14, w - 24, h - 28, 24); ctx.set_source_rgb(0.08, 0.09, 0.16); ctx.fill()
    for k in range(4):
        bh = 16 + k * 14
        ctx.rectangle(-58 + k * 30, -40 - bh, 20, bh)
        ctx.set_source_rgb(*(GRN if k < bars else (0.3, 0.31, 0.38))); ctx.fill()
    if bars == 0:
        xmark(ctx, 70, -64, 40, RED)
    say(ctx, "No service" if bars == 0 else "Connected", 0, 40, 30, RED if bars == 0 else GRN)
    say(ctx, "SOS?", 0, 110, 40, GREY)
    ctx.restore()


def hand(ctx, x, y, d, a=1.0):
    """flat hand pushing sideways; d=-1 points left, +1 points right"""
    ctx.save(); ctx.translate(x, y); ctx.scale(d, 1)
    ctx.set_source_rgba(0.93, 0.72, 0.56, a)
    rrect(ctx, -170, -45, 170, 90, 40); ctx.fill()
    for k in range(4):
        rrect(ctx, -10, -44 + k * 22, 70, 20, 10); ctx.fill()
    ctx.restore()


def button(ctx, x, y, r, col, pressed, icon):
    ctx.arc(x, y, r, 0, 6.3); ctx.set_source_rgb(*(col if pressed else (0.2, 0.21, 0.28))); ctx.fill()
    ctx.arc(x, y, r, 0, 6.3); ctx.set_source_rgb(*col); ctx.set_line_width(5); ctx.stroke()
    if pressed:
        ctx.arc(x, y, r + 16, 0, 6.3); ctx.set_source_rgba(*col, 0.35); ctx.set_line_width(10); ctx.stroke()
    icon(ctx, x, y, r * 1.1, BLACK if pressed else col)


def door_open_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col)
    for d in (-1, 1):
        ctx.move_to(d * 8, 0); ctx.line_to(d * 34, -22); ctx.line_to(d * 34, 22); ctx.close_path(); ctx.fill()
        ctx.rectangle(d * 44 - 4, -34, 8, 68); ctx.fill()
    ctx.restore()


def waves(ctx, x, y, t, col, n=3, d=1):
    for k in range(n):
        ph = (t * 1.5 + k / n) % 1
        ctx.arc(x, y, 40 + ph * 120, -0.6 if d > 0 else math.pi - 0.6, 0.6 if d > 0 else math.pi + 0.6)
        ctx.set_source_rgba(*col, 1 - ph); ctx.set_line_width(7); ctx.stroke()
        ctx.new_path()


def vent(ctx, x, y, w, col):
    for k in range(5):
        rrect(ctx, x - w / 2, y - 30 + k * 14, w, 7, 3); ctx.set_source_rgb(*col); ctx.fill()


def air_arrows(ctx, x0, x1, y, t, col, a=1.0):
    for k in range(5):
        ph = (t * 0.8 + k / 5) % 1
        px = x0 + (x1 - x0) * ph
        yy = y + math.sin(ph * 6 + k) * 14
        ctx.move_to(px - 30, yy); ctx.line_to(px + 20, yy)
        ctx.set_source_rgba(*col, a * math.sin(ph * math.pi)); ctx.set_line_width(7); ctx.stroke()
        ctx.move_to(px + 8, yy - 14); ctx.line_to(px + 26, yy); ctx.line_to(px + 8, yy + 14); ctx.stroke()


def wind_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col)
    ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k, L in enumerate((70, 50, 60)):
        yy = -26 + k * 26
        ctx.move_to(-40, yy); ctx.line_to(-40 + L, yy); ctx.stroke()
    ctx.restore()


def hatch_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(8)
    ctx.rectangle(-40, -10, 80, 50); ctx.stroke()
    ctx.move_to(-30, -10); ctx.line_to(10, -44); ctx.line_to(40, -10); ctx.stroke(); ctx.restore()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tst = wt(0, "stopped"); tph = wt(0, "phone"); tsg = wt(0, "signal")
    if tl < tph - 0.1:
        bg(ctx, tg, RED, 0.18)
        headline(ctx, "between floors...", [("The lift", WHT), ("STOPS", RED)], 1.0)
        jolt = 6 * math.exp(-max(0, tl - tst) * 5) if tl > tst - 0.05 else 0
        flick = 0.3 + 0.7 * (1 if (tl * 7) % 1 > 0.25 else 0)
        lift_box(ctx, 540, 840, 500, 680, 1.0, RED if tl > tst - 0.05 else BLU,
                 label="STUCK" if tl > tst - 0.05 else "8", light=flick, shake=jolt, t=tl)
        if tl > tst - 0.05:
            stamp(ctx, "STUCK", 800, 600, tl - tst + 0.05, RED, 60, 0.12)
    else:
        tt = tl - tph + 0.1
        bg(ctx, tg, RED, 0.22)
        headline(ctx, "and your phone has...", [("0", RED), ("bars", WHT)], tt)
        phone(ctx, 540, 820, 1.35, tl, 0, tt)
        if tl > tsg - 0.1:
            stamp(ctx, "NO SIGNAL", 540, 1180, tl - tsg + 0.1, RED, 64, -0.06)


def s1(ctx, tg, tl, T):
    tp = wt(1, "pry"); td = wt(1, "Don"); tf = wt(1, "Four"); t3 = wt(1, "three"); tfe = wt(1, "fear")
    if tl < td - 0.05:
        bg(ctx, tg, YEL, 0.14)
        headline(ctx, "your first instinct", [("Pry the", WHT), ("doors?", YEL)], tl)
        o = 0.12 * ease_out(clamp((tl - tp + 0.2) / 1.0))
        lift_box(ctx, 540, 840, 500, 680, 1.0, YEL, open_=o, light=0.6)
        g = 150 * o
        hand(ctx, 540 - g - 62, 860, 1, clamp(tl / 0.3))
        hand(ctx, 540 + g + 62, 960, -1, clamp(tl / 0.3))
    elif tl < tf - 0.1:
        tt = tl - td + 0.05
        bg(ctx, tg, RED, 0.18)
        headline(ctx, "the lift may be", [("between", RED), ("floors", WHT)], tt)
        card(ctx, 540, 840, 680, 680, RED, 1.0, glow=0.6)
        # shaft cross-section: two floor slabs, the car stuck half way
        for fy, lab in ((620, "FLOOR 8"), (1000, "FLOOR 7")):
            ctx.rectangle(220, fy, 300, 26); ctx.set_source_rgb(0.5, 0.52, 0.6); ctx.fill()
            say(ctx, lab, 260, fy - 30, 30, GREY, align="l")
        ctx.rectangle(220, 646, 300, 354); ctx.set_source_rgb(0.3, 0.27, 0.24); ctx.fill()
        say(ctx, "WALL", 370, 820, 40, (0.55, 0.5, 0.45))
        rrect(ctx, 560, 700, 240, 300, 16); ctx.set_source_rgb(*STEEL); ctx.fill()
        say(ctx, "LIFT", 680, 850, 48, WHT)
        ctx.move_to(680, 470); ctx.line_to(680, 700); ctx.set_source_rgb(0.55, 0.58, 0.68); ctx.set_line_width(6); ctx.stroke()
        stamp(ctx, "DON'T!", 540, 1130, tt, RED, 72, -0.08)
    else:
        tt = tl - tf + 0.1
        bg(ctx, tg, GRN, 0.12)
        headline(ctx, "instead", [("4 calm", GRN), ("moves", WHT)], tt)
        items = [("Door open", door_open_icon), ("Alarm", bell), ("???", wind_icon), ("Stay inside", door)]
        on3 = tl > t3 - 0.1
        for k, (lab, ic) in enumerate(items):
            numcard(ctx, 540, 545 + k * 178, 640, 158, k + 1, lab if (k != 2 or tl > tfe) else "???", tt - 0.2 - k * 0.22,
                    on=(k == 2 and on3), col=PUR if k == 2 else GRN, icon=ic)
        if on3:
            stamp(ctx, "BIGGEST FEAR", 760, 900, tl - t3 + 0.1, PUR, 40, 0.08)


def s2(ctx, tg, tl, T):
    tdo = wt(2, "door"); tso = wt(2, "Sometimes"); tfl = wt(2, "floor")
    bg(ctx, tg, GRN, 0.14)
    if tl < tso - 0.1:
        headline(ctx, "one", [("Press", WHT), ("door open", GRN)], tl)
        card(ctx, 540, 840, 520, 640, GRN, tl, glow=0.6)
        say(ctx, "PANEL", 540, 580, 30, GREY)
        pr = tl > tdo - 0.05
        button(ctx, 430, 760, 70, GRN, pr, door_open_icon)
        button(ctx, 650, 760, 70, (0.6, 0.62, 0.7), False, lambda c, x, y, s, col: say(c, "> <", x, y, 40, col))
        button(ctx, 430, 960, 70, YEL, False, bell)
        button(ctx, 650, 960, 70, BLU, False, lambda c, x, y, s, col: say(c, "8", x, y, 60, col))
        if pr:
            ph = clamp((tl - tdo) / 0.3)
            ctx.arc(430, 760, 70 + 60 * ph, 0, 6.3); ctx.set_source_rgba(*GRN, 1 - ph); ctx.set_line_width(6); ctx.stroke()
            pill(ctx, "door open", 540, 1180, tl - tdo, GRN, 40, icon=door_open_icon)
    else:
        tt = tl - tso + 0.1
        headline(ctx, "sometimes you're", [("right at a", WHT), ("floor", GRN)], tt)
        o = ease_io(clamp((tl - tfl + 0.2) / 0.8))
        lift_box(ctx, 540, 840, 500, 680, tt, GRN, open_=o, label="FLOOR 7")
        if o > 0.6:
            stamp(ctx, "OPEN!", 800, 600, tl - tfl - 0.4, GRN, 60, 0.1)
            tick(ctx, 540, 1010, 90 * clamp((o - 0.6) / 0.3), GRN)


def s3(ctx, tg, tl, T):
    tal = wt(3, "alarm"); tli = wt(3, "lift"); tbe = wt(3, "bell"); tin = wt(3, "intercom")
    bg(ctx, tg, YEL, 0.15)
    if tl < tli - 0.1:
        headline(ctx, "two", [("Press the", WHT), ("alarm", YEL)], tl)
        card(ctx, 540, 840, 520, 640, YEL, tl, glow=0.7)
        pr = tl > tal - 0.05
        s = 1 + 0.06 * math.sin(tl * 20) if pr else 1
        button(ctx, 540, 820, 140 * s, YEL, pr, bell)
        if pr:
            waves(ctx, 700, 820, tl, YEL, d=1); waves(ctx, 380, 820, tl, YEL, d=-1)
            stamp(ctx, "RING!", 780, 600, tl - tal, ORG, 56, 0.12)
    else:
        tt = tl - tli + 0.1
        headline(ctx, "built into the lift", [("Its own", WHT), ("bell + intercom", YEL)], tt)
        card(ctx, 330, 840, 380, 520, YEL, tt, glow=0.7)
        if tt > 0:
            bell(ctx, 330, 790, 160, YEL)
            say(ctx, "BELL", 330, 990, 46, WHT)
        card(ctx, 750, 840, 380, 520, YEL if tl > tin - 0.2 else (0.25, 0.27, 0.35), tl - tin + 0.25, glow=0.7)
        if tl > tin - 0.25:
            for r in range(4):
                for c in range(4):
                    ctx.arc(705 + c * 30, 745 + r * 30, 8, 0, 6.3)
            ctx.set_source_rgb(*YEL); ctx.fill()
            waves(ctx, 830, 790, tl, YEL)
            say(ctx, "INTERCOM", 750, 990, 46, WHT)
        pill(ctx, "no phone needed", 540, 1180, tl - tin - 0.5, GRN, 40, icon=tick)


def s4(ctx, tg, tl, T):
    tbr = wt(4, "breathe"); tno = wt(4, "not"); tair = wt(4, "air"); tli = wt(4, "Lifts"); tve = wt(4, "vents")
    if tl < tno - 0.1:
        bg(ctx, tg, PUR, 0.16)
        headline(ctx, "three", [("Breathe", PUR), ("slowly", WHT)], tl)
        card(ctx, 540, 840, 560, 640, PUR, tl, glow=0.7)
        r = 110 + 70 * (0.5 - 0.5 * math.cos(tl * 2.4))
        ctx.arc(540, 820, r, 0, 6.3); ctx.set_source_rgba(*PUR, 0.35); ctx.fill()
        ctx.arc(540, 820, r, 0, 6.3); ctx.set_source_rgb(*PUR); ctx.set_line_width(6); ctx.stroke()
        say(ctx, "IN... OUT", 540, 820, 50, WHT)
    elif tl < tli - 0.1:
        tt = tl - tno + 0.1
        bg(ctx, tg, RED, 0.16)
        headline(ctx, "the biggest fear", [("Run out of", WHT), ("air?", RED)], 1.0)
        card(ctx, 540, 820, 600, 560, (0.25, 0.27, 0.35), 1.0, glow=0)
        lvl = 1 - 0.75 * ease_out(clamp(tt / 0.8))
        rrect(ctx, 300, 760, 480, 70, 35); ctx.set_source_rgba(1, 1, 1, 0.1); ctx.fill()
        rrect(ctx, 300, 760, 480 * lvl, 70, 35); ctx.set_source_rgb(*RED); ctx.fill()
        say(ctx, "AIR", 540, 680, 50, GREY)
        if tl > tair - 0.05:
            stamp(ctx, "MYTH", 540, 960, tl - tair + 0.05, GRN, 110, -0.1)
    else:
        tt = tl - tli + 0.1
        bg(ctx, tg, BLU, 0.16)
        headline(ctx, "air moves in and out", [("Built-in", WHT), ("air vents", BLU)], tt)
        card(ctx, 540, 840, 640, 640, BLU, tt, glow=0.7)
        rrect(ctx, 340, 620, 400, 480, 20); ctx.set_source_rgb(*STEEL); ctx.fill()
        a = clamp((tl - tve + 0.3) / 0.3)
        for vx, vy in ((540, 660), (540, 1060)):
            vent(ctx, vx, vy, 160, (0.4 + 0.6 * a * BLU[0], 0.42 + 0.58 * a * BLU[1], 0.5 + 0.5 * a))
        air_arrows(ctx, 240, 840, 720, tl, BLU, a)
        air_arrows(ctx, 240, 840, 1000, tl + 0.5, BLU, a)
        person_icon(ctx, 540, 880, 170, WHT)
        pill(ctx, "plenty of air", 540, 1220, tl - tve - 0.3, GRN, 40, icon=tick)


def s5(ctx, tg, tl, T):
    tst = wt(5, "stay"); twa = wt(5, "wait"); tmo = wt(5, "moving"); tha = wt(5, "hatch")
    tre = wt(5, "rescuers"); tau = wt(5, "heroes")
    if tl < tmo - 0.3:
        bg(ctx, tg, GRN, 0.14)
        headline(ctx, "four", [("Stay inside", GRN), ("and wait", WHT)], tl)
        lift_box(ctx, 540, 840, 500, 680, tl, GRN, label="SAFEST")
        person_icon(ctx, 540, 960, 200, WHT)
        if tl > twa - 0.1:
            pill(ctx, "help is coming", 540, 1210, tl - twa + 0.1, GRN, 40, icon=clock)
    elif tl < tha - 0.3:
        tt = tl - tmo + 0.3
        bg(ctx, tg, ORG, 0.16)
        headline(ctx, "why stay inside?", [("It could", WHT), ("move again", ORG)], tt)
        dy = 30 * math.sin(tl * 9) * clamp(tt / 0.3)
        ctx.save(); ctx.translate(0, dy)
        lift_box(ctx, 540, 840, 420, 560, 1.0, ORG, label="MOVING")
        ctx.restore()
        for d in (-1, 1):
            y0 = 840 + d * 360
            ctx.move_to(540, y0 - d * 40); ctx.line_to(540, y0 + d * 20)
            ctx.set_source_rgb(*ORG); ctx.set_line_width(10); ctx.stroke()
            ctx.move_to(510, y0); ctx.line_to(540, y0 + d * 40); ctx.line_to(570, y0); ctx.close_path(); ctx.fill()
        pill(ctx, "at any time", 880, 1000, tt - 0.3, ORG, 36)
    else:
        tt = tl - tha + 0.3
        bg(ctx, tg, RED, 0.14)
        headline(ctx, "that roof hatch?", [("For", WHT), ("rescuers", RED), ("only", WHT)], tt)
        card(ctx, 540, 860, 600, 640, RED, tt, glow=0.6)
        rrect(ctx, 340, 640, 400, 500, 18); ctx.set_source_rgb(*STEEL); ctx.fill()
        rrect(ctx, 460, 610, 160, 36, 8); ctx.set_source_rgb(*RED); ctx.fill()
        say(ctx, "HATCH", 540, 628, 24, WHT)
        rrect(ctx, 440, 596, 200, 50, 10); ctx.set_source_rgb(*RED); ctx.fill()
        say(ctx, "HATCH", 540, 621, 30, WHT)
        climb = 50 * math.sin(clamp((tl - tha) / 1.0) * math.pi)
        person_icon(ctx, 540, 1020 - climb, 200, YEL)
        ctx.move_to(540, 900 - climb); ctx.line_to(540, 690)
        ctx.set_source_rgb(*YEL); ctx.set_line_width(10); ctx.set_dash([18, 14]); ctx.stroke(); ctx.set_dash([])
        ctx.move_to(510, 715); ctx.line_to(540, 675); ctx.line_to(570, 715); ctx.close_path(); ctx.fill()
        if tl > tre - 0.1:
            ctx.arc(540, 790, 70, 0, 6.3); ctx.set_source_rgb(*RED); ctx.fill()
            xmark(ctx, 540, 790, 90, WHT)
        if tl > tau - 0.3:
            stamp(ctx, "NOT AN ACTION MOVIE", 540, 1225, tl - tau + 0.3, PUR, 40, -0.05)


def s6(ctx, tg, tl, T):
    tve = wt(6, "vents"); tc = wt(6, "Comment"); ty = wt(6, "yes"); tn = wt(6, "no", 1)
    bg(ctx, tg, BLU, 0.14)
    headline(ctx, "comment below", [("Knew about the", WHT), ("air vents?", BLU)], tl)
    card(ctx, 540, 640, 420, 260, BLU, tl, glow=0.6)
    vent(ctx, 540, 630, 220, BLU)
    air_arrows(ctx, 360, 720, 640, tl, WHT, 0.6)
    for k, (lab, col, t0) in enumerate((("YES", GRN, ty), ("NO", RED, tn))):
        x = 330 + k * 420
        card(ctx, x, 960, 340, 200, col, tl - t0 + 0.15, glow=0.9)
        if tl > t0 - 0.15:
            say(ctx, lab, x, 960, 100, col)
    if tl < ty - 0.15:
        pill(ctx, "tell us below", 540, 960, tl - tc + 0.1, YEL, 44)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def _hum(A, t, d, g=0.12):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    x = (np.sin(2 * np.pi * 100 * tt) + 0.5 * np.sin(2 * np.pi * 200 * tt)) * np.minimum(1, tt / 0.1) * np.minimum(1, (d - tt) / 0.1)
    A.add(A.sfx_buf, x, t, g)


def _clunk(A, t, g=0.6):
    import numpy as np
    d = 0.4; n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.lp(A.noise(d), 600) * np.exp(-tt * 18) + np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 12)
    A.add(A.sfx_buf, x, t, g)


def _bell(A, t, d=1.0, g=0.06):
    for k in range(int(d / 0.06)):
        A.ding(t + k * 0.06, g, 1760 if k % 2 else 1568, 0.08)


def sfx(A):
    t_st = A.W(0, "stopped")
    _hum(A, 0.0, t_st - 0.05, 0.1)
    _clunk(A, t_st - 0.05)
    A.thump(t_st, 0.5, 55)
    A.whoosh(A.W(0, "phone") - 0.1, 0.15, 0.3)
    A.ding(A.W(0, "signal"), 0.06, 392)
    A.whoosh(A.S(1), 0.15, 0.3)
    A.thump(A.W(1, "Don") - 0.03, 0.6, 60)
    for k in range(4):
        A.pop(A.W(1, "Four") + 0.1 + k * 0.22, 0.15)
    A.boing(A.W(1, "three"), 0.12, 320)
    A.pop(A.W(2, "door"), 0.35)
    A.whoosh(A.W(2, "floor") - 0.1, 0.2, 0.6)
    A.ding(A.W(2, "floor") + 0.3, 0.07, A.note(79))
    A.pop(A.W(3, "alarm"), 0.35)
    _bell(A, A.W(3, "alarm") + 0.05, 0.9, 0.05)
    A.whoosh(A.W(3, "lift") - 0.1, 0.15, 0.3)
    A.pop(A.W(3, "intercom"), 0.25)
    A.whoosh(A.W(4, "breathe"), 0.12, 1.2)
    A.thump(A.W(4, "air") - 0.03, 0.6, 60)
    A.whoosh(A.W(4, "Lifts") - 0.1, 0.15, 0.6)
    A.pop(A.W(5, "stay"), 0.3)
    _hum(A, A.W(5, "moving") - 0.3, 1.2, 0.08)
    A.whoosh(A.W(5, "hatch") - 0.3, 0.15, 0.3)
    A.pop(A.W(5, "rescuers"), 0.3)
    A.boing(A.W(5, "heroes"), 0.12, 260, 0.6)
    A.pop(A.W(6, "yes"), 0.3); A.pop(A.W(6, "no", 1), 0.3)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(6, "Comment") + 0.1 + k * 0.1, 0.06, A.note(m))

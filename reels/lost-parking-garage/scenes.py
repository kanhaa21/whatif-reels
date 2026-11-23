"""Scenes for "What if you got lost in a parking garage?" (card style, English, female voice).
Everyday-emergencies queue, topic 4. Injected by reelkit.make before this runs: wt(line_i, word), TL, SCRIPT.

Scale: top views use 39 px per metre (a 4.4 m car is 171 px long, a 2.5 m bay is 98 px wide,
a person's shoulders are about 0.5 m = 20 px)."""
import math
import cairo
from reelkit.lib import clamp, ease_out, ease_io, pop, rrect, hrand, W, H
from reelkit.cards import *  # noqa: F401,F403

NO_FLASH = tuple(range(10))
PXM = 39                       # px per metre in the top views
FLOOR = (0.13, 0.135, 0.15)
DARK = (0.02, 0.02, 0.03)
CARC = (0.55, 0.57, 0.62)     # parked cars: all the same grey
HUNT = (0.75, 0.2, 0.25)      # the circling car
MINE = (0.3, 0.55, 1.0)       # your car
P_S = 0.5 * PXM / 68 * 100    # dot_person size for 0.5 m shoulders


def cut_times(i):
    try:
        return {0: [0, wt(0, "And") - 0.1],
                1: [0, wt(1, "But") - 0.1, wt(1, "Four") - 0.1],
                2: [0], 3: [0, wt(3, "phone") - 0.1], 4: [0, wt(4, "honks") - 0.15],
                5: [0], 6: [0]}.get(i, [0])
    except KeyError:
        return [0]


def blink(t, hz=2.2):
    return (t * hz) % 1 < 0.5


# ---------------------------------------------------------------- props
def car_top(ctx, x, y, ang, col=CARC, beam=0.0, flash=False):
    """top view of a 4.4 m x 1.8 m car at true scale; ang 0 = nose up"""
    s = 4.4 * PXM / 190
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    if beam > 0:
        g = cairo.LinearGradient(0, -95, 0, -520)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.55 * beam); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        ctx.move_to(-40, -92); ctx.line_to(40, -92); ctx.line_to(150, -520); ctx.line_to(-150, -520); ctx.close_path()
        ctx.set_source(g); ctx.fill()
    if flash:
        ctx.arc(0, 0, 210, 0, 6.3); ctx.set_source_rgba(*ORG, 0.28); ctx.fill()
    rrect(ctx, -42, -95, 84, 190, 24); ctx.set_source_rgb(*col); ctx.fill()
    rrect(ctx, -34, -52, 68, 36, 10); ctx.set_source_rgb(0.1, 0.11, 0.15); ctx.fill()
    rrect(ctx, -34, 44, 68, 26, 10); ctx.fill()
    for hx in (-30, 30):
        ctx.arc(hx, -88, 8, 0, 6.3)
        ctx.set_source_rgb(*((1, 0.95, 0.7) if beam > 0 else (0.75, 0.75, 0.7))); ctx.fill()
        rrect(ctx, hx - 9, 86, 18, 8, 3); ctx.set_source_rgb(*(ORG if flash else (0.5, 0.1, 0.1))); ctx.fill()
    ctx.restore()


def dot_person(ctx, x, y, col, ring=None, a=1.0):
    """top-view person: head and shoulders, 0.5 m wide"""
    if ring:
        ctx.arc(x, y, 26, 0, 6.3); ctx.set_source_rgba(*ring, 0.9 * a); ctx.set_line_width(4); ctx.stroke()
    ctx.save(); ctx.translate(x, y); ctx.scale(P_S / 100, P_S / 100)
    rrect(ctx, -34, -14, 68, 28, 14); ctx.set_source_rgba(*col, a); ctx.fill()
    ctx.arc(0, 0, 17, 0, 6.3); ctx.set_source_rgba(*col, a); ctx.fill()
    ctx.arc(0, 0, 17, 0, 6.3); ctx.set_source_rgba(0, 0, 0, 0.4 * a); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()


BAYS_Y = [530 + k * 98 for k in range(7)]
LANE = (350, 730)               # drive lane between the two rows of bays (about 9.7 m incl. walkway)


def garage(ctx, mine_at=None, mine_flash=False, empty=(), lights=0.25, t=0.0):
    """top view of one garage level inside the card area x 120..960, y 480..1200"""
    ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
    ctx.rectangle(120, 480, 840, 720); ctx.set_source_rgb(*FLOOR); ctx.fill()
    # ceiling lamps: pools of light
    for k, (lx, ly) in enumerate(((540, 560), (540, 900), (540, 1160))):
        g = cairo.RadialGradient(lx, ly, 0, lx, ly, 230)
        g.add_color_stop_rgba(0, 1, 0.97, 0.85, lights * (0.6 if k != 1 else 0.25)); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(g); ctx.paint()
    # bay lines
    ctx.set_source_rgba(1, 1, 1, 0.55); ctx.set_line_width(3)
    for side, x0, x1 in ((0, 130, 350), (1, 730, 950)):
        for by in BAYS_Y + [BAYS_Y[-1] + 98]:
            ctx.move_to(x0, by - 49); ctx.line_to(x1, by - 49)
        ctx.stroke()
    # lane arrows
    ctx.set_source_rgba(1, 1, 1, 0.25)
    for ay in (700, 1000):
        ctx.move_to(540, ay - 40); ctx.line_to(565, ay); ctx.line_to(550, ay); ctx.line_to(550, ay + 40)
        ctx.line_to(530, ay + 40); ctx.line_to(530, ay); ctx.line_to(515, ay); ctx.close_path(); ctx.fill()
    # parked cars, all the same grey
    for side in (0, 1):
        for k, by in enumerate(BAYS_Y):
            if (side, k) in empty: continue
            cx = 240 if side == 0 else 840
            if (side, k) == mine_at:
                car_top(ctx, cx, by, math.pi / 2 if side == 0 else -math.pi / 2, MINE, flash=mine_flash and blink(t))
            else:
                car_top(ctx, cx, by, math.pi / 2 if side == 0 else -math.pi / 2, CARC)
    # pillars (0.6 m)
    for side in (0, 1):
        px = 360 if side == 0 else 720
        for py in (530 + 49, 530 + 49 + 294):
            ctx.rectangle(px - 12, py - 12, 24, 24); ctx.set_source_rgb(0.42, 0.43, 0.47); ctx.fill()
    ctx.restore()


def pin(ctx, x, y, s, col, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(0, 50); ctx.curve_to(-20, 10, -40, -5, -40, -25); ctx.arc(0, -25, 40, math.pi, 0)
    ctx.curve_to(40, -5, 20, 10, 0, 50); ctx.close_path(); ctx.set_source_rgba(*col, a); ctx.fill()
    ctx.arc(0, -25, 15, 0, 6.3); ctx.set_source_rgba(0.08, 0.09, 0.16, a); ctx.fill()
    ctx.restore()


def pin_icon(ctx, x, y, s, col):
    pin(ctx, x, y, s * 0.9, col)


def bulb_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(8)
    ctx.arc(0, -10, 30, 0, 6.3); ctx.stroke()
    ctx.move_to(-14, 30); ctx.line_to(14, 30); ctx.move_to(-10, 42); ctx.line_to(10, 42); ctx.stroke()
    for a in range(5):
        ang = -math.pi + a * math.pi / 4
        ctx.move_to(42 * math.cos(ang), -10 + 42 * math.sin(ang)); ctx.line_to(52 * math.cos(ang), -10 + 52 * math.sin(ang))
    ctx.stroke(); ctx.restore()


def key_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(9)
    ctx.arc(-22, 0, 20, 0, 6.3); ctx.stroke()
    ctx.move_to(-2, 0); ctx.line_to(44, 0); ctx.move_to(30, 0); ctx.line_to(30, 16); ctx.move_to(42, 0); ctx.line_to(42, 12)
    ctx.stroke(); ctx.restore()


def lock_icon(ctx, x, y, s, col, opn=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col)
    rrect(ctx, -36, -6, 72, 52, 10); ctx.fill()
    ctx.set_line_width(10); ctx.arc(0, -10 - 14 * opn, 24, math.pi, 0); ctx.stroke()
    ctx.restore()


def eye_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(8)
    ctx.move_to(-46, 0); ctx.curve_to(-20, -36, 20, -36, 46, 0); ctx.curve_to(20, 36, -20, 36, -46, 0); ctx.stroke()
    ctx.arc(0, 0, 13, 0, 6.3); ctx.fill(); ctx.restore()


def fob(ctx, x, y, s, press=0.0, t=0.0):
    """car key fob with lock / unlock / red panic buttons; press = panic glow"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -90, -170, 180, 300, 70); ctx.set_source_rgb(0.1, 0.1, 0.13); ctx.fill_preserve()
    ctx.set_source_rgb(0.35, 0.36, 0.42); ctx.set_line_width(5); ctx.stroke()
    ctx.arc(0, -205, 26, 0, 6.3); ctx.set_source_rgb(0.6, 0.6, 0.65); ctx.set_line_width(8); ctx.stroke()
    for k, by in enumerate((-100, -20)):
        ctx.arc(0, by, 34, 0, 6.3); ctx.set_source_rgb(0.2, 0.21, 0.26); ctx.fill()
        lock_icon(ctx, 0, by - 4, 40, GREY, opn=float(k))
    r = 36 * (1 - 0.12 * press)
    ctx.arc(0, 68, r, 0, 6.3); ctx.set_source_rgb(*((1, 0.35, 0.35) if press > 0 else (0.7, 0.12, 0.15))); ctx.fill()
    say(ctx, "PANIC", 0, 68, 18, WHT)
    if press > 0:
        for k in range(3):
            ph = (t * 1.6 + k / 3) % 1
            ctx.arc(0, 68, 40 + ph * 120, 0, 6.3); ctx.set_source_rgba(*RED, (1 - ph) * 0.8); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()


def phone_map(ctx, x, y, s, t_pin, tl):
    """phone with a map; a pin drops at t_pin"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    w, h = 300, 560
    rrect(ctx, -w / 2, -h / 2, w, h, 40); ctx.set_source_rgb(0.12, 0.12, 0.16); ctx.fill_preserve()
    ctx.set_source_rgb(*BLU); ctx.set_line_width(5); ctx.stroke()
    rrect(ctx, -w / 2 + 14, -h / 2 + 16, w - 28, h - 32, 28); ctx.set_source_rgb(0.1, 0.13, 0.18); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    ctx.set_source_rgb(0.2, 0.25, 0.33); ctx.set_line_width(16)
    for k in range(-2, 3):
        ctx.move_to(-200, k * 110 + 20); ctx.line_to(200, k * 110 - 40); ctx.stroke()
    ctx.set_line_width(10)
    for k in range(-1, 2):
        ctx.move_to(k * 90, -300); ctx.line_to(k * 90 + 30, 300); ctx.stroke()
    ctx.rectangle(-60, -20, 120, 90); ctx.set_source_rgb(0.28, 0.3, 0.38); ctx.fill()
    say(ctx, "MALL", 0, 25, 22, GREY)
    ctx.restore()
    # you, blue dot
    ctx.arc(-70, 150, 16, 0, 6.3); ctx.set_source_rgb(*BLU); ctx.fill()
    ctx.arc(-70, 150, 16, 0, 6.3); ctx.set_source_rgb(*WHT); ctx.set_line_width(4); ctx.stroke()
    if tl > t_pin:
        p = ease_out(clamp((tl - t_pin) / 0.35))
        pin(ctx, 40, -90 - 120 * (1 - p), 110, RED, clamp((tl - t_pin) / 0.1))
        if p > 0.9:
            rrect(ctx, -110, -40, 220, 54, 14); ctx.set_source_rgba(1, 1, 1, 0.95); ctx.fill()
            say(ctx, "Parked car", 0, -13, 30, BLACK)
    ctx.restore()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tsa = wt(0, "same"); tpa = wt(0, "passed"); tth = wt(0, "three"); tti = wt(0, "times"); tan = wt(0, "And")
    if tl < tan - 0.1:
        bg(ctx, tg, RED, 0.18)
        headline(ctx, "level B3, almost empty", [("Passed you", WHT), ("3 times", RED)], 1.0)
        card(ctx, 540, 840, 840, 720, RED, 1.0, fill=DARK, glow=0.5)
        garage(ctx, empty={(0, 2), (1, 4), (1, 1)})
        ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
        dot_person(ctx, 640, 860, YEL, ring=YEL)
        # the same car drives up the lane, again and again
        lap = 1.15
        ph = (tl + 0.55) % lap / lap
        cy = 1330 - ph * 1000
        car_top(ctx, 470, cy, 0, HUNT, beam=1.0)
        ctx.restore()
        say(ctx, "YOU", 640, 820, 26, YEL)
        n = sum(tl > x for x in (tsa - 0.1, tpa - 0.1, tth - 0.1))
        for k in range(n):
            pill(ctx, f"x{k + 1}", 250 + k * 150, 1250, tl - (tsa, tpa, tth)[k] + 0.1, RED, 42)
        if tl > tti:
            stamp(ctx, "SAME CAR", 760, 600, tl - tti, RED, 52, 0.08)
    else:
        tt = tl - tan + 0.1
        bg(ctx, tg, YEL, 0.12)
        headline(ctx, "and worse", [("Where's", WHT), ("your car?", YEL)], tt)
        card(ctx, 540, 840, 840, 720, YEL, 1.0, fill=DARK, glow=0.4)
        garage(ctx, empty={(0, 2), (1, 4)})
        ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
        dot_person(ctx, 560, 840, YEL, ring=YEL)
        ctx.restore()
        for k, (qx, qy) in enumerate(((240, 628), (840, 726), (240, 922), (840, 1118), (840, 530))):
            if tl > tan + 0.15 * k:
                say(ctx, "?", qx, qy - 6 * math.sin(tl * 6 + k), 64, YEL)
        pill(ctx, "every car looks the same", 540, 1250, tt - 0.5, GREY, 36)


def s1(ctx, tg, tl, T):
    tpk = wt(1, "parking"); tbu = wt(1, "But"); tbe = wt(1, "bet"); tfo = wt(1, "Four"); tse = wt(1, "second"); tpo = wt(1, "pocket")
    if tl < tbu - 0.1:
        bg(ctx, tg, BLU, 0.12)
        headline(ctx, "maybe it's nothing", [("Just hunting", WHT), ("for parking?", BLU)], tl, size=70)
        card(ctx, 540, 840, 840, 720, BLU, 1.0, fill=DARK, glow=0.4)
        garage(ctx, empty={(0, 2), (1, 4), (1, 1)})
        ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
        cy = 1150 - 240 * ease_io(clamp(tl / 2.0))
        car_top(ctx, 470, cy, 0, HUNT, beam=1.0)
        ctx.restore()
        if tl > tpk - 0.4:
            sc = pop(tl - tpk + 0.4, 0.25)
            ctx.save(); ctx.translate(640, cy - 170); ctx.scale(sc, sc)
            rrect(ctx, -60, -60, 120, 120, 24); ctx.set_source_rgb(*BLU); ctx.fill()
            say(ctx, "P", 0, 0, 90, WHT); say(ctx, "?", 80, -40, 60, BLU)
            ctx.restore()
    elif tl < tfo - 0.1:
        tt = tl - tbu + 0.1
        bg(ctx, tg, RED, 0.2)
        headline(ctx, "but", [("Don't", RED), ("bet on it", WHT)], tt)
        card(ctx, 540, 840, 840, 720, RED, 1.0, fill=DARK, glow=0.6)
        garage(ctx, empty={(0, 2), (1, 4), (1, 1)}, lights=0.1)
        ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
        dot_person(ctx, 640, 700, YEL, ring=YEL)
        car_top(ctx, 470, 980 - 60 * ease_out(clamp(tt / 1.0)), 0, HUNT, beam=1.0)
        ctx.restore()
        if tl > tbe - 0.1:
            stamp(ctx, "STAY ALERT", 540, 1250, tl - tbe + 0.1, RED, 58, -0.05)
    else:
        tt = tl - tfo + 0.1
        bg(ctx, tg, GRN, 0.12)
        headline(ctx, "get out safely", [("4 moves", GRN)], tt)
        on2 = tl > tse - 0.1
        items = [("Walk to the light", bulb_icon), ("In your pocket?" if on2 else "???", pin_icon),
                 ("Panic button", key_icon), ("Lock up", lock_icon)]
        for k, (lab, ic) in enumerate(items):
            numcard(ctx, 540, 545 + k * 178, 640, 158, k + 1, lab, tt - 0.2 - k * 0.2,
                    on=(k == 1 and on2), col=PUR if k == 1 else GRN, icon=ic)
        if tl > tpo - 0.1:
            stamp(ctx, "IN YOUR POCKET", 640, 1190, tl - tpo + 0.1, PUR, 44, 0.06)


def s2(ctx, tg, tl, T):
    tli = wt(2, "lift"); tli2 = wt(2, "Lights"); tpe = wt(2, "People"); tgu = wt(2, "guard")
    bg(ctx, tg, GRN, 0.14)
    headline(ctx, "one", [("Walk to the", WHT), ("lift lobby", GRN)], tl)
    card(ctx, 540, 840, 840, 720, GRN, tl, fill=DARK, glow=0.5)
    if tl < 0: return
    garage(ctx, empty={(0, 2), (1, 4), (1, 1)}, lights=0.15)
    ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
    # lift lobby at the top of the lane, glowing
    lit = clamp((tl - tli + 0.2) / 0.4)
    g = cairo.RadialGradient(540, 500, 0, 540, 500, 300)
    g.add_color_stop_rgba(0, 1, 0.97, 0.8, 0.5 * lit); g.add_color_stop_rgba(1, 1, 0.97, 0.8, 0)
    ctx.set_source(g); ctx.paint()
    rrect(ctx, 430, 470, 220, 70, 10); ctx.set_source_rgb(*GRN); ctx.fill()
    say(ctx, "LIFT  EXIT", 540, 512, 30, BLACK)
    # people near the lobby
    if tl > tpe - 0.1:
        dot_person(ctx, 470, 580, WHT); dot_person(ctx, 520, 600, (0.8, 0.8, 0.9))
    if tl > tgu - 0.15:
        dot_person(ctx, 625, 585, BLU, ring=BLU)
    p = ease_io(clamp((tl - 0.3) / 2.2))
    dot_person(ctx, 600 - 20 * p, 1120 - 460 * p, YEL, ring=YEL)
    ctx.set_dash([10, 12]); ctx.move_to(600, 1120); ctx.line_to(600 - 20 * p, 1120 - 460 * p)
    ctx.set_source_rgba(*YEL, 0.6); ctx.set_line_width(4); ctx.stroke(); ctx.set_dash([])
    ctx.restore()
    if tl > tgu - 0.15:
        say(ctx, "GUARD", 720, 585, 24, BLU)
    for k, (lab, t0) in enumerate((("Lights", tli2), ("People", tpe), ("A guard", tgu))):
        pill(ctx, lab, 230 + k * 310, 1260, tl - t0 + 0.1, GRN, 36, icon=tick)


def s3(ctx, tg, tl, T):
    tma = wt(3, "maps"); tph = wt(3, "phone"); tpi = wt(3, "pinned"); tit = wt(3, "itself")
    bg(ctx, tg, PUR, 0.16)
    if tl < tph - 0.1:
        headline(ctx, "two", [("Open your", WHT), ("maps app", PUR)], tl)
    else:
        headline(ctx, "the surprise", [("Your phone", WHT), ("may know", PUR)], tl - tph + 0.1)
    phone_map(ctx, 540, 830, 1.15, tpi - 0.05, tl)
    if tl > tit - 0.1:
        stamp(ctx, "SAVED BY ITSELF", 540, 470 + 60, tl - tit + 0.1, PUR, 44, -0.06)
        pill(ctx, "if paired with your car", 540, 1250, tl - tit - 0.3, GREY, 34)


def s4(ctx, tg, tl, T):
    tpa = wt(4, "panic"); tke = wt(4, "key"); tho = wt(4, "honks"); tde = wt(4, "Delhi")
    if tl < tho - 0.15:
        bg(ctx, tg, RED, 0.16)
        headline(ctx, "three", [("Press", WHT), ("panic", RED)], tl)
        card(ctx, 540, 820, 640, 680, RED, tl, glow=0.5)
        pr = 1.0 if tl > tke else 0.0
        fob(ctx, 540, 860, 1.5, pr, tl - tke)
        if tl > tpa - 0.1:
            pill(ctx, "car alarm, on purpose", 540, 1240, tl - tpa + 0.1, RED, 36)
    else:
        tt = tl - tho + 0.15
        bg(ctx, tg, ORG, 0.16)
        headline(ctx, "found it", [("HONK", ORG), ("HONK", WHT)], tt)
        card(ctx, 540, 840, 840, 720, ORG, 1.0, fill=DARK, glow=0.5)
        garage(ctx, mine_at=(1, 5), mine_flash=True, empty={(0, 2), (1, 4)}, lights=0.2, t=tl)
        ctx.save(); rrect(ctx, 120, 480, 840, 720, 26); ctx.clip()
        dot_person(ctx, 560, 640, YEL, ring=YEL)
        for k in range(3):
            ph = (tl * 1.4 + k / 3) % 1
            ctx.arc(840, BAYS_Y[5], 60 + ph * 260, 0, 6.3); ctx.set_source_rgba(*ORG, (1 - ph) * 0.7); ctx.set_line_width(6); ctx.stroke()
        ctx.restore()
        say(ctx, "YOUR CAR", 840, BAYS_Y[5] - 80, 28, MINE)
        if tl > tde - 0.1:
            pill(ctx, "Delhi traffic mode", 540, 1250, tl - tde + 0.1, ORG, 40)


def s5(ctx, tg, tl, T):
    tke = wt(5, "keys"); tba = wt(5, "back"); tge = wt(5, "Get"); tlo = wt(5, "Lock")
    bg(ctx, tg, GRN, 0.14)
    headline(ctx, "four", [("Keys in hand.", WHT), ("Lock up", GRN)], tl, size=70)
    items = [("Keys in hand", key_icon, tke), ("Check back seat", eye_icon, tba), ("Get in", tick, tge)]
    for k, (lab, ic, t0) in enumerate(items):
        y = 560 + k * 175
        card(ctx, 540, y, 700, 145, GRN if tl > t0 - 0.1 else (0.22, 0.23, 0.3), tl - t0 + 0.2, glow=0.6, r=24)
        if tl > t0 - 0.2:
            ic(ctx, 280, y, 70, GRN)
            say(ctx, lab, 360, y, 50, WHT, align="l")
    if tl > tlo - 0.15:
        tt = tl - tlo + 0.15
        card(ctx, 540, 1110, 460, 200, GRN, tt, glow=0.9)
        lock_icon(ctx, 400, 1115, 110, GRN, opn=1 - ease_out(clamp(tt / 0.3)))
        say(ctx, "LOCKED", 590, 1110, 64, GRN)


def s6(ctx, tg, tl, T):
    tc = wt(6, "Comment"); ty = wt(6, "yes"); tn = wt(6, "no", 1)
    bg(ctx, tg, PUR, 0.14)
    headline(ctx, "comment below", [("Knew your", WHT), ("phone pins it?", PUR)], tl, size=70)
    card(ctx, 540, 640, 420, 260, PUR, tl, glow=0.6)
    if tl > 0:
        pin(ctx, 540, 650, 150, RED)
    for k, (lab, col, t0) in enumerate((("YES", GRN, ty), ("NO", RED, tn))):
        x = 330 + k * 420
        card(ctx, x, 960, 340, 200, col, tl - t0 + 0.15, glow=0.9)
        if tl > t0 - 0.15:
            say(ctx, lab, x, 960, 100, col)
    if tl < ty - 0.15:
        pill(ctx, "tell us below", 540, 960, tl - tc + 0.1, YEL, 44)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def _engine_pass(A, t, d=0.9, g=0.18):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    f = 70 + 20 * np.sin(np.pi * tt / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / 44100) * np.sin(np.pi * tt / d) ** 2
    A.add(A.sfx_buf, x, t, g)


def _honk(A, t, n=3, g=0.12):
    for k in range(n):
        A.ding(t + k * 0.32, g, 415, 0.22); A.ding(t + k * 0.32, g * 0.8, 523, 0.22)


def sfx(A):
    A.thump(0.02, 0.5, 55)
    for w in ("same", "passed", "three"):
        _engine_pass(A, A.W(0, w) - 0.3)
    A.thump(A.W(0, "times"), 0.4, 60)
    A.whoosh(A.W(0, "And") - 0.1, 0.15, 0.6)
    A.boing(A.W(1, "parking"), 0.1, 300)
    A.thump(A.W(1, "But") - 0.05, 0.5, 58)
    for k in range(4):
        A.pop(A.W(1, "Four") + 0.1 + k * 0.2, 0.15)
    A.ding(A.W(1, "pocket"), 0.07, A.note(79))
    A.whoosh(A.W(2, "walk") - 0.1, 0.12, 0.8)
    for w in ("Lights", "People", "guard"):
        A.pop(A.W(2, w), 0.25)
    A.pop(A.W(3, "maps"), 0.25)
    for k, m in enumerate((72, 76, 79)):
        A.ding(A.W(3, "pinned") + k * 0.1, 0.06, A.note(m))
    A.pop(A.W(4, "key"), 0.4)
    _honk(A, A.W(4, "honks") - 0.1)
    A.pop(A.W(5, "keys"), 0.25); A.pop(A.W(5, "back"), 0.25); A.pop(A.W(5, "Get"), 0.25)
    A.thump(A.W(5, "Lock"), 0.45, 70)
    A.pop(A.W(6, "yes"), 0.3); A.pop(A.W(6, "no", 1), 0.3)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(6, "Comment") + 0.1 + k * 0.1, 0.06, A.note(m))

"""Scenes for "What if your lift cable snapped on the 40th floor?" (v2, card style).
Owner's reference style (20 Nov 2026): near-black screen, grey kicker over a bold headline with one accent word,
neon UI cards, numbered step cards, a slammed stamp, small captions. Hinglish, female voice.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT."""
import math
import cairo
from reelkit.lib import clamp, ease_out, ease_io, pop, rrect, hrand, W, H
from reelkit.cards import *  # noqa: F401,F403

MUSIC = {"beat_from_scene": 2, "bpm": 112}
NO_FLASH = tuple(range(10))


def cut_times(i):
    try:
        return {1: [0, wt(1, "three") - 0.1], 2: [0, wt(2, "Just") - 0.1],
                4: [0, wt(4, "Myth") - 0.05]}.get(i, [0])
    except KeyError:
        return [0]


# ---------------------------------------------------------------- lift mockup (screen px)
def lift_card(ctx, x, y, tt, floor, snapped=-1.0, drop=0.0, shake=0.0, t=0.0, border=BLU):
    """tall UI card showing the lift: red header, floor display, doors; cables above it"""
    sx = shake * math.sin(t * 70)
    w, h = 400, 560
    top = y - h / 2 + drop
    # cables
    for k in range(6):
        cx = x - 75 + k * 30 + sx
        if k == 2 and snapped >= 0:
            whip = math.sin(snapped * 14) * 22 * math.exp(-snapped * 2.5)
            ctx.move_to(cx, top - 4); ctx.curve_to(cx + whip, top - 60, cx - 40, top - 90, cx - 30 + whip, top - 50)
            ctx.set_source_rgb(*RED); ctx.set_line_width(6); ctx.stroke()
            up = 120 + 200 * ease_out(snapped / 0.4)
            ctx.move_to(cx, 440); ctx.line_to(cx + whip * 0.4, max(445, top - up)); ctx.stroke()
            continue
        ctx.move_to(cx, 440); ctx.line_to(cx, top - 4)
        ctx.set_source_rgb(0.55, 0.58, 0.68); ctx.set_line_width(6); ctx.stroke()
    ctx.save(); ctx.translate(sx, drop)
    card(ctx, x, y, w, h, RED if snapped >= 0 else border, tt, glow=0.8)
    if tt >= 0:
        rrect(ctx, x - w / 2 + 14, y - h / 2 + 14, w - 28, 70, 20); ctx.set_source_rgb(*RED); ctx.fill()
        say(ctx, "LIFT", x - w / 2 + 40, y - h / 2 + 49, 34, WHT, align="l")
        say(ctx, "MAX 8 PERSONS", x + w / 2 - 40, y - h / 2 + 49, 22, WHT, bold=False, align="r")
        # floor display
        rrect(ctx, x - 120, y - 170, 240, 120, 20); ctx.set_source_rgb(0.01, 0.01, 0.02); ctx.fill()
        say(ctx, str(floor), x + 20, y - 110, 84, RED if snapped >= 0 else YEL)
        if snapped >= 0:
            ctx.move_to(x - 95, y - 130); ctx.line_to(x - 55, y - 130); ctx.line_to(x - 75, y - 90); ctx.close_path()
            ctx.set_source_rgb(*RED); ctx.fill()
        # doors
        for d in (-1, 1):
            rrect(ctx, x + (d - 1) * 75 + (5 if d > 0 else 0), y - 20, 145, 260, 10)
            ctx.set_source_rgb(0.16, 0.17, 0.23); ctx.fill()
    ctx.restore()


def speedlines(ctx, t, a=1.0, x0=200, x1=880):
    for k in range(14):
        x = x0 + hrand("sl", k) * (x1 - x0)
        y = ((hrand("sy", k) * H - t * 2400) % 700) + 450
        ctx.move_to(x, y); ctx.line_to(x, y + 120)
        ctx.set_source_rgba(1, 1, 1, 0.18 * a); ctx.set_line_width(3); ctx.stroke()


def bar(ctx, y, label, frac, col, tt, val):
    if tt < 0: return
    f = frac * ease_out(tt / 0.5)
    say(ctx, label, 150, y - 50, 38, WHT, align="l")
    say(ctx, val, 930, y - 50, 38, col, align="r")
    rrect(ctx, 150, y - 18, 780, 36, 18); ctx.set_source_rgba(1, 1, 1, 0.1); ctx.fill()
    rrect(ctx, 150, y - 18, max(36, 780 * f), 36, 18); ctx.set_source_rgb(*col); ctx.fill()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tsn = wt(0, "Snap"); tca = wt(0, "cable")
    snapped = tl >= tsn - 0.05
    ts = tl - tsn + 0.05
    bg(ctx, tg, RED if snapped else BLU, 0.22 if snapped else 0.14)
    drop = 0
    if tl > tca - 0.1:
        drop = 90 * ease_io((tl - tca + 0.1) / 1.2)
        speedlines(ctx, tl, clamp((tl - tca) / 0.3))
    floor = 40 - (int((tl - tca + 0.1) * 6) if tl > tca - 0.1 else 0)
    lift_card(ctx, 540, 820, 1.0, floor, ts if snapped else -1, drop, 4 * math.exp(-max(0, ts) * 4) if snapped else 0, tl)
    headline(ctx, "40th floor...", [("The lift cable", WHT), ("SNAPS", RED)], 1.0)
    if snapped:
        stamp(ctx, "SNAP!", 800, 640, ts, RED, 80, 0.12)


def s1(ctx, tg, tl, T):
    tp = wt(1, "three"); t170 = wt(1, "170"); tte = wt(1, "third")
    if tl < tp - 0.1:
        bg(ctx, tg, RED, 0.18)
        headline(ctx, "in free fall", [("170 km/h", RED), ("in", WHT), ("5 sec", BLU)], tl)
        f = clamp(tl / max(0.6, t170 + 0.4))
        card(ctx, 330, 800, 380, 330, BLU, tl - 0.1)
        say(ctx, f"{4.9 * ease_io(f):.1f}s", 330, 770, 110, BLU)
        say(ctx, "free fall", 330, 880, 34, GREY, bold=False)
        card(ctx, 750, 800, 380, 330, RED, tl - 0.35)
        if tl > 0.35:
            say(ctx, f"{int(172 * ease_io(f))}", 750, 770, 110, RED)
            say(ctx, "km/h", 750, 880, 34, GREY, bold=False)
        pill(ctx, "if nothing stops it", 540, 1100, tl - t170 - 0.4, YEL, 40)
    else:
        tt = tl - tp + 0.1
        bg(ctx, tg, GRN, 0.12)
        headline(ctx, "but", [("3 things", GRN), ("save you", WHT)], tt)
        on3 = tl > tte - 0.1
        items = [("Cables", cable_icon, BLU), ("Brakes", brake_icon, ORG), ("You?", person_icon, YEL)]
        for k, (lab, ic, col) in enumerate(items):
            numcard(ctx, 540, 560 + k * 215, 620, 185, k + 1, lab, tt - 0.25 - k * 0.3, on=(k == 2 and on3) or (k < 2 and not on3), col=col, icon=ic)
        if on3:
            stamp(ctx, "YOU!", 860, 1000, tl - tte + 0.1, PUR, 60, 0.1)


def s2(ctx, tg, tl, T):
    te = wt(2, "Just"); tc = wt(2, "cables")
    bg(ctx, tg, BLU, 0.15)
    one = tl > te - 0.1
    headline(ctx, "one", [("Up to 8", BLU), ("cables", WHT)] if not one else [("One cable", GRN), ("is enough", WHT)], tl if not one else tl - te + 0.1)
    card(ctx, 540, 840, 640, 680, GRN if one else BLU, tl, glow=0.6)
    # lift hanging from 6 cables
    ly = 980
    for k in range(6):
        x = 540 - 125 + k * 50
        cut = k == 2
        keep = (k == 3) if one else not cut
        col = RED if cut else (GRN if keep else (0.3, 0.32, 0.4))
        if cut:
            ctx.move_to(x, 540); ctx.line_to(x, 700); ctx.move_to(x, 760); ctx.line_to(x, ly - 120)
        else:
            ctx.move_to(x, 540); ctx.line_to(x, ly - 120)
        ctx.set_source_rgb(*col); ctx.set_line_width(12 if (one and keep) else 8); ctx.stroke()
        a = clamp((tl - tc + 0.1 - k * 0.08) / 0.15)
        if a > 0 and not one:
            ctx.arc(x, 650, 20 * a, 0, 6.3); ctx.set_source_rgb(*(RED if cut else GRN)); ctx.fill()
            (xmark if cut else tick)(ctx, x, 650, 26 * a, BLACK)
    rrect(ctx, 540 - 170, ly - 120, 340, 260, 24); ctx.set_source_rgb(0.18, 0.2, 0.3); ctx.fill()
    say(ctx, "LIFT", 540, ly + 10, 60, WHT)
    if not one:
        pill(ctx, "1 snapped", 330, 1240, tl - tc - 0.3, RED, 38)
        pill(ctx, "5 holding", 750, 1240, tl - tc - 0.55, GRN, 38)
    else:
        pill(ctx, "holds the whole lift", 540, 1240, tl - te + 0.3, GRN, 40, icon=bolt)


def s3(ctx, tg, tl, T):
    tsp = wt(3, "fast"); tj = wt(3, "grab")
    stopped = tl > tj
    bg(ctx, tg, ORG if stopped else RED, 0.15)
    headline(ctx, "two", [("Safety", ORG), ("brakes", WHT)], tl)
    card(ctx, 540, 860, 640, 720, ORG if stopped else (0.25, 0.27, 0.35), tl, glow=0.6 if stopped else 0)
    # rails
    for rx in (330, 750):
        ctx.rectangle(rx - 6, 520, 12, 680); ctx.set_source_rgb(0.6, 0.63, 0.72); ctx.fill()
    if tl < tj:
        y = 620 + ((tl * 500) % 300)
        speedlines(ctx, tl, 1.0, 360, 720)
    else:
        y = 620 + 300 + 40 * (1 - math.exp(-(tl - tj) * 10)) * math.cos((tl - tj) * 20)
        y = 860
    rrect(ctx, 370, y - 140, 340, 280, 24); ctx.set_source_rgb(0.18, 0.2, 0.3); ctx.fill()
    say(ctx, "LIFT", 540, y, 60, WHT)
    # brake shoes
    gap = 0 if stopped else 26
    for sx, rx in ((-1, 330), (1, 750)):
        bx = rx - sx * (22 + gap)
        rrect(ctx, bx - 16, y - 60, 32, 120, 8); ctx.set_source_rgb(*(ORG if stopped else (0.4, 0.42, 0.5))); ctx.fill()
        if stopped and tl - tj < 1.2:
            sparks(ctx, rx, y, tl, seed=str(sx), dirx=-sx)
    if tl > tsp - 0.1 and not stopped:
        pill(ctx, "too fast!", 540, 1250, tl - tsp + 0.1, RED, 40)
    if stopped:
        pill(ctx, "grabs the rails", 540, 1250, tl - tj, GRN, 40, icon=tick)
        stamp(ctx, "STOP", 820, 620, tl - tj, ORG, 64, 0.1)


def s4(ctx, tg, tl, T):
    tm = wt(4, "Myth"); tj = wt(4, "jump"); tf = wt(4, "movies")
    if tl < tm - 0.05:
        bg(ctx, tg, YEL, 0.12)
        headline(ctx, "three: you", [("Jump at the", WHT), ("last second?", YEL)], tl)
        card(ctx, 540, 860, 520, 700, YEL if tl > tj else (0.25, 0.27, 0.35), tl, glow=0.6)
        jump = 0
        if tl > tj - 0.1:
            jump = 160 * math.sin(math.pi * clamp((tl - tj + 0.1) / 0.8))
        person_icon(ctx, 540, 1060 - jump, 260, YEL)
        ctx.rectangle(330, 1150, 420, 8); ctx.set_source_rgb(0.5, 0.52, 0.6); ctx.fill()
        speedlines(ctx, tl, 0.8, 300, 780)
    else:
        tt = tl - tm + 0.05
        bg(ctx, tg, RED, 0.16)
        headline(ctx, "three: you", [("Jump at the", WHT), ("last second?", YEL)], 1.0)
        bar(ctx, 840, "Falling lift", 1.0, RED, tt - 0.15, "~170 km/h")
        bar(ctx, 1000, "Your jump", 0.05, GRN, tt - 0.45, "a few km/h")
        stamp(ctx, "MYTH", 540, 600, tt, RED, 120, -0.12)
        pill(ctx, "only works in movies", 540, 1170, tl - tf + 0.1, PUR, 40)


def s5(ctx, tg, tl, T):
    ta = wt(5, "alarm"); tan = wt(5, "inside"); tw_ = wt(5, "wait")
    bg(ctx, tg, GRN, 0.14)
    headline(ctx, "the real move", [("3", GRN), ("steps", WHT)], tl)
    steps = [("Press the alarm", bell, ta), ("Stay inside", door, tan), ("Wait for help", clock, tw_)]
    for k, (lab, ic, t0) in enumerate(steps):
        on = t0 - 0.1 <= tl < (steps[k + 1][2] - 0.1 if k < 2 else 99)
        numcard(ctx, 540, 560 + k * 215, 620, 185, k + 1, lab, tl - k * 0.2 if k == 0 else tl - t0 + 0.4, on=on, col=GRN, icon=ic, done=tl > t0 + 0.5)


def s6(ctx, tg, tl, T):
    tc = wt(6, "Comment"); ty = wt(6, "yes"); tn = wt(6, "no", 1)
    bg(ctx, tg, BLU, 0.14)
    headline(ctx, "comment below", [("Knew about", WHT), ("8 cables?", BLU)], tl)
    for k in range(8):
        x = 540 - 140 + k * 40
        a = clamp((tl - k * 0.05) / 0.2)
        ctx.move_to(x, 450); ctx.line_to(x, 450 + 200 * a); ctx.set_source_rgb(*BLU); ctx.set_line_width(10); ctx.stroke()
    rrect(ctx, 370, 650, 340, 60, 14); ctx.set_source_rgb(0.18, 0.2, 0.3); ctx.fill()
    for k, (lab, col, t0) in enumerate((("YES", GRN, ty), ("NO", RED, tn))):
        x = 330 + k * 420
        s = card(ctx, x, 900, 340, 200, col, tl - t0 + 0.15, glow=0.9)
        if tl > t0 - 0.15:
            say(ctx, lab, x, 900, 100, col)
    if tl < ty - 0.15:
        pill(ctx, "tell us below", 540, 900, tl - tc + 0.1, YEL, 44)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def _snap(A, t, g=0.7):
    import numpy as np
    d = 0.35; n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.hp(A.noise(d), 2500) * np.exp(-tt * 30) + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 20) * 0.6
    A.add(A.sfx_buf, x, t, g)


def _rumble(A, t, d, g=0.3):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.lp(A.noise(d), 220) * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 0.3)
    A.add(A.sfx_buf, x, t, g)


def _screech(A, t, d=0.9, g=0.12):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    f = 2600 + 300 * np.sin(2 * np.pi * 23 * tt)
    x = (np.sin(2 * np.pi * np.cumsum(f) / 44100) + 0.6 * A.bp(A.noise(d), 2000, 6000)) * np.minimum(1, tt / 0.03) * np.exp(-tt * 2.2)
    A.add(A.sfx_buf, x, t, g)


def _click(A, t, g=0.18):
    A.pop(t, g)


def sfx(A):
    t_sn = A.W(0, "Snap")
    _snap(A, t_sn - 0.05)
    A.thump(t_sn, 0.6, 55)
    _rumble(A, A.W(0, "cable") - 0.1, A.S(1) + A.W(1, "three") - A.W(0, "cable"))
    A.whoosh(A.W(0, "cable") + 0.2, 0.2, 0.5)
    _click(A, A.S(1) + 0.1); _click(A, A.S(1) + 0.35)
    A.ding(A.W(1, "170") + 0.4, 0.07, 1568)
    for k in range(3):
        _click(A, A.W(1, "three") + 0.15 + k * 0.3)
    A.boing(A.W(1, "third"), 0.12, 320)
    A.whoosh(A.S(2), 0.15, 0.3)
    for k in range(6):
        A.pop(A.W(2, "cables") + k * 0.08, 0.12)
    A.ding(A.W(2, "Just"), 0.08, A.note(79))
    A.whoosh(A.S(3), 0.15, 0.3)
    _rumble(A, A.S(3), A.W(3, "grab") - A.S(3), 0.25)
    _screech(A, A.W(3, "grab") - 0.1, 0.9)
    A.thump(A.W(3, "grab") + 0.05, 0.5, 60)
    A.whoosh(A.S(4), 0.15, 0.3)
    A.whoosh(A.W(4, "jump") + 0.1, 0.18, 0.4)
    A.thump(A.W(4, "Myth") - 0.03, 0.6, 60)
    A.boing(A.W(4, "movies"), 0.12, 260, 0.6)
    for w in ("alarm", "inside", "wait"):
        A.pop(A.W(5, w), 0.3)
    for k in range(3):
        A.ding(A.W(5, "alarm") + 0.1 + k * 0.25, 0.05, 1760, 0.25)
    A.pop(A.W(6, "yes"), 0.3); A.pop(A.W(6, "no", 1), 0.3)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(6, "Comment") + 0.1 + k * 0.1, 0.06, A.note(m))

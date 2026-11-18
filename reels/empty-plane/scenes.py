"""Scenes for "What if you woke up mid-flight and the plane was empty?". One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
No size changes in this topic, so people, seats and planes are drawn as plain cartoon shots,
with seats and cockpits sized to the people in them."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

BG = lambda ctx, tg, i: bg_glow(ctx, tg, i, dark_scenes=(0, 1))
MUSIC = {"beat_from_scene": 2, "bpm": 112}   # tense drone through the hook, storm and alarms; beat once you grab the radio

# lightning strikes (global seconds): the storm flashes through the first half, then the sky clears for the landing
EV = [0.3, 1.75, 2.9, 4.3, 5.9, 6.75, 8.4, 9.5, 10.7, 11.4, 12.5, 14.6, 16.4, 19.2, 21.5, 25.0, 28.8, 30.9, 33.2]


def flash(tg):
    f = 0.0
    for e in EV:
        d = tg - e
        if 0 <= d < 0.7:
            f = max(f, math.exp(-d * 8) * (0.55 + 0.45 * math.sin(d * 48) ** 2))
    return f

BLUE = (0.3, 0.6, 1.0)
SEATB = (0.22, 0.32, 0.75)
SEATP = (0.85, 0.28, 0.55)
NAVY = (0.08, 0.1, 0.22)
PANEL = (0.13, 0.13, 0.2)
HEROC = SHIRTS[1]


# ---------------------------------------------------------------- people bits (u = h / 100, head centre at feet - 86u)
def seated(ctx, x, fy, h, shirt=HEROC, expr="smile", arms="down", t=0.0, look=0.0, seat=SEATB, wide=1.0, hat=False, headset=False):
    u = h / 100
    # seat back + headrest
    rrect(ctx, x - 32 * u * wide, fy - 110 * u, 64 * u * wide, 84 * u, 14 * u); ctx.set_source_rgb(*seat); ctx.fill()
    rrect(ctx, x - 24 * u * wide, fy - 116 * u, 48 * u * wide, 20 * u, 9 * u)
    ctx.set_source_rgb(*[min(1, c * 1.25) for c in seat]); ctx.fill()
    person(ctx, x, fy, h, shirt, expr, arms, t, look=look)
    if hat: captain_hat(ctx, x + look * 3 * u, fy - 86 * u, u)
    if headset: headset_on(ctx, x, fy - 86 * u, u, look)
    # cushion front hides the legs, armrests
    rrect(ctx, x - 34 * u * wide, fy - 44 * u, 68 * u * wide, 48 * u, 10 * u); ctx.set_source_rgb(*[c * 0.75 for c in seat]); ctx.fill()
    for s in (-1, 1):
        rrect(ctx, x + s * 34 * u * wide - 6 * u, fy - 56 * u, 12 * u, 30 * u, 5 * u); ctx.set_source_rgb(*[c * 0.6 for c in seat]); ctx.fill()


def captain_hat(ctx, x, hy, u):
    ctx.save(); ctx.translate(x, hy)
    ctx.move_to(-17 * u, -11 * u); ctx.line_to(-20 * u, -27 * u); ctx.curve_to(-8 * u, -33 * u, 8 * u, -33 * u, 20 * u, -27 * u)
    ctx.line_to(17 * u, -11 * u); ctx.close_path(); ctx.set_source_rgb(*NAVY); ctx.fill()
    rrect(ctx, -19 * u, -14 * u, 38 * u, 6 * u, 3 * u); ctx.set_source_rgb(0.04, 0.04, 0.1); ctx.fill()
    ctx.arc(0, -21 * u, 4 * u, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()
    ctx.restore()


def headset_on(ctx, x, hy, u, look=0.0):
    ctx.save(); ctx.translate(x, hy)
    ctx.set_line_width(3.5 * u); ctx.set_source_rgb(0.12, 0.12, 0.16)
    ctx.arc(0, 0, 18 * u, math.pi * 1.05, math.pi * 1.95); ctx.stroke()
    for s in (-1, 1):
        rrect(ctx, s * 17 * u - 4.5 * u, -6 * u, 9 * u, 14 * u, 4 * u); ctx.set_source_rgb(*PNK); ctx.fill()
    ctx.set_line_width(2 * u); ctx.set_source_rgb(0.12, 0.12, 0.16)
    ctx.move_to(-16 * u, 6 * u); ctx.curve_to(-14 * u, 14 * u, -8 * u, 15 * u, -3 * u + look * 3 * u, 12 * u); ctx.stroke()
    ctx.arc(-3 * u + look * 3 * u, 12 * u, 2.2 * u, 0, 6.3); ctx.set_source_rgb(0.12, 0.12, 0.16); ctx.fill()
    ctx.restore()


def bubble(ctx, x, y, s, txt, tt, col=PNK, tail=1):
    if tt < 0: return
    sc = pop(tt, 0.2)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    w = text_w(ctx, txt, DISPLAY, s) + 60
    rrect(ctx, -w / 2, -s * 0.75, w, s * 1.5, s * 0.5); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.move_to(-tail * w * 0.15, s * 0.6); ctx.line_to(-tail * w * 0.3, s * 1.4); ctx.line_to(-tail * w * 0.32, s * 0.6); ctx.close_path(); ctx.fill()
    text(ctx, txt, 0, 0, s, col, shadow=False)
    ctx.restore()


def waves(ctx, x, y, t, col=CYN, n=3, r0=40, dr=50, ang=0.0, spread=0.7, a=1.0):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(n):
        ph = (t * 1.6 + k / n) % 1
        ctx.set_line_width(10)
        ctx.set_source_rgba(*col, a * (1 - ph))
        ctx.arc(x, y, r0 + dr * n * ph, ang - spread, ang + spread); ctx.stroke()


# ---------------------------------------------------------------- cabin + cockpit
def plane_window(ctx, x, y, s, t, night_=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -70, -100, 140, 200, 65); ctx.set_source_rgb(0.85, 0.87, 0.95); ctx.fill()
    rrect(ctx, -55, -85, 110, 170, 52); ctx.save(); ctx.clip()
    g = cairo.LinearGradient(0, -85, 0, 85)
    g.add_color_stop_rgb(0, 0.02, 0.03, 0.15); g.add_color_stop_rgb(1, 0.25, 0.12, 0.45)
    ctx.set_source(g); ctx.paint()
    for k in range(6):
        cx = ((hrand("cw", k) * 260 - t * 90) % 260) - 130
        ctx.arc(cx, 30 + hrand("cy", k) * 50, 30 + 20 * hrand("cr", k), 0, 6.3)
        ctx.set_source_rgba(0.75, 0.75, 0.95, 0.5); ctx.fill()
    ctx.arc(25, -45, 10, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.75); ctx.fill()
    f = flash(t)
    if f > 0.02:
        ctx.set_source_rgba(0.9, 0.9, 1, 0.8 * f); ctx.paint()
        if f > 0.3: bolt(ctx, -10, -85, 85, int(t * 2), a=f, w=4)
    ctx.restore()
    ctx.restore()


def cabin_bg(ctx, tg, dark=0.0):
    g = cairo.LinearGradient(0, 440, 0, 1300)
    g.add_color_stop_rgb(0, 0.12, 0.13, 0.35); g.add_color_stop_rgb(1, 0.25, 0.14, 0.42)
    ctx.set_source(g); ctx.rectangle(0, 440, W, 940); ctx.fill()
    # overhead bins
    rrect(ctx, -20, 440, W + 40, 80, 30); ctx.set_source_rgb(0.85, 0.86, 0.95); ctx.fill()
    ctx.set_source_rgba(0.3, 0.3, 0.5, 0.6); ctx.set_line_width(3)
    for k in range(4):
        ctx.move_to(k * 290 + 120, 445); ctx.line_to(k * 290 + 120, 515); ctx.stroke()
    if dark: ctx.set_source_rgba(0, 0.02, 0.08, dark); ctx.rectangle(0, 440, W, 940); ctx.fill()


def aisle(ctx, t, move):
    """rows of empty seats in perspective, rows coming toward the viewer as move grows"""
    vx, vy = 540, 560
    g = cairo.LinearGradient(0, 440, 0, 1300)
    g.add_color_stop_rgb(0, 0.1, 0.1, 0.3); g.add_color_stop_rgb(1, 0.3, 0.15, 0.45)
    ctx.set_source(g); ctx.rectangle(0, 440, W, 900); ctx.fill()
    # ceiling and floor planes
    ctx.move_to(0, 440); ctx.line_to(W, 440); ctx.line_to(vx + 160, vy - 40); ctx.line_to(vx - 160, vy - 40); ctx.close_path()
    ctx.set_source_rgb(0.85, 0.86, 0.95); ctx.fill()
    ctx.move_to(vx - 40, vy + 30); ctx.line_to(vx + 40, vy + 30); ctx.line_to(760, 1320); ctx.line_to(320, 1320); ctx.close_path()
    ctx.set_source_rgb(0.55, 0.2, 0.4); ctx.fill()
    for k in range(12, -1, -1):
        d = k - (move % 1.0)
        if d < -0.4: continue
        s = 1.0 / (1 + d * 0.42)
        yb = vy + 760 * s
        for side in (-1, 1):
            # side window
            wx = vx + side * 520 * s; wy = yb - 520 * s
            rrect(ctx, wx - 26 * s, wy - 40 * s, 52 * s, 80 * s, 24 * s); ctx.set_source_rgba(0.6, 0.75, 1, 0.8); ctx.fill()
            for j in range(2):
                sx = vx + side * (150 + j * 175) * s
                col = SEATB if (k + j) % 2 else SEATP
                rrect(ctx, sx - 80 * s, yb - 360 * s, 160 * s, 300 * s, 30 * s); ctx.set_source_rgb(*col); ctx.fill()
                rrect(ctx, sx - 55 * s, yb - 380 * s, 110 * s, 60 * s, 20 * s); ctx.set_source_rgb(*[min(1, c * 1.3) for c in col]); ctx.fill()
                rrect(ctx, sx - 50 * s, yb - 300 * s, 100 * s, 8 * s, 4 * s); ctx.set_source_rgba(1, 1, 1, 0.25); ctx.fill()
    g = cairo.RadialGradient(vx, vy, 50, vx, vy, 900)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0.05, 0.45)
    ctx.set_source(g); ctx.rectangle(0, 440, W, 900); ctx.fill()


def sky_view(ctx, tg, y0=440, y1=1000, dawn=0.0):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, 0.02 + 0.2 * dawn, 0.03 + 0.15 * dawn, 0.15 + 0.3 * dawn)
    g.add_color_stop_rgb(1, 0.35 + 0.5 * dawn, 0.15 + 0.3 * dawn, 0.5)
    ctx.set_source(g); ctx.rectangle(0, y0, W, y1 - y0); ctx.fill()
    for k in range(40):
        a = 0.3 + 0.4 * (0.5 + 0.5 * math.sin(tg * 2 + k * 1.3))
        ctx.arc(hrand("sx", k) * W, y0 + hrand("sy", k) * (y1 - y0) * 0.6, 1.5 + 2 * hrand("ss", k), 0, 6.3)
        ctx.set_source_rgba(1, 1, 1, a * (1 - dawn)); ctx.fill()
    for k in range(7):
        cx = ((hrand("ck", k) * 1500 - tg * 60) % 1500) - 200
        cy = y1 - 60 - 120 * hrand("cky", k)
        ctx.save(); ctx.translate(cx, cy); ctx.scale(2.2, 0.6)
        ctx.arc(0, 0, 60 + 40 * hrand("ckr", k), 0, 6.3); ctx.restore()
        ctx.set_source_rgba(0.8, 0.75, 1, 0.25); ctx.fill()
    f = flash(tg) * (1 - dawn)
    if f > 0.02:
        ctx.set_source_rgba(0.85, 0.85, 1, 0.45 * f); ctx.rectangle(0, y0, W, y1 - y0); ctx.fill()
        if f > 0.3: bolt(ctx, 200 + 700 * hrand("bxp", int(tg * 2)), y0, y0 + (y1 - y0) * 0.55, int(tg * 2), a=f)


def bolt(ctx, x, y0, y1, seed, a=1.0, w=8):
    pts = [(x, y0)]
    n = 9
    for k in range(1, n + 1):
        pts.append((x + (hrand("bz", seed, k) - 0.5) * 6 * w * 2.5, y0 + (y1 - y0) * k / n))
    ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for lw, col, al in ((w * 3.5, (0.6, 0.6, 1.0), 0.3), (w, (1, 1, 1), 1.0)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*col, al * a)
        ctx.move_to(*pts[0])
        for q in pts[1:]: ctx.line_to(*q)
        ctx.stroke()


def storm_cloud(ctx, x, y, s, tg, glow=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    for k in range(9):
        cx = (k - 4) * 70 + math.sin(tg * 0.6 + k) * 8
        cy = (hrand("sc", k) - 0.5) * 80
        r = 90 + 60 * hrand("sr", k)
        ctx.arc(cx, cy, r, 0, 6.3)
        ctx.set_source_rgba(0.2 + 0.55 * glow, 0.14 + 0.5 * glow, 0.34 + 0.5 * glow, 0.98); ctx.fill()
        ctx.arc(cx - r * 0.15, cy - r * 0.2, r * 0.75, 0, 6.3)
        ctx.set_source_rgba(0.32 + 0.5 * glow, 0.26 + 0.5 * glow, 0.5 + 0.4 * glow, 0.6); ctx.fill()
    ctx.restore()


def ocean(ctx, tg, y0=900, y1=1300, f=0.0):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, 0.03 + 0.3 * f, 0.06 + 0.3 * f, 0.18 + 0.3 * f); g.add_color_stop_rgb(1, 0.01, 0.02, 0.08)
    ctx.set_source(g); ctx.rectangle(0, y0, W, y1 - y0); ctx.fill()
    for k in range(18):
        y = y0 + 8 + k * (y1 - y0) / 18
        x = (hrand("wv", k) * W + tg * (25 + k * 6)) % (W + 200) - 100
        ctx.rectangle(x, y, 50 + k * 9, 3 + k * 0.3); ctx.set_source_rgba(0.6, 0.75, 1, 0.3 + 0.5 * f); ctx.fill()


def alarm_overlay(ctx, tl, a=0.4):
    if a <= 0.01: return
    p = 0.5 + 0.5 * math.sin(tl * 22)
    ctx.set_source_rgba(0.95, 0.05, 0.12, a * p); ctx.rectangle(0, 440, W, 940); ctx.fill()


def screen(ctx, x, y, w, h, kind, t, label=None):
    rrect(ctx, x - w / 2 - 8, y - h / 2 - 8, w + 16, h + 16, 12); ctx.set_source_rgb(0.05, 0.05, 0.08); ctx.fill()
    ctx.save(); rrect(ctx, x - w / 2, y - h / 2, w, h, 8); ctx.clip()
    if kind == "pfd":
        ctx.translate(x, y); ctx.rotate(0.03 * math.sin(t * 0.8))
        ctx.rectangle(-w, -h, 2 * w, h); ctx.set_source_rgb(0.15, 0.5, 1.0); ctx.fill()
        ctx.rectangle(-w, 0, 2 * w, h); ctx.set_source_rgb(0.6, 0.35, 0.15); ctx.fill()
        ctx.set_source_rgb(*WHT); ctx.rectangle(-w, -2, 2 * w, 4); ctx.fill()
        ctx.set_source_rgb(*YEL); ctx.set_line_width(6)
        ctx.move_to(-w * 0.3, 0); ctx.line_to(-w * 0.08, 0); ctx.move_to(w * 0.08, 0); ctx.line_to(w * 0.3, 0); ctx.stroke()
    else:
        ctx.set_source_rgb(0.02, 0.06, 0.08); ctx.paint()
        ctx.set_source_rgba(*GRN, 0.9); ctx.set_line_width(3)
        for r in (0.3, 0.6, 0.9):
            ctx.arc(x, y + h / 2, h * r, math.pi * 1.2, math.pi * 1.8); ctx.stroke()
        ctx.move_to(x, y + h / 2); ctx.line_to(x + math.sin(t * 2) * h * 0.4, y - h * 0.2); ctx.set_source_rgba(*CYN, 0.9); ctx.stroke()
    ctx.restore()
    if label: text(ctx, label, x, y + h / 2 + 34, 30, WHT, SANS)


def cockpit_back(ctx, tg, t, empty=True):
    """view from the cockpit door: windscreen, glowing panel, two empty pilot seats"""
    sky_view(ctx, tg, 440, 900)
    # windscreen frame
    ctx.set_source_rgb(0.18, 0.18, 0.26)
    ctx.rectangle(0, 440, W, 40); ctx.fill()
    for x in (90, 540, 990):
        ctx.move_to(x - 18, 440); ctx.line_to(x + 18, 440); ctx.line_to(x + 30 * (1 if x > 540 else -1 if x < 540 else 0) + 14, 900); ctx.line_to(x + 30 * (1 if x > 540 else -1 if x < 540 else 0) - 14, 900); ctx.close_path(); ctx.fill()
    # glareshield + panel
    rrect(ctx, -20, 860, W + 40, 70, 30); ctx.set_source_rgb(0.08, 0.08, 0.12); ctx.fill()
    ctx.rectangle(0, 900, W, 420); ctx.set_source_rgb(*PANEL); ctx.fill()
    for k, kind in enumerate(("pfd", "nd", "nd", "pfd")):
        screen(ctx, 160 + k * 253, 1000, 190, 140, kind, t)
    for k in range(18):
        ctx.arc(120 + k * 50, 1110, 9, 0, 6.3)
        on = (0.5 + 0.5 * math.sin(t * 3 + k * 1.7)) > 0.4
        ctx.set_source_rgb(*(YEL if k % 3 == 0 else GRN if on else (0.3, 0.3, 0.4))); ctx.fill()
    # pedestal
    rrect(ctx, 440, 1130, 200, 200, 20); ctx.set_source_rgb(0.1, 0.1, 0.15); ctx.fill()
    for s in (-1, 1):
        rrect(ctx, 540 + s * 40 - 14, 1150, 28, 70, 10); ctx.set_source_rgb(0.75, 0.78, 0.85); ctx.fill()
    # empty seat backs
    for x in (230, 850):
        rrect(ctx, x - 150, 1080, 300, 300, 50); ctx.set_source_rgb(0.28, 0.28, 0.36); ctx.fill()
        rrect(ctx, x - 90, 1040, 180, 90, 30); ctx.set_source_rgb(0.36, 0.36, 0.46); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.12); rrect(ctx, x - 110, 1140, 220, 14, 7); ctx.fill()


# ---------------------------------------------------------------- planes, tower, radio
def airliner(ctx, x, y, s, t, tilt=0.0, gear=0.0):
    """side view, nose to the right, centre of fuselage at (x, y)"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt); ctx.scale(s, s)
    # far wing
    ctx.move_to(-40, -10); ctx.line_to(60, -10); ctx.line_to(-30, -70); ctx.line_to(-80, -70); ctx.close_path()
    ctx.set_source_rgb(0.7, 0.72, 0.85); ctx.fill()
    # tail
    ctx.move_to(-300, -30); ctx.line_to(-380, -150); ctx.line_to(-330, -150); ctx.line_to(-220, -30); ctx.close_path()
    ctx.set_source_rgb(*PNK); ctx.fill()
    # fuselage
    ctx.move_to(-360, -40); ctx.line_to(250, -45); ctx.curve_to(330, -45, 360, 0, 360, 10)
    ctx.curve_to(340, 40, 300, 45, 250, 45); ctx.line_to(-280, 45); ctx.line_to(-370, -20); ctx.close_path()
    ctx.set_source_rgb(0.97, 0.97, 1.0); ctx.fill()
    ctx.rectangle(-300, 14, 560, 12); ctx.set_source_rgb(*BLUE); ctx.fill()
    for k in range(16):
        ctx.arc(-240 + k * 28, -12, 7, 0, 6.3); ctx.set_source_rgb(0.15, 0.2, 0.4); ctx.fill()
    ctx.move_to(285, -30); ctx.line_to(325, -28); ctx.line_to(340, -8); ctx.line_to(292, -10); ctx.close_path()
    ctx.set_source_rgb(0.15, 0.2, 0.4); ctx.fill()
    # gear
    if gear > 0:
        for gx in (-60, 230):
            ctx.set_source_rgb(0.3, 0.3, 0.35); ctx.rectangle(gx - 4, 40, 8, 30 * gear); ctx.fill()
            ctx.arc(gx, 40 + 34 * gear, 14 * gear, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
    # near wing + engine
    ctx.move_to(-60, 15); ctx.line_to(80, 15); ctx.line_to(-60, 120); ctx.line_to(-120, 120); ctx.close_path()
    ctx.set_source_rgb(0.85, 0.87, 0.97); ctx.fill()
    rrect(ctx, -10, 40, 110, 46, 23); ctx.set_source_rgb(0.75, 0.78, 0.9); ctx.fill()
    ctx.arc(100, 63, 20, 0, 6.3); ctx.set_source_rgb(0.25, 0.25, 0.35); ctx.fill()
    ctx.restore()


def small_plane(ctx, x, y, s, t, who=None, tilt=0.0):
    """high-wing propeller plane, nose right; who=(expr, arms) draws the passenger in the cabin window"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt); ctx.scale(s, s)
    ctx.move_to(-250, -30); ctx.line_to(-300, -120); ctx.line_to(-260, -120); ctx.line_to(-200, -30); ctx.close_path()
    ctx.set_source_rgb(*YEL); ctx.fill()
    ctx.move_to(-280, -20); ctx.line_to(120, -60); ctx.curve_to(190, -60, 210, -20, 210, 0)
    ctx.curve_to(210, 30, 180, 45, 120, 45); ctx.line_to(-200, 20); ctx.close_path()
    ctx.set_source_rgb(0.97, 0.97, 1.0); ctx.fill()
    ctx.move_to(-280, -4); ctx.line_to(200, 8); ctx.line_to(200, 20); ctx.line_to(-260, 6); ctx.close_path()
    ctx.set_source_rgb(*PNK); ctx.fill()
    # cabin window with passenger
    ctx.save(); rrect(ctx, 20, -55, 110, 55, 14); ctx.clip()
    ctx.set_source_rgb(0.55, 0.8, 1.0); ctx.paint()
    if who: person(ctx, 75, 60, 120, HEROC, who[0], who[1], t, look=0.8)
    ctx.restore()
    rrect(ctx, 20, -55, 110, 55, 14); ctx.set_source_rgb(0.25, 0.25, 0.35); ctx.set_line_width(4); ctx.stroke()
    # wing on top + strut
    rrect(ctx, -60, -82, 260, 24, 12); ctx.set_source_rgb(0.9, 0.9, 1.0); ctx.fill()
    ctx.set_source_rgb(0.6, 0.6, 0.7); ctx.set_line_width(6); ctx.move_to(60, 20); ctx.line_to(140, -60); ctx.stroke()
    # gear
    for gx in (40, 170):
        ctx.set_line_width(6); ctx.move_to(gx, 30); ctx.line_to(gx, 62); ctx.stroke()
        ctx.arc(gx, 66, 14, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill(); ctx.set_source_rgb(0.6, 0.6, 0.7)
    # propeller blur
    ctx.save(); ctx.translate(214, 0); ctx.scale(0.18, 1)
    ctx.arc(0, 0, 70, 0, 6.3); ctx.restore(); ctx.set_source_rgba(0.8, 0.85, 1, 0.35 + 0.15 * math.sin(t * 50)); ctx.fill()
    ctx.arc(214, 0, 9, 0, 6.3); ctx.set_source_rgb(*RED); ctx.fill()
    ctx.restore()


def runway(ctx, y, t, speed=0.0, x0=-50, x1=W + 50):
    ctx.rectangle(-50, y + 70, W + 100, max(0, 1300 - y - 70)); ctx.set_source_rgb(0.12, 0.3, 0.22); ctx.fill()
    ctx.rectangle(x0, y, x1 - x0, 70); ctx.set_source_rgb(0.2, 0.2, 0.26); ctx.fill()
    off = (t * speed) % 160
    for k in range(-1, 9):
        if x0 + k * 160 - off < x0: continue
        ctx.rectangle(x0 + k * 160 - off, y + 30, 80, 10); ctx.set_source_rgb(*WHT); ctx.fill()
    for k in range(-1, 14):
        if x0 + k * 100 - (t * speed) % 100 < x0: continue
        ctx.arc(x0 + k * 100 - (t * speed) % 100, y - 4, 5, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()


def tower(ctx, x, y, s, t):
    """control tower, base at (x, y)"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-45, 0); ctx.line_to(45, 0); ctx.line_to(30, -330); ctx.line_to(-30, -330); ctx.close_path()
    ctx.set_source_rgb(0.85, 0.86, 0.95); ctx.fill()
    ctx.move_to(-95, -330); ctx.line_to(95, -330); ctx.line_to(115, -420); ctx.line_to(-115, -420); ctx.close_path()
    ctx.set_source_rgb(0.25, 0.25, 0.4); ctx.fill()
    ctx.move_to(-85, -340); ctx.line_to(85, -340); ctx.line_to(102, -410); ctx.line_to(-102, -410); ctx.close_path()
    ctx.set_source_rgba(*CYN, 0.85); ctx.fill()
    rrect(ctx, -110, -445, 220, 30, 10); ctx.set_source_rgb(0.85, 0.86, 0.95); ctx.fill()
    ctx.set_source_rgb(0.6, 0.6, 0.7); ctx.set_line_width(5); ctx.move_to(0, -445); ctx.line_to(0, -500); ctx.stroke()
    ctx.arc(0, -505, 9, 0, 6.3); ctx.set_source_rgba(*RED, 0.4 + 0.6 * (math.sin(t * 6) > 0)); ctx.fill()
    ctx.restore()


def radio_box(ctx, x, y, s, freq, t, glow=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if glow: glow_circle(ctx, 0, 0, 380, CYN, 0.35 * glow)
    rrect(ctx, -300, -130, 600, 260, 40); ctx.set_source_rgb(0.12, 0.12, 0.18); ctx.fill()
    rrect(ctx, -270, -100, 400, 140, 20); ctx.set_source_rgb(0.02, 0.08, 0.06); ctx.fill()
    text(ctx, freq, -70, -30, 110, GRN, shadow=False)
    for k in range(2):
        ctx.arc(205, -40 + k * 110, 42, 0, 6.3); ctx.set_source_rgb(0.4, 0.42, 0.5); ctx.fill()
        a = t * 3 + k
        ctx.set_source_rgb(*WHT); ctx.set_line_width(8); ctx.move_to(205, -40 + k * 110)
        ctx.line_to(205 + math.cos(a) * 32, -40 + k * 110 + math.sin(a) * 32); ctx.stroke()
    text(ctx, "MHz", 80, 80, 40, WHT, SANS, shadow=False)
    ctx.restore()


def radar(ctx, x, y, r, t):
    ctx.arc(x, y, r + 10, 0, 6.3); ctx.set_source_rgb(0.1, 0.1, 0.15); ctx.fill()
    ctx.arc(x, y, r, 0, 6.3); ctx.set_source_rgb(0.02, 0.12, 0.08); ctx.fill()
    ctx.set_source_rgba(*GRN, 0.5); ctx.set_line_width(2)
    for f in (0.33, 0.66): ctx.arc(x, y, r * f, 0, 6.3); ctx.stroke()
    a = t * 2.5
    ctx.move_to(x, y); ctx.arc(x, y, r, a - 0.5, a); ctx.close_path(); ctx.set_source_rgba(*GRN, 0.35); ctx.fill()
    ctx.arc(x + r * 0.45, y - r * 0.3, 8, 0, 6.3); ctx.set_source_rgb(*YEL); ctx.fill()


def seatbelt_sign(ctx, x, y, s, on=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -90, -50, 180, 100, 20); ctx.set_source_rgb(0.1, 0.1, 0.15); ctx.fill()
    col = YEL if on else (0.35, 0.35, 0.45)
    if on: glow_circle(ctx, 0, 0, 130, YEL, 0.3)
    ctx.arc(-25, -15, 10, 0, 6.3); ctx.set_source_rgb(*col); ctx.fill()
    rrect(ctx, -38, 0, 26, 30, 8); ctx.fill()
    ctx.set_line_width(7); ctx.set_source_rgb(*col)
    ctx.move_to(5, 10); ctx.line_to(55, 10); ctx.stroke()
    rrect(ctx, 22, 0, 18, 20, 4); ctx.fill()
    ctx.restore()


def red_pulse(ctx, tl, a=0.45):
    g = cairo.RadialGradient(540, 860, 300, 540, 860, 1100)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.6, 0, 0.05, a * (0.7 + 0.3 * math.sin(tl * 9)))
    ctx.set_source(g); ctx.paint()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    """hook: alarm-lit cabin, you jolt awake, empty rows rush past, empty cockpit, nobody flying"""
    twk = wt(0, "wake"); t35 = wt(0, "35"); tev = wt(0, "Every"); tem = wt(0, "empty")
    tco = wt(0, "cockpit"); tno = wt(0, "Nobody"); tfl = wt(0, "flying")
    shake = 8 * math.sin(tl * 47) * (1.0 if tl < twk + 0.6 else 0.35)
    ctx.translate(shake, 0.5 * shake)
    if tl < tev - 0.1:
        cabin_bg(ctx, tg, dark=0.45)
        plane_window(ctx, 880, 700, 1.3, tg)
        awake = tl > twk - 0.05
        jolt = 22 * math.exp(-(tl - twk) * 7) * math.sin(tl * 50) if awake else 0
        seated(ctx, 470 + jolt, 1410, 820, HEROC, "shock" if awake else "smile", "up" if awake else "down", tl,
               look=0.8 if tl > t35 else 0, seat=SEATB)
        if not awake:
            for k in range(3):
                ph = (tl * 1.6 + k / 3) % 1
                text(ctx, "z", 640 + 50 * ph + k * 10, 560 - 120 * ph, 50 + 20 * k, WHT, alpha=1 - ph)
        if tl > t35 - 0.05:
            ps = pop(tl - t35 + 0.05, 0.22)
            ctx.save(); ctx.translate(820, 990); ctx.scale(ps, ps)
            rrect(ctx, -170, -60, 340, 120, 30); ctx.set_source_rgb(0.05, 0.05, 0.1); ctx.fill()
            text(ctx, "35,000 FT", 0, -2, 70, YEL, shadow=False)
            ctx.restore()
        alarm_overlay(ctx, tl, 0.3)
    elif tl < tco - 0.1:
        tt = tl - tev + 0.1
        aisle(ctx, tl, tt * 1.8)
        # failing cabin lights
        if math.sin(tl * 37) + math.sin(tl * 23) > 1.2:
            ctx.set_source_rgba(0, 0, 0.03, 0.6); ctx.rectangle(0, 440, W, 900); ctx.fill()
        if tl > tem - 0.05:
            popchip(ctx, "0 PASSENGERS", 540, 520, tl - tem + 0.05, WHT, (0, 0, 0), 66)
        red_pulse(ctx, tl, 0.45)
    else:
        tt = tl - tco + 0.1
        cockpit_back(ctx, tg, tl)
        dw = 300 * (1 - ease_out(tt / 0.4))
        ctx.set_source_rgb(0.1, 0.1, 0.16); ctx.rectangle(0, 440, 60 + dw, 900); ctx.fill(); ctx.rectangle(W - 60 - dw, 440, 60 + dw, 900); ctx.fill()
        if tl > tno - 0.1:
            # slow push toward the empty seats
            for x in (230, 850):
                a = 0.5 + 0.5 * math.sin(tl * 9)
                ctx.set_source_rgba(*RED, 0.7 * a); ctx.set_line_width(10)
                rrect(ctx, x - 160, 1030, 320, 360, 50); ctx.stroke()
        stamp(ctx, "NOBODY IS FLYING", 540, 640, tl - tfl + 0.05, RED, 90, -0.08)
        red_pulse(ctx, tl, 0.6)


def s1(ctx, tg, tl, T):
    """wilderness: tiny plane over a black ocean, a lightning storm wall ahead"""
    toc = wt(1, "ocean"); tst = wt(1, "storm")
    f = flash(tg)
    g = cairo.LinearGradient(0, 440, 0, 920)
    g.add_color_stop_rgb(0, 0.02 + 0.3 * f, 0.03 + 0.3 * f, 0.12 + 0.35 * f); g.add_color_stop_rgb(1, 0.12, 0.06, 0.25)
    ctx.set_source(g); ctx.rectangle(0, 440, W, 480); ctx.fill()
    for k in range(30):
        ctx.arc(hrand("os", k) * W, 460 + hrand("oy", k) * 300, 1.5 + 2 * hrand("or", k), 0, 6.3)
        ctx.set_source_rgba(1, 1, 1, 0.5 * (1 - f)); ctx.fill()
    z = ease_io(tl / T)
    ocean(ctx, tg, 900, 1300, f)
    # storm wall ahead, growing as it rolls in
    grow = ease_out((tl - tst + 0.4) / 1.2) if tl > tst - 0.4 else 0
    storm_cloud(ctx, 1000 - 90 * grow, 640, 0.75 + 0.35 * grow, tg, glow=f)
    storm_cloud(ctx, 860 - 70 * grow, 740, 0.55 + 0.3 * grow, tg, glow=0.8 * f)
    if f > 0.25:
        bolt(ctx, 900 - 80 * grow, 720, 1040, int(tg * 2), a=min(1, f * 1.4), w=9)
    ax = 300 + 120 * z
    airliner(ctx, ax, 720 + 10 * math.sin(tl * 2.2), 0.62, tl, tilt=0.03 * math.sin(tl * 3))
    # its tiny lit windows: one passenger
    if tl < toc - 0.1:
        popchip(ctx, "YOU ARE HERE", ax, 600, tl - 0.15, YEL, (0, 0, 0), 46)
    else:
        popchip(ctx, "BLACK OCEAN. NO LAND.", 540, 1215, tl - toc + 0.05, CYN, (0, 0, 0), 50)
    stamp(ctx, "STORM AHEAD", 540, 560, tl - tst, RED, 96, -0.08)


def s2(ctx, tg, tl, T):
    """alarms, the reveal that you're the pilot, then the breathing reset"""
    tal = wt(1, "Alarms"); twho = wt(1, "Who"); tyou = wt(1, "You."); tbr = wt(1, "breathe")
    calm = ease_io((tl - tbr + 0.2) / 0.9) if tl > tbr - 0.2 else 0
    sky_view(ctx, tg, 440, 1300)
    sh = 9 * (1 - calm) * math.sin(tl * 52)
    ctx.translate(sh, 0)
    # breathing ring behind you
    if calm > 0:
        r = 300 + 50 * math.sin((tl - tbr) * 3.2)
        ctx.set_line_width(18); ctx.set_source_rgba(*CYN, 0.8 * calm)
        ctx.arc(540, 760, r, 0, 6.3); ctx.stroke()
        glow_circle(ctx, 540, 760, r + 60, CYN, 0.25 * calm)
    hat = tl > tyou - 0.05
    s = pop(tl, 0.22)
    ctx.save(); ctx.translate(540, 1420); ctx.scale(s, s)
    seated(ctx, 0, 0, 840, HEROC, "shock" if calm < 0.5 else "worry", "cheeks" if calm < 0.5 else "down", tl,
           look=0.0, seat=(0.3, 0.3, 0.38), hat=hat, headset=False)
    ctx.restore()
    rrect(ctx, -20, 1170, W + 40, 300, 40); ctx.set_source_rgb(*PANEL); ctx.fill()
    for k, kind in enumerate(("pfd", "nd", "nd", "pfd")):
        screen(ctx, 160 + k * 253, 1250, 170, 110, kind, tl)
    alarm_overlay(ctx, tl, 0.45 * (1 - calm))
    if calm < 0.5 and math.sin(tl * 22) > -0.2:
        chip(ctx, "WARNING", 220, 520, 58, RED, WHT)
    if tl > twho - 0.05 and tl < tyou - 0.05:
        bubble(ctx, 760, 600, 66, "WHO'S FLYING?", tl - twho + 0.05, BLUE)
    if tl > tyou - 0.05 and tl < tbr - 0.2:
        stamp(ctx, "YOU.", 820, 600, tl - tyou + 0.05, RED, 130, -0.1)
    if calm > 0:
        popchip(ctx, "BREATHE IN... AND OUT", 540, 520, tl - tbr + 0.2, CYN, (0, 0, 0), 54)


def s3(ctx, tg, tl, T):
    ton = wt(3, "on?"); th = wt(3, "height"); td = wt(3, "direction"); tit = wt(3, "itself")
    ctx.rectangle(0, 440, W, 900); ctx.set_source_rgb(*PANEL); ctx.fill()
    lit = tl > ton - 0.05
    s = 1 + 0.2 * (1 - ease_out((tl - ton) / 0.3)) if lit else 1
    ctx.save(); ctx.translate(540, 590); ctx.scale(s, s)
    if lit: glow_circle(ctx, 0, 0, 260, GRN, 0.5)
    rrect(ctx, -170, -95, 340, 190, 40); ctx.set_source_rgb(0.25, 0.25, 0.32); ctx.fill()
    rrect(ctx, -140, -70, 280, 140, 30); ctx.set_source_rgb(*(GRN if lit else (0.35, 0.35, 0.42))); ctx.fill()
    text(ctx, "AUTOPILOT", 0, 0, 58, (0.05, 0.1, 0.05) if lit else WHT, shadow=False)
    ctx.restore()
    if not lit:
        # finger hovering, hesitating
        hx = 760 + 20 * math.sin(tl * 9)
        ctx.set_source_rgb(*SKIN); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(70)
        ctx.move_to(hx + 200, 900); ctx.line_to(hx, 700); ctx.stroke()
    for k, (lab, val, t0) in enumerate((("HEIGHT", "35,000 FT", th), ("DIRECTION", "HDG 090", td))):
        if tl < t0 - 0.05: continue
        ps = pop(tl - t0 + 0.05, 0.22)
        x = 290 + k * 500
        ctx.save(); ctx.translate(x, 830); ctx.scale(ps, ps)
        rrect(ctx, -220, -80, 440, 160, 26); ctx.set_source_rgb(0.02, 0.08, 0.06); ctx.fill()
        text(ctx, val, 0, -12, 64, GRN, shadow=False)
        text(ctx, lab, 0, 50, 30, CYN, SANS, shadow=False)
        if tl > t0 + 0.4: check(ctx, 190, -70, 50, YEL)
        ctx.restore()
    ctx.set_source_rgba(*CYN, 0.6); ctx.set_line_width(5); ctx.set_dash([20, 16], -tl * 80)
    ctx.move_to(60, 1080); ctx.line_to(1020, 1080); ctx.stroke(); ctx.set_dash([])
    px = 200 + 680 * ease_io(tl / T)
    airliner(ctx, px, 1060, 0.42, tl)
    if tl > tit - 0.1:
        popchip(ctx, "HANDS OFF. IT'S HOLDING.", 540, 1200, tl - tit + 0.1, YEL, (0, 0, 0), 48)


def s4(ctx, tg, tl, T):
    tra = wt(2, "radio"); tpr = wt(2, "Press"); tm = wt(2, "Mayday"); tth = wt(2, "three"); tti = wt(2, "times")
    tn = wt(2, "Not"); tbh = wt(2, "Bhaiya"); tro = wt(2, "roko")
    sky_view(ctx, tg, 440, 1300)
    if tl < tpr - 0.1:
        s = pop(tl - tra + 0.3, 0.25) if tl > tra - 0.3 else pop(tl, 0.25) * 0.6
        radio_box(ctx, 540, 820, s * 1.25, "118.7", tl, glow=1)
        waves(ctx, 540, 640, tl, CYN, 3, 60, 50, -math.pi / 2, 0.6)
        popchip(ctx, "YOUR LIFELINE", 540, 1140, tl - tra, CYN, (0, 0, 0), 60)
    elif tl < tn - 0.1:
        seated(ctx, 290, 1420, 800, HEROC, "shock", "up" if tl > tm - 0.1 else "down", tl, look=0.8, seat=(0.3, 0.3, 0.38), hat=True, headset=True)
        pr = tl > tpr + 0.1
        bx, by = 880, 1150
        ctx.save(); ctx.translate(bx, by)
        if pr: glow_circle(ctx, 0, 0, 200, RED, 0.5)
        ctx.arc(0, 0, 100, 0, 6.3); ctx.set_source_rgb(0.2, 0.2, 0.26); ctx.fill()
        ctx.arc(0, 8 if pr else 0, 76, 0, 6.3); ctx.set_source_rgb(*(RED if pr else (0.7, 0.15, 0.2))); ctx.fill()
        text(ctx, "TALK", 0, 8 if pr else 0, 46, WHT, shadow=False)
        ctx.restore()
        for k, t0 in enumerate((tm, tth, tti)):
            if tl < t0 - 0.05: continue
            y = 560 + k * 170
            bubble(ctx, 800, y, 66, "MAYDAY!", tl - t0 + 0.05, RED)
            ctx.arc(590, y, 32, 0, 6.3); ctx.set_source_rgba(*YEL, clamp((tl - t0) / 0.15)); ctx.fill()
            text(ctx, str(k + 1), 590, y, 42, (0, 0, 0), shadow=False, alpha=clamp((tl - t0) / 0.15))
    else:
        seated(ctx, 290, 1420, 800, HEROC, "smile", "wave", tl, look=0.8, seat=(0.3, 0.3, 0.38), hat=True, headset=True)
        if tl > tbh - 0.1:
            bubble(ctx, 690, 510, 56, "BHAIYA, SIDE MEIN ROKO!", tl - tbh + 0.1, PNK)
        ax = 1250 - 420 * ease_out((tl - tbh) / 1.2) if tl > tbh else 1300
        ctx.save(); ctx.translate(ax, 980); ctx.scale(1.1, 1.1)
        ctx.move_to(-90, 40); ctx.line_to(-90, -40); ctx.curve_to(-90, -80, -40, -90, 0, -90); ctx.line_to(60, -90)
        ctx.line_to(100, -20); ctx.line_to(100, 40); ctx.close_path(); ctx.set_source_rgb(*YEL); ctx.fill()
        ctx.rectangle(-90, 0, 190, 40); ctx.set_source_rgb(0.2, 0.7, 0.35); ctx.fill()
        rrect(ctx, 10, -70, 70, 50, 10); ctx.set_source_rgba(0.6, 0.85, 1, 0.9); ctx.fill()
        for wx in (-60, 70):
            ctx.arc(wx, 45, 22, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
        ctx.restore()
        stamp(ctx, "WRONG CALL!", 540, 1180, tl - tro, RED, 84, -0.08)


def static_box(ctx, x, y, w, h, tl, a=1.0):
    rrect(ctx, x - w / 2, y - h / 2, w, h, 24); ctx.set_source_rgba(0.05, 0.05, 0.1, 0.9 * a); ctx.fill()
    ctx.save(); rrect(ctx, x - w / 2, y - h / 2, w, h, 24); ctx.clip()
    seed = int(tl * 30)
    for k in range(40):
        yy = y - h / 2 + hrand("st", seed, k) * h
        xx = x - w / 2 + hrand("sx", seed, k) * w
        ctx.rectangle(xx, yy, 30 + 120 * hrand("sw", seed, k), 4); ctx.set_source_rgba(1, 1, 1, 0.6 * a); ctx.fill()
    ctx.restore()


def s5(ctx, tg, tl, T):
    tst = wt(3, "static"); tsw = wt(3, "Switch"); t121 = wt(3, "121"); tem = wt(3, "emergency")
    if tl < tsw - 0.1:
        sky_view(ctx, tg, 440, 1300)
        seated(ctx, 360, 1420, 800, HEROC, "worry", "down", tl, look=0.6 + 0.4 * math.sin(tl * 5), seat=(0.3, 0.3, 0.38), hat=True, headset=True)
        static_box(ctx, 800, 640, 430, 140, tl)
        text(ctx, "KSSHHH...", 800, 640, 60, WHT, stroke=5)
        if tl > tst - 0.05:
            popchip(ctx, "NO ANSWER", 540, 1200, tl - tst + 0.05, RED, WHT, 56)
    elif tl < tem - 0.1:
        f = clamp((tl - tsw) / max(0.2, t121 - tsw))
        val = 118.7 + (121.5 - 118.7) * ease_io(f)
        radio_box(ctx, 540, 800, 1.3, f"{val:.1f}", tl, glow=1 if f >= 1 else 0.3)
        if f < 1: static_box(ctx, 540, 1080, 600, 110, tl, a=1 - f)
        else: stamp(ctx, "121.5", 540, 1110, tl - t121, RED, 96, -0.06)
    else:
        tt = tl - tem + 0.1
        sky_view(ctx, tg, 440, 1300)
        radio_box(ctx, 290, 1050, 0.6, "121.5", tl, glow=1)
        tower(ctx, 860, 1250, 1.1, tl)
        airliner(ctx, 800, 640, 0.38, tl, tilt=-0.08)
        airliner(ctx, 260, 640, 0.3, tl, tilt=0.06)
        waves(ctx, 290, 960, tl, CYN, 3, 60, 60, -0.6, 0.5)
        waves(ctx, 290, 960, tl, CYN, 3, 60, 60, -1.9, 0.4)
        popchip(ctx, "EMERGENCY CHANNEL", 540, 470, tt, RED, WHT, 56)
        popchip(ctx, "TOWERS + PLANES LISTEN", 540, 1190, tt - 0.4, YEL, (0, 0, 0), 46)


def s6(ctx, tg, tl, T):
    tvo = wt(4, "voice"); tair = wt(4, "Air"); tst = wt(4, "step")
    sky_view(ctx, tg, 440, 1300, dawn=0.3 * ease_io((tl - tair) / 1.0) if tl > tair else 0)
    if tl < tair - 0.1:
        seated(ctx, 300, 1420, 800, HEROC, "worry" if tl < tvo else "shock", "down", tl, look=0.8, seat=(0.3, 0.3, 0.38), hat=True, headset=True)
        waves(ctx, 300, 640, tl, YEL, 3, 70, 60, -0.3, 0.6)
        bubble(ctx, 760, 620, 62, "I CAN HEAR YOU.", tl - tvo + 0.05, BLUE, tail=-1)
        return
    tt = tl - tair + 0.1
    s = pop(tt, 0.22)
    ctx.save(); ctx.translate(800, 1280); ctx.scale(s, s)
    rrect(ctx, -250, -760, 500, 760, 40); ctx.set_source_rgba(*CYN, 0.25); ctx.fill()
    person(ctx, 0, 0, 720, PNK, "smile", "wave", tl, look=-0.8)
    headset_on(ctx, 0, -86 * 7.2, 7.2, -0.8)
    radar(ctx, 140, -110, 95, tl)
    ctx.restore()
    popchip(ctx, "AIR TRAFFIC CONTROL", 800, 500, tt - 0.1, CYN, (0, 0, 0), 42)
    seated(ctx, 250, 1420, 760, HEROC, "smile", "down", tl, look=0.8, seat=(0.3, 0.3, 0.38), hat=True, headset=True)
    for k in range(3):
        ph = (tl * 1.2 + k / 3) % 1
        x = 680 - 300 * ph; y = 760 - 60 * math.sin(ph * math.pi)
        ctx.arc(x, y, 14, 0, 6.3); ctx.set_source_rgba(*YEL, 1 - ph); ctx.fill()
    if tl > tst - 0.6:
        for k, lab in enumerate(("WINGS LEVEL", "SLOW DESCENT")):
            t0 = tst - 0.6 + k * 0.35
            if tl < t0: continue
            ps = pop(tl - t0, 0.2)
            ctx.save(); ctx.translate(300, 560 + k * 110); ctx.scale(ps, ps)
            rrect(ctx, -230, -42, 460, 84, 30); ctx.set_source_rgb(*WHT); ctx.fill()
            check(ctx, -180, 0, 44, GRN)
            text(ctx, lab, 30, 0, 46, (0.1, 0.1, 0.2), shadow=False)
            ctx.restore()


def s7(ctx, tg, tl, T):
    tz = wt(5, "zero"); tla = wt(5, "landed"); tsm = wt(5, "small")
    sky_view(ctx, tg, 440, 1300, dawn=0.8)
    f = ease_io((tl - tla + 0.2) / 1.6) if tl > tla - 0.2 else 0
    ry = 1150
    runway(ctx, ry, tl, 380 * (1 - 0.6 * f) if f > 0 else 0, x0=-50 + 900 * (1 - min(1, f * 1.5)))
    px = 470 + 30 * math.sin(tl * 1.2)
    py = 760 + (ry - 70 - 760) * f + 12 * math.sin(tl * 2.3) * (1 - f)
    small_plane(ctx, px, py, 1.6, tl, who=("shock" if tl < tla + 1.2 else "cheeks", "down"), tilt=0.05 * math.sin(tl * 1.7) * (1 - f))
    if tl > tla + 1.0:
        for k in range(6):
            ph = ((tl - tla) * 1.5 + k / 6) % 1
            ctx.arc(px - 120 - 200 * ph, ry - 10 - 30 * ph, 20 + 30 * ph, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.5 * (1 - ph)); ctx.fill()
    zs = pop(tl - tz + 0.05, 0.25) if tl > tz - 0.05 else 0
    if zs > 0.01:
        ctx.save(); ctx.translate(840, 1000); ctx.scale(zs, zs)
        ctx.arc(0, 0, 160, 0, 6.3); ctx.set_source_rgb(*WHT); ctx.fill()
        ctx.arc(0, 0, 150, 0, 6.3); ctx.save(); ctx.clip()
        ctx.set_source_rgb(0.55, 0.8, 1.0); ctx.paint()
        person(ctx, 0, 600, 640, HEROC, "shock" if tl < tla + 1.2 else "cheeks", "down", tl, look=0.6)
        headset_on(ctx, 0, 600 - 86 * 6.4, 6.4, 0.6)
        ctx.restore(); ctx.restore()
    stamp(ctx, "TRUE STORY", 540, 520, tl - 0.1, PNK, 86, -0.08)
    if tl > tz - 0.05 and tl < tsm:
        popchip(ctx, "ZERO FLYING EXPERIENCE", 540, 1225, tl - tz + 0.05, YEL, (0, 0, 0), 50)
    if tl > tsm:
        popchip(ctx, "SAFE LANDING!", 540, 1225, tl - tsm, GRN, (0, 0, 0), 60)


def s8(ctx, tg, tl, T):
    tla = wt(6, "land"); tbu = wt(6, "But"); tgu = wt(6, "Guess")
    if tl < tbu - 0.1:
        sky_view(ctx, tg, 440, 1300, dawn=0.5)
        f = ease_io(tl / (tbu + 0.4))
        runway(ctx, 1150, tl, 0, x0=500 - 300 * f)
        ctx.set_source_rgba(*CYN, 0.35)
        ctx.move_to(560, 1150); ctx.line_to(-100, 560); ctx.line_to(-100, 760); ctx.close_path(); ctx.fill()
        ax = 300 + 260 * f; ay = 700 + 340 * f
        airliner(ctx, ax, ay, 0.8, tl, tilt=0.14 - 0.1 * f, gear=clamp(f * 2))
        if tl > tla - 0.05:
            popchip(ctx, "AUTOLAND", 760, 520, tl - tla + 0.05, CYN, (0, 0, 0), 66)
    elif tl < tgu - 0.1:
        tt = tl - tbu + 0.1
        ctx.rectangle(0, 440, W, 900); ctx.set_source_rgb(*PANEL); ctx.fill()
        for k in range(12):
            r_, c = divmod(k, 4)
            t0 = 0.08 * k
            if tt < t0: continue
            ps = pop(tt - t0, 0.18)
            x = 210 + c * 220; y = 640 + r_ * 200
            ctx.save(); ctx.translate(x, y); ctx.scale(ps, ps)
            rrect(ctx, -80, -60, 160, 120, 22); ctx.set_source_rgb(*[BLUE, PNK, YEL, CYN][(k * 7) % 4]); ctx.fill()
            text(ctx, ["APP", "LOC", "ILS", "A/T", "CMD", "FLAPS", "GEAR", "BARO", "NAV", "SPD", "ALT", "VS"][k], 0, 0, 44, (0.05, 0.05, 0.15), shadow=False)
            ctx.restore()
        q = ease_out((tt - 0.6) / 0.3)
        if q > 0:
            ctx.save(); ctx.translate(540, 840); ctx.scale(q, q)
            text(ctx, "???", 0, 0, 260, WHT, stroke=10)
            ctx.restore()
    else:
        tt = tl - tgu + 0.1
        cockpit_back(ctx, tg, tl)
        s = pop(tt, 0.22)
        ctx.save(); ctx.translate(460, 1420); ctx.scale(s, s)
        seated(ctx, 0, 0, 840, HEROC, "shock", "cheeks", tl, look=0.6, seat=(0.3, 0.3, 0.38), hat=True)
        ctx.restore()
        a = ease_out((tt - 0.2) / 0.25)
        if a > 0:
            ctx.save(); ctx.translate(880, 720 + 10 * math.sin(tl * 8))
            chip(ctx, "YOU!", 0, -80, 96, YEL, (0, 0, 0), alpha=a)
            ctx.set_source_rgba(*YEL, a); ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(0, 0); ctx.line_to(-150, 120); ctx.stroke()
            ctx.move_to(-185, 150); ctx.line_to(-170, 90); ctx.line_to(-125, 135); ctx.close_path(); ctx.fill()
            ctx.restore()


def s9(ctx, tg, tl, T):
    tma = wt(7, "made"); tco = wt(7, "Could")
    if tl < tma - 0.25:
        sky_view(ctx, tg, 440, 1300, dawn=1.0)
        hit = 0.25
        f = ease_out(tl / hit)
        runway(ctx, 1100, tl, 900)
        shake = 12 * math.exp(-(tl - hit) * 6) * math.sin(tl * 60) if tl > hit else 0
        airliner(ctx, 540 + shake, 960 + 80 * f, 1.25, tl, tilt=0.06 * (1 - f), gear=1)
        if tl > hit:
            for k in range(8):
                ph = ((tl - hit) * 1.4 + k / 8) % 1
                ctx.arc(420 - 350 * ph, 1090 - 40 * ph, 20 + 50 * ph, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.55 * (1 - ph)); ctx.fill()
        stamp(ctx, "TOUCHDOWN!", 540, 600, tl - hit, GRN, 110, -0.08, fg=(0, 0, 0))
    elif tl < tco - 0.1:
        tt = tl - tma + 0.25
        sky_view(ctx, tg, 440, 1300, dawn=1.0)
        glow_circle(ctx, 540, 760, 520, YEL, 0.35)
        sparkles(ctx, 540, 800, 420, tl, 16, YEL, "win")
        s = pop(tt, 0.22)
        ctx.save(); ctx.translate(540, 1420); ctx.scale(s, s)
        seated(ctx, 0, 0, 840, HEROC, "cheeks", "up", tl, seat=(0.3, 0.3, 0.38), hat=True, headset=True)
        ctx.restore()
        stamp(ctx, "YOU MADE IT!", 540, 560, tt - 0.1, GRN, 96, -0.08, fg=(0, 0, 0))
    else:
        tt = tl - tco + 0.1
        sky_view(ctx, tg, 440, 1300, dawn=1.0)
        ctx.save(); ctx.translate(540, 1420); s = pop(tt, 0.25); ctx.scale(s, s)
        person(ctx, 0, 0, 780, HEROC, "smile", "wave", tl)
        captain_hat(ctx, 0, -86 * 7.8, 7.8)
        ctx.restore()
        sc = pop(tt - 0.4, 0.25) * (1 + 0.04 * math.sin(tt * 8))
        ctx.save(); ctx.translate(540, 560); ctx.scale(sc, sc)
        g = cairo.LinearGradient(-400, 0, 400, 0)
        g.add_color_stop_rgb(0, 0.15, 0.55, 1.0); g.add_color_stop_rgb(1, 0.95, 0.25, 0.6)
        rrect(ctx, -400, -85, 800, 170, 85); ctx.set_source(g); ctx.fill()
        text(ctx, "YES OR NO?", 0, 0, 104, WHT, shadow=False)
        ctx.restore()


SCENES = [s0, s2, s4, s5, s6, s7, s8, s9]


def _engine(A, t0, t1, g=0.12):
    import numpy as np
    d = t1 - t0; n = int(d * 44100)
    x = A.lp(A.noise(d), 220) * 3
    e = np.ones(n); f = int(0.3 * 44100); e[:f] = np.linspace(0, 1, f); e[-f:] = np.linspace(1, 0, f)
    A.add(A.sfx_buf, x * e, t0, g)


def _static(A, t, d=0.35, g=0.12):
    import numpy as np
    x = A.bp(A.noise(d), 1500, 5000) * np.exp(-np.arange(int(d * 44100)) / 44100 * 6)
    A.add(A.sfx_buf, x, t, g)


def _thunder(A, t, g=0.3, d=1.6):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.lp(A.noise(d), 150) * 4 * np.exp(-tt * 2.0) * (0.6 + 0.4 * np.sin(tt * 9) ** 2)
    crack = A.hp(A.noise(0.12), 2500) * np.exp(-np.arange(int(0.12 * 44100)) / 44100 * 30)
    A.add(A.sfx_buf, crack, t, g * 0.6)
    A.add(A.sfx_buf, x, t + 0.05, g)


def _alarm(A, t0, t1, g=0.06):
    t = t0
    while t < t1:
        A.ding(t, g, 1760, 0.12); A.ding(t + 0.18, g, 1320, 0.12); t += 0.5


def sfx(A):
    _engine(A, 0.0, A.S(2) + 0.3, 0.14)
    # heartbeat that speeds up until you breathe
    t, gap = 0.4, 0.8
    while t < A.W(1, "breathe"):
        A.thump(t, 0.42, 50); A.thump(t + 0.2, 0.28, 45)
        t += gap; gap = max(0.48, gap - 0.025)
    for e in EV:
        if e < A.S(5): _thunder(A, e, 0.28 if e < A.S(1) else 0.18)
    _alarm(A, 0.05, A.W(0, "Every"), 0.05)
    _alarm(A, A.S(1), A.W(1, "breathe"), 0.07)
    A.whoosh(A.W(0, "35"), 0.15)
    A.thump(A.W(0, "Every"), 0.5, 55)
    A.thump(A.W(0, "cockpit"), 0.6, 45)
    A.scratch(A.W(0, "flying") - 0.05, 0.3)
    A.thump(A.W(0, "flying") + 0.05, 0.7, 40)
    A.pop(A.W(1, "Who"), 0.3)
    A.thump(A.W(1, "You."), 0.7, 50); A.scratch(A.W(1, "You.") - 0.05, 0.25)
    _static(A, A.W(2, "radio"), 0.4, 0.15)
    A.thump(A.W(2, "Press") + 0.1, 0.4, 120)
    for w in ("Mayday", "three", "times"):
        A.pop(A.W(2, w), 0.3)
    A.horn(A.W(2, "Bhaiya") + 0.3, 0.05)
    A.scratch(A.W(2, "roko") - 0.05, 0.3)
    _static(A, A.S(3), 1.6, 0.16)
    for k in range(8):
        A.ding(A.W(3, "Switch") + 0.05 + k * 0.17, 0.03, 2200, 0.08)
    A.ding(A.W(3, "121"), 0.1, 1318.5)
    A.whoosh(A.W(3, "emergency"), 0.2)
    _static(A, A.W(4, "voice") - 0.3, 0.3, 0.12)
    A.ding(A.W(4, "voice"), 0.08, 1046.5, 0.8)
    A.pop(A.W(4, "step") - 0.6, 0.3); A.pop(A.W(4, "step") - 0.25, 0.3)
    A.pop(A.S(5) + 0.1, 0.3)
    A.whoosh(A.W(5, "landed"), 0.2, 0.6)
    A.ding(A.W(5, "small"), 0.08, 1568); A.ding(A.W(5, "small") + 0.12, 0.08, 2093)
    A.ding(A.W(6, "land"), 0.1, 1318.5)
    for k in range(6):
        A.pop(A.W(6, "But") + 0.16 * k, 0.15)
    A.boing(A.W(6, "Guess"), 0.18, 300)
    A.thump(A.S(7) + 0.25, 0.7, 60); A.scratch(A.S(7) + 0.3, 0.3, 0.5)
    for k, m in enumerate((72, 76, 79, 84)):
        A.ding(A.W(7, "made") - 0.2 + k * 0.08, 0.07, A.note(m))
    A.pop(A.W(7, "Could"), 0.35)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(7, "Could") + 0.1 + k * 0.1, 0.07, A.note(m))

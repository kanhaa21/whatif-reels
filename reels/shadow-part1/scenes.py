"""Scenes for "What if your shadow moved 10 seconds before you?" Part 1. One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
The apartment is one fixed set in world pixels (floor at y = 1250); each shot is a camera on it.
Warm lamp light until the glass breaks, cold blue light after."""
import math
import cairo
import numpy as np
from reelkit.lib import *  # noqa: F401,F403

SR = 44100
MUSIC = {"beat_from_scene": 6, "bpm": 60, "whoosh_on_cuts": False}   # drone only; muted from the bass drop
NO_FLASH = (1, 2, 3, 4, 5, 6)

SKIN = (0.93, 0.74, 0.6); HOOD = (0.96, 0.72, 0.12); HOODD = (0.8, 0.54, 0.07)
PANTS = (0.2, 0.2, 0.25); HAIR = (0.1, 0.07, 0.06); SH = (0.02, 0.02, 0.04)
FY = 1250                 # floor line (world)
WX, WH = 470, 480         # woman: x, height
SX, SHH = 720, 552        # her shadow on the wall: x, height


def T0(i):
    return TL["scenes"][i]["t0"]


T_CRASH = 1.95                      # scene-2 local time the glass shatters (lamp dies with it)
COLD_T = T0(2) + T_CRASH


def BG(ctx, tg, i):
    ctx.set_source_rgb(0, 0, 0); ctx.paint()


class Cam:
    def __init__(self, ctx, cx, cy, z):
        self.a = (ctx, cx, cy, z)
    def __enter__(self):
        ctx, cx, cy, z = self.a
        ctx.save(); ctx.translate(540, 860); ctx.scale(z, z); ctx.translate(-cx, -cy); return ctx
    def __exit__(self, *a):
        self.a[0].restore()


# ---------------------------------------------------------------- character (also draws her shadow)
def _figure(ctx, x, fy, h, shadow=False, ra=0.0, la=0.0, crouch=0.0, face=0.0, expr="calm", walk=0.0, t=0.0,
           look=0.0, back=False, cam_point=0.0, finger=False, alpha=1.0):
    """front-facing woman, feet at (x, fy). ra/la: arm angles (0 = down, pi/2 = sideways, pi = up).
    face: -1..1 head turn (profile at +-1). shadow=True draws the same pose as a solid black silhouette."""
    u = h / 100.0
    dy = 26 * u * crouch

    def src(c):
        ctx.set_source_rgba(*(SH if shadow else c), alpha)

    ctx.save(); ctx.translate(x, fy)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(10 * u); src(PANTS)
    for s in (-1, 1):
        sw = math.sin(t * 9) * walk * s
        ctx.move_to(s * 9 * u, -40 * u + dy)
        ctx.line_to(s * (10 + 9 * crouch) * u + sw * 5 * u, -20 * u + dy * 0.45)
        ctx.line_to(s * 11 * u + sw * 9 * u, -2 * u)
        ctx.stroke()
    rrect(ctx, -20 * u, -75 * u + dy, 40 * u, 40 * u, 14 * u); src(HOOD); ctx.fill()
    if not shadow and not back:
        rrect(ctx, -11 * u, -52 * u + dy, 22 * u, 9 * u, 4 * u); src(HOODD); ctx.fill()
        ctx.set_line_width(1.6 * u); src((1, 0.95, 0.85))
        for s in (-1, 1):
            ctx.move_to(s * 3 * u, -70 * u + dy); ctx.line_to(s * 4 * u, -59 * u + dy)
        ctx.stroke()
    ctx.save(); ctx.translate(0, -74 * u + dy); ctx.scale(1, 0.55); ctx.arc(0, 0, 15 * u, 0, 6.3); ctx.restore()
    src(HOODD); ctx.fill()
    for s, a in ((1, ra), (-1, la)):
        if cam_point > 0 and s == 1: continue
        sx, sy = s * 18 * u, -69 * u + dy
        ex, ey = sx + s * math.sin(a) * 30 * u, sy + math.cos(a) * 30 * u
        ctx.set_line_width(9 * u); src(HOOD); ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.stroke()
        ctx.arc(ex, ey, 4.6 * u, 0, 6.3); src(SKIN); ctx.fill()
        if finger and s == 1:
            ctx.set_line_width(2.6 * u); src(SKIN)
            ctx.move_to(ex, ey); ctx.line_to(ex + math.sin(a) * 8 * u, ey + math.cos(a) * 8 * u); ctx.stroke()
    if cam_point > 0:
        # arm straight at the lens: foreshortened forearm and a hand that grows toward the viewer
        ctx.set_line_width(10 * u); src(HOOD)
        ctx.move_to(18 * u, -69 * u + dy); ctx.line_to(9 * u, -58 * u + dy); ctx.stroke()
        r = (5 + 8 * cam_point) * u
        ctx.arc(7 * u, -55 * u + dy, r, 0, 6.3); src(SKIN); ctx.fill()
        if shadow:
            ctx.set_line_width(1.6 * u); ctx.set_source_rgba(0.45, 0.65, 1, 0.7 * cam_point)
            ctx.arc(7 * u, -55 * u + dy, r, 0, 6.3); ctx.stroke()
            ctx.arc(7 * u, -55 * u + dy, r * 0.4, 0, 6.3); ctx.stroke()
    hy = -89 * u + dy
    hr = 15 * u
    # ponytail, behind the head
    if back:
        ctx.save(); ctx.translate(0, hy + 13 * u); ctx.scale(0.55, 1.3); ctx.arc(0, 0, 8 * u, 0, 6.3); ctx.restore()
    else:
        side = -1 if face >= 0 else 1
        ctx.save(); ctx.translate(side * (11 + 3 * abs(face)) * u, hy + 4 * u); ctx.rotate(-0.35 * side)
        ctx.scale(0.6, 1.25); ctx.arc(0, 0, 8 * u, 0, 6.3); ctx.restore()
    src(HAIR); ctx.fill()
    ctx.arc(0, hy, hr, 0, 6.3); src(HAIR if back else SKIN); ctx.fill()
    if shadow:
        if abs(face) > 0.4:
            sg = 1 if face > 0 else -1
            ctx.move_to(sg * 13.5 * u, hy - 3 * u); ctx.line_to(sg * 18.5 * u, hy + 3 * u)
            ctx.line_to(sg * 13.5 * u, hy + 6 * u); ctx.close_path(); src(SH); ctx.fill()
        ctx.restore(); return
    if back:
        ctx.restore(); return
    ctx.arc(0, hy - 1.5 * u, hr * 1.03, math.pi * 1.0, math.pi * 2.0); src(HAIR); ctx.fill()
    fx = face * 6 * u
    big = expr in ("fear",)
    for s in (-1, 1):
        er = (4.3 if big else 3.5) * u
        ctx.arc(fx + s * 5.6 * u, hy + 1.2 * u, er, 0, 6.3); src((1, 1, 1)); ctx.fill()
        ctx.arc(fx + s * 5.6 * u + look * 1.4 * u, hy + 1.5 * u, er * (0.4 if big else 0.58), 0, 6.3); src((0.08, 0.06, 0.1)); ctx.fill()
    ctx.set_line_width(1.3 * u); src(HAIR)
    lift = 2.2 * u if expr in ("worry", "fear") else 0
    for s in (-1, 1):
        ctx.move_to(fx + s * 2.8 * u, hy - 4.6 * u - lift); ctx.line_to(fx + s * 8.6 * u, hy - 4.4 * u); ctx.stroke()
    src((0.45, 0.15, 0.15))
    if expr == "fear":
        ctx.save(); ctx.translate(fx, hy + 8.5 * u); ctx.scale(1, 1.3); ctx.arc(0, 0, 2.4 * u, 0, 6.3); ctx.restore(); ctx.fill()
    elif expr == "worry":
        ctx.arc(fx, hy + 11 * u, 3.5 * u, math.pi * 1.2, math.pi * 1.8); ctx.stroke()
    else:
        ctx.move_to(fx - 2.5 * u, hy + 8 * u); ctx.line_to(fx + 2.5 * u, hy + 8 * u); ctx.stroke()
    ctx.restore()


def figure(ctx, *a, shadow=False, alpha=1.0, **k):
    """shadows render as one solid silhouette (no seams where body parts overlap)"""
    if shadow:
        ctx.push_group(); _figure(ctx, *a, shadow=True, alpha=1.0, **k)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(alpha)
    else:
        _figure(ctx, *a, alpha=alpha, **k)


# ---------------------------------------------------------------- the apartment (world pixels)
def glass(ctx, x, y, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.move_to(-15, -46); ctx.line_to(15, -46); ctx.line_to(12, 0); ctx.line_to(-12, 0); ctx.close_path()
    ctx.set_source_rgba(0.85, 0.95, 1, 0.45); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(2.5); ctx.stroke()
    ctx.restore()


def room(ctx, tg, glasses=3, wobble=0.0, flick=0.0):
    cold = tg >= COLD_T
    ctx.set_source_rgb(0.87, 0.8, 0.69); ctx.rectangle(-2000, -2000, 5200, 3250); ctx.fill()
    if not cold:
        glow_circle(ctx, 330, 835, 760, (1, 0.82, 0.5), 0.55 * (1 - flick))
    else:
        for k in range(6):
            y0 = 480 + k * 80
            ctx.move_to(-300, y0); ctx.line_to(1400, y0 + 300); ctx.line_to(1400, y0 + 328); ctx.line_to(-300, y0 + 28); ctx.close_path()
            ctx.set_source_rgba(0.75, 0.85, 1, 0.12); ctx.fill()
    # front door (left)
    rrect(ctx, 30, 740, 200, 510, 6); ctx.set_source_rgb(0.97, 0.95, 0.9); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.12); ctx.set_line_width(4)
    rrect(ctx, 55, 770, 150, 200, 4); ctx.stroke(); rrect(ctx, 55, 1000, 150, 220, 4); ctx.stroke()
    ctx.arc(205, 1010, 9, 0, 6.3); ctx.set_source_rgb(0.75, 0.6, 0.25); ctx.fill()
    # hallway (right)
    g = cairo.LinearGradient(860, 0, 1130, 0)
    g.add_color_stop_rgb(0, 0.05, 0.04, 0.05); g.add_color_stop_rgb(1, 0.0, 0.0, 0.01)
    ctx.set_source(g); ctx.rectangle(860, 700, 280, 550); ctx.fill()
    ctx.set_source_rgb(0.95, 0.93, 0.88); ctx.rectangle(846, 690, 14, 560); ctx.fill(); ctx.rectangle(846, 686, 300, 14); ctx.fill()
    # shelf + glasses
    ctx.set_source_rgb(0.7, 0.52, 0.32); ctx.rectangle(480, 690, 300, 14); ctx.fill()
    for k, gx in enumerate((540, 620, 700)):
        if k < glasses:
            glass(ctx, gx, 690, (math.sin(tg * 40) * 0.08 * wobble) if k == 2 else 0)
    # floor lamp
    ctx.set_source_rgb(0.75, 0.6, 0.25); ctx.set_line_width(7)
    ctx.move_to(330, 1245); ctx.line_to(330, 868); ctx.stroke()
    ctx.save(); ctx.translate(330, 1248); ctx.scale(1, 0.3); ctx.arc(0, 0, 40, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.move_to(298, 800); ctx.line_to(362, 800); ctx.line_to(385, 870); ctx.line_to(275, 870); ctx.close_path()
    ctx.set_source_rgb(*((0.98, 0.9, 0.72) if not cold and flick < 0.5 else (0.55, 0.52, 0.48))); ctx.fill()
    # skirting + floor
    ctx.set_source_rgb(0.95, 0.93, 0.88); ctx.rectangle(-2000, 1236, 5200, 14); ctx.fill()
    ctx.set_source_rgb(0.32, 0.22, 0.16); ctx.rectangle(-2000, 1250, 5200, 1500); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.25); ctx.set_line_width(3)
    for k in range(8):
        ctx.move_to(-2000, 1290 + k * 60); ctx.line_to(3200, 1290 + k * 60); ctx.stroke()
    if flick > 0:
        ctx.set_source_rgba(0, 0, 0.02, 0.7 * flick); ctx.rectangle(-2000, -2000, 5200, 4750); ctx.fill()


def grade(ctx, tg):
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_rgb(*((0.4, 0.52, 0.95) if tg >= COLD_T else (1.0, 0.93, 0.82))); ctx.paint()
    ctx.set_operator(cairo.OPERATOR_OVER)
    g = cairo.RadialGradient(540, 900, 380, 540, 900, 1150)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.7)
    ctx.set_source(g); ctx.paint()


def cap2(ctx, l1, l2, x, y, tt, bg=WHT, fg=(0, 0, 0), size=62):
    popchip(ctx, l1, x, y, tt, bg, fg, size)
    if l2: popchip(ctx, l2, x, y + size * 1.35, tt - 0.08, bg, fg, size)


def timer(ctx, x, y, n, tt):
    if tt < 0: return
    s = pop(tt, 0.18)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -130, -55, 260, 110, 22); ctx.set_source_rgba(0.03, 0.03, 0.06, 0.92); ctx.fill()
    text(ctx, f"00:{n:02d}", 0, 0, 74, (1, 0.25, 0.25), shadow=False)
    ctx.restore()


def flick_at(tl, t0, d=0.15):
    return 1.0 if t0 <= tl < t0 + d else 0.0


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    """S1 hook: she stands still, her shadow is already raising its hand"""
    ra_s = 0.9 + 1.9 * ease_out(tl / 0.9)
    fl = flick_at(tl, 0.5, 0.12)
    with Cam(ctx, 585, 900, 1.55):
        room(ctx, tg, flick=fl)
        figure(ctx, SX, FY, SHH, shadow=True, ra=ra_s, alpha=0.93)
        figure(ctx, WX, FY, WH, expr="calm", look=0.2, t=tl)
    grade(ctx, tg)
    cap2(ctx, "MY SHADOW", "MOVED FIRST", 300, 500, tl, YEL, (0, 0, 0), 88)


def s1(ctx, tg, tl, T):
    """S2-S3 proof: shadow raises again, a 10 s timer races down, then she raises the same hand"""
    tev = wt(1, "Every")
    if tl < 0.9:
        ra_s = 2.8 - 2.6 * ease_io(tl / 0.6)
    else:
        ra_s = 0.2 + 2.6 * ease_out((tl - 0.9) / 0.4)
    t_up = 2.6
    ra_w = 2.8 * ease_out((tl - t_up) / 0.55) if tl > t_up else 0
    z = 1.35 + 0.3 * ease_io((tl - 1.4) / 1.2)
    with Cam(ctx, 600, 930, z):
        room(ctx, tg)
        figure(ctx, SX, FY, SHH, shadow=True, ra=ra_s, alpha=0.93)
        figure(ctx, WX, FY, WH, expr="worry" if tl < t_up else "fear", look=1.0, face=0.25, ra=ra_w, t=tl)
    grade(ctx, tg)
    if tl > 1.0:
        n = 10 - int(clamp((tl - 1.4) / 1.2) * 10)
        timer(ctx, 860, 500, n, tl - 1.0)
    if tl > tev - 0.05:
        cap2(ctx, "10 SECONDS EARLY", "EVERY TIME", 540, 1130, tl - tev + 0.05, WHT, (0, 0, 0), 80)


def s2(ctx, tg, tl, T):
    """S4-S5: the shadow ducks, ten seconds later a glass falls and shatters; the lamp dies"""
    tso = wt(2, "something")
    tc = T_CRASH
    duck_s = ease_out((tl - 0.1) / 0.15)
    fall0 = tc - 0.38
    shake = 10 * math.exp(-(tl - tc) * 6) * math.sin(tl * 60) if tl > tc else 0
    duck_w = 0.55 * ease_out((tl - tc - 0.1) / 0.2) if tl > tc + 0.1 else 0
    with Cam(ctx, 610 + shake, 960, 1.45):
        room(ctx, tg, glasses=2 if tl > fall0 else 3, wobble=clamp((tl - 0.6) / 0.6) if tl < fall0 else 0)
        figure(ctx, SX, FY, SHH, shadow=True, crouch=0.75 * duck_s, alpha=0.93)
        figure(ctx, WX, FY, WH, expr="calm" if tl < tc else "fear", crouch=duck_w, look=0.8 if tl > tc else 0, t=tl,
               la=2.7 * duck_w / 0.55, ra=2.7 * duck_w / 0.55)
        if fall0 <= tl < tc:
            f = (tl - fall0) / (tc - fall0)
            glass(ctx, 700 + 20 * f, 690 + 550 * f * f, f * 4)
        if tl >= tc:
            bt = tl - tc
            for k in range(22):
                vx = (hrand("gx", k) - 0.5) * 700; vy = -(150 + 380 * hrand("gy", k))
                px = 715 + vx * bt; py = FY - 6 + vy * bt + 1400 * bt * bt
                if py > FY + 30: py = FY + 10 + 20 * hrand("gz", k); px = 715 + vx * min(bt, 0.5)
                ctx.save(); ctx.translate(px, py); ctx.rotate(bt * 9 + k)
                ctx.move_to(-9, -5); ctx.line_to(10, -3); ctx.line_to(2, 8); ctx.close_path()
                ctx.set_source_rgba(0.85, 0.95, 1, 0.9); ctx.fill(); ctx.restore()
    grade(ctx, tg)
    if tl > tc and tl < tc + 0.08:
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.paint()
    if tl < tc + 0.05:
        n = 10 - int(clamp((tl - 0.15) / (tc - 0.15)) * 10)
        timer(ctx, 860, 500, n, tl - 0.15)
        if tl > 0.3: popchip(ctx, "IT DUCKED", 300, 500, tl - 0.3, YEL, (0, 0, 0), 82)
    if tl > tso - 0.05:
        cap2(ctx, "SOMETHING", "I COULDN'T SEE", 540, 520, tl - tso + 0.05, WHT, (0, 0, 0), 84)


def s3(ctx, tg, tl, T):
    """S6-S7: she walks to the door; the shadow stays, then turns its head to the hallway"""
    tst = wt(3, "stopped"); ttu = wt(3, "turned")
    wx = WX - 280 * ease_io((tl - 0.1) / 2.2)
    walking = 0.1 < tl < 2.3
    if tl < 2.6:
        with Cam(ctx, 560, 900, 1.05):
            room(ctx, tg, glasses=2)
            figure(ctx, SX, FY, SHH, shadow=True, alpha=0.93)
            figure(ctx, wx, FY, WH, expr="calm", face=-0.7, look=-1, walk=1.0 if walking else 0, t=tl)
        grade(ctx, tg)
        if tl > tst - 0.05:
            cap2(ctx, "IT STOPPED", "COPYING ME", 540, 520, tl - tst + 0.05, WHT, (0, 0, 0), 84)
    else:
        z = 1.5 + 0.25 * ease_io((tl - 2.6) / (T - 2.6))
        fa = ease_io((tl - ttu) / 0.7) if tl > ttu else 0
        with Cam(ctx, 640, 960, z):
            room(ctx, tg, glasses=2)
            figure(ctx, SX, FY, SHH, shadow=True, face=fa, alpha=0.93)
            figure(ctx, 190, FY, WH, expr="calm", face=-0.9, la=2.0, t=tl)
        grade(ctx, tg)
        if tl > ttu:
            popchip(ctx, "IT LOOKED AWAY", 540, 500, tl - ttu, WHT, (0, 0, 0), 78)


MSG = ("DON'T TURN", "AROUND")


def s4(ctx, tg, tl, T):
    """S8-S9: it points into the hallway, then writes DON'T TURN AROUND; her face as she reads it"""
    tpo = wt(4, "pointed")
    w0, w1 = 1.85, 3.5
    if tl < 3.6:
        u = SHH / 100
        letters = sum(len(m) for m in MSG)
        n = int(clamp((tl - w0) / (w1 - w0)) * letters) if tl > w0 else 0
        with Cam(ctx, 600, 900, 1.6):
            room(ctx, tg, glasses=2)
            size = 60
            pos = None
            shown = n
            for k, m in enumerate(MSG):
                part = m[:max(0, min(len(m), shown))]
                shown -= len(m)
                wfull = text_w(ctx, m, DISPLAY, size)
                x0 = 455 - wfull / 2; y = 760 + k * 82
                if part:
                    text(ctx, part, x0, y, size, (0.04, 0.03, 0.05), align="l", shadow=False, alpha=0.92)
                    text(ctx, part, x0 + 1.5, y + 2, size, (0.04, 0.03, 0.05), align="l", shadow=False, alpha=0.3)
                    if len(part) < len(m) or (k == len(MSG) - 1):
                        pos = (x0 + text_w(ctx, part, DISPLAY, size), y)
            if tl < w0 - 0.1:
                pt = ease_out((tl - tpo) / 0.35) if tl > tpo else 0
                figure(ctx, SX, FY, SHH, shadow=True, face=1.0, ra=0.2 + 1.37 * pt, finger=pt > 0.5, alpha=0.93)
            else:
                if pos is None: pos = (455 - 120, 760)
                sx, sy = SX - 18 * u, FY - 69 * u
                a = math.atan2(-(pos[0] - sx), pos[1] - sy)
                figure(ctx, SX, FY, SHH, shadow=True, face=-1.0, la=a, alpha=0.93)
        grade(ctx, tg)
        if tl > tpo and tl < w0:
            popchip(ctx, "IT POINTED", 820, 500, tl - tpo, WHT, (0, 0, 0), 78)
    else:
        tt = tl - 3.6
        ctx.set_source_rgb(0.87, 0.8, 0.69); ctx.paint()
        for dx, dy, a in ((0, 0, 0.18), (6, 4, 0.12), (-6, -3, 0.12)):
            text(ctx, "DON'T TURN AROUND", 540 + dx, 540 + dy, 92, (0.04, 0.03, 0.05), shadow=False, alpha=a * 2)
        br = 1 + 0.012 * math.sin(tl * 13)
        ctx.save(); ctx.translate(540, 2300); ctx.scale(br, br); ctx.translate(-540, -2300)
        figure(ctx, 540, 2300, 1500, expr="fear", look=0.3 + 0.7 * (math.sin(tt * 5) > 0), t=tl)
        ctx.restore()
        grade(ctx, tg)
        ctx.set_line_width(14); ctx.set_source_rgba(0.5, 0.75, 1, 0.5)
        ctx.arc(540, 2300 - 89 * 15, 230, -1.1, 0.6); ctx.stroke()


def closeup(ctx, tg, tl, point):
    """S12: her face fills the frame; the shadow on the wall behind her turns to point at the lens"""
    ctx.set_source_rgb(0.87, 0.8, 0.69); ctx.paint()
    for k in range(5):
        y0 = 420 + k * 170
        ctx.move_to(-100, y0); ctx.line_to(1200, y0 + 220); ctx.line_to(1200, y0 + 270); ctx.line_to(-100, y0 + 50); ctx.close_path()
        ctx.set_source_rgba(0.75, 0.85, 1, 0.12); ctx.fill()
    sc = 1 + 0.07 * point
    ctx.save(); ctx.translate(820, 1850); ctx.scale(sc, sc); ctx.translate(-820, -1850)
    figure(ctx, 820, 1850, 1250, shadow=True, face=0.0, cam_point=point, la=0.1, alpha=0.95)
    ctx.restore()
    figure(ctx, 400, 2350, 1500, expr="fear", look=0.15, t=tl)
    grade(ctx, tg)


def s5(ctx, tg, tl, T):
    """S10-S11: she turns, the hallway is empty; her shadow has left her feet and stands by the hallway"""
    tno = wt(5, "Nothing"); tbu = wt(5, "But"); tle = wt(5, "left"); tfe = wt(5, "feet")
    t12 = tfe + 0.45
    if tl < tbu - 0.1:
        with Cam(ctx, 990, 980, 1.7):
            room(ctx, tg, glasses=2)
        turn = ease_io(tl / 0.8)
        figure(ctx, 330 - 40 * turn, 2250, 1400, back=True, t=tl)
        grade(ctx, tg)
        if tl > tno - 0.05:
            cap2(ctx, "NOTHING", "THERE", 800, 1080, tl - tno + 0.05, WHT, (0, 0, 0), 82)
    elif tl < t12:
        with Cam(ctx, 520, 900, 1.05):
            room(ctx, tg, glasses=2)
            figure(ctx, 800, FY, SHH, shadow=True, face=1.0, ra=math.pi / 2, finger=True, alpha=0.93)
            figure(ctx, 230, FY, WH, expr="fear", face=0.5, look=1.0, t=tl)
            if tl > tbu + 0.25:
                a = clamp((tl - tbu - 0.25) / 0.2)
                ctx.save(); ctx.translate(230, FY + 6); ctx.scale(1, 0.28)
                ctx.set_dash([18, 12]); ctx.set_line_width(10); ctx.set_source_rgba(1, 0.25, 0.25, a)
                ctx.arc(0, 0, 150, 0, 6.3); ctx.stroke(); ctx.set_dash([]); ctx.restore()
        grade(ctx, tg)
        if tl > tle - 0.1:
            cap2(ctx, "IT LEFT", "MY FEET", 540, 500, tl - tle + 0.1, (1, 0.25, 0.25), WHT, 86)
    else:
        closeup(ctx, tg, tl, 0.0)


def s6(ctx, tg, tl, T):
    """S12-S13: it points at you; cut to black before anything is shown"""
    tpo = wt(6, "pointed"); tyo = wt(6, "you")
    tcut = tyo + 0.45
    if tl < tcut:
        p = ease_out((tl - tpo + 0.25) / 0.5) if tl > tpo - 0.25 else 0
        closeup(ctx, tg, tl, p)
        if tl > tyo - 0.05:
            cap2(ctx, "WHAT DID", "IT SEE?", 540, 520, tl - tyo + 0.05, WHT, (0, 0, 0), 88)
    else:
        tt = tl - tcut
        ctx.set_source_rgb(0, 0, 0); ctx.paint()
        s = pop(tt, 0.25)
        ctx.save(); ctx.translate(540, 760); ctx.scale(s, s)
        text(ctx, "PART 2?", 0, 0, 170, WHT, stroke=6)
        ctx.restore()
        if tt > 0.45:
            a = ease_out((tt - 0.45) / 0.3)
            text(ctx, "FOLLOW BEFORE", 540, 960, 74, YEL, stroke=5, alpha=a)
            text(ctx, "THE SHADOW MOVES AGAIN", 540, 1060, 74, YEL, stroke=5, alpha=a)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


# ---------------------------------------------------------------- sound
def _hit(A, t, g=0.6, f=55):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7) + A.hp(A.noise(0.6), 3000) * np.exp(-tt * 40) * 0.6
    A.add(A.sfx_buf, x, t, g)


def _buzz(A, t, d=0.22, g=0.12):
    n = int(d * SR); tt = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 120 * tt)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 23 * tt))) * 0.4
    A.add(A.sfx_buf, A.lp(x, 2500), t, g)


def _crash(A, t, g=0.5):
    n = int(0.9 * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.hp(A.noise(0.9), 2200) * np.exp(-tt * 7), t, g)
    for k in range(8):
        A.ding(t + 0.02 + k * 0.045, 0.03, 2400 + 380 * k, 0.4)


def _scrape(A, t, d=0.09, g=0.07):
    n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.bp(A.noise(d), 900, 4000) * np.sin(np.pi * tt / d), t, g)


def _breath(A, t, d=0.45, g=0.1):
    n = int(d * SR); tt = np.arange(n) / SR
    A.add(A.sfx_buf, A.bp(A.noise(d), 500, 2500) * np.sin(np.pi * tt / d) ** 2, t, g)


def _creak(A, t, d=0.9, g=0.1):
    n = int(d * SR); tt = np.arange(n) / SR
    x = A.bp(A.noise(d), 180, 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt)) * np.sin(np.pi * tt / d)
    A.add(A.sfx_buf, x, t, g)


def _drop(A, t, d=2.2, g=0.9):
    n = int(d * SR); tt = np.arange(n) / SR
    f = 70 * np.exp(-tt * 0.6) + 25
    A.add(A.sfx_buf, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.6) * np.minimum(1, (d - tt) / 0.2), t, g)


def sfx(A):
    S = A.S
    _hit(A, 0.0, 0.7)
    _buzz(A, 0.5, 0.15)
    for k in range(10):                                    # timer racing down in the proof shot
        A.ding(S(1) + 1.4 + k * 0.12, 0.05, 2600, 0.05)
    A.ding(S(1) + 2.6, 0.06, 1568, 0.6)
    _hit(A, S(2) + 0.1, 0.35, 80)                          # the shadow ducks
    for k in range(10):
        A.ding(S(2) + 0.2 + k * 0.17, 0.04, 2600, 0.05)
    _crash(A, S(2) + T_CRASH, 0.5)
    _buzz(A, S(2) + T_CRASH, 0.2, 0.15)
    for k in range(4):
        A.thump(S(3) + 0.25 + k * 0.55, 0.18, 95)          # footsteps to the door
    _creak(A, S(3) + wt(3, "turned"), 1.0, 0.12)
    for k in range(17):
        _scrape(A, S(4) + 1.85 + k * 0.1, 0.08, 0.06)       # finger writing on the wall
    for k in range(4):
        _breath(A, S(4) + 3.6 + k * 0.45, 0.4, 0.12)
    _breath(A, S(5) + 0.1, 0.5, 0.1)
    _drop(A, A.W(5, "But") - 0.05, 1.6, 0.9)
    _hit(A, S(6) + wt(6, "you") + 0.45, 0.8, 45)           # cut to black
    A.music_level(S(3), S(5), 0.55)
    A.music_level(A.W(5, "But") - 0.05, A.tl["total"] + 0.3, 0.0)

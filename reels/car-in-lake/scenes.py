"""Scenes for "What if your car rolled into a lake?". One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
Car, driver and kids are drawn in centimetres (cam/World) so they stay in true scale to each other."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

BG = bg_glow
MUSIC = {"beat_from_scene": 4, "bpm": 112}   # tense drone for the hook and the myths, beat from "four letters"

WATER = (0.06, 0.32, 0.62)
DEEP = (0.03, 0.12, 0.32)
CARC = (0.95, 0.3, 0.55)
AUNTY = [(0.95, 0.55, 0.15), (0.6, 0.35, 0.95)]


def wi(i, k):
    """scene-local start time of the k-th word of line i (safe for one-letter words)"""
    return TL["lines"][i]["words"][k]["s"] - TL["scenes"][i]["t0"]


class Cam:
    """world (cm) -> screen: world point (cx, cy) lands on screen (sx, sy), k px per cm"""
    def __init__(self, ctx, cx, cy, k, sx=540, sy=860, rot=0.0):
        self.a = (ctx, cx, cy, k, sx, sy, rot)
    def __enter__(self):
        ctx, cx, cy, k, sx, sy, rot = self.a
        ctx.save(); ctx.translate(sx, sy); ctx.scale(k, k); ctx.rotate(rot); ctx.translate(-cx, -cy); return ctx
    def __exit__(self, *a):
        self.a[0].restore()


# ---------------------------------------------------------------- scenery
def night(ctx, tg, moon=True):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.02, 0.03, 0.12); g.add_color_stop_rgb(0.55, 0.12, 0.06, 0.28); g.add_color_stop_rgb(1, 0.05, 0.03, 0.14)
    ctx.set_source(g); ctx.paint()
    for k in range(50):
        a = 0.25 + 0.45 * (0.5 + 0.5 * math.sin(tg * 2 + k * 1.7))
        ctx.arc(hrand("nx", k) * W, 380 + hrand("ny", k) * 500, 1.5 + 2 * hrand("ns", k), 0, 6.3)
        ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    if moon:
        glow_circle(ctx, 860, 560, 200, (1, 0.95, 0.7), 0.35)
        ctx.arc(860, 560, 60, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.75); ctx.fill()


def water(ctx, wl, t, front=True, x0=-3000, x1=3000):
    """water surface at world y = wl (call inside a Cam)"""
    ctx.move_to(x0, wl)
    x = x0
    while x <= x1:
        ctx.line_to(x, wl + 3.5 * math.sin(x * 0.03 + t * 3) + 2 * math.sin(x * 0.07 - t * 2))
        x += 10
    ctx.line_to(x1, wl + 4000); ctx.line_to(x0, wl + 4000); ctx.close_path()
    if front:
        g = cairo.LinearGradient(0, wl, 0, wl + 300)
        g.add_color_stop_rgba(0, *WATER, 0.78); g.add_color_stop_rgba(1, *DEEP, 0.95)
        ctx.set_source(g); ctx.fill_preserve()
        ctx.set_source_rgba(*CYN, 0.9); ctx.set_line_width(2.5)
        ctx.new_path(); x = x0; ctx.move_to(x0, wl)
        while x <= x1:
            ctx.line_to(x, wl + 3.5 * math.sin(x * 0.03 + t * 3) + 2 * math.sin(x * 0.07 - t * 2)); x += 10
        ctx.stroke()
    else:
        ctx.set_source_rgb(*DEEP); ctx.fill()


def bubbles(ctx, x, y, t, n=10, spread=60, rise=200, r=4, seed="bb"):
    for k in range(n):
        ph = (t * (0.5 + 0.6 * hrand(seed, k)) + hrand(seed + "o", k)) % 1
        bx = x + (hrand(seed + "x", k) - 0.5) * spread + math.sin(t * 4 + k) * 4
        by = y - ph * rise
        ctx.arc(bx, by, r * (0.6 + hrand(seed + "r", k)), 0, 6.3)
        ctx.set_source_rgba(0.8, 0.95, 1, 0.8 * (1 - ph)); ctx.set_line_width(r * 0.35); ctx.stroke()


# ---------------------------------------------------------------- car (cm, faces right, y=0 at the beltline)
FRONT_WIN = [(-20, -6), (-20, -64), (55, -64), (122, -6)]
REAR_WIN = [(-155, -6), (-117, -64), (-30, -64), (-30, -6)]


def poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()


def car(ctx, t, expr="shock", arms="down", win=0.0, glow=0.0, inside_wl=None, kids=None, driver=True, look=0.6):
    # cabin
    ctx.move_to(-172, 2); ctx.line_to(-122, -72); ctx.line_to(62, -72); ctx.line_to(140, 2); ctx.close_path()
    ctx.set_source_rgb(0.85, 0.24, 0.48); ctx.fill()
    # windows: dark interior, then people, then glass
    for pts in (REAR_WIN, FRONT_WIN):
        poly(ctx, pts); ctx.set_source_rgb(0.1, 0.08, 0.2); ctx.fill()
    if kids:
        ctx.save(); poly(ctx, REAR_WIN); ctx.clip()
        for (kx, kh, kexp) in kids:
            person(ctx, kx, 85, kh, SHIRTS[3] if kh > 120 else SHIRTS[4], kexp, "down", t, look=0.5)
        ctx.restore()
    if driver:
        ctx.save(); poly(ctx, FRONT_WIN); ctx.clip()
        person(ctx, 28, 99, 150, SHIRTS[1], expr, arms, t, look=look)
        ctx.restore()
    if inside_wl is not None:
        for pts in (REAR_WIN, FRONT_WIN):
            ctx.save(); poly(ctx, pts); ctx.clip()
            ctx.rectangle(-300, inside_wl + 2 * math.sin(t * 3), 600, 200); ctx.set_source_rgba(*WATER, 0.75); ctx.fill()
            ctx.restore()
    # glass (front glass drops as win -> 1)
    ctx.save(); poly(ctx, REAR_WIN); ctx.clip(); ctx.paint_with_alpha(0)
    ctx.rectangle(-300, -80, 600, 80); ctx.set_source_rgba(0.6, 0.9, 1, 0.22); ctx.fill(); ctx.restore()
    ctx.save(); poly(ctx, FRONT_WIN); ctx.clip()
    gy = -64 + 58 * win
    ctx.rectangle(-300, gy, 600, 80); ctx.set_source_rgba(0.6, 0.9, 1, 0.22); ctx.fill()
    ctx.move_to(0, gy + 8); ctx.line_to(20, gy + 8); ctx.line_to(-5, gy + 40); ctx.line_to(-25, gy + 40); ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.25); ctx.fill()
    ctx.restore()
    # pillar
    ctx.rectangle(-30, -66, 10, 66); ctx.set_source_rgb(0.85, 0.24, 0.48); ctx.fill()
    # lower body
    rrect(ctx, -218, 0, 436, 64, 22); ctx.set_source_rgb(*CARC); ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.35); ctx.set_line_width(2.2)
    rrect(ctx, -25, 2, 135, 54, 6); ctx.stroke()
    rrect(ctx, -165, 2, 135, 54, 6); ctx.stroke()
    rrect(ctx, 80, 14, 22, 6, 3); ctx.set_source_rgb(0.98, 0.85, 0.9); ctx.fill()
    rrect(ctx, -60, 14, 22, 6, 3); ctx.fill()
    ctx.arc(208, 18, 9, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.6); ctx.fill()
    rrect(ctx, -220, 8, 10, 18, 4); ctx.set_source_rgb(1, 0.25, 0.25); ctx.fill()
    for wx in (-135, 135):
        ctx.arc(wx, 64, 34, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.12); ctx.fill()
        ctx.arc(wx, 64, 17, 0, 6.3); ctx.set_source_rgb(0.75, 0.78, 0.85); ctx.fill()
    if glow > 0:
        poly(ctx, FRONT_WIN); ctx.set_source_rgba(*YEL, glow); ctx.set_line_width(7); ctx.stroke()


# ---------------------------------------------------------------- props (screen px)
def phone(ctx, x, y, s, lines, col=(0.25, 0.35, 0.9), rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rrect(ctx, -110, -200, 220, 400, 34); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
    rrect(ctx, -98, -188, 196, 376, 26)
    g = cairo.LinearGradient(0, -190, 0, 190); g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, 0.55, 0.25, 0.75)
    ctx.set_source(g); ctx.fill()
    for k, (txt, sz) in enumerate(lines):
        text(ctx, txt, 0, -90 + k * 70, sz, WHT, shadow=False)
    ctx.arc(0, 130, 34, 0, 6.3); ctx.set_source_rgb(*GRN); ctx.fill()
    ctx.restore()


def tool(ctx, x, y, s, rot=-0.6):
    """window-breaker hammer: head at origin"""
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    rrect(ctx, -14, 0, 28, 150, 12); ctx.set_source_rgb(*RED); ctx.fill()
    rrect(ctx, -60, -26, 120, 34, 10); ctx.set_source_rgb(0.8, 0.82, 0.88); ctx.fill()
    for sx in (-1, 1):
        ctx.move_to(sx * 60, -26); ctx.line_to(sx * 84, -9); ctx.line_to(sx * 60, 8); ctx.close_path()
        ctx.set_source_rgb(0.95, 0.96, 1); ctx.fill()
    ctx.restore()


def aunty(ctx, x, y, h, col, t, look=0.0):
    person(ctx, x, y, h, col, "smile", "down", t, look=look)
    u = h / 100
    ctx.arc(x, y - 104 * u, 8 * u, 0, 6.3); ctx.set_source_rgb(0.15, 0.1, 0.08); ctx.fill()
    ctx.arc(x + look * 3 * u, y - 88.5 * u, 1.6 * u, 0, 6.3); ctx.set_source_rgb(0.9, 0.1, 0.2); ctx.fill()
    # dupatta
    ctx.move_to(x - 19 * u, y - 70 * u); ctx.line_to(x + 19 * u, y - 50 * u); ctx.set_line_width(6 * u)
    ctx.set_source_rgba(*YEL, 0.9); ctx.stroke()


def bubble(ctx, x, y, s, txt, tt, col=PNK):
    if tt < 0: return
    sc = pop(tt, 0.2)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    w = text_w(ctx, txt, DISPLAY, s) + 60
    rrect(ctx, -w / 2, -s * 0.75, w, s * 1.5, s * 0.5); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.move_to(w * 0.15, s * 0.6); ctx.line_to(w * 0.3, s * 1.4); ctx.line_to(w * 0.32, s * 0.6); ctx.close_path(); ctx.fill()
    text(ctx, txt, 0, 0, s, col, shadow=False)
    ctx.restore()


def jar(ctx, x, y, s, col=(0.95, 0.45, 0.1)):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -50, -120, 100, 120, 18); ctx.set_source_rgba(0.85, 0.95, 1, 0.5); ctx.fill()
    rrect(ctx, -44, -96, 88, 92, 14); ctx.set_source_rgb(*col); ctx.fill()
    for k in range(8):
        ctx.arc(-30 + hrand("jx", k) * 60, -85 + hrand("jy", k) * 70, 6, 0, 6.3)
        ctx.set_source_rgba(0.6, 0.15, 0.05, 0.8); ctx.fill()
    rrect(ctx, -54, -140, 108, 26, 8); ctx.set_source_rgb(*RED); ctx.fill()
    rrect(ctx, -40, -72, 80, 34, 6); ctx.set_source_rgb(1, 0.97, 0.88); ctx.fill()
    text(ctx, "ACHAAR", 0, -55, 20, (0.6, 0.1, 0.1), SANS, shadow=False)
    ctx.restore()


def tiles(ctx, cur, tt):
    """S W C O progress row at the top; cur = index of the active letter"""
    for k, L_ in enumerate("SWCO"):
        x = 540 + (k - 1.5) * 150
        on = k == cur
        s = (1.0 + 0.25 * (1 - ease_out(tt / 0.3))) if on else 0.8
        ctx.save(); ctx.translate(x, 500); ctx.scale(s, s)
        rrect(ctx, -55, -55, 110, 110, 22)
        ctx.set_source_rgb(*([YEL, CYN, PNK, GRN][k] if k <= cur else (0.25, 0.25, 0.4))); ctx.fill()
        text(ctx, L_, 0, 0, 80, (0, 0, 0) if k <= cur else (0.6, 0.6, 0.75), shadow=False)
        ctx.restore()


def splash(ctx, x, y, tt, n=40, spread=260, seed="sp"):
    """droplets thrown up from (x, y) world, tt seconds after impact"""
    if tt < 0 or tt > 1.6: return
    for k in range(n):
        vx = (hrand(seed, k) - 0.5) * spread * 2.2
        vy = -(260 + 360 * hrand(seed + "v", k))
        px = x + vx * tt; py = y + vy * tt + 0.5 * 981 * tt * tt
        if py > y + 10: continue
        ctx.arc(px, py, 4 + 7 * hrand(seed + "r", k), 0, 6.3)
        ctx.set_source_rgba(0.75, 0.95, 1, 0.9 * (1 - tt / 1.6)); ctx.fill()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tst = wt(0, "still")
    night(ctx, tg)
    hit = 0.3
    if tl < hit:
        f = tl / hit
        cx, cy, rot = -240 + 240 * f, -320 + 320 * f * f, 0.5 - 0.3 * f
    else:
        b = tl - hit
        cx, cy = 0, 18 * math.sin(b * 2.2) * math.exp(-b * 0.8) + 8 * math.sin(b * 1.3)
        rot = 0.2 * math.exp(-b * 2) * math.cos(b * 5) + 0.04 * math.sin(b * 1.7)
    shake = 14 * math.exp(-max(0, tl - hit) * 5) if tl > hit else 0
    z = ease_io((tl - tst + 0.1) / 0.6)
    k = 2.4 + 3.9 * z
    fx, fy = 0 + 50 * z, 0 - 60 * z
    with Cam(ctx, fx, fy, k, 540 + shake * math.sin(tl * 60), 900 + shake * math.cos(tl * 47)):
        water(ctx, 30, tg, front=False)
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot)
        car(ctx, tl, "shock", "up" if tl > hit else "down", look=0.8)
        ctx.restore()
        water(ctx, 30, tg)
        splash(ctx, 150, 30, tl - hit, seed="a"); splash(ctx, -150, 30, tl - hit - 0.05, seed="b")
    if tl < hit + 0.12 and tl > hit:
        ctx.set_source_rgba(1, 1, 1, 0.5 * (1 - (tl - hit) / 0.12)); ctx.paint()
    if z > 0:
        g = cairo.RadialGradient(540, 900, 300, 540, 900, 1100)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.6, 0, 0.05, (0.45 + 0.15 * math.sin(tl * 9)) * z)
        ctx.set_source(g); ctx.paint()
    if tl < wt(0, "Your") + 0.6:
        popchip(ctx, "SPLASH!", 540, 520, tl - hit, CYN, (0, 0, 0), 70)


def s1(ctx, tg, tl, T):
    tw = wt(1, "window"); tli = wt(1, "Literally")
    night(ctx, tg)
    sink = ease_io(tl / T)
    rot = 0.05 + 0.13 * sink
    with Cam(ctx, 0, 0, 2.1, 540, 930):
        water(ctx, 30 - 40 * sink, tg, front=False)
        ctx.save(); ctx.rotate(rot)
        g = 0.9 * (0.6 + 0.4 * math.sin(tl * 10)) if tl > tw - 0.05 else 0
        car(ctx, tl, "worry", "down", glow=g)
        ctx.restore()
        water(ctx, 30 - 40 * sink, tg)
        bubbles(ctx, 200, 60, tl, 8, 80, 90, 5)
    # big countdown ring
    secs = 60 - tl
    cx, cy, r = 540, 560, 95
    ctx.arc(cx, cy, r + 14, 0, 6.3); ctx.set_source_rgba(0, 0, 0, 0.5); ctx.fill()
    ctx.set_line_width(14); ctx.arc(cx, cy, r, 0, 6.3); ctx.set_source_rgba(1, 1, 1, 0.2); ctx.stroke()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * secs / 60); ctx.set_source_rgb(*RED if secs < 57 else YEL); ctx.stroke()
    text(ctx, f"{int(math.ceil(secs))}", cx, cy - 8, 92, WHT)
    text(ctx, "SEC", cx, cy + 58, 30, WHT, SANS)
    if tl > tw - 0.05:
        popchip(ctx, "YOUR WINDOW", 820, 760, tl - tw + 0.05, YEL, (0, 0, 0), 46)
        # arrow to window
        a = ease_out((tl - tw) / 0.25)
        ctx.set_source_rgba(*YEL, a); ctx.set_line_width(10)
        ctx.move_to(800, 800); ctx.line_to(720, 815); ctx.stroke()
        ctx.move_to(700, 818); ctx.line_to(735, 795); ctx.line_to(738, 838); ctx.close_path(); ctx.fill()
    stamp(ctx, "LITERALLY", 540, 1150, tl - tli + 0.05, PNK, 84, -0.08)


def s2(ctx, tg, tl, T):
    tg_ = wt(2, "Grab"); td = wt(2, "Don't"); tm = wt(2, "Mummy")
    # interior: seat, big worried driver
    rrect(ctx, 200, 520, 680, 900, 120); ctx.set_source_rgb(0.22, 0.14, 0.38); ctx.fill()
    rrect(ctx, 330, 470, 420, 160, 60); ctx.set_source_rgb(0.28, 0.18, 0.46); ctx.fill()
    s = pop(tl, 0.25)
    ctx.save(); ctx.translate(470, 1400); ctx.scale(s, s)
    person(ctx, 0, 0, 1050, SHIRTS[1], "worry" if tl < tg_ else "shock", "down", tl, look=0.8)
    ctx.restore()
    # water creeping on the windows
    ctx.rectangle(0, 1180 - 30 * ease_io(tl / T), W, 400); ctx.set_source_rgba(*WATER, 0.35); ctx.fill()
    if tl < tg_ - 0.1:
        bubble(ctx, 820, 640, 90, "?", tl - 0.05, YEL)
    else:
        ps = pop(tl - tg_ + 0.1, 0.22)
        txt = [("CALLING", 34), ("MUMMY", 56)] if tl > tm - 0.3 else [("9:41", 60), ("", 10)]
        phone(ctx, 800, 900, 1.1 * ps, txt, rot=0.12)
        if tl > td - 0.03:
            a = clamp((tl - td + 0.03) / 0.12)
            ctx.save(); ctx.translate(800, 900); ctx.scale(0.5 + 0.5 * a, 0.5 + 0.5 * a)
            cross(ctx, 0, 0, 380, RED, 50)
            ctx.restore()
            stamp(ctx, "DON'T!", 330, 640, tl - td + 0.03, RED, 96, -0.12)
    if tl > tm + 0.4:
        popchip(ctx, "ESCAPE FIRST. CALL LATER.", 540, 1200, tl - tm - 0.4, YEL, (0, 0, 0), 50)


def s3(ctx, tg, tl, T):
    tth = wt(3, "then"); tmy = wt(3, "Myth"); tpr = wt(3, "pressure")
    night(ctx, tg, moon=False)
    push = tl > tth - 0.1
    fill = ease_io(tl / (tth + 0.3))
    with Cam(ctx, 40, -10, 4.4, 540, 880):
        water(ctx, -40, tg, front=False)
        jig = 1.5 * math.sin(tl * 40) if push and tl < tmy else 0
        ctx.save(); ctx.translate(jig, 0)
        car(ctx, tl, "worry" if not push else "shock", "up" if push else "down", inside_wl=20 - 50 * fill if tl < tmy else None, look=0.9)
        ctx.restore()
        water(ctx, -40, tg)
        # pressure arrows pushing on the door
        if tl > tmy - 0.1:
            a = ease_out((tl - tmy + 0.1) / 0.3)
            for r_ in range(2):
                for c in range(4):
                    x = -10 + c * 32; y = 2 + r_ * 22
                    off = 10 * math.sin(tl * 6 + c + r_)
                    ctx.save(); ctx.translate(x, y + 16 + off * 0.2)
                    ctx.set_source_rgba(*CYN, a); ctx.set_line_width(4)
                    ctx.move_to(0, 22); ctx.line_to(0, 6); ctx.stroke()
                    ctx.move_to(-8, 8); ctx.line_to(8, 8); ctx.line_to(0, -6); ctx.close_path(); ctx.fill()
                    ctx.restore()
    if tl < tmy:
        popchip(ctx, "WAIT TO FILL UP?", 540, 560, tl - 0.1, WHT, (0, 0, 0), 66)
    if push and tl < tmy:
        popchip(ctx, "PUSH!", 300, 1150, tl - tth + 0.1, YEL, (0, 0, 0), 60)
    stamp(ctx, "MYTH!", 540, 560, tl - tmy + 0.03, RED, 120, -0.1)
    if tl > tpr - 0.05:
        popchip(ctx, "WATER PINS THE DOOR SHUT", 540, 1205, tl - tpr + 0.05, CYN, (0, 0, 0), 48)


def s4(ctx, tg, tl, T):
    tf = wt(4, "four")
    ts = [wi(4, k) for k in range(4, 8)]
    if tl < ts[0] - 0.1:
        s = pop(tl - tf + 0.1, 0.25)
        ctx.save(); ctx.translate(540, 860); ctx.scale(s, s)
        glow_circle(ctx, 0, 0, 420, PNK, 0.4)
        text(ctx, "4", 0, -40, 420, YEL, stroke=8)
        text(ctx, "LETTERS", 0, 230, 110, WHT, stroke=6)
        ctx.restore()
    else:
        cols = [YEL, CYN, PNK, GRN]
        for k, L_ in enumerate("SWCO"):
            tt = tl - ts[k] + 0.05
            if tt < 0: continue
            s = pop(tt, 0.2) * (1 + 0.04 * math.sin(tl * 6 + k))
            x = 300 + (k % 2) * 480; y = 700 + (k // 2) * 400
            ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate((k % 2 - 0.5) * 0.1)
            glow_circle(ctx, 0, 0, 260, cols[k], 0.35)
            rrect(ctx, -160, -160, 320, 320, 50); ctx.set_source_rgb(*cols[k]); ctx.fill()
            text(ctx, L_, 0, 0, 240, (0.05, 0.05, 0.15), shadow=False)
            ctx.restore()


def s5(ctx, tg, tl, T):
    toff = wt(5, "off"); tfa = wt(5, "Faster"); tsh = wt(5, "shaadi")
    tiles(ctx, 0, tl)
    if tl < tfa - 0.1:
        rrect(ctx, 230, 660, 620, 800, 110); ctx.set_source_rgb(0.22, 0.14, 0.38); ctx.fill()
        s = pop(tl, 0.22)
        h = 1000; u = h / 100; px, py = 540, 1580
        ctx.save(); ctx.translate(px, py); ctx.scale(s, s)
        person(ctx, 0, 0, h, SHIRTS[1], "worry" if tl < toff else "smile", "down" if tl < toff else "up", tl)
        # seatbelt
        f = ease_out((tl - toff) / 0.35) if tl > toff else 0
        ctx.set_line_width(7 * u); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(0.15, 0.15, 0.2)
        ctx.move_to(15 * u + 40 * u * f, -72 * u - 30 * u * f); ctx.line_to(-15 * u + 70 * u * f, -38 * u - 70 * u * f); ctx.stroke()
        rrect(ctx, -22 * u, -42 * u, 12 * u, 6 * u, 1.5 * u); ctx.set_source_rgb(0.8, 0.82, 0.9); ctx.fill()
        ctx.restore()
        if tl > toff - 0.05:
            popchip(ctx, "CLICK!", 830, 820, tl - toff + 0.05, YEL, (0, 0, 0), 64)
    else:
        tt = tl - tfa + 0.1
        # aunties closing in from the right, hero sprinting left
        ax = 1000 - 140 * ease_out(tt / 0.8)
        aunty(ctx, ax - 120, 1230, 560, AUNTY[0], tl, look=-1)
        aunty(ctx, ax + 90, 1230, 520, AUNTY[1], tl, look=-1)
        bubble(ctx, ax - 40, 600, 70, "SHAADI KAB?", tl - tsh + 0.05)
        hx = 380 - 220 * ease_io((tl - tsh) / 1.0) if tl > tsh else 380
        hop = abs(math.sin(tl * 10)) * 20
        person(ctx, hx, 1230 - hop, 560, SHIRTS[1], "shock", "run", tl, look=-1)
        for k in range(4):
            ctx.move_to(hx + 140 + k * 10, 860 + k * 70); ctx.line_to(hx + 240 + k * 10, 860 + k * 70)
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(6); ctx.stroke()


def s6(ctx, tg, tl, T):
    tpw = wt(6, "Power"); tst = wt(6, "Stuck"); tco = wt(6, "corner")
    tiles(ctx, 1, tl)
    if tl < tst - 0.1:
        win = ease_io((tl - 0.4) / 1.2)
        with Cam(ctx, 45, -32, 6.2, 540, 880):
            car(ctx, tl, "worry" if win < 0.5 else "smile", "down", win=win, look=0.9)
            water(ctx, 60, tg)
        if tl > tpw - 0.05:
            # window switch panel
            ps = pop(tl - tpw + 0.05, 0.22)
            ctx.save(); ctx.translate(800, 1120); ctx.scale(ps, ps)
            rrect(ctx, -150, -70, 300, 140, 30); ctx.set_source_rgb(0.15, 0.15, 0.22); ctx.fill()
            rrect(ctx, -60, -45, 120, 90, 18); ctx.set_source_rgb(0.4, 0.42, 0.5); ctx.fill()
            ctx.move_to(-30, -10); ctx.line_to(30, -10); ctx.line_to(0, 30); ctx.close_path(); ctx.set_source_rgb(*WHT); ctx.fill()
            ctx.move_to(100, -50); ctx.line_to(80, 5); ctx.line_to(105, 5); ctx.line_to(90, 55); ctx.line_to(130, -10); ctx.line_to(105, -10); ctx.line_to(120, -50); ctx.close_path()
            ctx.set_source_rgb(*YEL); ctx.fill()
            ctx.restore()
            popchip(ctx, "USUALLY WORKS AT FIRST", 360, 1120, tl - tpw - 0.3, YEL, (0, 0, 0), 40)
        else:
            popchip(ctx, "OPEN IT EARLY", 540, 640, tl - 0.4, CYN, (0, 0, 0), 56)
    else:
        tt = tl - tst + 0.1
        hitt = tco - tst + 0.1
        with Cam(ctx, 45, -32, 6.2, 540, 880):
            car(ctx, tl, "shock", "down", win=0, look=0.9)
            water(ctx, 60, tg)
        # hammer swings to the bottom corner of the glass (screen coords of world (110, -12))
        cx, cy = 540 + (110 - 45) * 6.2, 880 + (-12 + 32) * 6.2
        if tt < hitt:
            sw = ease_io(tt / max(0.3, hitt))
            tool(ctx, cx + 230 - 230 * sw, cy - 60 + 60 * sw, 1.3, -1.2 + 0.6 * sw)
        else:
            bt = tt - hitt
            # cracks + shards
            ctx.set_source_rgba(1, 1, 1, 0.95); ctx.set_line_width(4)
            for k in range(11):
                a = math.pi * 0.55 + k * 0.12 * math.pi
                L_ = (120 + 260 * hrand("cr", k)) * ease_out(bt / 0.15)
                ctx.move_to(cx, cy); ctx.line_to(cx + math.cos(a) * L_, cy + math.sin(a) * L_ * 0.8 - 60 * (k % 3) * ease_out(bt / 0.15))
            ctx.stroke()
            for k in range(26):
                vx = -(80 + 400 * hrand("gx", k)); vy = -(100 + 400 * hrand("gy", k))
                px = cx - 80 + vx * bt; py = cy - 80 + vy * bt + 900 * bt * bt
                if py > 1260: continue
                ctx.save(); ctx.translate(px, py); ctx.rotate(bt * 8 + k)
                ctx.move_to(-10, -6); ctx.line_to(12, -4); ctx.line_to(2, 10); ctx.close_path()
                ctx.set_source_rgba(0.75, 0.95, 1, 0.9); ctx.fill(); ctx.restore()
            tool(ctx, cx + 20, cy, 1.3, -0.6)
            stamp(ctx, "SMASH!", 360, 640, bt, RED, 100, -0.1)
        if tl > tco - 0.05:
            popchip(ctx, "HIT A CORNER", 540, 1180, tl - tco + 0.05, YEL, (0, 0, 0), 56)


def s7(ctx, tg, tl, T):
    tch = wt(7, "Children"); tol = wt(7, "Oldest")
    night(ctx, tg, moon=False)
    tiles(ctx, 2, tl)
    out = [(135, SHIRTS[3], 20, tch + 0.1), (110, SHIRTS[4], -70, tol + 0.1)]   # oldest first
    inside = [(-105, 135, "worry"), (-60, 110, "worry")]
    inside = [kd for kd, o in zip(inside, out) if tl < o[3]]
    with Cam(ctx, -40, -30, 2.6, 540, 1050):
        water(ctx, -6, tg, front=False)
        car(ctx, tl, "smile", "down", win=1.0, kids=inside, look=0.5)
        for n, (kh, col, kx, t0) in enumerate(out):
            f = ease_out((tl - t0) / 0.4)
            if f <= 0: continue
            y = -72 + (1 - f) * 70
            person(ctx, kx, y, kh, col, "smile", "wave", tl)
            ctx.save(); ctx.translate(kx - 34, y - kh * 0.95)
            ctx.arc(0, 0, 17, 0, 6.3); ctx.set_source_rgb(*WHT); ctx.fill()
            text(ctx, str(n + 1), 0, 0, 24, (0, 0, 0), shadow=False)
            ctx.restore()
        water(ctx, -6, tg)
    if tl < tol - 0.05:
        popchip(ctx, "KIDS FIRST", 540, 1200, tl - tch + 0.05, PNK, WHT, 60)
    else:
        popchip(ctx, "OLDEST → YOUNGEST", 540, 1200, tl - tol + 0.05, YEL, (0, 0, 0), 54)


def s8(ctx, tg, tl, T):
    tsw = wt(8, "Swim"); tth = wt(8, "Then"); t112 = wt(8, "112")
    night(ctx, tg, moon=True)
    tiles(ctx, 3, tl)
    wl = 760
    if tl < tth - 0.1:
        up = ease_io((tl - tsw + 0.3) / 0.9)
        y = 1500 - 690 * up
        ctx.rectangle(0, wl, W, H); ctx.set_source_rgba(*WATER, 0.6); ctx.fill()
        person(ctx, 540, y + 100, 640, SHIRTS[1], "shock" if up < 1 else "smile", "up", tl)
        bubbles(ctx, 540, y - 400, tl, 14, 200, 300, 10)
        ctx.rectangle(0, wl, W, H); ctx.set_source_rgba(*WATER, 0.25); ctx.fill()
        ctx.rectangle(0, wl - 3, W, 6); ctx.set_source_rgba(*CYN, 0.9); ctx.fill()
        popchip(ctx, "OUT!", 540, 600, tl - 0.05, GRN, (0, 0, 0), 80)
    else:
        tt = tl - tth + 0.1
        ctx.rectangle(0, 1100, W, H); ctx.set_source_rgba(*WATER, 0.6); ctx.fill()
        person(ctx, 330, 1250, 560, SHIRTS[1], "smile", "wave", tl)
        ctx.rectangle(0, 1100, W, H); ctx.set_source_rgba(*WATER, 0.3); ctx.fill()
        ps = pop(tt, 0.22)
        phone(ctx, 760, 880, 1.05 * ps, [("DIALLING", 32), ("112", 96)], col=(0.15, 0.6, 0.45), rot=0.08)
        if tl > t112 + 0.3:
            popchip(ctx, "INDIA EMERGENCY: 112", 540, 1190, tl - t112 - 0.3, YEL, (0, 0, 0), 48)


def s9(ctx, tg, tl, T):
    tn = wt(9, "Not"); tp = wt(9, "pickle"); twh = wt(9, "Who")
    end = tl > twh - 0.05
    if tl < tn - 0.1:
        # tool on a keychain / visor
        s = pop(tl, 0.25)
        ctx.save(); ctx.translate(540, 820); ctx.scale(s, s)
        glow_circle(ctx, 0, 0, 380, YEL, 0.35)
        sw = math.sin(tl * 3) * 0.12
        ctx.rotate(sw)
        ctx.arc(0, -300, 40, 0, 6.3); ctx.set_source_rgb(0.85, 0.85, 0.9); ctx.set_line_width(12); ctx.stroke()
        ctx.move_to(0, -260); ctx.line_to(0, -170); ctx.stroke()
        tool(ctx, 0, -150, 2.4, 0)
        ctx.restore()
        popchip(ctx, "KEYCHAIN • VISOR • CONSOLE", 540, 1180, tl - 0.6, CYN, (0, 0, 0), 44)
    elif not end:
        tt = tl - tn + 0.1
        # open dikki: boot full of luggage and pickle jars, tool buried at the bottom
        s = pop(tt, 0.25)
        ctx.save(); ctx.translate(540, 880); ctx.scale(s, s)
        ctx.move_to(-400, -260); ctx.line_to(400, -260); ctx.line_to(330, -420); ctx.line_to(-330, -420); ctx.close_path()
        ctx.set_source_rgb(0.85, 0.24, 0.48); ctx.fill()
        rrect(ctx, -420, -260, 840, 560, 40); ctx.set_source_rgb(*CARC); ctx.fill()
        rrect(ctx, -360, -220, 720, 400, 20); ctx.set_source_rgb(0.12, 0.08, 0.2); ctx.fill()
        ctx.arc(-200, 80, 110, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
        ctx.arc(-200, 80, 55, 0, 6.3); ctx.set_source_rgb(0.6, 0.62, 0.7); ctx.fill()
        tool(ctx, 150, 150, 0.55, 1.4)
        nj = int(clamp((tl - tp + 0.2) / 0.8) * 6) if tl > tp - 0.2 else 0
        for k in range(nj):
            jx = -40 + (k % 3) * 120; jy = 170 - (k // 3) * 150
            jar(ctx, jx, jy, 1.0, [(0.95, 0.45, 0.1), (0.85, 0.2, 0.1), (0.95, 0.7, 0.1)][k % 3])
        ctx.restore()
        stamp(ctx, "NOT IN THE DIKKI!", 540, 520, tt - 0.15, RED, 76, -0.08)
    else:
        tt = tl - twh + 0.05
        sc = pop(tt, 0.25) * (1 + 0.05 * math.sin(tt * 8))
        ctx.save(); ctx.translate(540, 820); ctx.scale(sc, sc)
        g = cairo.LinearGradient(-380, 0, 380, 0)
        g.add_color_stop_rgb(0, 0.15, 0.55, 1.0); g.add_color_stop_rgb(1, 0.95, 0.25, 0.6)
        rrect(ctx, -380, -90, 760, 180, 90); ctx.set_source(g); ctx.fill()
        text(ctx, "TAG THEM", 0, 0, 110, WHT, shadow=False)
        ctx.restore()
        text(ctx, "WHO NEEDS TO SEE THIS?", 540, 1010, 64, WHT, stroke=5, alpha=ease_out((tt - 0.2) / 0.2))
        tool(ctx, 540, 1150, 0.7, 0)


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]


def _splash(A, t, g=0.5, d=0.9):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.lp(A.noise(d), 1800) * np.exp(-tt * 4) + A.hp(A.noise(d), 4000) * 0.4 * np.exp(-tt * 7)
    A.add(A.sfx_buf, x, t, g)


def sfx(A):
    for k in range(int(A.S(4) / 0.8)):
        A.thump(0.6 + k * 0.8, 0.45, 50)                   # heartbeat under the hook and the myths
    A.whoosh(0.5, 0.25, 0.45)
    _splash(A, 0.5, 0.6)
    A.thump(0.5, 0.6, 60)
    A.thump(A.W(0, "still") - 0.05, 0.5, 45)
    for k in range(5):
        A.ding(A.S(1) + 0.2 + k * 1.0, 0.04, 2000, 0.15)   # clock tick
    A.ding(A.W(1, "window"), 0.1, 1318.5)
    A.boing(A.W(1, "Literally"), 0.12, 500, 0.35)
    A.pop(A.W(2, "Grab"), 0.3)
    A.scratch(A.W(2, "Don't") - 0.05, 0.3)
    A.thump(A.W(3, "then") + 0.1, 0.4, 90); A.thump(A.W(3, "then") + 0.4, 0.4, 90)
    A.thump(A.W(3, "Myth") - 0.02, 0.6, 60)
    for k in range(4):
        t = A.tl["lines"][4]["words"][4 + k]["s"]
        A.pop(t, 0.3); A.ding(t + 0.02, 0.07, A.note(72 + [0, 4, 7, 12][k]))
    A.pop(A.W(5, "off"), 0.4)
    A.boing(A.W(5, "shaadi"), 0.18, 350)
    A.whoosh(A.W(6, "Window") + 0.5, 0.15, 0.6)
    t_hit = A.W(6, "corner")
    import numpy as np
    A.add(A.sfx_buf, A.hp(A.noise(0.5), 2500) * np.exp(-np.arange(int(0.5 * 44100)) / 44100 * 9), t_hit, 0.5)
    for k in range(6):
        A.ding(t_hit + 0.03 + k * 0.05, 0.03, 2500 + 400 * k, 0.4)
    A.pop(A.W(7, "Oldest") - 0.4, 0.25); A.pop(A.W(7, "Oldest") + 0.35, 0.25)
    _splash(A, A.W(8, "Swim") + 0.6, 0.35, 0.6)
    A.ding(A.W(8, "112"), 0.08, 1568); A.ding(A.W(8, "112") + 0.12, 0.08, 2093)
    A.scratch(A.W(9, "Not") - 0.1, 0.3)
    A.thump(A.W(9, "Not") + 0.1, 0.5, 70)
    A.pop(A.W(9, "Who"), 0.35)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(9, "Who") + 0.1 + k * 0.1, 0.07, A.note(m))

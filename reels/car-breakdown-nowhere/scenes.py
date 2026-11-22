"""Scenes for "What if your car broke down in the middle of nowhere?" (card style, English, female voice).
Everyday-emergencies queue, topic 3. Injected by reelkit.make before this runs: wt(line_i, word), TL, SCRIPT."""
import math
import cairo
from reelkit.lib import clamp, ease_out, ease_io, pop, rrect, hrand, W, H
from reelkit.cards import *  # noqa: F401,F403

NO_FLASH = tuple(range(10))
STEEL = (0.16, 0.17, 0.23)
DARK = (0.01, 0.01, 0.02)
ASPH = (0.11, 0.115, 0.14)
SHOUL = (0.2, 0.19, 0.17)
GRASS = (0.06, 0.12, 0.08)
CARC = (0.85, 0.87, 0.92)


def cut_times(i):
    try:
        return {0: [0, wt(0, "lights") - 0.1, wt(0, "Twenty") - 0.1],
                1: [0, wt(1, "Don") - 0.05, wt(1, "Four") - 0.1],
                2: [0, wt(2, "Fully") - 0.1], 3: [0, wt(3, "Never") - 0.1],
                4: [0, wt(4, "Bonnet") - 0.1], 5: [0, wt(5, "borrow") - 0.3]}.get(i, [0])
    except KeyError:
        return [0]


def blink(t, hz=1.6):
    return (t * hz) % 1 < 0.55


# ---------------------------------------------------------------- props (screen px)
def car_side(ctx, x, y, s, col=CARC, head=0.0, hazard=False, t=0.0, bonnet=0.0):
    """side view of a hatchback facing right; (x, y) = centre of the wheel line"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if head > 0:  # headlight beam
        g = cairo.LinearGradient(170, 0, 620, 0)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.5 * head); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        ctx.move_to(175, -48); ctx.line_to(620, -120); ctx.line_to(620, 40); ctx.close_path(); ctx.set_source(g); ctx.fill()
    # body
    ctx.move_to(-190, -10); ctx.line_to(-190, -70); ctx.line_to(-120, -78)
    ctx.line_to(-80, -140); ctx.line_to(60, -140); ctx.line_to(110, -82); ctx.line_to(180, -70)
    ctx.line_to(185, -10); ctx.close_path(); ctx.set_source_rgb(*col); ctx.fill()
    # windows
    ctx.move_to(-110, -82); ctx.line_to(-74, -128); ctx.line_to(-10, -128); ctx.line_to(-10, -82); ctx.close_path()
    ctx.move_to(4, -82); ctx.line_to(4, -128); ctx.line_to(54, -128); ctx.line_to(92, -82); ctx.close_path()
    ctx.set_source_rgb(0.12, 0.14, 0.2); ctx.fill()
    # bonnet lid, hinged at the windscreen base, opens upward
    if bonnet > 0:
        ctx.save(); ctx.translate(110, -82); ctx.rotate(-1.0 * bonnet)
        ctx.move_to(0, 6); ctx.line_to(74, 16); ctx.line_to(74, -4); ctx.line_to(0, -14); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.fill(); ctx.restore()
        ctx.rectangle(115, -80, 62, 12); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
    # lights
    ctx.arc(176, -52, 10, 0, 6.3); ctx.set_source_rgb(*((1, 0.95, 0.7) if head > 0 else (0.35, 0.35, 0.38))); ctx.fill()
    on = hazard and blink(t)
    for hx in (-186, 172):
        rrect(ctx, hx, -40, 14, 16, 4); ctx.set_source_rgb(*(ORG if on else (0.4, 0.25, 0.12))); ctx.fill()
        if on:
            ctx.arc(hx + 7, -32, 36, 0, 6.3); ctx.set_source_rgba(*ORG, 0.25); ctx.fill()
    # wheels
    for wx in (-110, 110):
        ctx.arc(wx, -6, 40, 0, 6.3); ctx.set_source_rgb(0.05, 0.05, 0.06); ctx.fill()
        ctx.arc(wx, -6, 18, 0, 6.3); ctx.set_source_rgb(0.5, 0.52, 0.58); ctx.fill()
    ctx.restore()


def car_top(ctx, x, y, s, col=CARC, hazard=False, t=0.0, door=0.0):
    """top view, nose pointing up; door = left front door open amount"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -48, -95, 96, 190, 26); ctx.set_source_rgb(*col); ctx.fill()
    rrect(ctx, -38, -55, 76, 40, 10); ctx.set_source_rgb(0.12, 0.14, 0.2); ctx.fill()
    rrect(ctx, -38, 40, 76, 30, 10); ctx.fill()
    if door > 0:
        ctx.save(); ctx.translate(-48, -15); ctx.rotate(-1.1 * door)
        ctx.rectangle(-8, 0, 8, 60); ctx.set_source_rgb(*col); ctx.fill(); ctx.restore()
    on = hazard and blink(t)
    for hx, hy in ((-40, -92), (30, -92), (-40, 84), (30, 84)):
        rrect(ctx, hx, hy, 12, 10, 3); ctx.set_source_rgb(*(ORG if on else (0.4, 0.25, 0.12))); ctx.fill()
        if on:
            ctx.arc(hx + 6, hy + 5, 26, 0, 6.3); ctx.set_source_rgba(*ORG, 0.3); ctx.fill()
    ctx.restore()


def road_top(ctx, x0, x1, y0, y1, t, shoulder=110):
    """top view: grass, left shoulder, two-lane carriageway (left-hand traffic), moving dashes"""
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0); ctx.set_source_rgb(*GRASS); ctx.fill()
    rx = x0 + 150
    ctx.rectangle(rx, y0, shoulder, y1 - y0); ctx.set_source_rgb(*SHOUL); ctx.fill()
    ctx.rectangle(rx + shoulder, y0, x1 - rx - shoulder - 40, y1 - y0); ctx.set_source_rgb(*ASPH); ctx.fill()
    ctx.rectangle(rx + shoulder - 3, y0, 6, y1 - y0); ctx.set_source_rgb(0.9, 0.9, 0.9); ctx.fill()
    mid = rx + shoulder + (x1 - rx - shoulder - 40) / 2
    off = (t * 160) % 80
    for k in range(int((y1 - y0) / 80) + 2):
        yy = y0 + k * 80 - off
        if y0 <= yy <= y1 - 40:
            ctx.rectangle(mid - 4, yy, 8, 40); ctx.set_source_rgb(0.85, 0.75, 0.3); ctx.fill()
    return rx, rx + shoulder, mid


def phone(ctx, x, y, s, t, bars=0, tt=1.0, txt=None):
    """phone mockup with signal bars"""
    if tt < 0: return
    sc = s * pop(tt, 0.2)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    w, h = 220, 400
    rrect(ctx, -w / 2, -h / 2, w, h, 34); ctx.set_source_rgb(0.12, 0.12, 0.16); ctx.fill_preserve()
    ctx.set_source_rgb(*(RED if bars == 0 else GRN)); ctx.set_line_width(5); ctx.stroke()
    rrect(ctx, -w / 2 + 12, -h / 2 + 14, w - 24, h - 28, 24); ctx.set_source_rgb(0.08, 0.09, 0.16); ctx.fill()
    for k in range(4):
        bh = 16 + k * 14
        ctx.rectangle(-58 + k * 30, -40 - bh, 20, bh)
        ctx.set_source_rgb(*(GRN if k < bars else (0.3, 0.31, 0.38))); ctx.fill()
    if bars == 0 and txt is None:
        xmark(ctx, 70, -64, 40, RED)
    if txt is None:
        say(ctx, "No service" if bars == 0 else "Connected", 0, 40, 30, RED if bars == 0 else GRN)
    else:
        say(ctx, txt, 0, 50, 64, GRN)
        say(ctx, "calling...", 0, 120, 30, GREY)
    ctx.restore()


def tower(ctx, x, y, s, col, label, t, live=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgb(*col); ctx.set_line_width(8); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(-50, 120); ctx.line_to(0, -90); ctx.line_to(50, 120); ctx.stroke()
    for yy in (0, 60):
        w = 22 + yy * 0.24
        ctx.move_to(-w, yy); ctx.line_to(w, yy + 40); ctx.stroke()
        ctx.move_to(w, yy); ctx.line_to(-w, yy + 40); ctx.stroke()
    ctx.arc(0, -100, 14, 0, 6.3); ctx.fill()
    if live:
        for k in range(3):
            ph = (t * 1.2 + k / 3) % 1
            for d in (0, math.pi):
                ctx.arc(0, -100, 30 + ph * 70, d - 0.6, d + 0.6)
                ctx.set_source_rgba(*col, 1 - ph); ctx.set_line_width(6); ctx.stroke(); ctx.new_path()
    ctx.restore()
    say(ctx, label, x, y + 150 * s + 10, 30, col)


def triangle(ctx, x, y, s, col=RED, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(0, -50); ctx.line_to(50, 38); ctx.line_to(-50, 38); ctx.close_path()
    ctx.set_source_rgba(*col, a); ctx.set_line_width(14); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    ctx.move_to(-30, 46); ctx.line_to(30, 46); ctx.set_line_width(6); ctx.stroke()
    ctx.restore()


def tri_icon(ctx, x, y, s, col):
    triangle(ctx, x, y, s * 0.9, col)


def hazard_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    for r, lw in ((46, 8), (24, 7)):
        ctx.move_to(0, -r); ctx.line_to(r * 0.87, r * 0.5); ctx.line_to(-r * 0.87, r * 0.5); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.set_line_width(lw); ctx.stroke()
    ctx.restore()


def exit_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(40, -40); ctx.line_to(40, 40); ctx.stroke()
    ctx.move_to(20, 0); ctx.line_to(-40, 0); ctx.stroke()
    ctx.move_to(-20, -20); ctx.line_to(-42, 0); ctx.line_to(-20, 20); ctx.stroke()
    ctx.restore()


def tower_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(9)
    ctx.move_to(-28, 46); ctx.line_to(0, -30); ctx.line_to(28, 46); ctx.stroke()
    ctx.arc(0, -38, 9, 0, 6.3); ctx.fill()
    ctx.restore()


def walker(ctx, x, y, s, col, t, a=1.0):
    """walking stick figure facing right, feet at y"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.set_source_rgba(*col, a); ctx.set_line_width(18); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    sw = 0.5 * math.sin(t * 7)
    ctx.arc(0, -170, 22, 0, 6.3); ctx.fill()
    ctx.move_to(0, -145); ctx.line_to(0, -70); ctx.stroke()
    for d in (1, -1):
        ctx.move_to(0, -70); ctx.line_to(40 * math.sin(d * sw), 0); ctx.stroke()
        ctx.move_to(0, -130); ctx.line_to(36 * math.sin(-d * sw), -80); ctx.stroke()
    ctx.restore()


def dot_person(ctx, x, y, s, col):
    """top-view person: head and shoulders"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    rrect(ctx, -34, -14, 68, 28, 14); ctx.set_source_rgb(*col); ctx.fill()
    ctx.arc(0, 0, 18, 0, 6.3); ctx.set_source_rgb(*col); ctx.fill()
    ctx.arc(0, 0, 18, 0, 6.3); ctx.set_source_rgba(0, 0, 0, 0.35); ctx.set_line_width(4); ctx.stroke()
    ctx.restore()


def stars(ctx, n=40):
    for k in range(n):
        ctx.arc(90 + 900 * hrand("st", k), 570 + 260 * hrand("sy", k), 1.5 + 2 * hrand("sr", k), 0, 6.3)
        ctx.set_source_rgba(1, 1, 1, 0.25 + 0.5 * hrand("sa", k)); ctx.fill()


def night_road(ctx, y=1000):
    """side view: dark horizon, road strip"""
    ctx.rectangle(60, y + 20, 960, 30); ctx.set_source_rgb(*ASPH); ctx.fill()
    for k in range(7):
        ctx.rectangle(90 + k * 140, y + 32, 70, 6); ctx.set_source_rgb(0.5, 0.45, 0.25); ctx.fill()
    ctx.rectangle(60, y + 50, 960, 60); ctx.set_source_rgb(*GRASS); ctx.fill()


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tli = wt(0, "lights"); ttw = wt(0, "Twenty"); the = wt(0, "help")
    if tl < tli - 0.1:
        bg(ctx, tg, RED, 0.2)
        headline(ctx, "your car just died on a highway", [("No", WHT), ("network", RED)], 1.0)
        phone(ctx, 540, 800, 1.3, tl, 0, 1.0)
        stamp(ctx, "0 BARS", 540, 1150, tl - 0.25, RED, 70, -0.06)
    elif tl < ttw - 0.1:
        tt = tl - tli + 0.1
        bg(ctx, tg, PUR, 0.1, gy=700)
        headline(ctx, "middle of nowhere", [("No", WHT), ("lights", PUR)], tt)
        card(ctx, 540, 850, 960, 700, (0.25, 0.27, 0.35), 1.0, fill=DARK, glow=0)
        stars(ctx)
        night_road(ctx, 1000)
        head = max(0.0, 1 - tt / 0.35) * (1 if (tt * 20) % 1 > 0.4 else 0.2)
        car_side(ctx, 470, 1016, 1.15, CARC, head=head)
        if tt > 0.4:
            stamp(ctx, "DEAD", 760, 640, tt - 0.4, PUR, 64, 0.1)
    else:
        tt = tl - ttw + 0.1
        bg(ctx, tg, ORG, 0.14)
        headline(ctx, "nearest help", [("20 km", ORG), ("away", WHT)], tt)
        card(ctx, 540, 840, 900, 520, ORG, tt, glow=0.6)
        if tt > 0:
            car_side(ctx, 230, 860, 0.5, CARC, hazard=True, t=tl)
            # town icon
            for k, (hx, hh) in enumerate(((800, 90), (850, 130), (900, 70))):
                ctx.rectangle(hx, 880 - hh, 44, hh); ctx.set_source_rgb(*GREY); ctx.fill()
            p = ease_out(clamp((tl - ttw) / 1.2))
            ctx.set_dash([20, 16]); ctx.move_to(340, 900); ctx.line_to(340 + 440 * p, 900)
            ctx.set_source_rgb(*ORG); ctx.set_line_width(8); ctx.stroke(); ctx.set_dash([])
            say(ctx, "20 KM", 560, 990, 90, ORG)
            say(ctx, "YOU", 230, 720, 34, WHT); say(ctx, "HELP", 850, 720, 34, GREY)
        if tl > the - 0.1:
            pill(ctx, "pitch dark", 540, 1180, tl - the + 0.1, PUR, 40)


def s1(ctx, tg, tl, T):
    thw = wt(1, "highway"); tdo = wt(1, "Don"); tfo = wt(1, "Four"); tla = wt(1, "last"); tma = wt(1, "magic")
    if tl < tdo - 0.05:
        bg(ctx, tg, YEL, 0.12)
        headline(ctx, "your first instinct", [("Walk for", WHT), ("help?", YEL)], tl)
        card(ctx, 540, 850, 960, 640, YEL, tl, fill=DARK, glow=0.4)
        stars(ctx)
        night_road(ctx, 960)
        car_side(ctx, 230, 976, 0.6, CARC, hazard=True, t=tl)
        wx = 430 + 140 * tl
        walker(ctx, wx, 1000, 150, WHT, tl)
        ctx.set_dash([16, 14]); ctx.move_to(wx + 50, 1060); ctx.line_to(980, 1060)
        ctx.set_source_rgba(*YEL, 0.7); ctx.set_line_width(5); ctx.stroke(); ctx.set_dash([])
        if tl > thw - 0.1:
            # oncoming headlights on the same road
            gx = 1000 - 200 * clamp((tl - thw) / 1.0)
            g = cairo.RadialGradient(gx, 960, 0, gx, 960, 260)
            g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.7); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
            ctx.set_source(g); ctx.arc(gx, 960, 260, 0, 6.3); ctx.fill()
    elif tl < tfo - 0.1:
        tt = tl - tdo + 0.05
        bg(ctx, tg, RED, 0.18)
        headline(ctx, "walking the highway", [("Don't", RED)], tt)
        card(ctx, 540, 820, 600, 520, RED, 1.0, glow=0.6)
        walker(ctx, 540, 960, 150, WHT, 0)
        ctx.arc(540, 820, 210, 0, 6.3); ctx.set_source_rgb(*RED); ctx.set_line_width(22); ctx.stroke()
        ctx.move_to(392, 672); ctx.line_to(688, 968); ctx.stroke()
        pill(ctx, "stay with the car", 540, 1180, tt - 0.2, GRN, 42, icon=tick)
    else:
        tt = tl - tfo + 0.1
        bg(ctx, tg, GRN, 0.12)
        headline(ctx, "instead", [("4 moves", GRN), ("that keep you safe", WHT)], tt, size=64)
        items = [("Hazards on", hazard_icon), ("Get out left", exit_icon), ("Triangle back", tri_icon), ("???", tower_icon)]
        on4 = tl > tla - 0.1
        for k, (lab, ic) in enumerate(items):
            numcard(ctx, 540, 545 + k * 178, 640, 158, k + 1, lab, tt - 0.2 - k * 0.22,
                    on=(k == 3 and on4), col=PUR if k == 3 else GRN, icon=ic)
        if tl > tma - 0.1:
            stamp(ctx, "FEELS LIKE MAGIC", 700, 1100, tl - tma + 0.1, PUR, 40, 0.07)


def s2(ctx, tg, tl, T):
    tha = wt(2, "hazard"); tro = wt(2, "Fully"); tof = wt(2, "off")
    bg(ctx, tg, ORG, 0.15)
    if tl < tro - 0.1:
        headline(ctx, "one", [("Hazard lights", ORG), ("on", WHT)], tl)
        card(ctx, 540, 840, 960, 620, ORG, tl, fill=DARK, glow=0.6)
        on = tl > tha - 0.05
        stars(ctx, 25)
        night_road(ctx, 960)
        car_side(ctx, 540, 976, 1.2, CARC, hazard=on, t=tl - tha)
        # dashboard button
        cx, cy = 540, 640
        ctx.arc(cx, cy, 70, 0, 6.3); ctx.set_source_rgb(*(RED if on else (0.25, 0.25, 0.3))); ctx.fill()
        hazard_icon(ctx, cx, cy + 6, 90, WHT if on else GREY)
        if on:
            ph = clamp((tl - tha) / 0.35)
            ctx.arc(cx, cy, 70 + 50 * ph, 0, 6.3); ctx.set_source_rgba(*RED, 1 - ph); ctx.set_line_width(6); ctx.stroke()
            pill(ctx, "blink blink", 540, 1180, tl - tha - 0.3, ORG, 40)
    else:
        tt = tl - tro + 0.1
        headline(ctx, "roll it", [("Fully", WHT), ("off the road", ORG)], tt)
        card(ctx, 540, 840, 760, 700, ORG, tt, glow=0.5)
        ctx.save(); rrect(ctx, 170, 500, 740, 680, 26); ctx.clip()
        lx0, lx1, mid = road_top(ctx, 160, 920, 490, 1190, 0)
        p = ease_io(clamp((tl - tro) / 1.3))
        cx = (lx1 + 70) + (lx0 + 55 - lx1 - 70) * p
        car_top(ctx, cx, 900 - 140 * p, 1.1, CARC, hazard=True, t=tl)
        ctx.restore()
        say(ctx, "SHOULDER", lx0 + 55, 540, 22, GREY)
        if p > 0.95:
            pill(ctx, "off the road", 540, 1210, tl - tro - 1.3, GRN, 40, icon=tick)


def s3(ctx, tg, tl, T):
    tle = wt(3, "left"); tne = wt(3, "Never"); tbe = wt(3, "behind")
    if tl < tne - 0.1:
        bg(ctx, tg, GRN, 0.14)
        headline(ctx, "two", [("Get out on the", WHT), ("left", GRN)], tl)
    else:
        bg(ctx, tg, RED, 0.16)
        headline(ctx, "the danger zone", [("Never stand", WHT), ("behind it", RED)], tl - tne + 0.1)
    card(ctx, 540, 840, 760, 700, GRN if tl < tne - 0.1 else RED, 1.0, glow=0.5)
    ctx.save(); rrect(ctx, 170, 500, 740, 680, 26); ctx.clip()
    lx0, lx1, mid = road_top(ctx, 160, 920, 490, 1190, 0)
    cx, cy = lx0 + 60, 760
    # traffic coming up the left lane from behind
    for k in range(2):
        ty = 1300 - ((tl * 420 + k * 700) % 1400)
        car_top(ctx, (lx1 + mid) / 2 + 30, ty, 0.9, (0.4, 0.45, 0.6))
        g = cairo.RadialGradient((lx1 + mid) / 2 + 30, ty - 120, 0, (lx1 + mid) / 2 + 30, ty - 120, 140)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.35); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        ctx.set_source(g); ctx.paint()
    dp = ease_out(clamp((tl - tle + 0.3) / 0.4))
    car_top(ctx, cx, cy, 1.1, CARC, hazard=True, t=tl, door=dp)
    if tl < tne - 0.1:
        wp = ease_io(clamp((tl - tle) / 1.0))
        px = cx - 75 - 70 * wp; py = cy - 10 + 200 * wp
        dot_person(ctx, px, py, 140, GRN)
        if wp > 0.9:
            ctx.restore()
            pill(ctx, "away from traffic", 540, 1210, tl - tle - 1.0, GRN, 40, icon=tick)
            ctx.save()
    else:
        # danger zone between the car and oncoming traffic
        za = clamp((tl - tne) / 0.25)
        ctx.rectangle(lx0, cy + 115, lx1 - lx0 + 60, 260); ctx.set_source_rgba(*RED, 0.3 * za); ctx.fill()
        dot_person(ctx, cx, cy + 190, 140, YEL)
        ctx.arc(cx, cy + 190, 60, 0, 6.3); ctx.set_source_rgba(*RED, za); ctx.set_line_width(8); ctx.stroke()
        ctx.move_to(cx - 42, cy + 148); ctx.line_to(cx + 42, cy + 232); ctx.stroke()
    ctx.restore()
    if tl > tbe - 0.1:
        stamp(ctx, "DANGER ZONE", 640, 1200, tl - tbe + 0.1, RED, 50, -0.05)


def s4(ctx, tg, tl, T):
    ttr = wt(4, "triangle"); tfi = wt(4, "fifty"); tbo = wt(4, "Bonnet"); tla = wt(4, "language"); tbh = wt(4, "bhai")
    if tl < tbo - 0.1:
        bg(ctx, tg, RED, 0.14)
        headline(ctx, "three", [("Triangle", RED), ("50 m back", WHT)], tl)
        card(ctx, 540, 840, 960, 640, RED, tl, fill=DARK, glow=0.5)
        stars(ctx, 30)
        night_road(ctx, 990)
        # true scale: 50 m = 760 px (15.2 px per metre), so a 4 m car is about 60 px long
        car_side(ctx, 920, 1010, 0.16, CARC, hazard=True, t=tl)
        if blink(tl):
            ctx.arc(920, 1000, 40, 0, 6.3); ctx.set_source_rgba(*ORG, 0.25); ctx.fill()
        tp = ease_out(clamp((tl - ttr + 0.1) / 0.4))
        triangle(ctx, 160, 1000 - 30 * (1 - tp), 60, RED, tp)
        if tl > tfi - 0.2:
            p = ease_out(clamp((tl - tfi + 0.2) / 0.6))
            ctx.move_to(160, 900); ctx.line_to(160 + 730 * p, 900)
            ctx.set_source_rgb(*WHT); ctx.set_line_width(6); ctx.stroke()
            for xx in (160, 160 + 730 * p):
                ctx.move_to(xx, 880); ctx.line_to(xx, 920); ctx.stroke()
            say(ctx, "50 m", 520, 800, 110, RED)
            say(ctx, "your car", 920, 950, 26, GREY)
            pill(ctx, "Indian driving rules", 540, 620, tl - tfi - 0.5, GREY, 32)
    else:
        tt = tl - tbo + 0.1
        bg(ctx, tg, YEL, 0.14)
        headline(ctx, "and", [("Bonnet", YEL), ("up", WHT)], tt)
        card(ctx, 540, 840, 960, 640, YEL, 1.0, fill=DARK, glow=0.5)
        stars(ctx, 30)
        night_road(ctx, 990)
        b = ease_out(clamp((tl - tbo) / 0.5))
        car_side(ctx, 540, 1006, 1.3, CARC, hazard=True, t=tl, bonnet=b)
        if tl > tla - 0.2:
            # speech bubble from the car
            sc = pop(tl - tla + 0.2, 0.25)
            ctx.save(); ctx.translate(700, 640); ctx.scale(sc, sc)
            rrect(ctx, -200, -60, 400, 120, 40); ctx.set_source_rgb(*YEL); ctx.fill()
            ctx.move_to(-60, 58); ctx.line_to(-110, 130); ctx.line_to(-10, 58); ctx.fill()
            say(ctx, "HELP, BHAI!" if tl > tbh - 0.2 else "car language:", 0, 0, 52 if tl > tbh - 0.2 else 40, BLACK)
            ctx.restore()


def s5(ctx, tg, tl, T):
    tze = wt(5, "zero"); tdi = wt(5, "Dial"); tan = wt(5, "anyway"); tbo = wt(5, "borrow"); tto = wt(5, "tower")
    if tl < tbo - 0.3:
        bg(ctx, tg, PUR, 0.16)
        headline(ctx, "four: zero bars?", [("Dial", WHT), ("112", PUR), ("anyway", WHT)], tl)
        dialing = tl > tdi + 0.3
        phone(ctx, 540, 830, 1.35, tl, 0, 1.0, txt="112" if dialing else None)
        if tl > tan - 0.1:
            stamp(ctx, "TRY IT", 800, 600, tl - tan + 0.1, PUR, 54, 0.1)
    else:
        tt = tl - tbo + 0.3
        bg(ctx, tg, GRN, 0.14)
        headline(ctx, "emergency calls can", [("Borrow", WHT), ("another tower", GRN)], tt)
        card(ctx, 540, 850, 960, 680, GRN, tt, glow=0.5)
        tower(ctx, 230, 760, 1.2, (0.4, 0.42, 0.5), "YOUR SIM", tl, live=False)
        xmark(ctx, 230, 760, 150, RED)
        a = clamp((tl - tto + 0.4) / 0.3)
        tower(ctx, 850, 760, 1.2, GRN if a > 0 else (0.4, 0.42, 0.5), "OTHER NETWORK", tl, live=a > 0)
        phone(ctx, 540, 930, 0.85, tl, 1 if a > 0 else 0, 1.0, txt="112")
        if a > 0:
            ctx.set_dash([14, 12]); ctx.move_to(800, 660); ctx.line_to(620, 790)
            ctx.set_source_rgba(*GRN, a); ctx.set_line_width(6); ctx.stroke(); ctx.set_dash([])
        pill(ctx, "if any network is in range", 540, 1220, tl - tto - 0.2, YEL, 34)


def s6(ctx, tg, tl, T):
    tc = wt(6, "Comment"); ty = wt(6, "yes"); tn = wt(6, "no", 1)
    bg(ctx, tg, PUR, 0.14)
    headline(ctx, "comment below", [("Knew the", WHT), ("112 trick?", PUR)], tl)
    card(ctx, 540, 640, 420, 260, PUR, tl, glow=0.6)
    if tl > 0:
        say(ctx, "112", 540, 640, 120, PUR)
    for k, (lab, col, t0) in enumerate((("YES", GRN, ty), ("NO", RED, tn))):
        x = 330 + k * 420
        card(ctx, x, 960, 340, 200, col, tl - t0 + 0.15, glow=0.9)
        if tl > t0 - 0.15:
            say(ctx, lab, x, 960, 100, col)
    if tl < ty - 0.15:
        pill(ctx, "tell us below", 540, 960, tl - tc + 0.1, YEL, 44)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def _engine_die(A, t, d=0.9, g=0.25):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    f = 60 * (1 - 0.6 * tt / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / 44100) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 12 * tt)))
    x *= np.minimum(1, (d - tt) / 0.4)
    A.add(A.sfx_buf, x, t, g)


def _tick(A, t, n, gap=0.31, g=0.12):
    for k in range(n):
        A.ding(t + k * gap, g, 2200 if k % 2 else 1800, 0.03)


def sfx(A):
    A.thump(0.02, 0.5, 55)
    A.ding(A.W(0, "network"), 0.06, 392)
    _engine_die(A, A.W(0, "lights") - 0.1)
    A.thump(A.W(0, "Twenty") - 0.05, 0.4, 60)
    A.whoosh(A.W(1, "highway") - 0.1, 0.2, 0.8)
    A.thump(A.W(1, "Don") - 0.03, 0.6, 60)
    for k in range(4):
        A.pop(A.W(1, "Four") + 0.1 + k * 0.22, 0.15)
    A.boing(A.W(1, "magic"), 0.12, 320)
    A.pop(A.W(2, "hazard"), 0.35)
    _tick(A, A.W(2, "hazard") + 0.1, 6)
    A.whoosh(A.W(2, "Fully") - 0.1, 0.15, 1.0)
    A.pop(A.W(3, "left"), 0.3)
    A.whoosh(A.W(3, "Never") - 0.1, 0.15, 0.6)
    A.thump(A.W(3, "behind"), 0.5, 60)
    A.pop(A.W(4, "triangle"), 0.3)
    A.whoosh(A.W(4, "fifty") - 0.2, 0.12, 0.6)
    A.whoosh(A.W(4, "Bonnet") - 0.05, 0.15, 0.4)
    A.boing(A.W(4, "bhai"), 0.12, 260, 0.6)
    A.pop(A.W(5, "Dial"), 0.3)
    for k in range(3):
        A.ding(A.W(5, "Dial") + 0.3 + k * 0.12, 0.05, A.note(76 + k * 2), 0.06)
    A.whoosh(A.W(5, "borrow") - 0.3, 0.15, 0.4)
    for k, m in enumerate((72, 76, 79)):
        A.ding(A.W(5, "tower") + k * 0.1, 0.06, A.note(m))
    A.pop(A.W(6, "yes"), 0.3); A.pop(A.W(6, "no", 1), 0.3)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(6, "Comment") + 0.1 + k * 0.1, 0.06, A.note(m))

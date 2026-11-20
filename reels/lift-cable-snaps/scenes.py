"""Scenes for "What if your lift cable snapped on the 40th floor?". One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT.
Lift car, shaft and rider are drawn in centimetres (Cam) so they stay in true scale:
car 160 cm wide and 230 cm tall inside, rider 170 cm, storeys 300 cm apart."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

BG = lambda ctx, tg, i: bg_glow(ctx, tg, i, dark_scenes=(0, 1))
MUSIC = {"beat_from_scene": 2, "bpm": 112}   # tense drone for the snap and the fall, beat from "One"
NO_FLASH = ()

STEEL = (0.72, 0.76, 0.84)
CARW = (0.2, 0.22, 0.42)
WALL = (0.09, 0.08, 0.2)
MUMMY = (0.95, 0.4, 0.6)
HEROC = SHIRTS[1]


def wi(i, k):
    """scene-local start time of the k-th word of line i"""
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


def cut_times(i):
    """extra hard cuts inside long lines (scene-local seconds)"""
    try:
        return {1: [0, wt(1, "Three") - 0.1],
                2: [0, wt(2, "More") - 0.1],
                3: [0, wt(3, "Like") - 0.1],
                4: [0, wt(4, "Myth") - 0.05],
                5: [0, wt(5, "Press") - 0.1]}.get(i, [0])
    except KeyError:
        return [0]


# ---------------------------------------------------------------- shaft and car (world cm)
def shaft(ctx, ytop, ybot, scroll=0.0, first_floor=40, x0=-140, x1=140):
    """shaft walls with a floor slab every 300 cm; floor n is at y = -(n - first_floor) * 300 + scroll"""
    ctx.rectangle(x0 - 400, ytop, x1 - x0 + 800, ybot - ytop); ctx.set_source_rgb(*WALL); ctx.fill()
    ctx.rectangle(x0, ytop, x1 - x0, ybot - ytop); ctx.set_source_rgb(0.05, 0.05, 0.13); ctx.fill()
    n_lo = first_floor - int((ybot - scroll) / 300) - 1
    n_hi = first_floor + int((scroll - ytop) / 300) + 1
    for n in range(n_lo, n_hi + 1):
        y = -(n - first_floor) * 300 + scroll
        for sx in (-1, 1):
            xa = x0 if sx < 0 else x1
            ctx.rectangle(xa - (60 if sx < 0 else 0), y, 60, 26); ctx.set_source_rgb(0.3, 0.26, 0.5); ctx.fill()
        text(ctx, str(n), x0 - 120, y - 70, 52, (0.55, 0.5, 0.85), shadow=False)
    # guide rails
    for rx in (-100, 100):
        ctx.rectangle(rx - 4, ytop, 8, ybot - ytop); ctx.set_source_rgb(*STEEL); ctx.fill()


def ropes(ctx, top_y, car_top, n=6, snapped=None, t_snap=0.0, glow=None, lw=2.4):
    """hoist ropes from top_y down to the crosshead; snapped: index of the broken rope, t_snap: seconds since snap"""
    xs = [-25 + 50 * k / (n - 1) for k in range(n)]
    for k, x in enumerate(xs):
        ctx.set_line_width(lw)
        if snapped is not None and k == snapped and t_snap >= 0:
            # lower piece whips and hangs from the crosshead, upper piece recoils upward
            whip = math.sin(t_snap * 14) * 18 * math.exp(-t_snap * 2.5)
            ctx.move_to(x, car_top); ctx.curve_to(x + whip, car_top - 60, x - whip - 30, car_top - 100, x - 40 + whip, car_top - 50)
            ctx.set_source_rgb(*RED); ctx.stroke()
            up = 120 + 300 * ease_out(t_snap / 0.4)
            ctx.move_to(x, top_y); ctx.line_to(x + whip * 0.5, car_top - up); ctx.stroke()
            continue
        ctx.move_to(x, top_y); ctx.line_to(x, car_top)
        ctx.set_source_rgb(*(YEL if glow == k else STEEL)); ctx.stroke()
    return xs


def car(ctx, t, expr="smile", arms="down", rider=True, look=0.0, shake=0.0, brakes=0.0, panel=None):
    """lift car, floor at y=0, inside 160 x 230 cm, front wall cut away"""
    ctx.save(); ctx.translate(shake * math.sin(t * 70), 0)
    # sling / frame
    ctx.rectangle(-92, -262, 184, 22); ctx.set_source_rgb(0.38, 0.4, 0.55); ctx.fill()     # crosshead
    ctx.rectangle(-92, -262, 12, 280); ctx.rectangle(80, -262, 12, 280); ctx.fill()        # stiles
    ctx.rectangle(-92, 0, 184, 18); ctx.fill()
    # safety brake shoes on the stiles, next to the rails
    for sx in (-1, 1):
        bx = sx * (96 - 4 * brakes)
        rrect(ctx, bx - 7, -40, 14, 34, 3); ctx.set_source_rgb(*(ORG if brakes > 0.1 else (0.5, 0.52, 0.6))); ctx.fill()
    # cabin
    g = cairo.LinearGradient(0, -230, 0, 0)
    g.add_color_stop_rgb(0, 0.3, 0.32, 0.6); g.add_color_stop_rgb(1, 0.2, 0.18, 0.42)
    ctx.rectangle(-80, -240, 160, 240); ctx.set_source(g); ctx.fill()
    ctx.rectangle(-80, -240, 160, 10); ctx.set_source_rgb(0.95, 0.95, 1); ctx.fill()     # ceiling light
    ctx.rectangle(-70, -120, 140, 4); ctx.set_source_rgb(*STEEL); ctx.fill()             # handrail
    ctx.rectangle(-80, -6, 160, 6); ctx.set_source_rgb(0.4, 0.3, 0.55); ctx.fill()
    if panel:
        panel(ctx)
    if rider:
        person(ctx, -10, 0, 170, HEROC, expr, arms, t, look=look)
    ctx.set_source_rgb(0.6, 0.62, 0.75); ctx.set_line_width(4)
    ctx.rectangle(-80, -240, 160, 240); ctx.stroke()
    ctx.restore()


def button_panel(glow=0.0, t=0.0):
    def f(ctx):
        rrect(ctx, 52, -150, 22, 60, 3); ctx.set_source_rgb(0.75, 0.78, 0.88); ctx.fill()
        for k in range(4):
            ctx.arc(63, -142 + k * 12, 3.5, 0, 6.3); ctx.set_source_rgb(0.4, 0.45, 0.55); ctx.fill()
        a = glow * (0.6 + 0.4 * math.sin(t * 12))
        if a > 0:
            glow_circle(ctx, 63, -98, 20, YEL, a)
        ctx.arc(63, -98, 4.5, 0, 6.3); ctx.set_source_rgb(*(YEL if glow > 0 else RED)); ctx.fill()
    return f


def display(ctx, x, y, s, n, arrow_down=False, red=False):
    """floor indicator: big digits in a black box (screen px)"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -130, -70, 260, 140, 26); ctx.set_source_rgb(0.02, 0.02, 0.05); ctx.fill()
    ctx.set_source_rgb(*(RED if red else (0.4, 0.45, 0.6))); ctx.set_line_width(5); rrect(ctx, -130, -70, 260, 140, 26); ctx.stroke()
    text(ctx, str(n), 25, 0, 100, RED if red else YEL, shadow=False)
    if arrow_down:
        ctx.move_to(-95, -25); ctx.line_to(-55, -25); ctx.line_to(-75, 25); ctx.close_path()
        ctx.set_source_rgb(*RED); ctx.fill()
    ctx.restore()


def tiles(ctx, cur, tt, y=408):
    """step row 1 2 3; cur = active index (0-based)"""
    labels = ["1", "2", "3"]
    cols = [CYN, ORG, PNK]
    for k in range(3):
        x = 540 + (k - 1) * 100
        on = k == cur
        s = (0.62 + 0.15 * (1 - ease_out(tt / 0.3))) if on else 0.5
        ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
        rrect(ctx, -52, -52, 104, 104, 22)
        ctx.set_source_rgb(*(cols[k] if k <= cur else (0.25, 0.25, 0.4))); ctx.fill()
        text(ctx, labels[k], 0, 0, 74, (0, 0, 0) if k <= cur else (0.6, 0.6, 0.75), shadow=False)
        ctx.restore()


def speed_lines(ctx, t, a=1.0, x0=0, x1=W):
    for k in range(18):
        x = x0 + hrand("sl", k) * (x1 - x0)
        y = ((hrand("sy", k) * H - t * 2600) % (H + 400)) - 200
        ctx.move_to(x, y); ctx.line_to(x, y + 180 + 160 * hrand("sh", k))
        ctx.set_source_rgba(1, 1, 1, 0.25 * a); ctx.set_line_width(4); ctx.stroke()


def sparks(ctx, x, y, t, n=16, seed="sk", dirx=1):
    for k in range(n):
        ph = (t * (1.8 + hrand(seed, k)) + hrand(seed + "o", k)) % 1
        vx = dirx * (60 + 200 * hrand(seed + "x", k)); vy = -120 + 260 * hrand(seed + "y", k)
        px = x + vx * ph; py = y + vy * ph + 300 * ph * ph
        ctx.move_to(px, py); ctx.line_to(px - vx * 0.05, py - vy * 0.05)
        ctx.set_source_rgba(1, 0.85 - 0.4 * ph, 0.2, 1 - ph); ctx.set_line_width(4); ctx.stroke()


def mummy(ctx, x, y, h, t, expr="smile", look=0.0):
    person(ctx, x, y, h, MUMMY, expr, "down", t, look=look)
    u = h / 100
    ctx.arc(x, y - 104 * u, 8 * u, 0, 6.3); ctx.set_source_rgb(0.15, 0.1, 0.08); ctx.fill()        # bun
    ctx.arc(x + look * 3 * u, y - 88.5 * u, 1.6 * u, 0, 6.3); ctx.set_source_rgb(0.9, 0.1, 0.2); ctx.fill()  # bindi
    ctx.move_to(x - 19 * u, y - 70 * u); ctx.line_to(x + 19 * u, y - 50 * u); ctx.set_line_width(6 * u)
    ctx.set_source_rgba(*YEL, 0.9); ctx.stroke()                                                       # dupatta


def keyring(ctx, x, y, s, n, t):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(0.15 * math.sin(t * 5))
    ctx.arc(0, 0, 40, 0, 6.3); ctx.set_source_rgb(*STEEL); ctx.set_line_width(8); ctx.stroke()
    for k in range(n):
        a = math.pi * 0.15 + k * (math.pi * 0.7 / max(1, n - 1)) + 0.04 * math.sin(t * 7 + k)
        ctx.save(); ctx.rotate(a); ctx.translate(40, 0)
        col = [YEL, CYN, PNK, GRN, ORG][k % 5]
        ctx.arc(14, 0, 14, 0, 6.3); ctx.set_source_rgb(*col); ctx.fill()
        ctx.rectangle(24, -5, 70, 10); ctx.fill()
        ctx.rectangle(70, 5, 8, 12); ctx.rectangle(84, 5, 8, 8); ctx.fill()
        ctx.restore()
    ctx.restore()


def auto(ctx, x, y, s, t, brake=0.0):
    """auto-rickshaw side view facing left, wheels on y (screen px)"""
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(-0.06 * brake)
    # canopy
    ctx.move_to(-150, -150); ctx.curve_to(-140, -260, 140, -270, 170, -240); ctx.line_to(170, -60); ctx.line_to(-150, -60); ctx.close_path()
    ctx.set_source_rgb(*YEL); ctx.fill()
    ctx.rectangle(-120, -220, 120, 140); ctx.set_source_rgb(0.12, 0.1, 0.22); ctx.fill()
    # driver
    person(ctx, -60, -60, 150, (0.85, 0.85, 0.9), "shock" if brake > 0 else "smile", "down", t, look=-1)
    # body
    ctx.move_to(-190, -40); ctx.line_to(-170, -110); ctx.line_to(-120, -110); ctx.line_to(-110, -40); ctx.line_to(170, -40)
    ctx.line_to(170, 10); ctx.line_to(-190, 10); ctx.close_path(); ctx.set_source_rgb(0.15, 0.65, 0.35); ctx.fill()
    ctx.rectangle(-190, -40, 360, 10); ctx.set_source_rgb(*YEL); ctx.fill()
    for wx in (-160, 120):
        ctx.arc(wx, 15, 34, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.12); ctx.fill()
        ctx.arc(wx, 15, 14, 0, 6.3); ctx.set_source_rgb(*STEEL); ctx.fill()
    ctx.arc(-188, -60, 10, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.6); ctx.fill()
    ctx.restore()


def speed_bar(ctx, y, label, frac, col, tt, val):
    if tt < 0: return
    f = frac * ease_out(tt / 0.5)
    text(ctx, label, 120, y - 62, 46, WHT, align="l")
    rrect(ctx, 120, y - 30, 840, 60, 30); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()
    if f > 0.01:
        rrect(ctx, 120, y - 30, max(60, 840 * f), 60, 30); ctx.set_source_rgb(*col); ctx.fill()
    text(ctx, val, 950, y - 62, 46, col, align="r")


# ---------------------------------------------------------------- scenes
def s0(ctx, tg, tl, T):
    tsn = wt(0, "Snap"); tdr = wt(0, "drops")
    snapped = tl >= tsn
    ts = tl - tsn
    drop = 0.0
    if snapped:
        drop = 40 * ease_out(min(ts, 0.25) / 0.25) + (max(0, tl - tdr + 0.2) ** 2) * 300   # jolt, then the drop
    shake = 4 * math.exp(-max(0, ts) * 4) if snapped else 0
    sx = shake * math.sin(tl * 80) * 6
    with Cam(ctx, 0, -150 + drop * 0.15, 2.85, 540 + sx, 860):
        shaft(ctx, -2000, 1500, scroll=-drop)
        ctx.save(); ctx.translate(0, 0)
        ropes(ctx, -2000, -262, 6, snapped=1 if snapped else None, t_snap=ts)
        car(ctx, tl, "shock" if snapped else "worry", "up" if tl > tdr - 0.15 else "down", look=-0.3, shake=shake,
            panel=button_panel())
        ctx.restore()
    if tl > tdr:
        speed_lines(ctx, tl, clamp((tl - tdr) / 0.3))
    n = 40 - int(max(0, tl - tdr + 0.1) * 4)
    display(ctx, 540, 520, 1.0, n, arrow_down=snapped, red=snapped)
    if snapped and ts < 0.12:
        ctx.set_source_rgba(1, 0.2, 0.2, 0.45 * (1 - ts / 0.12)); ctx.paint()
    stamp(ctx, "SNAP!", 800, 680, ts, RED, 96, 0.12)


def s1(ctx, tg, tl, T):
    t170 = wt(1, "170"); tsec = wt(1, "seconds"); tth = wt(1, "Three"); tyou = wt(1, "you", 1)
    if tl < tth - 0.1:
        # falling: shaft scrolls up past the car, speed and clock count up
        f = clamp((tl - 0.05) / max(0.5, tsec + 0.3))
        scroll = -(1200 * tl + 600 * tl * tl)
        with Cam(ctx, 0, -140, 2.4, 540, 950, rot=0.03 * math.sin(tl * 9)):
            shaft(ctx, -1400, 1400, scroll=scroll % 3000 - 1500, first_floor=40 - int((1200 * tl + 600 * tl * tl) / 300))
            ropes(ctx, -1400, -262, 6, snapped=1, t_snap=3 + tl)
            car(ctx, tl, "shock", "up", look=0.0, shake=2.5)
        speed_lines(ctx, tl)
        # readouts
        rrect(ctx, 90, 450, 900, 190, 40); ctx.set_source_rgba(0, 0, 0, 0.6); ctx.fill()
        kmh = int(172 * ease_io(f))
        text(ctx, f"{kmh}", 330, 530, 120, RED if kmh > 100 else YEL)
        text(ctx, "KM/H", 330, 610, 34, WHT, SANS)
        secs = 4.9 * ease_io(f)
        text(ctx, f"{secs:.1f}s", 760, 530, 120, CYN)
        text(ctx, "IN FREE FALL", 760, 610, 34, WHT, SANS)
        if tl > tsec:
            popchip(ctx, "IF NOTHING STOPPED IT", 540, 1215, tl - tsec, YEL, (0, 0, 0), 50)
    else:
        tt = tl - tth + 0.1
        icons = ["CABLES", "BRAKES", "YOU"]
        cols = [CYN, ORG, PNK]
        for k in range(3):
            t0 = tth - 0.1 + k * 0.25
            if tl < t0: continue
            s = pop(tl - t0, 0.22) * (1 + 0.03 * math.sin(tl * 6 + k))
            x = 540 + (k - 1) * 320; y = 820
            on_you = k == 2 and tl > tyou - 0.1
            ctx.save(); ctx.translate(x, y); ctx.scale(s * (1.15 if on_you else 1), s * (1.15 if on_you else 1))
            if on_you:
                glow_circle(ctx, 0, 0, 260, PNK, 0.6)
            rrect(ctx, -140, -170, 280, 340, 40); ctx.set_source_rgb(*cols[k]); ctx.fill()
            text(ctx, str(k + 1), 0, -70, 150, (0.05, 0.05, 0.15), shadow=False)
            text(ctx, icons[k], 0, 90, 56 if k < 2 else 70, (0.05, 0.05, 0.15), shadow=False)
            ctx.restore()
        if tl > tyou - 0.1:
            person(ctx, 860, 1250, 300, HEROC, "worry", "down", tl, look=-1)
            popchip(ctx, "?!", 920, 900, tl - tyou + 0.1, WHT, (0, 0, 0), 60)
        popchip(ctx, "3 THINGS SAVE YOU", 540, 520, tt, YEL, (0, 0, 0), 64)


def s2(ctx, tg, tl, T):
    tc = wt(2, "cables"); te = wt(2, "Each"); tm = wt(2, "More"); ti = wt(2, "Indian")
    if tl < tm - 0.1:
        # close-up of the crosshead: 6 ropes, one snapped, five holding; true scale vs the rider below
        with Cam(ctx, 0, -215, 3.0, 540, 800):
            shaft(ctx, -600, 400, scroll=0, first_floor=36)
            glow = 3 if tl > te - 0.05 else None
            xs = ropes(ctx, -600, -262, 6, snapped=1, t_snap=5 + tl, glow=glow, lw=2.6)
            car(ctx, tl, "worry" if tl < te else "smile", "down", look=-0.2)
        if tl > tc - 0.1:
            popchip(ctx, "1 SNAPPED", 250, 540, tl - tc + 0.1, RED, WHT, 46)
            popchip(ctx, "5 STILL HOLDING", 820, 540, tl - tc + 0.25, GRN, (0, 0, 0), 46)
        if tl < te - 0.05:
            popchip(ctx, "4 TO 8 CABLES", 540, 1215, tl - tc + 0.05, CYN, (0, 0, 0), 64)
        else:
            popchip(ctx, "1 CABLE CAN HOLD IT ALL", 540, 1215, tl - te + 0.05, YEL, (0, 0, 0), 56)
    else:
        tt = tl - tm + 0.1
        mummy(ctx, 400, 1250, 700, tl, "smile", look=0.6)
        nk = 3 + int(clamp(tt / 1.2) * 9)
        keyring(ctx, 760, 820, 1.6 * pop(tt - 0.15, 0.25), nk, tl)
        popchip(ctx, f"SPARE KEY #{nk * 4 - 1}", 760, 1080, tt - 0.3, PNK, WHT, 50)
        if tl > ti - 0.05:
            stamp(ctx, "BACKUP QUEEN", 540, 560, tl - ti + 0.05, PNK, 86, -0.06)
    tiles(ctx, 0, tl)


def s3(ctx, tg, tl, T):
    tb = wt(3, "Brakes"); tr = wt(3, "rails"); tsc = wt(3, "Screech"); tli = wt(3, "Like")
    if tl < tli - 0.1:
        # car falls, governor at the top spins, brake shoes grab the rails, car stops
        stop_t = tr + 0.1
        if tl < tb:
            v = 1600; y = v * tl; br = 0.0
        else:
            y0 = 1600 * tb; d = min(tl, stop_t) - tb; dur = stop_t - tb
            y = y0 + 1600 * d - 0.5 * (1600 / dur) * d * d
            br = clamp((tl - tb) / 0.15)
        with Cam(ctx, 0, -130, 2.4, 540, 850):
            shaft(ctx, -1500, 1500, scroll=-(y % 600) if tl < stop_t else -(y % 600), first_floor=33)
            ropes(ctx, -1500, -262, 6, snapped=1, t_snap=8 + tl)
            car(ctx, tl, "shock" if tl < stop_t else "worry", "up" if tl < stop_t else "down", look=0.0,
                shake=2.0 if tb < tl < stop_t + 0.3 else 0, brakes=br)
            if tb < tl < stop_t + 0.6:
                sparks(ctx, -100, -20, tl, seed="l", dirx=-1); sparks(ctx, 100, -20, tl, seed="r", dirx=1)
        if tl < stop_t:
            speed_lines(ctx, tl, 1.0 if tl < tb else clamp((stop_t - tl) / (stop_t - tb)))
        # governor pulley (screen px) spins with the speed
        spin = tl * (14 if tl < tb else 14 * clamp((stop_t - tl) / max(0.1, stop_t - tb)))
        ctx.save(); ctx.translate(870, 620); ctx.rotate(spin)
        ctx.arc(0, 0, 70, 0, 6.3); ctx.set_source_rgb(0.3, 0.32, 0.5); ctx.fill()
        for k in range(4):
            ctx.save(); ctx.rotate(k * math.pi / 2); ctx.rectangle(-8, -66, 16, 50); ctx.set_source_rgb(*ORG); ctx.fill(); ctx.restore()
        ctx.arc(0, 0, 14, 0, 6.3); ctx.set_source_rgb(*STEEL); ctx.fill()
        ctx.restore()
        popchip(ctx, "SPEED GOVERNOR", 870, 730, tl - 0.4, ORG, (0, 0, 0), 38)
        if tl > tb - 0.05:
            popchip(ctx, "BRAKES GRAB THE RAILS", 540, 1215, tl - tb + 0.05, YEL, (0, 0, 0), 54)
        stamp(ctx, "SCREECH!", 330, 640, tl - tsc + 0.03, RED, 92, -0.1)
    else:
        tt = tl - tli + 0.1
        # road, auto skids to a halt beside a waving passenger
        ctx.rectangle(0, 1130, W, 140); ctx.set_source_rgb(0.15, 0.13, 0.25); ctx.fill()
        for k in range(6):
            ctx.rectangle(k * 220 - (tl * 200 % 220), 1195, 120, 12); ctx.set_source_rgb(*YEL); ctx.fill()
        stop = ease_out(tt / 0.5)
        ax = 1300 - 760 * stop
        brake = 1.0 if tt < 0.7 else 0.0
        if tt < 0.6:
            for k in range(4):
                ctx.move_to(ax + 220 + k * 30, 1000 + k * 40); ctx.line_to(ax + 420 + k * 30, 1000 + k * 40)
            ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(6); ctx.stroke()
        auto(ctx, ax, 1150, 1.35, tl, brake)
        person(ctx, 180, 1170, 430, SHIRTS[3], "smile", "wave", tl, look=1)
        popchip(ctx, "BHAIYA, STATION?", 260, 600, tt - 0.2, WHT, (0, 0, 0), 50)
        stamp(ctx, "SCREECH!", 680, 560, tt, RED, 80, 0.08)
    tiles(ctx, 1, tl)


def s4(ctx, tg, tl, T):
    tj = wt(4, "Jump"); tmy = wt(4, "Myth"); tca = wt(4, "cancels")
    if tl < tmy - 0.05:
        # rider crouches, then jumps inside the falling car (true scale: 170 cm rider, 230 cm car)
        jump = 0.0
        if tl > tj:
            p = clamp((tl - tj) / 0.9)
            jump = 55 * math.sin(math.pi * p)
        with Cam(ctx, 0, -110, 3.4, 540, 880):
            shaft(ctx, -900, 900, scroll=-(tl * 1500 % 600), first_floor=12)
            ropes(ctx, -900, -262, 6, snapped=1, t_snap=9 + tl)
            ctx.save()
            car(ctx, tl, "shock", "down", rider=False)
            person(ctx, -10, -jump, 170 - (14 if tl < tj else 0), HEROC, "worry" if tl < tj else "shock", "up" if tl > tj else "down", tl)
            ctx.restore()
        speed_lines(ctx, tl, 0.8)
        if tl > tj:
            popchip(ctx, "JUMP!", 820, 640, tl - tj, YEL, (0, 0, 0), 70)
    else:
        tt = tl - tmy + 0.05
        stamp(ctx, "MYTH!", 540, 600, tt, RED, 130, -0.08)
        speed_bar(ctx, 840, "LIFT FALLING", 1.0, RED, tt - 0.25, "~170 KM/H")
        speed_bar(ctx, 1040, "YOUR BEST JUMP", 0.05, GRN, tl - tca, "A FEW KM/H")
        if tl > tca + 0.6:
            person(ctx, 880, 1250, 150, HEROC, "worry", "down", tl, look=-1)
    tiles(ctx, 2, tl)


def s5(ctx, tg, tl, T):
    tb = wt(5, "Bollywood"); tp = wt(5, "Press"); tst = wt(5, "stay"); twa = wt(5, "wait")
    if tl < tp - 0.1:
        # Bollywood hero mid-air on very visible wires
        hy = 1180 - 60 * math.sin(tl * 3)
        for x in (450, 630):
            ctx.move_to(x, 380); ctx.line_to(x + (540 - x) * 0.2, hy - 720)
            ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(4); ctx.stroke()
        glow_circle(ctx, 540, hy - 380, 420, YEL, 0.35)
        sparkles(ctx, 540, hy - 380, 380, tl, 18, YEL)
        ctx.save(); ctx.translate(540, hy); ctx.rotate(0.12 * math.sin(tl * 2))
        person(ctx, 0, 0, 760, (0.1, 0.1, 0.12), "smile", "up", tl * 0.2)
        ctx.restore()
        for k in range(3):    # wind in the hair, slow-mo ripple
            ctx.move_to(200, 700 + k * 120); ctx.curve_to(260, 680 + k * 120, 320, 720 + k * 120, 380, 700 + k * 120)
            ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(5); ctx.stroke()
        popchip(ctx, "HERO LEGS: NOT INCLUDED", 540, 1190, tl - tb, PNK, WHT, 50)
    else:
        tt = tl - tp + 0.1
        # stopped car, rider presses the alarm; three-step checklist
        with Cam(ctx, 0, -125, 2.9, 540, 900):
            shaft(ctx, -900, 900, scroll=0, first_floor=8)
            ropes(ctx, -900, -262, 6, snapped=1, t_snap=12)
            car(ctx, tl, "smile", "down", look=1.0, brakes=1.0, panel=button_panel(1.0, tl))
            # arm reaching to the alarm button
            ctx.set_line_width(7.5 * 1.7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(*SKIN)
            ctx.move_to(19, -112); ctx.line_to(58, -100); ctx.stroke()
        steps = [("PRESS ALARM", 0.0, YEL), ("STAY INSIDE", tst - tp, CYN), ("WAIT", twa - tp, GRN)]
        for k, (s, t0, col) in enumerate(steps):
            if tt < t0: continue
            y = 520 + k * 0  # stacked as a row along the top
            x = [220, 540, 860][k]
            ctx.save(); ctx.translate(x, 540); sc = pop(tt - t0, 0.2); ctx.scale(sc, sc)
            chip(ctx, s, 0, 0, 44, col, (0, 0, 0))
            ctx.restore()
        if tt > 0.2:
            for k in range(3):
                a = (tl * 2 + k / 3) % 1
                ctx.arc(540 + (63 - 0) * 2.9, 900 + (-98 + 125) * 2.9, 40 + 120 * a, -0.6, 0.6)
                ctx.set_source_rgba(*YEL, 1 - a); ctx.set_line_width(6); ctx.stroke()


def s6(ctx, tg, tl, T):
    tk = wt(6, "Knew"); ty = wt(6, "Yes"); tn = wt(6, "no")
    # eight cables, then a big YES / NO choice
    for k in range(8):
        x = 540 + (k - 3.5) * 46
        a = clamp((tl - k * 0.05) / 0.2)
        ctx.move_to(x, 380); ctx.line_to(x, 380 + 360 * a)
        ctx.set_source_rgb(*STEEL); ctx.set_line_width(14); ctx.stroke()
    rrect(ctx, 330, 740, 420, 50, 12); ctx.set_source_rgb(0.38, 0.4, 0.55); ctx.fill()
    s = pop(tl, 0.25)
    ctx.save(); ctx.translate(540, 600); ctx.scale(s, s)
    glow_circle(ctx, 0, 0, 260, CYN, 0.4)
    text(ctx, "8", 0, 0, 260, YEL, stroke=10)
    ctx.restore()
    for k, (lab, col, t0) in enumerate((("YES", GRN, ty), ("NO", RED, tn))):
        if tl < t0 - 0.05: continue
        sc = pop(tl - t0 + 0.05, 0.22) * (1 + 0.04 * math.sin(tl * 7 + k))
        ctx.save(); ctx.translate(320 + k * 440, 990); ctx.scale(sc, sc)
        rrect(ctx, -170, -85, 340, 170, 50); ctx.set_source_rgb(*col); ctx.fill()
        text(ctx, lab, 0, 0, 110, WHT if k else (0, 0, 0), shadow=False)
        ctx.restore()
    if tl > tk - 0.05 and tl < ty:
        popchip(ctx, "COMMENT BELOW", 540, 990, tl - tk + 0.05, WHT, (0, 0, 0), 56)


SCENES = [s0, s1, s2, s3, s4, s5, s6]


def _snap(A, t, g=0.7):
    import numpy as np
    d = 0.35; n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.hp(A.noise(d), 2500) * np.exp(-tt * 30) + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 20) * 0.6
    A.add(A.sfx_buf, x, t, g)


def _rumble(A, t, d, g=0.35):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    x = A.lp(A.noise(d), 220) * np.minimum(1, tt / 0.3) * np.minimum(1, (d - tt) / 0.3)
    A.add(A.sfx_buf, x, t, g)


def _screech(A, t, d=0.9, g=0.18):
    import numpy as np
    n = int(d * 44100); tt = np.arange(n) / 44100
    f = 2600 + 300 * np.sin(2 * np.pi * 23 * tt)
    x = (np.sin(2 * np.pi * np.cumsum(f) / 44100) + 0.6 * A.bp(A.noise(d), 2000, 6000)) * np.minimum(1, tt / 0.03) * np.exp(-tt * 2.2)
    A.add(A.sfx_buf, x, t, g)


def sfx(A):
    t_sn = A.W(0, "Snap")
    for k in range(int(t_sn / 0.7) + 1):
        A.thump(0.3 + k * 0.7, 0.4, 50)                     # heartbeat before the snap
    _snap(A, t_sn - 0.05)
    A.thump(t_sn, 0.6, 55)
    _rumble(A, A.W(0, "drops"), A.S(1) + A.W(1, "Three") - 0.2 - A.W(0, "drops"))
    A.whoosh(A.W(0, "drops") + 0.3, 0.25, 0.5)
    A.ding(A.W(1, "seconds"), 0.08, 1568)
    for k in range(3):
        A.pop(A.W(1, "Three") + k * 0.25, 0.3)
    A.boing(A.W(1, "you", 1), 0.15, 320)
    A.pop(A.W(2, "One"), 0.3); A.ding(A.W(2, "cables"), 0.08, A.note(76))
    A.ding(A.W(2, "Each"), 0.08, A.note(79))
    A.boing(A.W(2, "Indian"), 0.18, 380)
    for k in range(6):
        A.ding(A.W(2, "More") + 0.2 + k * 0.12, 0.03, 3000 + 200 * k, 0.2)   # jingling keys
    A.pop(A.W(3, "Two"), 0.3)
    _rumble(A, A.S(3), A.W(3, "rails") - A.S(3) + 0.1, 0.3)
    _screech(A, A.W(3, "Brakes"), 1.0, 0.14)
    A.thump(A.W(3, "rails") + 0.1, 0.5, 60)
    _screech(A, A.W(3, "Like") + 0.05, 0.6, 0.12)
    A.horn(A.W(3, "passenger"), 0.05)
    A.pop(A.W(4, "Three"), 0.3)
    A.whoosh(A.W(4, "Jump") + 0.2, 0.2, 0.4)
    A.thump(A.W(4, "Myth") - 0.02, 0.6, 60)
    A.zap_down(A.W(4, "cancels") + 0.4, 0.14, 0.8)
    A.boing(A.W(5, "Bollywood"), 0.15, 260, 0.8)
    for k in range(4):
        A.ding(A.W(5, "Press") + k * 0.35, 0.07, 1760, 0.3)          # alarm bell
    A.pop(A.W(5, "stay"), 0.3); A.pop(A.W(5, "wait"), 0.3)
    A.pop(A.W(6, "Yes"), 0.3); A.pop(A.W(6, "no"), 0.3)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(6, "Send") + 0.1 + k * 0.1, 0.07, A.note(m))

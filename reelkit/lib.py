"""reelkit.lib - drawing helpers, characters and props for What-If reels (pycairo).
Screen is 1080x1920. Props marked (cm) draw in centimetres inside `with World(ctx, k):`,
where k = pixels per cm and floor y = 0 (up is negative)."""
import math, random
import cairo

W, H, FPS = 1080, 1920, 30
FLOOR_Y = 1230
DISPLAY = "Anton"     # headline / caption font
SANS = "Poppins"      # small labels
YEL = (1.0, 0.84, 0.1); RED = (1.0, 0.22, 0.25); ORG = (1.0, 0.55, 0.05)
CYN = (0.3, 0.9, 1.0); PNK = (1.0, 0.36, 0.62); GRN = (0.35, 0.95, 0.5); WHT = (1, 1, 1)
SKIN = (0.93, 0.72, 0.56)
HERO = (1.0, 0.8, 0.15)
SHIRTS = [(1.0, 0.45, 0.2), (0.3, 0.6, 1.0), (0.95, 0.3, 0.55), (0.3, 0.85, 0.55), (1.0, 0.8, 0.2), (0.7, 0.45, 1.0)]

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def ease_io(x):
    x = clamp(x); return x * x * (3 - 2 * x)


def ease_back(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def pop(t, d=0.22):
    """0 -> overshoot -> 1 scale"""
    if t <= 0: return 0.001
    return max(0.001, ease_back(t / d))


def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def font(ctx, fam, size):
    ctx.select_font_face(fam, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if fam == SANS else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def text_w(ctx, s, fam, size):
    font(ctx, fam, size)
    return ctx.text_extents(s).x_advance


def text(ctx, s, x, y, size, col=WHT, fam=DISPLAY, stroke=0, scol=(0, 0, 0), align="c",
         alpha=1.0, shadow=True):
    """y is the vertical centre of capitals"""
    font(ctx, fam, size)
    ext = ctx.text_extents(s)
    fe = ctx.font_extents()
    cap = size * (0.72 if fam == DISPLAY else 0.70)
    if align == "c": x0 = x - ext.x_advance / 2
    elif align == "r": x0 = x - ext.x_advance
    else: x0 = x
    y0 = y + cap / 2
    if shadow:
        ctx.move_to(x0 + size * 0.04, y0 + size * 0.06)
        ctx.text_path(s)
        ctx.set_source_rgba(0, 0, 0, 0.45 * alpha)
        if stroke:
            ctx.set_line_width(stroke * 2); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke_preserve()
        ctx.fill()
    ctx.move_to(x0, y0)
    ctx.text_path(s)
    if stroke:
        ctx.set_source_rgba(*scol, alpha)
        ctx.set_line_width(stroke * 2); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
    ctx.set_source_rgba(*col, alpha)
    ctx.fill()
    return ext.x_advance


def glow_circle(ctx, x, y, r, col, a=0.6):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *col, a)
    g.add_color_stop_rgba(0.4, *col, a * 0.35)
    g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def chip(ctx, s, x, y, size, bg, fg=(0, 0, 0), fam=DISPLAY, align="c", alpha=1.0, padx=22, pady=12):
    w = text_w(ctx, s, fam, size)
    hgt = size * 0.72 + pady * 2
    if align == "c": x0 = x - w / 2 - padx
    elif align == "l": x0 = x
    else: x0 = x - w - 2 * padx
    rrect(ctx, x0, y - hgt / 2, w + 2 * padx, hgt, hgt / 2.6)
    ctx.set_source_rgba(*bg, alpha); ctx.fill()
    text(ctx, s, x0 + padx + w / 2, y, size, fg, fam, shadow=False, alpha=alpha)
    return w + 2 * padx


def check(ctx, x, y, s, col):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(s * 0.22)
    ctx.move_to(x - s * 0.45, y); ctx.line_to(x - s * 0.1, y + s * 0.35); ctx.line_to(x + s * 0.5, y - s * 0.4)
    ctx.set_source_rgb(*col); ctx.stroke()


def cross(ctx, x, y, s, col, lw=None):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(lw or s * 0.22)
    ctx.move_to(x - s / 2, y - s / 2); ctx.line_to(x + s / 2, y + s / 2)
    ctx.move_to(x + s / 2, y - s / 2); ctx.line_to(x - s / 2, y + s / 2)
    ctx.set_source_rgb(*col); ctx.stroke()


def hrand(*a):
    return random.Random(hash(a) & 0xffffffff).random()


def person(ctx, x, y, h, shirt=(0.3, 0.6, 1.0), expr="smile", arms="down", t=0.0, look=0.0):
    """feet at (x, y), height h"""
    ctx.save(); ctx.translate(x, y)
    u = h / 100.0
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    # legs
    ctx.set_line_width(9 * u); ctx.set_source_rgb(0.15, 0.17, 0.3)
    ctx.move_to(-9 * u, -40 * u); ctx.line_to(-11 * u, -2 * u)
    ctx.move_to(9 * u, -40 * u); ctx.line_to(11 * u, -2 * u); ctx.stroke()
    # arms
    ctx.set_line_width(7.5 * u); ctx.set_source_rgb(*SKIN)
    if arms == "up":
        sw = math.sin(t * 14) * 6 * u
        ctx.move_to(-17 * u, -66 * u); ctx.line_to(-30 * u, -92 * u + sw)
        ctx.move_to(17 * u, -66 * u); ctx.line_to(30 * u, -92 * u - sw)
    elif arms == "cheeks":
        ctx.move_to(-17 * u, -66 * u); ctx.line_to(-24 * u, -80 * u)
        ctx.move_to(17 * u, -66 * u); ctx.line_to(24 * u, -80 * u)
    elif arms == "wave":
        ctx.move_to(-17 * u, -66 * u); ctx.line_to(-24 * u, -40 * u)
        a = math.sin(t * 9) * 0.5
        ctx.move_to(17 * u, -66 * u); ctx.line_to(17 * u + math.sin(-2.4 + a) * -28 * u, -66 * u + math.cos(-2.4 + a) * 28 * u)
    elif arms == "run":
        a = math.sin(t * 18)
        ctx.move_to(-17 * u, -66 * u); ctx.line_to(-17 * u - 18 * a * u, -45 * u)
        ctx.move_to(17 * u, -66 * u); ctx.line_to(17 * u + 18 * a * u, -45 * u)
    else:
        ctx.move_to(-17 * u, -66 * u); ctx.line_to(-24 * u, -40 * u)
        ctx.move_to(17 * u, -66 * u); ctx.line_to(24 * u, -40 * u)
    ctx.stroke()
    # body
    rrect(ctx, -19 * u, -72 * u, 38 * u, 36 * u, 12 * u); ctx.set_source_rgb(*shirt); ctx.fill()
    # head
    hx, hy, hr = 0, -86 * u, 15 * u
    ctx.arc(hx, hy, hr, 0, 6.3); ctx.set_source_rgb(*SKIN); ctx.fill()
    ctx.arc(hx, hy - 2 * u, hr, math.pi * 1.05, math.pi * 1.95); ctx.set_source_rgb(0.15, 0.1, 0.08); ctx.fill()
    if expr == "cheeks":
        for s in (-1, 1):
            ctx.arc(s * 11 * u, hy + 5 * u, 7 * u, 0, 6.3); ctx.set_source_rgb(0.98, 0.6, 0.55); ctx.fill()
    ex = look * 3 * u
    for s in (-1, 1):
        r = 2.6 * u if expr not in ("shock",) else 3.4 * u
        ctx.arc(s * 5.5 * u + ex, hy + 1 * u, r, 0, 6.3); ctx.set_source_rgb(0.08, 0.08, 0.12); ctx.fill()
    ctx.set_line_width(2.2 * u); ctx.set_source_rgb(0.25, 0.08, 0.08)
    if expr == "shock":
        ctx.arc(ex, hy + 8 * u, 3.6 * u, 0, 6.3); ctx.fill()
    elif expr == "worry":
        ctx.arc(ex, hy + 12 * u, 4.5 * u, math.pi * 1.15, math.pi * 1.85); ctx.stroke()
    elif expr == "cheeks":
        ctx.arc(ex, hy + 8 * u, 2 * u, 0, 6.3); ctx.fill()
    else:
        ctx.arc(ex, hy + 5 * u, 5 * u, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
    ctx.restore()


def pencil(ctx, x, y, h):
    """vertical pencil, base at (x,y), height h"""
    w = h * 0.07
    ctx.save(); ctx.translate(x, y)
    rrect(ctx, -w / 2, -h * 0.07, w, h * 0.07, w * 0.2); ctx.set_source_rgb(1.0, 0.55, 0.65); ctx.fill()
    ctx.rectangle(-w / 2, -h * 0.11, w, h * 0.04); ctx.set_source_rgb(0.75, 0.76, 0.8); ctx.fill()
    ctx.rectangle(-w / 2, -h * 0.82, w, h * 0.71); ctx.set_source_rgb(1.0, 0.8, 0.15); ctx.fill()
    ctx.rectangle(-w / 6, -h * 0.82, w / 3, h * 0.71); ctx.set_source_rgb(1.0, 0.88, 0.4); ctx.fill()
    ctx.move_to(-w / 2, -h * 0.82); ctx.line_to(w / 2, -h * 0.82); ctx.line_to(0, -h); ctx.close_path()
    ctx.set_source_rgb(0.95, 0.82, 0.62); ctx.fill()
    ctx.move_to(-w * 0.17, -h * 0.95); ctx.line_to(w * 0.17, -h * 0.95); ctx.line_to(0, -h); ctx.close_path()
    ctx.set_source_rgb(0.15, 0.15, 0.18); ctx.fill()
    ctx.restore()


def earth(ctx, x, y, r, t, face=False):
    glow_circle(ctx, x, y, r * 1.45, (0.3, 0.6, 1.0), 0.5)
    ctx.save(); ctx.arc(x, y, r, 0, 6.3); ctx.clip()
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 0.25, 0.6, 1.0); g.add_color_stop_rgb(1, 0.05, 0.2, 0.55)
    ctx.set_source(g); ctx.paint()
    rot = t * 40
    for k in range(9):
        cx = x - r + ((hrand("lx", k) * 2.6 * r + rot) % (2.6 * r)) - 0.3 * r
        cy = y - r * 0.8 + hrand("ly", k) * 1.6 * r
        rr = r * (0.16 + 0.18 * hrand("lr", k))
        ctx.save(); ctx.translate(cx, cy); ctx.scale(1.3, 0.85)
        ctx.arc(0, 0, rr, 0, 6.3); ctx.arc(rr * 0.6, rr * 0.5, rr * 0.7, 0, 6.3)
        ctx.set_source_rgb(0.25, 0.75, 0.4); ctx.fill(); ctx.restore()
    g = cairo.RadialGradient(x + r * 0.4, y + r * 0.4, r * 0.2, x, y, r * 1.05)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0.1, 0.55)
    ctx.set_source(g); ctx.paint()
    ctx.restore()
    if face:
        for s in (-1, 1):
            ctx.arc(x + s * r * 0.28, y - r * 0.1, r * 0.07, 0, 6.3); ctx.set_source_rgb(0.05, 0.05, 0.1); ctx.fill()
        ctx.set_line_width(r * 0.05); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.arc(x, y + r * 0.05, r * 0.3, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
        for s in (-1, 1):
            ctx.arc(x + s * r * 0.45, y + r * 0.12, r * 0.09, 0, 6.3); ctx.set_source_rgba(1, 0.5, 0.6, 0.6); ctx.fill()


def stamp(ctx, s, x, y, tt, col=RED, size=96, rot=-0.12, fg=WHT):
    if tt < 0: return
    sc = 2.0 - 1.0 * ease_out(tt / 0.14)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc)
    w = text_w(ctx, s, DISPLAY, size)
    rrect(ctx, -w / 2 - 36, -size * 0.62, w + 72, size * 1.24, 22)
    ctx.set_source_rgba(*col, 0.95); ctx.fill_preserve(); ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(7); ctx.stroke()
    text(ctx, s, 0, 0, size, fg, shadow=False)
    ctx.restore()


def popchip(ctx, s, x, y, tt, bg=YEL, fg=(0, 0, 0), size=50):
    if tt < 0: return
    sc = pop(tt, 0.2)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    chip(ctx, s, 0, 0, size, bg, fg)
    ctx.restore()


def sparkles(ctx, x, y, r, t, n=14, col=CYN, seed="sp"):
    for k in range(n):
        a = hrand(seed, k) * 6.3 + t * (0.5 + hrand(seed + "v", k))
        rr = r * (0.4 + 0.6 * hrand(seed + "r", k))
        tw = 0.5 + 0.5 * math.sin(t * 7 + k * 1.7)
        glow_circle(ctx, x + math.cos(a) * rr, y + math.sin(a) * rr, 18 + 22 * tw, col, 0.8 * tw)


def egg(ctx, x, y, r):
    ctx.save(); ctx.translate(x, y); ctx.scale(0.78, 1)
    ctx.move_to(0, -r * 1.25)
    ctx.curve_to(r * 0.9, -r * 1.2, r, r * 0.2, 0, r)
    ctx.curve_to(-r, r * 0.2, -r * 0.9, -r * 1.2, 0, -r * 1.25)
    ctx.restore()
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.4, r * 0.1, x, y, r * 1.2)
    g.add_color_stop_rgb(0, 1, 0.97, 0.9); g.add_color_stop_rgb(1, 0.85, 0.7, 0.55)
    ctx.set_source(g); ctx.fill()


def cat_head(ctx, x, y, s, t, narrow=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    col = (0.32, 0.3, 0.36)
    for sx in (-1, 1):
        ctx.move_to(sx * 140, -150); ctx.line_to(sx * 330, -470); ctx.line_to(sx * 360, -60); ctx.close_path()
        ctx.set_source_rgb(*col); ctx.fill()
        ctx.move_to(sx * 175, -170); ctx.line_to(sx * 315, -400); ctx.line_to(sx * 320, -120); ctx.close_path()
        ctx.set_source_rgb(0.75, 0.5, 0.55); ctx.fill()
    ctx.save(); ctx.scale(1.25, 1); ctx.arc(0, 0, 360, 0, 6.3); ctx.restore()
    ctx.set_source_rgb(*col); ctx.fill()
    for sx in (-1, 1):
        ex = sx * 150
        glow_circle(ctx, ex, -40, 170, (1, 0.85, 0.2), 0.5)
        ctx.save(); ctx.translate(ex, -40); ctx.scale(1, 1 - 0.55 * narrow)
        ctx.arc(0, 0, 80, 0, 6.3); ctx.set_source_rgb(1, 0.85, 0.15); ctx.fill()
        ctx.save(); ctx.scale(0.22, 1); ctx.arc(0, 0, 70, 0, 6.3); ctx.restore()
        ctx.set_source_rgb(0.05, 0.05, 0.05); ctx.fill()
        ctx.restore()
    ctx.move_to(-35, 90); ctx.line_to(35, 90); ctx.line_to(0, 130); ctx.close_path(); ctx.set_source_rgb(0.85, 0.5, 0.55); ctx.fill()
    ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.6)
    for sx in (-1, 1):
        for k in range(3):
            ctx.move_to(sx * 90, 130 + k * 22); ctx.line_to(sx * 360, 100 + k * 40 - 20)
    ctx.stroke()
    ctx.restore()


def pizza(ctx, x, y, r, t, bites=0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * 0.3)
    ctx.arc(0, 0, r, 0, 6.3); ctx.set_source_rgb(0.85, 0.55, 0.25); ctx.fill()
    ctx.arc(0, 0, r * 0.88, 0, 6.3); ctx.set_source_rgb(1.0, 0.82, 0.35); ctx.fill()
    for k in range(10):
        a = hrand("pa", k) * 6.3; rr = r * (0.2 + 0.6 * hrand("pr", k))
        ctx.arc(math.cos(a) * rr, math.sin(a) * rr, r * 0.1, 0, 6.3); ctx.set_source_rgb(0.8, 0.15, 0.12); ctx.fill()
    ctx.set_line_width(4); ctx.set_source_rgba(0.6, 0.35, 0.1, 0.8)
    for k in range(4):
        a = k * math.pi / 4
        ctx.move_to(math.cos(a) * -r * 0.88, math.sin(a) * -r * 0.88); ctx.line_to(math.cos(a) * r * 0.88, math.sin(a) * r * 0.88)
    ctx.stroke()
    ctx.restore()


def car_top(ctx, col=RED):
    rrect(ctx, -70, -130, 140, 260, 40); ctx.set_source_rgb(*col); ctx.fill()
    rrect(ctx, -56, -70, 112, 60, 16); ctx.set_source_rgb(0.08, 0.1, 0.18); ctx.fill()
    rrect(ctx, -52, 50, 104, 40, 14); ctx.set_source_rgb(0.08, 0.1, 0.18); ctx.fill()
    for s in (-1, 1):
        ctx.arc(s * 40, -122, 12, 0, 6.3); ctx.set_source_rgb(1, 0.95, 0.7); ctx.fill()


def plane(ctx, s=1.0):
    ctx.save(); ctx.scale(s, s)
    ctx.move_to(-120, 10); ctx.line_to(130, -90); ctx.line_to(40, 110); ctx.line_to(10, 40); ctx.close_path()
    ctx.set_source_rgb(*WHT); ctx.fill()
    ctx.move_to(10, 40); ctx.line_to(130, -90); ctx.line_to(-10, 70); ctx.close_path()
    ctx.set_source_rgb(0.7, 0.75, 0.85); ctx.fill()
    ctx.restore()


class World:
    def __init__(self, ctx, k, ax=540, fy=FLOOR_Y):
        self.ctx, self.k, self.ax, self.fy = ctx, k, ax, fy
    def __enter__(self):
        self.ctx.save(); self.ctx.translate(self.ax, self.fy); self.ctx.scale(self.k, self.k); return self.ctx
    def __exit__(self, *a):
        self.ctx.restore()


def room(ctx, wall=((0.13, 0.17, 0.42), (0.32, 0.17, 0.48)), floor=((0.55, 0.3, 0.55), (0.35, 0.15, 0.38)), fy=FLOOR_Y, dark=0.0):
    g = cairo.LinearGradient(0, 0, 0, fy)
    g.add_color_stop_rgb(0, *wall[0]); g.add_color_stop_rgb(1, *wall[1])
    ctx.set_source(g); ctx.rectangle(0, 0, W, fy); ctx.fill()
    g = cairo.LinearGradient(0, fy, 0, H)
    g.add_color_stop_rgb(0, *floor[0]); g.add_color_stop_rgb(1, *floor[1])
    ctx.set_source(g); ctx.rectangle(0, fy, W, H - fy); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.12); ctx.rectangle(0, fy - 2, W, 4); ctx.fill()
    if dark: ctx.set_source_rgba(0, 0.02, 0.08, dark); ctx.paint()


def ghosts(ctx, x, n, t, col=YEL, upto=None):
    """stack of n person-height outlines from floor (world coords)"""
    shown = n if upto is None else min(n, upto)
    for i in range(int(math.ceil(shown))):
        a = clamp(shown - i)
        ctx.save(); ctx.translate(x, -17 * i)
        ctx.set_source_rgba(*col, 0.25 * a); ctx.rectangle(-6, -17, 12, 17); ctx.fill()
        ctx.set_source_rgba(*col, 0.9 * a); ctx.set_line_width(0.5); ctx.rectangle(-6, -17, 12, 17); ctx.stroke()
        ctx.restore()


def dotted(ctx, x, y0, y1, col=YEL, lw=0.6, dash=2.0):
    ctx.save(); ctx.set_dash([dash, dash]); ctx.set_line_width(lw); ctx.set_source_rgba(*col, 0.95)
    ctx.move_to(x, y0); ctx.line_to(x, y1); ctx.stroke(); ctx.restore()


def hero_ring(ctx, x, h=17, a=1.0):
    glow_circle(ctx, x, -h * 0.5, h * 1.1, YEL, 0.35 * a)


def door(ctx, x0, open_=0):
    ctx.set_source_rgb(0.95, 0.88, 0.93); ctx.rectangle(x0 - 5, -205, 100, 205); ctx.fill()
    ctx.set_source_rgb(1.0, 0.62, 0.78); ctx.rectangle(x0, -200, 90, 200); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35)
    for (yy, hh) in ((-188, 80), (-95, 80)):
        rrect(ctx, x0 + 12, yy, 66, hh, 3); ctx.set_line_width(1.2); ctx.stroke()
    ctx.set_source_rgb(0.95, 0.85, 0.3); rrect(ctx, x0 + 66, -102, 16, 4, 2); ctx.fill()
    ctx.arc(x0 + 80, -100, 3, 0, 6.3); ctx.fill()


def sofa(ctx, x0, x1):
    ctx.set_source_rgb(0.15, 0.1, 0.12)
    for xx in (x0 + 3, x1 - 7): ctx.rectangle(xx, -15, 4, 15)
    ctx.fill()
    rrect(ctx, x0, -48, x1 - x0, 33, 6); ctx.set_source_rgb(0.25, 0.55, 0.95); ctx.fill()
    rrect(ctx, x0, -88, 18, 60, 7); ctx.fill()
    rrect(ctx, x0 + 14, -58, x1 - x0 - 14, 14, 6); ctx.set_source_rgb(0.4, 0.68, 1.0); ctx.fill()


def chair(ctx, x0):
    ctx.set_source_rgb(0.98, 0.84, 0.3)
    ctx.rectangle(x0, -45, 4, 45); ctx.rectangle(x0 + 40, -45, 4, 45); ctx.fill()
    rrect(ctx, x0 - 2, -48, 48, 5, 1.5); ctx.fill()
    ctx.rectangle(x0 + 40, -92, 4, 47); ctx.fill()
    rrect(ctx, x0 + 36, -92, 10, 30, 2); ctx.fill()


def car_side(ctx, cx):
    ctx.set_source_rgb(0.95, 0.3, 0.55)
    ctx.move_to(cx - 150, -30); ctx.line_to(cx - 150, -95); ctx.curve_to(cx - 110, -100, cx - 70, -145, cx, -145)
    ctx.line_to(cx + 200, -145); ctx.line_to(cx + 200, -30); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(0.12, 0.08, 0.2); ctx.arc(cx, -32.5, 40, math.pi, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.arc(cx, -32.5, 32.5, 0, 6.3); ctx.fill()
    ctx.set_source_rgb(0.75, 0.78, 0.85); ctx.arc(cx, -32.5, 19, 0, 6.3); ctx.fill()
    ctx.set_source_rgb(0.45, 0.48, 0.55)
    for k in range(5):
        a = k * 1.2566
        ctx.move_to(cx, -32.5); ctx.line_to(cx + math.cos(a) * 17, -32.5 + math.sin(a) * 17)
    ctx.set_line_width(3); ctx.stroke()
    ctx.set_source_rgb(0.5, 0.5, 0.55); ctx.rectangle(cx - 400, 0, 800, 12); ctx.fill()


def kscale(ctx, x, reading):
    rrect(ctx, x - 10, -3, 20, 3, 0.8); ctx.set_source_rgb(0.92, 0.95, 1); ctx.fill()
    rrect(ctx, x - 8, -2.6, 6, 2, 0.4); ctx.set_source_rgb(0.1, 0.12, 0.2); ctx.fill()


def cat_side(ctx, t, crouch=0.0, pupil=0.2, tail=0.0):
    col = (0.42, 0.43, 0.5)
    ctx.save(); ctx.translate(0, crouch * 4)
    # tail
    ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(*col)
    tw = math.sin(t * 6) * 4 * tail
    ctx.move_to(-21, -25); ctx.curve_to(-32, -28, -36 + tw, -40, -30 + tw, -50); ctx.stroke()
    # legs
    for lx in (-16, -9, 11, 17):
        rrect(ctx, lx - 2, -18, 4.2, 18 - crouch * 4, 2); ctx.fill()
    # body
    ctx.save(); ctx.translate(0, -24); ctx.scale(1, 0.48); ctx.arc(0, 0, 23, 0, 6.3); ctx.restore(); ctx.fill()
    # head
    hx, hy = 24, -33 + crouch * 3
    ctx.arc(hx, hy, 8.5, 0, 6.3); ctx.fill()
    for ex in (-4, 4):
        ctx.move_to(hx + ex - 3.5, hy - 6); ctx.line_to(hx + ex, hy - 14); ctx.line_to(hx + ex + 3.5, hy - 6); ctx.close_path(); ctx.fill()
    glow_circle(ctx, hx + 4, hy - 1, 6, YEL, 0.6)
    ctx.save(); ctx.translate(hx + 4.5, hy - 1); ctx.scale(1, 1.15)
    ctx.arc(0, 0, 2.3, 0, 6.3); ctx.set_source_rgb(1, 0.85, 0.15); ctx.fill()
    ctx.save(); ctx.scale(0.25 + 0.7 * pupil, 1); ctx.arc(0, 0, 2.0, 0, 6.3); ctx.restore()
    ctx.set_source_rgb(0.03, 0.03, 0.03); ctx.fill(); ctx.restore()
    ctx.move_to(hx + 8.5, hy + 2); ctx.line_to(hx + 7, hy + 3.2); ctx.set_source_rgb(0.95, 0.55, 0.6); ctx.set_line_width(1.2); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(0.3)
    for k in range(3):
        ctx.move_to(hx + 7, hy + 2.5); ctx.line_to(hx + 17, hy + 0.5 + k * 1.6)
    ctx.stroke()
    ctx.restore()


def shoe(ctx, x0):
    ctx.set_source_rgb(0.2, 0.55, 1.0)
    ctx.move_to(x0, 0); ctx.line_to(x0, -7); ctx.curve_to(x0 + 2, -11, x0 + 9, -11, x0 + 11, -9)
    ctx.line_to(x0 + 18, -6); ctx.curve_to(x0 + 26, -5, x0 + 28, -3, x0 + 28, 0); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.rectangle(x0, -1.6, 28, 1.6); ctx.fill()


def bread(ctx, x0, w=12, d=12, th=1.2):
    # 3/4 view slab: front face + top face skewed
    sk = 0.45
    ctx.set_source_rgb(0.75, 0.45, 0.2)
    ctx.rectangle(x0, -th, w, th); ctx.fill()
    ctx.move_to(x0, -th); ctx.line_to(x0 + w, -th); ctx.line_to(x0 + w + d * sk, -th - d * sk); ctx.line_to(x0 + d * sk, -th - d * sk); ctx.close_path()
    ctx.set_source_rgb(0.75, 0.45, 0.2); ctx.fill()
    ctx.move_to(x0 + 0.6, -th - 0.3); ctx.line_to(x0 + w - 0.6, -th - 0.3); ctx.line_to(x0 + w - 0.6 + d * sk * 0.95, -th - d * sk * 0.95)
    ctx.line_to(x0 + 0.6 + d * sk * 0.95, -th - d * sk * 0.95); ctx.close_path()
    ctx.set_source_rgb(0.98, 0.88, 0.62); ctx.fill()


def rice(ctx, x, y, rot=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(0.35, 0.14)
    ctx.arc(0, 0, 1, 0, 6.3); ctx.restore()
    ctx.set_source_rgb(0.98, 0.97, 0.92); ctx.fill()


def strawberry(ctx, x, y):
    ctx.save(); ctx.translate(x, y)
    ctx.move_to(0, 1.9); ctx.curve_to(-1.9, 0.6, -1.8, -1.6, -0.6, -1.7); ctx.curve_to(-0.2, -1.75, 0.2, -1.75, 0.6, -1.7)
    ctx.curve_to(1.8, -1.6, 1.9, 0.6, 0, 1.9); ctx.close_path(); ctx.set_source_rgb(0.95, 0.15, 0.25); ctx.fill()
    ctx.set_source_rgb(1, 0.9, 0.4)
    for k in range(9):
        ctx.arc(-1.0 + (k % 3) * 1.0 + (0.4 if (k // 3) % 2 else 0), -0.9 + (k // 3) * 0.9, 0.09, 0, 6.3); ctx.fill()
    ctx.set_source_rgb(0.2, 0.75, 0.35)
    for a in (-0.9, -0.3, 0.3, 0.9):
        ctx.save(); ctx.translate(0, -1.7); ctx.rotate(a); ctx.scale(0.35, 1); ctx.arc(0, -0.45, 0.5, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.restore()


def counter(ctx, x0, x1):
    ctx.set_source_rgb(0.3, 0.7, 0.95); ctx.rectangle(x0, -86, x1 - x0, 86); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.3); ctx.set_line_width(1)
    for xx in range(int(x0) + 5, int(x1), 45):
        rrect(ctx, xx, -78, 40, 66, 3); ctx.stroke()
        ctx.arc(xx + 34, -45, 1.5, 0, 6.3); ctx.fill()
    ctx.set_source_rgb(0.95, 0.95, 1); ctx.rectangle(x0 - 3, -90, x1 - x0 + 6, 4); ctx.fill()
    ctx.set_source_rgb(0.12, 0.08, 0.15); ctx.rectangle(x0 + 2, -8, x1 - x0 - 4, 8); ctx.fill()


def plate_food(ctx, x):
    ctx.set_source_rgb(1, 1, 1); ctx.save(); ctx.translate(x, -91.5); ctx.scale(1, 0.18); ctx.arc(0, 0, 13, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_source_rgb(1.0, 0.85, 0.3); ctx.save(); ctx.translate(x - 2, -94); ctx.scale(1, 0.5); ctx.arc(0, 0, 7, math.pi, 0); ctx.restore(); ctx.fill()
    ctx.set_source_rgb(1.0, 0.45, 0.35); ctx.arc(x + 6, -94, 2.5, 0, 6.3); ctx.fill()


def phone_upright(ctx, x0, screen_text=""):
    rrect(ctx, x0, -15, 7.2, 15, 0.9); ctx.set_source_rgb(0.08, 0.08, 0.12); ctx.fill()
    rrect(ctx, x0 + 0.3, -14.7, 6.6, 14.4, 0.7)
    g = cairo.LinearGradient(0, -15, 0, 0); g.add_color_stop_rgb(0, 0.25, 0.4, 0.95); g.add_color_stop_rgb(1, 0.85, 0.35, 0.7)
    ctx.set_source(g); ctx.fill()
    rrect(ctx, x0 + 0.6, -13.4, 4.2, 1.4, 0.5); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    rrect(ctx, x0 + 0.3, -5.6, 6.6, 5.3, 0.5); ctx.set_source_rgb(0.88, 0.89, 0.94); ctx.fill()
    for r in range(3):
        for c in range(7):
            rrect(ctx, x0 + 0.5 + c * 0.9, -5.3 + r * 1.6, 0.75, 1.3, 0.15); ctx.set_source_rgb(1, 1, 1); ctx.fill()


def stairs(ctx, x0, n=5):
    for k in range(n):
        ctx.set_source_rgb(0.98 - k * 0.04, 0.55, 0.72 - k * 0.03)
        ctx.rectangle(x0 + k * 28, -17 * (k + 1), 400, 17); ctx.fill()
        ctx.set_source_rgb(1, 0.8, 0.9); ctx.rectangle(x0 + k * 28, -17 * (k + 1), 400, 1.5); ctx.fill()


def lift_panel(ctx, x0):
    ctx.set_source_rgb(0.7, 0.75, 0.85); ctx.rectangle(x0 - 120, -260, 260, 260); ctx.fill()
    ctx.set_source_rgb(0.6, 0.65, 0.75); ctx.rectangle(x0 - 110, -230, 110, 230); ctx.rectangle(x0 + 2, -230, 110, 230); ctx.fill()
    rrect(ctx, x0 + 118, -140, 18, 50, 2); ctx.set_source_rgb(0.85, 0.88, 0.95); ctx.fill()
    for k in range(4):
        ctx.arc(x0 + 127, -132 + k * 11, 3.6, 0, 6.3); ctx.set_source_rgb(*(YEL if k == 3 else (0.4, 0.45, 0.55))); ctx.fill()


def pedal_well(ctx):
    ctx.set_source_rgb(0.22, 0.17, 0.38); ctx.rectangle(-300, -300, 600, 300); ctx.fill()
    ctx.set_source_rgb(0.4, 0.3, 0.55); ctx.move_to(-300, -60); ctx.line_to(80, -20); ctx.line_to(300, -20); ctx.line_to(300, 0); ctx.line_to(-300, 0); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(0.55, 0.55, 0.6); ctx.set_line_width(2.5)
    ctx.move_to(20, -120); ctx.line_to(30, -18); ctx.stroke()
    rrect(ctx, 20, -28, 20, 12, 2); ctx.set_source_rgb(0.85, 0.85, 0.9); ctx.fill()
    ctx.set_source_rgb(0.95, 0.3, 0.55); rrect(ctx, -200, -170, 120, 30, 8); ctx.fill()


def pill(ctx, x, y):
    ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.4)
    ctx.arc(0, 0, 0.5, 0, 6.3); ctx.restore(); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.set_source_rgb(0.9, 0.9, 0.95); ctx.rectangle(x - 0.5, y, 1, 0.3); ctx.fill()


def syringe(ctx, x0):
    rrect(ctx, x0, -1.6, 8.5, 1.6, 0.3); ctx.set_source_rgba(0.85, 0.95, 1, 0.9); ctx.fill()
    ctx.set_source_rgb(0.3, 0.6, 1); ctx.rectangle(x0 + 0.4, -1.3, 4.5, 1.0); ctx.fill()
    ctx.set_source_rgb(0.85, 0.85, 0.9); ctx.rectangle(x0 + 8.5, -1.0, 2.5, 0.4); ctx.rectangle(x0 - 2.5, -1.0, 2.5, 0.4); ctx.fill()
    ctx.rectangle(x0 + 11, -0.85, 3.5, 0.1); ctx.fill()


def lever_panel(ctx, glow=1.0):
    ctx.set_source_rgb(0.2, 0.25, 0.45); ctx.rectangle(-200, -220, 420, 220); ctx.fill()
    ctx.set_source_rgb(0.28, 0.33, 0.55); rrect(ctx, -180, -200, 380, 80, 6); ctx.fill()
    for k in range(6):
        c = [CYN, YEL, PNK, GRN, CYN, YEL][k]
        ctx.arc(-150 + k * 60, -160, 10, 0, 6.3); ctx.set_source_rgba(*c, 0.25 + 0.75 * glow); ctx.fill()
    ctx.set_source_rgb(0.6, 0.62, 0.7); ctx.rectangle(-40, -10, 80, 10); ctx.fill()
    ctx.save(); ctx.translate(0, -10); ctx.rotate(-0.35)
    ctx.set_line_width(7); ctx.move_to(0, 0); ctx.line_to(0, -70); ctx.stroke()
    ctx.arc(0, -74, 9, 0, 6.3); ctx.set_source_rgb(1.0, 0.3, 0.35); ctx.fill()
    ctx.restore()


def bed_blanket(ctx, x0, tug=0.0):
    ctx.set_source_rgb(0.28, 0.2, 0.4); ctx.rectangle(x0, -50, 400, 50); ctx.fill()
    ctx.set_source_rgb(0.95, 0.95, 1); ctx.rectangle(x0, -62, 400, 12); ctx.fill()
    ctx.set_source_rgb(0.3, 0.55, 1.0)
    ctx.move_to(x0 - 6, -64); ctx.line_to(x0 + 400, -64); ctx.line_to(x0 + 400, -58)
    ctx.line_to(x0 - 6, -58); ctx.close_path(); ctx.fill()
    ctx.move_to(x0, -64); ctx.curve_to(x0 - 10, -50, x0 - 12, -30, x0 - 10 - tug, -10); ctx.line_to(x0 + 4 - tug, -8)
    ctx.curve_to(x0 + 2, -30, x0 + 4, -50, x0 + 6, -60); ctx.close_path(); ctx.fill()


def wall_switch(ctx, x):
    rrect(ctx, x - 4, -124, 8, 8, 1); ctx.set_source_rgb(0.95, 0.95, 1); ctx.fill()
    rrect(ctx, x - 1.5, -122, 3, 4, 0.5); ctx.set_source_rgb(0.75, 0.78, 0.85); ctx.fill()
    ctx.set_source_rgb(0.9, 0.9, 0.95); rrect(ctx, x - 25, -80, 50, 40, 4); ctx.fill()
    for k in range(6):
        ctx.rectangle(x - 22 + k * 8, -78, 4, 36)
    ctx.set_source_rgb(0.75, 0.78, 0.85); ctx.fill()


def rain(ctx, t, a=0.5, n=90):
    ctx.set_line_width(2.5)
    for k in range(n):
        x = hrand("rx", k) * W + 40
        y = ((hrand("ry", k) * H) + t * (1400 + 400 * hrand("rv", k))) % (H + 200) - 100
        ctx.move_to(x, y); ctx.line_to(x - 12, y + 40)
        ctx.set_source_rgba(0.7, 0.85, 1, a * (0.4 + 0.6 * hrand("ra", k))); ctx.stroke()


def skyline(ctx, t, lights=1.0):
    g = cairo.LinearGradient(0, 0, 0, FLOOR_Y)
    g.add_color_stop_rgb(0, 0.03, 0.05, 0.16); g.add_color_stop_rgb(1, 0.18, 0.1, 0.3)
    ctx.set_source(g); ctx.paint()
    for k in range(13):
        x = k * 90 - 20; w = 70 + 30 * hrand("bw", k); h = 300 + 500 * hrand("bh", k)
        ctx.rectangle(x, FLOOR_Y - h, w, h + 400); ctx.set_source_rgb(0.08, 0.08, 0.18); ctx.fill()
        for j in range(int(h / 50)):
            for i in range(int(w / 25)):
                if hrand("win", k, j, i) < 0.55 * lights:
                    ctx.rectangle(x + 6 + i * 22, FLOOR_Y - h + 15 + j * 48, 10, 18)
                    ctx.set_source_rgba(1, 0.85, 0.45, 0.8); ctx.fill()


def icon_cat(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgb(0.75, 0.77, 0.85)
    ctx.arc(0, 0, 60, 0, 6.3); ctx.fill()
    for sx in (-1, 1):
        ctx.move_to(sx * 30, -45); ctx.line_to(sx * 55, -90); ctx.line_to(sx * 60, -25); ctx.close_path(); ctx.fill()
    for sx in (-1, 1):
        ctx.arc(sx * 22, -5, 9, 0, 6.3); ctx.set_source_rgb(1, 0.85, 0.15); ctx.fill()
    ctx.restore()


def icon_bread(ctx, x, y, s):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgb(0.8, 0.5, 0.22); ctx.arc(-30, -25, 38, math.pi, 1.5 * math.pi + 0.3); ctx.arc(30, -25, 38, 1.5 * math.pi - 0.3, 0)
    ctx.line_to(60, 60); ctx.line_to(-60, 60); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(0.98, 0.88, 0.62); ctx.rectangle(-48, -20, 96, 72); ctx.fill()
    ctx.restore()


def bg_glow(ctx, tg, i, dark_scenes=(0, 1)):
    g = cairo.LinearGradient(0, 0, 0, H)
    if i in dark_scenes:
        g.add_color_stop_rgb(0, 0.01, 0.02, 0.06); g.add_color_stop_rgb(1, 0.05, 0.03, 0.12)
    else:
        g.add_color_stop_rgb(0, 0.04, 0.06, 0.2); g.add_color_stop_rgb(0.6, 0.1, 0.07, 0.28); g.add_color_stop_rgb(1, 0.16, 0.06, 0.26)
    ctx.set_source(g); ctx.paint()
    # rays
    if i >= 2:
        ctx.save(); ctx.translate(540, -200)
        for k in range(10):
            a = math.radians(60 + k * 6.5) + math.sin(tg * 0.4 + k) * 0.03
            ctx.move_to(0, 0); ctx.line_to(math.cos(a - 0.03) * 2600, math.sin(a - 0.03) * 2600)
            ctx.line_to(math.cos(a + 0.03) * 2600, math.sin(a + 0.03) * 2600); ctx.close_path()
            ctx.set_source_rgba(0.5, 0.8, 1.0, 0.035 + 0.02 * math.sin(tg + k)); ctx.fill()
        ctx.restore()
    # floating particles
    for k in range(34):
        x = (hrand("px", k) * W + math.sin(tg * 0.3 + k) * 30) % W
        y = (hrand("py", k) * H - tg * (12 + 30 * hrand("pv", k))) % H
        a = 0.15 + 0.25 * (0.5 + 0.5 * math.sin(tg * 1.5 + k))
        ctx.arc(x, y, 2 + 3 * hrand("pr", k), 0, 6.3); ctx.set_source_rgba(0.7, 0.9, 1.0, a); ctx.fill()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.45); g.add_color_stop_rgba(0.18, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.75, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.5)
    ctx.set_source(g); ctx.paint()

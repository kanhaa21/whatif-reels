"""Card style (owner's reference reels, 20 Nov 2026): near-black background with a soft colour glow,
a small grey kicker line over a bold white headline with one accent word, neon-bordered UI cards,
numbered step cards, a slammed stamp, and small word-by-word captions in the lower middle.
Use with "style": "card" in script.json; scenes call these helpers."""
import math
import cairo
from .lib import clamp, ease_out, ease_back, pop, rrect, text_w, hrand, W, H

UI = "Inter"
BLACK = (0.035, 0.035, 0.05)
CARD = (0.075, 0.08, 0.11)
GREY = (0.62, 0.64, 0.7)
WHT = (1, 1, 1)
RED = (1.0, 0.27, 0.3)
GRN = (0.25, 0.9, 0.45)
BLU = (0.3, 0.55, 1.0)
YEL = (1.0, 0.82, 0.2)
ORG = (1.0, 0.58, 0.15)
PUR = (0.62, 0.45, 1.0)
CAPY = 1330


def ui_font(ctx, size, bold=True, italic=False):
    ctx.select_font_face(UI, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def tw(ctx, s, size, bold=True):
    ui_font(ctx, size, bold); return ctx.text_extents(s).x_advance


def say(ctx, s, x, y, size, col=WHT, bold=True, align="c", alpha=1.0):
    """y = vertical centre of capitals"""
    ui_font(ctx, size, bold)
    w = ctx.text_extents(s).x_advance
    x0 = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    ctx.move_to(x0, y + size * 0.36); ctx.text_path(s)
    ctx.set_source_rgba(*col, alpha); ctx.fill()
    return w


def bg(ctx, tg, glow=BLU, a=0.16, gx=540, gy=900):
    ctx.set_source_rgb(*BLACK); ctx.paint()
    g = cairo.RadialGradient(gx, gy, 0, gx, gy, 900)
    g.add_color_stop_rgba(0, *glow, a); g.add_color_stop_rgba(1, *glow, 0)
    ctx.set_source(g); ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.025); ctx.set_line_width(1)
    for k in range(0, W + 1, 90):
        ctx.move_to(k, 0); ctx.line_to(k, H)
    for k in range(0, H + 1, 90):
        ctx.move_to(0, k); ctx.line_to(W, k)
    ctx.stroke()


def headline(ctx, kicker, parts, tt, y=300, size=78):
    """kicker: small grey line; parts: [(text, colour), ...] on one line, or a list of such lines.
    Pops in over 0.2 s from tt = 0."""
    if tt < 0: return
    a = clamp(tt / 0.15)
    dy = 18 * (1 - ease_out(tt / 0.25))
    lines = parts if parts and isinstance(parts[0], list) else [parts]
    if kicker:
        say(ctx, kicker, 540, y - size * 0.95 + dy, 36, GREY, bold=False, alpha=a)
    for li, ln in enumerate(lines):
        tot = sum(tw(ctx, t, size) for t, _ in ln) + 22 * (len(ln) - 1)
        x = 540 - min(tot, 1000) / 2
        sc = min(1.0, 1000 / tot)
        ctx.save(); ctx.translate(540, y + li * size * 1.12 + dy); ctx.scale(sc, sc); ctx.translate(-540, 0)
        x = 540 - tot / 2
        for t, col in ln:
            x += say(ctx, t, x, 0, size, col, align="l", alpha=a) + 22
        ctx.restore()


def card(ctx, x, y, w, h, border=BLU, tt=1.0, fill=CARD, glow=0.5, r=30, lw=4):
    """neon-bordered rounded card centred on (x, y); pops in from tt = 0"""
    if tt < 0: return 0
    s = 0.88 + 0.12 * ease_back(tt / 0.25)
    a = clamp(tt / 0.12)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    if glow > 0:
        for k in range(3):
            rrect(ctx, -w / 2 - 6 - k * 6, -h / 2 - 6 - k * 6, w + 12 + k * 12, h + 12 + k * 12, r + 6 + k * 6)
            ctx.set_source_rgba(*border, glow * a * 0.12 / (k + 1)); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, r); ctx.set_source_rgba(*fill, a); ctx.fill_preserve()
    ctx.set_source_rgba(*border, a); ctx.set_line_width(lw); ctx.stroke()
    ctx.restore()
    return s


def pill(ctx, s, x, y, tt, col=GRN, size=46, icon=None):
    """outlined pill tag ('fast hai' style): tinted fill, coloured border and text"""
    if tt < 0: return
    sc = pop(tt, 0.2)
    w = tw(ctx, s, size) + (size * 1.1 if icon else 0)
    h = size * 1.6
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    rrect(ctx, -w / 2 - 30, -h / 2, w + 60, h, 16)
    ctx.set_source_rgba(*col, 0.16); ctx.fill_preserve(); ctx.set_source_rgba(*col, 1); ctx.set_line_width(3); ctx.stroke()
    x0 = -w / 2
    if icon:
        icon(ctx, x0 + size * 0.4, 0, size * 0.75, col); x0 += size * 1.1
    say(ctx, s, x0, 0, size, col, align="l")
    ctx.restore()


def numcard(ctx, x, y, w, h, n, label, tt, on=False, col=YEL, icon=None, done=False):
    """'01' step card: big outlined number top-left, label bottom-left, highlighted border when on"""
    if tt < 0: return
    card(ctx, x, y, w, h, col if on else (0.22, 0.23, 0.3), tt, glow=0.8 if on else 0, r=24, lw=4 if on else 2)
    a = clamp(tt / 0.15)
    ctx.save(); ctx.translate(x - w / 2 + 26, y - h / 2 + 62)
    ui_font(ctx, 78, True); ctx.move_to(0, 28); ctx.text_path(f"{n:02d}")
    ctx.set_source_rgba(*(col if on else GREY), a); ctx.set_line_width(2.5); ctx.stroke()
    ctx.restore()
    if icon:
        icon(ctx, x + w / 2 - 60, y - h / 2 + 62, 52, col if on else GREY)
    lines = label.split("\n")
    for k, ln in enumerate(lines):
        say(ctx, ln, x - w / 2 + 26, y + h / 2 - 44 - (len(lines) - 1 - k) * 50, 42, WHT, align="l", alpha=a)
    if done:
        ctx.arc(x + w / 2 - 40, y + h / 2 - 44, 22, 0, 6.3); ctx.set_source_rgba(*GRN, a); ctx.fill()
        tick(ctx, x + w / 2 - 40, y + h / 2 - 44, 24, BLACK)


def stamp(ctx, s, x, y, tt, col=RED, size=110, rot=-0.13):
    """slammed outline stamp ('REJECTED' style)"""
    if tt < 0: return
    sc = 1.9 - 0.9 * ease_out(tt / 0.14)
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc)
    w = tw(ctx, s, size)
    rrect(ctx, -w / 2 - 36, -size * 0.66, w + 72, size * 1.32, 18)
    ctx.set_source_rgba(*col, 0.92); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(6); ctx.stroke()
    say(ctx, s, 0, 0, size, WHT)
    ctx.restore()


def dim(ctx, a):
    ctx.set_source_rgba(0, 0, 0, a); ctx.paint()


# ---------------------------------------------------------------- small icons (centre x, y, size s)
def tick(ctx, x, y, s, col):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_line_width(s * 0.16)
    ctx.move_to(x - s * 0.32, y); ctx.line_to(x - s * 0.08, y + s * 0.25); ctx.line_to(x + s * 0.35, y - s * 0.28)
    ctx.set_source_rgb(*col); ctx.stroke()


def xmark(ctx, x, y, s, col):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(s * 0.16)
    ctx.move_to(x - s * 0.3, y - s * 0.3); ctx.line_to(x + s * 0.3, y + s * 0.3)
    ctx.move_to(x + s * 0.3, y - s * 0.3); ctx.line_to(x - s * 0.3, y + s * 0.3)
    ctx.set_source_rgb(*col); ctx.stroke()


def bolt(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(10, -50); ctx.line_to(-30, 8); ctx.line_to(-2, 8); ctx.line_to(-12, 50); ctx.line_to(30, -10); ctx.line_to(2, -10); ctx.line_to(14, -50)
    ctx.close_path(); ctx.set_source_rgb(*col); ctx.fill(); ctx.restore()


def bell(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(-36, 26); ctx.curve_to(-30, 10, -34, -40, 0, -44); ctx.curve_to(34, -40, 30, 10, 36, 26); ctx.close_path()
    ctx.set_source_rgb(*col); ctx.fill()
    ctx.rectangle(-44, 24, 88, 10); ctx.fill()
    ctx.arc(0, 42, 10, 0, 6.3); ctx.fill(); ctx.restore()


def clock(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.arc(0, 0, 42, 0, 6.3); ctx.set_source_rgb(*col); ctx.set_line_width(9); ctx.stroke()
    ctx.move_to(0, 0); ctx.line_to(0, -26); ctx.move_to(0, 0); ctx.line_to(18, 10); ctx.stroke(); ctx.restore()


def door(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    rrect(ctx, -30, -46, 60, 92, 6); ctx.set_source_rgb(*col); ctx.set_line_width(9); ctx.stroke()
    ctx.move_to(0, -40); ctx.line_to(0, 40); ctx.stroke(); ctx.restore()


def cable_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col); ctx.set_line_width(8)
    for k in range(4):
        ctx.move_to(-30 + k * 20, -46); ctx.line_to(-30 + k * 20, 46)
    ctx.stroke(); ctx.restore()


def brake_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col)
    ctx.rectangle(-6, -48, 12, 96); ctx.fill()
    for sx in (-1, 1):
        ctx.move_to(sx * 12, -24); ctx.line_to(sx * 40, -34); ctx.line_to(sx * 40, 34); ctx.line_to(sx * 12, 24); ctx.close_path(); ctx.fill()
    ctx.restore()


def person_icon(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100); ctx.set_source_rgb(*col)
    ctx.arc(0, -22, 20, 0, 6.3); ctx.fill()
    ctx.move_to(-36, 46); ctx.curve_to(-36, 0, 36, 0, 36, 46); ctx.close_path(); ctx.fill(); ctx.restore()


def sparks(ctx, x, y, t, n=14, seed="sk", dirx=1, col=ORG):
    for k in range(n):
        ph = (t * (1.8 + hrand(seed, k)) + hrand(seed + "o", k)) % 1
        vx = dirx * (60 + 220 * hrand(seed + "x", k)); vy = -140 + 280 * hrand(seed + "y", k)
        px = x + vx * ph; py = y + vy * ph + 300 * ph * ph
        ctx.move_to(px, py); ctx.line_to(px - vx * 0.05, py - vy * 0.05)
        ctx.set_source_rgba(*col, 1 - ph); ctx.set_line_width(4); ctx.stroke()


# ---------------------------------------------------------------- captions and end card
def draw_captions(ctx, tg, chunks, cy=CAPY):
    """2-3 words at a time, white, the word being spoken in yellow, upcoming words grey"""
    cur = next((c for c in chunks if c["s"] <= tg < c["e"]), None)
    if not cur: return
    words = [w["w"] for w in cur["words"]]
    size, spc = 64, 18
    widths = [tw(ctx, w, size) for w in words]
    tot = sum(widths) + spc * (len(words) - 1)
    sc = min(1.0, 940 / tot)
    a = clamp((tg - cur["s"]) / 0.08)
    ctx.save(); ctx.translate(540, cy); ctx.scale(sc, sc)
    x = -tot / 2
    for w, wd, wi in zip(words, widths, cur["words"]):
        active = wi["s"] - 0.03 <= tg < wi["e"] + 0.02 or (wi is cur["words"][-1] and tg >= wi["s"])
        said = tg >= wi["s"] - 0.03
        col = YEL if active else (WHT if said else GREY)
        ctx.save(); ctx.translate(x, 0)
        ui_font(ctx, size, True); ctx.move_to(3, size * 0.36 + 4); ctx.text_path(w); ctx.set_source_rgba(0, 0, 0, 0.6 * a); ctx.fill()
        say(ctx, w, 0, 0, size, col, align="l", alpha=a if said else 0.75 * a)
        ctx.restore()
        x += wd + spc
    ctx.restore()


def draw_end_cta(ctx, tg, txt, voice_end):
    if not txt: return
    t0 = voice_end - 2.6
    if tg < t0: return
    pill(ctx, txt, 540, 1200, tg - t0, GRN, 40, icon=_plane)


def _plane(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s / 100, s / 100)
    ctx.move_to(-48, 4); ctx.line_to(50, -40); ctx.line_to(16, 46); ctx.line_to(4, 16); ctx.close_path()
    ctx.set_source_rgb(*col); ctx.fill(); ctx.restore()

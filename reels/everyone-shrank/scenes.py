"""Scenes for "What if everyone shrank?" (v1 trimmed). One function per voice line.
Injected by reelkit.make before this runs: wt(line_i, word) -> scene-local word time, TL, SCRIPT."""
import math
import cairo
from reelkit.lib import *  # noqa: F401,F403

BG = bg_glow                      # background drawn under every frame
MUSIC = {"beat_from_scene": 3, "bpm": 112}   # drone + heartbeat until "Science time", then the plucked beat

def s0(ctx, tg, tl, T):
    tlight = wt(0, "light")
    # stars
    for k in range(80):
        a = 0.3 + 0.5 * (0.5 + 0.5 * math.sin(tg * 2 + k * 1.3))
        ctx.arc(hrand("stx", k) * W, hrand("sty", k) * H, 1.2 + 2 * hrand("sts", k), 0, 6.3)
        ctx.set_source_rgba(1, 1, 1, a); ctx.fill()
    zoom = 1 + 0.08 * tl
    ctx.save(); ctx.translate(540, 900); ctx.scale(zoom, zoom); ctx.translate(-540, -900)
    earth(ctx, 540, 960, 300, tg)
    # beam
    f = ease_out((tl - tlight + 0.3) / 0.5)
    if f > 0:
        flick = 0.85 + 0.15 * math.sin(tl * 40)
        g = cairo.LinearGradient(0, 0, 0, 960)
        g.add_color_stop_rgba(0, *CYN, 0.0); g.add_color_stop_rgba(0.4, *CYN, 0.35 * f * flick); g.add_color_stop_rgba(1, *CYN, 0.7 * f * flick)
        ctx.move_to(540 - 40, -50); ctx.line_to(540 + 40, -50); ctx.line_to(540 + 330 * f, 960); ctx.line_to(540 - 330 * f, 960); ctx.close_path()
        ctx.set_source(g); ctx.fill()
        glow_circle(ctx, 540, 900, 520 * f, CYN, 0.5 * f)
        sparkles(ctx, 540, 900, 380, tl, 18, CYN)
    ctx.restore()
    if tl > T - 0.25:
        ctx.set_source_rgba(0.7, 0.95, 1, (tl - (T - 0.25)) / 0.25 * 0.9); ctx.paint()


def s1(ctx, tg, tl, T):
    ts = wt(1, "shrinks"); tp = wt(1, "to")
    if tl < tp - 0.1:
        # crowd of normal people, then shrink
        f = ease_io((tl - ts + 0.1) / 0.9)
        hgt = 520 * (1 - 0.9 * f)
        if tl < 0.25:
            ctx.set_source_rgba(0.7, 0.95, 1, 0.9 * (1 - tl / 0.25)); ctx.paint()
        for k, (dx, sh) in enumerate([(-300, 0), (300, 2), (0, 1)]):
            x = 540 + dx * (1 - 0.6 * f); y = 1200
            hh = hgt * (0.85 if k < 2 else 1.0)
            if f > 0:
                glow_circle(ctx, x, y - hh / 2, hh * 0.9 + 60, CYN, 0.45 * (1 - f * 0.5))
            person(ctx, x, y, hh, SHIRTS[sh], "shock" if f > 0.1 else "smile", "down", tl)
        if f > 0: sparkles(ctx, 540, 1100, 350, tl, 16, CYN)
        # ruler
        lbl = "1.7 M" if f < 0.5 else "17 CM"
        chip(ctx, lbl, 900, 600 + (1 - f) * 0, 54, YEL if f >= 0.5 else WHT, (0, 0, 0))
        if f > 0: text(ctx, "÷10", 900, 690, 48, CYN, SANS)
    else:
        tt = tl - (tp - 0.1)
        if tt < 0.12:
            ctx.set_source_rgba(1, 1, 1, 0.4 * (1 - tt / 0.12)); ctx.paint()
        s = pop(tt, 0.25)
        ctx.save(); ctx.translate(540, 1220); ctx.scale(s, s); ctx.translate(-540, -1220)
        pencil(ctx, 700, 1220, 760)
        person(ctx, 420, 1220, 690, SHIRTS[1], "smile", "wave", tl)
        ctx.restore()
        # height bracket
        a = ease_out((tt - 0.3) / 0.2)
        if a > 0:
            ctx.set_source_rgba(*YEL, a); ctx.set_line_width(5)
            ctx.move_to(170, 530); ctx.line_to(200, 530); ctx.move_to(185, 530); ctx.line_to(185, 1220)
            ctx.move_to(170, 1220); ctx.line_to(200, 1220); ctx.stroke()
            ctx.save(); ctx.translate(140, 875); ctx.rotate(-math.pi / 2)
            text(ctx, "17 CM TALL", 0, 0, 48, YEL, alpha=a)
            ctx.restore()


def s2(ctx, tg, tl, T):
    sh = 10 * (0.6 + 0.4 * math.sin(tl * 30))
    ctx.save(); ctx.translate(math.sin(tl * 37) * sh, math.cos(tl * 29) * sh * 0.6)
    s = pop(tl, 0.2)
    ctx.save(); ctx.translate(540, 1250); ctx.scale(s, s)
    person(ctx, 0, 0, 820, SHIRTS[1], "shock", "cheeks", tl)
    ctx.restore()
    tw = wt(2, "Why")
    if tl > tw - 0.05:
        sc = pop(tl - tw + 0.05, 0.18)
        ctx.save(); ctx.translate(820, 620); ctx.scale(sc, sc); ctx.rotate(0.12)
        ctx.arc(0, 0, 120, 0, 6.3); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        ctx.move_to(-70, 70); ctx.line_to(-150, 150); ctx.line_to(-20, 100); ctx.close_path(); ctx.fill()
        text(ctx, "?!", 0, 0, 130, PNK, shadow=False)
        ctx.restore()
    ctx.restore()
    popchip(ctx, "HELIUM VOICE", 260, 1150, tl - 0.15, PNK, WHT, 52)


def s3(ctx, tg, tl, T):
    tsci = wt(3, "Science")
    # atom
    cx, cy = 540, 860
    ctx.save(); ctx.translate(cx, cy); s = pop(tl, 0.22); ctx.scale(s, s)
    for k in range(3):
        ctx.save(); ctx.rotate(k * math.pi / 3); ctx.scale(1, 0.38)
        ctx.arc(0, 0, 300, 0, 6.3); ctx.restore()
        ctx.set_source_rgba(*CYN, 0.9); ctx.set_line_width(8); ctx.stroke()
        a = tl * 4 + k * 2.1
        ex, ey = math.cos(a) * 300, math.sin(a) * 300 * 0.38
        c, s_ = math.cos(k * math.pi / 3), math.sin(k * math.pi / 3)
        glow_circle(ctx, ex * c - ey * s_, ex * s_ + ey * c, 50, YEL, 0.9)
    glow_circle(ctx, 0, 0, 120, PNK, 0.8)
    ctx.arc(0, 0, 50, 0, 6.3); ctx.set_source_rgb(*PNK); ctx.fill()
    ctx.restore()
    stamp(ctx, "SCIENCE TIME", 540, 860, tl - tsci + 0.05, YEL, 110, -0.1, (0, 0, 0))


def s4(ctx, tg, tl, T):
    ta = wt(4, "inside")
    # airport top view
    x0, y0, w, h = 110, 520, 860, 640
    a = ease_out(tl / 0.25)
    rrect(ctx, x0, y0, w, h, 30); ctx.set_source_rgba(0.12, 0.3, 0.18, a); ctx.fill()
    for k, (rx, ry, rw, rh, rot) in enumerate([(160, 640, 760, 70, 0), (160, 1020, 760, 70, 0), (300, 560, 70, 580, 0.0)]):
        rrect(ctx, rx, ry, rw, rh, 10); ctx.set_source_rgba(0.25, 0.26, 0.3, a); ctx.fill()
    for k in range(13):
        ctx.rectangle(190 + k * 56, 672, 28, 6); ctx.rectangle(190 + k * 56, 1052, 28, 6)
    ctx.set_source_rgba(1, 1, 1, 0.8 * a); ctx.fill()
    rrect(ctx, 520, 760, 330, 200, 20); ctx.set_source_rgba(0.75, 0.78, 0.85, a); ctx.fill()
    text(ctx, "T3", 685, 860, 60, (0.2, 0.22, 0.3), shadow=False, alpha=a)
    # plane on runway
    px = 150 + ((tl * 260) % 900)
    ctx.save(); ctx.translate(px, 675)
    ctx.set_source_rgb(1, 1, 1)
    rrect(ctx, -60, -9, 120, 18, 9); ctx.fill()
    ctx.move_to(-5, 0); ctx.line_to(-25, -45); ctx.line_to(10, 0); ctx.line_to(-25, 45); ctx.close_path(); ctx.fill()
    ctx.move_to(-55, 0); ctx.line_to(-65, -18); ctx.line_to(-45, 0); ctx.line_to(-65, 18); ctx.close_path(); ctx.fill()
    ctx.restore()
    # crowd dots filling
    fill = ease_io((tl - 0.3) / (ta + 0.6))
    n = int(1400 * fill)
    for k in range(n):
        x = x0 + 12 + hrand("cx", k) * (w - 24); y = y0 + 12 + hrand("cy", k) * (h - 24)
        ctx.arc(x, y, 5.5, 0, 6.3); ctx.set_source_rgb(*SHIRTS[k % 6]); ctx.fill()
    # counter
    v = int(8_000_000_000 * ease_out((tl - 0.2) / 1.6))
    chip(ctx, f"{v:,}", 540, 460 + 0, 58, WHT, (0, 0, 0))
    if tl > ta - 0.05:
        popchip(ctx, "DELHI AIRPORT ≈ 20 KM²", 540, 1215, tl - ta + 0.05, CYN, (0, 0, 0), 46)


def s5(ctx, tg, tl, T):
    tf = wt(5, "Fall"); tt_ = wt(5, "Tiny"); tsl = wt(5, "slower"); tso = wt(5, "softer")
    if tl < tf - 0.1:
        # balance scale
        s = pop(tl, 0.22)
        ctx.save(); ctx.translate(540, 900); ctx.scale(s, s)
        tilt = math.sin(tl * 3) * 0.06 * math.exp(-tl * 0.8)
        ctx.set_source_rgb(0.85, 0.75, 0.4); ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(0, 300); ctx.line_to(0, -120); ctx.stroke()
        ctx.move_to(-160, 300); ctx.line_to(160, 300); ctx.stroke()
        ctx.save(); ctx.translate(0, -120); ctx.rotate(tilt)
        ctx.move_to(-300, 0); ctx.line_to(300, 0); ctx.stroke()
        for sx in (-300, 300):
            ctx.set_line_width(4); ctx.move_to(sx, 0); ctx.line_to(sx - 80, 150); ctx.move_to(sx, 0); ctx.line_to(sx + 80, 150); ctx.stroke()
            ctx.save(); ctx.translate(sx, 150); ctx.rotate(-tilt)
            ctx.scale(1, 0.25); ctx.arc(0, 0, 110, 0, math.pi); ctx.restore()
            ctx.fill()
        ctx.restore()
        ctx.restore()
        tilt_y = math.sin(tilt) * 300
        egg(ctx, 240, 900 + 30 - 75 + tilt_y * s * -1, 70 * s)
        person(ctx, 840, 900 + 30 + tilt_y * s, 230 * s, SHIRTS[0], "smile", "down", tl)
        popchip(ctx, "YOU ≈ 60 G", 540, 1200, tl - 1.0, YEL)
    else:
        # bed + falling
        tt = tl - (tf - 0.1)
        rrect(ctx, 90, 700, 520, 140, 20); ctx.set_source_rgb(0.95, 0.95, 1.0); ctx.fill()
        rrect(ctx, 90, 830, 520, 120, 10); ctx.set_source_rgb(0.45, 0.3, 0.65); ctx.fill()
        rrect(ctx, 110, 650, 200, 70, 30); ctx.set_source_rgb(0.85, 0.88, 1.0); ctx.fill()
        ctx.rectangle(100, 940, 30, 240); ctx.rectangle(570, 940, 30, 240); ctx.set_source_rgb(0.35, 0.22, 0.5); ctx.fill()
        ctx.rectangle(60, 1180, 960, 10); ctx.set_source_rgba(1, 1, 1, 0.3); ctx.fill()
        # fall path: walk off edge at t=0.3, slow fall
        fall_t = tt - 0.4
        if fall_t < 0:
            x, y = 560 + 60 * ease_io(tt / 0.4), 700; expr = "smile"; arms = "down"
        else:
            x = 620 + 140 * ease_out(fall_t / 1.3)
            prog = clamp(fall_t / 1.3)
            y = 700 + 480 * prog ** 1.4
            expr = "shock" if prog < 1 else "smile"; arms = "up" if prog < 1 else "wave"
            if prog >= 1:
                y = 1180 - 30 * abs(math.sin((fall_t - 1.3) * 7)) * math.exp(-(fall_t - 1.3) * 3)
            else:
                for k in range(5):
                    ctx.move_to(x - 40 + k * 20, y - 220 - k * 6); ctx.line_to(x - 40 + k * 20, y - 300)
                ctx.set_source_rgba(1, 1, 1, 0.4); ctx.set_line_width(4); ctx.stroke()
        person(ctx, x, y, 170, SHIRTS[0], expr, arms, tl)
        popchip(ctx, "FALLS SLOWER", 300, 1240, tl - tsl + 0.05, CYN, (0, 0, 0), 44)
        popchip(ctx, "LANDS SOFTER", 760, 1240, tl - tso + 0.05, YEL, (0, 0, 0), 44)


def s6(ctx, tg, tl, T):
    te = wt(6, "elephant"); tw_ = wt(6, "waiting")
    rise = ease_out((tl - 0.3) / 1.2)
    narrow = ease_io((tl - tw_ + 0.1) / 0.4)
    zoom = 1 + 0.12 * ease_io((tl - tw_) / 2.0)
    ctx.save(); ctx.translate(540, 1000); ctx.scale(zoom, zoom); ctx.translate(-540, -1000)
    cat_head(ctx, 540, 1400 - 520 * rise, 1.15, tl, narrow)
    shake = 4 * math.sin(tl * 45)
    person(ctx, 540 + shake, 1260, 150, SHIRTS[4], "shock" if rise > 0.3 else "smile", "up" if rise > 0.3 else "down", tl, look=0)
    ctx.restore()
    if narrow > 0:
        g = cairo.RadialGradient(540, 960, 300, 540, 960, 1150)
        g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.6, 0, 0.05, 0.6 * narrow)
        ctx.set_source(g); ctx.paint()
    popchip(ctx, "CAT = ELEPHANT", 540, 470, tl - te + 0.05, RED, WHT, 56)


def s7(ctx, tg, tl, T):
    th = wt(7, "hungry"); thm = wt(7, "hamster"); tp = wt(7, "pizza"); tmo = wt(7, "months")
    if tl < thm - 0.1:
        sh = math.sin(tl * 50) * 4
        person(ctx, 420 + sh, 1180, 520, SHIRTS[2], "worry", "down", tl)
        # heat waves leaving
        for k in range(6):
            ph = (tl * 0.9 + k / 6) % 1
            x = 300 + k * 50; y = 640 - ph * 200
            ctx.move_to(x, y)
            for j in range(8):
                ctx.line_to(x + math.sin(j * 1.2 + tl * 6) * 14, y - j * 14)
            ctx.set_source_rgba(1, 0.4, 0.2, 0.8 * (1 - ph)); ctx.set_line_width(6); ctx.stroke()
        # thermometer
        tx, ty = 830, 620
        lvl = 1 - 0.65 * ease_io(tl / 1.6)
        rrect(ctx, tx - 30, ty, 60, 420, 30); ctx.set_source_rgb(0.9, 0.92, 1); ctx.fill()
        rrect(ctx, tx - 16, ty + 14 + 380 * (1 - lvl), 32, 380 * lvl, 16); ctx.set_source_rgb(*CYN if lvl < 0.6 else RED); ctx.fill()
        ctx.arc(tx, ty + 440, 56, 0, 6.3); ctx.set_source_rgb(*(CYN if lvl < 0.6 else RED)); ctx.fill()
        popchip(ctx, "ALWAYS HUNGRY", 540, 470, tl - th + 0.05, YEL)
    elif tl < tp - 0.4:
        tt = tl - (thm - 0.1)
        s = pop(tt, 0.2)
        ctx.save(); ctx.translate(540, 1200); ctx.scale(s, s)
        person(ctx, 0, 0, 760, SHIRTS[2], "cheeks", "down", tl)
        ctx.restore()
        popchip(ctx, "HAMSTER MODE", 540, 470, tt - 0.1, PNK, WHT, 56)
    else:
        tt = tl - (tp - 0.4)
        s = pop(tt, 0.25)
        ctx.save(); ctx.translate(540, 860); ctx.scale(s, s)
        glow_circle(ctx, 0, 0, 420, YEL, 0.35)
        pizza(ctx, 0, 0, 300, tl)
        ctx.restore()
        person(ctx, 820, 1200, 150, SHIRTS[2], "smile", "up", tl)
        if tl > tmo - 0.1:
            days = int(min(70, (tl - tmo + 0.1) * 70))
            popchip(ctx, f"FOOD FOR {days}+ DAYS", 540, 470, tl - tmo + 0.1, GRN, (0, 0, 0), 52)


def s8(ctx, tg, tl, T):
    tc = wt(8, "cardio"); ttx = wt(8, "Texting")
    s = pop(tl, 0.25)
    ctx.save(); ctx.translate(540, 900); ctx.scale(s * 0.86, s * 0.86)
    rrect(ctx, -270, -420, 540, 840, 60); ctx.set_source_rgb(0.08, 0.08, 0.1); ctx.fill()
    rrect(ctx, -250, -400, 500, 800, 46)
    g = cairo.LinearGradient(0, -400, 0, 400); g.add_color_stop_rgb(0, 0.25, 0.35, 0.9); g.add_color_stop_rgb(1, 0.6, 0.3, 0.8)
    ctx.set_source(g); ctx.fill()
    rrect(ctx, -60, -390, 120, 30, 15); ctx.set_source_rgb(0.05, 0.05, 0.07); ctx.fill()
    # chat bubbles
    rrect(ctx, -210, -300, 280, 70, 26); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    text(ctx, "u up?", -190, -265, 36, (0.1, 0.1, 0.2), SANS, align="l", shadow=False)
    # keyboard
    rrect(ctx, -250, 60, 500, 340, 30); ctx.set_source_rgb(0.85, 0.86, 0.9); ctx.fill()
    for r in range(3):
        for c in range(7):
            rrect(ctx, -230 + c * 66, 80 + r * 92, 56, 76, 12); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()
    # running person on keys
    run = (tl * 0.55) % 1
    x = 370 + 340 * (0.5 - 0.5 * math.cos(run * 2 * math.pi))
    hop = abs(math.sin(tl * 9)) * 25
    person(ctx, x, 1150 - hop, 170, SHIRTS[3], "worry", "run", tl, look=1 if math.sin(run * 2 * math.pi) > 0 else -1)
    for k in range(3):
        ph = (tl * 2 + k / 3) % 1
        ctx.arc(x + 30 + k * 8, 960 + ph * 50, 7, 0, 6.3); ctx.set_source_rgba(0.5, 0.8, 1, 1 - ph); ctx.fill()
    popchip(ctx, "60-INCH SCREEN", 540, 470, tl - 0.5, CYN, (0, 0, 0), 50)
    stamp(ctx, "CARDIO", 540, 760, tl - tc + 0.05, RED, 120)


def s9(ctx, tg, tl, T):
    tsb = wt(9, "shoebox"); tb = wt(9, "1BHK"); tst = wt(9, "Still"); tfo = wt(9, "Follow")
    s = pop(tl - tsb + 0.2, 0.25)
    ctx.save(); ctx.translate(540, 900); ctx.scale(s, s)
    # shoebox
    ctx.move_to(-360, -120); ctx.line_to(-300, -220); ctx.line_to(400, -220); ctx.line_to(360, -120); ctx.close_path()
    ctx.set_source_rgb(0.75, 0.5, 0.3); ctx.fill()
    rrect(ctx, -380, -140, 760, 70, 10); ctx.set_source_rgb(0.85, 0.6, 0.38); ctx.fill()
    ctx.rectangle(-360, -70, 720, 340); ctx.set_source_rgb(0.7, 0.47, 0.28); ctx.fill()
    text(ctx, "SHOES CO.", 160, 210, 40, (0.5, 0.32, 0.18), shadow=False)
    # door & window
    rrect(ctx, -280, 30, 140, 240, 12); ctx.set_source_rgb(0.3, 0.18, 0.1); ctx.fill()
    ctx.arc(-170, 160, 8, 0, 6.3); ctx.set_source_rgb(1, 0.85, 0.3); ctx.fill()
    rrect(ctx, -60, 0, 180, 140, 10); ctx.set_source_rgb(1, 0.9, 0.5); ctx.fill()
    ctx.set_source_rgb(0.3, 0.18, 0.1); ctx.set_line_width(8)
    ctx.move_to(30, 0); ctx.line_to(30, 140); ctx.move_to(-60, 70); ctx.line_to(120, 70); ctx.stroke()
    ctx.restore()
    if s > 0.01:
        person(ctx, 540 - 160 * s + 0, 900 + 270 * s, 230 * s, SHIRTS[0], "smile", "wave", tl)
    follow = tl > tfo - 0.05
    if tl > tb - 0.05 and not follow:
        popchip(ctx, "1BHK • MUMBAI", 540, 470, tl - tb + 0.05, WHT, (0, 0, 0), 54)
        tt = tl - tb - 0.4
        if tt > 0:
            sc = pop(tt, 0.2)
            ctx.save(); ctx.translate(850, 640); ctx.rotate(0.15); ctx.scale(sc, sc)
            rrect(ctx, -150, -55, 300, 110, 18); ctx.set_source_rgb(*YEL); ctx.fill()
            text(ctx, "₹45,000/mo", 0, 0, 48, (0, 0, 0), SANS, shadow=False)
            ctx.restore()
    if not follow: stamp(ctx, "STILL OVERPRICED", 540, 1000, tl - tst + 0.05, RED, 92)
    if tl > tfo - 0.05:
        tt = tl - tfo + 0.05
        ctx.set_source_rgba(0.02, 0.02, 0.08, 0.8 * ease_out(tt / 0.2)); ctx.paint()
        sc = pop(tt, 0.25) * (1 + 0.05 * math.sin(tt * 8))
        ctx.save(); ctx.translate(540, 900); ctx.scale(sc, sc)
        g = cairo.LinearGradient(-380, 0, 380, 0)
        g.add_color_stop_rgb(0, 0.15, 0.55, 1.0); g.add_color_stop_rgb(1, 0.95, 0.25, 0.6)
        rrect(ctx, -380, -90, 760, 180, 90); ctx.set_source(g); ctx.fill()
        text(ctx, "FOLLOW", 0, 0, 110, WHT, shadow=False)
        ctx.restore()
        text(ctx, "FOR MORE WHAT-IFS", 540, 1080, 64, WHT, stroke=5, alpha=ease_out((tt - 0.2) / 0.2))


SCENES = [s0, s1, s2, s3, s4, s5, s6, s7, s8, s9]


def sfx(A):
    """Sound effects; A is reelkit.audio.Mixer. A.W(i, word) = absolute word time, A.S(i) = scene start."""
    for k in range(int(A.S(2) / 0.8)):
        A.thump(0.4 + k * 0.8, 0.5, 50)                       # heartbeat under the hook
    A.ding(A.W(0, "light") - 0.3, 0.06, 220, 2.0)              # beam hum
    A.zap_down(A.W(1, "shrinks") - 0.05)
    for k in range(8):
        A.ding(A.W(1, "shrinks") + 0.1 + k * 0.09, 0.03, 1500 + 300 * k)
    A.boing(A.S(2), 0.25)                                     # chipmunk voice
    A.ding(A.W(3, "Science"), 0.18, 1318.5)
    A.pop(A.W(4, "inside"), 0.3)
    A.boing(A.W(5, "Fall") + 0.3, 0.08, 900, 1.1)
    A.thump(A.W(5, "Fall") + 1.45, 0.4, 120)
    A.growl(A.W(6, "elephant") - 0.2, 0.6)
    A.thump(A.W(6, "waiting") - 0.05, 0.6, 45)
    A.ding(A.W(7, "pizza"), 0.12, 1568)
    A.thump(A.W(8, "cardio") - 0.02, 0.5, 70)
    tb = A.W(9, "1BHK") + 0.4
    A.ding(tb, 0.08, 2093); A.ding(tb + 0.07, 0.08, 2637)
    A.scratch(A.W(9, "Still") - 0.12, 0.3)
    A.music_level(A.W(9, "Still") - 0.12, A.W(9, "Still") + 1.1, 0.25)
    A.pop(A.W(9, "Follow"), 0.35)
    for k, m in enumerate((79, 84, 88)):
        A.ding(A.W(9, "Follow") + 0.1 + k * 0.1, 0.07, A.note(m))

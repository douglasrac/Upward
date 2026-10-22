"""Monta a fachada fechada de uma loja a partir de uma especificacao (veja stores.py)."""
import math
import random

from draw import (Pen, blinds, col, door_handle, easel_closed, glass, hanging_closed, neon_closed,
                  placard_closed, reflections, rolling_shutter, security_grille, sidewalk, wall)
from items import ITEMS, lantern, pot_plant, tv

FLOOR = 300          # altura de um andar na imagem
WALK = 22            # altura da calcada


# ------------------------------------------------------------------ conteudo das vitrines

def fill_row(p, x0, x1, base, h, names, rnd, gap=6):
    """Enfileira itens (sorteados de names) entre x0 e x1, com o pe em base."""
    x = x0 + gap
    while True:
        name = rnd.choice(names)
        wf, fn = ITEMS[name]
        w = wf * h
        if x + w > x1 - gap:
            break
        fn(p, x + w / 2, base, h, rnd)
        x += w + gap


def shelf(p, x0, x1, y, color=(70, 52, 40)):
    p.rect(x0 + 3, y, x1 - 3, y + 4, fill=col(color))


def retail_display(p, x0, y0, x1, y1, spec, rnd):
    """Vitrine de loja: prateleiras com produtos, ou expositores no chao."""
    names = spec["items"]
    mode = spec.get("display", "shelves")
    h = y1 - y0
    if mode == "floor":  # itens grandes no chao (sofa, bicicleta, arara...)
        fill_row(p, x0, x1, y1 - 4, h * 0.58, names, rnd, gap=10)
    elif mode == "racks":  # arara alta + itens no chao
        fill_row(p, x0, x1, y1 - 4, h * 0.62, names, rnd, gap=4)
    else:
        rows = spec.get("shelves", 2)
        step = (h - 10) / rows
        for i in range(rows):
            base = y0 + 8 + step * (i + 1) - 4
            shelf(p, x0, x1, base, spec.get("shelf_color", (70, 52, 40)))
            fill_row(p, x0, x1, base, step * 0.72, names, rnd)


def chairs_on_table(p, cx, base, rnd, wood=(150, 110, 74), cloth=None):
    """Mesa com as cadeiras viradas em cima: sinal classico de restaurante fechado."""
    top = base - 34
    p.rect(cx - 2, top, cx + 2, base, fill=col(wood, 0.7))
    p.rect(cx - 12, base - 3, cx + 12, base, fill=col(wood, 0.7))
    p.rect(cx - 22, top - 3, cx + 22, top, fill=col(wood))
    if cloth:  # toalha caindo pelos lados
        p.poly([(cx - 24, top - 4), (cx + 24, top - 4), (cx + 26, top + 14), (cx - 26, top + 14)], fill=col(cloth))
    for side in (-1, 1):
        sx = cx + side * 11
        p.rect(sx - 10, top - 7, sx + 10, top - 3, fill=col(wood, 0.9))
        p.line(sx - 8, top - 7, sx - 8, top - 26, col(wood, 0.8), 2)
        p.line(sx + 8, top - 7, sx + 8, top - 26, col(wood, 0.8), 2)


def booth(p, cx, base, rnd, color=(160, 40, 40)):
    p.rect(cx - 40, base - 42, cx - 28, base, fill=col(color), radius=3)
    p.rect(cx + 28, base - 42, cx + 40, base, fill=col(color), radius=3)
    p.rect(cx - 28, base - 22, cx + 28, base - 18, fill=(200, 200, 205, 255))
    p.rect(cx - 2, base - 18, cx + 2, base, fill=(150, 150, 156, 255))


def stool(p, cx, base, color):
    p.rect(cx - 1, base - 26, cx + 1, base, fill=(150, 150, 156, 255))
    p.ellipse(cx - 8, base - 30, cx + 8, base - 24, fill=col(color))


def wall_decor(p, x0, y0, x1, spec, rnd):
    """Algo na parede do fundo do salao, variando de vitrine para vitrine."""
    cx = (x0 + x1) / 2 + rnd.uniform(-20, 20)
    kind = rnd.choice(spec.get("decor", ["frame", "frame", "mirror", "clock", "shelf", "plant"]))
    if kind == "frame":
        n = rnd.choice([1, 2, 3])
        for i in range(n):
            fx = cx + (i - (n - 1) / 2) * 34
            w, h = rnd.choice([(22, 28), (26, 20), (18, 24)])
            p.rect(fx - w / 2 - 3, y0 + 14, fx + w / 2 + 3, y0 + 20 + h, fill=col(rnd.choice([(150, 120, 60), (40, 40, 44),
                                                                                              (230, 230, 225)])))
            p.rect(fx - w / 2, y0 + 17, fx + w / 2, y0 + 17 + h, fill=col(rnd.choice([(90, 120, 150), (160, 90, 70),
                                                                                         (100, 140, 90), (200, 170, 110)])))
    elif kind == "mirror":
        p.ellipse(cx - 26, y0 + 10, cx + 26, y0 + 50, fill=(200, 170, 100, 255))
        p.ellipse(cx - 22, y0 + 13, cx + 22, y0 + 47, fill=(110, 130, 150, 255))
    elif kind == "clock":
        p.circle(cx, y0 + 30, 16, fill=(235, 230, 220, 255), outline=(60, 50, 40, 255), width=3)
        p.line(cx, y0 + 30, cx, y0 + 19, (30, 30, 30, 255), 2)
        p.line(cx, y0 + 30, cx + 8, y0 + 32, (30, 30, 30, 255), 2)
    elif kind == "shelf":
        shelf(p, cx - 50, cx + 50, y0 + 40, (90, 66, 46))
        fill_row(p, cx - 50, cx + 50, y0 + 40, 22, spec.get("shelf_items", ["bottle", "pot_plant", "cup"]), rnd)
    elif kind == "plant":
        pot_plant(p, cx, y0 + 52, 44, rnd)
    elif kind == "lantern":
        lantern(p, cx, y0 + 4, 34, rnd, spec.get("lantern_color", (200, 50, 40)))
    elif kind == "tv":  # TV de bar esportivo presa na parede
        p.rect(cx - 2, y0 + 4, cx + 2, y0 + 12, fill=(50, 50, 54, 255))
        tv(p, cx, y0 + 52, 40, rnd)
    elif kind == "pennant":  # bandeirolas (papel picado)
        for i in range(7):
            x = x0 + 8 + i * (x1 - x0 - 16) / 7
            p.poly([(x, y0 + 8), (x + 16, y0 + 8), (x + 16, y0 + 26), (x + 8, y0 + 22), (x, y0 + 26)],
                   fill=col(rnd.choice([(230, 60, 90), (60, 170, 220), (250, 200, 50), (120, 200, 90), (240, 130, 50)])))
        p.line(x0 + 4, y0 + 8, x1 - 4, y0 + 8, (60, 60, 60, 255), 1)


def restaurant_display(p, x0, y0, x1, y1, spec, rnd, idx=0):
    """Salao do restaurante visto pela vitrine: cardapio/decoracao ao fundo, balcao e mesas."""
    h = y1 - y0
    inner = spec.get("interior", "tables")
    # parede do fundo: cardapio so na primeira vitrine; nas outras, decoracao
    if spec.get("menu_board", True) and x1 - x0 > 110 and idx == 0:
        mx0, mx1 = x0 + 14, min(x1 - 14, x0 + 14 + (x1 - x0) * 0.55)
        p.rect(mx0, y0 + 10, mx1, y0 + 46, fill=(28, 34, 32, 255), outline=(110, 90, 60, 255), width=2)
        p.text((mx0 + mx1) / 2, y0 + 19, spec.get("menu_title", "MENU"), "comic", 9, (230, 230, 220, 255),
               maxw=mx1 - mx0 - 6)
        for i in range(3):
            yy = y0 + 28 + i * 6
            p.line(mx0 + 6, yy, mx0 + (mx1 - mx0) * rnd.uniform(0.45, 0.8), yy, (180, 180, 170, 255), 1)
            p.line(mx1 - 16, yy, mx1 - 6, yy, (180, 180, 170, 255), 1)
    elif x1 - x0 > 90:
        wall_decor(p, x0, y0, x1, spec, rnd)
    if spec.get("back_items"):
        sy = y0 + 56
        shelf(p, x0, x1, sy, (80, 60, 44))
        fill_row(p, x0, x1, sy, 22, spec["back_items"], rnd)
    # balcao com itens
    # com mesas na frente, o balcao fica la atras (mais alto e mais baixo de altura)
    counter_top = y1 - 52 if inner != "tables_counter" else y1 - 74
    counter_bot = y1 if inner != "tables_counter" else y1 - 40
    if inner in ("counter", "bar", "tables_counter"):
        cc = spec.get("counter_color", (90, 60, 44))
        p.rect(x0 + 4, counter_top, x1 - 4, counter_bot, fill=col(cc))
        p.rect(x0 + 2, counter_top - 4, x1 - 2, counter_top, fill=col(cc, 1.3))
        fill_row(p, x0 + 6, x1 - 6, counter_top - 4, 26, spec.get("counter_items", ["cup"]), rnd, gap=10)
        if inner == "bar":
            x = x0 + 22
            while x < x1 - 16:
                stool(p, x, y1, spec.get("accent", (160, 40, 40)))
                x += 32
    if inner in ("tables", "tables_counter"):
        x = x0 + 34
        while x < x1 - 30:
            chairs_on_table(p, x, y1, rnd, spec.get("wood", (150, 110, 74)), spec.get("tablecloth"))
            x += 62
    elif inner == "booths":
        x = x0 + 48
        while x < x1 - 44:
            booth(p, x, y1, rnd, spec.get("accent", (160, 40, 40)))
            x += 92


# ------------------------------------------------------------------ fachada

def storefront_layout(x0, x1, door, door_w):
    """Divide a frente em segmentos ('door' ou 'win')."""
    segs = []
    if door == "left":
        segs = [("door", x0, x0 + door_w), ("win", x0 + door_w, x1)]
    elif door == "right":
        segs = [("win", x0, x1 - door_w), ("door", x1 - door_w, x1)]
    elif door == "sides":
        segs = [("door", x0, x0 + door_w), ("win", x0 + door_w, x1 - door_w), ("door", x1 - door_w, x1)]
    else:
        c = (x0 + x1) / 2
        segs = [("win", x0, c - door_w / 2), ("door", c - door_w / 2, c + door_w / 2), ("win", c + door_w / 2, x1)]
    out = []
    for kind, a, b in segs:
        if kind == "win" and b - a > 330:  # janelas largas viram varias, com montantes
            n = math.ceil((b - a) / 280)
            step = (b - a) / n
            for i in range(n):
                out.append(("win", a + i * step, a + (i + 1) * step))
        elif b - a > 20:
            out.append((kind, a, b))
    return out


def draw_window(p, x0, y0, x1, y1, spec, rnd, frame, idx=0):
    style = spec.get("front", "modern")
    gx0, gy0, gx1, gy1 = x0 + 5, y0 + 5, x1 - 5, y1 - 5
    if style == "arch":
        gy0 += 14
    glass(p, gx0, gy0, gx1, gy1, spec.get("glass", (30, 40, 56)))
    cy0 = gy0 + (28 if spec.get("awning") else 0)  # o toldo cobre o alto da vitrine
    if spec.get("kind") == "food":
        restaurant_display(p, gx0, cy0, gx1, gy1, spec, rnd, idx)
    else:
        retail_display(p, gx0, cy0, gx1, gy1, spec, rnd)
    if spec.get("blinds"):
        blinds(p, gx0, gy0, gx1, gy0 + (gy1 - gy0) * spec["blinds"])
    if spec.get("window_text"):
        p.text((gx0 + gx1) / 2, gy0 + 16, spec["window_text"], spec.get("window_font", "script"), 13,
               (230, 220, 190, 200), maxw=gx1 - gx0 - 16)
    reflections(p, gx0, gy0, gx1, gy1, rnd)
    fw = 5 if style != "wood" else 7
    p.rect(x0, y0, x1, y1, outline=frame, width=fw)
    if style == "arch":
        p.chord(x0, y0 - 6, x1, y0 + 40, 180, 360, frame)
        p.chord(x0 + 6, y0, x1 - 6, y0 + 36, 180, 360, col(spec.get("glass", (30, 40, 56)), 1.15))
    if style == "wood":  # travessa horizontal (bandeira)
        p.rect(x0, y0 + 28, x1, y0 + 33, fill=frame)


def draw_door(p, x0, y0, x1, y1, spec, rnd, frame):
    p.rect(x0, y0, x1, y1, fill=col(frame[:3], 0.8))
    dc = spec.get("door_color")
    if dc:  # porta solida (madeira/pintada) com visor
        p.rect(x0 + 6, y0 + 6, x1 - 6, y1, fill=col(dc))
        p.rect(x0 + 16, y0 + 18, x1 - 16, y0 + (y1 - y0) * 0.45, fill=col(spec.get("glass", (30, 40, 56))))
        p.rect(x0 + 16, y0 + (y1 - y0) * 0.55, x1 - 16, y1 - 14, outline=col(dc, 0.75), width=2)
    else:
        glass(p, x0 + 7, y0 + 7, x1 - 7, y1 - 2, spec.get("glass", (30, 40, 56)))
        if spec.get("blinds"):
            blinds(p, x0 + 7, y0 + 7, x1 - 7, y0 + 7 + (y1 - y0) * spec["blinds"] * 0.6)
        reflections(p, x0 + 7, y0 + 7, x1 - 7, y1 - 2, rnd)
        p.rect(x0 + 6, y0 + 6, x1 - 6, y1 - 1, outline=frame, width=3)
    if x1 - x0 > 120:  # porta dupla
        cx = (x0 + x1) / 2
        p.rect(cx - 3, y0 + 6, cx + 3, y1, fill=frame)
        door_handle(p, cx - 12, y0 + (y1 - y0) * 0.45, spec.get("handle", (150, 120, 80)))
        door_handle(p, cx + 7, y0 + (y1 - y0) * 0.45, spec.get("handle", (150, 120, 80)))
    else:
        door_handle(p, x1 - 20, y0 + (y1 - y0) * 0.45, spec.get("handle", (150, 120, 80)))


def draw_awning(p, x0, x1, y, spec, rnd, depth=26):
    a = spec["awning"]
    c1 = col(a[0])
    c2 = col(a[1]) if len(a) > 1 else col(a[0], 1.25)
    p.poly([(x0 - 6, y + depth), (x1 + 6, y + depth), (x1, y), (x0, y)], fill=c1)
    if len(a) > 1:
        sw = 18
        x = x0
        i = 0
        while x < x1:
            if i % 2:
                xa, xb = x, min(x1, x + sw)
                p.poly([(xa, y), (xb, y), (xb + (xb - (x0 + x1) / 2) * 0.012, y + depth),
                        (xa + (xa - (x0 + x1) / 2) * 0.012, y + depth)], fill=c2)
            x += sw
            i += 1
    # bambinela recortada
    vy = y + depth
    p.rect(x0 - 6, vy, x1 + 6, vy + 8, fill=c1)
    x = x0 - 6
    i = 0
    while x < x1 + 6:
        p.chord(x, vy + 2, x + 16, vy + 16, 0, 180, c2 if i % 2 else c1)
        x += 16
        i += 1
    if spec.get("awning_text"):
        p.text((x0 + x1) / 2, vy + 5, spec["awning_text"], "sans", 7, (245, 240, 230, 255), maxw=x1 - x0 - 20)


def draw_sign(p, cx, cy, w, h, spec, rnd):
    style = spec.get("sign", "board")
    text = spec["title"]
    fk = spec.get("font", "sans")
    fill = col(spec.get("sign_bg", (40, 50, 60)))
    ink = col(spec.get("ink", (235, 230, 215)))
    size = spec.get("font_size", h * 0.62)
    if style == "board":
        p.rect(cx - w / 2 - 4, cy - h / 2 - 4, cx + w / 2 + 4, cy + h / 2 + 4, fill=col(spec.get("sign_trim", (170, 165, 150))),
               radius=4)
        p.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=fill, radius=3)
        p.text(cx, cy, text, fk, size, ink, maxw=w - 20)
    elif style == "letters":  # letras soltas na parede, com sombra
        p.text(cx + 2, cy + 2, text, fk, size, (0, 0, 0, 120), maxw=w)
        p.text(cx, cy, text, fk, size, ink, maxw=w)
    elif style == "neon":  # neon apagado: tubo de vidro sobre placa escura
        p.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=(18, 18, 22, 255), radius=8)
        p.text(cx, cy, text, fk, size, col(spec.get("ink", (220, 80, 160)), 0.8), maxw=w - 20, stroke=1,
               stroke_fill=col(spec.get("ink", (220, 80, 160)), 0.45))
    elif style == "oval":
        p.ellipse(cx - w / 2 - 4, cy - h / 2 - 4, cx + w / 2 + 4, cy + h / 2 + 4, fill=col(spec.get("sign_trim", (190, 160, 90))))
        p.ellipse(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=fill)
        p.text(cx, cy, text, fk, size, ink, maxw=w * 0.78)
    elif style == "banner":
        p.line(cx - w / 2, cy - h / 2 - 6, cx + w / 2, cy - h / 2 - 6, (60, 60, 60, 255), 2)
        p.poly([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx + w / 2 - 12, cy),
                (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2 + 12, cy), (cx - w / 2, cy + h / 2)],
               fill=fill)
        p.text(cx, cy, text, fk, size, ink, maxw=w - 40)
    elif style == "marquee":  # placa com lampadas (apagadas) em volta
        p.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=fill, radius=6)
        n = int(w / 12)
        for i in range(n + 1):
            x = cx - w / 2 + 6 + i * (w - 12) / n
            p.circle(x, cy - h / 2 + 5, 2.5, fill=(200, 190, 150, 255))
            p.circle(x, cy + h / 2 - 5, 2.5, fill=(200, 190, 150, 255))
        p.text(cx, cy, text, fk, size * 0.85, ink, maxw=w - 24)
    if spec.get("subtitle"):
        p.text(cx, cy + h / 2 + 9, spec["subtitle"], spec.get("sub_font", "sans"), 9,
               col(spec.get("sub_ink", spec.get("ink", (235, 230, 215))), 0.9), maxw=w)


def draw_closed(p, spec, door_box, win_boxes, front_box, rnd):
    kind = spec.get("closed", "hanging")
    dx0, dy0, dx1, dy1 = door_box if door_box else front_box
    dcx = (dx0 + dx1) / 2
    if kind == "hanging":
        hanging_closed(p, dcx, dy0 + 26, spec.get("closed_text", "CLOSED"),
                       plate=spec.get("closed_plate", (30, 32, 40)), ink=spec.get("closed_ink", (236, 236, 240)))
    elif kind == "placard":
        placard_closed(p, dcx, dy0 + 60, spec.get("closed_lines", ("SORRY", "WE'RE CLOSED")),
                       w=min(90, dx1 - dx0 - 10))
    elif kind == "neon":
        wb = win_boxes[0] if win_boxes else front_box
        top = wb[1] + (62 if spec.get("awning") else 34)
        # restaurante tem o cardapio no alto a esquerda: o neon vai para a direita
        nx = wb[2] - 62 if spec.get("kind") == "food" else (wb[0] + wb[2]) / 2
        neon_closed(p, nx, top, spec.get("neon_color", (200, 50, 60)))
    elif kind == "easel":
        x = dx1 + 34 if dx1 + 60 < front_box[2] else dx0 - 34
        easel_closed(p, x, front_box[3] + WALK - 2, spec.get("closed_lines", ("CLOSED", "see you", "tomorrow!")))
    elif kind == "grille":
        x0, y0, x1, y1 = front_box
        security_grille(p, x0, y0, x1, y1, drop=1.0)
        hanging_closed(p, dcx, y0 + 30, spec.get("closed_text", "CLOSED"))
    elif kind == "grille_door":
        security_grille(p, dx0, dy0, dx1, dy1, drop=1.0)
        if win_boxes:
            wb = win_boxes[0]
            placard_closed(p, wb[2] - 50, wb[1] + (70 if spec.get("awning") else 40), ("CLOSED",), w=70)
    elif kind == "shutter_half":
        x0, y0, x1, y1 = front_box
        rolling_shutter(p, x0, y0, x1, y1, drop=spec.get("shutter_drop", 0.45))
        hanging_closed(p, dcx, y0 + (y1 - y0) * spec.get("shutter_drop", 0.45) + 4, spec.get("closed_text", "CLOSED"))


def extras(p, spec, W, front_box, rnd):
    fx0, fy0, fx1, fy1 = front_box
    base = fy1
    for e in spec.get("extras", []):
        if e == "planters":
            for cx in (fx0 + 40, fx1 - 40):
                p.rect(cx - 30, base - 22, cx + 30, base, fill=(96, 64, 44, 255))
                for _ in range(10):
                    p.circle(cx + rnd.uniform(-26, 26), base - 22 - rnd.uniform(0, 12), 6, fill=(56, 120, 60, 255))
        elif e == "pots":
            for cx in (fx0 - 16, fx1 + 16):
                if 10 < cx < W - 10:
                    pot_plant(p, cx, base, 60, rnd)
        elif e == "lamps":
            for cx in (fx0 + 20, fx1 - 20):
                p.rect(cx - 2, fy0 - 26, cx + 2, fy0 - 14, fill=(40, 40, 44, 255))
                p.chord(cx - 12, fy0 - 18, cx + 12, fy0 + 2, 180, 360, (40, 40, 46, 255))
        elif e == "sconces":
            for cx in (fx0 - 14, fx1 + 14):
                if 10 < cx < W - 10:
                    p.rect(cx - 5, fy0 + 30, cx + 5, fy0 + 52, fill=(200, 180, 120, 255), radius=3)
                    p.rect(cx - 2, fy0 + 52, cx + 2, fy0 + 58, fill=(60, 60, 60, 255))
        elif e == "bench":
            cx = fx0 + (fx1 - fx0) * 0.25
            p.rect(cx - 36, base - 18, cx + 36, base - 14, fill=(110, 80, 56, 255))
            p.rect(cx - 36, base - 32, cx + 36, base - 28, fill=(110, 80, 56, 255))
            for x in (cx - 30, cx + 26):
                p.rect(x, base - 32, x + 4, base, fill=(40, 40, 44, 255))
        elif e == "bike":
            from items import bike
            bike(p, fx1 - 60, base + WALK - 4, 46, rnd)
        elif e == "lanterns":
            n = max(3, int((fx1 - fx0) / 140))
            for i in range(n):
                lantern(p, fx0 + (fx1 - fx0) * (i + 0.5) / n, fy0 - 30, 34, rnd, spec.get("lantern_color", (200, 50, 40)))
        elif e == "string_lights":
            x = fx0
            while x < fx1:
                p.arc(x, fy0 - 26, x + 80, fy0 - 6, 0, 180, (60, 60, 60, 255), 1)
                for k in range(5):
                    t = (k + 0.5) / 5
                    yy = fy0 - 16 + math.sin(t * math.pi) * 9
                    p.circle(x + 80 * t, yy, 2.5, fill=(200, 190, 150, 255))
                x += 80
        elif e == "flag":
            cx = fx1 + 20 if fx1 + 30 < W else fx0 - 20
            p.line(cx, fy0 - 40, cx + 30, fy0 - 70, (150, 150, 150, 255), 2)
            p.rect(cx + 14, fy0 - 74, cx + 40, fy0 - 58, fill=col(spec.get("flag", (200, 40, 40))))


def compose(tmpl, spec, W, floors):
    rnd = random.Random(tmpl)
    H = FLOOR * floors
    p = Pen(W, H)
    wall_c = spec.get("wall_color", (90, 96, 110))
    wall(p, 0, 0, W, H, spec.get("wall", "stucco"), wall_c, rnd, spec.get("wall_color2"))
    # cornija e pilares laterais (separam das lojas vizinhas)
    p.rect(0, 0, W, 8, fill=col(wall_c, 0.7))
    p.rect(0, 0, 8, H, fill=col(wall_c, 0.78))
    p.rect(W - 8, 0, W, H, fill=col(wall_c, 0.78))
    for f in range(1, floors):
        p.rect(0, FLOOR * f - 4, W, FLOOR * f + 4, fill=col(wall_c, 0.6))

    top_of_ground = FLOOR * (floors - 1)
    margin = spec.get("margin", max(22, min(70, W * 0.05)))
    fx0, fx1 = margin, W - margin
    fy1 = H - WALK
    fy0 = top_of_ground + spec.get("front_top", 104)
    frame = col(spec.get("frame", (34, 36, 46)))

    if floors > 1:
        upper(p, spec, W, rnd, frame)

    # placa
    sign_cy = top_of_ground + spec.get("sign_y", 48)
    sign_w = spec.get("sign_w", min(W * 0.62, 520))
    sign_h = spec.get("sign_h", 50)
    if floors == 1 or spec.get("ground_sign", False):
        draw_sign(p, W / 2, sign_cy, sign_w, sign_h, spec, rnd)

    # vitrines e portas
    door_w = spec.get("door_w", 84 if W < 900 else 130)
    segs = storefront_layout(fx0, fx1, spec.get("door", "center"), door_w)
    p.rect(fx0 - 6, fy0 - 6, fx1 + 6, fy1, fill=col(frame[:3], 0.85))
    door_box, wins = None, []
    kick = spec.get("kick", 26 if spec.get("front") in ("wood", "classic") else 0)
    for kind, a, b in segs:
        if kind == "door":
            draw_door(p, a + 2, fy0, b - 2, fy1, spec, rnd, frame)
            door_box = door_box or (a + 2, fy0, b - 2, fy1)
        else:
            wy1 = fy1 - kick
            draw_window(p, a + 2, fy0, b - 2, wy1, spec, rnd, frame, len(wins))
            if kick:
                p.rect(a + 2, wy1, b - 2, fy1, fill=col(spec.get("kick_color", frame[:3]), 1.0))
                p.rect(a + 10, wy1 + 6, b - 10, fy1 - 6, outline=col(spec.get("kick_color", frame[:3]), 0.7), width=2)
            wins.append((a + 2, fy0, b - 2, wy1))
        if spec.get("front") == "classic":  # pilastras entre os vaos
            for x in (a, b):
                p.rect(x - 7, fy0 - 10, x + 7, fy1, fill=col(wall_c, 1.12))
                p.rect(x - 10, fy0 - 14, x + 10, fy0 - 8, fill=col(wall_c, 1.25))

    if spec.get("awning"):
        draw_awning(p, fx0, fx1, fy0 - 10, spec, rnd)
    sidewalk(p, W, H - WALK, H, spec.get("walk", (70, 62, 58)))
    extras(p, spec, W, (fx0, fy0, fx1, fy1), rnd)
    draw_closed(p, spec, door_box, wins, (fx0, fy0, fx1, fy1), rnd)
    return p.finish(spec.get("darkness", 0.62))


def upper(p, spec, W, rnd, frame):
    """Andar de cima das lojas de 2 andares: letreiro grande e janelas com vitrine."""
    draw_sign(p, W / 2, spec.get("sign_y", 48), spec.get("sign_w", min(W * 0.7, 900)), spec.get("sign_h", 56), spec, rnd)
    up = dict(spec)
    up["items"] = spec.get("upper_items", spec["items"])
    up["display"] = spec.get("upper_display", spec.get("display", "shelves"))
    up["kind"] = "retail"
    margin = spec.get("margin", 50)
    x0, x1 = margin, W - margin
    y0, y1 = 100, FLOOR - 26
    n = max(2, round((x1 - x0) / 240))
    step = (x1 - x0) / n
    for i in range(n):
        draw_window(p, x0 + i * step + 6, y0, x0 + (i + 1) * step - 6, y1, up, rnd, frame, i)
    if spec.get("upper_banner"):
        p.rect(0, y1 + 6, W, y1 + 20, fill=col(spec.get("sign_bg", (40, 50, 60))))
        p.text(W / 2, y1 + 13, spec["upper_banner"], "sans", 9, col(spec.get("ink", (235, 230, 215))), maxw=W - 40)

"""Produtos e moveis que aparecem nas vitrines. Cada item: fn(p, cx, base_y, h, rnd), desenhado com o
pe em base_y e altura ~h. ITEMS[nome] = (largura relativa a h, fn)."""
import math

from draw import col, mix

BRIGHT = [(214, 92, 120), (236, 180, 60), (90, 160, 210), (110, 190, 120), (200, 110, 200), (240, 130, 70),
          (230, 230, 220), (220, 70, 80), (80, 200, 190), (250, 210, 90)]


def pick(rnd, palette=BRIGHT):
    return col(rnd.choice(palette))


# ------------------------------------------------------------ varejo

def bottle(p, cx, by, h, rnd, glass=None):
    c = glass or rnd.choice([(60, 110, 70), (110, 50, 50), (140, 110, 60), (70, 80, 120), (200, 200, 190)])
    w = h * 0.26
    p.rect(cx - w / 2, by - h * 0.7, cx + w / 2, by, fill=col(c), radius=3)
    p.rect(cx - w * 0.18, by - h, cx + w * 0.18, by - h * 0.7, fill=col(c))
    p.rect(cx - w * 0.4, by - h * 0.5, cx + w * 0.4, by - h * 0.28, fill=col((230, 225, 210)))


def can(p, cx, by, h, rnd):
    w = h * 0.5
    c = pick(rnd)
    p.rect(cx - w / 2, by - h * 0.7, cx + w / 2, by, fill=c, radius=2)
    p.rect(cx - w / 2, by - h * 0.45, cx + w / 2, by - h * 0.3, fill=(240, 240, 240, 255))


def box(p, cx, by, h, rnd):
    w = h * rnd.uniform(0.5, 0.8)
    hh = h * rnd.uniform(0.5, 0.95)
    c = pick(rnd)
    p.rect(cx - w / 2, by - hh, cx + w / 2, by, fill=c)
    p.rect(cx - w / 2 + 3, by - hh * 0.7, cx + w / 2 - 3, by - hh * 0.45, fill=col(c, 1.4))


def phone(p, cx, by, h, rnd):
    w = h * 0.45
    p.rect(cx - w / 2 - 4, by - 4, cx + w / 2 + 4, by, fill=(70, 70, 76, 255))
    p.rect(cx - w / 2, by - h, cx + w / 2, by - 4, fill=(24, 24, 28, 255), radius=4)
    p.rect(cx - w / 2 + 2, by - h + 4, cx + w / 2 - 2, by - 9, fill=col(mix((40, 60, 110), (90, 50, 120), rnd.random())))


def books(p, cx, by, h, rnd):
    x = cx - h * 0.45
    while x < cx + h * 0.45:
        bw = rnd.uniform(4, 8)
        bh = h * rnd.uniform(0.7, 1.0)
        c = col(rnd.choice([(120, 50, 40), (50, 70, 110), (60, 90, 60), (150, 120, 70), (90, 60, 90), (40, 40, 44)]))
        p.rect(x, by - bh, x + bw, by, fill=c)
        p.line(x + 1, by - bh * 0.8, x + bw - 1, by - bh * 0.8, (220, 200, 150, 255), 1)
        x += bw + 1


def magazine(p, cx, by, h, rnd):
    w = h * 0.7
    c = pick(rnd)
    p.rect(cx - w / 2, by - h, cx + w / 2, by, fill=c)
    p.rect(cx - w / 2 + 3, by - h + 4, cx + w / 2 - 3, by - h + 11, fill=(245, 245, 240, 255))
    p.rect(cx - w / 2 + 6, by - h * 0.55, cx + w / 2 - 6, by - 6, fill=col(c, 0.7))


def newspaper(p, cx, by, h, rnd):
    w = h * 0.75
    p.rect(cx - w / 2, by - h, cx + w / 2, by, fill=(225, 222, 210, 255))
    p.rect(cx - w / 2 + 3, by - h + 3, cx + w / 2 - 3, by - h + 9, fill=(40, 40, 40, 255))
    for i in range(4):
        p.line(cx - w / 2 + 4, by - h + 15 + i * 6, cx + w / 2 - 4, by - h + 15 + i * 6, (120, 120, 120, 255), 1)


def pills(p, cx, by, h, rnd):
    c = pick(rnd)
    p.rect(cx - h * 0.3, by - h * 0.55, cx + h * 0.3, by, fill=(240, 240, 236, 255))
    p.rect(cx - h * 0.3, by - h * 0.4, cx + h * 0.3, by - h * 0.2, fill=c)
    p.rect(cx - h * 0.22, by - h * 0.75, cx + h * 0.22, by - h * 0.55, fill=(240, 240, 236, 255), radius=2)


def flower(p, cx, by, h, rnd):
    p.rect(cx - h * 0.18, by - h * 0.3, cx + h * 0.18, by, fill=col((110, 80, 60)))
    for _ in range(4):
        x = cx + rnd.uniform(-h * 0.3, h * 0.3)
        y = by - h * rnd.uniform(0.55, 1.0)
        p.line(cx, by - h * 0.3, x, y, (60, 110, 60, 255), 1)
        c = pick(rnd)
        for k in range(5):
            a = k * 1.256
            p.circle(x + math.cos(a) * h * 0.06, y + math.sin(a) * h * 0.06, h * 0.06, fill=c)


def sunglasses(p, cx, by, h, rnd):
    stand = col((200, 200, 205))
    p.rect(cx - 2, by - h * 0.6, cx + 2, by, fill=stand)
    p.rect(cx - h * 0.25, by - 3, cx + h * 0.25, by, fill=stand)
    y = by - h * 0.7
    c = col(rnd.choice([(20, 20, 24), (60, 40, 30), (40, 60, 90)]))
    p.ellipse(cx - h * 0.4, y - h * 0.12, cx - h * 0.05, y + h * 0.12, fill=c)
    p.ellipse(cx + h * 0.05, y - h * 0.12, cx + h * 0.4, y + h * 0.12, fill=c)
    p.line(cx - h * 0.05, y, cx + h * 0.05, y, c, 2)


def record(p, cx, by, h, rnd):
    w = h * 0.9
    c = pick(rnd)
    p.rect(cx - w / 2, by - w, cx + w / 2, by, fill=c)
    p.circle(cx + w * 0.15, by - w / 2, w * 0.42, fill=(18, 18, 20, 255))
    p.circle(cx + w * 0.15, by - w / 2, w * 0.12, fill=col(c, 1.3))
    p.rect(cx - w / 2, by - w, cx - w * 0.1, by, fill=c)
    p.circle(cx - w * 0.3, by - w * 0.6, w * 0.12, fill=col(c, 0.6))


def fishtank(p, cx, by, h, rnd):
    w = h * 1.2
    p.rect(cx - w / 2, by - 6, cx + w / 2, by, fill=(60, 50, 44, 255))
    p.rect(cx - w / 2, by - h, cx + w / 2, by - 6, fill=(40, 90, 110, 255), outline=(120, 140, 150, 255), width=2)
    for _ in range(4):
        x, y = cx + rnd.uniform(-w * 0.35, w * 0.35), by - rnd.uniform(h * 0.3, h * 0.8)
        c = col(rnd.choice([(240, 140, 50), (240, 200, 60), (200, 80, 80)]))
        p.ellipse(x - 5, y - 3, x + 5, y + 3, fill=c)
        p.poly([(x + 4, y), (x + 9, y - 4), (x + 9, y + 4)], fill=c)
    for i in range(3):
        x = cx - w / 3 + i * w / 3
        p.line(x, by - 6, x + rnd.uniform(-6, 6), by - h * 0.5, (60, 140, 70, 255), 2)


def pet_bed(p, cx, by, h, rnd):
    c = pick(rnd)
    p.ellipse(cx - h * 0.6, by - h * 0.45, cx + h * 0.6, by, fill=c)
    p.ellipse(cx - h * 0.45, by - h * 0.38, cx + h * 0.45, by - h * 0.08, fill=col(c, 1.3))
    # cachorrinho de pelucia
    p.ellipse(cx - h * 0.25, by - h * 0.55, cx + h * 0.2, by - h * 0.2, fill=(200, 170, 120, 255))
    p.circle(cx + h * 0.22, by - h * 0.5, h * 0.14, fill=(200, 170, 120, 255))
    p.ellipse(cx + h * 0.2, by - h * 0.62, cx + h * 0.3, by - h * 0.42, fill=(150, 110, 70, 255))


def watch(p, cx, by, h, rnd):
    p.rect(cx - h * 0.25, by - h * 0.35, cx + h * 0.25, by, fill=(60, 30, 40, 255), radius=3)
    strap = col(rnd.choice([(80, 50, 30), (40, 40, 44), (190, 170, 120)]))
    p.rect(cx - h * 0.08, by - h, cx + h * 0.08, by - h * 0.35, fill=strap)
    p.circle(cx, by - h * 0.68, h * 0.18, fill=(200, 190, 150, 255))
    p.circle(cx, by - h * 0.68, h * 0.14, fill=(240, 240, 235, 255))
    p.line(cx, by - h * 0.68, cx, by - h * 0.78, (30, 30, 30, 255), 1)
    p.line(cx, by - h * 0.68, cx + h * 0.07, by - h * 0.68, (30, 30, 30, 255), 1)


def jewelry(p, cx, by, h, rnd):
    # busto de veludo com colar
    p.rect(cx - h * 0.3, by - h * 0.2, cx + h * 0.3, by, fill=(40, 30, 50, 255))
    p.poly([(cx - h * 0.28, by - h * 0.2), (cx + h * 0.28, by - h * 0.2), (cx + h * 0.12, by - h * 0.7),
            (cx - h * 0.12, by - h * 0.7)], fill=(50, 34, 60, 255))
    p.rect(cx - h * 0.07, by - h, cx + h * 0.07, by - h * 0.7, fill=(50, 34, 60, 255))
    gem = col(rnd.choice([(230, 210, 120), (220, 220, 230), (200, 80, 100), (90, 160, 220)]))
    p.arc(cx - h * 0.16, by - h * 0.75, cx + h * 0.16, by - h * 0.4, 20, 160, gem, 2)
    p.circle(cx, by - h * 0.4, 3, fill=gem)


def china(p, cx, by, h, rnd):
    c = col(rnd.choice([(230, 230, 240), (240, 236, 220)]))
    trim = col(rnd.choice([(60, 90, 160), (170, 60, 60), (200, 160, 60)]))
    if rnd.random() < 0.5:  # bule
        p.ellipse(cx - h * 0.35, by - h * 0.6, cx + h * 0.35, by, fill=c)
        p.rect(cx - h * 0.35, by - h * 0.32, cx + h * 0.35, by - h * 0.26, fill=trim)
        p.poly([(cx + h * 0.3, by - h * 0.35), (cx + h * 0.55, by - h * 0.55), (cx + h * 0.32, by - h * 0.2)], fill=c)
        p.circle(cx, by - h * 0.64, h * 0.07, fill=trim)
    else:  # prato em pe
        p.circle(cx, by - h * 0.45, h * 0.42, fill=c)
        p.circle(cx, by - h * 0.45, h * 0.42, outline=trim, width=2)
        p.circle(cx, by - h * 0.45, h * 0.24, outline=trim, width=1)


def cosmetics(p, cx, by, h, rnd):
    for i, dx in enumerate((-h * 0.25, 0, h * 0.25)):
        c = pick(rnd)
        if i == 1:
            p.rect(cx + dx - 4, by - h * 0.8, cx + dx + 4, by, fill=(30, 30, 34, 255))
            p.rect(cx + dx - 3, by - h, cx + dx + 3, by - h * 0.8, fill=c)
        else:
            p.rect(cx + dx - 6, by - h * 0.45, cx + dx + 6, by, fill=c, radius=2)
            p.rect(cx + dx - 7, by - h * 0.55, cx + dx + 7, by - h * 0.45, fill=(220, 210, 190, 255))


def candle(p, cx, by, h, rnd):
    c = col(rnd.choice([(240, 230, 210), (220, 160, 170), (180, 200, 230), (230, 210, 140)]))
    hh = h * rnd.uniform(0.5, 1.0)
    p.rect(cx - h * 0.14, by - hh, cx + h * 0.14, by, fill=c)
    p.line(cx, by - hh, cx, by - hh - 4, (40, 40, 40, 255), 1)


def soap(p, cx, by, h, rnd):
    for i in range(3):
        c = pick(rnd)
        p.rect(cx - h * 0.3, by - (i + 1) * h * 0.22, cx + h * 0.3, by - i * h * 0.22 - 1, fill=c, radius=3)


def shirt(p, cx, by, h, rnd, c=None):
    """Camisa no cabide (by = linha da arara)."""
    c = c or pick(rnd)
    p.arc(cx - 4, by - 4, cx + 4, by + 4, 180, 360, (170, 170, 176, 255), 1)
    p.line(cx - h * 0.3, by + 6, cx, by, (170, 170, 176, 255), 1)
    p.line(cx + h * 0.3, by + 6, cx, by, (170, 170, 176, 255), 1)
    p.poly([(cx - h * 0.3, by + 6), (cx + h * 0.3, by + 6), (cx + h * 0.42, by + h * 0.3), (cx + h * 0.28, by + h * 0.34),
            (cx + h * 0.26, by + h * 0.9), (cx - h * 0.26, by + h * 0.9), (cx - h * 0.28, by + h * 0.34),
            (cx - h * 0.42, by + h * 0.3)], fill=c)


def clothes_rack(p, cx, by, h, rnd, palette=None):
    w = h * 1.6
    pole = (150, 150, 156, 255)
    p.line(cx - w / 2, by, cx - w / 2, by - h, pole, 2)
    p.line(cx + w / 2, by, cx + w / 2, by - h, pole, 2)
    p.line(cx - w / 2, by - h, cx + w / 2, by - h, pole, 2)
    n = 4
    for i in range(n):
        x = cx - w / 2 + w * (i + 0.5) / n
        shirt(p, x, by - h + 1, h * 0.62, rnd, col(rnd.choice(palette)) if palette else None)


def mannequin(p, cx, by, h, rnd, dress=None):
    skin = (200, 190, 180, 255)
    p.rect(cx - 2, by - h * 0.25, cx + 2, by, fill=(120, 120, 126, 255))
    p.rect(cx - h * 0.12, by - 3, cx + h * 0.12, by, fill=(120, 120, 126, 255))
    p.circle(cx, by - h * 0.92, h * 0.07, fill=skin)
    c = dress or pick(rnd)
    p.poly([(cx - h * 0.1, by - h * 0.83), (cx + h * 0.1, by - h * 0.83), (cx + h * 0.2, by - h * 0.28),
            (cx - h * 0.2, by - h * 0.28)], fill=c)
    p.rect(cx - h * 0.1, by - h * 0.84, cx + h * 0.1, by - h * 0.62, fill=col(c[:3], 0.85))


def shoe(p, cx, by, h, rnd):
    c = pick(rnd, [(120, 60, 40), (30, 30, 34), (200, 60, 70), (230, 230, 225), (90, 110, 160)])
    p.poly([(cx - h * 0.4, by), (cx + h * 0.45, by), (cx + h * 0.45, by - h * 0.18), (cx, by - h * 0.25),
            (cx - h * 0.2, by - h * 0.5), (cx - h * 0.4, by - h * 0.5)], fill=c)
    p.rect(cx - h * 0.42, by - 3, cx + h * 0.47, by, fill=(240, 240, 236, 255))


def purse(p, cx, by, h, rnd):
    c = pick(rnd, [(120, 60, 40), (30, 30, 34), (190, 60, 80), (200, 170, 120), (60, 80, 120)])
    p.arc(cx - h * 0.25, by - h, cx + h * 0.25, by - h * 0.4, 180, 360, col(c[:3], 0.7), 2)
    p.rect(cx - h * 0.4, by - h * 0.65, cx + h * 0.4, by, fill=c, radius=5)
    p.rect(cx - h * 0.4, by - h * 0.65, cx + h * 0.4, by - h * 0.4, fill=col(c[:3], 0.8), radius=5)
    p.circle(cx, by - h * 0.4, 2, fill=(220, 200, 120, 255))


def briefcase(p, cx, by, h, rnd):
    c = col(rnd.choice([(80, 50, 30), (30, 30, 34), (110, 70, 40)]))
    p.rect(cx - h * 0.12, by - h * 0.75, cx + h * 0.12, by - h * 0.6, outline=c, width=2)
    p.rect(cx - h * 0.45, by - h * 0.6, cx + h * 0.45, by, fill=c, radius=3)
    p.rect(cx - h * 0.45, by - h * 0.4, cx + h * 0.45, by - h * 0.36, fill=col(c[:3], 0.6))


def tv(p, cx, by, h, rnd):
    w = h * 1.4
    p.rect(cx - 3, by - h * 0.15, cx + 3, by, fill=(50, 50, 54, 255))
    p.rect(cx - w * 0.25, by - 3, cx + w * 0.25, by, fill=(50, 50, 54, 255))
    p.rect(cx - w / 2, by - h, cx + w / 2, by - h * 0.15, fill=(18, 18, 20, 255), radius=2)
    p.rect(cx - w / 2 + 3, by - h + 3, cx + w / 2 - 3, by - h * 0.15 - 3,
           fill=col(mix((30, 40, 70), (60, 30, 70), rnd.random())))


def laptop(p, cx, by, h, rnd):
    w = h * 1.1
    p.poly([(cx - w / 2, by - h * 0.85), (cx + w / 2 - 4, by - h * 0.85), (cx + w / 2, by - 4), (cx - w / 2 + 4, by - 4)],
           fill=(40, 40, 46, 255))
    p.rect(cx - w / 2 - 6, by - 5, cx + w / 2 + 6, by, fill=(150, 150, 156, 255))


def console(p, cx, by, h, rnd):
    c = pick(rnd)
    p.rect(cx - h * 0.45, by - h * 0.35, cx + h * 0.45, by, fill=(30, 30, 36, 255), radius=4)
    p.circle(cx - h * 0.25, by - h * 0.18, 3, fill=c)
    p.circle(cx + h * 0.25, by - h * 0.18, 3, fill=c)


def cheese(p, cx, by, h, rnd):
    c = col(rnd.choice([(240, 200, 80), (230, 170, 60), (245, 230, 170), (210, 130, 50)]))
    if rnd.random() < 0.5:
        p.ellipse(cx - h * 0.5, by - h * 0.45, cx + h * 0.5, by, fill=c)
        p.rect(cx - h * 0.5, by - h * 0.3, cx + h * 0.5, by - h * 0.12, fill=col(c[:3], 0.85))
    else:
        p.poly([(cx - h * 0.5, by), (cx + h * 0.5, by), (cx + h * 0.5, by - h * 0.55)], fill=c)
        for _ in range(3):
            p.circle(cx + rnd.uniform(0, h * 0.35), by - rnd.uniform(4, h * 0.25), 2, fill=col(c[:3], 0.7))


def candy_jar(p, cx, by, h, rnd):
    p.rect(cx - h * 0.3, by - h * 0.85, cx + h * 0.3, by, fill=(170, 200, 210, 120), outline=(200, 220, 230, 255),
           width=1, radius=6)
    p.rect(cx - h * 0.2, by - h, cx + h * 0.2, by - h * 0.85, fill=pick(rnd))
    for _ in range(12):
        p.circle(cx + rnd.uniform(-h * 0.22, h * 0.22), by - rnd.uniform(4, h * 0.6), 3, fill=pick(rnd))


def lollipop(p, cx, by, h, rnd):
    p.line(cx, by, cx, by - h * 0.55, (240, 240, 240, 255), 2)
    c1, c2 = pick(rnd), pick(rnd)
    p.circle(cx, by - h * 0.75, h * 0.24, fill=c1)
    p.arc(cx - h * 0.16, by - h * 0.91, cx + h * 0.16, by - h * 0.59, 0, 300, c2, 3)


def swimsuit(p, cx, by, h, rnd):
    c = pick(rnd)
    p.line(cx - h * 0.15, by - h, cx - h * 0.1, by - h * 0.7, c, 2)
    p.line(cx + h * 0.15, by - h, cx + h * 0.1, by - h * 0.7, c, 2)
    p.poly([(cx - h * 0.22, by - h * 0.7), (cx + h * 0.22, by - h * 0.7), (cx + h * 0.18, by - h * 0.25),
            (cx, by - h * 0.12), (cx - h * 0.18, by - h * 0.25)], fill=c)
    p.circle(cx - h * 0.08, by - h * 0.5, 2, fill=(240, 240, 240, 255))
    p.circle(cx + h * 0.08, by - h * 0.4, 2, fill=(240, 240, 240, 255))


def beach_ball(p, cx, by, h, rnd):
    r = h * 0.35
    cs = [(220, 60, 60), (240, 240, 230), (60, 120, 220), (240, 200, 60)]
    for i in range(4):
        p.pie(cx - r, by - 2 * r, cx + r, by, i * 90, i * 90 + 90, col(cs[i]))


def salon_chair(p, cx, by, h, rnd):
    # espelho na parede + cadeira de cabeleireiro
    p.rect(cx - h * 0.3, by - h * 1.05, cx + h * 0.3, by - h * 0.55, fill=(150, 170, 190, 255),
           outline=(200, 180, 120, 255), width=2, radius=8)
    c = col(rnd.choice([(150, 40, 60), (30, 30, 34), (200, 200, 200)]))
    p.rect(cx - 2, by - h * 0.2, cx + 2, by, fill=(170, 170, 176, 255))
    p.ellipse(cx - h * 0.25, by - 5, cx + h * 0.25, by, fill=(170, 170, 176, 255))
    p.rect(cx - h * 0.25, by - h * 0.35, cx + h * 0.25, by - h * 0.2, fill=c, radius=3)
    p.rect(cx - h * 0.2, by - h * 0.7, cx + h * 0.2, by - h * 0.33, fill=c, radius=4)


def atm(p, cx, by, h, rnd):
    p.rect(cx - h * 0.3, by - h, cx + h * 0.3, by, fill=(60, 66, 76, 255), radius=3)
    p.rect(cx - h * 0.22, by - h * 0.9, cx + h * 0.22, by - h * 0.62, fill=(30, 60, 90, 255))
    for i in range(3):
        for j in range(3):
            p.rect(cx - h * 0.15 + j * h * 0.11, by - h * 0.55 + i * h * 0.08, cx - h * 0.08 + j * h * 0.11,
                   by - h * 0.49 + i * h * 0.08, fill=(170, 170, 176, 255))
    p.rect(cx - h * 0.2, by - h * 0.22, cx + h * 0.2, by - h * 0.18, fill=(20, 20, 20, 255))


def sofa(p, cx, by, h, rnd):
    c = pick(rnd, [(150, 60, 50), (60, 90, 110), (180, 160, 120), (70, 110, 80), (120, 120, 126)])
    w = h * 1.6
    p.rect(cx - w / 2, by - h * 0.7, cx + w / 2, by - h * 0.15, fill=c, radius=6)
    p.rect(cx - w / 2 + 6, by - h * 0.4, cx + w / 2 - 6, by - h * 0.15, fill=col(c[:3], 1.15), radius=4)
    p.rect(cx - w / 2, by - h * 0.5, cx - w / 2 + 10, by - h * 0.15, fill=col(c[:3], 0.85), radius=4)
    p.rect(cx + w / 2 - 10, by - h * 0.5, cx + w / 2, by - h * 0.15, fill=col(c[:3], 0.85), radius=4)
    p.rect(cx - w / 2 + 4, by - h * 0.15, cx - w / 2 + 8, by, fill=(60, 40, 30, 255))
    p.rect(cx + w / 2 - 8, by - h * 0.15, cx + w / 2 - 4, by, fill=(60, 40, 30, 255))


def floor_lamp(p, cx, by, h, rnd):
    p.line(cx, by, cx, by - h * 0.8, (60, 60, 64, 255), 2)
    p.ellipse(cx - h * 0.15, by - 4, cx + h * 0.15, by, fill=(60, 60, 64, 255))
    p.poly([(cx - h * 0.18, by - h * 0.78), (cx + h * 0.18, by - h * 0.78), (cx + h * 0.1, by - h),
            (cx - h * 0.1, by - h)], fill=pick(rnd, [(230, 220, 190), (200, 120, 80), (140, 170, 160)]))


def armchair(p, cx, by, h, rnd):
    c = pick(rnd, [(150, 60, 50), (60, 90, 110), (200, 170, 100), (70, 110, 80)])
    p.rect(cx - h * 0.4, by - h * 0.85, cx + h * 0.4, by - h * 0.2, fill=c, radius=8)
    p.rect(cx - h * 0.45, by - h * 0.45, cx + h * 0.45, by - h * 0.2, fill=col(c[:3], 0.85), radius=5)
    p.rect(cx - h * 0.4, by - h * 0.2, cx - h * 0.33, by, fill=(60, 40, 30, 255))
    p.rect(cx + h * 0.33, by - h * 0.2, cx + h * 0.4, by, fill=(60, 40, 30, 255))


def fruit_crate(p, cx, by, h, rnd):
    w = h * 1.1
    p.rect(cx - w / 2, by - h * 0.35, cx + w / 2, by, fill=(150, 110, 70, 255))
    p.line(cx - w / 2, by - h * 0.18, cx + w / 2, by - h * 0.18, (110, 80, 50, 255), 1)
    c = col(rnd.choice([(220, 60, 50), (240, 160, 40), (120, 180, 60), (240, 220, 80), (130, 60, 140)]))
    for i in range(6):
        x = cx - w / 2 + 6 + i * (w - 12) / 5
        p.circle(x, by - h * 0.42, h * 0.11, fill=c)
    for i in range(5):
        x = cx - w / 2 + 11 + i * (w - 22) / 4
        p.circle(x, by - h * 0.58, h * 0.11, fill=col(c[:3], 1.1))


def teddy(p, cx, by, h, rnd):
    c = col(rnd.choice([(170, 120, 70), (200, 170, 130), (120, 80, 50), (230, 200, 200)]))
    p.ellipse(cx - h * 0.28, by - h * 0.55, cx + h * 0.28, by, fill=c)
    p.circle(cx, by - h * 0.7, h * 0.2, fill=c)
    p.circle(cx - h * 0.16, by - h * 0.86, h * 0.08, fill=c)
    p.circle(cx + h * 0.16, by - h * 0.86, h * 0.08, fill=c)
    p.circle(cx, by - h * 0.64, h * 0.07, fill=col(c[:3], 1.2))
    p.rect(cx - h * 0.12, by - h * 0.55, cx + h * 0.12, by - h * 0.5, fill=pick(rnd))


def blocks(p, cx, by, h, rnd):
    s = h * 0.32
    for i, (dx, dy) in enumerate([(-s, 0), (0, 0), (s, 0), (-s / 2, 1), (s / 2, 1), (0, 2)]):
        x = cx + dx - s / 2
        y = by - (dy + 1) * s
        c = pick(rnd)
        p.rect(x, y, x + s - 1, y + s - 1, fill=c)
        p.text(x + s / 2, y + s / 2, "ABCXYZ"[i], "sans", s * 0.6, (255, 255, 255, 255))


def ball(p, cx, by, h, rnd):
    kind = rnd.choice(["soccer", "basket", "tennis"])
    r = h * (0.35 if kind != "tennis" else 0.18)
    if kind == "soccer":
        p.circle(cx, by - r, r, fill=(240, 240, 236, 255))
        p.circle(cx, by - r, r * 0.35, fill=(30, 30, 30, 255))
    elif kind == "basket":
        p.circle(cx, by - r, r, fill=(220, 120, 50, 255))
        p.line(cx - r, by - r, cx + r, by - r, (60, 30, 20, 255), 1)
        p.line(cx, by - 2 * r, cx, by, (60, 30, 20, 255), 1)
    else:
        p.circle(cx, by - r, r, fill=(210, 230, 70, 255))


def bike(p, cx, by, h, rnd):
    r = h * 0.28
    c = pick(rnd)
    for x in (cx - h * 0.45, cx + h * 0.45):
        p.circle(x, by - r, r, outline=(30, 30, 30, 255), width=2)
    p.line(cx - h * 0.45, by - r, cx, by - r, c, 2)
    p.line(cx, by - r, cx + h * 0.2, by - h * 0.7, c, 2)
    p.line(cx - h * 0.45, by - r, cx - h * 0.1, by - h * 0.7, c, 2)
    p.line(cx - h * 0.1, by - h * 0.7, cx + h * 0.2, by - h * 0.7, c, 2)
    p.line(cx + h * 0.45, by - r, cx + h * 0.25, by - h * 0.8, c, 2)
    p.rect(cx - h * 0.18, by - h * 0.78, cx - h * 0.02, by - h * 0.72, fill=(30, 30, 30, 255))


def racket(p, cx, by, h, rnd):
    c = pick(rnd)
    p.line(cx, by, cx, by - h * 0.45, (60, 60, 60, 255), 3)
    p.ellipse(cx - h * 0.22, by - h, cx + h * 0.22, by - h * 0.42, outline=c, width=3)
    for i in range(1, 4):
        p.line(cx - h * 0.2 + i * h * 0.1, by - h * 0.95, cx - h * 0.2 + i * h * 0.1, by - h * 0.47, (200, 200, 200, 255), 1)


def tshirt_band(p, cx, by, h, rnd):
    c = col(rnd.choice([(30, 30, 34), (120, 30, 40), (40, 40, 80)]))
    w = h * 0.8
    p.poly([(cx - w * 0.3, by - h), (cx + w * 0.3, by - h), (cx + w * 0.55, by - h * 0.75), (cx + w * 0.38, by - h * 0.62),
            (cx + w * 0.36, by), (cx - w * 0.36, by), (cx - w * 0.38, by - h * 0.62), (cx - w * 0.55, by - h * 0.75)], fill=c)
    p.circle(cx, by - h * 0.55, h * 0.14, outline=pick(rnd), width=2)
    p.line(cx - h * 0.1, by - h * 0.62, cx + h * 0.1, by - h * 0.48, pick(rnd), 2)


def skull_rack(p, cx, by, h, rnd):
    # expositor de piercings / correntes
    p.rect(cx - h * 0.35, by - h, cx + h * 0.35, by, fill=(30, 26, 30, 255))
    for i in range(4):
        y = by - h * 0.85 + i * h * 0.2
        for j in range(3):
            p.circle(cx - h * 0.2 + j * h * 0.2, y, 2, fill=(200, 200, 205, 255))


def arcade(p, cx, by, h, rnd):
    c = pick(rnd, [(160, 40, 160), (40, 120, 200), (220, 60, 60), (40, 160, 90), (240, 180, 40)])
    w = h * 0.5
    p.rect(cx - w / 2, by - h, cx + w / 2, by, fill=col(c[:3], 0.6))
    p.rect(cx - w / 2, by - h, cx + w / 2, by - h * 0.85, fill=c)
    p.rect(cx - w / 2 + 4, by - h * 0.82, cx + w / 2 - 4, by - h * 0.5, fill=(20, 30, 50, 255))
    p.poly([(cx - w / 2, by - h * 0.5), (cx + w / 2, by - h * 0.5), (cx + w / 2 + 3, by - h * 0.4),
            (cx - w / 2 - 3, by - h * 0.4)], fill=(40, 40, 46, 255))
    p.circle(cx - w * 0.2, by - h * 0.46, 2, fill=(220, 40, 40, 255))
    p.circle(cx + w * 0.15, by - h * 0.46, 2, fill=(240, 220, 40, 255))


def grocery_shelf_item(p, cx, by, h, rnd):
    rnd.choice([box, can, bottle, fruit_crate])(p, cx, by, h, rnd)


def sport_shoe(p, cx, by, h, rnd):
    shoe(p, cx, by, h, rnd)
    p.line(cx - h * 0.1, by - h * 0.15, cx + h * 0.3, by - h * 0.25, pick(rnd), 2)


# ------------------------------------------------------------ comida

def coffee_machine(p, cx, by, h, rnd):
    c = col(rnd.choice([(170, 170, 176), (150, 40, 40), (40, 40, 44)]))
    p.rect(cx - h * 0.45, by - h, cx + h * 0.45, by, fill=c, radius=4)
    p.rect(cx - h * 0.3, by - h * 0.55, cx + h * 0.3, by - h * 0.2, fill=(30, 30, 34, 255))
    p.rect(cx - 3, by - h * 0.55, cx + 3, by - h * 0.42, fill=(150, 150, 156, 255))
    p.circle(cx - h * 0.25, by - h * 0.8, 3, fill=(60, 60, 60, 255))
    p.circle(cx + h * 0.25, by - h * 0.8, 3, fill=(60, 60, 60, 255))


def cup(p, cx, by, h, rnd):
    c = pick(rnd, [(240, 240, 236), (150, 90, 60), (90, 140, 120), (200, 80, 80)])
    p.poly([(cx - h * 0.3, by - h), (cx + h * 0.3, by - h), (cx + h * 0.22, by), (cx - h * 0.22, by)], fill=c)
    p.rect(cx - h * 0.33, by - h - 3, cx + h * 0.33, by - h, fill=col(c[:3], 0.8))


def cake(p, cx, by, h, rnd):
    p.rect(cx - h * 0.04, by - h * 0.2, cx + h * 0.04, by, fill=(200, 200, 205, 255))
    p.ellipse(cx - h * 0.5, by - h * 0.25, cx + h * 0.5, by - h * 0.15, fill=(220, 220, 225, 255))
    c = pick(rnd, [(240, 200, 210), (120, 70, 50), (250, 240, 220), (240, 180, 80)])
    p.rect(cx - h * 0.4, by - h * 0.7, cx + h * 0.4, by - h * 0.22, fill=c, radius=3)
    p.rect(cx - h * 0.4, by - h * 0.7, cx + h * 0.4, by - h * 0.6, fill=(250, 250, 245, 255), radius=3)
    for i in range(4):
        p.circle(cx - h * 0.3 + i * h * 0.2, by - h * 0.74, 3, fill=(200, 40, 50, 255))


def bread(p, cx, by, h, rnd):
    c = col((200, 150, 80))
    if rnd.random() < 0.5:
        p.ellipse(cx - h * 0.5, by - h * 0.4, cx + h * 0.5, by, fill=c)
        for i in range(3):
            p.line(cx - h * 0.3 + i * h * 0.25, by - h * 0.32, cx - h * 0.2 + i * h * 0.25, by - h * 0.12,
                   col((150, 100, 50)), 2)
    else:
        p.chord(cx - h * 0.5, by - h * 0.6, cx + h * 0.5, by + h * 0.3, 180, 360, c)


def donut(p, cx, by, h, rnd):
    r = h * 0.35
    p.circle(cx, by - r, r, fill=(200, 150, 90, 255))
    p.circle(cx, by - r, r * 0.85, fill=pick(rnd, [(240, 160, 190), (110, 60, 40), (250, 250, 240), (240, 200, 80)]))
    p.circle(cx, by - r, r * 0.3, fill=(0, 0, 0, 0))
    p.circle(cx, by - r, r * 0.3, fill=(34, 30, 34, 255))
    for _ in range(5):
        a = rnd.uniform(0, 6.28)
        p.line(cx + math.cos(a) * r * 0.55, by - r + math.sin(a) * r * 0.55, cx + math.cos(a) * r * 0.65,
               by - r + math.sin(a) * r * 0.65, pick(rnd), 1)


def ice_cream(p, cx, by, h, rnd):
    p.poly([(cx - h * 0.15, by - h * 0.55), (cx + h * 0.15, by - h * 0.55), (cx, by)], fill=(210, 160, 90, 255))
    for i in range(rnd.randint(1, 2)):
        p.circle(cx, by - h * 0.62 - i * h * 0.22, h * 0.17, fill=pick(rnd, [(250, 220, 230), (120, 70, 50),
                                                                            (250, 245, 220), (160, 220, 160)]))


def ice_tubs(p, cx, by, h, rnd):
    w = h * 1.4
    p.rect(cx - w / 2, by - h * 0.45, cx + w / 2, by, fill=(200, 210, 220, 255))
    for i in range(4):
        x = cx - w / 2 + 4 + i * (w - 8) / 4
        p.rect(x + 1, by - h * 0.42, x + (w - 8) / 4 - 1, by - h * 0.3,
               fill=pick(rnd, [(250, 220, 230), (120, 70, 50), (250, 245, 220), (160, 220, 160), (250, 200, 120)]))


def smoothie(p, cx, by, h, rnd):
    c = pick(rnd, [(230, 90, 120), (240, 180, 60), (130, 200, 100), (160, 90, 180)])
    p.poly([(cx - h * 0.2, by - h * 0.8), (cx + h * 0.2, by - h * 0.8), (cx + h * 0.15, by), (cx - h * 0.15, by)], fill=c)
    p.line(cx + h * 0.05, by - h * 0.8, cx + h * 0.15, by - h, (240, 240, 240, 255), 2)
    p.circle(cx - h * 0.12, by - h * 0.8, h * 0.08, fill=(120, 190, 80, 255))


def sandwich(p, cx, by, h, rnd):
    w = h * 0.9
    p.rect(cx - w / 2, by - h * 0.12, cx + w / 2, by, fill=(210, 170, 110, 255), radius=3)
    p.rect(cx - w / 2 - 2, by - h * 0.18, cx + w / 2 + 2, by - h * 0.12, fill=(120, 180, 80, 255))
    p.rect(cx - w / 2, by - h * 0.24, cx + w / 2, by - h * 0.18, fill=(220, 90, 80, 255))
    p.rect(cx - w / 2, by - h * 0.28, cx + w / 2, by - h * 0.24, fill=(240, 210, 100, 255))
    p.chord(cx - w / 2, by - h * 0.45, cx + w / 2, by - h * 0.15, 180, 360, (210, 170, 110, 255))


def burger(p, cx, by, h, rnd):
    w = h * 0.7
    p.rect(cx - w / 2, by - h * 0.12, cx + w / 2, by, fill=(200, 150, 80, 255), radius=3)
    p.rect(cx - w / 2 - 1, by - h * 0.22, cx + w / 2 + 1, by - h * 0.12, fill=(90, 50, 30, 255), radius=2)
    p.rect(cx - w / 2 - 2, by - h * 0.26, cx + w / 2 + 2, by - h * 0.22, fill=(110, 190, 70, 255))
    p.chord(cx - w / 2, by - h * 0.55, cx + w / 2, by - h * 0.1, 180, 360, (210, 150, 70, 255))


def pizza(p, cx, by, h, rnd):
    r = h * 0.45
    p.ellipse(cx - r, by - r * 0.5, cx + r, by, fill=(200, 140, 70, 255))
    p.ellipse(cx - r * 0.85, by - r * 0.45, cx + r * 0.85, by - r * 0.05, fill=(220, 80, 50, 255))
    for _ in range(5):
        p.circle(cx + rnd.uniform(-r * 0.6, r * 0.6), by - rnd.uniform(r * 0.12, r * 0.38), 2, fill=(160, 40, 40, 255))


def beer_taps(p, cx, by, h, rnd):
    w = h * 1.1
    p.rect(cx - w / 2, by - h * 0.55, cx + w / 2, by - h * 0.45, fill=(170, 150, 90, 255))
    for i in range(4):
        x = cx - w / 2 + 6 + i * (w - 12) / 3
        p.rect(x - 1, by - h * 0.45, x + 1, by - h * 0.3, fill=(170, 150, 90, 255))
        p.rect(x - 3, by - h, x + 3, by - h * 0.55, fill=pick(rnd, [(30, 30, 30), (120, 40, 30), (40, 80, 50)]), radius=2)


def pint(p, cx, by, h, rnd):
    c = col(rnd.choice([(220, 160, 40), (90, 40, 20), (240, 200, 90)]))
    p.poly([(cx - h * 0.2, by - h * 0.8), (cx + h * 0.2, by - h * 0.8), (cx + h * 0.16, by), (cx - h * 0.16, by)], fill=c)
    p.rect(cx - h * 0.21, by - h * 0.92, cx + h * 0.21, by - h * 0.8, fill=(245, 240, 225, 255))


def wine_glass(p, cx, by, h, rnd):
    g = (190, 200, 210, 255)
    p.line(cx, by, cx, by - h * 0.45, g, 1)
    p.line(cx - h * 0.15, by, cx + h * 0.15, by, g, 1)
    p.chord(cx - h * 0.2, by - h, cx + h * 0.2, by - h * 0.4, 0, 180, col(rnd.choice([(120, 30, 40), (230, 220, 160)])))
    p.arc(cx - h * 0.2, by - h * 1.1, cx + h * 0.2, by - h * 0.4, 0, 180, g, 1)


def cocktail(p, cx, by, h, rnd):
    g = (190, 200, 210, 255)
    p.line(cx, by, cx, by - h * 0.45, g, 1)
    p.line(cx - h * 0.15, by, cx + h * 0.15, by, g, 1)
    p.poly([(cx - h * 0.3, by - h), (cx + h * 0.3, by - h), (cx, by - h * 0.45)],
           fill=pick(rnd, [(230, 90, 120), (90, 180, 220), (240, 180, 60)]))
    p.circle(cx + h * 0.2, by - h * 0.98, h * 0.06, fill=(120, 190, 80, 255))


def sushi(p, cx, by, h, rnd):
    w = h * 1.3
    p.rect(cx - w / 2, by - h * 0.12, cx + w / 2, by, fill=(60, 40, 30, 255))
    for i in range(4):
        x = cx - w / 2 + 6 + i * (w - 12) / 3
        p.rect(x - 6, by - h * 0.3, x + 6, by - h * 0.12, fill=(240, 240, 236, 255), radius=3)
        p.rect(x - 6, by - h * 0.38, x + 6, by - h * 0.28, fill=pick(rnd, [(240, 120, 90), (200, 60, 60), (240, 200, 90)]),
               radius=3)


def lantern(p, cx, by, h, rnd, color=(200, 50, 40)):
    """Lanterna pendurada: by = ponto de pendurar (topo)."""
    p.line(cx, by, cx, by + h * 0.15, (60, 40, 30, 255), 1)
    p.ellipse(cx - h * 0.25, by + h * 0.15, cx + h * 0.25, by + h * 0.65, fill=col(color))
    p.rect(cx - h * 0.15, by + h * 0.12, cx + h * 0.15, by + h * 0.18, fill=(200, 160, 60, 255))
    p.rect(cx - h * 0.15, by + h * 0.62, cx + h * 0.15, by + h * 0.68, fill=(200, 160, 60, 255))
    p.line(cx, by + h * 0.68, cx, by + h * 0.8, (200, 160, 60, 255), 1)


def plate_set(p, cx, by, h, rnd):
    p.ellipse(cx - h * 0.4, by - h * 0.15, cx + h * 0.4, by, fill=(235, 235, 240, 255))
    wine_glass(p, cx + h * 0.45, by, h * 0.6, rnd)


def pot_plant(p, cx, by, h, rnd):
    p.poly([(cx - h * 0.2, by - h * 0.35), (cx + h * 0.2, by - h * 0.35), (cx + h * 0.15, by), (cx - h * 0.15, by)],
           fill=col(rnd.choice([(170, 90, 60), (220, 220, 215), (60, 60, 64)])))
    for _ in range(9):
        a = rnd.uniform(-2.6, -0.5)
        l = h * rnd.uniform(0.35, 0.65)
        p.line(cx, by - h * 0.35, cx + math.cos(a) * l * 0.8, by - h * 0.35 + math.sin(a) * l, (60, 120, 70, 255), 3)


ITEMS = {
    "bottle": (0.35, bottle), "can": (0.6, can), "box": (0.85, box), "phone": (0.7, phone), "books": (1.0, books),
    "magazine": (0.85, magazine), "newspaper": (0.9, newspaper), "pills": (0.75, pills), "flower": (0.8, flower),
    "sunglasses": (0.95, sunglasses), "record": (1.0, record), "fishtank": (1.35, fishtank), "pet_bed": (1.3, pet_bed),
    "watch": (0.55, watch), "jewelry": (0.75, jewelry), "china": (0.95, china), "cosmetics": (0.9, cosmetics),
    "candle": (0.4, candle), "soap": (0.7, soap), "clothes_rack": (1.75, clothes_rack), "mannequin": (0.5, mannequin),
    "shoe": (1.0, shoe), "purse": (0.95, purse), "briefcase": (1.0, briefcase), "tv": (1.5, tv), "laptop": (1.3, laptop),
    "console": (1.0, console), "cheese": (1.1, cheese), "candy_jar": (0.75, candy_jar), "lollipop": (0.6, lollipop),
    "swimsuit": (0.55, swimsuit), "beach_ball": (0.8, beach_ball), "salon_chair": (0.8, salon_chair), "atm": (0.7, atm),
    "sofa": (1.7, sofa), "floor_lamp": (0.45, floor_lamp), "armchair": (0.95, armchair), "fruit_crate": (1.2, fruit_crate),
    "teddy": (0.65, teddy), "blocks": (1.05, blocks), "ball": (0.8, ball), "bike": (1.5, bike), "racket": (0.5, racket),
    "tshirt_band": (0.95, tshirt_band), "skull_rack": (0.8, skull_rack), "arcade": (0.6, arcade),
    "grocery": (1.0, grocery_shelf_item), "sport_shoe": (1.0, sport_shoe), "coffee_machine": (1.0, coffee_machine),
    "cup": (0.7, cup), "cake": (1.05, cake), "bread": (1.05, bread), "donut": (0.8, donut), "ice_cream": (0.45, ice_cream),
    "ice_tubs": (1.45, ice_tubs), "smoothie": (0.5, smoothie), "sandwich": (1.0, sandwich), "burger": (0.8, burger),
    "pizza": (1.0, pizza), "beer_taps": (1.2, beer_taps), "pint": (0.5, pint), "wine_glass": (0.45, wine_glass),
    "cocktail": (0.65, cocktail), "sushi": (1.35, sushi), "plate_set": (1.1, plate_set), "pot_plant": (0.7, pot_plant),
}

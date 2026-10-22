"""Primitivas de desenho das fachadas: caneta com supersampling, paredes, vidro, placas e textos."""
import math
import random

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

S = 2  # desenha em 2x e reduz no final (bordas suaves)


def col(c, f=1.0, a=255):
    """Cor RGB(A) multiplicada por f."""
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + (a,)


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


FONT_FILES = {
    "sans": ["arialbd.ttf"], "round": ["ARLRDBD.TTF"], "condensed": ["BRLNSB.TTF", "AGENCYB.TTF"],
    "serif": ["georgiab.ttf"], "bodoni": ["BOD_B.TTF"], "elegant": ["BOD_CR.TTF", "CENTAUR.TTF"],
    "script": ["segoescb.ttf"], "brush": ["BRUSHSCI.TTF"], "fancy": ["FREESCPT.TTF"], "vivaldi": ["VIVALDII.TTF"],
    "slab": ["ROCKB.TTF"], "cooper": ["COOPBL.TTF"], "broadway": ["BROADW.TTF"], "showcard": ["SHOWG.TTF"],
    "stencil": ["STENCIL.TTF"], "impact": ["impact.ttf"], "comic": ["comicbd.ttf"], "jokerman": ["JOKERMAN.TTF"],
    "ravie": ["RAVIE.TTF"], "gothic": ["OLDENGL.TTF"], "algerian": ["ALGER.TTF"], "bauhaus": ["BAUHS93.TTF"],
    "forte": ["FORTE.TTF"], "elephant": ["ELEPHNT.TTF"], "magneto": ["MAGNETOB.TTF"], "papyrus": ["PAPYRUS.TTF"],
    "harlow": ["HARLOWSI.TTF"], "playbill": ["PLAYBILL.TTF"], "britannic": ["BRITANIC.TTF"], "gill": ["GILSANUB.TTF"],
    "typewriter": ["courbd.ttf"], "chiller": ["CHILLER.TTF"], "calligraphy": ["LCALLIG.TTF"], "verdana": ["verdanab.ttf"],
}
_font_cache = {}


def font(kind, size):
    key = (kind, int(size))
    if key not in _font_cache:
        f = None
        for name in FONT_FILES.get(kind, []) + ["arialbd.ttf"]:
            try:
                f = ImageFont.truetype(name, max(6, int(size * S)))
                break
            except OSError:
                pass
        _font_cache[key] = f or ImageFont.load_default()
    return _font_cache[key]


class Pen:
    """Desenha em coordenadas da imagem final (o supersampling fica escondido aqui)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 255))
        self.d = ImageDraw.Draw(self.img)

    def _s(self, *v):
        return [v_ * S for v_ in v]

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1, radius=0):
        if x1 <= x0 or y1 <= y0:
            return
        box = self._s(x0, y0, x1, y1)
        if radius:
            self.d.rounded_rectangle(box, radius=radius * S, fill=fill, outline=outline, width=int(width * S))
        else:
            self.d.rectangle(box, fill=fill, outline=outline, width=int(width * S))

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.d.ellipse(self._s(x0, y0, x1, y1), fill=fill, outline=outline, width=int(width * S))

    def circle(self, cx, cy, r, fill=None, outline=None, width=1):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, fill, outline, width)

    def poly(self, pts, fill=None, outline=None):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill, outline=outline)

    def line(self, x0, y0, x1, y1, fill, width=1):
        self.d.line(self._s(x0, y0, x1, y1), fill=fill, width=max(1, int(width * S)))

    def arc(self, x0, y0, x1, y1, a0, a1, fill, width=1):
        self.d.arc(self._s(x0, y0, x1, y1), a0, a1, fill=fill, width=max(1, int(width * S)))

    def pie(self, x0, y0, x1, y1, a0, a1, fill):
        self.d.pieslice(self._s(x0, y0, x1, y1), a0, a1, fill=fill)

    def chord(self, x0, y0, x1, y1, a0, a1, fill):
        self.d.chord(self._s(x0, y0, x1, y1), a0, a1, fill=fill)

    def text(self, cx, cy, s, kind, size, fill, maxw=None, stroke=0, stroke_fill=None, anchor="mm"):
        """Texto centrado; encolhe ate caber em maxw."""
        while True:
            f = font(kind, size)
            box = self.d.textbbox((0, 0), s, font=f, stroke_width=int(stroke * S))
            tw = (box[2] - box[0]) / S
            if maxw is None or tw <= maxw or size <= 7:
                break
            size *= 0.92
        self.d.text((cx * S, cy * S), s, font=f, fill=fill, anchor=anchor,
                    stroke_width=int(stroke * S), stroke_fill=stroke_fill)
        return tw

    def overlay(self, fn, alpha_box=None):
        """Desenha numa camada transparente e compoe por cima (para reflexos, sombras)."""
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        saved = self.d
        self.d = ImageDraw.Draw(layer)
        fn()
        self.d = saved
        if alpha_box:
            mask = Image.new("L", self.img.size, 0)
            ImageDraw.Draw(mask).rectangle(self._s(*alpha_box), fill=255)
            layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", self.img.size, 0), mask))
        self.img.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.img)

    def finish(self, darkness=0.62, night=(20, 26, 48), blend=0.18):
        """Reduz para o tamanho final e aplica 'luz apagada' (escurece e puxa para azul-noite)."""
        img = self.img.resize((self.w, self.h), Image.LANCZOS).convert("RGB")
        img = ImageEnhance.Brightness(img).enhance(darkness)
        img = Image.blend(img, Image.new("RGB", img.size, night), blend)
        return img.convert("RGBA")


# ------------------------------------------------------------------ paredes

def wall(p, x0, y0, x1, y1, style, color, rnd, color2=None):
    p.rect(x0, y0, x1, y1, fill=col(color))
    if style == "brick":
        bh, bw = 9, 24
        mortar = col(color, 0.72)
        for row, y in enumerate(range(int(y0), int(y1), bh)):
            off = (bw // 2) * (row % 2)
            for x in range(int(x0) - off, int(x1), bw):
                f = rnd.uniform(0.88, 1.1)
                p.rect(max(x0, x + 1), y + 1, min(x1, x + bw - 1), min(y1, y + bh - 1), fill=col(color, f))
            p.line(x0, y, x1, y, mortar, 1)
    elif style == "planks":
        for x in range(int(x0), int(x1), 18):
            p.rect(x, y0, x + 17, y1, fill=col(color, rnd.uniform(0.9, 1.08)))
            p.line(x, y0, x, y1, col(color, 0.6), 1)
    elif style == "tiles":
        t = 22
        for y in range(int(y0), int(y1), t):
            for x in range(int(x0), int(x1), t):
                p.rect(x + 1, y + 1, min(x1, x + t - 1), min(y1, y + t - 1), fill=col(color, rnd.uniform(0.93, 1.07)))
    elif style == "marble":
        for _ in range(int((x1 - x0) * (y1 - y0) / 2500)):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            pts = [(x, y)]
            for _ in range(5):
                x += rnd.uniform(-14, 14)
                y += rnd.uniform(4, 14)
                pts.append((x, y))
            for a, b in zip(pts, pts[1:]):
                p.line(a[0], a[1], b[0], b[1], col(color, 1.12), 1)
    elif style == "panels":
        pw = 96
        for x in range(int(x0), int(x1), pw):
            p.rect(x + 4, y0 + 4, min(x1 - 4, x + pw - 4), y1 - 4, outline=col(color, 0.78), width=2)
    elif style == "stripes":
        c2 = color2 or col(color, 1.2)
        for i, x in enumerate(range(int(x0), int(x1), 20)):
            if i % 2:
                p.rect(x, y0, min(x1, x + 20), y1, fill=col(c2))
    elif style == "stucco":
        for _ in range(int((x1 - x0) * (y1 - y0) / 60)):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            p.rect(x, y, x + 1, y + 1, fill=col(color, rnd.uniform(0.9, 1.1)))
    elif style == "stone":
        y = y0
        while y < y1:
            h = rnd.choice([18, 22, 26])
            x = x0 - rnd.uniform(0, 30)
            while x < x1:
                w = rnd.uniform(30, 60)
                p.rect(max(x0, x + 1), y + 1, min(x1, x + w - 1), min(y1, y + h - 1),
                       fill=col(color, rnd.uniform(0.85, 1.1)), radius=2)
                x += w
            y += h


def sidewalk(p, w, y0, y1, color=(70, 62, 58)):
    p.rect(0, y0, w, y1, fill=col(color))
    p.rect(0, y0, w, y0 + 3, fill=col(color, 1.6))


# ------------------------------------------------------------------ vidro e porta

def glass(p, x0, y0, x1, y1, tint=(30, 40, 56)):
    for i in range(int(y0), int(y1)):
        t = (i - y0) / max(1, (y1 - y0))
        p.rect(x0, i, x1, i + 1, fill=col(mix(tint, col(tint, 1.25), t)))


def reflections(p, x0, y0, x1, y1, rnd):
    def draw():
        for _ in range(rnd.randint(2, 3)):
            off = rnd.uniform(0, max(1, x1 - x0 - 40))
            wd = rnd.uniform(8, 30)
            p.poly([(x0 + off, y1), (x0 + off + wd, y1), (x0 + off + wd + 90, y0), (x0 + off + 90, y0)],
                   fill=(255, 255, 255, 20))
    p.overlay(draw, (x0, y0, x1, y1))


def blinds(p, x0, y0, x1, y1, color=(46, 48, 60)):
    for y in range(int(y0), int(y1), 6):
        p.rect(x0 + 2, y, x1 - 2, y + 4, fill=col(color))


def door_handle(p, x, y, color=(150, 120, 80), vertical=True):
    if vertical:
        p.rect(x, y, x + 5, y + 46, fill=col(color))
    else:
        p.rect(x, y, x + 30, y + 5, fill=col(color))


# ------------------------------------------------------------------ sinais de "fechado"

def hanging_closed(p, cx, top, text="CLOSED", w=82, plate=(30, 32, 40), ink=(236, 236, 240), kind="sans"):
    p.line(cx, top, cx - w * 0.28, top + 20, (170, 170, 176, 255), 1)
    p.line(cx, top, cx + w * 0.28, top + 20, (170, 170, 176, 255), 1)
    p.circle(cx, top, 3, fill=(170, 170, 176, 255))
    p.rect(cx - w / 2, top + 20, cx + w / 2, top + 46, fill=col(plate), outline=col(ink, 0.85), width=2, radius=4)
    p.text(cx, top + 33, text, kind, 14, col(ink), maxw=w - 10)


def placard_closed(p, cx, cy, lines=("SORRY", "WE'RE CLOSED"), w=90, plate=(240, 236, 220), ink=(180, 40, 40)):
    h = 18 + 15 * (len(lines) - 1)
    p.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, fill=col(plate), outline=col(ink), width=2, radius=3)
    for i, s in enumerate(lines):
        p.text(cx, cy - h / 2 + 10 + i * 15, s, "condensed", 12, col(ink), maxw=w - 8)


def neon_closed(p, cx, cy, color=(200, 50, 60), text="CLOSED"):
    p.rect(cx - 50, cy - 16, cx + 50, cy + 16, fill=(20, 20, 26, 255), radius=6)
    p.text(cx, cy, text, "round", 17, col(color, 0.75), maxw=90, stroke=1, stroke_fill=col(color, 0.45))


def easel_closed(p, cx, base, lines=("CLOSED", "see you", "tomorrow!"), board=(40, 46, 44), frame=(120, 86, 54)):
    p.line(cx - 26, base, cx - 18, base - 74, col(frame), 4)
    p.line(cx + 26, base, cx + 18, base - 74, col(frame), 4)
    p.rect(cx - 24, base - 76, cx + 24, base - 18, fill=col(board), outline=col(frame), width=3)
    sizes = [12, 10, 10, 10]
    for i, s in enumerate(lines):
        p.text(cx, base - 64 + i * 15, s, "comic" if i else "condensed", sizes[min(i, 3)],
               (235, 235, 225, 255), maxw=42)


def security_grille(p, x0, y0, x1, y1, drop=1.0, color=(110, 114, 120)):
    """Grade de seguranca (pantografica) descida ate 'drop' da altura."""
    yb = y0 + (y1 - y0) * drop
    p.rect(x0, y0 - 6, x1, y0, fill=col(color, 0.6))
    for x in range(int(x0), int(x1), 12):
        p.line(x, y0, x + 6, yb, col(color), 1)
        p.line(x + 6, y0, x, yb, col(color), 1)
        p.line(x, y0, x, yb, col(color, 1.2), 2)
    p.rect(x0, yb - 3, x1, yb, fill=col(color, 0.8))
    p.rect((x0 + x1) / 2 - 6, yb - 8, (x0 + x1) / 2 + 6, yb, fill=(40, 40, 44, 255))


def rolling_shutter(p, x0, y0, x1, y1, drop=1.0, color=(118, 122, 130)):
    yb = y0 + (y1 - y0) * drop
    for y in range(int(y0), int(yb), 7):
        p.rect(x0, y, x1, min(yb, y + 6), fill=col(color, 1.0 - 0.15 * ((y - y0) / max(1, y1 - y0))))
        p.line(x0, y + 6, x1, y + 6, col(color, 0.55), 1)
    p.rect(x0, yb - 6, x1, yb, fill=col(color, 0.6))

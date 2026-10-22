"""Gera a arte e os sons iniciais do Upward em assets/.

Sao placeholders feitos por codigo: troque qualquer arquivo por outro com o
mesmo nome (PNG com transparencia; WAV PCM) e rode o build de novo.

    python tools/gen_assets.py
"""
import os
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
TEX = os.path.join(ROOT, "textures")
SND = os.path.join(ROOT, "sounds")
RATE = 22050


# ---------------------------------------------------------------- texturas

def shutter():
    """Porta de aco de enrolar. 100 px de largura repetem lado a lado;
    150 px de altura = 1 andar. Embaixo fica a barra com o puxador."""
    w, h = 100, 150
    img = Image.new("RGBA", (w, h))
    px = img.load()
    slat = 9
    for y in range(h):
        k = y % slat
        # cada lamina: claro em cima, escurece, sulco escuro no fim
        if k == slat - 1:
            base = 58
        elif k == 0:
            base = 128
        else:
            base = 118 - k * 4
        shade = 1.0 - 0.18 * (y / h)  # um pouco mais escuro embaixo (luz apagada)
        for x in range(w):
            g = int(base * shade + ((x * 7 + y * 3) % 5) - 2)
            px[x, y] = (g - 6, g, g + 10, 248)
    d = ImageDraw.Draw(img)
    # barra inferior e puxador
    d.rectangle([0, h - 11, w, h - 1], fill=(62, 66, 74, 255))
    d.line([0, h - 11, w, h - 11], fill=(150, 156, 166, 255))
    d.rounded_rectangle([w // 2 - 9, h - 8, w // 2 + 9, h - 4], radius=2, fill=(30, 32, 36, 255))
    img.save(os.path.join(TEX, "closed_shutter.png"))


def sign():
    """Placa CLOSED pendurada por dois fios."""
    w, h = 104, 46
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([22, 0, 30, 14], fill=(40, 40, 40, 255), width=2)
    d.line([w - 22, 0, w - 30, 14], fill=(40, 40, 40, 255), width=2)
    d.rounded_rectangle([4, 13, w - 5, h - 3], radius=5, fill=(0, 0, 0, 90))
    d.rounded_rectangle([2, 11, w - 7, h - 5], radius=5, fill=(196, 44, 44, 255), outline=(250, 240, 230, 255), width=2)
    font = None
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, 15)
            break
        except OSError:
            pass
    font = font or ImageFont.load_default()
    text = "CLOSED"
    box = d.textbbox((0, 0), text, font=font)
    tx = (w - 7 - (box[2] - box[0])) // 2 + 1
    ty = 11 + (h - 16 - (box[3] - box[1])) // 2 - box[1]
    d.text((tx, ty), text, font=font, fill=(255, 248, 238, 255))
    img.save(os.path.join(TEX, "closed_sign.png"))


def lights_off():
    """Escurecimento azul-noite para escritorios fora do expediente."""
    Image.new("RGBA", (4, 4), (12, 16, 34, 170)).save(os.path.join(TEX, "lights_off.png"))


# ---------------------------------------------------------------- sons

def save(name, signal):
    signal = signal / max(1e-6, np.max(np.abs(signal))) * 0.9
    data = (signal * 32767).astype(np.int16)
    with wave.open(os.path.join(SND, name), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        f.writeframes(data.tobytes())


def lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc)
        y[i] = acc
    return y


def rattle(duration, rate_start, rate_end, rng):
    """Chacoalhar metalico de porta de enrolar: estalos a cada lamina."""
    n = int(duration * RATE)
    t = np.arange(n) / RATE
    out = np.zeros(n)
    rate = np.linspace(rate_start, rate_end, n)
    phase = np.cumsum(rate) / RATE
    hits = np.nonzero(np.diff(np.floor(phase)) > 0)[0]
    click_len = int(0.025 * RATE)
    ct = np.arange(click_len) / RATE
    for h in hits:
        f = rng.uniform(900, 1700)
        click = (rng.standard_normal(click_len) * 0.6 + np.sin(2 * np.pi * f * ct)) * np.exp(-ct * 160)
        end = min(n, h + click_len)
        out[h:end] += click[: end - h] * rng.uniform(0.5, 1.0)
    rumble = lowpass(rng.standard_normal(n), 0.02) * 3.0
    return out + rumble * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))


def thunk(rng, length=0.25):
    n = int(length * RATE)
    t = np.arange(n) / RATE
    body = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 18)
    hit = lowpass(rng.standard_normal(n), 0.15) * np.exp(-t * 60)
    return body * 1.4 + hit


def shutter_sounds():
    rng = np.random.default_rng(7)
    down = rattle(0.9, 34, 22, rng)
    end = thunk(rng)
    # a batida no chao comeca um pouco antes do chacoalhar terminar
    close = np.concatenate([down, np.zeros(len(end) * 2 // 3)])
    close[-len(end):] += end * 2.2
    save("shutter_close.wav", close * fade_io(len(close)))

    up = rattle(0.8, 20, 36, rng)
    start = thunk(rng, 0.15) * 0.8
    up[: len(start)] += start
    save("shutter_open.wav", up * fade_io(len(up)))


def fade_io(n, ms=5):
    k = int(ms / 1000 * RATE)
    env = np.ones(n)
    env[:k] = np.linspace(0, 1, k)
    env[-k:] = np.linspace(1, 0, k)
    return env


if __name__ == "__main__":
    os.makedirs(TEX, exist_ok=True)
    os.makedirs(os.path.join(SND, "emitters"), exist_ok=True)
    shutter()
    sign()
    lights_off()
    # O som sintetico da porta (shutter_sounds) foi trocado por gravacoes reais:
    # veja tools/prepare_sounds.py e assets/sounds/CREDITOS.txt
    print("assets gerados em", os.path.abspath(ROOT))

"""Corta e converte os sons reais (Wikimedia Commons, dominio publico) para assets/sounds.

Fontes (baixe para uma pasta e passe o caminho):
  https://upload.wikimedia.org/wikipedia/commons/c/c2/Garage_door_closing.ogg
  https://upload.wikimedia.org/wikipedia/commons/4/4e/Garage_door_opening.ogg

    python tools/prepare_sounds.py <pasta com os .ogg>

Precisa do pacote soundfile (pip install soundfile).
"""
import os
import struct
import sys

import numpy as np
import soundfile as sf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sounds")
FADE = 0.03  # segundos de crossfade entre os trechos


def strip_skeleton(path):
    """As portas de garagem vem com uma trilha Ogg Skeleton que o libsndfile nao le; tira so ela."""
    data = open(path, "rb").read()
    out, skeleton, i = bytearray(), set(), 0
    while i < len(data):
        serial = struct.unpack_from("<I", data, i + 14)[0]
        nseg = data[i + 26]
        size = 27 + nseg + sum(data[i + 27:i + 27 + nseg])
        page = data[i:i + size]
        body = page[27 + nseg:]
        if body.startswith(b"fishead") or body.startswith(b"fisbone"):
            skeleton.add(serial)
        if serial not in skeleton:
            out += page
        i += size
    clean = path + ".vorbis.ogg"
    open(clean, "wb").write(out)
    return clean


def load(path):
    try:
        x, sr = sf.read(path)
    except sf.LibsndfileError:
        x, sr = sf.read(strip_skeleton(path))
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x, sr


def cut(x, sr, start, end):
    return x[int(start * sr):int(end * sr)].copy()


def join(parts, sr):
    """Emenda trechos com crossfade curto para nao estalar."""
    n = int(FADE * sr)
    ramp = np.linspace(0, 1, n)
    out = parts[0]
    for p in parts[1:]:
        mixed = out[-n:] * (1 - ramp) + p[:n] * ramp
        out = np.concatenate([out[:-n], mixed, p[n:]])
    return out


def finish(x, sr, name):
    n = int(0.01 * sr)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    x = x / max(1e-6, np.max(np.abs(x))) * 0.9
    sf.write(os.path.join(OUT, name), x, sr, subtype="PCM_16")
    print(f"{name}: {len(x) / sr:.2f} s")


def main(src):
    # fechando: a parte mais forte da descida + a batida final no chao (7,7 s)
    x, sr = load(os.path.join(src, "Garage_door_closing.ogg"))
    finish(join([cut(x, sr, 3.7, 5.9), cut(x, sr, 7.62, 8.2)], sr), sr, "shutter_close.wav")

    # abrindo: destrava (0,6 s), comeca a subir e bate no alto (5,4 s)
    x, sr = load(os.path.join(src, "Garage_door_opening.ogg"))
    finish(join([cut(x, sr, 0.55, 0.9), cut(x, sr, 1.85, 3.0), cut(x, sr, 5.3, 5.9)], sr), sr, "shutter_open.wav")


if __name__ == "__main__":
    main(sys.argv[1])

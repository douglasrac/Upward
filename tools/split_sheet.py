"""Separa uma imagem com varias fachadas (em faixas ou em grade, separadas por linhas brancas) e grava
cada uma, no tamanho do jogo, em assets/textures/closed_custom/<template>.png.

    python tools/split_sheet.py <imagem> <template1> <template2> ...
    (ordem de leitura: da esquerda para a direita, de cima para baixo)

O tamanho de cada loja vem de tools/facades/stores.py. Depois rode tools/facades/make.py para levar
as artes para assets/textures/closed/.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "facades"))
from stores import STORES  # noqa: E402

CUSTOM = os.path.join(HERE, "..", "assets", "textures", "closed_custom")
WHITE = 200        # brilho medio de uma linha separadora
MIN_STRIP = 40     # faixas menores que isso sao ignoradas


def find_cells(img):
    """Faixas horizontais e, dentro de cada uma, colunas separadas por linhas brancas verticais."""
    cells = []
    for y0, y1 in find_strips(img):
        strip = img.crop((0, y0, img.size[0], y1))
        for x0, x1 in find_strips(strip.transpose(Image.TRANSPOSE)):  # colunas viram linhas
            cells.append((x0, y0, x1, y1))
    return cells


def find_strips(img):
    rows = np.asarray(img.convert("RGB")).astype(int).mean(axis=(1, 2))
    strips, start = [], None
    for y, b in enumerate(rows):
        if b <= WHITE and start is None:
            start = y
        elif b > WHITE and start is not None:
            strips.append((start, y))
            start = None
    if start is not None:
        strips.append((start, len(rows)))
    return [(a, b) for a, b in strips if b - a >= MIN_STRIP]


def main(argv):
    # --trim 0.075: corta essa fracao de cada lateral antes de ajustar (bom quando a fachada veio
    # larga demais: tira as bordas, como vasos, e aperta menos o resto)
    trim = 0.0
    if "--trim" in argv:
        i = argv.index("--trim")
        trim = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    src, templates = argv[0], argv[1:]
    img = Image.open(src).convert("RGB")
    found = find_cells(img)
    if len(found) != len(templates):
        sys.exit(f"Achei {len(found)} fachadas {found}, mas foram informados {len(templates)} templates.")
    os.makedirs(CUSTOM, exist_ok=True)
    for box, tmpl in zip(found, templates):
        cells, floors, _ = STORES[tmpl]
        w, h = cells * 100, floors * 300
        side = int((box[2] - box[0]) * trim)
        strip = img.crop((box[0] + side, box[1], box[2] - side, box[3]))
        ratio, target = strip.size[0] / strip.size[1], w / h
        strip.resize((w, h), Image.LANCZOS).save(os.path.join(CUSTOM, tmpl + ".png"), optimize=True)
        print(f"{tmpl}: faixa {strip.size[0]}x{strip.size[1]} ({ratio:.2f}:1) -> {w}x{h} ({target:.2f}:1), "
              f"ajuste {abs(ratio / target - 1) * 100:.0f}%")


if __name__ == "__main__":
    main(sys.argv[1:])

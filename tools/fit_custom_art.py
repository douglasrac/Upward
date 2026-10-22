"""Encaixa uma arte de fachada no tamanho do jogo (casas x 100 por andares x 300).

Modos:
  stretch  estica para o tamanho exato (deforma se a proporcao for diferente)
  wall     mantem a proporcao: reduz pela largura e completa o alto repetindo a parede
           de cima da imagem (a fachada fica apoiada na calcada, com mais parede acima)

    python tools/fit_custom_art.py <entrada> <saida.png> <largura> <altura> [stretch|wall] [x0 y0 x1 y1]

O recorte opcional (x0 y0 x1 y1) separa uma fachada de uma imagem com varias.
"""
import sys

from PIL import Image

WALL_SAMPLE = 6  # linhas do topo usadas para "crescer" a parede


def fit(img, w, h, mode):
    if mode == "stretch":
        return img.resize((w, h), Image.LANCZOS)
    scaled_h = round(img.size[1] * w / img.size[0])
    if scaled_h >= h:  # mais alta que o espaco: estica so o necessario
        return img.resize((w, h), Image.LANCZOS)
    body = img.resize((w, scaled_h), Image.LANCZOS)
    # amostra so a parede lisa da esquerda (o letreiro costuma encostar no topo, no meio)
    # e repete pela largura toda, para nao "puxar" o letreiro para cima
    sample_w = w // 5
    sample = body.crop((0, 0, sample_w, WALL_SAMPLE)).resize((sample_w, h - scaled_h), Image.BILINEAR)
    out = Image.new("RGB", (w, h))
    for x in range(0, w, sample_w):
        out.paste(sample, (x, 0))
    out.paste(body, (0, h - scaled_h))
    return out


def main(argv):
    src, dst, w, h = argv[0], argv[1], int(argv[2]), int(argv[3])
    mode = argv[4] if len(argv) > 4 else "wall"
    img = Image.open(src).convert("RGB")
    if len(argv) > 8:
        img = img.crop(tuple(int(v) for v in argv[5:9]))
    fit(img, w, h, mode).save(dst, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1:])

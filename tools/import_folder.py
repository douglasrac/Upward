"""Importa uma pasta de artes de fachada ja nomeadas pelo template (ex.: retail-level-one-a.jpg).

Cada imagem e reduzida para o tamanho do jogo e gravada em assets/textures/closed_custom/<template>.png.
Avisa quando a proporcao foge mais de 5% da loja (ai convem olhar antes de usar).

    python tools/import_folder.py "<pasta>"
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "facades"))
from stores import STORES  # noqa: E402

CUSTOM = os.path.join(HERE, "..", "assets", "textures", "closed_custom")


def main(folder):
    os.makedirs(CUSTOM, exist_ok=True)
    for name in sorted(os.listdir(folder)):
        tmpl, ext = os.path.splitext(name)
        if ext.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        if tmpl not in STORES:
            print(f"IGNORADO {name}: nome nao e de nenhuma loja conhecida")
            continue
        cells, floors, _ = STORES[tmpl]
        w, h = cells * 100, floors * 300
        img = Image.open(os.path.join(folder, name)).convert("RGB")
        diff = (img.size[0] / img.size[1]) / (w / h) - 1
        flag = "  <-- ATENCAO" if abs(diff) > 0.05 else ""
        img.resize((w, h), Image.LANCZOS).save(os.path.join(CUSTOM, tmpl + ".png"), optimize=True)
        print(f"{tmpl}: {img.size[0]}x{img.size[1]} -> {w}x{h}, ajuste {diff * 100:+.0f}%{flag}")


if __name__ == "__main__":
    main(sys.argv[1])

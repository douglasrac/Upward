"""Gera as imagens de loja fechada em assets/textures/closed/.

    python tools/facades/make.py                 # todas
    python tools/facades/make.py retail-level-one  # so as que contem o texto
    python tools/facades/make.py --sheet <png>   # tambem grava uma folha de conferencia
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw  # noqa: E402

from facade import FLOOR, compose  # noqa: E402
from stores import STORES  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "textures", "closed")
# Arte feita a mao: assets/textures/closed_custom/<template>.png tem prioridade e nunca e sobrescrita
CUSTOM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "textures", "closed_custom")
PX_PER_CELL = 100


def main(argv):
    sheet_path = None
    if "--sheet" in argv:
        i = argv.index("--sheet")
        sheet_path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    filt = argv[0] if argv else ""
    os.makedirs(OUT, exist_ok=True)
    made = []
    for tmpl, (cells, floors, spec) in STORES.items():
        if filt not in tmpl:
            continue
        w = cells * PX_PER_CELL
        custom = os.path.join(CUSTOM, tmpl + ".png")
        if os.path.exists(custom):
            img = Image.open(custom)
            if img.size != (w, floors * FLOOR):
                print(f"AVISO {tmpl}: arte propria tem {img.size}, o ideal e {(w, floors * FLOOR)}")
            img.save(os.path.join(OUT, tmpl + ".png"), optimize=True)
            made.append((tmpl, img))
            print(f"{tmpl}: arte propria (closed_custom)")
            continue
        img = compose(tmpl, spec, w, floors)
        assert img.size == (w, floors * FLOOR), (tmpl, img.size)
        img.save(os.path.join(OUT, tmpl + ".png"))
        made.append((tmpl, img))
        print(f"{tmpl}: {img.size[0]}x{img.size[1]}")
    if sheet_path and made:
        contact_sheet(made, sheet_path)


def contact_sheet(made, path, col_w=700):
    """Folha com todas as imagens reduzidas, para conferir de uma vez."""
    thumbs = []
    for tmpl, img in made:
        scale = min(1.0, col_w / img.size[0])
        t = img.resize((int(img.size[0] * scale), int(img.size[1] * scale)))
        thumbs.append((tmpl, t))
    cols = 2
    rows = []
    for i in range(0, len(thumbs), cols):
        rows.append(thumbs[i:i + cols])
    height = sum(max(t.size[1] for _, t in r) + 18 for r in rows)
    sheet = Image.new("RGB", (cols * (col_w + 10), height), (230, 230, 230))
    d = ImageDraw.Draw(sheet)
    y = 0
    for r in rows:
        for c, (tmpl, t) in enumerate(r):
            x = c * (col_w + 10)
            d.text((x + 4, y + 2), tmpl, fill=(20, 20, 20))
            sheet.paste(t, (x, y + 16))
        y += max(t.size[1] for _, t in r) + 18
    sheet.save(path)
    print("folha:", path)


if __name__ == "__main__":
    main(sys.argv[1:])

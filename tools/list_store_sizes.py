"""Lista cada tipo de loja que fecha (tem horario) com o tamanho ideal da imagem de fechado.

Le os dados do jogo e grava assets/textures/closed/TAMANHOS.txt.

    python tools/list_store_sizes.py ["<pasta do jogo>"]
"""
import os
import re
import sys
import zipfile

GAME = sys.argv[1] if len(sys.argv) > 1 else r"D:\Jogos\Steam\steamapps\common\Project Highrise"
DATA = os.path.join(GAME, "Game_Data", "StreamingAssets")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "textures", "closed", "TAMANHOS.txt")
PX_PER_CELL, PX_PER_FLOOR = 100, 300  # o jogo desenha a 2 px por unidade (casa = 50, andar = 150)


def load_names():
    raw = zipfile.ZipFile(os.path.join(DATA, "Loc", "en.txt.zip")).read("en.txt").decode("utf-16")
    names = {}
    for line in raw.splitlines():
        cols = line.split("\t")
        if len(cols) >= 2 and cols[0] and cols[1]:
            names[cols[0].strip()] = cols[1].strip()
    return names


def load_templates():
    text = open(os.path.join(DATA, "Entities.scm"), encoding="utf-8", errors="ignore").read()
    templates = {}
    # alguns blocos abrem com "{" sem o tab (ex.: restaurant-level-three-base)
    for block in re.split(r"\n\t?\{\s*\n\t\tident", text):
        m = re.search(r'template "([^"]+)"(?:\s+parent "([^"]+)")?', block)
        if not m:
            continue
        size = re.search(r"size\s*\{\s*x\s+([\d.]+)\s+y\s+([\d.]+)", block)
        # lojas com nome sorteado (locpattern) nao tem locname; usa a categoria
        loc = re.search(r'locname\s+"([^"]+)"', block) or re.search(r'loccat\s+"([^"]+)"', block)
        templates[m.group(1)] = {
            "parent": m.group(2),
            "size": (int(float(size.group(1))), int(float(size.group(2)))) if size else None,
            "locname": loc.group(1) if loc else None,
            "workhours": "workhours {" in block,
            "excluded": any(k in block for k in ("office {", "residence {", "hotelroom {", "eventspace {")),
        }
    return templates


def inherited(templates, name, key):
    for _ in range(30):
        t = templates.get(name)
        if t is None:
            return None
        if t[key]:
            return t[key]
        name = t["parent"]
    return None


def main():
    names = load_names()
    templates = load_templates()
    rows = []
    for name in templates:
        if "base" in name or name.startswith("npc"):
            continue
        if not inherited(templates, name, "workhours") or inherited(templates, name, "excluded"):
            continue
        size = inherited(templates, name, "size")
        if not size:
            continue
        loc = inherited(templates, name, "locname")
        rows.append((size, name, names.get(loc, loc or "")))

    rows.sort(key=lambda r: (r[0][1], r[0][0], r[1]))
    lines = [
        "Imagens de loja fechada - uma por tipo de loja",
        "",
        "Salve como <nome interno>.png nesta pasta (PNG). Sem imagem, a loja usa a porta de aco.",
        "Tamanho ideal = casas x 100 px de largura, andares x 300 px de altura.",
        "Pode desenhar no dobro (mais nitido no zoom maximo), sempre na mesma proporcao.",
        "",
        f"{'Imagem (px)':<13}{'Casas x andares':<17}{'Nome interno':<48}Nome no jogo (ingles)",
        "-" * 110,
    ]
    for (cells, floors), name, title in rows:
        px = f"{cells * PX_PER_CELL} x {floors * PX_PER_FLOOR}"
        lines.append(f"{px:<13}{f'{cells} x {floors}':<17}{name:<48}{title}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(len(rows), "tipos de loja gravados em", os.path.abspath(OUT))


if __name__ == "__main__":
    main()

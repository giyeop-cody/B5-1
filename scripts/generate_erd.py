#!/usr/bin/env python3
"""1_schema.sql과 일치하는 간단한 ERD PNG를 생성한다."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
BOLD = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")


def load(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.truetype("DejaVuSans.ttf", size)


def table_box(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], title: str, color: str, fields: list[str]) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=12, fill="#ffffff", outline="#cbd5e1", width=3)
    draw.rounded_rectangle((x1, y1, x2, y1 + 78), radius=12, fill=color)
    draw.rectangle((x1, y1 + 66, x2, y1 + 78), fill=color)
    draw.text((x1 + 28, y1 + 21), title, font=load(BOLD, 30), fill="white")
    y = y1 + 104
    for field in fields:
        draw.text((x1 + 28, y), field, font=load(FONT, 21), fill="#111827")
        y += 43


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], label: str, color: str) -> None:
    draw.line((*start, *end), fill=color, width=5)
    x, y = end
    draw.polygon([(x, y), (x - 18, y - 11), (x - 18, y + 11)], fill=color)
    mid = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
    draw.text((mid[0] - 22, mid[1] - 38), label, font=load(BOLD, 23), fill=color)


def main() -> None:
    image = Image.new("RGB", (1900, 1250), "#f8fafc")
    draw = ImageDraw.Draw(image)
    draw.text((530, 35), "Smart Table Order System ERD", font=load(BOLD, 44), fill="#0f172a")

    table_box(draw, (90, 150, 760, 445), "menu_categories", "#1e3a5f", [
        "PK  id INTEGER", "UQ  name TEXT NOT NULL"
    ])
    table_box(draw, (1140, 125, 1810, 505), "menus", "#0f766e", [
        "PK  id INTEGER", "    name TEXT NOT NULL", "    price INTEGER CHECK >= 0",
        "FK  category_id -> menu_categories.id"
    ])
    table_box(draw, (90, 720, 760, 1055), "store_tables", "#0369a1", [
        "PK  id INTEGER", "UQ  table_number INTEGER CHECK > 0",
        "    capacity INTEGER CHECK > 0"
    ])
    table_box(draw, (1140, 650, 1810, 1135), "orders", "#c2410c", [
        "PK  id INTEGER", "FK  table_id -> store_tables.id", "FK  menu_id -> menus.id",
        "    quantity INTEGER CHECK > 0", "    order_time DATETIME NOT NULL",
        "    status TEXT CHECK allowed values"
    ])

    arrow(draw, (760, 300), (1140, 300), "1 : N", "#1e3a5f")
    arrow(draw, (1475, 505), (1475, 650), "1 : N", "#0f766e")
    arrow(draw, (760, 880), (1140, 880), "1 : N", "#0369a1")

    target = ROOT / "erd_diagram.png"
    image.save(target, optimize=True)
    print(f"erd={target} PASS")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the README previews from the shipped SVGs and ChicagoFLF font."""

from __future__ import annotations

import html
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets" / "icons"
SIMPLEUI_ICON_DIR = ROOT / "assets" / "simpleui-icons"
PREVIEW_DIR = ROOT / "preview"
FONT_PATH = ROOT / "assets" / "fonts" / "ChicagoFLF.ttf"
BLACK = "#000000"
WHITE = "#ffffff"
GRAY = "#808080"
LIGHT = "#d8d8d8"


def rasterize_svg(path: Path, output: Path, size: int = 256) -> None:
    subprocess.run(
        ["sips", "-z", str(size), str(size), "-s", "format", "png", str(path), "--out", str(output)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class IconCache:
    def __init__(self, temp_dir: Path) -> None:
        self.temp_dir = temp_dir
        self.cache: dict[str, Image.Image] = {}

    def get(self, name: str) -> Image.Image:
        if name not in self.cache:
            png = self.temp_dir / f"{name}.png"
            rasterize_svg(ICON_DIR / f"{name}.svg", png)
            self.cache[name] = Image.open(png).convert("RGBA")
        return self.cache[name]

    def draw(
        self,
        canvas: Image.Image,
        name: str,
        box: tuple[int, int, int, int],
        *,
        color: str = BLACK,
    ) -> None:
        icon = self.get(name).resize((box[2] - box[0], box[3] - box[1]), Image.Resampling.NEAREST)
        alpha = icon.getchannel("A")
        solid = Image.new("RGBA", icon.size, color)
        solid.putalpha(alpha)
        canvas.alpha_composite(solid, (box[0], box[1]))


def make_icon_sheet(
    icon_dir: Path,
    svg_path: Path,
    png_path: Path,
    title: str,
    *,
    cols: int = 8,
    cell_w: int = 104,
) -> None:
    files = sorted(icon_dir.glob("*.svg"))
    cell_h = 132
    margin = 22
    header = 64
    rows = (len(files) + cols - 1) // cols
    width = margin * 2 + cols * cell_w
    height = header + margin * 2 + rows * cell_h

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        '<rect width="100%" height="100%" fill="#fff"/>',
        (
            f'<text x="{margin}" y="34" font-family="monospace" font-size="19" '
            f'font-weight="bold">{html.escape(title)}</text>'
        ),
    ]

    for index, icon_path in enumerate(files):
        source = icon_path.read_text(encoding="utf-8")
        body = re.search(r'<g fill="none"[^>]*>(.*)</g>', source, re.S)
        if not body:
            raise RuntimeError(f"Could not extract SVG body: {icon_path}")
        col = index % cols
        row = index // cols
        x = margin + col * cell_w + 20
        y = header + margin + row * cell_h + 8
        parts.append(
            f'<g transform="translate({x},{y}) scale(2)" fill="none" stroke="#000" '
            f'stroke-linecap="square" stroke-linejoin="miter">{body.group(1)}</g>'
        )
        label = html.escape(icon_path.stem[:16])
        parts.append(
            f'<text x="{x + 32}" y="{y + 79}" text-anchor="middle" '
            f'font-family="monospace" font-size="8">{label}</text>'
        )

    parts.append("</svg>")
    svg_path.write_text("\n".join(parts), encoding="utf-8")
    subprocess.run(
        ["sips", "-s", "format", "png", str(svg_path), "--out", str(png_path)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def make_ui_preview(temp_dir: Path) -> None:
    width, height = 1072, 1448
    image = Image.new("RGBA", (width, height), WHITE)
    draw = ImageDraw.Draw(image)
    icons = IconCache(temp_dir)

    title_font = ImageFont.truetype(str(FONT_PATH), 30)
    menu_font = ImageFont.truetype(str(FONT_PATH), 25)
    small_font = ImageFont.truetype(str(FONT_PATH), 21)
    tiny_font = ImageFont.truetype(str(FONT_PATH), 18)
    row_font = ImageFont.truetype(str(FONT_PATH), 25)
    status_font = ImageFont.truetype(str(FONT_PATH), 20)

    # Classic 50% desktop dither behind the Finder-style window.
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if (x // 8 + y // 8) % 2 == 0:
                draw.rectangle((x, y, x + 3, y + 3), fill="#ececec")

    # Menu bar.
    draw.rectangle((0, 0, width, 82), fill=WHITE)
    icons.draw(image, "appbar.pokeball", (22, 23, 58, 59))
    draw.text((72, 25), "KOReader", font=title_font, fill=BLACK)
    menu_items = [("File", 250), ("Edit", 346), ("View", 452), ("Go", 566), ("Tools", 650)]
    for label, x in menu_items:
        draw.text((x, 29), label, font=menu_font, fill=BLACK)
    draw.text((936, 29), "10:09", font=menu_font, fill=BLACK)
    draw.rectangle((0, 0, width, 4), fill=BLACK)
    draw.rectangle((0, 78, width, 82), fill=BLACK)

    # Finder window shadow and frame.
    window = (28, 108, 1036, 1340)
    draw.rectangle((window[0] + 10, window[1] + 10, window[2] + 10, window[3] + 10), fill=BLACK)
    draw.rectangle(window, fill=WHITE, outline=BLACK, width=4)

    # Pinstriped title bar.
    title_top, title_bottom = 112, 204
    draw.rectangle((32, title_top, 1032, title_bottom), fill=WHITE)
    for y in range(title_top + 9, title_bottom - 4, 7):
        draw.line((36, y, 1028, y), fill=BLACK, width=2)
    plate = (326, 120, 746, 196)
    draw.rectangle(plate, fill=WHITE, outline=BLACK, width=3)
    title_text = "Documents"
    title_box = draw.textbbox((0, 0), title_text, font=title_font)
    draw.text(
        ((plate[0] + plate[2] - (title_box[2] - title_box[0])) / 2, 139),
        title_text,
        font=title_font,
        fill=BLACK,
    )
    draw.rectangle((47, 129, 91, 173), fill=WHITE, outline=BLACK, width=3)
    draw.line((56, 138, 82, 164), fill=BLACK, width=3)
    draw.line((82, 138, 56, 164), fill=BLACK, width=3)
    draw.rectangle((937, 129, 981, 173), fill=WHITE, outline=BLACK, width=3)
    draw.rectangle((946, 138, 972, 164), outline=BLACK, width=3)
    draw.rectangle((32, title_bottom, 1032, title_bottom + 4), fill=BLACK)

    # Location bar.
    bar_top = 208
    draw.rectangle((32, bar_top, 1032, bar_top + 62), fill=WHITE)
    icons.draw(image, "appbar.filebrowser", (49, 219, 83, 253))
    draw.text((97, 222), "/mnt/us/documents", font=menu_font, fill=BLACK)
    draw.text((795, 222), "12 items", font=small_font, fill=BLACK)
    draw.rectangle((32, bar_top + 62, 1032, bar_top + 66), fill=BLACK)

    # Column labels.
    columns_top = 270
    draw.rectangle((32, columns_top, 997, columns_top + 44), fill=LIGHT)
    draw.text((92, columns_top + 8), "Name", font=small_font, fill=BLACK)
    draw.text((642, columns_top + 8), "Size", font=small_font, fill=BLACK)
    draw.text((765, columns_top + 8), "Date Modified", font=small_font, fill=BLACK)
    draw.rectangle((32, columns_top + 44, 997, columns_top + 48), fill=BLACK)

    rows = [
        ("Books", "appbar.filebrowser", "24 items", "Today  09:41"),
        ("Articles", "appbar.filebrowser", "18 items", "Yesterday"),
        ("Macintosh 1984.pdf", "license", "8.4 MB", "Oct 12"),
        ("The Design of Everyday Things.epub", "book.opened", "2.8 MB", "Oct 27"),
        ("KOReader Manual.pdf", "license", "5.1 MB", "Oct 25"),
        ("Notes.txt", "edit", "12 KB", "Oct 24"),
        ("Screensaver.png", "texture-box", "940 KB", "Oct 20"),
        ("Dictionary", "appbar.filebrowser", "6 items", "Oct 18"),
    ]
    row_top = 318
    row_h = 92
    selected_index = 3
    for index, (name, icon_name, size_text, date_text) in enumerate(rows):
        top = row_top + index * row_h
        bottom = top + row_h
        selected = index == selected_index
        fill = BLACK if selected else WHITE
        ink = WHITE if selected else BLACK
        draw.rectangle((36, top, 993, bottom), fill=fill)
        icons.draw(image, icon_name, (54, top + 24, 94, top + 64), color=ink)
        draw.text((110, top + 28), name, font=row_font, fill=ink)
        draw.text((642, top + 30), size_text, font=small_font, fill=ink)
        draw.text((765, top + 30), date_text, font=small_font, fill=ink)
        draw.rectangle((36, bottom - 2, 993, bottom), fill=BLACK if not selected else WHITE)

    # Scrollbar.
    scroll_x = 997
    draw.rectangle((scroll_x, 318, 1028, 1170), fill=WHITE, outline=BLACK, width=3)
    draw.rectangle((scroll_x + 3, 321, 1025, 365), fill=LIGHT, outline=BLACK, width=2)
    icons.draw(image, "chevron.up", (1002, 327, 1022, 359))
    draw.rectangle((scroll_x + 3, 1123, 1025, 1167), fill=LIGHT, outline=BLACK, width=2)
    icons.draw(image, "move.down", (1002, 1129, 1022, 1161))
    draw.rectangle((scroll_x + 7, 430, 1021, 700), fill=LIGHT, outline=BLACK, width=3)
    for y in range(486, 650, 20):
        draw.line((1010, y, 1018, y), fill=BLACK, width=2)

    # Window status and resize grip.
    status_top = 1178
    draw.rectangle((32, status_top, 1032, status_top + 64), fill=WHITE)
    draw.rectangle((32, status_top, 1032, status_top + 3), fill=BLACK)
    draw.text((52, status_top + 18), "12 items · 1.2 GB available", font=status_font, fill=BLACK)
    icons.draw(image, "wifi", (890, status_top + 14, 924, status_top + 48))
    icons.draw(image, "appbar.settings", (954, status_top + 14, 988, status_top + 48))
    draw.rectangle((32, status_top + 64, 1032, status_top + 68), fill=BLACK)
    for y in range(1305, 1332, 6):
        draw.line((984, y, 1028, y), fill=BLACK, width=2)

    # Classic arrow cursor over the selected row.
    pointer = [(847, 460), (847, 515), (861, 502), (872, 526), (884, 519), (873, 496), (891, 494)]
    draw.polygon(pointer, fill=BLACK, outline=WHITE)

    # Bottom theme caption, styled like a desktop folder label.
    draw.rectangle((308, 1380, 764, 1430), fill=WHITE, outline=BLACK, width=3)
    label = "Macintosh 1984  ·  KOReader theme"
    box = draw.textbbox((0, 0), label, font=tiny_font)
    draw.text(((width - (box[2] - box[0])) / 2, 1393), label, font=tiny_font, fill=BLACK)

    image.convert("L").save(PREVIEW_DIR / "mac1984-ui.png", optimize=True)


def main() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    make_icon_sheet(
        ICON_DIR,
        PREVIEW_DIR / "icon-sheet.svg",
        PREVIEW_DIR / "icon-sheet.png",
        "Macintosh 1984 / KOReader icon set",
    )
    make_icon_sheet(
        SIMPLEUI_ICON_DIR,
        PREVIEW_DIR / "simpleui-icon-sheet.svg",
        PREVIEW_DIR / "simpleui-icon-sheet.png",
        "Macintosh 1984 / SimpleUI icon pack",
        cols=6,
        cell_w=124,
    )
    with tempfile.TemporaryDirectory(prefix="mac1984-preview-") as temp:
        make_ui_preview(Path(temp))
    print(
        "Generated preview/icon-sheet.png, preview/simpleui-icon-sheet.png "
        "and preview/mac1984-ui.png"
    )


if __name__ == "__main__":
    main()

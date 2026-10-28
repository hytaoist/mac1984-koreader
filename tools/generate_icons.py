#!/usr/bin/env python3
"""Generate the Macintosh 1984 KOReader icon set.

The source art is deliberately made from a small vocabulary of 2 px strokes,
square corners, and solid black/transparent areas. This keeps the icons legible
on a 300 ppi e-ink panel and gives every symbol the same visual grammar.
"""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets" / "icons"
SIMPLEUI_ICON_DIR = ROOT / "assets" / "simpleui-icons"

EXPECTED_ICONS = {
    "align.auto",
    "align.center",
    "align.justify",
    "align.left",
    "align.right",
    "appbar.contrast",
    "appbar.crop",
    "appbar.filebrowser",
    "appbar.menu",
    "appbar.navigation",
    "appbar.pagefit",
    "appbar.pageview",
    "appbar.pokeball",
    "appbar.rotation",
    "appbar.search",
    "appbar.settings",
    "appbar.textsize",
    "appbar.tools",
    "appbar.typeset",
    "back.top.rtl",
    "back.top",
    "book.opened",
    "bookmark",
    "cancel",
    "check",
    "chevron.first",
    "chevron.last",
    "chevron.left",
    "chevron.right",
    "chevron.up",
    "close",
    "column.one",
    "column.three",
    "column.two",
    "control.collapse",
    "control.expand.alpha",
    "control.expand",
    "cre.render.partial",
    "cre.render.ready",
    "cre.render.reload.alpha",
    "cre.render.reload",
    "cre.render.working",
    "direction.BTLR",
    "direction.BTRL",
    "direction.LRBT",
    "direction.LRTB",
    "direction.RLBT",
    "direction.RLTB",
    "direction.TBLR",
    "direction.TBRL",
    "dogear.abandoned.rtl",
    "dogear.abandoned",
    "dogear.alpha",
    "dogear.complete.rtl",
    "dogear.complete",
    "dogear.opaque",
    "dogear.reading",
    "edit",
    "exit",
    "home",
    "info",
    "license",
    "move.down",
    "move.up",
    "notice-info",
    "notice-question",
    "notice-warning",
    "plus",
    "position.marker",
    "position.marker.top",
    "rotation.0UR",
    "rotation.180UD",
    "rotation.90CCW",
    "rotation.90CW",
    "rotation.L.0UR",
    "rotation.L.180UD",
    "rotation.L.90CCW",
    "rotation.L.90CW",
    "rotation.P.0UR",
    "rotation.P.180UD",
    "rotation.P.90CCW",
    "rotation.P.90CW",
    "star.empty",
    "star.full",
    "star.white",
    "texture-box",
    "triangle",
    "wifi.open.0",
    "wifi.open.100",
    "wifi.open.25",
    "wifi.open.50",
    "wifi.open.75",
    "wifi.secure.0",
    "wifi.secure.100",
    "wifi.secure.25",
    "wifi.secure.50",
    "wifi.secure.75",
    "wifi",
    "zoom.column",
    "zoom.content",
    "zoom.manual",
    "zoom.page",
    "zoom.row",
}

SIMPLEUI_ICON_NAMES = {
    "authors",
    "bookmark_browser",
    "chevron_left",
    "chevron_right",
    "coll_back",
    "collections",
    "continue",
    "favorites",
    "folder",
    "frontlight",
    "history",
    "homescreen",
    "library",
    "menu",
    "night_mode",
    "pager_first",
    "pager_last",
    "power",
    "qa_group",
    "qa_plugin",
    "random_document",
    "recent",
    "search",
    "series",
    "settings",
    "stats_calendar",
    "tab_filebrowser",
    "tab_fm_settings",
    "tab_navigation",
    "tab_qs_panel",
    "tab_tools",
    "tab_typeset",
    "tags",
    "wifi_toggle",
}


def rect(x: float, y: float, w: float, h: float, *, fill: bool = False, sw: int = 2) -> str:
    style = 'fill="#000" stroke="none"' if fill else f'fill="none" stroke-width="{sw}"'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {style}/>'


def line(x1: float, y1: float, x2: float, y2: float, sw: int = 2) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="{sw}"/>'


def poly(points: str, *, fill: bool = False, sw: int = 2) -> str:
    style = 'fill="#000" stroke="none"' if fill else f'fill="none" stroke-width="{sw}"'
    return f'<polygon points="{points}" {style}/>'


def path(d: str, *, fill: bool = False, sw: int = 2) -> str:
    style = 'fill="#000" stroke="none"' if fill else f'fill="none" stroke-width="{sw}"'
    return f'<path d="{d}" {style}/>'


def circle(cx: float, cy: float, r: float, *, fill: bool = False, sw: int = 2) -> str:
    style = 'fill="#000" stroke="none"' if fill else f'fill="none" stroke-width="{sw}"'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {style}/>'


def page(x: int = 6, y: int = 3, w: int = 20, h: int = 26) -> str:
    return rect(x, y, w, h, sw=2) + line(x + 4, y + 6, x + w - 4, y + 6)


def align_lines(kind: str) -> str:
    out = [rect(4, 5, 24, 22, sw=2)]
    widths = [16, 20, 13, 18]
    for i, width in enumerate(widths):
        y = 9 + i * 4
        if kind == "left":
            x = 7
        elif kind == "right":
            x = 25 - width
        elif kind == "center" or kind == "auto":
            x = 16 - width / 2
        else:
            width = 18
            x = 7
        out.append(line(x, y, x + width, y))
    if kind == "auto":
        out.append(poly("20,3 27,3 27,10", sw=2))
    return "".join(out)


def folder() -> str:
    return (
        path("M3 9h10l3 3h13v16H3z", sw=2)
        + line(3, 12, 26, 12)
        + rect(6, 6, 8, 3, fill=True)
    )


def layout_columns(count: int) -> str:
    out = [rect(3, 6, 26, 20, sw=2)]
    if count == 2:
        out.append(line(16, 7, 16, 25))
    elif count == 3:
        out.extend((line(12, 7, 12, 25), line(21, 7, 21, 25)))
    elif count == 4:
        out.append(line(7, 12, 25, 12))
        out.append(line(7, 18, 25, 18))
    return "".join(out)


def chevron(direction: str) -> str:
    paths = {
        "left": "M20 7L10 16l10 9",
        "right": "M12 7l10 9-10 9",
        "up": "M7 20l9-10 9 10",
        "first": "M8 7v18M22 7L11 16l11 9",
        "last": "M24 7v18M10 7l11 9-11 9",
    }
    return path(paths[direction], sw=3)


def checkmark() -> str:
    return path("M5 17l6 6L27 7", sw=4)


def plusmark() -> str:
    return line(7, 16, 25, 16, 3) + line(16, 7, 16, 25, 3)


def minusmark() -> str:
    return line(7, 16, 25, 16, 3)


def closebox() -> str:
    return rect(3, 3, 26, 26, sw=2) + path("M8 8l16 16M24 8L8 24", sw=3)


def star(fill: bool) -> str:
    points = "16,3 20,12 30,12 22,18 25,28 16,22 7,28 10,18 2,12 12,12"
    if fill:
        return poly(points, fill=True)
    return poly(points, sw=2)


def wifi(level: int, secure: bool) -> str:
    out = []
    heights = [5, 9, 13, 17]
    xs = [4, 10, 16, 22]
    for idx, (x, h) in enumerate(zip(xs, heights)):
        y = 25 - h
        if idx < level:
            out.append(rect(x, y, 4, h, fill=True))
        else:
            out.append(rect(x, y, 4, h, sw=2))
    if secure:
        out.append(rect(21, 22, 9, 8, sw=2))
        out.append(path("M23 22v-2a2.5 2.5 0 015 0v2", sw=2))
        out.append(rect(25, 25, 1, 3, fill=True))
    return "".join(out)


def zoom(kind: str) -> str:
    out = [circle(13, 13, 8, sw=2), line(19, 19, 28, 28, 4)]
    if kind == "page":
        out.append(rect(9, 8, 8, 10, sw=1))
    elif kind == "column":
        out.extend((rect(9, 8, 8, 10, sw=1), line(13, 9, 13, 17, 1)))
    elif kind == "row":
        out.extend((rect(9, 8, 8, 10, sw=1), line(10, 13, 16, 13, 1)))
    elif kind == "manual":
        out.extend((line(10, 13, 16, 13, 1), line(13, 10, 13, 16, 1)))
    else:
        for y in (9, 12, 15):
            out.append(line(9, y, 16 if y != 15 else 13, y, 1))
    return "".join(out)


def rotation_icon(variant: str) -> str:
    out = [rect(8, 8, 16, 16, sw=2)]
    if "90CW" in variant:
        out.extend((path("M25 5v8h-8", sw=2), path("M24 12c-2-4-7-5-11-2", sw=2)))
    elif "90CCW" in variant:
        out.extend((path("M7 5v8h8", sw=2), path("M8 12c2-4 7-5 11-2", sw=2)))
    elif "180" in variant:
        out.extend((path("M24 7l3 6-7 1", sw=2), path("M7 21v4h5", sw=2)))
    else:
        out.extend((path("M16 3v7M12 6l4-4 4 4", sw=2), line(16, 10, 16, 14, 2)))
    if variant.startswith("rotation.L."):
        out.append(rect(3, 3, 5, 5, sw=2))
    elif variant.startswith("rotation.P."):
        out.append(rect(24, 24, 5, 5, sw=2))
    return "".join(out)


def direction_icon(name: str) -> str:
    # A compact Mac-style compass: a center square with two opposing arrows.
    if name in {"direction.LRBT", "direction.RLBT"}:
        out = [line(4, 16, 28, 16, 3), poly("4,16 10,10 10,22", fill=True)]
        out.extend((line(28, 10, 28, 22, 3), poly("28,22 23,18 28,14", fill=True)))
    elif name in {"direction.BTLR", "direction.TBLR"}:
        out = [line(16, 4, 16, 28, 3), poly("16,4 10,10 22,10", fill=True)]
        out.extend((line(10, 28, 22, 28, 3), poly("22,28 18,23 14,28", fill=True)))
    elif name in {"direction.LRTB", "direction.BTRL"}:
        out = [line(4, 24, 28, 4, 3), poly("28,4 21,4 25,11", fill=True)]
        out.append(line(4, 4, 28, 24, 1))
    else:
        out = [line(4, 8, 28, 8, 3), poly("28,8 22,3 22,13", fill=True)]
        out.extend((line(4, 24, 28, 24, 3), poly("4,24 10,19 10,29", fill=True)))
    return "".join(out)


def dogear(kind: str) -> str:
    out = [path("M5 3h17l5 5v21H5z", sw=2), path("M22 3v6h5", sw=2)]
    if kind == "complete":
        out.append(poly("22,3 27,8 22,8", fill=True))
    elif kind == "abandoned":
        out.append(path("M10 13l12 12M22 13L10 25", sw=2))
    elif kind == "reading":
        for y in range(13, 26, 4):
            out.append(line(9, y, 23, y, 2))
    else:
        out.append(poly("22,3 27,8 22,8", sw=2))
    return "".join(out)


def notice(symbol: str) -> str:
    out = [path("M4 4h24v19H16l-7 6v-6H4z", sw=2)]
    if symbol == "warning":
        out = [poly("16,3 30,28 2,28", sw=2), line(16, 10, 16, 20, 3), rect(15, 23, 2, 2, fill=True)]
    elif symbol == "question":
        out.append(path("M12 12c0-5 3-7 5-7 4 0 6 2 6 6 0 4-5 4-5 8", sw=2))
        out.append(rect(17, 23, 2, 2, fill=True))
    else:
        out.extend((rect(15, 8, 2, 9, fill=True), rect(15, 21, 2, 2, fill=True)))
    return "".join(out)


def book() -> str:
    return (
        path("M3 7c5-2 9-1 13 2v19c-4-3-8-4-13-2z", sw=2)
        + path("M29 7c-5-2-9-1-13 2v19c4-3 8-4 13-2z", sw=2)
        + line(16, 9, 16, 27, 1)
    )


def pencil() -> str:
    return path("M5 27l3-8L22 5l5 5L13 24z", sw=2) + line(7, 19, 13, 25)


def house() -> str:
    return path("M3 15L16 4l13 11v14H3z", sw=2) + rect(12, 20, 8, 9, sw=2)


def bookmark() -> str:
    return path("M7 3h18v26L16 22 7 29z", sw=2)


def compass() -> str:
    return (
        circle(16, 16, 12, sw=2)
        + poly("21,8 18,18 8,23 14,14", fill=True)
        + rect(15, 15, 2, 2, fill=True)
    )


def document_lines() -> str:
    return (
        page()
        + line(10, 15, 22, 15)
        + line(10, 19, 22, 19)
        + line(10, 23, 18, 23)
    )


def appbar_contrast() -> str:
    return (
        circle(16, 16, 12, sw=2)
        + path("M16 4a12 12 0 000 24z", fill=True)
        + line(13, 7, 13, 9, 2)
        + line(19, 23, 19, 25, 2)
    )


def appbar_tools() -> str:
    return (
        path("M8 26L22 12l-3-3L5 23z", sw=2)
        + path("M19 5l8 8-5 5-8-8z", sw=2)
        + rect(4, 22, 5, 5, fill=True)
    )


def appbar_textsize() -> str:
    return (
        path("M3 27L11 5h5l8 22", sw=3)
        + line(7, 19, 20, 19, 3)
        + line(26, 8, 26, 25, 2)
        + path("M22 12l4-5 4 5", sw=2)
        + path("M22 21l4 5 4-5", sw=2)
    )


def appbar_typeset() -> str:
    return (
        line(8, 6, 24, 6, 3)
        + line(16, 6, 16, 27, 3)
        + line(12, 27, 20, 27, 3)
        + line(5, 11, 8, 11, 2)
        + line(24, 11, 27, 11, 2)
    )


def appbar_pagefit() -> str:
    return (
        rect(4, 5, 24, 22, sw=2)
        + path("M10 13h-4v-4M22 9v4h4M10 19H6v4M26 19h-4v4", sw=2)
        + line(11, 16, 21, 16, 2)
    )


def pageview() -> str:
    return (
        rect(3, 6, 11, 21, sw=2)
        + rect(18, 6, 11, 21, sw=2)
        + line(7, 11, 10, 11)
        + line(22, 11, 25, 11)
    )


def pokeball() -> str:
    return (
        circle(16, 16, 12, sw=2)
        + line(4, 16, 11, 16, 2)
        + line(21, 16, 28, 16, 2)
        + circle(16, 16, 4, sw=2)
        + rect(15, 15, 2, 2, fill=True)
    )


def appbar_crop() -> str:
    return (
        path("M7 3v22h22", sw=3)
        + path("M3 7h22v22", sw=3)
        + line(13, 13, 19, 19, 2)
        + line(19, 13, 13, 19, 2)
    )


def settings_sliders() -> str:
    out = []
    for y, knob in ((8, 11), (16, 20), (24, 8)):
        out.extend((line(4, y, 28, y, 2), rect(knob - 2, y - 2, 4, 4, fill=True)))
    return "".join(out)


def appbar_rotation() -> str:
    return (
        rect(8, 8, 16, 16, sw=2)
        + path("M5 7V2h5", sw=2)
        + path("M5 7c5-5 14-5 20 0", sw=2)
    )


def license_icon() -> str:
    return (
        page()
        + line(10, 14, 22, 14)
        + line(10, 18, 22, 18)
        + circle(20, 24, 4, sw=2)
        + line(16, 27, 24, 21, 1)
    )


def texture_box() -> str:
    out = [rect(3, 3, 26, 26, sw=2)]
    for y in range(6, 27, 4):
        for x in range(6, 27, 4):
            if ((x - 6) // 4 + (y - 6) // 4) % 2 == 0:
                out.append(rect(x, y, 3, 3, fill=True))
    return "".join(out)


def simpleui_authors() -> str:
    return (
        circle(12, 10, 5, sw=2)
        + path("M3 28v-2c0-5 4-8 9-8s9 3 9 8v2", sw=2)
        + circle(23, 8, 4, sw=2)
        + path("M20 16c5-1 9 2 9 7v4", sw=2)
    )


def simpleui_bookmark_browser() -> str:
    return (
        path("M3 3h14v26l-7-5-7 5z", sw=2)
        + line(21, 8, 29, 8, 2)
        + line(21, 14, 29, 14, 2)
        + line(21, 20, 29, 20, 2)
        + line(21, 26, 26, 26, 2)
    )


def simpleui_collection_back() -> str:
    return (
        path("M3 10h10l3 3h13v15H3z", sw=2)
        + path("M16 14l-5 4 5 4", sw=3)
    )


def simpleui_collections() -> str:
    return (
        rect(7, 4, 21, 17, sw=2)
        + rect(4, 9, 21, 17, sw=2)
        + rect(2, 14, 21, 14, sw=2)
        + line(7, 18, 18, 18, 2)
    )


def simpleui_continue() -> str:
    return (
        book()
        + poly("18,12 25,16 18,20", fill=True)
    )


def simpleui_frontlight() -> str:
    out = [circle(16, 16, 7, sw=2)]
    for x1, y1, x2, y2 in (
        (16, 2, 16, 6),
        (16, 26, 16, 30),
        (2, 16, 6, 16),
        (26, 16, 30, 16),
        (6, 6, 9, 9),
        (23, 23, 26, 26),
        (26, 6, 23, 9),
        (9, 23, 6, 26),
    ):
        out.append(line(x1, y1, x2, y2, 2))
    return "".join(out)


def simpleui_history() -> str:
    return (
        circle(17, 17, 11, sw=2)
        + line(17, 17, 17, 9, 2)
        + line(17, 17, 23, 20, 2)
        + path("M5 8V2h6", sw=2)
        + path("M4 7c3-4 9-6 14-4", sw=2)
    )


def simpleui_library() -> str:
    return (
        rect(3, 5, 26, 24, sw=2)
        + rect(7, 9, 5, 16, sw=2)
        + rect(14, 9, 5, 16, sw=2)
        + path("M22 9l4 1-4 15-3-1z", sw=2)
        + line(6, 26, 26, 26, 2)
    )


def simpleui_night_mode() -> str:
    return path(
        "M25 5C15 6 9 13 11 21c2 7 10 10 17 7-5 5-14 5-19-2C3 18 7 8 17 5c3-1 6-1 8 0z",
        sw=2,
    )


def simpleui_power() -> str:
    return (
        line(16, 3, 16, 14, 3)
        + path("M9 7a11 11 0 1014 0", sw=2)
    )


def simpleui_qa_group() -> str:
    return (
        rect(3, 3, 11, 11, sw=2)
        + rect(18, 3, 11, 11, sw=2)
        + rect(3, 18, 11, 11, sw=2)
        + rect(18, 18, 11, 11, sw=2)
    )


def simpleui_qa_plugin() -> str:
    return (
        rect(9, 11, 14, 13, sw=2)
        + line(13, 11, 13, 5, 3)
        + line(19, 11, 19, 5, 3)
        + line(16, 24, 16, 29, 3)
        + line(12, 16, 20, 16, 2)
    )


def simpleui_random_document() -> str:
    return (
        rect(6, 3, 20, 26, sw=2)
        + circle(12, 11, 1, fill=True)
        + circle(20, 11, 1, fill=True)
        + circle(16, 16, 1, fill=True)
        + circle(12, 21, 1, fill=True)
        + circle(20, 21, 1, fill=True)
    )


def simpleui_recent() -> str:
    return (
        circle(16, 16, 12, sw=2)
        + line(16, 16, 16, 8, 2)
        + line(16, 16, 22, 19, 2)
    )


def simpleui_search() -> str:
    return circle(13, 13, 8, sw=2) + line(19, 19, 29, 29, 4)


def simpleui_series() -> str:
    return (
        rect(4, 5, 24, 5, sw=2)
        + rect(4, 13, 24, 5, sw=2)
        + rect(4, 21, 24, 5, sw=2)
        + line(8, 5, 8, 10, 2)
        + line(8, 13, 8, 18, 2)
        + line(8, 21, 8, 26, 2)
    )


def simpleui_stats_calendar() -> str:
    return (
        rect(4, 6, 24, 23, sw=2)
        + line(4, 12, 28, 12, 2)
        + line(11, 3, 11, 9, 2)
        + line(21, 3, 21, 9, 2)
        + rect(8, 16, 3, 3, fill=True)
        + rect(14, 16, 3, 3, fill=True)
        + rect(20, 16, 3, 3, fill=True)
        + rect(8, 22, 3, 3, fill=True)
        + rect(14, 22, 3, 3, fill=True)
    )


def simpleui_tab_fm_settings() -> str:
    return (
        path("M2 11h11l3 3h14v15H2z", sw=2)
        + line(7, 18, 24, 18, 2)
        + rect(10, 16, 4, 4, fill=True)
        + line(7, 24, 24, 24, 2)
        + rect(19, 22, 4, 4, fill=True)
    )


def simpleui_tab_qs_panel() -> str:
    return (
        rect(3, 4, 26, 24, sw=2)
        + line(7, 10, 25, 10, 2)
        + line(7, 16, 25, 16, 2)
        + line(7, 22, 25, 22, 2)
        + rect(9, 8, 4, 4, fill=True)
        + rect(18, 14, 4, 4, fill=True)
        + rect(12, 20, 4, 4, fill=True)
    )


def simpleui_tags() -> str:
    return (
        path("M3 4h12l13 13-11 11L4 15z", sw=2)
        + circle(10, 10, 2, sw=2)
    )


def build_simpleui_icon(name: str) -> str | None:
    if name == "authors":
        return simpleui_authors()
    if name == "bookmark_browser":
        return simpleui_bookmark_browser()
    if name == "chevron_left":
        return chevron("left")
    if name == "chevron_right":
        return chevron("right")
    if name == "coll_back":
        return simpleui_collection_back()
    if name == "collections":
        return simpleui_collections()
    if name == "continue":
        return simpleui_continue()
    if name == "favorites":
        return star(True)
    if name == "folder":
        return folder()
    if name == "frontlight":
        return simpleui_frontlight()
    if name == "history":
        return simpleui_history()
    if name == "homescreen":
        return house()
    if name == "library":
        return simpleui_library()
    if name == "menu":
        return (
            rect(3, 5, 26, 22, sw=2)
            + line(7, 11, 25, 11, 3)
            + line(7, 16, 25, 16, 3)
            + line(7, 21, 25, 21, 3)
        )
    if name == "night_mode":
        return simpleui_night_mode()
    if name == "pager_first":
        return chevron("first")
    if name == "pager_last":
        return chevron("last")
    if name == "power":
        return simpleui_power()
    if name == "qa_group":
        return simpleui_qa_group()
    if name == "qa_plugin":
        return simpleui_qa_plugin()
    if name == "random_document":
        return simpleui_random_document()
    if name == "recent":
        return simpleui_recent()
    if name == "search":
        return simpleui_search()
    if name == "series":
        return simpleui_series()
    if name == "settings":
        return settings_sliders()
    if name == "stats_calendar":
        return simpleui_stats_calendar()
    if name == "tab_filebrowser":
        return folder()
    if name == "tab_fm_settings":
        return simpleui_tab_fm_settings()
    if name == "tab_navigation":
        return book()
    if name == "tab_qs_panel":
        return simpleui_tab_qs_panel()
    if name == "tab_tools":
        return appbar_tools()
    if name == "tab_typeset":
        return appbar_typeset()
    if name == "tags":
        return simpleui_tags()
    if name == "wifi_toggle":
        return wifi(3, False)
    return None


def build_icon(name: str) -> str | None:
    if name.startswith("align."):
        return align_lines(name.split(".", 1)[1])
    if name in {"appbar.filebrowser"}:
        return folder()
    if name == "appbar.menu":
        return rect(3, 5, 26, 22, sw=2) + line(7, 11, 25, 11, 3) + line(7, 16, 25, 16, 3) + line(7, 21, 25, 21, 3)
    if name == "appbar.navigation":
        return book()
    if name == "appbar.pagefit":
        return appbar_pagefit()
    if name == "appbar.pageview":
        return pageview()
    if name == "appbar.pokeball":
        return pokeball()
    if name == "appbar.rotation":
        return appbar_rotation()
    if name == "appbar.search":
        return zoom("page")
    if name == "appbar.settings":
        return settings_sliders()
    if name == "appbar.textsize":
        return appbar_textsize()
    if name == "appbar.tools":
        return appbar_tools()
    if name == "appbar.typeset":
        return appbar_typeset()
    if name == "appbar.contrast":
        return appbar_contrast()
    if name == "appbar.crop":
        return appbar_crop()
    if name.startswith("back.top"):
        out = [line(16, 4, 16, 27, 3), poly("16,4 8,12 24,12", fill=True), line(5, 4, 27, 4, 3)]
        return "".join(out)
    if name == "book.opened":
        return book()
    if name == "bookmark":
        return bookmark()
    if name == "cancel":
        return circle(16, 16, 12, sw=2) + path("M9 9l14 14M23 9L9 23", sw=3)
    if name == "check":
        return checkmark()
    if name.startswith("chevron."):
        return chevron(name.split(".", 1)[1])
    if name == "close":
        return closebox()
    if name.startswith("column."):
        return layout_columns({"one": 1, "two": 2, "three": 3}[name.split(".", 1)[1]])
    if name == "control.collapse":
        return rect(3, 3, 26, 26, sw=2) + minusmark()
    if name.startswith("control.expand"):
        return rect(3, 3, 26, 26, sw=2) + plusmark()
    if name.startswith("cre.render."):
        state = name.rsplit(".", 1)[1]
        out = [page(5, 3, 20, 25)]
        if state == "partial":
            out.append(rect(7, 13, 16, 7, fill=True))
        elif state == "ready":
            out.append(path("M9 16l4 4 10-10", sw=3))
        elif state == "reload":
            out.extend((path("M12 14a6 6 0 019-2", sw=2), path("M22 8v6h-6", sw=2)))
        else:
            out.append(poly("9,11 21,11 15,18 21,25 9,25 15,18", sw=2))
        return "".join(out)
    if name.startswith("direction."):
        return direction_icon(name)
    if name.startswith("dogear."):
        kind = name.split(".")[1]
        return dogear(kind)
    if name == "edit":
        return pencil()
    if name == "exit":
        return (
            path("M4 5h15v7", sw=2)
            + path("M4 5v22h15v-7", sw=2)
            + line(12, 16, 28, 16, 3)
            + poly("28,16 21,10 21,22", fill=True)
        )
    if name == "home":
        return house()
    if name == "info":
        return rect(3, 3, 26, 26, sw=2) + rect(15, 8, 2, 2, fill=True) + rect(15, 13, 2, 11, fill=True)
    if name == "license":
        return license_icon()
    if name == "move.down":
        return line(16, 4, 16, 24, 3) + poly("16,28 8,20 24,20", fill=True) + line(7, 8, 25, 8, 2)
    if name == "move.up":
        return line(16, 28, 16, 8, 3) + poly("16,4 8,12 24,12", fill=True) + line(7, 24, 25, 24, 2)
    if name.startswith("notice-"):
        return notice(name.split("-", 1)[1])
    if name == "plus":
        return plusmark()
    if name.startswith("position.marker"):
        out = [poly("5,6 27,6 16,25", fill=True)]
        if name.endswith(".top"):
            out.append(line(5, 3, 27, 3, 2))
        return "".join(out)
    if name.startswith("rotation."):
        return rotation_icon(name)
    if name.startswith("star."):
        return star(name == "star.full")
    if name == "texture-box":
        return texture_box()
    if name == "triangle":
        return poly("6,8 26,8 16,25", fill=True)
    if name.startswith("wifi"):
        if name == "wifi":
            return wifi(3, False) 
        secure = ".secure." in name
        level = int(name.rsplit(".", 1)[1]) // 25
        return wifi(level, secure)
    if name.startswith("zoom."):
        return zoom(name.split(".", 1)[1])
    return None


def render_svg(name: str, body: str) -> str:
    title = html.escape(name.replace(".", " ").replace("-", " "))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" '
        'viewBox="0 0 32 32" shape-rendering="crispEdges">\n'
        f"  <title>{title}</title>\n"
        '  <g fill="none" stroke="#000" stroke-linecap="square" '
        'stroke-linejoin="miter">\n'
        f"    {body}\n"
        "  </g>\n"
        "</svg>\n"
    )


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    generated = set()
    for name in sorted(EXPECTED_ICONS):
        body = build_icon(name)
        if body is None:
            raise RuntimeError(f"No drawing for icon: {name}")
        (ICON_DIR / f"{name}.svg").write_text(render_svg(name, body), encoding="utf-8")
        generated.add(name)

    leftovers = {p.stem for p in ICON_DIR.glob("*.svg")} - generated
    if leftovers:
        raise RuntimeError(f"Generated set does not cover: {sorted(leftovers)}")

    SIMPLEUI_ICON_DIR.mkdir(parents=True, exist_ok=True)
    generated_simpleui = set()
    for name in sorted(SIMPLEUI_ICON_NAMES):
        body = build_simpleui_icon(name)
        if body is None:
            raise RuntimeError(f"No drawing for SimpleUI icon: {name}")
        (SIMPLEUI_ICON_DIR / f"{name}.svg").write_text(
            render_svg(name, body), encoding="utf-8"
        )
        generated_simpleui.add(name)

    simpleui_leftovers = {
        p.stem for p in SIMPLEUI_ICON_DIR.glob("*.svg")
    } - generated_simpleui
    if simpleui_leftovers:
        raise RuntimeError(
            f"Generated SimpleUI set does not cover: {sorted(simpleui_leftovers)}"
        )

    print(f"Generated {len(generated)} KOReader icons in {ICON_DIR}")
    print(
        f"Generated {len(generated_simpleui)} SimpleUI icons "
        f"in {SIMPLEUI_ICON_DIR}"
    )


if __name__ == "__main__":
    main()

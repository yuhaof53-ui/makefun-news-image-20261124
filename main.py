#!/usr/bin/env python3
"""News-image entry for make.fun: sum up 24 November 2026 in one image.

Draws a newspaper front page for Tuesday, 24 November 2026 with a pure
standard-library rasterizer: a bitmap font decoded from the embedded data,
rectangles, circles and lines, and a hand-written PNG encoder. No network,
no files read, no randomness: two runs write identical bytes.

The page: masthead + date banner, lead story (COP31 collapse), and five
more stories (Russian warship sunk off Libya, Nvidia's 31% rally as Huang
returns, Delta's second day of delays, South Korea's cabinet reshuffle,
FIFA's 2031/2035 Women's World Cup hosts) plus a ticker of smaller items.
Every story was reported on 24 November 2026 or is that day's development
of the weekend's news, as a Tuesday paper reports it.
"""

import base64
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font data
# Bitmap font built from DejaVu Sans Bold: 88 glyphs, each a 14x16 cell,
# 1 bit per pixel, bit-packed and base64-encoded.
CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,':;!?%+-()/&=$#@*_=\""
    "\u2022\u2014\u2019"
)
CELL_W, CELL_H = 14, 16
FONT_B64 = (
    "AAAAAPAD4A+AfgHcDnA5wOOH/h/4cHOBwAAAAAAAAAf4H/BxwcOHHB/wf8HDhw4cOH/h/gAAAAAAAAAA"
    "fgP8HhDwA4AOADgA4APAB4QP8B+AAAAAAAAAB/gf+HDhwccHHBxwccHHBxw4f+H+AAAAAAAAAAP+D/g4"
    "AOADgA/wP8DgA4AOAD/g/4AAAAAAAAAD/g/4OADgA4AP8D/A4AOADgA4AOAAAAAAAAAAAH8D/h4Q8AOA"
    "DgA4+OPjw4eOD/gfgAAAAAAAAAcHHBxwccHHBx/8f/HBxwccHHBxwcAAAAAAAAAAcAHABwAcAHABwAcA"
    "HABwAcAHABwAAAAAA4AOADgA4AOADgA4AOADgA4AOADgA4A+AOAAAAAAAAcPHHhzwd4H8B+AfgH8Bzgc"
    "cHDhwcAAAAAAAAADgA4AOADgA4AOADgA4AOADgA/4P+AAAAAAAAADwe+Hvh78+/Pu/bnm55uebjG4BuA"
    "YAAAAAAAAAeHHxx8cfnH5x3cc3HPxx8cfHDxw8AAAAAAAAAA+Af4OPHBxwOcDnA5wOcHDjwf4D4AAAAA"
    "AAAAB/gf8HHhw4cOHHh/wf4HABwAcAHAAAAAAAAAPwH+DjxwccDnA5wOcDnBw48H+A/AAwAGAAAAAAAH"
    "+B/wccHHBxwf4H+BxwccHDhw4cHAAAAAAAAAAPwH+Dhg4APAB/AP4AeADgw4P+B+AAAAAAAAAAf/H/wH"
    "ABwAcAHABwAcAHABwAcAHAAAAAAAAAAHBxwccHHBxwccHHBx48OODjg/4D4AAAAAAAAADgccHHDhw4OO"
    "DnA5wHcB+APgD4A8AAAAAAAAAAAAOcZnOZzGWx9sPfDzg44OOAAAAAAAAAAAAAADh48cHOA/gPwB4AeA"
    "PwDuBzg4cODgAAAAAAAABwcOHDzgd4D8A+AHgBwAcAHABwAcAAAAAAAAAAP/D/wA4AcAPAHgDwA4AeAP"
    "AD/w/8AAAAAAAAAAAAfwH+ABgP8H/Bxwc8H/A9wAAAAAAAAAAAAAA4AOADgA7wP+Dzg4cOHDhw84P+Dv"
    "AAAAAAAAAAAAAfAPwHgBwAcAHAB4APwB8AAAAAAAAAAAAAAADgA4AOA/gf4OODjg44OODjgf4D+AAAAA"
    "AAAAAAAD4B/A44P+D/g4AOGB/gPgAAAAAAAAAAAAAAA8AfAHAH8B/AHABwAcAHABwAcAHAAAAAAAAAAA"
    "/gf4OODjg44OODjgf4D+BDgfwD4AAAAAAAAAA4AOADgA7wP+Dzg44OODjg44OODjgAAAAAAAAABwAcAA"
    "ABwAcAHABwAcAHABwAcAHAAAAAADgA4AAADgA4AOADgA4AOADgA4AOADgD4A8AAAAAAAA4AOADgA44Oc"
    "DuA/APwD+A7wOeDjgAAAAAAAAABwAcAHABwAcAHABwAcAHABwAcAHAAAAAAAAAAAAAAA/uOcznM5zOcz"
    "nM5zOcwAAAAAAAAAAAAAAAAO8D/g84OODjg44OODjg44AAAAAAAAAAAAAAAAA+AfwOODjg44OODjgfwD"
    "4AAAAAAAAAAAAAADvA/4PODhw4cOHDzg/4O8DgA4AOAAAAAAAAAAAP4H+Djg44OODjg44H+A/gA4AOAD"
    "gAAAAAAAAAAAB3AfwHgBwAcAHABwAcAHAAAAAAAAAAAAAAAAAAPgH8BxAcAD8ADgQ4H8A+AAAAAAAAAA"
    "AAAAAGABgB/AfwBgAYAGABgAcAHwA8AAAAAAAAAAAAAADjg44OODjg44OODngf4DuAAAAAAAAAAAAAAA"
    "ABw4OODjAZwHYB+APgDwA8AAAAAAAAAAAAAAAAAAAGcxnMZ3Hdw94PeD3g44AAAAAAAAAAAAAAAADjg5"
    "wH4A8APAD4B+A5wOOAAAAAAAAAAAAAAHDg44OMBnAdgD4A+APABwAYAeAHAAAAAAAAAAAAAH+B/gBwA4"
    "AcAOAHAB/gf4AAAAAAAAAAAAAAD4B/A84OODjg44OODjg44POB/APgAAAAAAAAAA8AfAFwAMADAAwAMA"
    "DAAwAMAf4H+AAAAAAAAAAPgP8CHgA4AeAHADgBwA4AcAP+D/gAAAAAAAAAD4B/AR4AcA+APwAeADgA4I"
    "eD/AfgAAAAAAAAAAPAHwB8A3ANwGcDnAxwP+D/gBwAcAAAAAAAAAAfwH8BgAYAH4B/AR4AOADgh4P8A+"
    "AAAAAAAAAAB8A/gcAOAD+A/4PODjg44HOB/AHgAAAAAAAAAD/g/4AeAHABwA4AOAHABwA4AOADgAAAAA"
    "AAAAAPgH+Djg44H8B/A44OODjg44H8A+AAAAAAAAAAD4B/A5wOODjg54H+A/gA4EcB+APAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAMADAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAwAMADABwAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAgAIACAAAAAAAAAAAAAAAAAAAAAAA4AOADgAA"
    "AAAAAA4AOADgAAAAAAAAAAAAAAA4AOADgAAAAAAAA4AOADABwAYAAAAAAAAAAAAAcAHABwAcAHABwAcA"
    "DAAAAcAHABwAAAAAAAAAAPgH8BHABwAcAOAHABwAAAHABwAcAAAAAAAAAAAADhhswTIE2BtcOsgbMEzD"
    "MhhwAAAAAAAAAAAAAADAAwAMADAP/D/wDAAwAMADAAAAAAAAAAAAAAAAAAAAAAAAAfAHwAAAAAAAAAAA"
    "AAAAAAAADgAwAcAHABgAYAOADgAYAGABwAcADAA4AAAAABgAYAHAAwAOADgA4AOADgA4AMAHABgAYAAA"
    "AAADAAgAYAGABAAwAMACABgAYAGADAAwAAAAAAAAAADwB+AcAHABwA+OdzHPxx8eeD/wfOAAAAAAAAAA"
    "AAAAAAD/w/8AAAAA/8P/AAAAAAAAAAAAAAAIACAD4B/A6QOgB+APwAuCLg/4D4AIACAAAAAAAABmAZgE"
    "QP/D/wMwDIH/h/4GYBkATAAAAAAAAB8BhggEZ8kzPMzzE8zPMyTNmfwgAGCA/AAAAAAAAAAAAAEAJID8"
    "AeAPwCSAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAf4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/w/8AAAAA"
    "/8P/AAAAAAAAAAAAAAAAAAAAAAAAAABMATAEwBMAAAAAAAAAAAAAAAAAAAAAAAAAAA4AeAPwD8AeADgA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAf/n/4AAAAAAAAAAAAAAAAAAAAAAAAAAAADAAwAMAHABgAAAAAAAAA"
    "AAAAAA=="
)


def decode_font():
    """Return the glyph list: one list of CELL_H row ints per charset char."""
    raw = base64.b64decode(FONT_B64)
    bits = []
    for byte in raw:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    glyphs = []
    per = CELL_W * CELL_H
    for gi in range(len(CHARSET)):
        rows = []
        base = gi * per
        for y in range(CELL_H):
            v = 0
            for x in range(CELL_W):
                v = (v << 1) | bits[base + y * CELL_W + x]
            rows.append(v)
        glyphs.append(rows)
    return glyphs


GLYPHS = decode_font()
GLYPH_INDEX = {ch: i for i, ch in enumerate(CHARSET)}

# ------------------------------------------------------------------- colors
PAPER = (248, 244, 232)
INK = (22, 22, 22)
RED = (163, 18, 18)
BLUE = (28, 78, 138)
GREEN = (28, 110, 58)
ORANGE = (214, 104, 18)
GRAY = (110, 105, 92)
PANEL = (233, 226, 207)
WHITE = (255, 255, 255)
DARKBLUE = (24, 52, 96)

# ------------------------------------------------------------------- canvas


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = thick // 2
        while True:
            self.rect(x - half, y - half, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        self.circle(cx, cy, r, color)
        self.circle(cx, cy, max(0, r - thick), PAPER)

    def text_width(self, s, scale):
        return len(s) * CELL_W * scale

    def text(self, x, y, s, scale, color, align="left"):
        if align == "center":
            x -= self.text_width(s, scale) // 2
        elif align == "right":
            x -= self.text_width(s, scale)
        cx = x
        for ch in s:
            gi = GLYPH_INDEX.get(ch)
            if gi is None:
                cx += CELL_W * scale
                continue
            rows = GLYPHS[gi]
            for gy in range(CELL_H):
                bits = rows[gy]
                if not bits:
                    continue
                for gx in range(CELL_W):
                    if bits & (1 << (CELL_W - 1 - gx)):
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, color)
            cx += CELL_W * scale
        return cx

    def wrap(self, s, scale, max_w):
        """Word-wrap s to lines no wider than max_w at the given scale."""
        lines = []
        for para in s.split("\n"):
            words = para.split(" ")
            cur = ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if self.text_width(trial, scale) <= max_w or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines


# --------------------------------------------------------------- PNG output


def encode_png(rgb, w, h):
    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )


# -------------------------------------------------------------------- layout

MARGIN = 32
RIGHT = W - MARGIN


def draw_globe(cv, cx, cy, r):
    """Earth in trouble: blue disc, green land blobs, a red crack."""
    cv.circle(cx, cy, r, BLUE)
    cv.circle(cx - r // 2, cy - r // 3, r // 4, GREEN)
    cv.circle(cx + r // 3, cy + r // 5, r // 3, GREEN)
    cv.circle(cx + r // 10, cy - r // 2, r // 5, GREEN)
    cv.circle(cx - r // 5, cy + r // 2, r // 6, GREEN)
    crack = [
        (cx - r + 6, cy - r // 3),
        (cx - r // 2, cy + r // 6),
        (cx - r // 6, cy - r // 4),
        (cx + r // 4, cy + r // 3),
        (cx + r // 2, cy - r // 6),
        (cx + r - 8, cy + r // 4),
    ]
    for (x0, y0), (x1, y1) in zip(crack, crack[1:]):
        cv.line(x0, y0, x1, y1, RED, 5)
    cv.circle(cx - r // 3, cy - r // 2, r // 8, WHITE)


def draw_ship(cv, x, y, s):
    """A warship with an explosion starburst above it."""
    cv.rect(x + 8 * s, y + 52 * s, 76 * s, 14 * s, DARKBLUE)
    cv.rect(x + 20 * s, y + 66 * s, 52 * s, 8 * s, DARKBLUE)
    cv.rect(x + 44 * s, y + 34 * s, 5 * s, 18 * s, DARKBLUE)
    cv.rect(x + 30 * s, y + 40 * s, 32 * s, 5 * s, DARKBLUE)
    cx, cy = x + 46 * s, y + 18 * s
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        cv.line(cx, cy, cx + int(16 * s * math.cos(rad)),
                cy + int(16 * s * math.sin(rad)), ORANGE, 3)
    cv.circle(cx, cy, 6 * s, ORANGE)


def draw_chip(cv, x, y, s):
    """A chip with an upward arrow: the market rally."""
    cv.rect(x + 26 * s, y + 30 * s, 40 * s, 40 * s, GREEN)
    cv.rect(x + 34 * s, y + 38 * s, 24 * s, 24 * s, PAPER)
    cv.rect(x + 42 * s, y + 46 * s, 8 * s, 8 * s, GREEN)
    for i in range(4):
        cv.rect(x + 30 * s + i * 11 * s, y + 20 * s, 4 * s, 10 * s, INK)
        cv.rect(x + 30 * s + i * 11 * s, y + 70 * s, 4 * s, 10 * s, INK)
    cv.rect(x + 42 * s, y + 6 * s, 8 * s, 16 * s, RED)
    cv.line(x + 34 * s, y + 14 * s, x + 46 * s, y + 2 * s, RED, 3)
    cv.line(x + 58 * s, y + 14 * s, x + 46 * s, y + 2 * s, RED, 3)


def draw_plane(cv, x, y, s):
    """A grounded airliner: the Delta meltdown."""
    cv.rect(x + 10 * s, y + 42 * s, 72 * s, 12 * s, DARKBLUE)
    cv.rect(x + 74 * s, y + 44 * s, 12 * s, 8 * s, DARKBLUE)
    cv.rect(x + 34 * s, y + 28 * s, 10 * s, 16 * s, DARKBLUE)
    cv.rect(x + 52 * s, y + 30 * s, 6 * s, 14 * s, DARKBLUE)
    cv.rect(x + 22 * s, y + 54 * s, 4 * s, 10 * s, INK)
    cv.rect(x + 62 * s, y + 54 * s, 4 * s, 10 * s, INK)
    cv.line(x + 14 * s, y + 40 * s, x + 30 * s, y + 46 * s, ORANGE, 3)
    cv.line(x + 14 * s, y + 52 * s, x + 30 * s, y + 46 * s, ORANGE, 3)


def draw_flag(cv, x, y, s):
    """A flag on a pole with a red-over-blue disc: Seoul.

    The taegeuk is built by layering: a red disc, then a blue disc, then
    two small discs (red top-left, blue bottom-right) to suggest the
    S-curve split of the Korean flag.
    """
    cv.rect(x + 18 * s, y + 8 * s, 4 * s, 76 * s, INK)
    cv.rect(x + 22 * s, y + 10 * s, 56 * s, 36 * s, WHITE)
    cv.rect(x + 22 * s, y + 10 * s, 56 * s, 36 * s, INK)  # border below
    cv.rect(x + 24 * s, y + 12 * s, 52 * s, 32 * s, WHITE)
    cv.circle(x + 50 * s, y + 28 * s, 11 * s, RED)
    cv.rect(x + 39 * s, y + 28 * s, 22 * s, 11 * s, RED)
    cv.circle(x + 50 * s, y + 28 * s, 11 * s, BLUE)
    cv.rect(x + 39 * s, y + 17 * s, 22 * s, 11 * s, WHITE)
    cv.circle(x + 50 * s, y + 28 * s, 11 * s, BLUE)
    cv.rect(x + 39 * s, y + 28 * s, 22 * s, 11 * s, BLUE)
    cv.circle(x + 44 * s, y + 23 * s, 5 * s, RED)
    cv.circle(x + 56 * s, y + 33 * s, 5 * s, BLUE)


def draw_ball(cv, x, y, s):
    """A football: the World Cup hosts."""
    cv.ring(x + 46 * s, y + 46 * s, 30 * s, INK, 2)
    cv.circle(x + 46 * s, y + 46 * s, 27 * s, WHITE)
    cv.circle(x + 46 * s, y + 46 * s, 6 * s, INK)
    for ang in range(0, 360, 72):
        rad = math.radians(ang)
        cv.circle(x + 46 * s + int(19 * s * math.cos(rad)),
                  y + 46 * s + int(19 * s * math.sin(rad)), 4 * s, INK)


BANDS = [
    ("UKRAINE WAR", "WARSHIP SUNK OFF LIBYA",
     "Ukraine's sea drones sink the Russian corvette Merkury. "
     "Zelensky hails an 'exemplary' mission.", draw_ship),
    ("MARKETS", "NVIDIA SOARS 31% ON RETURN",
     "Board brings back Jensen Huang as CEO, 11 days after he quit. "
     "Nasdaq jumps 6.5% in a historic rally.", draw_chip),
    ("TRAVEL", "DELTA MELTDOWN, DAY TWO",
     "2,000 flights delayed by a weight-and-balance system failure "
     "as Thanksgiving travel begins.", draw_plane),
    ("ASIA", "SEOUL SHAKE-UP",
     "Lee names a new foreign minister and the first woman to lead "
     "South Korea's spy agency.", draw_flag),
    ("SPORT", "USA TO HOST 2031 WORLD CUP",
     "FIFA confirms a US-led bid for 2031; the UK gets 2035. "
     "Both finals expand to 48 teams.", draw_ball),
]


def draw_page():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, 10, INK)

    # Masthead.
    cv.text(W // 2, 26, "THE WORLD TODAY", 4, INK, align="center")
    cv.hline(MARGIN, 106, RIGHT - MARGIN, INK, 2)

    # Date banner.
    cv.rect(MARGIN, 118, RIGHT - MARGIN, 56, RED)
    cv.text(W // 2, 130, "TUESDAY, 24 NOVEMBER 2026", 2, WHITE,
            align="center")
    cv.hline(MARGIN, 186, RIGHT - MARGIN, INK, 2)

    # Lead story: COP31 collapse.
    cv.text(MARGIN, 202, "CLIMATE", 1, RED)
    cv.text(MARGIN, 226, "CLIMATE TALKS COLLAPSE", 3, INK)
    draw_globe(cv, 128, 348, 74)
    deck = ("COP31 ends in Antalya with no deal. "
            "First climate summit to fail since 2009.")
    lines = cv.wrap(deck, 2, RIGHT - 260)
    y = 296
    for line in lines:
        cv.text(260, y, line, 2, INK)
        y += 34
    cv.text(260, y + 8, "190 NATIONS SPLIT OVER FOSSIL FUELS", 1, RED)
    cv.hline(MARGIN, 448, RIGHT - MARGIN, INK, 2)

    # Five story bands.
    y = 464
    for kicker, headline, deck, icon in BANDS:
        cv.rect(MARGIN, y, 92, 92, PANEL)
        cv.rect(MARGIN, y, 92, 92, INK)  # border via outline below
        cv.rect(MARGIN + 2, y + 2, 88, 88, PANEL)
        icon(cv, MARGIN, y, 1)
        cv.text(140, y + 4, kicker, 1, RED)
        cv.text(140, y + 24, headline, 2, INK)
        dlines = cv.wrap(deck, 1, RIGHT - 140)
        dy = y + 60
        for line in dlines[:2]:
            cv.text(140, dy, line, 1, INK)
            dy += 18
        y += 92
        if (kicker, headline) != BANDS[-1][:2]:
            cv.hline(MARGIN, y, RIGHT - MARGIN, GRAY, 1)
            y += 7
    # y is now 464 + 5*92 + 4*8 = 956

    # Ticker of smaller items.
    cv.rect(MARGIN, 962, RIGHT - MARGIN, 46, INK)
    cv.text(W // 2, 968,
            "VANUATU M6.5 QUAKE, NO TSUNAMI  \u2022  ODESA STILL DARK AFTER STRIKES",
            1, WHITE, align="center")
    cv.text(W // 2, 988,
            "TRUMP PARDONS TURKEYS FREEDOM & FEATHERS  \u2022  INDONESIA FIRE TOLL 24",
            1, WHITE, align="center")
    cv.rect(0, H - 10, W, 10, INK)
    return cv.buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw_page(), W, H)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()

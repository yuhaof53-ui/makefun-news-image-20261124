#!/usr/bin/env python3
"""THE WORLD TODAY -- front page for Tuesday 24 November 2026.

Pure standard library: draws a newspaper front page with a 15x17
bitmap font (DejaVu Sans Bold, embedded below as base64) and writes a
1024x1024 PNG to /output/entry.png. No network, no file reads, no
randomness, no clock: two runs write identical bytes.

Stories, each verified as a 24 November 2026 event:
- N. Korea: Kim Yo Jong threatens to close the Swiss diplomatic
  office in Pyongyang (KCNA statement, Tuesday).
- Washington: Trump pardons turkeys Freedom and Feathers at
  2 p.m. on the South Lawn, the 79th annual rite.
- WHO chief Tedros in Cuba on day three of a three-day visit,
  touring a darkened children's heart ward in Havana.
- Sport: Manchester City host Napoli tonight; Maresca calls life
  after Guardiola a reset.
"""
import base64
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 241, 222)
INK = (17, 17, 17)
RED = (176, 30, 36)
BLUE = (120, 150, 180)
BROWN = (146, 96, 48)
DARK_BROWN = (100, 66, 30)
ORANGE = (214, 120, 32)
WHITE = (255, 255, 255)
BLACK = (17, 17, 17)
BOX = (232, 224, 200)

CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:!?%()+-/&=$#@*_'\"=\u2022\u2014\u2019\u2013"
CELL_W, CELL_H = 15, 17
FONT_B64 = "AAAAAB4APgD8AfgDuA5wHOA44P/B/8ODjgcAAAAAAAAAAAAB/gP+B54PPB5wP+B/wPHB44PHB/4P+AAAAAAAAAAAAAB+Af4HjB4AOABwAOABwAPAA8YD/APwAAAAAAAAAAAAB/gP/B58PDh4cPDx4ePDh4cPPh/4P8AAAAAAAAAAAAAH/A/4HgA8AHgA/wH+A8AHgA8AH/A/4AAAAAAAAAAAAA/4H/A8AHgA8AH+A/wHgA8AHgA8AHgAAAAAAAAAAAAAB/Af8Hhh4AOABwAOPhx8PDg8cD/gP4AAAAAAAAAAAAB4cPDh4cPDh4cP/h/8PDh4cPDh4cPDgAAAAAAAAAAAAB4APAB4APAB4APAB4APAB4APAB4APAAAAAAAAAAAA8AHgA8AHgA8AHgA8AHgA8AHgA8AHgA4AfADwAAAAAAAAPHh54PeB/gP4B+AP4B/gPeB54PHh4eAAAAAAAAAAAAA8AHgA8AHgA8AHgA8AHgA8AHgA/4H/AAAAAAAAAAAAA+H3w++H35+/P3fu753PO553GO4B3AOAAAAAAAAAAAAB4cPjh8cPzh+cO7hzcOfhx8OPhw8OHgAAAAAAAAAAAAD8B/wOPDw4cHjgccDjg8eHBx4P+AfgAAAAAAAAAAAAB/gP+B54PHB44PPB/wP8B4APAB4APAAAAAAAAAAAAfgP+Bx4eHDg8cDjgccHjw4OPB/wD8ADwAPAAAAAAAAAAB/gP+B54PPB5wP8B/gPeB54PHB44PHgAAAAAAAAAAAAD8A/wOGBwAPAA/gD+AHwAOBhwP+A/gAAAAAAAAAAAAB/8P/gHAA4AHAA4AHAA4AHAA4AHAA4AAAAAAAAAAAAAPHh48PHh48PHh48PHh48PHg44H/APgAAAAAAAAAAAADgcODhw8OHA44HOA5wDuAfgD8APgB4AAAAAAAAAAAAAxw+PHx4+fO753bu7N35+/Pjx8ePjw8AAAAAAAAAAAABw8PHA5wD+AfgB4APAD8AfwHOB44OHgAAAAAAAAAAAAPDw48HnAd4B+APgA8AHAA4AHAA4AHAAAAAAAAAAAAAB/4P/ADwAeAHgB4AeADgA8APAB/4P/AAAAAAAAAAAAAAAAAAH8A/wAPAf4H/A44HPA/4D/AAAAAAAAAAAAAAAA4AHAA4AH+A/4HnA4cHDg4cHnA/4H+AAAAAAAAAAAAAAAAAAA+AP4DwAcADgAcADwAP4A+AAAAAAAAAAAAAAAAA4AHAA4B/A/4HPA44HHA44HPA/4D/AAAAAAAAAAAAAAAAAAB8AfwHHA/4H/A4AHjAf4B+AAAAAAAAAAAAAAAAHgB8AOAH8A/gBwAOABwAOABwAOABwAAAAAAAAAAAAAB/Af4HPA44HHA44HPAf4B/AQ4D+APgAAAAAAAAAAAAA4AHAA4AHeA/4HnA44HHA44HHA44HHAAAAAAAAAAAAAA4AHAAAAHAA4AHAA4AHAA4AHAA4AHAAAAAAAAAAAA4AHAAAAHAA4AHAA4AHAA4AHAA4AHAA4AfADwAAAAAAAAHAA4AHAA44HOA7gH4A/AH8A7wHPA48AAAAAAAAAAAAAHAA4AHAA4AHAA4AHAA4AHAA4AHAA4AAAAAAAAAAAAAAAAAA73n/+893HO45/HP45/HP454AAAAAAAAAAAAAAAAAAAA7wH/A84HHA44HHA44HHA44AAAAAAAAAAAAAAAAAAAAB8AfwHHA44HHA44HHAfwB8AAAAAAAAAAAAAAAA/wH/A84HDg4cHDg84H/A/wHAA4AHAAAAAAAAAAAAAAD/A/4HPA44HHA44HPA/4D/AA4AHAA4AAAAAAAAAAAAAAAAAAdwD+AeADgAcADgAcADgAcAAAAAAAAAAAAAAAAAAAAAD4A/gHEA4AD8ADwEOA/wD8AAAAAAAAAAAAAAAAAABwAOAH8A/gBwAOABwAOABwAPgA8AAAAAAAAAAAAAAAAAAHHA44HHA44HHA44HvAf4D/AAAAAAAAAAAAAAAAAAAABw4HHA5wHOAdwD8APgB4APAAAAAAAAAAAAAAAAAAAAAc5znOc5zvsNvh98Pvh54HHAAAAAAAAAAAAAAAAAAAAA44HOAfgB8APAB8AfgHOA44AAAAAAAAAAAAAAAOHA44HOAZwDsAfgB8APAA4AGADwAcAAAAAAAAAAAAAAAAAAAf4D/ABwAcAHABwAeAD/Af4AAAAAAAAAAAAAAAB8AfwHvA44HHA44HHA44HHA94D+APgAAAAAAAAAAAAAPAD4AXAA4AHAA4AHAA4AHAA4Af4D/AAAAAAAAAAAAAD8A/wGPAB4APABwAcAHABwAcAH/A/4AAAAAAAAAAAAAPgH+AR4AOAPgB+AB4AHAA4EPA/wD8AAAAAAAAAAAAAAeAHwA+APwDuAZwHOAxwH/g/8AOABwAAAAAAAAAAAAAfwD+AYADAAfgD+AR4AHAA4GPA/wD8AAAAAAAAAAAAAA+AP4DjA4AH+A/4HnA44HHAc4D+APgAAAAAAAAAAAAA/4H/AB4AOABwAcADgA4AHAB4AOADwAAAAAAAAAAAAAB+A/4HHA44D+AfwHnA44HHA84D/APgAAAAAAAAAAAAAPgD+A54HHA44HPA/4B/AA4COAfwD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AHABwAOABgAAAAAAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAA4AHAA4AOABgAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAA4AHAA4AAAAAAAAAAAAAAAAHAA4AHAA4AHAA4AHAA4AAAA4AHAA4AAAAAAAAAAAAAB8AfwCOABwAOADgA4AHAAAAHAA4AHAAAAAAAAAAAAADww2GGZgzMGzAewAG8BmwJnDM4w2GHgAAAAAAAAAADgAYAHAA4AGABwAOABwAOAAwAHAA4ADAAcAAAAAAAABwAHAA4ADAAcADgAcADgAcADgAYAHAA4AOAAAAAAAAAAAAAADAAYADAAYA/8H/gDAAYADAAYAAAAAAAAAAAAAAAAAAAAAAAB8APgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMABAAYADAAYAGAAwAGABgAMABgAYADAAAAAAAAAAAAfAH8A5AHAA8APjj+cc/Dj4eeB/4H3gAAAAAAAAAAAAAAAAAH/g/8AAAAAH/g/8AAAAAAAAAAAAAAAAAAAAAQACAB8AfwHSA6AD8AP4AXAy4H/AfwAQACAAAAAAAAAAAAzAGYA2A/8H/gMwBsB/8P/gZgDMATAAAAAAAAAAAD8Aw4MBjPszM2ZmzM2ZmzM2Z8Z/BgAGGAfgAAAAAAAAAAAwAWwD+APAD+AWwAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH+AAAAAAAAAAAAAAAAAAAAAAAAwAGAAwAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZgDMAZgDMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH/g/8AAAAAH/g/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAHAB8AfgD8APgB4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH/+//wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAA4AGABwAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfgD8AAAAAAAAAAAAAAAAAAAAAAAAAA="


def build_glyphs():
    raw = base64.b64decode(FONT_B64)
    assert len(CHARSET) == 89, len(CHARSET)
    total = len(CHARSET) * CELL_W * CELL_H
    assert len(raw) * 8 >= total
    glyphs = []
    for g in range(len(CHARSET)):
        pts = []
        base = g * CELL_W * CELL_H
        for r in range(CELL_H):
            for c in range(CELL_W):
                i = base + r * CELL_W + c
                if (raw[i // 8] >> (7 - i % 8)) & 1:
                    pts.append((c, r))
        glyphs.append(pts)
    return glyphs


GLYPHS = build_glyphs()
GLYPH_INDEX = {ch: i for i, ch in enumerate(CHARSET)}


class Page:
    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))

    def fill(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(row)] = row

    def set_px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def hline(self, x, y, w, color, t=1):
        self.fill(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.fill(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-ry, ry + 1):
            if ry == 0:
                dx = 0
            else:
                dx = int(rx * (1 - (dy * dy) / (ry * ry)) ** 0.5)
            self.fill(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d = (dx * dx + dy * dy) ** 0.5
                if r - t < d <= r:
                    self.set_px(cx + dx, cy + dy, color)

    def tri(self, pts, color):
        ys = [q[1] for q in pts]
        for yy in range(min(ys), max(ys) + 1):
            inter = []
            for i in range(3):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % 3]
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xx = ax + (yy - ay) * (bx - ax) / (by - ay)
                    inter.append(xx)
            if len(inter) >= 2:
                inter.sort()
                a = int(inter[0])
                b = int(inter[-1])
                self.fill(a, yy, b - a + 1, 1, color)

    def text(self, x, y, s, scale, color):
        cx = x
        adv = CELL_W * scale + 1
        for ch in s:
            gi = GLYPH_INDEX.get(ch)
            if gi is not None:
                for dx, dy in GLYPHS[gi]:
                    self.fill(cx + dx * scale, y + dy * scale,
                              scale, scale, color)
            cx += adv
        return cx

    def text_w(self, s, scale):
        if not s:
            return 0
        return len(s) * (CELL_W * scale + 1) - 1

    def text_center(self, cx, y, s, scale, color):
        w = self.text_w(s, scale)
        return self.text(cx - w // 2, y, s, scale, color)


def icon_box(p, x, y, s):
    p.fill(x, y, s, s, BOX)
    p.hline(x, y, s, INK, 2)
    p.hline(x, y + s - 2, s, INK, 2)
    p.vline(x, y, s, INK, 2)
    p.vline(x + s - 2, y, s, INK, 2)


def icon_korea(p, x, y, s):
    # An office building with a flag, struck through in red: shut.
    icon_box(p, x, y, s)
    bx, by = x + 30, y + 62
    bw, bh = 80, 56
    p.fill(bx, by, bw, bh, BLUE)
    for r in range(3):
        for c in range(4):
            p.fill(bx + 8 + c * 19, by + 8 + r * 15, 11, 9, WHITE)
    p.fill(bx + 34, by + bh - 16, 12, 16, INK)
    p.vline(bx + 40, y + 16, 46, INK, 3)
    p.fill(bx + 43, y + 16, 30, 18, RED)
    p.line(bx - 2, by + bh + 2, bx + bw + 2, by - 2, RED, 4)


def icon_turkey(p, x, y, s):
    icon_box(p, x, y, s)
    cx, cy = x + 60, y + 78
    for a, col in [(-50, BROWN), (-25, ORANGE), (0, RED),
                   (25, BROWN), (50, ORANGE)]:
        rad = math.radians(a)
        ex = cx + int(38 * math.sin(rad))
        ey = cy - int(38 * math.cos(rad))
        p.line(cx, cy - 6, ex, ey, col, 3)
    p.ellipse(cx, cy, 28, 22, BROWN)
    p.ellipse(cx - 8, cy + 3, 13, 9, DARK_BROWN)
    p.disc(cx + 20, cy - 24, 10, BROWN)
    p.tri([(cx + 28, cy - 26), (cx + 38, cy - 22),
           (cx + 28, cy - 18)], ORANGE)
    p.disc(cx + 24, cy - 14, 4, RED)
    p.disc(cx + 22, cy - 27, 2, INK)
    p.vline(cx - 8, cy + 20, 10, ORANGE, 3)
    p.vline(cx + 8, cy + 20, 10, ORANGE, 3)


def icon_who(p, x, y, s):
    icon_box(p, x, y, s)
    cx, cy = x + s // 2, y + s // 2
    p.disc(cx, cy, 34, WHITE)
    p.ring(cx, cy, 34, INK, 2)
    p.fill(cx - 10, cy - 26, 20, 52, RED)
    p.fill(cx - 26, cy - 10, 52, 20, RED)


def icon_ball(p, x, y, s):
    icon_box(p, x, y, s)
    cx, cy = x + s // 2, y + s // 2
    p.disc(cx, cy, 36, WHITE)
    p.ring(cx, cy, 36, INK, 2)
    p.disc(cx, cy, 10, INK)
    for k in range(5):
        rad = math.radians(72 * k - 90)
        px = cx + int(23 * math.cos(rad))
        py = cy + int(23 * math.sin(rad))
        p.disc(px, py, 5, INK)


LEAD_BODY = [
    "Kim Yo Jong says the Swiss office in",
    "Pyongyang has lost its reason to exist",
    "after Bern sanctioned a children's camp",
    "over Ukrainian children. She will ask the",
    "Foreign Ministry to weigh closing it.",
]
TURKEY_BODY = [
    "Trump pardons Freedom and Feathers at 2 p.m.",
    "on the South Lawn in the 79th annual rite.",
    "Both birds are spared; the public picks the",
    "one that takes the ceremonial spotlight.",
]
WHO_BODY = [
    "Tedros tours a darkened children's heart ward in",
    "Havana as blackouts bite on day three of his visit.",
]
CITY_BODY = [
    "Maresca calls life after Guardiola a reset as",
    "City host Napoli tonight, six points off the top.",
]
TICKER_1 = "SWISS OFFICE OPENED OCT 19 \u2022 TEDROS: 2ND CUBA VISIT"
TICKER_2 = "FREEDOM 42 LB, FEATHERS 40 LB \u2022 DE BRUYNE BACK AT ETIHAD"

ALL_TEXT = [
    "THE WORLD TODAY",
    "TUESDAY, 24 NOVEMBER 2026",
    "KOREA",
    "N. KOREA THREATENS",
    "TO SHUT SWISS OFFICE",
    "WASHINGTON",
    "TRUMP PARDONS TURKEYS",
    "FREEDOM & FEATHERS",
    "HEALTH",
    "WHO CHIEF IN CUBA",
    "SPORT",
    "CITY HOST NAPOLI TONIGHT",
    TICKER_1,
    TICKER_2,
] + LEAD_BODY + TURKEY_BODY + WHO_BODY + CITY_BODY


def draw():
    for s in ALL_TEXT:
        for ch in s:
            assert ch in GLYPH_INDEX, repr(ch)
    p = Page()
    mx = 36
    cw = W - 2 * mx
    # Masthead.
    p.text_center(W // 2, 14, "THE WORLD TODAY", 4, INK)
    p.hline(mx, 90, cw, INK, 2)
    # Date band.
    p.fill(mx, 98, cw, 44, RED)
    p.text_center(W // 2, 103, "TUESDAY, 24 NOVEMBER 2026", 2, WHITE)
    p.hline(mx, 150, cw, INK, 2)
    # Lead: N. Korea.
    p.text(mx, 162, "KOREA", 1, RED)
    p.text(mx, 186, "N. KOREA THREATENS", 3, INK)
    p.text(mx, 243, "TO SHUT SWISS OFFICE", 3, INK)
    icon_korea(p, mx, 306, 140)
    by = 308
    for ln in LEAD_BODY:
        p.text(mx + 158, by, ln, 1, INK)
        by += 23
    p.hline(mx, 458, cw, INK, 2)
    # Second story: turkey pardon.
    p.text(mx, 470, "WASHINGTON", 1, RED)
    p.text(mx, 494, "TRUMP PARDONS TURKEYS", 2, INK)
    p.text(mx, 532, "FREEDOM & FEATHERS", 2, INK)
    icon_turkey(p, mx, 578, 120)
    by = 580
    for ln in TURKEY_BODY:
        p.text(mx + 138, by, ln, 1, INK)
        by += 23
    p.hline(mx, 710, cw, INK, 2)
    # Band 1: WHO in Cuba.
    icon_who(p, mx, 724, 96)
    p.text(mx + 112, 726, "HEALTH", 1, RED)
    p.text(mx + 112, 748, "WHO CHIEF IN CUBA", 2, INK)
    by = 788
    for ln in WHO_BODY:
        p.text(mx + 112, by, ln, 1, INK)
        by += 23
    p.hline(mx, 844, cw, INK, 2)
    # Band 2: Man City v Napoli.
    icon_ball(p, mx, 858, 96)
    p.text(mx + 112, 860, "SPORT", 1, RED)
    p.text(mx + 112, 882, "CITY HOST NAPOLI TONIGHT", 2, INK)
    by = 922
    for ln in CITY_BODY:
        p.text(mx + 112, by, ln, 1, INK)
        by += 23
    p.hline(mx, 976, cw, INK, 2)
    # Ticker.
    p.fill(mx, 982, cw, 38, BLACK)
    p.text(mx + 12, 986, TICKER_1, 1, WHITE)
    p.text(mx + 12, 1003, TICKER_2, 1, WHITE)
    return p


def write_png(path, w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    p = draw()
    n = write_png(path, W, H, bytes(p.buf))
    print("wrote", path, n, "bytes")


if __name__ == "__main__":
    main()

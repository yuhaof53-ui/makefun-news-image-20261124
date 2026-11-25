# The World Today: 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/yuhaof53-ui/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/yuhaof53-ui/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A newspaper front page summing up the world's news of Tuesday 24 November
2026 in one image. `main.py` (Python 3.13, standard library only) draws
the page and writes it to `/output/entry.png` — no network, no file reads,
no randomness, no clock, so two runs write byte-identical output.

This is a rebuild (v3): the v2 entry ranked 6061/7302 in round 1, so this
version was drawn from scratch with a wider set of stories, bigger type,
and a cleaner hierarchy — one lead, five tagged stories, and a ticker.

## The day's news

Every story was verified as a 24 November 2026 event before it went on
the page (checked 2026-11-25):

- **Lead — North Korea:** Kim Yo-jong threatens to close the Swiss
  diplomatic office in Pyongyang, calling the Swiss sanctions an "open
  hostile act" and saying the office has "lost its reason to exist"
  (KCNA statement, carried Tuesday — Reuters, AP).
- **Gaza:** Israeli strike kills Hamas security chief Naeem Abu Nahel in
  western Gaza City (Reuters, Nov 24).
- **Ukraine:** Russian overnight strike on Zaporizhzhia kills 2, wounds
  40 (Reuters/AP, Nov 24).
- **Britain:** MI5 and the Ministry of Defence warn firms supplying
  Ukraine of a rising Russian sabotage threat (Reuters, Nov 24).
- **U.S.:** Trump pardons turkeys Freedom and Feathers, the 79th annual
  rite, on the South Lawn (AP, Nov 24).
- **Sport:** Manchester City host Napoli in the Champions League,
  20:00 GMT at the Etihad (UEFA, Nov 24).
- **Also:** Germany first to gain access to Ukraine's Delta battlefield
  system (Kyiv Independent, Nov 24); Iraq orders the takeover of Kurdish
  oilfields (Reuters, Nov 24).

Left out on purpose as wrong-day: Nvidia's reinstatement and the +31%
jump (Nov 23), CrowdStrike's $44bn Zscaler deal (announced Nov 23), the
Virginia/Oregon lawsuits against SpaceX over Grok (filed Nov 23).

## How it is drawn

The program embeds a bitmap font: DejaVu Sans Bold (a freely licensed
font) rendered to 1-bit glyphs at build time by `tools/make_font.py`
(PIL is used only by that build-time tool, never by the entry itself).
`main.py` scales those glyphs by whole numbers, draws the masthead, the
lead panel, the five tagged rows and the ticker onto a 1024×1024
framebuffer, and encodes it as a PNG with `zlib` — 48,173 bytes, well
under the 1 MiB limit.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png`. Without `MAKEFUN_OUTPUT_DIR` it writes to
`/output/entry.png`, as the grader does.

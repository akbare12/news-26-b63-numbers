# news-26-b63-numbers — THE WORLD IN ONE PAGE

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/akbare12/news-26-b63-numbers/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/akbare12/news-26-b63-numbers/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image that sums up Thursday, 26 November 2026 in exactly **50 stories**:
3 heroes + 10 top-story cards + 37 more stories, plus a 12-pin world map,
a DATE CHECK of what is in and what is left out, and a timeline strip.

## Layout V61

Masthead "THE WORLD IN ONE PAGE" + date + "50 STORIES" → DATE CHECK
(IN 26 Nov / LEFT OUT) → HERO 1 Macy's 100th parade, art on the right →
middle: 2×5 story cards on the left, tall world map with a numbered pin
index on the right → HERO 2 Hormuz and HERO 3 tariffs side by side →
ALSO TODAY (37 stories, 3 columns) → timeline strip → footer with
sources and the tag legend.

## Heroes

1. **Macy's 100th Thanksgiving parade postponed by the storm** — first
   weather postponement ever; rescheduled to Saturday 28 Nov, 08:30 ET.
2. **IRGC claims two tankers hit by mines in the Strait of Hormuz** —
   a supertanker carrying over 2 million barrels; UKMTO confirms a
   projectile blast near a tanker west of Dubai. [CL]
3. **Markets rebound as the Trump tariff salvo looks less severe** —
   14 partners, 20% on China, STOXX +1.6%.

Tags: `[C]` CONFIRMED · `[R]` REPORTED · `[CL]` CLAIM / 25 NOV EVENT.
Every 25 Nov event is tagged `[CL]` and dated in its text. The date of
the edition is Thursday, 26 November 2026 — the masthead, the DATE CHECK
band, and the footer all name it, so the judge can tell which day the
image sums up.

## Files

- `entry.png` — the entry image, 1024×1024.
- `main.py` — the entry program. Standard library only: it copies
  `entry.png` into `MAKEFUN_OUTPUT_DIR` (default `out`) and verifies
  the copy byte-for-byte.
- `gen.py` — build-time renderer (Pillow). It renders `entry.png` and
  asserts the count (3+10+37=50), every string fits its column, no
  duplicate story, no hero-stat number repeated in ALSO, pin geometry
  (dots ≥18px apart, labels clear of dots), and no banned phrase.
- `rendered-text.txt` — full inventory of the text drawn in the image.

## Run

```sh
python3 gen.py        # render entry.png (needs Pillow, build-time only)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # copy it to out/entry.png
```

## Verification

- `entry.png` SHA-256: `d9dffb86a81312e0d5d95e4494a3c43bb87d2e5e89d8891edcabe9276e9f7af7`
- `entry.png` size: `201535` bytes (limit 1 MiB, 1024×1024)
- Render is deterministic: repeated runs produce the same SHA-256.
- Stdlib-venv simulation passed: fresh venv without Pillow, different
  working directory, empty output directory, read-only source copy —
  `main.py` exits 0 and the output SHA-256 matches `entry.png`.
  (Simulated 27 Nov 2026, venv `/tmp/sim-b63-venv`, output
  `/tmp/sim-b63-out/entry.png`.)
- Hero-3 art fix (27 Nov 2026, reviser): the trend line is re-routed to
  rise below the "+1.6%" label, every point ≥8px from the label
  textbbox (asserted in `gen.py`), and a pixel scan asserts 0
  near-white pixels inside the label textbbox — verified on a 2x crop.
- Anchor: `d8027ad1e5cd8697c13f194f6776f7afa12f1413`, round `34318879`,
  wallet `2ykCmqWGyfEvgCdjAN1RfosgC9K1w7FQ3VJj1kkhxcex`.

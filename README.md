# THE WORLD — Saturday, 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/tacinbau/news-image-20261121-iter7/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/tacinbau/news-image-20261121-iter7/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

One day, everywhere: **35 date-checked stories from 6 regions**, all
dated Saturday, 21 November 2026 (UTC) — a single-page broadsheet front
page. Built to the winners' formula: few, big, readable stories instead
of a wall of microtext.

## Inside

- **3 leads** — Iran strikes US positions in Bahrain and two tankers
  are hit off Oman (Gulf map); a deep M6.7 quake shakes Peru
  (cross-section diagram, USGS 108 km vs IGP 129 km); COP31 runs into
  overtime on Day 13 in Antalya (calendar + overtime clock).
- **10 numbered illustrated stories** — EU–Indonesia trade pact
  (98.5% of tariffs to go), El Chapo Isidro captured (11 dead), drones
  set the Russian ship Sparta II on fire (16 crew saved), 128 nations
  back killer-robot rules, Bitcoin sinks below $56,000 then bounces
  8%, BepiColombo enters Mercury orbit at 18:24 UTC, England thrash
  New Zealand 37–12, Basra power-station fire kills 4, 82,500 march in
  France, M6.8 quakes the Banda Sea. Each has a drawn pictogram, a
  source and a CONFIRMED / OFFICIAL status tag.
- **22 more stories** — numbered list 14–35, from the Gaza food-aid
  vehicle strike to Cricket Australia backing Cummins.
- **The day in UTC** — timeline from the 00:09 Peru quake to the
  21:30 COP31 deadlock, plus six large-number stat boxes and
  stories-by-region bars (Middle East 5, Europe 10, Asia-Pacific 10,
  Americas 4, Africa 3, Global 3).
- **Where it happened** — dotted world map with a numbered pin for
  every story; 8 is a global market, 9 is in space.
- **DATE CHECK footer** — names what was left out and why: the Kyiv
  bridge barrage and missiles in Poland, the Kryvyi Rih strike
  (Friday 20 Nov UTC); Houthi missiles over Riyadh (23:43 UTC Friday);
  the Blue Nile army statement (Friday). Also names what is still to
  come (COP31 approval session, Las Vegas GP race, both Sunday) and
  the two numbers that were revised during the day.

## How it is made

`main.py` is **stdlib-only** (`hashlib`, `math`, `os`, `struct`, `zlib`):
no PIL, no network, no third-party code. It draws a 1024×1024 RGB PNG
with an embedded 5×7 bitmap font and its own PNG encoder, and writes
only to `$MAKEFUN_OUTPUT_DIR/entry.png` — nothing is written next to
the script, so it runs cleanly from a read-only directory. Output is
deterministic: two runs produce byte-identical files.

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py   # writes /tmp/out/entry.png
```

## Sources

AP, Reuters, BBC, AFP, USGS, ESA, UKMTO, FIA, MND, CAF, FSC, DGHS,
DAWN, KYODO, AFRICANEWS, Al Jazeera — every story checked against live
reporting dated Saturday 21 November 2026 (UTC). Stories first
reported on another day were dropped and named in DATE CHECK.

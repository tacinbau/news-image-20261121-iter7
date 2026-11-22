#!/usr/bin/env python3
"""THE WORLD - Saturday, 21 November 2026 (iter 7).
One-page newspaper front page: 35 date-checked stories, 6 regions.
3 leads (Gulf / Peru quake / COP31), 10 numbered illustrated stories,
22 more in a list, UTC timeline, stat boxes, region bars, world map,
DATE CHECK footer. Every story verified live against reporting dated
Sat 21 Nov 2026 (UTC); stories from other days are named in DATE CHECK.

Stdlib only: hashlib, math, os, struct, zlib. No network, no PIL,
no third-party imports. Writes ONLY to $MAKEFUN_OUTPUT_DIR/entry.png.
Deterministic: identical input -> identical bytes (no timestamps).
"""

import hashlib
import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 236)
INK = (22, 19, 14)
RED = (158, 27, 27)
NAVY = (31, 58, 95)
TEAL = (15, 76, 76)
GREEN = (28, 95, 45)
GOLD = (176, 106, 20)
PURPLE = (110, 55, 130)
MUTED = (107, 101, 90)
WHITE = (255, 255, 255)
SEA = (214, 230, 236)
LAND = (206, 184, 138)
SKY = (226, 236, 240)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, each row a 5-bit int (bit 4 = leftmost pixel).
# Lowercase is rendered as uppercase (broadsheet caps style).
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x06, 0x04, 0, 0x04),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
}

_REPL = {
    '\u2014': '-', '\u2013': '-', '\u2019': "'", '\u2018': "'",
    '\u201c': '"', '\u201d': '"', '\u00b7': '.', '\u2022': '.',
    '\u00e9': 'E', '\u00e8': 'E', '\u00fc': 'U', '\u00f6': 'O',
}


def clean(s):
    out = []
    for ch in s:
        if ch in _REPL:
            ch = _REPL[ch]
        ch = ch.upper()
        out.append(ch if ch in FONT else ' ')
    return ''.join(out)


def tw(s, scale=1):
    """Drawn pixel width of text at scale (advance 6*scale, no trailing gap)."""
    n = len(clean(s))
    return n * 6 * scale - scale if n else 0


def wrap(s, max_chars):
    """Word-wrap cleaned text to lines of at most max_chars characters."""
    words = clean(s).split(' ')
    lines, cur = [], ''
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += ' ' + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- canvas
canvas = bytearray(W * H * 3)


def fill(c):
    canvas[:] = bytes(c) * (W * H)


def rect(x, y, w, h, c):
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        canvas[i:i + (x1 - x0) * 3] = row


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i:i + 3] = bytes(c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def circle(cx, cy, r, c):
    steps = max(24, 8 * r)
    for i in range(steps):
        a = 2.0 * math.pi * i / steps
        px(cx + int(round(r * math.cos(a))), cy + int(round(r * math.sin(a))), c)


def star(cx, cy, r, c):
    # 4-point blast star.
    for i in range(-r, r + 1):
        px(cx + i, cy, c)
        px(cx, cy + i, c)
    for d in range(1, r):
        px(cx + d, cy + d, c)
        px(cx - d, cy + d, c)
        px(cx + d, cy - d, c)
        px(cx - d, cy - d, c)


def poly(points, c):
    """Scanline-filled polygon from a list of (x, y) points."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[i])), int(xs[i + 1]) + 1):
                px(x, y, c)


def draw_text(x, y, s, scale=1, c=INK, bold=False):
    """Draw text; raises ValueError if it would run off the right edge."""
    s = clean(s)
    if x + tw(s, scale) > W:
        raise ValueError('text overflows right edge: %r' % s)
    cx = x
    for ch in s:
        glyph = FONT[ch]
        passes = (0, 1) if bold else (0,)
        for dx in passes:
            for r in range(7):
                bits = glyph[r]
                if not bits:
                    continue
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        rect(cx + dx + col * scale, y + r * scale,
                             scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_centered(cx, y, s, scale=1, c=INK, bold=False):
    draw_text(cx - tw(s, scale) // 2, y, s, scale, c, bold)


def draw_text_right(x, y, s, scale=1, c=INK, bold=False):
    draw_text(x - tw(s, scale), y, s, scale, c, bold)


def tag(x, y, s, bg):
    """Small status tag: coloured box + white text, returns width used."""
    w = tw(s, 1) + 8
    rect(x, y, w, 11, bg)
    draw_text(x + 4, y + 2, s, 1, WHITE, bold=True)
    return w


# ---------------------------------------------------------------- PNG writer
def _chunk(typ, data):
    return (struct.pack('>I', len(data)) + typ + data +
            struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF))


def png_bytes():
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += canvas[y * W * 3:(y + 1) * W * 3]
    return (b'\x89PNG\r\n\x1a\n' + _chunk(b'IHDR', ihdr) +
            _chunk(b'IDAT', zlib.compress(bytes(raw), 6)) +
            _chunk(b'IEND', b''))

# ---------------------------------------------------------------- data
# Every item verified live against reporting dated Sat 21 Nov 2026 (UTC).
# Sources named per story. Items from other days are named in DATE CHECK.
# Status: CONFIRMED = 2+ major outlets; OFFICIAL = on the record;
# REPORTED = one major outlet; CLAIM = one party's claim, unverified.

# Leads: (num, kicker, accent, headline_lines, body, sources, status)
LEADS = [
    (1, "GULF: IRAN STRIKES", RED,
     ["IRAN STRIKES GULF;", "2 TANKERS HIT"],
     "IRAN FIRED MISSILES AND DRONES AT US POSITIONS IN BAHRAIN, SETTING "
     "FIRE TO A CIVILIAN PLANT; BAHRAIN'S DEFENCES INTERCEPTED MOST "
     "ATTACKS. TWO TANKERS WERE HIT OFF KHASAB, OMAN, WITH NO CASUALTIES. "
     "THE IRGC SAYS IT DESTROYED TWO US PATRIOT RADARS; UNCONFIRMED.",
     "AP · REUTERS · UKMTO", "CONFIRMED"),
    (2, "PERU: QUAKE 6.7", NAVY,
     ["DEEP 6.7 QUAKE", "SHAKES PERU"],
     "A MAGNITUDE 6.7 EARTHQUAKE STRUCK 9 KM NE OF CARHUAMAYO AT 00:09 UTC, "
     "DEEP BELOW THE ANDES - USGS PUTS IT AT 108 KM, PERU'S IGP AT 129 KM. "
     "IT WAS FELT ACROSS LIMA AND CENTRAL PERU; NO TSUNAMI, NO DEATHS OR "
     "SERIOUS DAMAGE REPORTED ON SATURDAY.",
     "AP · USGS", "CONFIRMED"),
    (3, "COP31: OVERTIME", TEAL,
     ["COP31 TALKS RUN", "INTO OVERTIME"],
     "TALKS IN ANTALYA SLIPPED INTO OVERTIME ON SATURDAY WITH ABOUT 200 "
     "COUNTRIES STILL SPLIT OVER ADAPTATION FINANCE AND ANY MENTION OF COAL, "
     "OIL AND GAS. A THIRD DRAFT WAS PROMISED FOR SATURDAY MORNING; BY "
     "EVENING NO NEW TEXT HAD APPEARED. HOEKSTRA: 'EITHER A GOOD "
     "DEAL OR NO DEAL.'",
     "AP · REUTERS", "CONFIRMED"),
]

# Small stories: (num, kicker, headline, summary, sources, status, pictogram)
SMALL = [
    (4, "BRUSSELS", "EU AND INDONESIA SIGN TRADE PACT",
     "98.5% OF TARIFFS TO GO; TALKS RAN 10 YEARS.",
     "EC · ANTARA", "OFFICIAL", "flags"),
    (5, "SINALOA", "MEXICO CAPTURES CARTEL BOSS CHAPO ISIDRO",
     "11 DEAD IN RAID; $5M US REWARD.",
     "AP · MEXICO", "CONFIRMED", "cuffs"),
    (6, "GULF OF FINLAND", "DRONES SET RUSSIAN SHIP ON FIRE",
     "SPARTA II HIT; 16 CREW SAVED.",
     "REUTERS · FINLAND", "CONFIRMED", "ship"),
    (7, "GENEVA", "128 NATIONS BACK KILLER-ROBOT RULES",
     "TWO-YEAR PATH; NO BINDING DEAL YET.",
     "AP · REUTERS", "CONFIRMED", "robot"),
    (8, "WORLD MARKETS", "BITCOIN SINKS BELOW $56,000, THEN BOUNCES",
     "TWO-YEAR LOW $55,251; UP 8% BY EVENING.",
     "REUTERS", "CONFIRMED", "chart"),
    (9, "SPACE", "BEPICOLOMBO ENTERS MERCURY ORBIT",
     "37-MINUTE BURN AT 18:24; 2ND CRAFT EVER.",
     "ESA", "OFFICIAL", "planet"),
    (10, "LONDON", "ENGLAND THRASH NEW ZEALAND 37-12",
     "RECORD MARGIN AT TWICKENHAM.",
     "REUTERS", "CONFIRMED", "score"),
    (11, "BASRA", "BASRA POWER-STATION FIRE KILLS 4",
     "800 MW PLANT SHUT; 35 HURT.",
     "REUTERS · INA", "CONFIRMED", "flame"),
    (12, "PARIS", "82,500 MARCH IN FRANCE",
     "6TH SATURDAY OF PRICE PROTESTS.",
     "REUTERS", "CONFIRMED", "crowd"),
    (13, "BANDA SEA", "M6.8 QUAKES THE BANDA SEA",
     "09:42 UTC; FELT IN DARWIN; NO TSUNAMI.",
     "GFZ · USGS", "CONFIRMED", "wave"),
]

# The 22 more: (num, headline) - one line each, sources in the footer key.
MORE = [
    (14, "GAZA — 3 KILLED IN AID-VEHICLE STRIKE"),
    (15, "HORMUZ — IRAN SAYS IT DOWNED 2 US DRONES"),
    (16, "GULF — US DENIES IRAN HIT AN F-16"),
    (17, "LENINGRAD — GOVERNOR SAYS 80 DRONES DOWNED"),
    (18, "TAIPEI — 21 CHINESE JETS HELD A PATROL"),
    (19, "BRASILIA — BOLSONARO, 71, IN INTENSIVE CARE"),
    (20, "CHANDEL — 16 DEAD FROM SUSPECTED TOXIC LIQUOR"),
    (21, "LAS VEGAS — VERSTAPPEN ON POLE AFTER PENALTY"),
    (22, "WELLINGTON — RAHUL'S 136 PUTS INDIA 118 AHEAD"),
    (23, "DUBLIN — IRELAND BEAT SOUTH AFRICA 20-17"),
    (24, "WARSAW — RUTTE VOWS TO DEFEND EVERY INCH"),
    (25, "NEWCASTLE — NEWCASTLE HOLD ARSENAL 2-2"),
    (26, "LONDON — LEEDS THRASH CHELSEA 4-1"),
    (27, "MELBOURNE — AUSTRALIA BEAT ENGLAND BY 3 WKTS"),
    (28, "ADDIS ABABA — 700,000 DISPLACED BY CONFLICT"),
    (29, "FUKUSHIMA — 1,500 STRANDED BY SNOW; 700 DARK"),
    (30, "MASTUNG — PAKISTAN SAYS 15 MILITANTS KILLED"),
    (31, "TAIPEI — TAIWAN BANS BELOW-CLOSE SHORTS"),
    (32, "ABUJA — ALL 54 CAF NATIONS BACK INFANTINO"),
    (33, "W. KORDOFAN — RELIEF GROUP SAYS RSF KILLED 5"),
    (34, "DHAKA — 2 MORE DIE WITH MEASLES SYMPTOMS"),
    (35, "SYDNEY — CRICKET AUSTRALIA BACKS CUMMINS"),
]

# (time, label) - all times UTC, all verified.
TIMELINE = [
    ("00:09", "PERU M6.7", "QUAKE"),
    ("02:00", "SINALOA", "RAID"),
    ("03:45", "ROBOT TALKS", "END"),
    ("09:42", "BANDA SEA", "M6.8"),
    ("18:24", "BEPICOLOMBO", "BURN"),
    ("21:30", "COP31", "NO DEAL"),
]

# (big number, caption) - every number verified live.
STATS = [
    ("6.7", "PERU QUAKE MAGNITUDE (USGS)"),
    ("2", "TANKERS HIT OFF KHASAB (UKMTO)"),
    ("128", "NATIONS BACK GENEVA ROBOT-ARMS TALKS"),
    ("98.5%", "OF TARIFFS TO GO (EU-INDONESIA PACT)"),
    ("82,500", "MARCHERS IN FRANCE (MINISTRY)"),
    ("DAY 13", "OF A 12-DAY CLIMATE SUMMIT"),
]

# (region, count, colour) - counts sum to 35 and match the story list.
REGIONS = [
    ("MIDDLE EAST", 5, RED),
    ("EUROPE", 10, NAVY),
    ("ASIA-PACIFIC", 10, TEAL),
    ("AMERICAS", 4, GOLD),
    ("AFRICA", 3, GREEN),
    ("GLOBAL", 3, MUTED),
]

DATE_CHECK = (
    "LEFT OUT (OTHER DAY) - KYIV BARRAGE AND MISSILES IN POLAND, "
    "KRYVYI RIH STRIKE (FRI 20 NOV UTC); HOUTHI MISSILES OVER RIYADH "
    "(23:43 UTC FRI); BLUE NILE ARMY STATEMENT (FRI). "
    "NOT YET (FUTURE) - COP31 APPROVAL SESSION (SUN 06:00 GMT); LAS VEGAS "
    "GP RACE (SUN 04:00 UTC). PERU'S QUAKE STRUCK 19:09 FRI LOCAL = 00:09 "
    "UTC SAT. MANIPUR TOLL HIT 16 ON SATURDAY (OFFICIAL); DEATHS BEGAN "
    "18 NOV. LENINGRAD TALLY WAS REVISED DURING THE DAY; WE USE THE FINAL "
    "FIGURE."
)

FOOTER = [
    "HOW WE CHECKED: CONFIRMED = 2+ MAJOR OUTLETS · OFFICIAL = ON THE "
    "RECORD · REPORTED = ONE MAJOR OUTLET · CLAIM = ONE PARTY'S CLAIM, "
    "UNVERIFIED.",
    "ALL TIMES UTC. EVERY STORY HAPPENED, OR WAS FIRST REPORTED, ON "
    "SATURDAY 21 NOVEMBER 2026. PINS ARE NUMBERED; 8 IS A GLOBAL MARKET, "
    "9 IS IN SPACE.",
    "SOURCES: AP, REUTERS, BBC, AFP, USGS, ESA, UKMTO, FIA, MND, CAF, "
    "FSC, DGHS, DAWN, KYODO, AFRICANEWS, AL JAZEERA.",
    "LIST SOURCES: 14 REUTERS · 15 TASNIM · 16 CENTCOM · 17 REUTERS · "
    "18 MND · 19 REUTERS · 20 OFFICIALS · 21 FIA · 22 CRICKET · 23 "
    "REUTERS · 24 NATO · 25 REUTERS · 26 REUTERS · 27 AJ · 28 "
    "AFRICANEWS · 29 KYODO · 30 DAWN · 31 FSC · 32 CAF · 33 RELIEF "
    "GROUP · 34 DGHS · 35 AP.",
]

# ---------------------------------------------------------------- illustrations
def draw_gulf(x, y, w, h):
    """Schematic Persian Gulf: Iran north, Arabia south, strait east."""
    rect(x, y, w, h, SEA)
    # Iran (north land).
    poly([(x, y), (x + w, y), (x + w, y + 34), (x + w - 40, y + 28),
          (x + w - 90, y + 38), (x + w - 150, y + 30), (x + w - 210, y + 40),
          (x + 60, y + 32), (x, y + 42)], (208, 192, 158))
    # Arabia (south land).
    poly([(x, y + h), (x + w, y + h), (x + w, y + 74), (x + w - 30, y + 68),
          (x + w - 90, y + 80), (x + w - 160, y + 70), (x + 120, y + 82),
          (x + 40, y + 72), (x, y + 80)], LAND)
    # Qatar peninsula.
    poly([(x + 196, y + 78), (x + 202, y + 78), (x + 205, y + 62),
          (x + 200, y + 60)], LAND)
    # Oman corner (bottom right).
    poly([(x + w, y + h), (x + w, y + 66), (x + w - 24, y + 62),
          (x + w - 10, y + 78)], (208, 192, 158))
    # Bahrain island.
    disc(x + 158, y + 56, 3, RED)
    # Tankers off Khasab (near the strait, right).
    rect(x + 258, y + 48, 18, 6, INK)
    rect(x + 282, y + 58, 18, 6, INK)
    star(x + 267, y + 42, 6, RED)
    star(x + 291, y + 52, 6, RED)
    draw_text(x + 10, y + 6, "IRAN", 1, INK, bold=True)
    draw_text(x + 12, y + 92, "SAUDI ARABIA", 1, INK, bold=True)
    draw_text(x + 250, y + 8, "HORMUZ", 1, INK, bold=True)
    draw_text(x + 120, y + 62, "BAHRAIN", 1, RED, bold=True)
    draw_text(x + 140, y + 92, "2 US BASES", 1, INK)
    draw_text(x + 234, y + 92, "2 TANKERS HIT", 1, RED, bold=True)


def draw_quake(x, y, w, h):
    """Quake cross-section: surface, strata, hypocentre, depth scale."""
    rect(x, y, w, h, SKY)
    poly([(x, y + 38), (x + w, y + 38), (x + w, y + 62), (x, y + 62)],
         (214, 196, 150))
    poly([(x, y + 62), (x + w, y + 62), (x + w, y + 86), (x, y + 86)],
         (196, 172, 120))
    poly([(x, y + 86), (x + w, y + 86), (x + w, y + h), (x, y + h)],
         (172, 144, 92))
    # Andes mountains on the surface, left.
    poly([(x + 8, y + 38), (x + 30, y + 18), (x + 52, y + 38)], (150, 128, 96))
    poly([(x + 40, y + 38), (x + 58, y + 24), (x + 76, y + 38)], (150, 128, 96))
    rect(x, y + 38, w, 2, INK)
    # Fault line down to the hypocentre.
    line(x + 170, y + 38, x + 170, y + 82, RED)
    for r in (26, 18, 10):
        circle(x + 170, y + 82, r, RED)
    star(x + 170, y + 82, 6, RED)
    disc(x + 170, y + 82, 2, RED)
    # Depth bracket, right.
    line(x + 296, y + 38, x + 296, y + 82, INK)
    line(x + 292, y + 38, x + 300, y + 38, INK)
    line(x + 292, y + 82, x + 300, y + 82, INK)
    draw_text(x + 12, y + 26, "LIMA", 1, INK, bold=True)
    draw_text(x + 146, y + 26, "JUNIN", 1, INK, bold=True)
    draw_text(x + 218, y + 56, "108 KM (USGS)", 1, INK)
    draw_text(x + 218, y + 70, "129 KM (IGP)", 1, INK)
    draw_text(x + 12, y + 96, "DEEP QUAKE - NO TSUNAMI", 1, INK, bold=True)


def draw_cop31(x, y, w, h):
    """Calendar Nov 9-21 (+1 overtime day) and an overtime clock."""
    rect(x, y, w, h, WHITE)
    draw_text(x + 8, y + 8, "NOVEMBER 2026", 1, INK, bold=True)
    rect(x + 208, y + 6, 98, 16, WHITE)
    rect(x + 208, y + 6, 98, 1, RED)
    rect(x + 208, y + 21, 98, 1, RED)
    rect(x + 208, y + 6, 1, 16, RED)
    rect(x + 305, y + 6, 1, 16, RED)
    draw_text(x + 216, y + 10, "NO DEAL YET", 1, RED, bold=True)
    for row in range(2):
        for col in range(7):
            day = 9 + row * 7 + col
            bx = x + 8 + col * 24
            by = y + 26 + row * 26
            if row == 1 and col == 6:
                rect(bx, by, 22, 22, RED)
                draw_text(bx + 5, by + 7, "+1", 1, WHITE, bold=True)
                continue
            if day > 21:
                continue
            if day == 21:
                rect(bx, by, 22, 22, RED)
                draw_text(bx + 5, by + 7, "21", 1, WHITE, bold=True)
            else:
                rect(bx, by, 22, 22, (232, 226, 210))
                draw_text(bx + 5, by + 7, str(day), 1, INK)
    draw_text(x + 8, y + 84, "9-20 SCHEDULED, 21 = DAY 13", 1, INK, bold=True)
    # Clock, hands past the deadline.
    cx, cy = x + 256, y + 58
    disc(cx, cy, 25, WHITE)
    circle(cx, cy, 25, INK)
    circle(cx, cy, 24, INK)
    line(cx, cy, cx - 8, cy - 14, INK)
    line(cx, cy, cx + 12, cy - 16, RED)
    disc(cx, cy, 2, INK)
    draw_text(cx - 24, y + 88, "OVERTIME", 1, RED, bold=True)


LEAD_ART = {1: draw_gulf, 2: draw_quake, 3: draw_cop31}


def draw_picto(kind, x, y, w, h):
    """Small pictogram panel + big number for one small story."""
    tints = {
        'flags': (224, 232, 240), 'cuffs': (240, 228, 210),
        'ship': (214, 230, 236), 'robot': (228, 228, 232),
        'chart': (232, 238, 226), 'planet': (226, 226, 236),
        'score': (232, 236, 224), 'flame': (244, 224, 210),
        'crowd': (236, 230, 214), 'wave': (214, 230, 236),
    }
    rect(x, y, w, h, tints[kind])
    rect(x, y, w, 1, INK)
    rect(x, y + h - 1, w, 1, INK)
    rect(x, y, 1, h, INK)
    rect(x + w - 1, y, 1, h, INK)
    if kind == 'flags':
        rect(x + 8, y + 14, 26, 20, NAVY)
        for i in range(6):
            a = 2.0 * math.pi * i / 6
            disc(x + 21 + int(7 * math.cos(a)), y + 24 + int(6 * math.sin(a)),
                 1, (255, 210, 60))
        rect(x + 38, y + 14, 26, 10, RED)
        rect(x + 38, y + 24, 26, 10, WHITE)
        draw_text(x + 72, y + 15, "98.5%", 3, RED, bold=True)
    elif kind == 'cuffs':
        circle(x + 20, y + 25, 9, INK)
        circle(x + 46, y + 25, 9, INK)
        line(x + 28, y + 21, x + 38, y + 21, INK)
        line(x + 28, y + 29, x + 38, y + 29, INK)
        draw_text(x + 66, y + 18, "11 DEAD", 2, RED, bold=True)
    elif kind == 'ship':
        poly([(x + 6, y + 32), (x + 58, y + 32), (x + 52, y + 42),
              (x + 12, y + 42)], INK)
        rect(x + 24, y + 22, 16, 10, INK)
        rect(x + 42, y + 18, 4, 14, INK)
        disc(x + 20, y + 12, 2, INK)
        disc(x + 50, y + 10, 2, INK)
        star(x + 33, y + 12, 5, RED)
        draw_text(x + 66, y + 18, "16 SAVED", 2, INK, bold=True)
    elif kind == 'robot':
        rect(x + 14, y + 12, 34, 26, (190, 196, 200))
        rect(x + 14, y + 12, 34, 1, INK)
        rect(x + 14, y + 37, 34, 1, INK)
        rect(x + 14, y + 12, 1, 26, INK)
        rect(x + 47, y + 12, 1, 26, INK)
        line(x + 31, y + 12, x + 31, y + 5, INK)
        disc(x + 31, y + 4, 2, RED)
        rect(x + 20, y + 20, 7, 7, INK)
        rect(x + 35, y + 20, 7, 7, INK)
        rect(x + 22, y + 31, 18, 2, INK)
        draw_text(x + 66, y + 15, "128", 3, NAVY, bold=True)
    elif kind == 'chart':
        line(x + 8, y + 42, x + 62, y + 42, INK)
        line(x + 8, y + 42, x + 8, y + 8, INK)
        line(x + 10, y + 14, x + 24, y + 20, RED)
        line(x + 24, y + 20, x + 38, y + 38, RED)
        line(x + 38, y + 38, x + 50, y + 30, GREEN)
        line(x + 50, y + 30, x + 62, y + 24, GREEN)
        draw_text(x + 70, y + 18, "$55.3K", 2, RED, bold=True)
    elif kind == 'planet':
        disc(x + 30, y + 25, 13, (160, 158, 150))
        disc(x + 26, y + 21, 2, (120, 118, 112))
        disc(x + 34, y + 29, 2, (120, 118, 112))
        disc(x + 31, y + 25, 1, (120, 118, 112))
        for i in range(120):
            a = 2.0 * math.pi * i / 120
            px(x + 30 + int(round(22 * math.cos(a))),
               y + 25 + int(round(8 * math.sin(a))), INK)
        disc(x + 50, y + 19, 2, RED)
        draw_text(x + 66, y + 18, "18:24", 2, INK, bold=True)
    elif kind == 'score':
        rect(x + 6, y + 8, 56, 34, INK)
        draw_text(x + 12, y + 13, "ENG 37", 1, WHITE, bold=True)
        draw_text(x + 12, y + 27, "NZL 12", 1, WHITE, bold=True)
        draw_text(x + 68, y + 15, "37-12", 3, INK, bold=True)
    elif kind == 'flame':
        poly([(x + 30, y + 6), (x + 40, y + 20), (x + 44, y + 30),
              (x + 38, y + 42), (x + 22, y + 42), (x + 16, y + 30),
              (x + 20, y + 20)], RED)
        poly([(x + 30, y + 22), (x + 36, y + 30), (x + 34, y + 38),
              (x + 26, y + 38), (x + 24, y + 30)], GOLD)
        draw_text(x + 58, y + 18, "4 DEAD", 2, RED, bold=True)
    elif kind == 'crowd':
        for row in range(3):
            for col in range(5):
                disc(x + 12 + col * 10, y + 14 + row * 11, 3, NAVY)
                rect(x + 8 + col * 10, y + 18 + row * 11, 8, 5, NAVY)
        draw_text(x + 66, y + 15, "82,500", 3, INK, bold=True)
    elif kind == 'wave':
        for row in range(3):
            yy = y + 14 + row * 11
            for xx in range(0, 56, 4):
                px(x + 8 + xx, yy + (3 if (xx // 4) % 2 else -3), NAVY)
                px(x + 8 + xx, yy + (3 if (xx // 4) % 2 else -3) + 1, NAVY)
        draw_text(x + 72, y + 15, "M6.8", 3, NAVY, bold=True)


# ---------------------------------------------------------------- world map
# Continents as unions of ellipses in (lon, lat, rx, ry) degrees.
LAND_ELLIPSES = [
    (-100, 48, 32, 20), (-152, 64, 14, 7), (-88, 14, 12, 5),
    (-42, 74, 12, 7), (-60, -12, 14, 22), (-70, -35, 7, 10),
    (14, 52, 18, 9), (16, 64, 9, 7), (-2, 54, 3, 5),
    (18, 6, 16, 22), (22, -22, 11, 11),
    (95, 52, 42, 16), (78, 20, 9, 11), (101, 12, 9, 7),
    (114, -2, 14, 3), (45, 24, 11, 9), (140, 38, 5, 6),
    (122, 13, 4, 6), (134, -25, 13, 7), (172, -41, 3, 5),
]

# (num, lon, lat, colour, label dx, label dy)
PINS = [
    (1, 50.5, 26.2, RED, 0, 0),
    (2, -76.0, -11.0, GOLD, 0, 0),
    (3, 30.7, 36.9, MUTED, 0, 0),
    (4, 4.4, 50.8, NAVY, 18, -4),
    (5, -107.5, 25.6, GOLD, 0, 0),
    (6, 27.0, 60.0, NAVY, 0, 0),
    (7, 6.1, 46.2, NAVY, 10, 14),
    (8, -74.0, 40.7, MUTED, 0, 0),
    (9, 8.6, 49.9, PURPLE, -4, -16),
    (10, -0.1, 51.5, NAVY, -16, -10),
    (11, 47.8, 30.5, RED, 14, 10),
    (12, 2.3, 48.9, NAVY, -18, 8),
    (13, 129.0, -6.5, TEAL, 0, 0),
]


def _on_land(lon, lat):
    for clon, clat, rx, ry in LAND_ELLIPSES:
        if ((lon - clon) / rx) ** 2 + ((lat - clat) / ry) ** 2 <= 1.0:
            return True
    return False


def draw_world_map(x, y, w, h):
    rect(x, y, w, h, SEA)
    step = 4
    for py in range(y + 2, y + h - 1, step):
        lat = 90.0 - (py - y) / float(h) * 150.0
        for pxx in range(x + 2, x + w - 1, step):
            lon = (pxx - x) / float(w) * 360.0 - 180.0
            if _on_land(lon, lat):
                rect(pxx, py, 2, 2, LAND)
    rect(x, y, w, 1, INK)
    rect(x, y + h - 1, w, 1, INK)
    rect(x, y, 1, h, INK)
    rect(x + w - 1, y, 1, h, INK)
    for num, lon, lat, col, dx, dy in PINS:
        px0 = x + int((lon + 180.0) / 360.0 * w)
        py0 = y + int((90.0 - lat) / 150.0 * h)
        lx, ly = px0 + dx, py0 + dy
        if dx or dy:
            line(px0, py0, lx, ly, INK)
            disc(px0, py0, 2, INK)
        disc(lx, ly, 5, col)
        draw_text_centered(lx, ly - 3, str(num), 1, WHITE, bold=True)

# ---------------------------------------------------------------- layout
MX = 28
CW = 314
LEAD_X = [28, 355, 682]
SMALL_X = [28, 223, 418, 613, 808]
SMALL_W = 187
STATUS_COLOUR = {"CONFIRMED": GREEN, "OFFICIAL": NAVY,
                 "REPORTED": MUTED, "CLAIM": RED}


def draw_lead(x, y, num, kicker, accent, head_lines, body, sources, status):
    rect(x, y, CW, 20, accent)
    draw_text(x + 8, y + 6, kicker, 1, WHITE, bold=True)
    ix, iy, iw, ih = x, y + 24, CW, 110
    rect(ix, iy, iw, ih, WHITE)
    LEAD_ART[num](ix + 1, iy + 1, iw - 2, ih - 2)
    rect(ix, iy, iw, 1, INK)
    rect(ix, iy + ih - 1, iw, 1, INK)
    rect(ix, iy, 1, ih, INK)
    rect(ix + iw - 1, iy, 1, ih, INK)
    draw_text(x, iy + ih + 2, sources, 1, MUTED)
    ky = iy + ih + 16
    kicker_line = "%d %s" % (num, {
        1: "BAHRAIN . HORMUZ . IRAN WAR",
        2: "JUNIN, PERU . EARTHQUAKE",
        3: "ANTALYA, TURKIYE . CLIMATE",
    }[num])
    draw_text(x, ky, kicker_line, 1, INK, bold=True)
    tag(x + CW - (tw(status, 1) + 8), ky - 2, status,
        STATUS_COLOUR[status])
    yy = ky + 16
    for line in head_lines:
        assert tw(line, 2) <= CW, line
        draw_text(x, yy, line, 2, INK)
        yy += 16
    yy += 4
    lines = wrap(body, 49)
    assert len(lines) <= 7, "lead %d body too long: %d lines" % (num, len(lines))
    for line in lines:
        draw_text(x, yy, line, 1, INK)
        yy += 10
    return yy


def draw_small(x, y, num, kicker, headline, summary, sources, status, kind):
    draw_picto(kind, x, y, SMALL_W, 50)
    ky = y + 54
    draw_text(x, ky, "%d %s" % (num, kicker), 1, INK, bold=True)
    tag(x + SMALL_W - (tw(status, 1) + 8), ky - 2, status,
        STATUS_COLOUR[status])
    yy = ky + 14
    lines = wrap(headline, 30)
    assert len(lines) <= 2, "small %d headline too long" % num
    for line in lines:
        draw_text(x, yy, line, 1, INK, bold=True)
        yy += 10
    yy += 2
    lines = wrap(summary, 30)
    assert len(lines) <= 2, "small %d summary too long" % num
    for line in lines:
        draw_text(x, yy, line, 1, INK)
        yy += 10
    yy += 2
    draw_text(x, yy, sources, 1, MUTED)
    return yy


def main():
    n_stories = len(LEADS) + len(SMALL) + len(MORE)
    assert n_stories == 35, n_stories
    assert sum(c for _r, c, _col in REGIONS) == 35

    fill(PAPER)
    rect(0, 0, W, 4, RED)

    # Top bar.
    rect(MX, 8, tw("THE WORLD IN ONE DAY", 1) + 12, 18, INK)
    draw_text(MX + 6, 13, "THE WORLD IN ONE DAY", 1, WHITE, bold=True)
    draw_text_right(W - MX, 10,
                    "35 STORIES . 6 REGIONS . EVERY ONE DATED "
                    "SATURDAY 21 NOVEMBER 2026", 1, INK)
    rect(MX, 32, W - 2 * MX, 2, RED)

    # Headline + sub-headline.
    draw_text_centered(W // 2, 38, "SATURDAY 21 NOVEMBER 2026", 6, INK,
                       bold=True)
    rect(MX, 84, W - 2 * MX, 1, INK)
    draw_text_centered(W // 2, 87,
                       "IRAN HITS BAHRAIN BASES - A DEEP QUAKE SHAKES "
                       "PERU - COP31 RUNS INTO OVERTIME", 1, INK)
    rect(MX, 98, W - 2 * MX, 1, INK)

    # UTC timeline.
    rect(MX, 104, 104, 30, INK)
    draw_text_centered(MX + 52, 108, "THE DAY", 1, WHITE, bold=True)
    draw_text_centered(MX + 52, 118, "IN UTC", 1, WHITE, bold=True)
    line(140, 120, W - MX, 120, INK)
    for i, (t, lab1, lab2) in enumerate(TIMELINE):
        cx = 170 + i * 140
        disc(cx, 120, 3, RED)
        draw_text_centered(cx, 106, t, 1, RED, bold=True)
        draw_text_centered(cx, 126, lab1, 1, INK)
        draw_text_centered(cx, 136, lab2, 1, INK)

    # Stat boxes.
    stat_colours = [NAVY, RED, TEAL, NAVY, RED, TEAL]
    for i, ((big, cap), col) in enumerate(zip(STATS, stat_colours)):
        bx = MX + i * 162
        rect(bx, 146, 155, 50, WHITE)
        rect(bx, 146, 155, 3, col)
        rect(bx, 146, 155, 1, INK)
        rect(bx, 195, 155, 1, INK)
        rect(bx, 146, 1, 50, INK)
        rect(bx + 154, 146, 1, 50, INK)
        draw_text(bx + 8, 154, big, 3, col, bold=True)
        lines = wrap(cap, 23)
        assert len(lines) <= 2
        yy = 176
        for cap_line in lines:
            draw_text(bx + 8, yy, cap_line, 1, INK)
            yy += 10

    # Region bars.
    draw_text(MX, 200, "STORIES BY REGION", 1, RED, bold=True)
    total = sum(c for _r, c, _col in REGIONS)
    widths = [int(round(c * 968.0 / total)) for _r, c, _col in REGIONS]
    widths[-1] += 968 - sum(widths)
    bx = MX
    for (name, count, col), wseg in zip(REGIONS, widths):
        rect(bx, 212, wseg, 20, col)
        draw_text_centered(bx + wseg // 2, 218, "%s %d" % (name, count),
                           1, WHITE, bold=True)
        bx += wseg

    # Leads.
    for x, (num, kicker, accent, head_lines, body, sources, status) in \
            zip(LEAD_X, LEADS):
        draw_lead(x, 238, num, kicker, accent, head_lines, body,
                  sources, status)
    rect(MX, 514, W - 2 * MX, 1, INK)

    # Small stories, two rows of five.
    for row in range(2):
        y = 520 + row * 132
        for x, story in zip(SMALL_X, SMALL[row * 5:(row + 1) * 5]):
            num, kicker, headline, summary, sources, status, kind = story
            draw_small(x, y, num, kicker, headline, summary, sources,
                       status, kind)

    # Bottom: map + numbered list.
    draw_text(MX, 782, "WHERE IT HAPPENED", 1, RED, bold=True)
    draw_text(416, 782, "ALSO ON SATURDAY 21 NOVEMBER 2026 - 22 MORE "
                        "STORIES", 1, RED, bold=True)
    draw_world_map(MX, 786, 372, 130)
    for i, (num, text) in enumerate(MORE):
        col = i // 11
        row = i % 11
        lx = 416 + col * 290
        ly = 798 + row * 11
        line_text = "%d %s" % (num, text)
        assert tw(line_text, 1) <= 288, line_text
        draw_text(lx, ly, line_text, 1, INK)

    # DATE CHECK box.
    rect(MX, 920, W - 2 * MX, 44, WHITE)
    rect(MX, 920, W - 2 * MX, 2, RED)
    rect(MX, 962, W - 2 * MX, 2, RED)
    rect(MX, 920, 2, 44, RED)
    rect(W - MX - 2, 920, 2, 44, RED)
    dc_lines = wrap("DATE CHECK: " + DATE_CHECK, 158)
    assert len(dc_lines) <= 3, "DATE CHECK too long: %d lines" % len(dc_lines)
    yy = 926
    for dc_line in dc_lines:
        draw_text(MX + 8, yy, dc_line, 1, INK)
        yy += 10

    # Footer.
    yy = 968
    for entry in FOOTER:
        for fline in wrap(entry, 161):
            draw_text(MX, yy, fline, 1, MUTED)
            yy += 9
    assert yy <= 1022, "footer overflows: %d" % yy

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    data = png_bytes()
    with open(path, "wb") as f:
        f.write(data)
    print("stories=%d leads=%d small=%d more=%d regions=%d" %
          (n_stories, len(LEADS), len(SMALL), len(MORE), len(REGIONS)))
    print("md5=%s" % hashlib.md5(data).hexdigest())
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()

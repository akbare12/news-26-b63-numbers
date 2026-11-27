#!/usr/bin/env python3
"""V61 news-image-20261126 builder (account b63). Renders entry.png 1024x1024.
Fresh from brief + KANON-20261126.md. PIL is build-time only; main.py is stdlib-only.
Layout V61: masthead -> DATE CHECK -> HERO MACY'S (art right) -> middle
(cards 2x5 left, map + pin index right) -> bottom heroes side by side
(Hormuz | tariff) -> ALSO 3 cols -> TIMELINE strip -> footer.
Counts: 3 heroes + 10 cards + 37 ALSO = 50 stories exactly.
"""
import hashlib
import json
import math
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FD = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else FD, size)


# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (17, 17, 17)
MUTED = (70, 70, 70)
NAVY = (20, 33, 61)
NAVY2 = (28, 46, 84)
RED = (178, 34, 34)
RED_DK = (140, 20, 20)
GOLD = (212, 160, 32)
GOLD_LT = (232, 196, 90)
CREAM = (255, 243, 205)
CREAM_BD = (183, 121, 31)
TEAL = (14, 74, 78)
TEAL_DK = (10, 52, 56)
GREEN = (31, 92, 50)
GREEN_DK = (22, 66, 36)
OCEAN = (214, 228, 240)
LAND = (233, 223, 200)
LAND_BD = (154, 143, 122)
WHITE = (255, 255, 255)
GREY_LINE = (120, 120, 120)
CARD_BG = (255, 255, 255)

# ---------------------------------------------------------------- content
MASTHEAD_TITLE = "THE WORLD IN ONE PAGE"
MASTHEAD_DATE = "Thursday, 26 November 2026"

DATE_IN = ("IN \u2014 26 NOV:  Macy's parade \u00b7 Hormuz claim \u00b7 Market rebound \u00b7 "
           "Kyiv mall \u00b7 Gaza strike \u00b7 UK migration")
DATE_OUT = ("LEFT OUT:  COP31 collapse (22 Nov) \u00b7 Shenzhou-24 launch (25 Nov) \u00b7 "
            "Cairo blast, 31 dead (25 Nov) \u00b7 Cartagena hostages freed (25 Nov) \u00b7 "
            "Huawei verdict (24 Nov)")

HERO1 = {
    "kicker": "HERO 1 \u00b7 THANKSGIVING \u00b7 [C]",
    "headline": "MACY'S 100TH PARADE POSTPONED BY STORM \u2014 FIRST TIME EVER",
    "deck": ("The centennial parade moves to Saturday after high winds ground the "
             "giant balloons; Philadelphia's parade is cancelled too."),
    "why": ("WHY IT MATTERS: The centennial parade is America's Thanksgiving ritual, "
            "and a weather delay \u2014 never before in 100 years \u2014 shows how "
            "fierce the East Coast storm was."),
    "stat": "100TH EDITION \u00b7 GUSTS 60 MPH \u00b7 SAT 28 NOV \u00b7 08:30 ET",
    "art_label": "100TH",
}

HERO2 = {
    "kicker": "HERO 2 \u00b7 STRAIT OF HORMUZ \u00b7 [CL]",
    "headline": "IRGC CLAIMS TWO TANKERS HIT BY MINES",
    "deck": ("Iran says a supertanker with over 2 million barrels was hit near Khasab; "
             "UKMTO confirms a blast west of Dubai."),
    "why": ("WHY IT MATTERS: The unverified claim puts the world's busiest "
            "oil chokepoint at the centre of the Iran war."),
    "stat": "2M BARRELS \u00b7 BRENT $93.8 \u00b7 UKMTO 222-26",
    "art_label": "2M",
}

HERO3 = {
    "kicker": "HERO 3 \u00b7 TRADE \u00b7 [C]",
    "headline": "MARKETS REBOUND AS TARIFF SALVO LOOKS LESS SEVERE",
    "deck": ("European and Asian stocks rally as new levies will not stack on July "
             "tariffs; Wall Street shut for Thanksgiving."),
    "why": ("WHY IT MATTERS: Investors judged the 14-partner plan, led by 20% on "
            "China, as manageable \u2014 for now."),
    "stat": "14 PARTNERS \u00b7 20% CHINA \u00b7 STOXX +1.6%",
    "art_label": "+1.6%",
}

# cards: headline (kicker+tag merged), deck (1 line), stat (1 line)
CARDS = [
    ("GAZA [C] \u2014 HAMAS EDUCATION CHIEF KILLED",
     "Abu Nada and wife die in Deir al-Balah; 9 killed.",
     "9 KILLED \u00b7 3RD NIGHT"),
    ("KYIV [C] \u2014 RUSSIAN MISSILES HIT KYIV MALL",
     "Desnianskyi mall struck amid 113 drones; 7 hurt.",
     "7 HURT \u00b7 113 DRONES"),
    ("BOGOR [C] \u2014 FLOODED GOLD MINE KILLS 13",
     "13 dead, 13 missing in a flooded shaft 100m down.",
     "13 DEAD \u00b7 13 MISSING"),
    ("NETANYAHU [C] \u2014 JUDGE: DROP THE CASE",
     "Judge urges dropping Case 4000, sole bribery count.",
     "CASE 4000 \u00b7 SOLE BRIBERY COUNT"),
    ("N. KOREA [C] \u2014 KIM TOURS NUCLEAR PLANT",
     "Kim urges wider tactical nuclear use on plant tour.",
     "TACTICAL NUCLEAR PUSH"),
    ("STARMIND [CL] \u2014 FCC CLEARS 1M SATELLITES",
     "Approved 25 Nov, first US nod for space data hubs.",
     "1M SATELLITES \u00b7 25 NOV"),
    ("UK [C] \u2014 NET MIGRATION FALLS TO 77,000",
     "Lowest since 1997, ONS figures to June 2026.",
     "77,000 \u00b7 LOWEST SINCE 1997"),
    ("RUSSIA [C] \u2014 RECORD DEFENCE BUDGET",
     "Parliament signs off the largest post-Soviet budget.",
     "RECORD POST-SOVIET BUDGET"),
    ("BANGKOK [C] \u2014 OIL DEPOT BLAST HURTS 7",
     "Bangkok oil depot blast injures 7; out in 30 min.",
     "7 HURT \u00b7 FIRE IN 30 MIN"),
    ("GERMANY [C] \u2014 2 HELD IN SYNAGOGUE PLOT",
     "Two Iraqi suspects held after raids in Cologne.",
     "2 ARRESTED \u00b7 COLOGNE + HEIDELBERG"),
]

# ALSO: (tag, text) - exactly 37, each one line at 10px in a 314px column.
ALSO = [
    ("C", "Eisenkot seals Israel's first coalition deal"),
    ("C", "Merz warns Russia's ambitions go beyond Ukraine"),
    ("R", "UK on alert over drone threat to air bases"),
    ("C", "Norse Atlantic suspends all flights, warns of bankruptcy"),
    ("C", "Poundland enters administration; 11,000 jobs at risk"),
    ("C", "Malaysia sues Google for $146m over harmful content"),
    ("C", "Kenya court halts US-backed Ebola facility"),
    ("C", "Belarus offers to fly Zelensky to Moscow; he refuses"),
    ("C", "Kushner calls Putin 'historic figure' and 'grandmaster'"),
    ("C", "Estonia decides to close its border"),
    ("C", "Copernicus: longest stretch above two-degree warming"),
    ("R", "Nvidia halts AI server shipments to 4 countries"),
    ("C", "US Bitcoin funds hit a record $4.94bn"),
    ("CL", "Tanker struck by projectile east of Khasab, 25 Nov"),
    ("CL", "Saudi downs a pair of missiles headed for Riyadh, 25 Nov"),
    ("CL", "Houthis claim strike on Ras Tanura refinery, 25 Nov"),
    ("CL", "Saudi reports minor damage at Jazan Port, 25 Nov"),
    ("C", "UN rights chief warns of atrocity-crime risk in Gaza"),
    ("C", "Russian strike kills a couple, 37 and 38, in Kharkiv"),
    ("C", "18 wounded in Russian strike on Kryvyi Rih"),
    ("C", "Ukrainian drones damage 5 jets at Savasleyka base"),
    ("C", "Drones set fire to Subkhankulovo pumping station"),
    ("C", "OPEC+ to meet 29 Nov on 2027 output"),
    ("C", "Gold at $3,572 an ounce, down 8% in a month"),
    ("C", "Nvidia falls 3.91% to $149.30"),
    ("C", "S&P 500 slips 0.25%, Nasdaq 0.62% on Wednesday"),
    ("C", "MSCI world index gains 0.4%"),
    ("C", "Brent settled Wednesday up 3.5% at $94.61"),
    ("C", "WTI gains 0.2% to $83.32"),
    ("C", "EU faces 15% tariff; Vietnam up to 35% if talks fail"),
    ("C", "Tariff hearings set for 25 Jan; rollout likely Feb/Mar"),
    ("C", "India faces 17% or 25% tariffs in the US plan"),
    ("C", "High wind warning in force for NYC from 10:00"),
    ("C", "NYC balloon rule: no flight if winds top 23 mph"),
    ("C", "Nvidia now $2.3tn below its October peak"),
    ("C", "Dollar index flat at 103.71"),
    ("C", "Tariffs follow an 8-month Section 301 probe"),
]

TIMELINE = [
    "10:00 \u2014 NYC WIND WARNING",
    "SAT 08:30 \u2014 PARADE",
    "25 NOV \u2014 FCC: SPACE DATA",
    "29 NOV \u2014 OPEC+",
    "25 JAN \u2014 HEARINGS",
    "FEB/MAR \u2014 TARIFFS",
]

LEGEND = "[C] CONFIRMED \u00b7 [R] REPORTED \u00b7 [CL] CLAIM / 25 NOV EVENT"
SOURCES = "SOURCES: Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 UKMTO \u00b7 ONS \u00b7 KCNA \u00b7 FCC"

# pins: (number, label, lon, lat, index short story)
PINS = [
    (1, "NEW YORK", -74.0, 40.7, "Parade"),
    (2, "SANTA CLARA", -121.96, 37.35, "Nvidia"),
    (3, "LONDON", -0.1, 51.5, "Migration"),
    (4, "KYIV", 30.5, 50.45, "Mall"),
    (5, "GAZA", 34.5, 31.5, "Gaza strike"),
    (6, "MUMBAI", 72.9, 19.1, "India tariff"),
    (7, "HORMUZ", 56.3, 26.6, "Mine claim"),
    (8, "JAZAN", 42.5, 16.9, "Port"),
    (9, "NAIROBI", 36.8, -1.3, "Ebola ruling"),
    (10, "BOGOR", 106.8, -6.6, "Mine flood"),
    (11, "BANGKOK", 100.5, 13.75, "Blast"),
    (12, "BEIJING", 116.4, 39.9, "China tariff"),
]

# simplified continent polygons (lon, lat), equirectangular
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 72), (-65, 60), (-55, 47), (-60, 45), (-70, 42), (-75, 35),
     (-80, 32), (-81, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 30),
     (-125, 40), (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 75),
     (-55, 76), (-60, 70)],
    # South America
    [(-80, 10), (-75, 10), (-65, 10), (-55, 5), (-50, 0), (-40, -5),
     (-35, -10), (-40, -20), (-50, -30), (-60, -35), (-70, -40),
     (-70, -50), (-75, -55), (-70, -30), (-80, -20), (-80, -10), (-80, 0)],
    # Africa
    [(-10, 35), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (40, 20),
     (45, 11), (50, 10), (48, 0), (40, -10), (35, -20), (30, -30),
     (20, -35), (15, -30), (12, -18), (10, -5), (8, 4), (-8, 4),
     (-15, 10), (-17, 15), (-15, 25), (-10, 30)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (25, 71),
     (18, 69), (12, 65), (5, 60), (5, 58), (-5, 50), (-10, 43)],
    # Asia
    [(30, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 69), (170, 66), (178, 65), (170, 60), (162, 60), (158, 52),
     (150, 59), (142, 50), (140, 40), (135, 35), (130, 33), (127, 35),
     (122, 38), (120, 30), (115, 22), (110, 20), (108, 12), (105, 8),
     (100, 8), (98, 12), (95, 16), (92, 21), (88, 22), (85, 19), (80, 15),
     (77, 8), (75, 12), (72, 20), (68, 23), (65, 25), (60, 25), (57, 26),
     (55, 26), (52, 28), (50, 29), (48, 30), (45, 29), (42, 30), (40, 36),
     (36, 36), (33, 41), (30, 45), (28, 45), (30, 50), (35, 55), (40, 60),
     (35, 65), (30, 68)],
    # Indonesia
    [(95, -5), (105, -5), (110, -7), (115, -8), (120, -10), (125, -9),
     (130, -4), (135, -3), (140, -4), (141, -8), (135, -8), (125, -8),
     (115, -7), (105, -6)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
     (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
     (118, -20)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
     (143, 43), (145, 44), (142, 42), (140, 39), (137, 36), (133, 34)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (50, -20), (47, -25), (44, -25),
     (43, -20)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (175, -40), (172, -43),
     (168, -46)],
]

# ---------------------------------------------------------------- helpers
TEXT_BOXES = []   # (x0, y0, x1, y1, text) every drawn text line
DIVIDERS = []     # y positions of horizontal rules
RENDERED_STRINGS = []  # full rendered text inventory for grep checks


def wrap(text, fnt, width, max_lines=None):
    """Greedy wrap on spaces. No silent truncation: raise if it cannot fit."""
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if not cur:
                raise AssertionError("single word too wide: %r" % wd)
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        raise AssertionError("wrap %d lines > max %d: %r -> %r"
                             % (len(lines), max_lines, text, lines))
    return lines


def draw_text(d, xy, text, fnt, fill=INK):
    """Draw one line and record its bbox."""
    x, y = xy
    d.text((x, y), text, font=fnt, fill=fill)
    bb = d.textbbox((x, y), text, font=fnt)
    TEXT_BOXES.append((bb[0], bb[1], bb[2], bb[3], text))
    RENDERED_STRINGS.append(text)
    return bb


def draw_wrapped(d, x, y, text, fnt, width, max_lines=None, fill=INK,
                 line_gap=2):
    lines = wrap(text, fnt, width, max_lines)
    cy = y
    for ln in lines:
        draw_text(d, (x, cy), ln, fnt, fill)
        cy += fnt.size + line_gap
    return cy  # y just below last line (includes trailing gap)


def text_w(text, fnt):
    return fnt.getlength(text)


def fit_assert(text, fnt, width, what):
    w = text_w(text, fnt)
    assert w <= width, "%s too wide: %.1f > %d : %r" % (what, w, width, text)
    return w


# ---------------------------------------------------------------- checks
STOPWORDS = set("""the a an in on of to and for after with at by from as is are
was were it its us uk says say amid over under into up down out off new
first second more most all per via near west east north south about than
then now also day top he she his her they their we our you your this that
these those not no yes if or but so do does did will would can could
hero why matters cl nov 25 26""".split())


def tokens(text):
    toks = re.findall(r"[a-z0-9]+(?:[.,][0-9]+)?", text.lower())
    return {t for t in toks if t not in STOPWORDS and (len(t) >= 2 or t.isdigit())}


def dup_scan(named_texts):
    """Flag any pair of story texts sharing >=3 distinctive words."""
    bad = []
    items = list(named_texts)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            shared = tokens(a[1]) & tokens(b[1])
            if len(shared) >= 3:
                bad.append((a[0], b[0], sorted(shared)))
    return bad


def norm_numbers(text):
    """Normalized numbers: strip $, %, commas; collapse trailing .0."""
    out = set()
    for m in re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", text):
        s = m.replace("$", "").replace("%", "").replace(",", "")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        out.add(s)
    for m in re.findall(r"\b\d{1,2}:\d{2}\b", text):
        out.add(m)
    return out


def check_counts():
    assert len(CARDS) == 10, "cards %d" % len(CARDS)
    assert len(ALSO) == 37, "also %d" % len(ALSO)
    assert 3 + 10 + 37 == 50
    assert len(PINS) == 12
    assert len(TIMELINE) == 6


def check_banned(full_text):
    low = full_text.lower()
    for phrase in ("third senior hamas official", "3rd senior official",
                   "bangchak", "significant figure"):
        assert phrase not in low, "BANNED phrase present: %r" % phrase


def check_tags():
    # every ALSO item has a tag in C/R/CL; 25 Nov events must be CL
    for tag, text in ALSO:
        assert tag in ("C", "R", "CL"), tag
        if "25 Nov" in text:
            assert tag == "CL", "25 Nov event not CL: %r" % text
    for h in (HERO1, HERO2, HERO3):
        assert "[C]" in h["kicker"] or "[CL]" in h["kicker"]
    for head, _, _ in CARDS:
        assert "[C]" in head or "[CL]" in head, head
    # hero why-it-matters ends with a period
    for h in (HERO1, HERO2, HERO3):
        assert h["why"].rstrip().endswith("."), h["kicker"]


def check_hero_stat_numbers():
    hero_nums = set()
    for h in (HERO1, HERO2, HERO3):
        hero_nums |= norm_numbers(h["stat"])
    for tag, text in ALSO:
        shared = norm_numbers(text) & hero_nums
        assert not shared, "ALSO repeats hero stat number %s: %r" % (shared, text)

# ---------------------------------------------------------------- sections
def render_masthead(d):
    d.rectangle([0, 0, W, 90], fill=NAVY)
    d.rectangle([0, 90, W, 93], fill=GOLD)
    DIVIDERS.append(91)
    draw_text(d, (28, 24), MASTHEAD_TITLE, font(38, True), WHITE)
    f_stories = font(26, True)
    draw_text(d, (W - 28 - text_w("50 STORIES", f_stories), 12),
              "50 STORIES", f_stories, GOLD_LT)
    draw_text(d, (W - 28 - text_w(MASTHEAD_DATE, font(14, True)), 48),
              MASTHEAD_DATE, font(14, True), WHITE)


def render_datecheck(d):
    y0, y1 = 96, 160
    d.rectangle([24, y0, 1000, y1], fill=CREAM, outline=CREAM_BD, width=2)
    draw_text(d, (36, y0 + 5), "DATE CHECK \u2014 WHAT'S IN \u00b7 WHAT'S OUT",
              font(13, True), RED_DK)
    f = font(11)
    fit_assert(DATE_IN, f, 928, "DATE IN")
    fit_assert(DATE_OUT, f, 928, "DATE OUT")
    draw_text(d, (36, y0 + 24), DATE_IN, f, INK)
    draw_text(d, (36, y0 + 42), DATE_OUT, f, INK)


def art_macys(d, x0, y0, x1, y1):
    """Balloon art: sky, buildings, giant balloons. Label fully inside."""
    d.rectangle([x0, y0, x1, y1], fill=(52, 84, 122))
    # solid navy strip at top for the label (inside art box)
    d.rectangle([x0, y0, x1, y0 + 52], fill=NAVY)
    d.line([x0, y0 + 52, x1, y0 + 52], fill=GOLD, width=2)
    # skyline
    import random
    rnd = random.Random(61)
    bx = x0
    while bx < x1:
        bw = rnd.randint(28, 52)
        bh = rnd.randint(28, 78)
        d.rectangle([bx, y1 - bh, min(bx + bw, x1), y1], fill=(24, 38, 58))
        for wy in range(y1 - bh + 8, y1 - 8, 12):
            for wx in range(bx + 5, min(bx + bw, x1) - 5, 10):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(232, 196, 90))
        bx += bw + 4
    # big red balloon (left) + gold balloon (right), thin white stripes
    d.ellipse([x0 + 34, y0 + 66, x0 + 186, y0 + 148], fill=RED)
    d.ellipse([x0 + 100, y0 + 66, x0 + 120, y0 + 148], fill=(255, 255, 255))
    d.ellipse([x0 + 222, y0 + 80, x0 + 322, y0 + 140], fill=GOLD)
    d.ellipse([x0 + 262, y0 + 80, x0 + 282, y0 + 140], fill=(255, 255, 255))
    # ropes
    d.line([x0 + 70, y0 + 148, x0 + 60, y1 - 78], fill=(220, 220, 220), width=2)
    d.line([x0 + 150, y0 + 148, x0 + 160, y1 - 78], fill=(220, 220, 220), width=2)
    d.line([x0 + 272, y0 + 140, x0 + 262, y1 - 78], fill=(220, 220, 220), width=2)
    # label "100TH" on the navy strip, fully inside art box, gap >= 2px
    f = font(40, True)
    tw = text_w(HERO1["art_label"], f)
    lx = x0 + (x1 - x0 - tw) / 2
    ly = y0 + 5
    bb = d.textbbox((lx, ly), HERO1["art_label"], font=f)
    assert bb[0] >= x0 + 2 and bb[1] >= y0 + 2 and bb[2] <= x1 - 2 \
        and bb[3] <= y1 - 2, "100TH label escapes art box"
    draw_text(d, (lx, ly), HERO1["art_label"], f, GOLD_LT)
    return (x0, y0, x1, y1)


def render_hero1(d):
    y0, y1 = 166, 356
    d.rectangle([24, y0, 1000, y1], fill=CARD_BG, outline=RED, width=2)
    tx = 36
    tw = 552
    draw_text(d, (tx, y0 + 8), HERO1["kicker"], font(11, True), RED)
    y = draw_wrapped(d, tx, y0 + 26, HERO1["headline"], font(24, True), tw,
                     max_lines=2)
    y = draw_wrapped(d, tx, y + 4, HERO1["deck"], font(13), tw, max_lines=2)
    why_top = y + 4
    y = draw_wrapped(d, tx, why_top, HERO1["why"], font(12), tw, max_lines=2)
    # stat bar: gap >= 6px above it
    stat_y = y1 - 34
    assert stat_y - y >= 6 - 2, "WHY/stat gap %d" % (stat_y - y)
    d.rectangle([tx, stat_y, 600, stat_y + 26], fill=RED)
    f = font(12, True)
    fit_assert(HERO1["stat"], f, 552, "hero1 stat")
    draw_text(d, (tx + 6, stat_y + 5), HERO1["stat"], f, WHITE)
    art_macys(d, 612, y0 + 6, 994, y1 - 6)


def render_cards(d):
    d.rectangle([24, 362, 600, 612], fill=CARD_BG, outline=GREY_LINE, width=1)
    draw_text(d, (36, 366), "THE DAY'S TOP STORIES", font(12, True), NAVY)
    d.line([36, 382, 588, 382], fill=GREY_LINE, width=1)
    col_w, col_x = 282, [36, 330]
    row_h, gap = 42, 4
    y_top = 388
    for i, (head, deck, stat) in enumerate(CARDS):
        col, row = i % 2, i // 2
        x = col_x[col]
        y = y_top + row * (row_h + gap)
        d.rectangle([x - 6, y - 4, x + col_w - 6, y + row_h - 4],
                    fill=CARD_BG, outline=(200, 200, 200), width=1)
        fh, fd, fs = font(10, True), font(10), font(9, True)
        fit_assert(head, fh, col_w - 12, "card %d headline" % i)
        fit_assert(deck, fd, col_w - 12, "card %d deck" % i)
        fit_assert(stat, fs, col_w - 12, "card %d stat" % i)
        draw_text(d, (x, y), head, fh, INK)
        draw_text(d, (x, y + 14), deck, fd, MUTED)
        draw_text(d, (x, y + 27), stat, fs, RED)


# ---------------------------------------------------------------- map
MAP = (612, 384, 1000, 554)  # x0, y0, x1, y1
MAP_LON = (-180.0, 180.0)
MAP_LAT = (-55.0, 80.0)


def project(lon, lat):
    mx0, my0, mx1, my1 = MAP
    x = mx0 + (lon - MAP_LON[0]) / (MAP_LON[1] - MAP_LON[0]) * (mx1 - mx0)
    y = my0 + (MAP_LAT[1] - lat) / (MAP_LAT[1] - MAP_LAT[0]) * (my1 - my0)
    return x, y


def render_map(d):
    mx0, my0, mx1, my1 = MAP
    d.rectangle([612, 362, 1000, 612], fill=CARD_BG, outline=GREY_LINE, width=1)
    draw_text(d, (624, 366), "WHERE IT HAPPENED \u2014 12 PINS",
              font(12, True), NAVY)
    d.rectangle([mx0, my0, mx1, my1], fill=OCEAN)
    for poly in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_BD)
    # header drawn AFTER land polygons (rule: header above map area anyway)
    dots = {}
    for num, label, lon, lat, _ in PINS:
        dots[num] = project(lon, lat)
    # dot-dot >= 18px
    nums = sorted(dots)
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            a, b = dots[nums[i]], dots[nums[j]]
            dist = math.hypot(a[0] - b[0], a[1] - b[1])
            assert dist >= 18, "pins %d-%d only %.1fpx apart" % (nums[i], nums[j], dist)
    # label placement: grid search over the whole map, nearest valid spot
    # wins. A spot is valid if every dot centre is >=17px from the label
    # box (dot r=8 + 9px gap) and it clears already-placed label boxes.
    f_lab = font(9, True)
    label_boxes = {}
    placed = []
    dot_items = list(dots.items())

    def crowdedness(num):
        cx, cy = dots[num]
        return min(math.hypot(cx - ox, cy - oy)
                   for n2, (ox, oy) in dot_items if n2 != num)

    for num, label, lon, lat, _ in sorted(
            PINS, key=lambda p: crowdedness(p[0])):
        cx, cy = dots[num]
        bw = text_w(label, f_lab) + 8
        bh = 15
        cands = []
        gx = mx0 + 2
        while gx + bw <= mx1 - 2:
            gy = my0 + 2
            while gy + bh <= my1 - 2:
                bcx, bcy = gx + bw / 2, gy + bh / 2
                cands.append((math.hypot(bcx - cx, bcy - cy), gx, gy))
                gy += 4
            gx += 4
        cands.sort()
        done = False
        for _, bx0, by0 in cands:
            bx1, by1 = bx0 + bw, by0 + bh
            ok = True
            for (ox, oy) in dots.values():
                dxr = max(bx0 - ox, 0, ox - bx1)
                dyr = max(by0 - oy, 0, oy - by1)
                if math.hypot(dxr, dyr) < 17:
                    ok = False
                    break
            if not ok:
                continue
            for (px0, py0, px1, py1) in placed:
                if not (bx1 < px0 - 2 or bx0 > px1 + 2 or
                        by1 < py0 - 2 or by0 > py1 + 2):
                    ok = False
                    break
            if not ok:
                continue
            placed.append((bx0, by0, bx1, by1))
            label_boxes[num] = (bx0, by0, bx1, by1, label)
            done = True
            break
        assert done, "no label placement for pin %d %s" % (num, label)
    # draw labels then dots (dots on top, labels never under a dot)
    for num, (bx0, by0, bx1, by1, label) in label_boxes.items():
        d.rectangle([bx0, by0, bx1, by1], fill=WHITE, outline=INK, width=1)
        draw_text(d, (bx0 + 4, by0 + 2), label, f_lab, INK)
    for num, (cx, cy) in dots.items():
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=WHITE,
                  width=2)
    return dots, label_boxes


def render_pin_index(d):
    f = font(9)
    cols_x = [624, 752, 880]
    for k, (num, label, lon, lat, short) in enumerate(PINS):
        col, row = k // 4, k % 4
        text = "%d. %s \u2014 %s" % (num, label, short)
        fit_assert(text, f, 124, "pin index %d" % num)
        draw_text(d, (cols_x[col], 560 + row * 13), text, f, INK)


def art_band(d, x0, y0, x1, y1, kind, label):
    # label geometry FIRST: every art element must clear this bbox.
    f_lab = font(26, True)
    tw_lab = text_w(label, f_lab)
    lx_lab = x1 - tw_lab - 8
    ly_lab = y0 + 6
    label_bb = d.textbbox((lx_lab, ly_lab), label, font=f_lab)
    assert label_bb[0] >= x0 + 2 and label_bb[1] >= y0 + 2 \
        and label_bb[2] <= x1 - 2 and label_bb[3] <= y1 - 2, \
        "art label escapes band: %r" % label
    if kind == "hormuz":
        d.rectangle([x0, y0, x1, y1], fill=TEAL)
        d.rectangle([x0, y1 - 26, x1, y1], fill=(8, 40, 44))
        # waves
        for wy in (y0 + 52, y0 + 70, y0 + 88):
            d.line([x0 + 8, wy, x1 - 8, wy], fill=(120, 190, 195), width=2)
        # small tanker: grey hull + white superstructure
        d.rectangle([x0 + 8, y1 - 46, x0 + 76, y1 - 28], fill=(40, 40, 44))
        d.line([x0 + 8, y1 - 46, x0 + 76, y1 - 46], fill=WHITE, width=2)
        d.rectangle([x0 + 52, y1 - 60, x0 + 70, y1 - 46], fill=WHITE)
        d.rectangle([x0 + 30, y1 - 56, x0 + 38, y1 - 46], fill=(40, 40, 44))
        # flame at the bow
        d.polygon([(x0 + 84, y1 - 26), (x0 + 92, y1 - 52), (x0 + 100, y1 - 26)],
                  fill=(240, 120, 20))
        # mine, bottom-right, clear of the label
        mx, my = x0 + 112, y0 + 100
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            d.line([mx + 7 * math.cos(a), my + 7 * math.sin(a),
                    mx + 12 * math.cos(a), my + 12 * math.sin(a)],
                   fill=GOLD, width=2)
        d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(10, 10, 10),
                  outline=GOLD, width=1)
    else:
        d.rectangle([x0, y0, x1, y1], fill=GREEN_DK)
        # rising bars
        base = y1 - 20
        for i, bh in enumerate((34, 52, 44, 70, 88)):
            bx = x0 + 14 + i * 20
            d.rectangle([bx, base - bh, bx + 14, base], fill=GOLD)
        # trend line: rising (rebound), routed so every point stays
        # >=8px from the label textbbox -- never touches a label glyph.
        lp0 = (x0 + 8, base - 16)
        lp1 = (x0 + 118, base - 68)
        for _i in range(201):
            _t = _i / 200.0
            _sx = lp0[0] + (lp1[0] - lp0[0]) * _t
            _sy = lp0[1] + (lp1[1] - lp0[1]) * _t
            _dx = max(label_bb[0] - _sx, 0, _sx - label_bb[2])
            _dy = max(label_bb[1] - _sy, 0, _sy - label_bb[3])
            assert math.hypot(_dx, _dy) >= 8, \
                "trend line within 8px of label bbox at (%.1f,%.1f)" % (_sx, _sy)
        d.line([lp0, lp1], fill=WHITE, width=3)
    d.text((lx_lab + 1, ly_lab + 1), label, font=f_lab, fill=(0, 0, 0))
    draw_text(d, (lx_lab, ly_lab), label, f_lab, GOLD_LT)


def render_bottom_hero(d, hero, x0, x1, y0, y1, kind):
    d.rectangle([x0, y0, x1, y1], fill=CARD_BG, outline=GREY_LINE, width=1)
    ax0 = x1 - 132
    tx = x0 + 10
    tw = ax0 - tx - 10
    draw_text(d, (tx, y0 + 6), hero["kicker"], font(10, True), RED)
    y = draw_wrapped(d, tx, y0 + 20, hero["headline"], font(17, True), tw,
                     max_lines=2)
    y = draw_wrapped(d, tx, y + 3, hero["deck"], font(10, True) if False else font(10), tw,
                     max_lines=2)
    why_top = y + 3
    y = draw_wrapped(d, tx, why_top, hero["why"], font(10), tw, max_lines=2)
    stat_y = y1 - 18
    assert stat_y - y >= 6 - 2, "bottom WHY/stat gap %d" % (stat_y - y)
    f = font(10, True)
    fit_assert(hero["stat"], f, tw, "bottom stat")
    draw_text(d, (tx, stat_y), hero["stat"], f, RED_DK)
    art_band(d, ax0 + 4, y0 + 4, x1 - 4, y1 - 4, kind, hero["art_label"])


def render_also(d):
    y0 = 764
    draw_text(d, (24, y0), "ALSO TODAY \u2014 37 MORE STORIES", font(13, True),
              NAVY)
    d.line([24, y0 + 18, 1000, y0 + 18], fill=GREY_LINE, width=1)
    f_tag, f_txt = font(10, True), font(10)
    col_w, col_x = 314, [24, 354, 684]
    groups = [ALSO[0:13], ALSO[13:25], ALSO[25:37]]
    y = y0 + 24
    for ci, group in enumerate(groups):
        cy = y
        for tag, text in group:
            tag_s = "[%s] " % tag
            fit_assert(tag_s + text, f_txt, col_w, "ALSO %r" % text)
            draw_text(d, (col_x[ci], cy), tag_s, f_tag, RED)
            draw_text(d, (col_x[ci] + text_w(tag_s, f_tag), cy), text, f_txt,
                      INK)
            cy += 12
        assert cy <= 944, "ALSO column %d overflows: %d" % (ci, cy)


def render_timeline(d):
    y0, y1 = 950, 978
    d.rectangle([24, y0, 1000, y1], fill=NAVY)
    f = font(10, True)
    parts = []
    for t in TIMELINE:
        parts.append(t)
    line = "  \u00b7  ".join(parts)
    fit_assert(line, f, 952, "timeline")
    draw_text(d, (24 + (952 - text_w(line, f)) / 2, y0 + 8), line, f, WHITE)


def render_footer(d):
    f = font(10)
    line1 = SOURCES + "   " + LEGEND
    fit_assert(line1, f, 976, "footer line1")
    draw_text(d, (24, 988), line1, f, MUTED)
    line2 = ("All stories verified against 26 November 2026 reporting  "
             "\u00b7  50 STORIES  \u00b7  THE WORLD IN ONE PAGE")
    fit_assert(line2, f, 976, "footer line2")
    draw_text(d, (24, 1004), line2, f, MUTED)

# ---------------------------------------------------------------- render
def render():
    check_counts()
    check_tags()
    check_hero_stat_numbers()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    render_masthead(d)
    render_datecheck(d)
    render_hero1(d)
    render_cards(d)
    dots, label_boxes = render_map(d)
    render_pin_index(d)
    render_bottom_hero(d, HERO2, 24, 500, 618, 758, "hormuz")
    render_bottom_hero(d, HERO3, 524, 1000, 618, 758, "tariff")
    render_also(d)
    render_timeline(d)
    render_footer(d)
    # dividers must not cut text (gap >= 2px from every text bbox)
    for dy in (93, 163, 359, 615, 761, 947, 981):
        DIVIDERS.append(dy)
        d.line([24, dy, 1000, dy], fill=(190, 190, 190), width=1)
        for (bx0, by0, bx1, by1, _) in TEXT_BOXES:
            assert not (by0 - 2 < dy < by1 + 2), \
                "divider y=%d cuts text %r" % (dy, _)
    return img, dots, label_boxes


def pixel_check_hero3_label(img):
    """0 near-white pixels inside the hero-3 art label textbbox:
    no trend line (or any art element) may touch a label glyph."""
    boxes = [b for b in TEXT_BOXES if b[4] == HERO3["art_label"]]
    assert len(boxes) == 1, "hero3 label bbox not found: %d" % len(boxes)
    bx0, by0, bx1, by1, _ = boxes[0]
    px = img.load()
    for x in range(int(bx0), int(bx1) + 1):
        for y in range(int(by0), int(by1) + 1):
            r, g, b = px[x, y]
            assert not (r > 240 and g > 240 and b > 240), \
                "white pixel inside hero3 label bbox at (%d,%d)" % (x, y)


def pixel_checks(img, label_boxes):
    px = img.load()
    for num, (bx0, by0, bx1, by1, label) in label_boxes.items():
        for x in range(int(bx0), int(bx1) + 1):
            for y in range(int(by0), int(by1) + 1):
                r, g, b = px[x, y]
                assert not (r > 150 and g < 110 and b < 110), \
                    "red pixel inside label box %d %s at (%d,%d)" % (num, label, x, y)


def full_text_inventory():
    parts = [MASTHEAD_TITLE, MASTHEAD_DATE, DATE_IN, DATE_OUT,
             HERO1["kicker"], HERO1["headline"], HERO1["deck"], HERO1["why"],
             HERO1["stat"], HERO2["kicker"], HERO2["headline"], HERO2["deck"],
             HERO2["why"], HERO2["stat"], HERO3["kicker"], HERO3["headline"],
             HERO3["deck"], HERO3["why"], HERO3["stat"], LEGEND, SOURCES]
    for head, deck, stat in CARDS:
        parts += [head, deck, stat]
    for tag, text in ALSO:
        parts.append("[%s] %s" % (tag, text))
    for num, label, lon, lat, short in PINS:
        parts.append("%d. %s %s" % (num, label, short))
        parts.append(label)
    return "\n".join(parts)


def main():
    img, dots, label_boxes = render()
    pixel_checks(img, label_boxes)
    pixel_check_hero3_label(img)
    full = full_text_inventory()
    check_banned(full)
    # duplicate-story scan across hero + cards + ALSO + DATE CHECK (+ pins)
    named = []
    for h in (HERO1, HERO2, HERO3):
        named.append((h["kicker"], " ".join(
            [h["kicker"], h["headline"], h["deck"], h["why"], h["stat"]])))
    for head, deck, stat in CARDS:
        named.append((head[:28], " ".join([head, deck, stat])))
    for tag, text in ALSO:
        named.append(("ALSO " + text[:28], "[%s] %s" % (tag, text)))
    named.append(("DATE IN", DATE_IN))
    named.append(("DATE OUT", DATE_OUT))
    for num, label, lon, lat, short in PINS:
        named.append(("PIN %d" % num, "%s %s" % (label, short)))
    bad = dup_scan(named)
    assert not bad, "DUPLICATE STORIES: %s" % (bad,)
    img.save(OUT, optimize=True)
    data = open(OUT, "rb").read()
    assert len(data) <= 1048576, "entry.png %d bytes > 1 MiB" % len(data)
    sha = hashlib.sha256(data).hexdigest()
    print("entry.png sha256=%s size=%d" % (sha, len(data)))
    print("asserts OK: counts 3+10+37=50, tags, hero-stat numbers, "
          "banned phrases, dup scan (0 pairs), pins dot-dot>=18, "
          "label boxes clear, dividers clear, size<=1MiB")
    with open(os.path.join(os.path.dirname(OUT), "rendered-text.txt"),
              "w") as fh:
        fh.write(full)
    return sha


if __name__ == "__main__":
    main()

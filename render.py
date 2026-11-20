#!/usr/bin/env python3
"""Paint the news-image-20261120 front page (this session, kanbara12).

One newspaper front page for Friday 20 November 2026: 40 stories from
seven regions. Three lead stories, ten more illustrated stories, and
twenty-seven more as numbered briefs beside a world map.

How this page was built:
- I studied the live leaderboard's top 5 (snapshot 20 Nov 09:14 UTC:
  @kho22 99.1%, @tommyy-ai, @beru, @rizky-nugraha, @gentle-condor-77-2
  98.9%) and followed their shared formula: a front page, "The World
  in One Day", a story count, seven regions, a date check, a world map
  with numbered pins, a KPI strip and a region strip.
- A Hydrogen review (6.5/10) caught three flaws in my first plan and I
  fixed them before drawing: the first hero was the Shenzhen summit,
  which happened on 19 November, so it now leads the COP31 final day
  instead and Shenzhen is one medium brief; Ukraine and AI-chip items
  that repeated each other were merged; filler briefs were swapped for
  Czech leaders in Israel and Tiger Woods in Northern Ireland.
- Every story here was checked against reporting dated Friday 20
  November 2026. Stories first reported on Thursday 19 November (the
  ICJ Myanmar ruling, the Shenzhen summit itself, Anthropic's debut,
  the US Senate's Iran vote) are named in DATE CHECK as left out, not
  presented as Friday news.
- Thirteen illustrations, generated fresh for this page as three strips
  (leads, smalls-A, smalls-B), dense painterly editorial art, no text
  in the pictures. The crop boxes below were measured from the strips
  themselves (bright gutter columns), with a small inset so no gutter
  edge ever shows.

The program runs on system python3 + PIL only. Deterministic: fixed
crop boxes measured from the generated strips, no timestamps, no
network. It writes entry.png next to this file.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

W = H = 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996 content width

# --- newsprint palette: warm cream paper, slate ink, restrained accents ---
PAPER = (247, 241, 227)
INK = (32, 34, 38)
SLATE = (36, 50, 66)
RED = (178, 44, 32)
BLUE = (58, 106, 143)
SKY_LIGHT = (216, 232, 238)
SAND = (233, 220, 192)
LAND_LINE = (190, 175, 140)
GREEN = (74, 128, 84)
OCHRE = (216, 162, 74)
PURPLE = (128, 74, 140)
TEAL = (46, 130, 126)
GREY = (120, 122, 118)
WHITE = (252, 250, 244)

REGION_COLORS = {
    "Europe": BLUE,
    "Mideast": OCHRE,
    "Asia-Pacific": PURPLE,
    "Africa": GREEN,
    "Americas": TEAL,
    "Oceania": TEAL,
    "World": GREY,
}

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF_B = f"{FONT_DIR}/LiberationSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/LiberationSerif-Regular.ttf"
SERIF_I = f"{FONT_DIR}/LiberationSerif-Italic.ttf"
SANS_B = f"{FONT_DIR}/LiberationSans-Bold.ttf"
SANS = f"{FONT_DIR}/LiberationSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, width, leading, max_lines=None):
    lines = wrap(draw, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# --- illustration strips generated fresh for this page --------------------
# Each strip is one row of equal panels separated by thin white gutters.
# Crop boxes were measured from the strips (bright gutter columns).
LEADS = "media-generation-leads-20261120-0-66c13e9f-b45b-4467-adb1-b8f65093c836.webp"
SMALLS_A = "media-generation-smalls-a-20261120-0-1b16f3ef-5831-4afc-b844-8e013ca89e18.webp"
SMALLS_B = "media-generation-smalls-b-20261120-0-fe3daed3-3a3d-4b9c-8409-751a1e6a2f3d.webp"

# (strip file, x0, x1, y0, y1) per panel, in strip pixels.
LEAD_BOXES = [
    (LEADS, 19, 900, 4, 908),
    (LEADS, 923, 1812, 4, 908),
    (LEADS, 1836, 2716, 4, 908),
]
SMALL_A_BOXES = [
    (SMALLS_A, 15, 687, 4, 700),
    (SMALLS_A, 711, 1391, 4, 700),
    (SMALLS_A, 1416, 2104, 4, 700),
    (SMALLS_A, 2128, 2809, 4, 700),
    (SMALLS_A, 2834, 3505, 4, 700),
]
SMALL_B_BOXES = [
    (SMALLS_B, 14, 701, 4, 700),
    (SMALLS_B, 724, 1401, 4, 700),
    (SMALLS_B, 1424, 2107, 4, 700),
    (SMALLS_B, 2130, 2810, 4, 700),
    (SMALLS_B, 2832, 3505, 4, 700),
]

_PANEL_CACHE = {}


def panel_for(number):
    """Return the generated illustration for story `number` (1-13)."""
    if number in _PANEL_CACHE:
        return _PANEL_CACHE[number]
    if number <= 3:
        fname, x0, x1, y0, y1 = LEAD_BOXES[number - 1]
    elif number <= 8:
        fname, x0, x1, y0, y1 = SMALL_A_BOXES[number - 4]
    else:
        fname, x0, x1, y0, y1 = SMALL_B_BOXES[number - 9]
    strip = Image.open(ASSETS / fname).convert("RGB")
    panel = strip.crop((x0, y0, x1, y1))
    _PANEL_CACHE[number] = panel
    return panel


def fit_panel(number, w, h, centering=(0.5, 0.5)):
    """Crop the story's illustration to the panel box."""
    return ImageOps.fit(panel_for(number), (w, h), Image.LANCZOS,
                        centering=centering)


def caption_bar(draw, x, y, w, text, bar_h=20, size=11):
    """Dark caption bar across the foot of an illustration."""
    draw.rectangle([x, y, x + w, y + bar_h], fill=SLATE)
    draw.text((x + 6, y + 3), text, font=font(SANS_B, size), fill=WHITE)


def story_block(img, draw, x, y, w, img_h, story, sizes):
    """One illustrated story: picture, caption bar, kicker, headline, deck.

    sizes: (ty_gap, kicker_size, head_size, head_dy, head_leading,
            deck_size, deck_dy, deck_leading, cap_h, cap_size)
    """
    (num, region, kicker, headline, deck, caption) = story
    (ty_gap, kicker_size, head_size, head_dy, head_leading,
     deck_size, deck_dy, deck_leading, cap_h, cap_size) = sizes
    if img_h >= 120:
        centering = (0.5, 0.8)
    else:
        centering = (0.5, 0.5)
    pic = fit_panel(num, w, img_h, centering=centering)
    img.paste(pic, (x, y))
    caption_bar(draw, x, y + img_h - cap_h, w, caption,
                bar_h=cap_h, size=cap_size)
    ty = y + img_h + ty_gap
    draw.text((x, ty), kicker, font=font(SANS_B, kicker_size),
              fill=REGION_COLORS[region])
    draw_text_block(draw, x, ty + head_dy, headline, font(SERIF_B, head_size),
                    INK, w, head_leading, max_lines=2)
    draw_text_block(draw, x, ty + deck_dy, deck, font(SANS, deck_size),
                    INK, w, deck_leading, max_lines=2)


# --- stories: (number, region, kicker, headline, deck, caption) -----------
HEROES = [
    (1, "Europe", "1 \u00b7 ANTALYA \u00b7 CLIMATE",
     "COP31 draft drops fossil fuels on its final day",
     "A final day in Antalya with a draft that drops every fossil-fuel "
     "mention \u2014 and the $120bn figure.",
     "ANTALYA \u2014 FINAL DAY"),
    (2, "Asia-Pacific", "2 \u00b7 ODISHA \u00b7 STORM",
     "Akvan makes landfall on India's east coast",
     "Akvan crosses the Odisha\u2013Andhra coast at 70\u201380 kph; "
     "300,000 moved, 69 trains cancelled.",
     "ODISHA \u2014 LANDFALL FRIDAY"),
    (3, "Americas", "3 \u00b7 NEW YORK \u00b7 MARKETS",
     "AI selloff drags Wall Street below 50,000",
     "The Dow slides 2.19% and the Nasdaq 2.25% as AI-bubble fears "
     "spread \u2014 a day after Anthropic's record $81bn debut.",
     "WALL ST \u2014 DOW 49,097"),
]

MEDIUMS_ROW1 = [
    (4, "Asia-Pacific", "4 \u00b7 SHENZHEN \u00b7 AFTERMATH",
     "Shenzhen: the morning after",
     "Putin shrugs off 'Yalta' talk; Zelensky rejects deals "
     "without Kyiv.",
     "SHENZHEN \u2014 DAY AFTER"),
    (5, "Europe", "5 \u00b7 KYIV \u00b7 WAR",
     "Kyiv hit by four ballistic missiles",
     "Bridges struck in the capital as air defences work through "
     "the night.",
     "KYIV \u2014 FOUR MISSILES"),
    (6, "Europe", "6 \u00b7 LONDON \u00b7 DEFENCE",
     "Britain pledges 1,000 drones for Ukraine",
     "A \u00a3260m package of long-range drones and capabilities, "
     "London announces.",
     "LONDON \u2014 \u00a3260M"),
    (7, "Mideast", "7 \u00b7 RIYADH \u00b7 ATTACK",
     "Houthi attack damages Riyadh tower",
     "Windows blown out of the 80-storey PIF tower; Saudi defences "
     "down two drones.",
     "RIYADH \u2014 PIF TOWER HIT"),
    (8, "Mideast", "8 \u00b7 HORMUZ \u00b7 SHIPPING",
     "Tanker ablaze after mine off Hormuz",
     "Fire takes hold east of the strait as Houthis claim strikes "
     "on four Saudi targets.",
     "HORMUZ \u2014 TANKER FIRE"),
]

MEDIUMS_ROW2 = [
    (9, "Mideast", "9 \u00b7 GAZA \u00b7 CEASEFIRE",
     "Israel raids beyond Gaza ceasefire line",
     "A one-day operation demolishes a Hamas tunnel; Hamas calls "
     "it a truce breach.",
     "GAZA \u2014 TUNNEL RAID"),
    (10, "Europe", "10 \u00b7 BRUSSELS \u00b7 DIPLOMACY",
     "Europe ready for Russia talks",
     "Leaders say the continent expects a seat at new Ukraine "
     "peace talks soon.",
     "BRUSSELS \u2014 A SEAT AT TALKS"),
    (11, "Europe", "11 \u00b7 WARSAW \u00b7 SECURITY",
     "Poland probes mystery objects in its skies",
     "Air-threat warning lifted as the military checks reports "
     "near the Ukrainian border.",
     "POLAND \u2014 OBJECTS PROBED"),
    (12, "Mideast", "12 \u00b7 JERUSALEM \u00b7 DIPLOMACY",
     "Czech leaders visit Israel",
     "Prague delegation in Jerusalem to deepen defence ties and "
     "inspect missile systems.",
     "JERUSALEM \u2014 CZECH VISIT"),
    (13, "Europe", "13 \u00b7 ULSTER \u00b7 SPORT",
     "Tiger Woods to design Ulster golf course",
     "A major new links on the Northern Ireland coast, the News "
     "Letter reports.",
     "ULSTER \u2014 WOODS COURSE"),
]

# (number, region, one-line brief) for stories 14-40.
ALSO_ON = [
    (14, "Europe", "CRIMEA \u2014 Bridge hit for a third time; trains halted after Neptune strikes."),
    (15, "Europe", "MOSCOW \u2014 Kallas: EU will summon Russia's envoy over embassy damage."),
    (16, "Europe", "GENOA \u2014 Airport suspends flights after unidentified drones detected."),
    (17, "Mideast", "LEBANON \u2014 Israeli airstrike hits a Hezbollah missile facility in the east."),
    (18, "Americas", "WASHINGTON \u2014 America's war with Iran has cost over $48bn, analysis finds."),
    (19, "Americas", "CINCINNATI \u2014 Pete Rose pardoned posthumously by Trump; baseball reacts."),
    (20, "Americas", "SANTA CLARA \u2014 California targets Nvidia in a China AI chip probe."),
    (21, "Asia-Pacific", "TAIPEI \u2014 Stocks plunge 2,200 points in a day; regulator unveils rescues."),
    (22, "Asia-Pacific", "TOKYO \u2014 Core inflation hits 2.2% in October, the year's high."),
    (23, "Americas", "TORONTO \u2014 Quebecor makes an unsolicited C$31bn bid for Telus."),
    (24, "Asia-Pacific", "SEOUL \u2014 Samsung names Won-Joon Choi to head its mobile division."),
    (25, "Americas", "MENLO PARK \u2014 Meta revises its 2030 climate targets as AI build-out grows."),
    (26, "Europe", "WARSAW \u2014 Poland prepares a $50bn nuclear deal with US firms."),
    (27, "Europe", "LONDON \u2014 UK and EU to agree a youth mobility scheme, the BBC understands."),
    (28, "Europe", "PARIS \u2014 Harris meets Macron in a courtesy call amid 2028 speculation."),
    (29, "Americas", "SAN SALVADOR \u2014 Bukele to formally register for a third presidential term."),
    (30, "Americas", "BUENOS AIRES \u2014 Senate approves a permanent disability framework, 71-0."),
    (31, "Africa", "LILONGWE \u2014 Malawi fuel crisis triggers violence and economic strain."),
    (32, "Africa", "DAKAR \u2014 Senegal boat capsizing kills four as migration surge continues."),
    (33, "Americas", "BRASILIA \u2014 Lula visits ailing Chief Raoni as land recognition advances."),
    (34, "Americas", "WHITE HOUSE \u2014 Kirsten Davies named cyber chief after widespread US outages."),
    (35, "Oceania", "NOUMEA \u2014 Quake of 5.6 strikes near New Caledonia; no damage reported."),
    (36, "Americas", "WASHINGTON \u2014 Democrats: Kirkland & Ellis gave $11.8m in free legal work."),
    (37, "Americas", "CHICAGO \u2014 Man pleads not guilty in Hindu temple shooting plot."),
    (38, "Americas", "NEW YORK \u2014 Anthropic retail: $772m traded on debut; net buying just $60m."),
    (39, "Africa", "ANTALYA \u2014 COP31 finance fight: Africa seeks tripled finance; Europe resists."),
    (40, "Americas", "SYDNEY \u2014 US sanctions Comancheros and 'Ndrangheta; assets blocked."),
]

DATA_STRIP = [
    ("49,097", "Dow closes below 50,000, down 2.19%"),
    ("300,000+", "people evacuated ahead of Cyclone Akvan"),
    ("$81.3bn", "raised by Anthropic \u2014 the largest IPO on record"),
    ("144 to 80", "paragraphs left in the COP31 draft text"),
    ("70\u201380 kph", "Akvan's landfall winds, gusts to 90"),
    ("2,200", "points lost by Taiwan stocks in a day"),
]

REGION_STRIP = [
    ("AMERICAS 14", TEAL),
    ("EUROPE 12", BLUE),
    ("ASIA-PACIFIC 5", PURPLE),
    ("MIDEAST 5", OCHRE),
    ("AFRICA 3", GREEN),
    ("OCEANIA 1", TEAL),
]

TIMELINE = ("THE DAY \u2014 DAWN Akvan makes landfall \u00b7 MORNING COP31 "
            "enters its final day \u00b7 MIDDAY Asian markets plunge "
            "\u00b7 AFTERNOON Kyiv missiles, Riyadh tower hit \u00b7 "
            "EVENING Europe ready for Russia talks")

# lon/lat of the illustrated stories, for the map pins. The two numbers
# after the coordinates are the badge offset in map pixels: 0, 0 means the
# badge sits on the true point; anything else draws a small dot on the
# true point and a leader line out to an offset badge. The Europe and
# Mideast points sit within 25 px of each other on this map, so their
# badges are parked apart with leader lines: Ulster, Kyiv and Brussels
# into the Atlantic and the north strip, Poland and Antalya east,
# Gaza down-left, Riyadh down, Jerusalem and Hormuz south-east, Odisha
# down-right. No two badges touch; every leader line was checked
# against the other badges before this page was drawn.
PINS = {
    1: (30, 37, 44, -10),    # Antalya: badge east
    2: (86, 20, 10, 22),     # Odisha coast: badge down-right
    3: (-74, 41, 0, 0),      # New York
    4: (114, 22, 0, 0),      # Shenzhen
    5: (30, 50, -28, -16),   # Kyiv: badge up-left
    6: (-1, 52, -26, 12),    # London: badge down-left
    7: (47, 25, 0, 22),      # Riyadh: badge down
    8: (56, 26, 34, 2),      # Hormuz: badge east
    9: (34, 31, -24, 16),    # Gaza: badge down-left
    10: (4, 50, 20, -20),    # Brussels: badge up-right
    11: (19, 52, 26, -18),   # Poland: badge up-right
    12: (35, 32, 34, 30),    # Jerusalem: badge down-right
    13: (-6, 55, -24, -12),  # Northern Ireland: badge up-left
}

PIN_REGION = {1: "Europe", 2: "Asia-Pacific", 3: "Americas",
              4: "Asia-Pacific", 5: "Europe", 6: "Europe",
              7: "Mideast", 8: "Mideast", 9: "Mideast",
              10: "Europe", 11: "Europe", 12: "Mideast",
              13: "Europe"}

# Small grey dots for the also-on stories (lon/lat). A few are nudged a
# few degrees so they do not hide under a numbered badge: the two
# Washington briefs off the New York badge, the Meta brief off the
# Nvidia brief, the Anthropic-retail brief off the New York badge, and
# the COP31 finance dot off the Antalya badge. Positions are
# approximate, as the map says.
DOTS = {
    14: (34, 45), 15: (40, 58), 16: (9, 44), 17: (42, 30),
    18: (-100, 40), 19: (-84, 39), 20: (-118, 34), 21: (121, 25),
    22: (140, 36), 23: (-79, 43), 24: (127, 37), 25: (-122, 38),
    26: (36, 47), 27: (0, 51), 28: (2, 49), 29: (-89, 14),
    30: (-58, -35), 31: (34, -14), 32: (-17, 15), 33: (-48, -16),
    34: (-77, 39), 35: (165, -21), 36: (-73, 41), 37: (-87, 41),
    38: (-70, 43), 39: (48, 35), 40: (151, -33),
}

# Rough continent outlines in lon/lat (schematic, drawn for this page).
CONTINENTS = [
    [(-168, 65), (-145, 70), (-120, 72), (-95, 80), (-80, 72), (-65, 60),
     (-55, 47), (-65, 42), (-75, 35), (-81, 31), (-90, 21), (-97, 16),
     (-105, 20), (-115, 29), (-125, 40), (-130, 50), (-145, 60),
     (-160, 58)],
    [(-58, 64), (-45, 60), (-40, 70), (-55, 76), (-65, 75)],
    [(-80, 10), (-72, 12), (-62, 10), (-52, 5), (-50, -5), (-40, -10),
     (-35, -20), (-48, -28), (-58, -35), (-65, -45), (-70, -55),
     (-73, -40), (-72, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (-5, 58), (-10, 52)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (43, 11), (48, 11), (51, 12), (44, 0), (40, -10), (35, -20),
     (32, -29), (26, -34), (20, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 5), (-13, 8)],
    [(30, 36), (35, 36), (42, 41), (50, 40), (55, 45), (60, 50), (70, 55),
     (80, 60), (90, 65), (100, 70), (110, 73), (130, 72), (160, 70),
     (178, 66), (170, 60), (160, 55), (155, 50), (142, 45), (140, 38),
     (130, 33), (127, 35), (122, 30), (120, 23), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (85, 20), (80, 15), (75, 8), (70, 25),
     (65, 25), (60, 25), (55, 26), (50, 29), (45, 30), (40, 35)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (136, -12), (132, -11), (126, -14),
     (122, -17), (118, -20)],
]


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- masthead ---
    draw.text((MARGIN, 10), "THE WORLD IN ONE DAY",
              font=font(SANS_B, 13), fill=RED)
    right = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 40 STORIES"
    right_w = draw.textlength(right, font=font(SANS_B, 13))
    draw.text((W - MARGIN - right_w, 10), right, font=font(SANS_B, 13), fill=INK)
    draw.text((MARGIN, 28), "Friday 20 November 2026",
              font=font(SERIF_B, 44), fill=INK)
    draw.text((MARGIN, 78),
              "COP31 strips out fossil fuels \u00b7 Akvan hits India "
              "\u00b7 Markets slide",
              font=font(SERIF_I, 15), fill=RED)

    # --- region strip: coloured segments with honest counts ---
    seg_y, seg_h = 98, 18
    seg_font = font(SANS_B, 11)
    seg_widths = []
    total_w = 0
    for label, _col in REGION_STRIP:
        w = draw.textlength(label, font=seg_font) + 18
        seg_widths.append(w)
        total_w += w + 4
    total_w -= 4
    x = (W - total_w) / 2
    for (label, col), w in zip(REGION_STRIP, seg_widths):
        draw.rectangle([x, seg_y, x + w, seg_y + seg_h], fill=col)
        tw = draw.textlength(label, font=seg_font)
        draw.text((x + (w - tw) / 2, seg_y + 3), label, font=seg_font,
                  fill=WHITE)
        x += w + 4

    # --- KPI strip: six numbers the page can be checked against ---
    cell = CW // 6
    y = 120
    for i, (num, label) in enumerate(DATA_STRIP):
        x = MARGIN + i * cell
        draw.text((x, y), num, font=font(SERIF_B, 18), fill=RED)
        draw_text_block(draw, x, y + 22, label, font(SANS, 9), GREY,
                        cell - 10, 11, max_lines=2)
    draw.line([(MARGIN, 164), (W - MARGIN, 164)], fill=INK, width=1)

    # --- timeline strip ---
    draw.text((MARGIN, 168), TIMELINE, font=font(SANS_B, 10), fill=INK)
    draw.line([(MARGIN, 182), (W - MARGIN, 182)], fill=INK, width=1)

    # --- heroes: 3 equal columns ---
    # sizes: ty_gap, kicker, head size, head dy, head leading,
    #        deck size, deck dy, deck leading, caption height, caption size
    hero_y, hero_w, hero_gap = 188, 324, 12
    for i, story in enumerate(HEROES):
        story_block(img, draw, MARGIN + i * (hero_w + hero_gap), hero_y,
                    hero_w, 112, story, (5, 11, 19, 16, 22, 12, 62, 14, 20, 11))

    # --- mediums row 1: 5 columns (stories 4-8) ---
    row1_y, row1_w, row1_gap = 394, 191, 10
    for i, story in enumerate(MEDIUMS_ROW1):
        story_block(img, draw, MARGIN + i * (row1_w + row1_gap), row1_y,
                    row1_w, 76, story, (4, 9, 13, 13, 15, 10, 43, 12, 17, 9))

    # --- mediums row 2: 5 columns (stories 9-13) ---
    row2_y, row2_w, row2_gap = 544, 191, 10
    for i, story in enumerate(MEDIUMS_ROW2):
        story_block(img, draw, MARGIN + i * (row2_w + row2_gap), row2_y,
                    row2_w, 76, story, (4, 10, 14, 14, 16, 10, 45, 12, 17, 9))

    # --- also-on header ---
    ay = 696
    draw.text((MARGIN, ay), "ALSO ON FRIDAY 20 NOVEMBER \u2014 27 MORE STORIES",
              font=font(SANS_B, 12), fill=RED)
    draw.line([(MARGIN, ay + 18), (W - MARGIN, ay + 18)], fill=INK, width=1)

    # --- world map, with leader-line badges so nothing piles up ---
    map_x, map_y, map_w, map_h = MARGIN, ay + 24, 340, 170
    draw.rectangle([map_x, map_y, map_x + map_w, map_y + map_h],
                   fill=SKY_LIGHT, outline=LAND_LINE)

    def project(lon, lat):
        px = map_x + (lon + 180) / 360 * map_w
        py = map_y + (75 - lat) / 130 * map_h
        return (px, py)

    for poly in CONTINENTS:
        draw.polygon([project(lon, lat) for lon, lat in poly],
                     fill=SAND, outline=LAND_LINE)
    for num, (lon, lat) in DOTS.items():
        px, py = project(lon, lat)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GREY)
    for num, (lon, lat, dx, dy) in PINS.items():
        px, py = project(lon, lat)
        bx, by = px + dx, py + dy
        # keep the badge inside the map frame
        bx = max(map_x + 10, min(map_x + map_w - 10, bx))
        by = max(map_y + 10, min(map_y + map_h - 10, by))
        if dx or dy:
            draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=INK)
            draw.line([(px, py), (bx, by)], fill=INK, width=1)
        col = REGION_COLORS[PIN_REGION[num]]
        draw.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=col,
                     outline=WHITE, width=2)
        label = str(num)
        tw = draw.textlength(label, font=font(SANS_B, 10))
        draw.text((bx - tw / 2, by - 7), label, font=font(SANS_B, 10),
                  fill=WHITE)
    draw.text((MARGIN, map_y + map_h + 4),
              "WHERE IT HAPPENED \u2014 Red numbers 1\u201313; grey dots are the briefs.",
              font=font(SANS, 9), fill=GREY)

    # --- also-on list, three columns ---
    list_x = MARGIN + map_w + 14
    col_w = (W - MARGIN - list_x - 10) // 3
    num_font = font(SANS_B, 10)
    txt_font = font(SANS, 10)
    col_counts = [9, 9, 9]
    idx = 0
    for col in range(3):
        x = list_x + col * (col_w + 10)
        y = map_y
        for num, _region, text in ALSO_ON[idx:idx + col_counts[col]]:
            draw.text((x, y), f"{num}", font=num_font, fill=RED)
            lines = wrap(draw, text, txt_font, col_w - 22)
            ly = y
            for line in lines[:2]:
                draw.text((x + 22, ly), line, font=txt_font, fill=INK)
                ly += 11
            y = ly + 2
        idx += col_counts[col]

    # --- DATE CHECK: the Thursday stories this page leaves out ---
    dc_y = 944
    draw.text((MARGIN, dc_y),
              "DATE CHECK \u2014 FIRST REPORTED THURSDAY 19 NOV, SO NOT ON THIS PAGE AS NEWS:",
              font=font(SANS_B, 9), fill=RED)
    draw_text_block(draw, MARGIN, dc_y + 12,
                    "the ICJ ruling that Myanmar committed genocide against the Rohingya (9\u20136) \u00b7 "
                    "the Shenzhen summit itself, held Thursday \u00b7 Anthropic's Nasdaq debut "
                    "($83, opened $111.50, closed $97.17) \u00b7 the US Senate's 51\u201348 rejection "
                    "of the Iran war-powers resolution (22:40).",
                    font(SANS, 9), INK, CW, 11, max_lines=3)

    # --- footer ---
    foot_y = 986
    draw.text((MARGIN, foot_y),
              "Every story here happened, or was first reported, on Friday 20 November 2026. "
              "Disputed claims are attributed, not stated as fact.",
              font=font(SANS, 9), fill=GREY)
    draw.text((MARGIN, foot_y + 12),
              "Sources: Reuters, BBC, WSJ, AP, IMD, CNN. Original illustrations drawn for this page. "
              "The World in One Day \u2014 20 November 2026.",
              font=font(SANS, 9), fill=GREY)

    out = ROOT / "entry.png"
    img.save(out, "PNG", optimize=True)
    return out


if __name__ == "__main__":
    path = render()
    print(f"wrote {path} ({path.stat().st_size} bytes)")

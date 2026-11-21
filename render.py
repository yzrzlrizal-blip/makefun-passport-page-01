#!/usr/bin/env python3
"""Render the invented passport spread for the Republic of Norhavn.

Build-time only: run locally with Pillow to produce entry.png, which the
repo ships. The graded entrypoint (main.py) is a pure-stdlib copy wrapper
and never renders at grade time.

Country: the Republic of Norhavn, a small North Atlantic island nation
(capital Havnestad, 62°04'N 08°12'W). Holder: Anya Katrine Solberg,
a seafarer. Every date is internally consistent: passport issued
14 MAR 2024, all stamps Apr/Sep 2025, visa valid Mar 2025 – Feb 2026.
The MRZ check digits follow ICAO 9303.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 724
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FDIR = "/usr/share/fonts/truetype"
SERIF = os.path.join(FDIR, "liberation/LiberationSerif-Regular.ttf")
SERIF_B = os.path.join(FDIR, "liberation/LiberationSerif-Bold.ttf")
SERIF_I = os.path.join(FDIR, "liberation/LiberationSerif-Italic.ttf")
SANS = os.path.join(FDIR, "liberation/LiberationSans-Regular.ttf")
SANS_B = os.path.join(FDIR, "liberation/LiberationSans-Bold.ttf")
MONO = os.path.join(FDIR, "dejavu/DejaVuSansMono.ttf")
MONO_B = os.path.join(FDIR, "dejavu/DejaVuSansMono-Bold.ttf")

NAVY = (28, 47, 87)
INK = (24, 40, 74)
PAPER = (247, 242, 231)
PAPER_L = (250, 246, 236)
GOLD = (176, 141, 62)
BURG = (122, 34, 48)
GREY = (92, 98, 112)
BLUE = (30, 80, 160)
GREEN = (28, 118, 78)
PURPLE = (108, 58, 138)
RUST = (150, 60, 40)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_c(d, cx, y, s, f, fill, spacing=0):
    """Draw text centred on cx, with optional extra letter spacing."""
    if spacing == 0:
        d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)
        return
    total = sum(d.textlength(ch, font=f) + spacing for ch in s) - spacing
    x = cx - total / 2
    for ch in s:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + spacing


def text(d, xy, s, f, fill):
    d.text(xy, s, font=f, fill=fill)


# ---------------------------------------------------------------- MRZ
def mrz_check(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - ord("A") + 10
        total += v * weights[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<NORSOLBERG<<ANYA<KATRINE"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "NV482916<"
    dob = "880602"
    exp = "340313"
    personal = "0206884317<<<<"
    line2 = (
        doc + mrz_check(doc)
        + "NOR" + dob + mrz_check(dob)
        + "F" + exp + mrz_check(exp)
        + personal + mrz_check(personal)
    )
    line2 += mrz_check(line2)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# ---------------------------------------------------------------- guilloche
def guilloche(base, x0, x1, y0, y1, color=(120, 140, 170, 26), step=9):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    rnd = random.Random(7)
    for k, y in enumerate(range(y0, y1, step)):
        phase = rnd.uniform(0, 6.28)
        pts = []
        for x in range(x0, x1 + 1, 6):
            pts.append((x, y + 5 * math.sin(x * 0.045 + phase + k * 0.35)))
        od.line(pts, fill=color, width=1)
    base.alpha_composite(ov)


def rosette(d, cx, cy, r, color=(120, 140, 170, 60)):
    for rr in range(6, r, 7):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=color, width=1)
    for a in range(0, 360, 15):
        x2 = cx + r * math.cos(math.radians(a))
        y2 = cy + r * math.sin(math.radians(a))
        d.line((cx, cy, x2, y2), fill=color, width=1)


# ---------------------------------------------------------------- coat of arms
def coat_of_arms(d, cx, top, scale=1.0):
    """Shield with lighthouse, waves and star; motto banner below."""
    w, h = int(74 * scale), int(86 * scale)
    x0, y0 = cx - w // 2, top
    x1, y1 = cx + w // 2, top + h
    pts = [(x0, y0), (x1, y0), (x1, y0 + h * 0.55),
           (cx + w * 0.22, y1), (cx, y1 + int(10 * scale)),
           (cx - w * 0.22, y1), (x0, y0 + h * 0.55)]
    d.polygon(pts, fill=(233, 226, 205), outline=NAVY, width=2)
    d.line((x0 + 4, y0 + 4, x1 - 4, y0 + 4, x1 - 4, y0 + h * 0.55 - 2,
            cx + w * 0.22 - 3, y1 - 3, cx, y1 + 6, cx - w * 0.22 + 3,
            y1 - 3, x0 + 4, y0 + h * 0.55 - 2), fill=GOLD, width=1)
    # lighthouse: white tower with red bands, on waves
    tw = int(16 * scale)
    tx0, tx1 = cx - tw // 2, cx + tw // 2
    ty0, ty1 = y0 + int(16 * scale), y0 + int(58 * scale)
    d.polygon([(tx0 + 2, ty1), (tx0 + 4, ty0), (tx1 - 4, ty0), (tx1 - 2, ty1)],
              fill=(250, 248, 240), outline=INK, width=1)
    for by in (ty0 + 12, ty0 + 26):
        d.polygon([(tx0 + 3, by), (tx1 - 3, by), (tx1 - 3, by + 7),
                   (tx0 + 3, by + 7)], fill=BURG)
    d.rectangle((cx - 8, ty0 - 7, cx + 8, ty0), fill=INK)
    d.ellipse((cx - 4, ty0 - 12, cx + 4, ty0 - 4), fill=GOLD, outline=INK)
    for ang in (-35, -18, 0, 18, 35):
        a = math.radians(90 + ang)
        d.line((cx, ty0 - 8, cx + 26 * math.cos(a), ty0 - 8 - 26 * math.sin(a)),
               fill=(212, 178, 90, 180), width=1)
    # waves
    for k, wy in enumerate((ty1 + 4, ty1 + 11)):
        for xx in range(x0 + 8, x1 - 8, 14):
            d.arc((xx, wy - 5, xx + 14, wy + 5), 180, 360, fill=BLUE, width=2)
    # star above the tower
    sx, sy, sr = cx, y0 + 8, 5
    star = []
    for i in range(10):
        r = sr if i % 2 == 0 else sr * 0.45
        a = math.radians(-90 + i * 36)
        star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
    d.polygon(star, fill=GOLD, outline=INK)
    # motto banner
    by = y1 + 8
    d.polygon([(cx - 44, by), (cx + 44, by), (cx + 38, by + 11),
               (cx - 38, by + 11)], fill=NAVY)
    text_c(d, cx, by + 1, "SEMPER AD MARE", font(SANS_B, 8), (240, 236, 220))


# ---------------------------------------------------------------- portrait
def silhouette_points():
    """Left-facing profile with bun, in a 152x190 box.

    Rounder cranium, distinct nose, narrow neck, gently sloping
    shoulders — a head, not a pawn.
    """
    return [(66, 18), (82, 12), (98, 16), (110, 28), (116, 46),
            (114, 66), (110, 84), (104, 98), (98, 108), (102, 126),
            (110, 148), (124, 188), (38, 188), (46, 160), (58, 138),
            (66, 122), (62, 114), (56, 106), (53, 100), (55, 96),
            (44, 88), (54, 76), (58, 66), (60, 52), (62, 34)]


def portrait(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    # pale blue-grey backdrop with fine vertical guilloche
    d.rectangle(box, fill=(214, 224, 232))
    for xx in range(x0 + 4, x1, 7):
        d.line((xx, y0, xx, y1), fill=(190, 202, 216), width=1)
    pts = [(x0 + 8 + px * (w - 16) / 152, y0 + 6 + py * (h - 12) / 190)
           for px, py in silhouette_points()]
    d.polygon(pts, fill=INK)
    # bun: round knot at the back of the head, merged into the hair
    bx, by = x0 + 8 + 112 * (w - 16) / 152, y0 + 6 + 42 * (h - 12) / 190
    br = 14 * w / 152
    d.ellipse((bx - br, by - br, bx + br, by + br), fill=INK)
    d.rectangle(box, outline=NAVY, width=2)
    d.rectangle((x0 + 4, y0 + 4, x1 - 4, y1 - 4), outline=GOLD, width=1)


# ---------------------------------------------------------------- stamps
def circle_stamp(text_lines, color, rotate=0):
    """Circular entry stamp, drawn on its own layer so it can rotate."""
    S = 136
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = S // 2
    col = color + (205,)
    d.ellipse((6, 6, S - 6, S - 6), outline=col, width=3)
    d.ellipse((16, 16, S - 16, S - 16), outline=col, width=2)
    # small stars left/right
    for sx in (24, S - 24):
        d.text((sx - 4, c - 7), "*", font=font(SANS_B, 13), fill=col)
    y = c - 30
    for i, (s, f, sz) in enumerate(text_lines):
        text_c(d, c, y, s, font(f, sz), col)
        y += sz + 5
    return lay.rotate(rotate, resample=Image.BICUBIC, expand=False)


def rect_stamp(text_lines, color, rotate=0, w=150, h=72):
    lay = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    col = color + (205,)
    d.rectangle((10, 10, 10 + w, 10 + h), outline=col, width=3)
    d.rectangle((14, 14, 10 + w - 4, 10 + h - 4), outline=col, width=1)
    y = 16
    for s, f, sz in text_lines:
        text_c(d, 10 + w // 2, y, s, font(f, sz), col)
        y += sz + 4
    return lay.rotate(rotate, resample=Image.BICUBIC, expand=False)


def signature(d, x0, y, w):
    """A flowing ink signature above the holder's line."""
    pts = []
    for x in range(0, w, 2):
        yy = y - 6 + 5 * math.sin(x * 0.16) + 3 * math.sin(x * 0.053 + 1.2)
        if 40 < x < 70:
            yy -= 6 * math.sin((x - 40) / 30 * math.pi)
        pts.append((x0 + x, yy))
    d.line(pts, fill=(30, 40, 110), width=2)
    d.line((x0, y + 8, x0 + w, y + 8), fill=GREY, width=1)


def island_map(d, x0, y0):
    """Outline of Norhavn with a star at Havnestad, south coast."""
    pts = [(x0 + 18, y0 + 34), (x0 + 30, y0 + 12), (x0 + 52, y0 + 4),
           (x0 + 78, y0 + 10), (x0 + 96, y0 + 26), (x0 + 104, y0 + 44),
           (x0 + 88, y0 + 58), (x0 + 62, y0 + 62), (x0 + 40, y0 + 56),
           (x0 + 22, y0 + 48)]
    d.polygon(pts, fill=(226, 234, 226), outline=NAVY, width=2)
    # compass ticks
    for xx in range(x0, x0 + 112, 14):
        d.line((xx, y0 + 68, xx, y0 + 70), fill=GREY, width=1)
    sx, sy = x0 + 62, y0 + 52
    star = []
    for i in range(10):
        r = 7 if i % 2 == 0 else 3
        a = math.radians(-90 + i * 36)
        star.append((sx + r * math.cos(a), sy + r * math.sin(a)))
    d.polygon(star, fill=BURG, outline=INK)
    text(d, (x0 + 74, y0 + 46), "HAVNESTAD", font(SANS_B, 8), INK)
    text_c(d, x0 + 56, y0 + 76, "NORHAVN  62°04′N  08°12′W",
           font(SANS, 8), GREY)


# ---------------------------------------------------------------- build
def build():
    img = Image.new("RGBA", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # spread frame + gutter
    d.rectangle((16, 16, W - 16, H - 16), outline=NAVY, width=3)
    d.rectangle((22, 22, W - 22, H - 22), outline=GOLD, width=1)
    d.rectangle((506, 22, 518, H - 22), fill=(0, 0, 0, 22))
    d.line((512, 22, 512, H - 22), fill=(90, 90, 90, 90), width=1)

    guilloche(img, 24, 500, 24, 700)
    guilloche(img, 524, 1000, 24, 700)

    # ================= LEFT PAGE — data page =================
    rosette(d, 262, 66, 46)
    coat_of_arms(d, 262, 24, scale=0.72)
    text_c(d, 262, 116, "REPUBLIC OF NORHAVN", font(SERIF_B, 25), INK, spacing=1)
    text_c(d, 262, 144, "PASSPORT  •  VEGABRÉF", font(SERIF_I, 13), NAVY, spacing=2)
    d.line((44, 164, 488, 164), fill=NAVY, width=1)

    portrait(d, (44, 176, 196, 366))

    # data fields
    fx, fw = 212, 488
    y = 178

    def row(label, value, x=None, yv=None, vfont=None, label2=None):
        nonlocal y
        xx = fx if x is None else x
        yy = y if yv is None else yv
        lab = label + ("  /  " + label2 if label2 else "")
        text(d, (xx, yy), lab, font(SANS, 9), GREY)
        text(d, (xx, yy + 11), value, font(vfont or SANS_B, 16), INK)
        return yy + 36

    # top row: type / code / number
    text(d, (fx, y), "TYPE / GERÐ", font(SANS, 9), GREY)
    text(d, (fx, y + 11), "P", font(SANS_B, 16), INK)
    text(d, (fx + 62, y), "CODE / LAND", font(SANS, 9), GREY)
    text(d, (fx + 62, y + 11), "NOR", font(SANS_B, 16), INK)
    text(d, (fx + 140, y), "PASSPORT No. / NUMMER", font(SANS, 9), GREY)
    text(d, (fx + 140, y + 11), "NV 482 916", font(MONO_B, 16), INK)
    y += 38
    y = row("SURNAME", "SOLBERG", label2="ÆTTARNAVN", yv=y)
    y = row("GIVEN NAMES", "ANYA KATRINE", label2="FORNAVN", yv=y)
    y = row("NATIONALITY", "NORHAVNISH", label2="RÍKISFANG", yv=y)
    # date of birth + sex
    text(d, (fx, y), "DATE OF BIRTH  /  FØÐINGARDAGUR", font(SANS, 9), GREY)
    text(d, (fx, y + 11), "02 JUN 1988", font(SANS_B, 16), INK)
    text(d, (fx + 190, y), "SEX / KYN", font(SANS, 9), GREY)
    text(d, (fx + 190, y + 11), "F", font(SANS_B, 16), INK)
    y += 38
    y = row("PLACE OF BIRTH", "HAVNESTAD, NORHAVN", label2="FØÐISTAÐUR", yv=y)
    # issue + expiry
    text(d, (fx, y), "DATE OF ISSUE  /  ÚTGÁFUDAGUR", font(SANS, 9), GREY)
    text(d, (fx, y + 11), "14 MAR 2024", font(SANS_B, 16), INK)
    text(d, (fx + 190, y), "DATE OF EXPIRY", font(SANS, 9), GREY)
    text(d, (fx + 190, y + 11), "13 MAR 2034", font(SANS_B, 16), INK)
    y += 38
    y = row("AUTHORITY", "HAVNESTAD PASSPORT OFFICE", label2="ÚTGÁFUSTOFA", yv=y)
    y = row("PERSONAL No.", "020688-4317", label2="KENNITALA", yv=y)
    # signature
    text(d, (fx, y), "HOLDER'S SIGNATURE  /  UNDIRSKRIFT", font(SANS, 9), GREY)
    signature(d, fx, y + 26, 180)

    # observations box under the portrait
    d.rectangle((44, 382, 196, 470), outline=NAVY, width=1)
    text(d, (52, 388), "OBSERVATIONS", font(SANS_B, 9), NAVY)
    obs = "Holder is a seafarer.\nSee Seaman's Book\nNo. SB-77120.\nIssued Havnestad."
    yy = 402
    for line in obs.split("\n"):
        text(d, (52, yy), line, font(SANS, 10), INK)
        yy += 14
    # seafarer stamp under the observations
    st = rect_stamp([("SEAFARER", SANS_B, 13), ("FISHING VESSEL CREW", SANS_B, 9)],
                    RUST, rotate=-6, w=140, h=52)
    img.alpha_composite(st, (48, 486))

    # MRZ strip
    d.rectangle((36, 596, 488, 672), fill=(255, 255, 255), outline=NAVY, width=1)
    l1, l2 = mrz_lines()
    text(d, (46, 606), l1, font(MONO, 15), INK)
    text(d, (46, 632), l2, font(MONO, 15), INK)
    text_c(d, 262, 682, "THIS PASSPORT CONTAINS 32 PAGES  •  ÞETTA VEGABRÉF HEFUR 32 SÍÐUR",
           font(SANS, 8), GREY)

    # ================= RIGHT PAGE — visas & stamps =================
    text_c(d, 762, 34, "VISAS", font(SERIF_B, 22), INK, spacing=3)
    text_c(d, 762, 60, "VEGABRÉF  —  PAGE 12", font(SANS, 9), GREY, spacing=2)
    d.line((540, 76, 984, 76), fill=NAVY, width=1)

    # visa sticker — Kingdom of Norway
    vx0, vy0, vx1, vy1 = 540, 88, 984, 222
    d.rectangle((vx0, vy0, vx1, vy1), fill=(216, 231, 222), outline=NAVY, width=2)
    d.rectangle((vx0 + 4, vy0 + 4, vx1 - 4, vy1 - 4), outline=NAVY, width=1)
    d.rectangle((vx0 + 4, vy0 + 4, vx1 - 4, vy0 + 30), fill=NAVY)
    text_c(d, 762, vy0 + 8, "KINGDOM OF NORWAY  •  VISITOR VISA", font(SANS_B, 13),
           (240, 236, 220))
    text(d, (vx0 + 14, vy0 + 40), "TYPE  C  —  MULTIPLE ENTRY", font(SANS_B, 12), INK)
    text(d, (vx0 + 14, vy0 + 58), "VALID  01 MAR 2025  –  28 FEB 2026", font(SANS, 12), INK)
    text(d, (vx0 + 14, vy0 + 76), "DURATION OF STAY  90 DAYS", font(SANS, 12), INK)
    text(d, (vx0 + 14, vy0 + 94), "ISSUED  20 FEB 2025  •  HAVNESTAD", font(SANS, 12), INK)
    text(d, (vx0 + 300, vy0 + 40), "No. N-884120", font(MONO_B, 12), INK)
    text(d, (vx0 + 14, vy0 + 112),
         "CONDITION: SEAFARER — FISHING VESSEL CREW — HARBOUR DISTRICTS ONLY",
         font(SANS_B, 9), BURG)
    # visa seal
    d.ellipse((vx1 - 52, vy1 - 52, vx1 - 12, vy1 - 12), outline=GOLD, width=2)
    d.ellipse((vx1 - 46, vy1 - 46, vx1 - 18, vy1 - 18), outline=GOLD, width=1)
    text_c(d, vx1 - 32, vy1 - 42, "N", font(SERIF_B, 16), NAVY)

    # stamps: two trips, chronological, entry = circle, exit = rectangle
    stamps = [
        ("rect", "EXIT", "HAVNESTAD", "02 APR 2025", NAVY, -6),
        ("circ", "ENTRY", "KEFLAVÍK", "02 APR 2025", BLUE, 8),
        ("rect", "EXIT", "KEFLAVÍK", "09 APR 2025", NAVY, 5),
        ("circ", "ENTRY", "HAVNESTAD", "09 APR 2025", GREEN, -9),
        ("rect", "EXIT", "HAVNESTAD", "18 SEP 2025", NAVY, 7),
        ("circ", "ENTRY", "BERGEN", "18 SEP 2025", PURPLE, -6),
        ("rect", "EXIT", "BERGEN", "25 SEP 2025", NAVY, -5),
        ("circ", "ENTRY", "HAVNESTAD", "25 SEP 2025", GREEN, 9),
    ]
    centres = [(652, 272), (882, 272), (652, 368), (882, 368),
               (652, 464), (882, 464), (652, 560), (882, 560)]
    for (kind, word, place, date, color, rot), (cx, cy) in zip(stamps, centres):
        if kind == "circ":
            lay = circle_stamp([(word, SANS_B, 14), (place, SANS_B, 12),
                                (date, SANS, 11)], color, rotate=rot)
            img.alpha_composite(lay, (cx - 68, cy - 68))
        else:
            lay = rect_stamp([(word, SANS_B, 14), (place, SANS_B, 11),
                              (date, SANS, 11)], color, rotate=rot)
            img.alpha_composite(lay, (cx - 85, cy - 46))

    # harbour-tax fee stamp, bottom right
    fee = rect_stamp([("HARBOUR TAX PAID", SANS_B, 13), ("40 KR  •  18 SEP 2025", SANS_B, 10),
                      ("HAVNESTAD PORT AUTHORITY", SANS, 9)], RUST, rotate=-7,
                     w=170, h=60)
    img.alpha_composite(fee, (800, 622))

    # island map, bottom left of the visa page
    island_map(d, 548, 616)

    img.convert("RGB").save(OUT, optimize=True)
    size = os.path.getsize(OUT)
    print(f"wrote {OUT} {size} bytes, {W}x{H}")
    assert size <= 1_048_576, "over the 1 MiB cap"
    return OUT


if __name__ == "__main__":
    build()

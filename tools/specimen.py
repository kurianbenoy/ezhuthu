#!/usr/bin/env python3
"""Generate Kallar specimen / proof images.

Outputs (proofs/):
  kallar_hero.png       — dark Sarvam-inspired hero poster
  kallar_axis.png       — the APER axis, 0 → 100
  kallar_gradient.png   — spectrum text block
  kallar_spectrum.png   — gradient wordmark
  kallar_glyphs.png     — monochrome character sheet
"""
import math
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import render_alpha  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
PROOFS = os.path.join(ROOT, "proofs")
TMP = os.path.join(tempfile.gettempdir(), "ezhuthu_specimen")
os.makedirs(TMP, exist_ok=True)
os.makedirs(PROOFS, exist_ok=True)

REG = os.path.join(FONTS, "Kallar-Regular.ttf")
BOLD = os.path.join(FONTS, "Kallar-Bold.ttf")
SPECTRUM = os.path.join(FONTS, "Kallar-Spectrum.ttf")

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Sarvam-adjacent spectrum: indigo → blue → periwinkle → violet → pink → orange → gold
STOPS = [
    (0.00, (24, 30, 92)),
    (0.18, (43, 63, 176)),
    (0.38, (92, 100, 219)),
    (0.56, (160, 108, 210)),
    (0.72, (217, 115, 160)),
    (0.86, (238, 121, 68)),
    (1.00, (249, 195, 109)),
]


def rgb(c):
    return tuple(int(v) for v in c)


def gradient_array(w, h, stops=STOPS, y0=None, y1=None):
    if y0 is None:
        y0 = 0
    if y1 is None:
        y1 = h
    arr = np.zeros((h, w, 3), dtype=np.float32)
    for y in range(h):
        t = (y - y0) / max(1, (y1 - y0))
        t = min(1.0, max(0.0, t))
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                u = (t - p0) / max(1e-9, p1 - p0)
                arr[y, :, 0] = c0[0] + (c1[0] - c0[0]) * u
                arr[y, :, 1] = c0[1] + (c1[1] - c0[1]) * u
                arr[y, :, 2] = c0[2] + (c1[2] - c0[2]) * u
                break
    return arr


def gradient_image(w, h, stops=STOPS, y0=None, y1=None):
    arr = gradient_array(w, h, stops, y0, y1)
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def glow_background(w, h):
    # deep vertical gradient
    base = gradient_array(w, h, [
        (0.0, (5, 7, 16)),
        (0.35, (12, 14, 38)),
        (0.68, (28, 15, 48)),
        (1.0, (48, 17, 28)),
    ])
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    for cx, cy, rx, ry, color, strength in [
        (0.50 * w, 0.82 * h, 0.62 * w, 0.40 * h, (238, 121, 68), 0.30),
        (0.24 * w, 0.18 * h, 0.45 * w, 0.40 * h, (60, 84, 220), 0.22),
        (0.82 * w, 0.30 * h, 0.35 * w, 0.35 * h, (120, 72, 190), 0.16),
    ]:
        d = np.sqrt(((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2)
        m = np.exp(-d * d * 2.6)[..., None]
        base += np.array(color, dtype=np.float32) * m * strength
    # subtle grain
    rng = np.random.default_rng(7)
    base += rng.normal(0, 2.0, base.shape)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")


def ink_alpha(font_path, text, size, pad=40):
    alpha, baseline = render_alpha(font_path, text, size=size, pad=pad)
    return alpha, baseline


def bbox_alpha(alpha):
    return alpha.getbbox()


def gradient_text(font_path, text, size, stops=STOPS, pad=40, glow=0):
    alpha, baseline = ink_alpha(font_path, text, size, pad)
    if alpha is None:
        return None, 0, 0
    bbox = alpha.getbbox()
    if bbox is None:
        return None, 0, 0
    grad = gradient_image(alpha.width, alpha.height, stops, bbox[1], bbox[3])
    layer = grad.convert("RGBA")
    layer.putalpha(alpha)
    if glow:
        gl = alpha.filter(ImageFilter.GaussianBlur(glow))
        gl_img = gradient_image(alpha.width, alpha.height, stops, bbox[1], bbox[3])
        gl_layer = gl_img.convert("RGBA")
        a = np.array(gl, dtype=np.float32) * 0.55
        gl_layer.putalpha(Image.fromarray(a.astype(np.uint8)))
        out = Image.new("RGBA", (alpha.width, alpha.height), (0, 0, 0, 0))
        out.alpha_composite(gl_layer)
        out.alpha_composite(layer)
        return out, baseline, alpha.getbbox()
    return layer, baseline, alpha.getbbox()


def paste_center(canvas, layer, cx, baseline=None, top=None):
    x = int(cx - layer.width / 2)
    y = int((baseline - 0) - layer.height) if top is None else int(top)
    canvas.alpha_composite(layer, (x, y))
    return x, y


def paste_at_baseline(canvas, layer, x, baseline, baseline_in_layer):
    y = int(baseline - baseline_in_layer)
    canvas.alpha_composite(layer, (int(x), y))
    return int(x), y


def draw_label(draw, text, xy, size=20, color=(220, 225, 255), bold=False,
               tracking=0):
    font = ImageFont.truetype(DEJAVU_BOLD if bold else DEJAVU, size)
    x, y = xy
    if tracking:
        for ch in text:
            draw.text((x, y), ch, font=font, fill=color)
            x += draw.textlength(ch, font=font) + tracking
    else:
        draw.text((x, y), text, font=font, fill=color)
    return draw


def draw_rule(draw, x0, y0, x1, y1, color=(255, 255, 255, 30), width=1):
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)


def instantiate_aper(src, aper):
    out = os.path.join(TMP, f"aper{int(aper)}.ttf")
    f = TTFont(src)
    instantiateVariableFont(f, {"APER": aper}, inplace=True)
    f.save(out)
    return out


def solid_text(font_path, text, size, color=(20, 20, 30, 255), pad=20):
    alpha, baseline = render_alpha(font_path, text, size=size, pad=pad)
    if alpha is None:
        return None, 0
    layer = Image.new("RGBA", (alpha.width, alpha.height), color[:3] + (255,))
    layer.putalpha(alpha)
    return layer, baseline


def paste_text(canvas, font_path, text, size, x, baseline, color=(20, 20, 30),
               pad=20):
    layer, b = solid_text(font_path, text, size, color + (255,) if len(color) == 3 else color, pad)
    if layer is None:
        return
    canvas.alpha_composite(layer, (int(x), int(baseline - b)))


def paste_text_right(canvas, font_path, text, size, right, baseline, color=(20, 20, 30)):
    layer, b = solid_text(font_path, text, size, color + (255,) if len(color) == 3 else color)
    if layer is None:
        return
    canvas.alpha_composite(layer, (int(right - layer.width), int(baseline - b)))


def _cubic(p0, p1, p2, p3, t):
    mt = 1 - t
    return (
        mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
        mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1],
    )


def teardrop_pts(cx, cy, rx, ry, cusp=20, n=40):
    """Smooth petal outline in PIL coordinates (y grows down): round base,
    pointed crown at the top."""
    p0 = (cx, cy + ry)                 # round base (lower on screen)
    p1 = (cx + rx, cy)                 # right
    tip = (cx, cy - ry - cusp)         # pointed crown (higher on screen)
    p3 = (cx - rx, cy)                 # left
    pts = []
    for i in range(n):
        t = i / n
        pts.append(_cubic(p0, (cx + rx * 0.62, cy + ry), (cx + rx, cy + ry * 0.62), p1, t))
    for i in range(n):
        t = i / n
        pts.append(_cubic(p1, (cx + rx, cy - ry * 0.42), (cx + rx * 0.55, tip[1] + ry * 0.12), tip, t))
    for i in range(n):
        t = i / n
        pts.append(_cubic(tip, (cx - rx * 0.55, tip[1] + ry * 0.12), (cx - rx, cy - ry * 0.42), p3, t))
    for i in range(n):
        t = i / n
        pts.append(_cubic(p3, (cx - rx, cy + ry * 0.62), (cx - rx * 0.62, cy + ry), p0, t))
    return pts


def petal_outline(cx, cy, rx, ry, cusp=0.18, n=120):
    """Petal/leaf polyline for decorative background arches."""
    pts = []
    tip = (cx, cy + ry + cusp * ry)
    left = (cx - rx, cy)
    right = (cx + rx, cy)
    # right side: bottom -> right -> tip
    for i in range(n // 2):
        t = i / (n // 2)
        # quadratic-ish bezier from bottom to right
        x = cx + rx * math.sin(t * math.pi / 2)
        y = cy - ry * math.cos(t * math.pi / 2)
        pts.append((x, y))
    for i in range(n // 2):
        t = i / (n // 2)
        x = cx + rx * math.cos(t * math.pi / 2) ** 0.8
        y = cy + ry * math.sin(t * math.pi / 2)
        pts.append((x, y))
    pts.append(tip)
    for i in range(n // 2):
        t = i / (n // 2)
        x = cx - rx * math.cos(t * math.pi / 2) ** 0.8
        y = cy + ry * math.cos(t * math.pi / 2)
        pts.append((x, y))
    for i in range(n // 2):
        t = i / (n // 2)
        x = cx - rx * math.cos(t * math.pi / 2)
        y = cy - ry * math.sin(t * math.pi / 2)
        pts.append((x, y))
    return pts


def add_petal_motif(canvas, cx, cy, rx, ry, color=(255, 255, 255), alpha=18, width=2):
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    pts = petal_outline(cx, cy, rx, ry)
    d.line(pts + [pts[0]], fill=(*color, alpha), width=width, joint="curve")
    # interior concentric petals
    for k in (0.74, 0.48, 0.24):
        p2 = petal_outline(cx, cy, rx * k, ry * k)
        d.line(p2 + [p2[0]], fill=(*color, int(alpha * 0.7)), width=width)
    canvas.alpha_composite(overlay)


def add_mandala(canvas, cx, cy, R, petals=24, alpha=14, width=1):
    """A delicate Sarvam-style petal mandala, drawn as hairlines."""
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(petals):
        a = 2 * math.pi * i / petals
        px = cx + R * math.sin(a)
        py = cy - R * math.cos(a)
        base = petal_outline(0, 0, 18, 74)
        rot = []
        ca, sa = math.cos(a), math.sin(a)
        for x, y in base:
            rot.append((px + x * ca - y * sa, py + x * sa + y * ca))
        d.line(rot + [rot[0]], fill=(255, 255, 255, alpha), width=width, joint="curve")
    for rr, aa in ((R + 74, alpha), (R * 0.72, int(alpha * 0.8)), (R * 0.42, int(alpha * 0.6))):
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255, aa), width=width)
    canvas.alpha_composite(overlay)


# ---------------------------------------------------------------------------
# hero
# ---------------------------------------------------------------------------
def make_hero():
    W, H = 1600, 1000
    bg = glow_background(W, H).convert("RGBA")
    add_mandala(bg, W * 0.5, H * 0.46, 350, petals=24, alpha=16, width=1)
    d = ImageDraw.Draw(bg)
    draw_label(d, "KALLAR", (72, 62), 19, (190, 205, 255), bold=True, tracking=3)
    draw_label(d, "APERTURE-VARIABLE MALAYALAM", (72, 92), 14, (130, 145, 190), tracking=2)
    draw_label(d, "APER 0 → 100", (W - 236, 62), 15, (255, 210, 170), bold=True)
    draw_rule(d, 72, 130, W - 72, 130, (255, 255, 255, 26))

    word = "കല്ലാർ"
    layer, baseline, bbox = gradient_text(BOLD, word, 360, glow=18)
    if layer:
        x, y = paste_center(bg, layer, W / 2, top=190)
    # tagline
    tag, tb, _ = gradient_text(BOLD, "ഭാഷയിൽ വിരിയുന്ന ലിപി", 88,
                               stops=[(0, (230, 236, 255)), (1, (255, 186, 120))])
    if tag:
        paste_center(bg, tag, W / 2, top=640)
    d = ImageDraw.Draw(bg)
    draw_label(d, "A Malayalam typeface that blooms — from round loops to lotus gateways.",
               (W / 2 - 380, 770), 24, (205, 212, 235))
    draw_label(d, "Kallar  ·  variable Aperture axis  ·  COLRv1 spectrum",
               (W / 2 - 330, 806), 18, (150, 162, 200))
    # bottom cards
    cols = [
        ("01", "APERTURE", "One axis, round to petal."),
        ("02", "SPECTRUM", "Blue-to-orange COLRv1."),
        ("03", "MALAYALAM", "Full Unicode block + Latin."),
    ]
    x0 = 72
    for i, (num, title, body) in enumerate(cols):
        x = x0 + i * 500
        draw_rule(d, x, 880, x + 420, 880, (255, 255, 255, 34))
        draw_label(d, num, (x, 898), 14, (238, 121, 68), bold=True)
        draw_label(d, title, (x + 40, 896), 17, (240, 243, 255), bold=True, tracking=1)
        draw_label(d, body, (x + 40, 922), 16, (160, 172, 205))
    draw_label(d, "Kallar  /  v1.100  /  OFL 1.1", (72, 962), 13,
               (120, 132, 168))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_hero.png"))
    print("hero")


# ---------------------------------------------------------------------------
# axis strip
# ---------------------------------------------------------------------------
def make_axis():
    W, H = 1600, 760
    bg = glow_background(W, H).convert("RGBA")
    add_mandala(bg, W * 0.5, H * 0.48, 280, petals=20, alpha=9, width=1)
    d = ImageDraw.Draw(bg)
    draw_label(d, "THE APERTURE AXIS", (72, 58), 18, (190, 205, 255),
               bold=True, tracking=3)
    draw_label(d, "APER 0 → 100  ·  one axis, from the classic loop to the lotus gateway",
               (72, 90), 16, (135, 150, 190))
    draw_rule(d, 72, 132, W - 72, 132, (255, 255, 255, 26))

    rows = [(0, "ROUND"), (25, "QUARTER"), (50, "BLOOM"),
            (75, "THREE-QUARTERS"), (100, "PETAL")]
    colw = (W - 160) / len(rows)
    for i, (aper, name) in enumerate(rows):
        fpath = instantiate_aper(BOLD, aper)
        cx = 80 + colw * (i + 0.5)
        alpha, baseline = render_alpha(fpath, "ക", size=200, pad=10)
        if alpha is not None:
            layer = Image.new("RGBA", (alpha.width, alpha.height), (255, 238, 224, 255))
            layer.putalpha(alpha)
            bg.alpha_composite(layer, (int(cx - alpha.width / 2), 190))
        draw_label(d, f"{aper:03d}", (int(cx - 20), 168), 26, (238, 121, 68), bold=True)
        draw_label(d, name, (int(cx - 50), 500), 13, (185, 195, 225), tracking=2)
        word, wb = render_alpha(fpath, "മലയാളം", size=42, pad=6)
        if word is not None:
            wl = Image.new("RGBA", (word.width, word.height), (220, 226, 245, 255))
            wl.putalpha(word)
            bg.alpha_composite(wl, (int(cx - word.width / 2), 540))
        draw_rule(d, int(cx - colw * 0.36), 620, int(cx + colw * 0.36), 620,
                  (255, 255, 255, 24))
    draw_label(d, "classic loop", (80, 650), 13, (150, 162, 200))
    draw_label(d, "lotus gateway", (W - 230, 650), 13, (238, 180, 120))
    draw_label(d, "Malayalam · Kallar Bold · variable APER", (80, 704), 12,
               (120, 132, 168))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_axis.png"))
    print("axis")


# ---------------------------------------------------------------------------
# gradient block
# ---------------------------------------------------------------------------
def make_gradient():
    W, H = 1600, 980
    bg = glow_background(W, H).convert("RGBA")
    add_petal_motif(bg, W * 0.78, H * 0.38, W * 0.24, H * 0.30, alpha=12, width=1)
    d = ImageDraw.Draw(bg)
    draw_label(d, "SPECTRUM / COLRv1", (72, 58), 17, (190, 205, 255),
               bold=True, tracking=3)
    draw_label(d, "The same letterforms, filled with a blue → orange flow.",
               (72, 88), 16, (135, 150, 190))
    draw_rule(d, 72, 126, W - 72, 126, (255, 255, 255, 26))

    lines = [
        ("ഭാഷയുടെ സാധ്യതകൾ", 126, 150),
        ("എല്ലാവർക്കും വേണ്ടിയുള്ള എഐ", 78, 350),
        ("മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്.", 54, 500),
        ("അതിന്റെ ലിപിക്ക് ഇന്ന് ഒരു പുതിയ ഭാവം.", 54, 590),
    ]
    for text, size, top in lines:
        layer, baseline, bbox = gradient_text(BOLD if size >= 100 else REG, text, size, glow=10 if size >= 100 else 0)
        if layer:
            bg.alpha_composite(layer, (72, top))
    d = ImageDraw.Draw(bg)
    draw_rule(d, 72, 760, W - 72, 760, (255, 255, 255, 30))
    draw_label(d, "Blue at the crown, orange at the baseline — a continuous field across the text block.",
               (72, 784), 19, (190, 200, 230))
    draw_label(d, "Kallar Spectrum  ·  COLRv1 / CPAL  ·  falls back to monochrome",
               (72, 818), 16, (130, 145, 185))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_gradient.png"))
    print("gradient")


# ---------------------------------------------------------------------------
# spectrum wordmark
# ---------------------------------------------------------------------------
def make_spectrum():
    W, H = 1600, 620
    bg = Image.new("RGBA", (W, H), (6, 8, 16, 255))
    add_petal_motif(bg, W / 2, H / 2 + 20, W * 0.34, H * 0.40, alpha=12, width=1)
    layer, baseline, bbox = gradient_text(BOLD, "കല്ലാർ", 300, glow=16)
    if layer:
        paste_center(bg, layer, W / 2, top=30)
    d = ImageDraw.Draw(bg)
    draw_label(d, "kallār", (72, 520), 18, (140, 155, 195), tracking=1)
    draw_label(d, "KALLAR / SPECTRUM", (W - 330, 520), 14,
               (238, 150, 100), bold=True, tracking=2)
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_spectrum.png"))
    print("spectrum")


# ---------------------------------------------------------------------------
# glyph sheet
# ---------------------------------------------------------------------------
def make_glyphs():
    W, H = 1600, 1500
    bg = Image.new("RGB", (W, H), (250, 249, 246))
    d = ImageDraw.Draw(bg)
    fpath = instantiate_aper(REG, 100)
    d.text((72, 50), "KALLAR", font=ImageFont.truetype(DEJAVU_BOLD, 22),
           fill=(20, 20, 30))
    d.text((72, 82), "Malayalam consonants · independent vowels · signs · digits",
           font=ImageFont.truetype(DEJAVU, 16), fill=(90, 90, 100))
    d.line([(72, 120), (W - 72, 120)], fill=(200, 200, 205), width=1)

    groups = [
        ("CONSONANTS", list("കഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരറലവശഷസഹളഴ")),
        ("VOWELS", list("അആഇഈഉഊഋൠഌൡഎഏഐഒഓഔ")),
        ("SIGNS & CHILLUS", ["ാ", "ി", "ീ", "ു", "ൂ", "ൃ", "െ", "േ", "ൈ", "ൊ", "ോ", "ൌ", "ം", "ഃ", "്", "ൺ", "ൻ", "ർ", "ൽ", "ൾ"]),
        ("DIGITS", list("൦൧൨൩൪൫൬൭൮൯")),
    ]
    y = 150
    for title, chars in groups:
        d.text((72, y), title, font=ImageFont.truetype(DEJAVU_BOLD, 13), fill=(150, 100, 60))
        y += 26
        cols = 12
        cellw = (W - 144) / cols
        for i, ch in enumerate(chars):
            alpha, baseline = render_alpha(fpath, ch, size=92, pad=6)
            if alpha is not None:
                x = int(72 + (i % cols) * cellw + (cellw - alpha.width) / 2)
                yy = int(y + (i // cols) * 108 + (108 - alpha.height) / 2)
                bg.paste((20, 20, 30), (x, yy), alpha)
            d.text((72 + int((i % cols) * cellw) + 4, y + (i // cols) * 108 + 92),
                   f"{ord(ch):04X}", font=ImageFont.truetype(DEJAVU, 10), fill=(150, 150, 160))
        y += ((len(chars) + cols - 1) // cols) * 108 + 30
    d.line([(72, H - 80), (W - 72, H - 80)], fill=(200, 200, 205), width=1)
    d.text((72, H - 62), "Aperture 100 / Petal · Kallar Regular",
           font=ImageFont.truetype(DEJAVU, 13), fill=(100, 100, 110))
    bg.save(os.path.join(PROOFS, "kallar_glyphs.png"))
    print("glyphs")


def rounded_gradient(w, h, radius, stops=STOPS, alpha=255):
    img = gradient_image(w, h, stops).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle((0, 0, w, h), radius=radius, fill=alpha)
    img.putalpha(mask)
    return img


def make_poster():
    W, H = 1600, 2000
    bg = glow_background(W, H).convert("RGBA")
    add_mandala(bg, W / 2, 760, 470, petals=24, alpha=15, width=2)
    d = ImageDraw.Draw(bg)
    draw_label(d, "KALLAR", (90, 80), 20, (190, 205, 255), bold=True, tracking=4)
    draw_label(d, "A MALAYALAM TYPEFACE THAT BLOOMS", (90, 114), 14, (135, 150, 190), tracking=3)
    draw_label(d, "APER 0 → 100", (W - 300, 80), 16, (255, 210, 170), bold=True)
    draw_rule(d, 90, 160, W - 90, 160, (255, 255, 255, 26))

    layer, baseline, bbox = gradient_text(BOLD, "സർവം", 420, glow=20)
    if layer:
        paste_center(bg, layer, W / 2, top=300)

    tag, tb = solid_text(BOLD, "ഭാഷയിൽ എല്ലാം", 108, (244, 235, 220, 255))
    if tag:
        paste_center(bg, tag, W / 2, top=1040)

    paste_text(bg, REG, "എല്ലാ ഭാഷകളും എല്ലാ മനുഷ്യർക്കും.", 38, 90, 1250, (190, 198, 220))
    paste_text(bg, REG, "ഒരു ലിപി. ഒരു വാതിൽ. ഒരു ലോകം.", 38, 90, 1310, (190, 198, 220))
    draw_rule(d, 90, 1400, W - 90, 1400, (255, 255, 255, 24))

    # APER strip
    y = 1460
    for i, (v, name) in enumerate([(0, "ROUND"), (25, "QUARTER"), (50, "BLOOM"),
                                   (75, "THREE-QUARTERS"), (100, "PETAL")]):
        fpath = instantiate_aper(BOLD, v)
        alpha, b = render_alpha(fpath, "ക", size=150, pad=6)
        x = 90 + i * 290
        if alpha is not None:
            lay = Image.new("RGBA", (alpha.width, alpha.height), (255, 238, 224, 255))
            lay.putalpha(alpha)
            bg.alpha_composite(lay, (x, y))
        draw_label(d, f"{v:03d}", (x + 10, y + 190), 18, (238, 121, 68), bold=True)
        draw_label(d, name, (x + 10, y + 218), 11, (160, 172, 205), tracking=2)
    draw_label(d, "Kallar  /  v1.100  /  OFL 1.1  /  Malayalam + Latin",
               (90, H - 80), 14, (140, 152, 185))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_poster.png"))
    print("poster")


def make_editorial():
    W, H = 1600, 1100
    bg = Image.new("RGBA", (W, H), (245, 240, 230, 255))
    d = ImageDraw.Draw(bg)
    # paper grain
    rng = np.random.default_rng(11)
    grain = rng.normal(0, 2.2, (H, W, 1))
    bg = Image.fromarray(np.clip(np.array(bg)[:, :, :3] + grain, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(bg)
    draw_label(d, "KALLAR  /  EDITORIAL", (80, 62), 13, (150, 110, 70), bold=True, tracking=2)
    draw_rule(d, 80, 96, W - 80, 96, (30, 30, 30, 40))
    draw_rule(d, W // 2, 130, W // 2, H - 80, (30, 30, 30, 28), width=1)

    # left page
    drop, db, _ = gradient_text(BOLD, "മ", 300, stops=[(0, (20, 24, 40)), (1, (80, 40, 30))], glow=0)
    if drop:
        bg.alpha_composite(drop, (80, 150))
    paste_text(bg, BOLD, "വായനയുടെ", 82, 80, 560, (22, 22, 30))
    paste_text(bg, BOLD, "പുതിയ വഴി", 82, 80, 650, (22, 22, 30))
    lines = [
        "മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്.",
        "കേരളത്തിലെ ഔദ്യോഗിക ഭാഷയും",
        "ഇതാണ്. കല്ലാർ ഈ",
        "ലിപിക്ക് ഒരു പുതിയ ഭാവം",
        "നൽകുന്നു — വൃത്താകൃതിയിൽ",
        "നിന്ന് താമരയുടെ ദളങ്ങളിലേക്ക്.",
    ]
    y = 730
    for line in lines:
        paste_text(bg, REG, line, 26, 84, y, (50, 46, 42))
        y += 42
    draw_label(d, "01", (80, H - 120), 14, (150, 110, 70), bold=True)
    draw_label(d, "Kallar / Aperture 100", (80, H - 92), 12, (120, 110, 100))

    # right page
    draw_label(d, "PULL QUOTE", (W // 2 + 80, 160), 12, (150, 110, 70), bold=True, tracking=2)
    quote, qb, _ = gradient_text(BOLD, "ഭാഷയിൽ", 96, stops=[(0, (20, 24, 40)), (1, (110, 50, 35))])
    quote2, qb2, _ = gradient_text(BOLD, "വിരിയുന്ന ലിപി", 96, stops=[(0, (110, 50, 35)), (1, (20, 24, 40))])
    if quote:
        bg.alpha_composite(quote, (W // 2 + 80, 220))
    if quote2:
        bg.alpha_composite(quote2, (W // 2 + 80, 360))
    paste_text(bg, REG, "ഒരു അക്ഷരം ഒരു വാതിൽ തുറക്കുന്നു.", 30,
               W // 2 + 80, 600, (60, 55, 50))
    paste_text(bg, REG, "ഓരോ ദളവും ഒരു പുതിയ ഭാഷ.", 30,
               W // 2 + 80, 650, (60, 55, 50))
    # lotus mark
    add_mandala(bg, W // 2 + 300, 860, 120, petals=16, alpha=45, width=2)
    draw_label(d, "02", (W - 120, H - 120), 14, (150, 110, 70), bold=True)
    draw_label(d, "Kallar / Spectrum", (W - 360, H - 92), 12, (120, 110, 100))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_editorial.png"))
    print("editorial")


def make_social():
    W = H = 1080
    grad = gradient_image(W, H, STOPS).convert("RGBA")
    # darken edges
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((X - W / 2) / (W * 0.7)) ** 2 + ((Y - H / 2) / (H * 0.7)) ** 2)
    vig = np.clip(1 - d * 0.8, 0, 1)[..., None]
    arr = np.array(grad)[:, :, :3] * vig
    bg = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    add_mandala(bg, W / 2, H / 2, 330, petals=24, alpha=20, width=1)
    layer, baseline, bbox = gradient_text(BOLD, "കല്ലാർ", 260,
                                          stops=[(0, (255, 244, 228)), (1, (255, 205, 160))],
                                          glow=14)
    if layer:
        paste_center(bg, layer, W / 2, top=260)
    d = ImageDraw.Draw(bg)
    draw_label(d, "KALLAR", (60, 56), 15, (255, 255, 255), bold=True, tracking=3)
    draw_label(d, "APERTURE-VARIABLE MALAYALAM", (60, 84), 11, (255, 235, 220), tracking=2)
    draw_label(d, "APER 100", (W - 190, 56), 14, (255, 255, 255), bold=True)
    paste_text(bg, BOLD, "ഭാഷയിൽ വിരിയുന്ന ലിപി", 34, 60, H - 120, (255, 248, 238))
    draw_label(d, "A typeface that blooms.", (60, H - 92), 20, (255, 240, 225))
    draw_rule(d, 60, H - 58, W - 60, H - 58, (255, 255, 255, 90))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_social.png"))
    print("social")


def make_ui():
    W, H = 1600, 1000
    bg = Image.new("RGBA", (W, H), (9, 11, 20, 255))
    d = ImageDraw.Draw(bg)
    # sidebar
    d.rectangle((0, 0, 300, H), fill=(13, 16, 28, 255))
    draw_rule(d, 300, 0, 300, H, (255, 255, 255, 20))
    paste_text(bg, BOLD, "കല്ലാർ", 38, 34, 78, (245, 236, 222))
    draw_label(d, "KALLAR", (36, 92), 11, (238, 121, 68), bold=True, tracking=3)
    menu = [("ചാറ്റ്", True), ("ഭാഷ", False), ("ഡോക്യുമെന്റ്", False), ("സെറ്റിംഗ്സ്", False)]
    y = 180
    for item, active in menu:
        if active:
            d.rounded_rectangle((20, y - 28, 280, y + 18), radius=12, fill=(64, 34, 25, 255))
        paste_text(bg, REG, item, 22, 46, y, (238, 236, 230) if active else (150, 158, 185))
        y += 62
    draw_label(d, "APER", (36, H - 110), 11, (140, 150, 180), bold=True, tracking=2)
    draw_label(d, "100", (36, H - 86), 26, (238, 121, 68), bold=True)
    d.rounded_rectangle((96, H - 100, 264, H - 94), radius=3, fill=(255, 255, 255, 24))
    d.rounded_rectangle((96, H - 100, 264, H - 94), radius=3, fill=(238, 121, 68, 255))

    # top bar
    paste_text(bg, REG, "സ്വാഗതം", 20, 340, 68, (150, 160, 190))
    d.rounded_rectangle((W - 250, 38, W - 40, 82), radius=22, fill=(24, 26, 42, 255),
                        outline=(60, 64, 90, 255), width=1)
    draw_label(d, "APER 100", (W - 215, 52), 12, (255, 210, 170), bold=True, tracking=2)
    draw_rule(d, 340, 110, W - 40, 110, (255, 255, 255, 20))

    # main heading
    paste_text(bg, BOLD, "നിങ്ങളുടെ ഭാഷയിൽ,", 62, 340, 240, (246, 240, 230))
    paste_text(bg, BOLD, "നിങ്ങളുടെ എഐ", 62, 340, 320, (246, 240, 230))
    paste_text(bg, REG, "മലയാളത്തിൽ ചിന്തിക്കുന്ന, മലയാളത്തിൽ", 24,
               340, 410, (165, 175, 200))
    paste_text(bg, REG, "സംസാരിക്കുന്ന, മലയാളത്തിന് വേണ്ടി", 24,
               340, 446, (165, 175, 200))
    paste_text(bg, REG, "പണിയുന്ന എഐ.", 24, 340, 482, (165, 175, 200))

    # gradient button
    btn = rounded_gradient(300, 64, 18)
    bg.alpha_composite(btn, (340, 540))
    paste_text(bg, BOLD, "ആരംഭിക്കാം", 26, 380, 585, (255, 250, 242))
    d.rounded_rectangle((670, 540, 830, 604), radius=18, outline=(255, 255, 255, 30), width=1)
    paste_text(bg, REG, "കൂടുതൽ", 24, 708, 585, (220, 225, 245))

    # right card
    d.rounded_rectangle((980, 180, W - 40, 820), radius=28, fill=(18, 20, 34, 255),
                        outline=(50, 54, 78, 255), width=1)
    layer, baseline, bbox = gradient_text(BOLD, "കമലം", 150, glow=12)
    if layer:
        paste_center(bg, layer, 1290, top=240)
    draw_label(d, "APERTURE 100 / PETAL", (1290 - 105, 470), 12, (238, 150, 100), bold=True, tracking=2)
    paste_text(bg, REG, "ഓരോ അക്ഷരവും ഒരു വാതിൽ.", 26, 1030, 560, (220, 226, 242))
    paste_text(bg, REG, "ഓരോ ദളവും ഒരു ഭാഷ.", 26, 1030, 602, (180, 190, 215))
    d.rounded_rectangle((1030, 680, 1560, 684), radius=2, fill=(50, 54, 78, 255))
    draw_label(d, "Kallar  ·  COLRv1 Spectrum", (1030, 710), 12,
               (140, 152, 185), tracking=1)
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_ui.png"))
    print("ui")


def make_lockup():
    W, H = 1600, 620
    bg = Image.new("RGBA", (W, H), (247, 243, 235, 255))
    d = ImageDraw.Draw(bg)
    # gateway/lotus mark: line-art petals on a threshold
    outer = teardrop_pts(300, 300, 108, 158, cusp=30)
    d.line(outer + [outer[0]], fill=(36, 30, 26, 255), width=7, joint="curve")
    inner = teardrop_pts(300, 308, 62, 92, cusp=16)
    d.line(inner + [inner[0]], fill=(36, 30, 26, 255), width=5, joint="curve")
    d.line((300 - 128, 458, 300 + 128, 458), fill=(36, 30, 26, 255), width=7)
    d.ellipse((287, 297, 313, 323), fill=(238, 121, 68, 255))
    paste_text(bg, BOLD, "കല്ലാർ", 96, 500, 300, (28, 26, 30))
    draw_label(d, "KALLAR", (510, 350), 18, (120, 80, 50), bold=True, tracking=4)
    draw_label(d, "Aperture-variable Malayalam  ·  APER 0—100", (510, 384), 15, (120, 110, 100))
    draw_rule(d, 510, 430, 1100, 430, (30, 30, 30, 40))
    draw_label(d, "OFL 1.1  ·  v1.100", (510, 450), 13, (150, 120, 90))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_lockup.png"))
    print("lockup")


def make_anim():
    W = H = 480
    frames = []
    font_paths = {v: instantiate_aper(BOLD, v) for v in range(0, 101, 5)}
    for v in range(0, 101, 5):
        bg = Image.new("RGBA", (W, H), (8, 10, 20, 255))
        d = ImageDraw.Draw(bg)
        # soft horizon
        for y in range(H):
            t = y / H
            r = int(8 + 18 * t)
            g = int(10 + 10 * t)
            b = int(20 + 16 * t)
            d.line([(0, y), (W, y)], fill=(r, g, b, 255))
        alpha, baseline = render_alpha(font_paths[v], "ക", size=250, pad=10)
        if alpha is not None:
            layer = Image.new("RGBA", (alpha.width, alpha.height), (255, 238, 224, 255))
            layer.putalpha(alpha)
            bg.alpha_composite(layer, (int(W / 2 - alpha.width / 2), int(80)))
        d = ImageDraw.Draw(bg)
        draw_label(d, "APER", (40, 392), 12, (150, 162, 200), bold=True, tracking=2)
        draw_label(d, f"{v:03d}", (40, 410), 30, (238, 121, 68), bold=True)
        # progress bar
        d.rounded_rectangle((130, 420, W - 40, 426), radius=3, fill=(255, 255, 255, 28))
        d.rounded_rectangle((130, 420, 130 + (W - 170) * v / 100, 426), radius=3,
                            fill=(238, 121, 68, 255))
        frames.append(bg.convert("RGB"))
    frames[0].save(os.path.join(PROOFS, "kallar_aper.gif"),
                   save_all=True, append_images=frames[1:], duration=90, loop=0,
                   optimize=True)
    print("anim")


def main():
    which = sys.argv[1:] or ["hero", "axis", "gradient", "spectrum", "glyphs",
                             "poster", "editorial", "social", "ui", "lockup", "anim"]
    if "poster" in which:
        make_poster()
    if "editorial" in which:
        make_editorial()
    if "social" in which:
        make_social()
    if "ui" in which:
        make_ui()
    if "lockup" in which:
        make_lockup()
    if "anim" in which:
        make_anim()
    if "hero" in which:
        make_hero()
    if "axis" in which:
        make_axis()
    if "gradient" in which:
        make_gradient()
    if "spectrum" in which:
        make_spectrum()
    if "glyphs" in which:
        make_glyphs()


if __name__ == "__main__":
    main()

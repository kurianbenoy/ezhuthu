#!/usr/bin/env python3
"""Generate the multiscript specimen images.

Outputs (proofs/):
  kallar_multiscript.png       — five-script hero poster
  kallar_multiscript_axis.png  — the APER axis across four scripts
  kallar_devanagari.png        — Devanagari sheet
  kallar_tamil.png             — Tamil sheet
  kallar_telugu.png            — Telugu sheet
  kallar_kannada.png           — Kannada sheet
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from specimen import (  # noqa: E402
    PROOFS,
    STOPS,
    add_mandala,
    draw_label,
    draw_rule,
    glow_background,
    gradient_text,
    solid_text,
)
from multiscript import SCRIPTS  # noqa: E402
from render import render_alpha  # noqa: E402

FONTS = os.path.join(os.path.dirname(PROOFS), "fonts")
TMP = os.path.join(PROOFS, "..", "sources", "masters")
os.makedirs(TMP, exist_ok=True)

PAPER = (247, 243, 235, 255)
INK = (28, 26, 30)
MUTED = (120, 110, 100)
ORANGE = (238, 121, 68)
BLUE = (43, 63, 176)


def font_path(stem, style):
    return os.path.join(FONTS, f"{stem}-{style}.ttf")


def instantiate_script(stem, weight, aper, tag=""):
    src = os.path.join(FONTS, f"{stem}-{'Bold' if weight >= 700 else 'Regular'}.ttf")
    out = os.path.join(TMP, f"{stem}-{weight}-aper{int(aper)}{tag}.ttf")
    font = TTFont(src)
    instantiateVariableFont(font, {"APER": aper}, inplace=True)
    font.save(out)
    return out


def paper_background(w, h):
    bg = Image.new("RGBA", (w, h), PAPER)
    rng = np.random.default_rng(19)
    grain = rng.normal(0, 1.6, (h, w, 1))
    arr = np.clip(np.array(bg)[:, :, :3] + grain, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def paste_solid(canvas, font, text, size, x, baseline, color=INK, pad=20):
    layer, b = solid_text(font, text, size, color=color + (255,), pad=pad)
    if layer is None:
        return
    canvas.alpha_composite(layer, (int(x), int(baseline - b)))


def gradient_paste(canvas, font, text, size, x, baseline, stops=STOPS,
                   glow=0, pad=24):
    layer, b, _ = gradient_text(font, text, size, stops=stops, pad=pad, glow=glow)
    if layer is None:
        return
    canvas.alpha_composite(layer, (int(x), int(baseline - b)))


def script_display(script):
    return script["name"]


def make_hero():
    W, H = 1600, 1900
    bg = glow_background(W, H).convert("RGBA")
    add_mandala(bg, W / 2, 260, 360, petals=28, alpha=14, width=1)
    d = ImageDraw.Draw(bg)
    draw_label(d, "KALLAR", (90, 80), 20, (205, 215, 255),
               bold=True, tracking=5)
    draw_label(d, "MULTISCRIPT  /  ONE APERTURE", (90, 116), 14,
               (145, 160, 200), tracking=4)
    draw_label(d, "APER 0 → 100", (W - 300, 80), 16, (255, 210, 170),
               bold=True)
    draw_rule(d, 90, 164, W - 90, 164, (255, 255, 255, 28))

    # Malayalam stays the reference row, then the four new scripts.
    rows = [
        ("മലയാളം", "MALAYALAM", "MLYM",
         os.path.join(FONTS, "Kallar-BoldPetal.ttf"), "കല്ലാർ"),
    ]
    for key, script in SCRIPTS.items():
        rows.append((
            {
                "devanagari": "देवनागरी", "tamil": "தமிழ்",
                "telugu": "తెలుగు", "kannada": "ಕನ್ನಡ",
            }[key],
            key.upper(),
            {"devanagari": "DEVA", "tamil": "TAML",
             "telugu": "TELU", "kannada": "KNDA"}[key],
            font_path(script["stem"], "BoldPetal"),
            script_display(script),
        ))

    y = 260
    for name, label, code, path, text in rows:
        draw_label(d, label, (90, y - 10), 13, (150, 165, 205),
                   bold=True, tracking=3)
        draw_label(d, code, (90, y + 14), 11, (238, 140, 100), tracking=2)
        paste_solid(bg, path, name, 34, 90, y + 92, (200, 208, 232))
        gradient_paste(bg, path, text, 132, 300, y + 80,
                       stops=[(0, (255, 246, 232)), (1, (255, 205, 160))],
                       glow=10)
        y += 290
        if y < 1650:
            draw_rule(d, 90, y - 40, W - 90, y - 40, (255, 255, 255, 22))

    draw_rule(d, 90, H - 130, W - 90, H - 130, (255, 255, 255, 30))
    draw_label(d, "KALLAR  /  v1.200  /  OFL 1.1", (90, H - 100),
               14, (150, 162, 195), tracking=1)
    draw_label(d, "MALAYALAM  ·  DEVANAGARI  ·  TAMIL  ·  TELUGU  ·  KANNADA",
               (90, H - 74), 12, (190, 170, 150), tracking=1)
    draw_label(d, "A type system that blooms.", (W - 330, H - 100), 16,
               (255, 235, 220))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_multiscript.png"))
    print("multiscript hero")


def make_axis():
    W, H = 1600, 1160
    bg = glow_background(W, H).convert("RGBA")
    bg = Image.blend(bg, Image.new("RGBA", (W, H), (8, 10, 22, 255)), 0.55)
    d = ImageDraw.Draw(bg)
    draw_label(d, "THE APERTURE AXIS", (90, 78), 20, (210, 220, 255),
               bold=True, tracking=4)
    draw_label(d, "ROUND  →  BLOOM  →  PETAL", (90, 112), 13,
               (150, 165, 205), tracking=3)
    draw_label(d, "APER 0 — 100", (W - 280, 80), 15, (255, 210, 170),
               bold=True)

    values = [0, 25, 50, 75, 100]
    rows = [
        ("devanagari", "क", "DEVANAGARI"),
        ("tamil", "ண", "TAMIL"),
        ("telugu", "క", "TELUGU"),
        ("kannada", "ಕ", "KANNADA"),
    ]
    left = 330
    colw = (W - left - 80) / len(values)
    top = 230
    rowh = 205
    for j, v in enumerate(values):
        x = left + j * colw + colw / 2
        draw_label(d, f"{v:03d}", (int(x - 18), 180), 14, (238, 140, 100),
                   bold=True)
        draw_label(d, "ROUND" if v == 0 else "PETAL" if v == 100 else "",
                   (int(x - 28), 202), 9, (125, 140, 180), tracking=2)
    draw_rule(d, 90, 222, W - 90, 222, (255, 255, 255, 26))

    for i, (key, glyph, label) in enumerate(rows):
        script = SCRIPTS[key]
        y = top + i * rowh
        draw_label(d, label, (90, y + 86), 13, (150, 165, 205),
                   bold=True, tracking=3)
        for j, v in enumerate(values):
            p = instantiate_script(script["stem"], 700, v, tag="_axis")
            alpha, _ = render_alpha(p, glyph, size=128, pad=12)
            if alpha is None:
                continue
            x = int(left + j * colw + (colw - alpha.width) / 2)
            layer = Image.new("RGBA", (alpha.width, alpha.height),
                              (248, 241, 228, 255))
            layer.putalpha(alpha)
            bg.alpha_composite(layer, (x, int(y + 20)))
        if i < len(rows) - 1:
            draw_rule(d, 90, y + rowh - 18, W - 90, y + rowh - 18,
                      (255, 255, 255, 18))
    draw_label(d, "Kallar  /  the same axis in four scripts",
               (90, H - 60), 12, (150, 162, 195))
    bg.convert("RGB").save(os.path.join(PROOFS, "kallar_multiscript_axis.png"))
    print("multiscript axis")


def make_sheet(key):
    script = SCRIPTS[key]
    stem = script["stem"]
    display = script["display"]
    rep = {
        "devanagari": "क", "tamil": "ண",
        "telugu": "క", "kannada": "ಕ",
    }[key]
    script_name = {
        "devanagari": "देवनागरी", "tamil": "தமிழ்",
        "telugu": "తెలుగు", "kannada": "ಕನ್ನಡ",
    }[key]
    W, H = 1600, 1200
    bg = paper_background(W, H)
    d = ImageDraw.Draw(bg)
    draw_label(d, f"KALLAR  /  {key.upper()}", (80, 62), 13,
               (150, 110, 70), bold=True, tracking=2)
    draw_rule(d, 80, 96, W - 80, 96, (30, 30, 30, 40))
    draw_label(d, "APER 0 — 100", (W - 250, 62), 13, (150, 110, 70),
               bold=True, tracking=2)

    # large display word
    gradient_paste(bg, font_path(stem, "BoldPetal"), script["name"], 250,
                   80, 380, stops=[(0, (20, 24, 40)), (1, (120, 50, 35))],
                   pad=40)
    # the script's own name, in its own script
    paste_solid(bg, font_path(stem, "Petal"), script_name, 44, 80, 520,
                (120, 80, 50))
    # second display word
    paste_solid(bg, font_path(stem, "BoldPetal"), display[2], 110,
                80, 650, (28, 26, 30))
    # paragraph
    y = 745
    for line in script["paragraph"]:
        paste_solid(bg, font_path(stem, "Petal"), line, 30, 80, y,
                    (55, 50, 45))
        y += 46

    # APER strip
    strip_y = 880
    draw_label(d, "THE APER STRIP", (80, strip_y - 28), 11, (150, 110, 70),
               bold=True, tracking=2)
    for j, v in enumerate((0, 25, 50, 75, 100)):
        p = instantiate_script(stem, 700, v, tag="_sheet")
        alpha, _ = render_alpha(p, rep, size=92, pad=10)
        if alpha is None:
            continue
        x = 80 + j * 300
        layer = Image.new("RGBA", (alpha.width, alpha.height),
                          (28, 26, 30, 255))
        layer.putalpha(alpha)
        bg.alpha_composite(layer, (x, strip_y))
        draw_label(d, f"{v:03d}", (x, strip_y + 120), 12, (238, 121, 68),
                   bold=True)
        draw_label(d, "ROUND" if v == 0 else "PETAL" if v == 100 else "",
                   (x, strip_y + 140), 9, (140, 120, 100), tracking=2)

    # spectrum sample, on the right, above the strip
    draw_label(d, "SPECTRUM  /  COLRv1", (W - 520, 640), 11, (150, 110, 70),
               bold=True, tracking=2)
    gradient_paste(bg, font_path(stem, "BoldPetal"), script["name"], 96,
                   W - 520, 775, stops=STOPS, glow=6)

    draw_rule(d, 80, H - 90, W - 80, H - 90, (30, 30, 30, 36))
    draw_label(d, f"{script['family']}  /  OFL 1.1  /  base: Manjari  /  "
               f"{script['script_name']} letters: {script['donor_name']}",
               (80, H - 70), 11, (150, 130, 110))
    bg.convert("RGB").save(os.path.join(PROOFS, f"kallar_{key}.png"))
    print(f"{key} sheet")


def main():
    which = sys.argv[1:] or ["hero", "axis", "devanagari", "tamil",
                             "telugu", "kannada"]
    if "hero" in which:
        make_hero()
    if "axis" in which:
        make_axis()
    for key in ("devanagari", "tamil", "telugu", "kannada"):
        if key in which:
            make_sheet(key)


if __name__ == "__main__":
    main()

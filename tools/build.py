#!/usr/bin/env python3
"""Ezhuthu font builder.

Pipeline: parametric glyph designs (glyphs_ml) -> MalayalamFont (ufoLib2 subclass,
vendored from SMC Nupuram) with GSUB/GPOS via fontFeatures -> UFO -> ufo2ft
compilers -> TTF / OTF / WOFF2.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
from munch import munchify
from ufoLib2.objects import Anchor, Component, Glyph

from glyphs_ml import DESIGNS, build_ml
import shapes
from malayalamfont import MalayalamFont
from shapes import GlyphBuilder
from svgglyph import SVGGlyph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "config.yaml")

LATIN_DIGITS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
PUNCT = {".": 260, ",": 260, ":": 300, "'": 240, '"': 420, "(": 340, ")": 340,
         "-": 400}


def latin_digit(b, ch):
    """Parametric 0-9: simple stems + arches, height 620."""
    top = 620
    if ch == "0":
        shapes.ml_arch_ring(b, 90, 290, 20, top, 68)
    elif ch == "1":
        b.stem(220, 20, 220, top, 68)
        b.stem(100, 140, 220, 20, 60)  # little diagonal flag at top
    elif ch == "2":
        shapes.ml_arch_ring(b, 90, 290, 240, top, 68)
        b.stem(90, 260, 290, 20, 68)
        shapes.ml_bar(b, 80, 300, 20, 68)
    elif ch == "3":
        shapes.ml_arch_ring(b, 90, 290, 220, top, 68)
        shapes.ml_cup(b, 290, 30, 130, 74, 350, 175)
        shapes.ml_bar(b, 110, 300, 320, 60)
    elif ch == "4":
        b.stem(200, top, 90, 180, 68)
        shapes.ml_bar(b, 70, 290, 180, 68)
        b.stem(210, top, 210, 20, 68)
    elif ch == "5":
        b.stem(90, top, 290, top, 68)
        b.stem(90, top, 90, 300, 68)
        shapes.ml_arch_ring(b, 100, 290, 20, 320, 68)
    elif ch == "6":
        shapes.ml_arch_ring(b, 90, 370, 20, 340, 68)
        shapes.ml_arch(b, 80, 290, 20, top, 68)
    elif ch == "7":
        shapes.ml_bar(b, 80, 300, top, 68)
        b.stem(300, top, 130, 20, 68)
    elif ch == "8":
        shapes.ml_arch_ring(b, 90, 290, 200, top, 68)
        shapes.ml_arch_ring(b, 90, 290, 20, 260, 68)
    elif ch == "9":
        shapes.ml_arch_ring(b, 90, 370, 320, top, 68)
        shapes.ml_arch(b, 90, 380, 20, 340, 68)
    return


def latin_punct(b, ch):
    if ch == ".":
        b.dot(130, 20, 68)
    elif ch == ",":
        b.dot(130, -20, 68)
        b.stem(130, -20, 170, -120, 56)
    elif ch == ":":
        b.dot(130, 400, 68)
        b.dot(130, 150, 68)
    elif ch == "'":
        b.stem(140, 360, 100, 480, 62)
        b.stem(120, 440, 120, 480, 62)
    elif ch == '"':
        b.stem(100, 360, 60, 480, 62)
        b.stem(200, 360, 160, 480, 62)
    elif ch == "(":
        # sweep an arc band from bottom-right up and over the top to bottom-left
        b.arc(140, 310, 300, 64, 300, 570)
    elif ch == ")":
        b.arc(140, 310, 300, 64, 10, 280)
    elif ch == "-":
        shapes.ml_bar(b, 60, 320, 300, 68)


def dotted_circle(b):
    import math
    for i in range(16):
        a = math.pi / 2 + (math.pi / 8) * i
        b.dot(355 + 260 * math.cos(a), 350 + 260 * math.sin(a), 40)


class EzhuthuFont(MalayalamFont):
    """MalayalamFont whose glyph designs come from glyphs_ml + a few basics."""

    def __init__(self, options, style="Regular", weight=400, design=None):
        super().__init__(options, style=style, weight=weight)
        self.design = design or DESIGNS[style]

    def load_design_glyphs(self, design_dir=None):
        design = self.design
        made = build_ml(self, design)
        self.add_basics()

    # basics --------------------------------------------------------------
    def add_basics(self):
        design = self.design
        if ".notdef" not in self:
            self.newGlyph(".notdef")
        notdef = self[".notdef"]
        notdef.width = 700
        b = GlyphBuilder(notdef)
        shapes.ml_arch_ring(b, 140, 560, 60, 660, 74)
        b.union()

        # Malayalam digits ൦..൯
        for i, cp in enumerate(range(0x0D66, 0x0D70)):
            gname = "uni" + format(cp, "04X")
            g = self.newGlyph(gname)
            g.width = 560
            g.unicodes = [cp]
            b = GlyphBuilder(g)
            top = 620
            if i == 0:
                b.loop(160, 320, 80, 68)
            elif i == 1:
                b.stem(280, 40, 280, top, 68)
                b.stem(120, 160, 280, 40, 60)
            elif i == 2:
                shapes.ml_arch_ring(b, 110, 310, 240, top, 68)
                b.stem(110, 280, 310, 40, 68)
                shapes.ml_bar(b, 90, 320, 40, 68)
            elif i == 3:
                shapes.ml_arch_ring(b, 110, 310, 220, top, 68)
                shapes.ml_cup(b, 310, 40, 130, 74, 350, 175)
                shapes.ml_bar(b, 130, 310, 330, 60)
            else:
                b.stem(300, 40, 300, top, 68)
                b.loop(160, 420, 70, 68)
                for _k in range(i - 4):
                    b.dot(160, 300 - _k * 90, 60)
            b.union()

        # rare Malayalam block glyphs
        def _rare(name, cp, fn, width=560):
            gname = "uni" + format(cp, "04X")
            g = self.newGlyph(gname)
            g.width = width
            g.unicodes = [cp]
            b = GlyphBuilder(g)
            fn(b)
            b.union()

        def tiny_loop(b, y=700, r=30):
            b.loop(60, y, r, 56)
            # counter inner hole handled by loop; center dot
            b.dot(60, y, 150)

        def nnn_design(b):
            shapes.ml_arch(b, 80, 330, 0, 500, 78)
            b.stem(360, 500, 360, 0, 78)
            shapes.ml_crook(b, 360, 500, 70, 78)
            shapes.ml_arch(b, 390, 660, 0, 500, 78)
            shapes.ml_cup(b, 660, 25, 60, 78, 278, 80)

        def tts_design(b):
            shapes.ml_arch(b, 90, 380, 0, 500, 78)
            shapes.ml_cup(b, 90, 20, 70, 78, 265, 105)
            shapes.ml_cup(b, 400, 60, 160, 78, 345, 175)

        def avagraha_design(b):
            b.stem(160, 500, 80, 330, 62)
            b.stem(160, 500, 245, 330, 62)
            shapes.ml_cup(b, 160, 420, 90, 62, 345, 195)

        def para_design(b):
            b.stem(60, 500, 60, 200, 62)
            shapes.ml_bar(b, 30, 260, 350, 62)
            shapes.ml_bar(b, 30, 260, 260, 62)

        def numbar_design(n):
            def _f(b):
                b.stem(140, 160, 140, 0, 62)
                for k in range(n):
                    b.dot(140, 260 + k * 90, 44)
            return _f

        def quarter_design(b):
            b.loop(140, 240, 60, 56)

        def more_dots(b):
            b.loop(140, 240, 60, 56)
            b.dot(260, 240, 44)

        def even_more(b):
            b.loop(140, 240, 60, 56)
            b.dot(260, 240, 44)
            b.dot(260, 120, 44)

        def dots2(b):
            b.dot(120, 320, 44)
            b.dot(120, 230, 44)
            shapes.ml_bar(b, 40, 220, 140, 56)

        def dots3(b):
            for _k in range(3):
                b.dot(120, 340 - _k * 90, 44)
            shapes.ml_bar(b, 40, 220, 120, 56)

        def candrabindu2(b):
            b.loop(60, 700, 28, 54)
            b.dot(60, 790, 44)

        _rare("uni0D04", 0x0D04, candrabindu2, 120)
        _rare("uni0D29", 0x0D29, nnn_design, 860)
        _rare("uni0D3A", 0x0D3A, tts_design, 620)
        _rare("uni0D3D", 0x0D3D, avagraha_design, 340)
        _rare("uni0D4F", 0x0D4F, para_design, 300)
        _rare("uni0D70", 0x0D70, numbar_design(1), 340)
        _rare("uni0D71", 0x0D71, numbar_design(2), 340)
        _rare("uni0D72", 0x0D72, numbar_design(3), 340)
        _rare("uni0D73", 0x0D73, quarter_design, 340)
        _rare("uni0D74", 0x0D74, more_dots, 340)
        _rare("uni0D75", 0x0D75, even_more, 340)

        gc = self.newGlyph("uni25CC")  # dotted circle
        gc.width = 710
        b = GlyphBuilder(gc)
        dotted_circle(b)
        b.union()

        for ch, adv in [(d, 560) for d in LATIN_DIGITS] + list(PUNCT.items()):
            name = SVGGlyph.get_glyph_name(ch)
            if name in self:
                continue
            g = self.newGlyph(name)
            g.width = adv
            g.unicodes = [ord(ch)]
            b = GlyphBuilder(g)
            if ch.isdigit():
                latin_digit(b, ch)
            else:
                latin_punct(b, ch)
            b.union()


def build_style(style):
    with open(CONFIG) as fp:
        options = munchify(yaml.safe_load(fp))
    weight = DESIGNS[style].weight
    mf = EzhuthuFont(options, style=style, weight=weight)
    # empty/base glyphs + parametric designs (design_dir unused by our override)
    mf.build(None)

    mf.buildFeatures()
    mf.setFontInfo()
    mf.updateFontVersion()
    return mf


def compile_fonts(styles, formats=("ttf",)):
    import ufo2ft
    import ufoLib2
    os.makedirs("fonts", exist_ok=True)
    for style in styles:
        ufo = ufoLib2.Font.open(f"sources/ufo/Ezhuthu-{style}.ufo")
        for fmt in formats:
            if fmt == "ttf":
                font = ufo2ft.compileTTF(ufo)
                font.save(f"fonts/Ezhuthu-{style}.ttf")
            elif fmt == "otf":
                font = ufo2ft.compileOTF(ufo)
                font.save(f"fonts/Ezhuthu-{style}.otf")
            print(f"compiled fonts/Ezhuthu-{style}.{fmt}")


if __name__ == "__main__":
    os.chdir(ROOT)
    os.makedirs("sources/ufo", exist_ok=True)
    styles = sys.argv[1:] or ["Regular"]
    for style in styles:
        mf = build_style(style)
        print(f"{style}: {len(mf)} glyphs, {len(mf.features.text.splitlines())} fea lines")
        mf.save(f"sources/ufo/Ezhuthu-{style}.ufo", overwrite=True)
        print(f"saved sources/ufo/Ezhuthu-{style}.ufo")
    compile_fonts(styles)

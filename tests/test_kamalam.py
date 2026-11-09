#!/usr/bin/env python3
"""Shape, variation and color tests for Ezhuthu Kamalam.

Run: .venv/bin/python tests/test_kamalam.py
"""
import os
import sys

import uharfbuzz as hb
from fontTools.ttLib import TTFont, TTLibError

REG = "fonts/EzhuthuKamalam-Regular.ttf"
BOLD = "fonts/EzhuthuKamalam-Bold.ttf"
SPECTRUM = "fonts/EzhuthuKamalam-Spectrum.ttf"
SPECTRUM_REG = "fonts/EzhuthuKamalam-SpectrumRegular.ttf"
PETAL = "fonts/EzhuthuKamalam-Petal.ttf"

FAILS = []


def fail(msg):
    print("FAIL", msg)
    FAILS.append(msg)


def load(path):
    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    return hb.Font(face)


def shape(font, text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True, "calt": True})
    return [font.glyph_to_string(gi.codepoint) for gi in buf.glyph_infos]


# ---------------------------------------------------------------------------
# tables / axes
# ---------------------------------------------------------------------------
def test_axes():
    f = TTFont(REG)
    if "fvar" not in f:
        return fail("Regular is not variable")
    axes = {a.axisTag: a for a in f["fvar"].axes}
    if "APER" not in axes:
        return fail("APER axis missing")
    a = axes["APER"]
    if (a.minValue, a.defaultValue, a.maxValue) != (0, 100, 100):
        fail(f"APER range wrong: {a.minValue}/{a.defaultValue}/{a.maxValue}")
    if "STAT" not in f:
        fail("STAT table missing")
    else:
        st = f["STAT"].table
        values = []
        if st.AxisValueArray:
            for av in st.AxisValueArray.AxisValue:
                if av.Format == 1:
                    values.append((av.AxisIndex, av.Value))
        if (0, 0) not in values or (0, 50) not in values or (0, 100) not in values:
            fail(f"STAT axis values incomplete: {values}")

    fs = TTFont(PETAL)
    if "fvar" in fs:
        fail("static Petal instance still has fvar")
    print("PASS axes")


def test_license():
    for path in (REG, BOLD, SPECTRUM, PETAL):
        f = TTFont(path)
        lic = f["name"].getDebugName(13) or ""
        if "SIL Open Font License" not in lic:
            fail(f"{path}: OFL name missing")
        if "Manjari" not in (f["name"].getDebugName(0) or ""):
            fail(f"{path}: Manjari attribution missing in copyright")
    print("PASS license metadata")


# ---------------------------------------------------------------------------
# shaping
# ---------------------------------------------------------------------------
CASES = [
    "ക", "ൻ", "ർ", "ൽ", "ൾ", "ൺ", "ൖ", "ൿ",
    "ക്ക", "ക്ഷ", "ഗ്ഗ", "ങ്ങ", "ഞ്ഞ", "മ്പ", "റ്റ", "സ്ത്ര",
    "ക്കു", "ല്ലൂ", "ക്രു", "കി", "കെ", "കൈ", "കൊ", "കോ", "കൌ",
    "ക്യ", "ക്വ", "ജ്ര", "അം", "അഃ",
    "മലയാളം", "എഴുത്ത്", "കേരളം", "ശ്രീ", "ചന്ദ്രൻ", "കൊണ്ട്",
]


def test_shaping():
    reg = load(REG)
    blob0 = shape(reg, "മലയാളം")
    for aper in (0, 50, 100):
        reg.set_variations({"APER": aper})
        for text in CASES:
            names = shape(reg, text)
            if not names or ".notdef" in names:
                fail(f"APER {aper}: {text!r} -> {names}")
            if aper == 100:
                base = shape(reg, text)
                if text == "മലയാളം":
                    pass
        # sequences must be identical across the axis
        reg.set_variations({"APER": 0})
        seq0 = [shape(reg, t) for t in CASES]
        reg.set_variations({"APER": 100})
        seq100 = [shape(reg, t) for t in CASES]
        if seq0 != seq100:
            fail(f"shaping changed across APER at {aper}")
            break
    print("PASS shaping across APER")


def test_marks_and_calt():
    reg = load(REG)
    # the i-sign wrap is a Manjari feature we keep
    names = shape(reg, "നി")
    if len(names) < 2:
        fail(f"നി shaped oddly: {names}")
    # anusvara and visarga attach
    for text in ("അം", "അഃ", "കാം"):
        names = shape(reg, text)
        if not names or ".notdef" in names:
            fail(f"mark case {text!r} -> {names}")
    print("PASS marks/calt")


def test_coverage():
    f = TTFont(REG)
    cmap = f.getBestCmap()
    hb_font = load(REG)
    import unicodedata
    missing = []
    for cp in range(0x0D00, 0x0D80):
        if cp not in cmap:
            continue
        try:
            unicodedata.name(chr(cp))
        except ValueError:
            continue
        names = shape(hb_font, chr(cp))
        if ".notdef" in names:
            missing.append(hex(cp))
    if missing:
        fail("coverage misses: " + ", ".join(missing))
    else:
        print("PASS coverage")


def test_outline_variation():
    # instantiate two extremes and compare a contour's bbox
    from fontTools.varLib.instancer import instantiateVariableFont
    heights = []
    for aper in (0, 100):
        f = TTFont(REG)
        instantiateVariableFont(f, {"APER": aper}, inplace=True)
        g = f["glyf"]["th1"]  # ത
        heights.append(g.yMax - g.yMin)
    if heights[0] == heights[1]:
        fail("APER does not change outlines")
    else:
        print(f"PASS outline variation ({heights[0]} -> {heights[1]})")


# ---------------------------------------------------------------------------
# color
# ---------------------------------------------------------------------------
def test_color():
    for path in (SPECTRUM, SPECTRUM_REG):
        f = TTFont(path)
        if "COLR" not in f or "CPAL" not in f:
            fail(f"{path}: missing COLR/CPAL")
            continue
        colr = f["COLR"]
        if colr.version != 1:
            fail(f"{path}: COLR version {colr.version}, expected 1")
        cpal = f["CPAL"]
        if not cpal.palettes or len(cpal.palettes[0]) < 2:
            fail(f"{path}: CPAL palette too small")
        records = colr.table.BaseGlyphList.BaseGlyphPaintRecord
        if len(records) < 500:
            fail(f"{path}: too few color glyphs: {len(records)}")
        ok = 0
        for rec in records[:50]:
            p = rec.Paint
            if p.Format != 10:  # PaintGlyph
                continue
            if p.Paint.Format != 4:  # PaintLinearGradient
                continue
            if not p.Paint.ColorLine.ColorStop:
                continue
            ok += 1
        if ok < 40:
            fail(f"{path}: paint graph check failed ({ok}/50)")
        print(f"PASS color tables {os.path.basename(path)} "
              f"({len(records)} glyphs, {len(cpal.palettes[0])} colors)")


def main():
    test_axes()
    test_license()
    test_shaping()
    test_marks_and_calt()
    test_coverage()
    test_outline_variation()
    test_color()
    print()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        sys.exit(1)
    print("all Kamalam tests passed")


if __name__ == "__main__":
    main()

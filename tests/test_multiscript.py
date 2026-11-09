#!/usr/bin/env python3
"""Shaping, coverage, variation and colour tests for the multiscript family.

Run: .venv/bin/python tests/test_multiscript.py
"""
import os
import sys
import unicodedata

import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

from kallar import add_case_pairs  # noqa: E402
from multiscript import SCRIPTS  # noqa: E402

FAILS = []


def fail(msg):
    print("FAIL", msg)
    FAILS.append(msg)


def path(stem, style):
    return os.path.join(ROOT, "fonts", f"{stem}-{style}.ttf")


def load(path_name):
    blob = hb.Blob.from_file_path(path_name)
    face = hb.Face(blob)
    return hb.Font(face)


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True, "calt": True})
    return [
        (font.glyph_to_string(info.codepoint), pos.x_advance)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions)
    ]


def outline(font_path, glyph_name, aper):
    font = TTFont(font_path)
    instantiateVariableFont(font, {"APER": aper}, inplace=True)
    glyph = font["glyf"][glyph_name]
    pen = DecomposingRecordingPen(font.getGlyphSet())
    glyph.draw(pen, font["glyf"])
    return pen.value


# ---------------------------------------------------------------------------
# axes / metadata
# ---------------------------------------------------------------------------
def test_axes():
    for key, script in SCRIPTS.items():
        for style in ("Regular", "Bold"):
            font = TTFont(path(script["stem"], style))
            if "fvar" not in font:
                fail(f"{key} {style}: not variable")
                continue
            axes = {a.axisTag: a for a in font["fvar"].axes}
            if "APER" not in axes:
                fail(f"{key} {style}: APER missing")
                continue
            a = axes["APER"]
            if (a.minValue, a.defaultValue, a.maxValue) != (0, 100, 100):
                fail(f"{key} {style}: APER range wrong")
            if "STAT" not in font:
                fail(f"{key} {style}: STAT missing")
                continue
            values = set()
            st = font["STAT"].table
            if st.AxisValueArray:
                for av in st.AxisValueArray.AxisValue:
                    if av.Format == 1:
                        values.add(av.Value)
            if not {0, 50, 100}.issubset(values):
                fail(f"{key} {style}: STAT values {sorted(values)}")
    print("PASS axes (4 scripts x Regular/Bold)")


def test_metadata():
    for key, script in SCRIPTS.items():
        stem = script["stem"]
        files = [
            path(stem, "Regular"), path(stem, "Bold"),
            path(stem, "Round"), path(stem, "Petal"),
            path(stem, "BoldPetal"),
            path(stem, "SpectrumRegular"), path(stem, "Spectrum"),
        ]
        for p in files:
            font = TTFont(p)
            lic = font["name"].getDebugName(13) or ""
            copyright_note = font["name"].getDebugName(0) or ""
            designer = font["name"].getDebugName(9) or ""
            if "SIL Open Font License" not in lic:
                fail(f"{os.path.basename(p)}: OFL missing")
            if "Base skeleton: Manjari" not in copyright_note:
                fail(f"{os.path.basename(p)}: Manjari base attribution missing")
            if "Manjari Project Authors" not in copyright_note:
                fail(f"{os.path.basename(p)}: Manjari copyright missing")
            if "Noto Project Authors" not in copyright_note:
                fail(f"{os.path.basename(p)}: Noto donor copyright missing")
            if "Kallar Project Authors" not in copyright_note:
                fail(f"{os.path.basename(p)}: Kallar copyright missing")
            if "Santhosh Thottingal" not in designer:
                fail(f"{os.path.basename(p)}: Manjari designer credit missing")
            if "Noto Project Authors" not in designer:
                fail(f"{os.path.basename(p)}: Noto donor designer credit missing")
        if (TTFont(path(stem, "Regular"))["name"].getDebugName(1)
                != script["family"]):
            fail(f"{key}: family name mismatch")
    print("PASS license and attribution metadata")


def test_manjari_base():
    """The shared Latin, digits and punctuation must be Manjari's outlines."""
    refs = {}
    for weight in (400, 700):
        name = "Manjari-Regular.ttf" if weight == 400 else "Manjari-Bold.ttf"
        ref = TTFont(os.path.join(ROOT, "sources", "base", name))
        scale_upem(ref, 1000)
        add_case_pairs(ref)
        refs[weight] = ref

    def outline(font, gname):
        pen = DecomposingRecordingPen(font.getGlyphSet())
        font["glyf"][gname].draw(pen, font["glyf"])
        return pen.value

    # The donor may localise glyph names (Tamil uses zero.tamil for U+0030),
    # so resolve the output glyph through its cmap.
    shared = {ord("H"): "H", ord("a"): "a", ord("0"): "zero",
              ord("."): "period"}
    for key, script in SCRIPTS.items():
        for style, weight in (("Regular", 400), ("Bold", 700)):
            font = TTFont(path(script["stem"], style))
            ref = refs[weight]
            cmap = font.getBestCmap()
            for cp, ref_name in shared.items():
                gname = cmap.get(cp)
                if gname is None or gname not in font["glyf"]:
                    fail(f"{key} {style}: U+{cp:04X} missing")
                    continue
                if outline(font, gname) != outline(ref, ref_name):
                    fail(f"{key} {style}: U+{cp:04X} is not Manjari's outline")
                if (font["hmtx"].metrics[gname]
                        != ref["hmtx"].metrics[ref_name]):
                    fail(f"{key} {style}: U+{cp:04X} is not Manjari's advance")
            space = cmap.get(0x20)
            if (space is None or font["hmtx"].metrics[space]
                    != ref["hmtx"].metrics["space"]):
                fail(f"{key} {style}: space is not Manjari's advance")

            # The Latin kern pairs must be Manjari's too, not the donor's.
            ref_path = os.path.join(
                ROOT, "sources", "base",
                "Manjari-Regular.ttf" if weight == 400 else "Manjari-Bold.ttf",
            )
            ref_hb = load(ref_path)
            out_hb = load(path(script["stem"], style))
            for text in ("AV", "To", "Wa"):
                ref_adv = [round(adv * 1000 / 2048)
                           for _, adv in shape(ref_hb, text)]
                out_adv = [adv for _, adv in shape(out_hb, text)]
                if len(ref_adv) != len(out_adv) or any(
                        abs(a - b) > 1 for a, b in zip(ref_adv, out_adv)):
                    fail(f"{key} {style}: Latin kern {text!r} is not Manjari's")
    print("PASS Manjari base (shared Latin, digits, punctuation, spacing and kerning)")


# ---------------------------------------------------------------------------
# shaping
# ---------------------------------------------------------------------------
def test_shaping():
    for key, script in SCRIPTS.items():
        cases = ([script["name"]] + script["cases"] + script["display"]
                 + script["paragraph"])
        for style in ("Regular", "Bold"):
            font = load(path(script["stem"], style))
            for aper in (0, 50, 100):
                font.set_variations({"APER": aper})
                for text in cases:
                    seq = shape(font, text)
                    if not seq or any(name == ".notdef" for name, _ in seq):
                        fail(f"{key} {style} APER {aper}: {text!r} -> {seq}")
            font.set_variations({"APER": 0})
            seq0 = [shape(font, t) for t in cases]
            font.set_variations({"APER": 100})
            seq100 = [shape(font, t) for t in cases]
            if seq0 != seq100:
                fail(f"{key} {style}: shaping/advances changed across APER")
    print("PASS shaping across APER (glyph sequences and advances)")


def test_coverage():
    for key, script in SCRIPTS.items():
        base = TTFont(script["donor"])
        base_cmap = {
            cp for table in base["cmap"].tables if table.isUnicode()
            for cp in table.cmap
            if any(lo <= cp <= hi for lo, hi in script["ranges"])
        }
        derived = TTFont(path(script["stem"], "Regular"))
        cmap = derived.getBestCmap()
        missing = sorted(cp for cp in base_cmap if cp not in cmap)
        if missing:
            fail(f"{key}: missing cmap codepoints {missing[:10]}")
        hb_font = load(path(script["stem"], "Regular"))
        hb_font.set_variations({"APER": 100})
        carrier = {
            "devanagari": "क", "tamil": "க", "telugu": "క",
            "kannada": "ಕ",
        }[key]
        bad = []
        for cp in sorted(base_cmap):
            ch = chr(cp)
            try:
                category = unicodedata.category(ch)
            except ValueError:
                category = "Lo"
            text = carrier + ch if category.startswith("M") else ch
            seq = shape(hb_font, text)
            if not seq or any(name == ".notdef" for name, _ in seq):
                bad.append(hex(cp))
        if bad:
            fail(f"{key}: unshaped codepoints {bad[:10]}")
        print(f"  {key}: {len(base_cmap)} codepoints, {len(cmap)} cmap entries")
    print("PASS coverage")


# ---------------------------------------------------------------------------
# outlines
# ---------------------------------------------------------------------------
def test_outline_variation():
    for key, script in SCRIPTS.items():
        reg = path(script["stem"], "Regular")
        cmap = TTFont(reg).getBestCmap()
        changed = None
        for ch in "".join(script["display"] + script["cases"]):
            gname = cmap.get(ord(ch))
            if gname is None:
                continue
            if outline(reg, gname, 0) != outline(reg, gname, 100):
                changed = ch
                break
        if changed is None:
            fail(f"{key}: no outline variation found")
        else:
            print(f"  {key}: {changed} changes across APER")
        # Latin must stay untouched in the script families
        latin = cmap.get(ord("H"))
        if latin and outline(reg, latin, 0) != outline(reg, latin, 100):
            fail(f"{key}: Latin H was warped")
    print("PASS outline variation (script glyphs change, Latin stays put)")


def test_static_instances():
    for key, script in SCRIPTS.items():
        stem = script["stem"]
        cases = [
            (path(stem, "Round"), f"{script['family']} Round", "Regular"),
            (path(stem, "Petal"), f"{script['family']} Petal", "Regular"),
            (path(stem, "BoldPetal"), f"{script['family']} Petal", "Bold"),
        ]
        for p, family, style in cases:
            font = TTFont(p)
            if "fvar" in font:
                fail(f"{os.path.basename(p)}: still variable")
            if font["name"].getDebugName(1) != family:
                fail(f"{os.path.basename(p)}: family {font['name'].getDebugName(1)!r}")
            if font["name"].getDebugName(2) != style:
                fail(f"{os.path.basename(p)}: style {font['name'].getDebugName(2)!r}")
        cmap = TTFont(path(stem, "Regular")).getBestCmap()
        gname = cmap.get(ord(script["display"][0][0]))
        if gname:
            round_font = TTFont(path(stem, "Round"))
            petal_font = TTFont(path(stem, "Petal"))
            p0 = DecomposingRecordingPen(round_font.getGlyphSet())
            p1 = DecomposingRecordingPen(petal_font.getGlyphSet())
            round_font["glyf"][gname].draw(p0, round_font["glyf"])
            petal_font["glyf"][gname].draw(p1, petal_font["glyf"])
            if p0.value == p1.value:
                fail(f"{key}: static Round and Petal are identical")
    print("PASS static instances")


# ---------------------------------------------------------------------------
# colour
# ---------------------------------------------------------------------------
def test_color():
    for key, script in SCRIPTS.items():
        for style in ("SpectrumRegular", "Spectrum"):
            p = path(script["stem"], style)
            font = TTFont(p)
            if "COLR" not in font or "CPAL" not in font:
                fail(f"{os.path.basename(p)}: missing COLR/CPAL")
                continue
            if font["COLR"].version != 1:
                fail(f"{os.path.basename(p)}: COLR version {font['COLR'].version}")
            palette = font["CPAL"].palettes[0]
            if len(palette) < 2:
                fail(f"{os.path.basename(p)}: CPAL palette too small")
            records = font["COLR"].table.BaseGlyphList.BaseGlyphPaintRecord
            if len(records) < font["maxp"].numGlyphs - 10:
                fail(f"{os.path.basename(p)}: only {len(records)} colour glyphs")
            ok = 0
            for rec in records[:50]:
                paint = rec.Paint
                if paint.Format != 10:  # PaintGlyph
                    continue
                if paint.Paint.Format != 4:  # PaintLinearGradient
                    continue
                if paint.Paint.ColorLine.ColorStop:
                    ok += 1
            if ok < 40:
                fail(f"{os.path.basename(p)}: paint graph {ok}/50")
    print("PASS COLRv1 / CPAL spectrum")


def main():
    test_axes()
    test_metadata()
    test_manjari_base()
    test_shaping()
    test_coverage()
    test_outline_variation()
    test_static_instances()
    test_color()
    print()
    if FAILS:
        print(f"{len(FAILS)} failure(s)")
        sys.exit(1)
    print("all multiscript tests passed")


if __name__ == "__main__":
    main()

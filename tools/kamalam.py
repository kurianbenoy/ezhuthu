#!/usr/bin/env python3
"""Ezhuthu Kamalam — the aperture-variable Malayalam display family.

Design idea
-----------
Every Malayalam loop/arch is treated as a *gateway*: a round base that rises
to a soft lotus-petal crown.  The transformation is parametric and applied to
a proven open-source Malayalam skeleton (Manjari by Santhosh Thottingal /
SMC, OFL-1.1).  It is exposed as the ``APER`` (Aperture) variation axis:

    APER 0    classic round Manjari-derived forms
    APER 100  the full petal / gateway display cut (default)

The same outlines are then given a COLRv1 blue→orange spectrum in the
``Ezhuthu Kamalam Spectrum`` build, referencing Sarvam's visual language
without copying its wordmark.

All masters are point-compatible: the warp only moves existing TrueType
points, so varLib can interpolate between them cleanly.
"""
from __future__ import annotations

import argparse
import copy
import math
import os
import sys

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    SourceDescriptor,
)
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib import build as varlib_build
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.colorLib.builder import buildCOLR, buildCPAL
from fontTools.ttLib.tables import otTables as ot
from fontTools.otlLib.builder import buildStatTable
from scipy.spatial import cKDTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "sources", "base")
MASTERS = os.path.join(ROOT, "sources", "masters")
FONTS = os.path.join(ROOT, "fonts")
PROOFS = os.path.join(ROOT, "proofs")

UPEM = 1000

# Design constants (in 1000-unit em)
HOLE_BUMP = 110.0       # how far a counter crown rises at APER=100
PEAK_BUMP = 40.0        # how far an outer contour crown rises
SIGMA_F = 0.28          # width of the peak-sharpening field
PINCH = 0.055           # horizontal pinch at the crown
CAP_FRAC = 0.55         # max counter movement as a fraction of local stroke


# ---------------------------------------------------------------------------
# geometry helpers
# ---------------------------------------------------------------------------
def contour_area(pts):
    a = 0.0
    for j in range(len(pts)):
        x0, y0 = pts[j]
        x1, y1 = pts[(j + 1) % len(pts)]
        a += x0 * y1 - x1 * y0
    return a / 2.0


def _split_contours(glyph):
    start = 0
    contours = []
    for end in glyph.endPtsOfContours:
        contours.append((start, end))
        start = end + 1
    return contours


# ---------------------------------------------------------------------------
# the petal warp
# ---------------------------------------------------------------------------
def petal_warp(font: TTFont, hole_bump=HOLE_BUMP, peak_bump=PEAK_BUMP,
               sigma_f=SIGMA_F, pinch=PINCH, cap_frac=CAP_FRAC):
    """Move counters and outer crowns into lotus-petal shapes.

    The operation is point-preserving: only coordinates change, so two
    masters warped with different parameters remain interpolation-compatible.
    """
    glyf = font["glyf"]
    for gname in font.getGlyphOrder():
        if gname not in glyf:
            continue
        glyph = glyf[gname]
        if glyph.numberOfContours <= 0:
            continue
        coords = glyph.coordinates
        new = copy.deepcopy(coords)
        contours = _split_contours(glyph)
        allpts = [coords[i] for i in range(len(coords))]
        gymin = min(p[1] for p in allpts)
        gymax = max(p[1] for p in allpts)
        gh = max(1.0, gymax - gymin)

        # All outer-contour points, used to cap counter movement so a petal
        # can never break through the stroke.
        outer_pts = []
        for s, e in contours:
            pts = [coords[i] for i in range(s, e + 1)]
            if contour_area(pts) < 0:
                outer_pts.extend(pts)
        tree = cKDTree(outer_pts) if outer_pts else None

        for s, e in contours:
            pts = [coords[i] for i in range(s, e + 1)]
            ar = contour_area(pts)
            xmin = min(p[0] for p in pts)
            xmax = max(p[0] for p in pts)
            ymin = min(p[1] for p in pts)
            ymax = max(p[1] for p in pts)
            cx = (xmin + xmax) / 2.0
            w = max(1.0, (xmax - xmin) / 2.0)
            h = ymax - ymin

            if ar > 0:  # counter
                if h <= 20 or w <= 20 or tree is None:
                    continue
                for i in range(s, e + 1):
                    x, y = coords[i]
                    u = (x - cx) / w
                    v = (y - ymin) / h
                    if v <= 0.45:
                        continue
                    t = (v - 0.45) / 0.55
                    dist = tree.query((x, y))[0]
                    bump = min(hole_bump, cap_frac * dist)
                    pin = min(pinch * w, 0.30 * dist)
                    new[i] = (x - pin * u * t * t,
                              y + bump * (1.0 - u * u) * t * t)
            else:  # outer contour: sharpen local crowns
                n = len(pts)
                peaks = []
                for j in range(n):
                    y0 = pts[(j - 1) % n][1]
                    y1 = pts[j][1]
                    y2 = pts[(j + 1) % n][1]
                    if y1 >= y0 and y1 >= y2 and y1 > gymin + 0.45 * gh:
                        if (not peaks or
                                abs(pts[j][0] - peaks[-1][0]) > 0.15 * (xmax - xmin)):
                            peaks.append((pts[j][0], y1))
                for px, py in peaks:
                    sigma = max(30.0, (xmax - xmin) * sigma_f)
                    for i in range(s, e + 1):
                        x, y = coords[i]
                        wy = max(0.0, (y - (gymin + 0.35 * gh)) / (gh * 0.65))
                        wy = min(1.0, wy)
                        d = (x - px) / sigma
                        pull = math.exp(-d * d) * (wy * wy)
                        new[i] = (new[i][0] - 0.5 * pinch * (x - px) * math.exp(-d * d) * wy,
                                  new[i][1] + peak_bump * pull)
        glyph.coordinates = new
        glyph.recalcBounds(glyf)


# ---------------------------------------------------------------------------
# font metadata
# ---------------------------------------------------------------------------
def set_names(font: TTFont, family, style, full=None, ps=None,
              weight=400, copyright_note=None, version="Version 1.000"):
    full = full or f"{family} {style}"
    ps = ps or f"{family.replace(' ', '')}-{style.replace(' ', '')}"
    copyright_note = copyright_note or (
        "Copyright 2026 The Ezhuthu Project Authors. "
        "Based on Manjari, Copyright 2018 The Manjari Project Authors "
        "(https://gitlab.com/smc/fonts/manjari, OFL-1.1)."
    )
    name = font["name"]
    # Keep name IDs >= 256: those are the fvar/STAT axis and instance names
    # created by varLib.  Only the classic IDs are rewritten.
    name.names = [n for n in name.names if n.nameID >= 256]
    records = {
        0: copyright_note,
        1: family,
        2: style,
        3: f"{ps};{version};EZHX",
        4: full,
        5: version,
        6: ps,
        8: "Ezhuthu Project Authors",
        9: "Ezhuthu Project Authors; base design by Santhosh Thottingal (SMC)",
        11: "https://example.invalid/ezhuthu",
        12: "https://example.invalid/ezhuthu",
        13: "This Font Software is licensed under the SIL Open Font License, "
            "Version 1.1. This license is available with a FAQ at: "
            "https://scripts.sil.org/OFL",
        14: "https://scripts.sil.org/OFL",
        16: family,
        17: style,
        21: family,
        22: style,
        25: ps.split("-")[0],  # Variations PostScript Name Prefix
    }
    for nid, value in records.items():
        name.setName(value, nid, 3, 1, 0x409)  # Windows Unicode English
        name.setName(value, nid, 1, 0, 0)      # Mac Roman
    # Remove legacy names that could conflict with Manjari
    for nid in (18, 19, 20):
        name.removeNames(nameID=nid)


def set_metrics(font: TTFont, weight=400):
    os2 = font["OS/2"]
    hhea = font["hhea"]
    head = font["head"]
    asc, desc = 800, -300
    os2.sTypoAscender = asc
    os2.sTypoDescender = desc
    os2.sTypoLineGap = 0
    # Win metrics must cover the real glyph extents (-614 .. 1075) so
    # descenders and tall marks are never clipped by legacy rasterizers.
    os2.usWinAscent = 1100
    os2.usWinDescent = 700
    os2.usWeightClass = weight
    os2.achVendID = "EZHX"
    os2.fsSelection = (os2.fsSelection & ~0x21) | (0x20 if weight >= 700 else 0x40)
    os2.fsSelection |= 0x80  # USE_TYPO_METRICS
    hhea.ascent = asc
    hhea.descent = desc
    hhea.lineGap = 0
    head.macStyle = 1 if weight >= 700 else 0
    # neutral, upright font
    font["post"].italicAngle = 0.0
    font["post"].underlinePosition = -100
    font["post"].underlineThickness = 50
    font["post"].isFixedPitch = 0


def normalize(src, dst, petal=False, weight=400, family="Ezhuthu Kamalam",
              style="Regular", **warp_kwargs):
    font = TTFont(src)
    scale_upem(font, UPEM)
    for tag in ("prep", "fpgm", "cvt ", "VDMX", "hdmx", "LTSH"):
        if tag in font:
            del font[tag]
    if petal:
        petal_warp(font, **warp_kwargs)
    set_metrics(font, weight=weight)
    set_names(font, family, style, weight=weight)
    font.save(dst)
    return font


# ---------------------------------------------------------------------------
# variable font
# ---------------------------------------------------------------------------
def build_designspace(round_path, petal_path, out_path,
                      family="Ezhuthu Kamalam", style="Regular"):
    ds = DesignSpaceDocument()
    axis = AxisDescriptor()
    axis.name = "Aperture"
    axis.tag = "APER"
    axis.minimum = 0
    axis.default = 100
    axis.maximum = 100
    ds.addAxis(axis)

    for path, loc in [(petal_path, 100), (round_path, 0)]:
        src = SourceDescriptor()
        src.path = path
        src.name = os.path.basename(path)
        src.familyName = family
        src.styleName = style
        src.location = {"Aperture": loc}
        if loc == 100:
            src.copyInfo = True
            src.copyLib = True
            src.copyGroups = True
            src.copyFeatures = True
        ds.addSource(src)

    for name, loc, sub in [
        ("Round", 0, "Round"),
        ("Bloom", 50, "Bloom"),
        ("Petal", 100, "Regular"),
    ]:
        inst = InstanceDescriptor()
        inst.familyName = family
        inst.styleName = sub
        inst.name = name
        inst.location = {"Aperture": loc}
        ds.addInstance(inst)

    ds.write(out_path)
    return ds


def build_vf(designspace_path, out_path, family="Ezhuthu Kamalam", style="Regular"):
    ds = DesignSpaceDocument.fromfile(designspace_path)
    vf, _, _ = varlib_build(ds)
    set_metrics(vf, weight=700 if style == "Bold" else 400)
    set_names(vf, family, style, weight=700 if style == "Bold" else 400)
    # A clear STAT table for the custom axis
    buildStatTable(
        vf,
        axes=[dict(
            tag="APER",
            name="Aperture",
            ordering=0,
            values=[
                dict(value=0, name="Round", flags=0x2),
                dict(value=50, name="Bloom"),
                dict(value=100, name="Petal"),
            ],
        )],
        elidedFallbackName="Regular",
    )
    vf.save(out_path)
    return vf


# ---------------------------------------------------------------------------
# COLRv1 spectrum
# ---------------------------------------------------------------------------
SPECTRUM = [
    (0.00, (0.09, 0.13, 0.42, 1.0)),   # deep indigo
    (0.20, (0.16, 0.25, 0.70, 1.0)),   # blue
    (0.40, (0.35, 0.38, 0.86, 1.0)),   # periwinkle
    (0.58, (0.63, 0.42, 0.82, 1.0)),   # violet
    (0.74, (0.85, 0.45, 0.55, 1.0)),   # pink
    (0.88, (0.93, 0.47, 0.27, 1.0)),   # Sarvam orange
    (1.00, (0.98, 0.76, 0.42, 1.0)),   # warm gold
]


def add_spectrum(src, dst, family="Ezhuthu Kamalam Spectrum",
                 style="Bold", y_top=620, y_bottom=-120):
    font = TTFont(src)
    glyph_map = font.getReverseGlyphMap()
    glyf = font["glyf"]
    palette = [color for _, color in SPECTRUM]

    stops = []
    for off, _ in SPECTRUM:
        stops.append({
            "StopOffset": off,
            "PaletteIndex": len(stops),
            "Alpha": 1.0,
        })

    color_glyphs = {}
    for gname in font.getGlyphOrder():
        if gname not in glyf:
            continue
        g = glyf[gname]
        if g.numberOfContours == 0:
            continue
        color_glyphs[gname] = {
            "Format": int(ot.PaintFormat.PaintGlyph),
            "Glyph": gname,
            "Paint": {
                "Format": int(ot.PaintFormat.PaintLinearGradient),
                "ColorLine": {
                    "Extend": 0,   # PAD
                    "ColorStop": stops,
                },
                "x0": 0, "y0": y_top,
                "x1": 0, "y1": y_bottom,
                "x2": 500, "y2": y_top,
            },
        }

    colr = buildCOLR(color_glyphs, version=1, glyphMap=glyph_map)
    font["COLR"] = colr
    font["CPAL"] = buildCPAL([palette], nameTable=font["name"])
    set_names(font, family, style, weight=700)
    font.save(dst)
    return font


# ---------------------------------------------------------------------------
# instances / proof helpers
# ---------------------------------------------------------------------------
def instantiate(src, dst, location):
    font = TTFont(src)
    instantiateVariableFont(font, location, inplace=True)
    font.save(dst)
    return font


def instantiate_with_names(src, dst, location, family, style):
    font = TTFont(src)
    instantiateVariableFont(font, location, inplace=True)
    # drop variation tables left over from the instancer
    for tag in ("fvar", "gvar", "STAT", "avar", "HVAR"):
        if tag in font:
            del font[tag]
    set_names(font, family, style, weight=700 if "Bold" in style else 400)
    font.save(dst)
    return font


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", nargs="?", default="all",
                    choices=["masters", "variable", "spectrum", "instances", "all"])
    ap.add_argument("--proof", action="store_true",
                    help="also render proof PNGs (slow)")
    args = ap.parse_args(argv)

    os.makedirs(MASTERS, exist_ok=True)
    os.makedirs(FONTS, exist_ok=True)
    os.makedirs(PROOFS, exist_ok=True)

    reg_round = os.path.join(MASTERS, "Kamalam-Regular-Round.ttf")
    reg_petal = os.path.join(MASTERS, "Kamalam-Regular-Petal.ttf")
    bold_round = os.path.join(MASTERS, "Kamalam-Bold-Round.ttf")
    bold_petal = os.path.join(MASTERS, "Kamalam-Bold-Petal.ttf")

    if args.command in ("masters", "all"):
        normalize(os.path.join(BASE, "Manjari-Regular.ttf"), reg_round,
                  petal=False, weight=400, style="Regular")
        normalize(os.path.join(BASE, "Manjari-Regular.ttf"), reg_petal,
                  petal=True, weight=400, style="Regular")
        normalize(os.path.join(BASE, "Manjari-Bold.ttf"), bold_round,
                  petal=False, weight=700, style="Bold")
        normalize(os.path.join(BASE, "Manjari-Bold.ttf"), bold_petal,
                  petal=True, weight=700, style="Bold")
        print("masters written to", MASTERS)

    reg_ds = os.path.join(MASTERS, "Kamalam-Regular.designspace")
    bold_ds = os.path.join(MASTERS, "Kamalam-Bold.designspace")
    if args.command in ("variable", "all"):
        build_designspace(reg_round, reg_petal, reg_ds, style="Regular")
        build_designspace(bold_round, bold_petal, bold_ds, style="Bold")
        reg_vf = os.path.join(FONTS, "EzhuthuKamalam-Regular.ttf")
        bold_vf = os.path.join(FONTS, "EzhuthuKamalam-Bold.ttf")
        build_vf(reg_ds, reg_vf, style="Regular")
        build_vf(bold_ds, bold_vf, style="Bold")
        print("variable fonts written to", FONTS)

    if args.command in ("spectrum", "all"):
        bold_vf = os.path.join(FONTS, "EzhuthuKamalam-Bold.ttf")
        spectrum = os.path.join(FONTS, "EzhuthuKamalam-Spectrum.ttf")
        add_spectrum(bold_vf, spectrum)
        print("spectrum written to", spectrum)

    if args.command in ("instances", "all"):
        reg_vf = os.path.join(FONTS, "EzhuthuKamalam-Regular.ttf")
        bold_vf = os.path.join(FONTS, "EzhuthuKamalam-Bold.ttf")
        instantiate_with_names(reg_vf, os.path.join(FONTS, "EzhuthuKamalam-Round.ttf"),
                               {"APER": 0}, "Ezhuthu Kamalam Round", "Regular")
        instantiate_with_names(reg_vf, os.path.join(FONTS, "EzhuthuKamalam-Petal.ttf"),
                               {"APER": 100}, "Ezhuthu Kamalam Petal", "Regular")
        instantiate_with_names(bold_vf, os.path.join(FONTS, "EzhuthuKamalam-BoldPetal.ttf"),
                               {"APER": 100}, "Ezhuthu Kamalam Petal", "Bold")
        print("static instances written")

    # WOFF2 for every TTF in fonts/ root
    for fn in sorted(os.listdir(FONTS)):
        if not fn.endswith(".ttf"):
            continue
        src = os.path.join(FONTS, fn)
        dst = src[:-4] + ".woff2"
        tt = TTFont(src)
        tt.flavor = "woff2"
        tt.save(dst)
        print("woff2", dst)


if __name__ == "__main__":
    main()

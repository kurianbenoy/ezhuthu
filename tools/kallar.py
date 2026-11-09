#!/usr/bin/env python3
"""Kallar — the aperture-variable Malayalam display family.

Design idea
-----------
Every Malayalam loop/arch is treated as a *gateway*: a round base that rises
to a soft lotus-petal crown.  The transformation is parametric and applied to
a proven open-source Malayalam skeleton (Manjari by Santhosh Thottingal /
SMC, OFL-1.1).  It is exposed as the ``APER`` (Aperture) variation axis:

    APER 0    classic round Manjari-derived forms
    APER 100  the full petal / gateway display cut (default)

The same outlines are then given a COLRv1 blue→orange spectrum in the
``Kallar Spectrum`` build, referencing Sarvam's visual language
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

# Reproducible builds: freeze the head timestamps so repeated builds are
# byte-identical unless the design actually changes.
from fontTools.misc.timeTools import timestampFromString  # noqa: E402
FIXED_TIME = timestampFromString("Mon Nov  9 00:00:00 2026")

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
               sigma_f=SIGMA_F, pinch=PINCH, cap_frac=CAP_FRAC,
               only=None, freeze_top=None, peak_max_frac=None,
               freeze_above=None, peak_max_y=None, freeze_fade=None,
               valley_bump=0.0):
    """Move counters and outer crowns into lotus-petal shapes.

    The operation is point-preserving: only coordinates change, so two
    masters warped with different parameters remain interpolation-compatible.

    ``only`` restricts the transform to a set of glyph names.  ``freeze_top``
    is a fraction of the glyph height and ``freeze_above`` an absolute y:
    points above that line do not move, which keeps a headline (Devanagari
    shirorekha) perfectly straight.  ``freeze_fade`` softens the transition
    over that many units below the freeze line.  ``peak_max_frac`` /
    ``peak_max_y`` limit outer-contour peak candidates to below that height.
    ``valley_bump`` optionally pulls rounded lower loops into downward petals.
    """
    glyf = font["glyf"]
    for gname in font.getGlyphOrder():
        if only is not None and gname not in only:
            continue
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
        freeze_y = None
        if freeze_above is not None:
            freeze_y = freeze_above
        elif freeze_top is not None:
            freeze_y = gymin + freeze_top * gh
        peak_y = None
        if peak_max_y is not None:
            peak_y = peak_max_y
        elif peak_max_frac is not None:
            peak_y = gymin + peak_max_frac * gh

        def move_weight(y):
            """Smooth 0..1 falloff below the freeze line."""
            if freeze_y is None:
                return 1.0
            if y > freeze_y:
                return 0.0
            if not freeze_fade:
                return 1.0
            return min(1.0, (freeze_y - y) / freeze_fade)

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
                    weight = move_weight(y)
                    if weight <= 0:
                        continue
                    u = (x - cx) / w
                    v = (y - ymin) / h
                    if v <= 0.45:
                        continue
                    t = (v - 0.45) / 0.55
                    dist = tree.query((x, y))[0]
                    bump = min(hole_bump, cap_frac * dist) * weight
                    pin = min(pinch * w, 0.30 * dist) * weight
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
                        if peak_y is not None and y1 > peak_y:
                            continue
                        if (not peaks or
                                abs(pts[j][0] - peaks[-1][0]) > 0.15 * (xmax - xmin)):
                            peaks.append((pts[j][0], y1))
                for px, py in peaks:
                    sigma = max(30.0, (xmax - xmin) * sigma_f)
                    for i in range(s, e + 1):
                        x, y = coords[i]
                        weight = move_weight(y)
                        if weight <= 0:
                            continue
                        wy = max(0.0, (y - (gymin + 0.35 * gh)) / (gh * 0.65))
                        wy = min(1.0, wy)
                        d = (x - px) / sigma
                        pull = math.exp(-d * d) * (wy * wy)
                        new[i] = (new[i][0] - 0.5 * pinch * (x - px) *
                                  math.exp(-d * d) * wy * weight,
                                  new[i][1] + peak_bump * pull * weight)

                if valley_bump:
                    valleys = []
                    for j in range(n):
                        y0 = pts[(j - 1) % n][1]
                        y1 = pts[j][1]
                        y2 = pts[(j + 1) % n][1]
                        if y1 < y0 and y1 < y2 and y1 < gymin + 0.55 * gh:
                            if (not valleys or
                                    abs(pts[j][0] - valleys[-1][0]) >
                                    0.15 * (xmax - xmin)):
                                valleys.append((pts[j][0], y1))
                    for px, py in valleys:
                        sigma = max(30.0, (xmax - xmin) * sigma_f)
                        for i in range(s, e + 1):
                            x, y = coords[i]
                            weight = move_weight(y)
                            if weight <= 0:
                                continue
                            wy = max(0.0, (gymin + 0.55 * gh - y) / (0.55 * gh))
                            wy = min(1.0, wy)
                            d = (x - px) / sigma
                            pull = math.exp(-d * d) * (wy * wy)
                            new[i] = (new[i][0] - 0.5 * pinch * (x - px) *
                                      math.exp(-d * d) * wy * weight,
                                      new[i][1] - valley_bump * pull * weight)
        glyph.coordinates = new
        glyph.recalcBounds(glyf)


# ---------------------------------------------------------------------------
# font metadata
# ---------------------------------------------------------------------------
def set_names(font: TTFont, family, style, full=None, ps=None,
              weight=400, copyright_note=None, version="Version 1.100",
              designer=None, url=None):
    full = full or f"{family} {style}"
    ps = ps or f"{family.replace(' ', '')}-{style.replace(' ', '')}"
    copyright_note = copyright_note or (
        "Copyright 2026 The Kallar Project Authors. "
        "Based on Manjari, Copyright 2018 The Manjari Project Authors "
        "(https://gitlab.com/smc/fonts/manjari, OFL-1.1)."
    )
    designer = designer or (
        "Kallar Project Authors; base design by Santhosh Thottingal (SMC)"
    )
    url = url or "https://github.com/kurianbenoy/kallar"
    name = font["name"]
    # Keep name IDs >= 256: those are the fvar/STAT axis and instance names
    # created by varLib.  Only the classic IDs are rewritten.
    name.names = [n for n in name.names if n.nameID >= 256]
    records = {
        0: copyright_note,
        1: family,
        2: style,
        3: f"{ps};{version};KLLR",
        4: full,
        5: version,
        6: ps,
        8: "Kallar Project Authors",
        9: designer,
        11: url,
        12: url,
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
    # Remove Mac-platform records: modern fonts only need the Windows set,
    # and duplicate Mac names make font QA noisy.
    name.names = [n for n in name.names if n.platformID != 1]
    # Remove legacy names that could conflict with Manjari
    for nid in (18, 19, 20):
        name.removeNames(nameID=nid)


def set_metrics(font: TTFont, weight=400, asc=None, desc=None,
                win_asc=None, win_desc=None, auto_win=False,
                underline_position=None, underline_thickness=None):
    os2 = font["OS/2"]
    hhea = font["hhea"]
    head = font["head"]
    head.fontRevision = 1.1
    head.created = FIXED_TIME
    head.modified = FIXED_TIME
    # Minimal smart-dropout prep.  The font has no TT hinting otherwise;
    # this keeps legacy rasterizers on the smart-dropout path.
    from fontTools.ttLib.tables import ttProgram
    from fontTools.ttLib import newTable
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromBytecode(bytes([
        0xB8, 0x01, 0xFF, 0x85,  # PUSHW 0x01FF; SCANCTRL
        0xB0, 0x04, 0x8D,        # PUSHB 0x04; SCANTYPE
    ]))
    font["prep"] = prep
    asc = 800 if asc is None else asc
    desc = -300 if desc is None else desc
    if auto_win:
        glyf = font["glyf"]
        extents = []
        for gname in font.getGlyphOrder():
            if gname not in glyf:
                continue
            g = glyf[gname]
            if getattr(g, "numberOfContours", 0) == 0:
                continue
            extents.append((g.yMin, g.yMax))
        ymin = min(e[0] for e in extents)
        ymax = max(e[1] for e in extents)
        win_asc = max(asc, int(math.ceil(ymax)) + 50)
        win_desc = max(-desc, int(math.ceil(-ymin)) + 50)
    else:
        win_asc = 1100 if win_asc is None else win_asc
        win_desc = 700 if win_desc is None else win_desc
    os2.sTypoAscender = asc
    os2.sTypoDescender = desc
    os2.sTypoLineGap = 0
    os2.usWinAscent = win_asc
    os2.usWinDescent = win_desc
    os2.usWeightClass = weight
    os2.achVendID = "KLLR"
    # bit 0 = italic, bit 5 = bold, bit 6 = regular.  The base fonts differ in
    # which of these they set, so clear all three before setting the style bit.
    os2.fsSelection = (os2.fsSelection & ~0x61) | (0x20 if weight >= 700 else 0x40)
    os2.fsSelection |= 0x80  # USE_TYPO_METRICS
    hhea.ascent = asc
    hhea.descent = desc
    hhea.lineGap = 0
    head.macStyle = 1 if weight >= 700 else 0
    # neutral, upright font
    font["post"].italicAngle = 0.0
    font["post"].underlinePosition = (
        -100 if underline_position is None else underline_position
    )
    font["post"].underlineThickness = (
        50 if underline_thickness is None else underline_thickness
    )
    font["post"].isFixedPitch = 0


def add_case_pairs(font: TTFont):
    """Add the two Latin case pairs Manjari omits (ď, Ǒ).

    Manjari has Ď and ǒ but not their lower/upper counterparts.  A composite
    is enough: the base letter plus a combining caron.  The spacing U+02C7
    caron is cloned into a zero-width U+030C mark so the precomposed letters
    use a proper mark component.
    """
    glyf = font["glyf"]
    if "Dcaron" not in glyf or "caron" not in glyf:
        return

    from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphComponent

    # A zero-width combining caron for U+030C and the precomposed letters.
    if "caroncomb" not in glyf:
        order = list(font.getGlyphOrder())
        mark = copy.deepcopy(glyf["caron"])
        glyf["caroncomb"] = mark
        if "caroncomb" not in order:
            order.append("caroncomb")
        font["hmtx"].metrics["caroncomb"] = (0, 0)
        font.setGlyphOrder(order)
        glyf.glyphOrder = order
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[0x030C] = "caroncomb"
        gdef = font.get("GDEF")
        if gdef is not None and getattr(gdef.table, "GlyphClassDef", None):
            gdef.table.GlyphClassDef.classDefs["caroncomb"] = 3  # mark

    # the offset used by Dcaron is already in the current UPM
    caron_offset = None
    for comp in glyf["Dcaron"].components:
        if comp.glyphName in ("caron", "caroncomb"):
            caron_offset = (comp.x, comp.y)
            comp.glyphName = "caroncomb"
            break
    for comp in glyf["ocaron"].components:
        if comp.glyphName in ("caron", "caroncomb"):
            comp.glyphName = "caroncomb"
            break
    if caron_offset is None:
        return

    for new_name, base, cp in (("dcaron", "d", 0x010F), ("Ocaron", "O", 0x01D1)):
        if new_name in glyf:
            continue
        order = list(font.getGlyphOrder())
        g = Glyph()
        g.numberOfContours = -1
        g.components = []
        for comp_name, x, y in ((base, 0, 0), ("caroncomb", *caron_offset)):
            c = GlyphComponent()
            c.flags = 0
            c.glyphName = comp_name
            c.x = x
            c.y = y
            g.components.append(c)
        g.recalcBounds(glyf)
        glyf[new_name] = g
        if new_name not in order:
            order.append(new_name)
        font["hmtx"].metrics[new_name] = font["hmtx"].metrics[base]
        font.setGlyphOrder(order)
        glyf.glyphOrder = order
        for table in font["cmap"].tables:
            if table.isUnicode():
                table.cmap[cp] = new_name
    font["maxp"].numGlyphs = len(font.getGlyphOrder())


def normalize(src, dst, petal=False, weight=400, family="Kallar",
              style="Regular", **warp_kwargs):
    font = TTFont(src)
    scale_upem(font, UPEM)
    for tag in ("prep", "fpgm", "cvt ", "VDMX", "hdmx", "LTSH"):
        if tag in font:
            del font[tag]
    if petal:
        petal_warp(font, **warp_kwargs)
    add_case_pairs(font)
    set_metrics(font, weight=weight)
    set_names(font, family, style, weight=weight)
    font.recalcTimestamp = False
    font.save(dst)
    return font


# ---------------------------------------------------------------------------
# variable font
# ---------------------------------------------------------------------------
def build_designspace(round_path, petal_path, out_path,
                      family="Kallar", style="Regular"):
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
        (style, 100, style),
    ]:
        inst = InstanceDescriptor()
        inst.familyName = family
        inst.styleName = sub
        inst.name = name
        inst.location = {"Aperture": loc}
        ds.addInstance(inst)

    ds.write(out_path)
    return ds


def build_vf(designspace_path, out_path, family="Kallar", style="Regular",
             metrics=None, copyright_note=None, designer=None, url=None,
             stat_values=None):
    ds = DesignSpaceDocument.fromfile(designspace_path)
    vf, _, _ = varlib_build(ds)
    set_metrics(vf, weight=700 if style == "Bold" else 400, **(metrics or {}))
    set_names(vf, family, style, weight=700 if style == "Bold" else 400,
              copyright_note=copyright_note, designer=designer, url=url)
    # A clear STAT table for the custom axis.  The default poetic names are
    # used by the Malayalam family; the multiscript build passes shorter
    # labels because the family name plus "Bloom"/"Petal" would exceed the
    # 31-character Windows limit.
    stat_values = stat_values or [
        dict(value=0, name="Round", flags=0x2),
        dict(value=50, name="Bloom"),
        dict(value=100, name="Petal"),
    ]
    buildStatTable(
        vf,
        axes=[dict(
            tag="APER",
            name="Aperture",
            ordering=0,
            values=stat_values,
        )],
        elidedFallbackName="Regular",
        macNames=False,
    )
    vf["name"].names = [n for n in vf["name"].names if n.platformID != 1]
    vf.recalcTimestamp = False
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


def add_spectrum(src, dst, family="Kallar Spectrum",
                 style="Bold", weight=700, y_top=620, y_bottom=-120,
                 copyright_note=None, designer=None, url=None):
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
    set_names(font, family, style, weight=weight,
              copyright_note=copyright_note, designer=designer, url=url)
    font["name"].names = [n for n in font["name"].names if n.platformID != 1]
    font.recalcTimestamp = False
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


def instantiate_with_names(src, dst, location, family, style,
                           copyright_note=None, designer=None, url=None):
    font = TTFont(src)
    instantiateVariableFont(font, location, inplace=True)
    # drop variation tables left over from the instancer
    for tag in ("fvar", "gvar", "STAT", "avar", "HVAR", "MVAR"):
        if tag in font:
            del font[tag]
    set_names(font, family, style, weight=700 if "Bold" in style else 400,
              copyright_note=copyright_note, designer=designer, url=url)
    font.recalcTimestamp = False
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

    reg_round = os.path.join(MASTERS, "Kallar-Regular-Round.ttf")
    reg_petal = os.path.join(MASTERS, "Kallar-Regular-Petal.ttf")
    bold_round = os.path.join(MASTERS, "Kallar-Bold-Round.ttf")
    bold_petal = os.path.join(MASTERS, "Kallar-Bold-Petal.ttf")

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

    reg_ds = os.path.join(MASTERS, "Kallar-Regular.designspace")
    bold_ds = os.path.join(MASTERS, "Kallar-Bold.designspace")
    if args.command in ("variable", "all"):
        build_designspace(reg_round, reg_petal, reg_ds, style="Regular")
        build_designspace(bold_round, bold_petal, bold_ds, style="Bold")
        reg_vf = os.path.join(FONTS, "Kallar-Regular.ttf")
        bold_vf = os.path.join(FONTS, "Kallar-Bold.ttf")
        build_vf(reg_ds, reg_vf, style="Regular")
        build_vf(bold_ds, bold_vf, style="Bold")
        print("variable fonts written to", FONTS)

    if args.command in ("spectrum", "all"):
        reg_vf = os.path.join(FONTS, "Kallar-Regular.ttf")
        bold_vf = os.path.join(FONTS, "Kallar-Bold.ttf")
        spectrum = os.path.join(FONTS, "Kallar-Spectrum.ttf")
        spectrum_reg = os.path.join(FONTS, "Kallar-SpectrumRegular.ttf")
        add_spectrum(bold_vf, spectrum, style="Bold", weight=700)
        add_spectrum(reg_vf, spectrum_reg, style="Regular", weight=400)
        print("spectrum written to", spectrum, spectrum_reg)

    if args.command in ("instances", "all"):
        reg_vf = os.path.join(FONTS, "Kallar-Regular.ttf")
        bold_vf = os.path.join(FONTS, "Kallar-Bold.ttf")
        instantiate_with_names(reg_vf, os.path.join(FONTS, "Kallar-Round.ttf"),
                               {"APER": 0}, "Kallar Round", "Regular")
        instantiate_with_names(reg_vf, os.path.join(FONTS, "Kallar-Petal.ttf"),
                               {"APER": 100}, "Kallar Petal", "Regular")
        instantiate_with_names(bold_vf, os.path.join(FONTS, "Kallar-BoldPetal.ttf"),
                               {"APER": 100}, "Kallar Petal", "Bold")
        print("static instances written")

    # WOFF2 for every TTF in fonts/ root
    for fn in sorted(os.listdir(FONTS)):
        if not fn.endswith(".ttf"):
            continue
        src = os.path.join(FONTS, fn)
        dst = src[:-4] + ".woff2"
        tt = TTFont(src)
        tt.flavor = "woff2"
        tt.recalcTimestamp = False
        tt.save(dst)
        print("woff2", dst)


if __name__ == "__main__":
    main()

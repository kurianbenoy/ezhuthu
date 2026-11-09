#!/usr/bin/env python3
"""Kallar multiscript — Manjari is the base of every family.

The whole Kallar system starts from the same **Manjari** skeleton.  Manjari
supplies the shared Latin, digits, punctuation, symbols, spacing, metrics and
design language of every family.  The Malayalam family is Manjari throughout.

Manjari is a Malayalam + Latin face, so it has no Devanagari, Tamil, Telugu or
Kannada outlines.  Those four families therefore use the corresponding Noto
Sans faces as **script donors**: the donor supplies only the script-specific
letter structures (and the GSUB/GPOS rules that shape them), while every
shared glyph is transplanted from Manjari.  The donor is instantiated at the
weight that matches Manjari's pen, so the script letters sit at the same
stroke weight as the Manjari base.

Each family is a separate variable font because the scripts have different
shaping tables, glyph sets and vertical metrics.  They share the APER axis
(0..100, default 100), the five named stops, the Spectrum palette and the
static Round/Petal instances, so they can be used together as one type system.

Usage:
    python tools/multiscript.py                 # all four scripts
    python tools/multiscript.py devanagari      # one script
    python tools/multiscript.py tamil telugu    # a subset

The build is deterministic: the base fonts are vendored, the timestamps are
pinned and the transform only moves existing TrueType points, so repeated runs
produce byte-identical files.
"""
from __future__ import annotations

import argparse
import copy
import os
import sys
from functools import lru_cache

from fontTools import subset
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kallar import (  # noqa: E402
    UPEM,
    add_case_pairs,
    add_spectrum,
    build_designspace,
    build_vf,
    instantiate_with_names,
    petal_warp,
    set_metrics,
    set_names,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "sources", "base")
DONORS = os.path.join(ROOT, "sources", "donors")
MASTERS = os.path.join(ROOT, "sources", "masters")
FONTS = os.path.join(ROOT, "fonts")
PROJECT_URL = "https://github.com/kurianbenoy/kallar"

MANJARI_REGULAR = os.path.join(BASE, "Manjari-Regular.ttf")
MANJARI_BOLD = os.path.join(BASE, "Manjari-Bold.ttf")

# Manjari's OS/2 x-height and cap-height, scaled from its 2048 UPM base.
MANJARI_X_HEIGHT = {400: 500, 700: 523}
MANJARI_CAP_HEIGHT = {400: 676, 700: 699}

# The Malayalam block.  Everything outside it is shared Latin / punctuation /
# symbols in Manjari and is transplanted into every script family.
MALAYALAM_RANGES = [(0x0D00, 0x0D7F)]

NOTO_DEVA = "https://github.com/notofonts/devanagari"
NOTO_TAML = "https://github.com/notofonts/tamil"
NOTO_TELU = "https://github.com/notofonts/telugu"
NOTO_KNDA = "https://github.com/notofonts/kannada"

SCRIPTS = {
    "devanagari": {
        "family": "Kallar Devanagari",
        "name": "कल्लार",
        "stem": "KallarDevanagari",
        "donor": os.path.join(DONORS, "NotoSansDevanagari-VF.ttf"),
        "donor_name": "Noto Sans Devanagari",
        "script_name": "Devanagari",
        "upstream": NOTO_DEVA,
        # Manjari Regular is ~73 units at 1000 UPM and Manjari Bold ~112.
        # The donor's variable axis is instantiated at the closest weight so
        # the script letters share Manjari's pen weight.
        "wght": {400: 360, 700: 550},
        "ranges": [(0x0900, 0x097F), (0xA8E0, 0xA8FF), (0x1CD0, 0x1CFF)],
        "warp": dict(hole_bump=110, peak_bump=60, freeze_above=545,
                     peak_max_y=545, freeze_fade=120, sigma_f=0.22,
                     pinch=0.055, cap_frac=0.55),
        "metrics": dict(asc=800, desc=-300, auto_win=True),
        "display": ["कमल", "द्वार", "नमस्ते"],
        "paragraph": [
            "सभी भाषाएँ सभी लोगों के लिए।",
            "एक लिपि। एक द्वार। एक लोक।",
        ],
        "cases": [
            "नमस्ते", "कमल", "द्वार", "श्री", "क्ष", "त्र", "ज्ञ",
            "संस्कृत", "हिन्दी", "भारत", "कर्म", "धर्म", "बुद्ध",
            "संसार", "कमलम्", "देवनागरी",
        ],
    },
    "tamil": {
        "family": "Kallar Tamil",
        "name": "கல்லார்",
        "stem": "KallarTamil",
        "donor": os.path.join(DONORS, "NotoSansTamil-VF.ttf"),
        "donor_name": "Noto Sans Tamil",
        "script_name": "Tamil",
        "upstream": NOTO_TAML,
        "wght": {400: 360, 700: 550},
        "ranges": [(0x0B80, 0x0BFF)],
        "warp": dict(hole_bump=100, peak_bump=25, freeze_top=0.82,
                     sigma_f=0.30, pinch=0.05, cap_frac=0.55),
        "metrics": dict(asc=800, desc=-300, auto_win=True),
        "display": ["தாமரை", "வாசல்", "வணக்கம்"],
        "paragraph": [
            "எல்லா மொழிகளும் எல்லா மக்களுக்கும்.",
            "ஒரு மொழி. ஒரு வாசல். ஒரு உலகம்.",
        ],
        "cases": [
            "வணக்கம்", "தாமரை", "வாசல்", "தமிழ்", "ஸ்ரீ", "க்ஷ",
            "ஞானம்", "அன்பு", "மனிதம்", "தமிழ்நாடு", "சென்னை",
            "கண்ணன்", "வீடு", "நன்றி",
        ],
    },
    "telugu": {
        "family": "Kallar Telugu",
        "name": "కల్లార్",
        "stem": "KallarTelugu",
        "donor": os.path.join(DONORS, "NotoSansTelugu-VF.ttf"),
        "donor_name": "Noto Sans Telugu",
        "script_name": "Telugu",
        "upstream": NOTO_TELU,
        # Telugu's base stem is heavier, so its donor is instantiated a
        # little lighter to land on the same Manjari weight.
        "wght": {400: 340, 700: 500},
        "ranges": [(0x0C00, 0x0C7F)],
        "warp": dict(hole_bump=110, peak_bump=40, sigma_f=0.28,
                     pinch=0.055, cap_frac=0.55),
        "metrics": dict(asc=800, desc=-300, auto_win=True),
        "display": ["కమలం", "ద్వారం", "నమస్కారం"],
        "paragraph": [
            "అన్ని భాషలు అందరికీ.",
            "ఒక భాష. ఒక ద్వారం. ఒక ప్రపంచం.",
        ],
        "cases": [
            "నమస్కారం", "కమలం", "ద్వారం", "శ్రీ", "క్ష", "జ్ఞానం",
            "తెలుగు", "భారతం", "సంస్కృతం", "కమల", "దేవత",
            "ప్రపంచం", "అమ్మ", "నాన్న",
        ],
    },
    "kannada": {
        "family": "Kallar Kannada",
        "name": "ಕಲ್ಲಾರ್",
        "stem": "KallarKannada",
        "donor": os.path.join(DONORS, "NotoSansKannada-VF.ttf"),
        "donor_name": "Noto Sans Kannada",
        "script_name": "Kannada",
        "upstream": NOTO_KNDA,
        "wght": {400: 360, 700: 550},
        "ranges": [(0x0C80, 0x0CFF)],
        "warp": dict(hole_bump=110, peak_bump=36, sigma_f=0.28,
                     pinch=0.055, cap_frac=0.55),
        "metrics": dict(asc=800, desc=-300, auto_win=True),
        "display": ["ಕಮಲ", "ದ್ವಾರ", "ನಮಸ್ಕಾರ"],
        "paragraph": [
            "ಎಲ್ಲಾ ಭಾಷೆಗಳು ಎಲ್ಲರಿಗೂ.",
            "ಒಂದು ಭಾಷೆ. ಒಂದು ದ್ವಾರ. ಒಂದು ಜಗತ್ತು.",
        ],
        "cases": [
            "ನಮಸ್ಕಾರ", "ಕಮಲ", "ದ್ವಾರ", "ಶ್ರೀ", "ಕ್ಷ", "ಜ್ಞಾನ",
            "ಕನ್ನಡ", "ಭಾರತ", "ಸಂಸ್ಕೃತ", "ಬೆಂಗಳೂರು", "ಕರ್ನಾಟಕ",
            "ಅಮ್ಮ", "ಅಪ್ಪ", "ನಮಸ್ಕಾರಂ",
        ],
    },
}

# Tables that cannot survive a change of outlines / instancing.
DROP_TABLES = (
    "fvar", "gvar", "avar", "STAT", "HVAR", "MVAR", "VVAR", "DSIG",
    "prep", "fpgm", "cvt ", "VDMX", "hdmx", "LTSH",
)


# ---------------------------------------------------------------------------
# Manjari base
# ---------------------------------------------------------------------------
def load_manjari(weight=400):
    """Load Manjari at the production UPM, without hinting or variations."""
    path = MANJARI_REGULAR if weight == 400 else MANJARI_BOLD
    font = TTFont(path)
    scale_upem(font, UPEM)
    for tag in DROP_TABLES:
        if tag in font:
            del font[tag]
    # Manjari lacks U+010F/U+01D1; the Malayalam build adds the same two
    # composites, so the shared Latin is complete in every family.
    add_case_pairs(font)
    return font


def unicode_cmap(font):
    cmap = {}
    for table in font["cmap"].tables:
        if table.isUnicode():
            cmap.update(table.cmap)
    return cmap


@lru_cache(maxsize=1)
def manjari_malayalam_glyphs():
    """The GSUB closure of Manjari's Malayalam codepoints.

    These glyphs are not transplanted into the sister families: each family
    carries its own script, and the Malayalam family is the Manjari family.
    """
    font = TTFont(MANJARI_REGULAR)
    codepoints = script_codepoints(font, MALAYALAM_RANGES)
    return frozenset(script_glyphs(MANJARI_REGULAR, codepoints))


@lru_cache(maxsize=1)
def manjari_shared_glyphs():
    """Glyphs transplanted from Manjari into the sister families."""
    malayalam = manjari_malayalam_glyphs()
    cmap = unicode_cmap(TTFont(MANJARI_REGULAR))
    return frozenset(
        name for cp, name in cmap.items()
        if not any(lo <= cp <= hi for lo, hi in MALAYALAM_RANGES)
        and name not in malayalam
    )


def transplant_manjari(manjari, donor, malayalam_glyphs):
    """Transplant Manjari's shared glyphs into a script donor.

    The donor is used as the shaping container: its glyph order, GSUB/GPOS,
    GDEF and script glyphs stay in place.  Every codepoint outside the
    Malayalam block that Manjari covers is remapped to a Manjari outline,
    using the donor's glyph name where one already exists so the donor's
    layout tables keep working.  Missing Manjari glyphs are appended under
    their Manjari names; composites are flattened so the result can never
    contain a nested component.
    """
    mglyphset = manjari.getGlyphSet()
    dglyf = donor["glyf"]
    mhmtx = manjari["hmtx"]
    dhmtx = donor["hmtx"]
    mcmap = unicode_cmap(manjari)
    dcmap = unicode_cmap(donor)

    order = list(donor.getGlyphOrder())
    names = set(order)
    copied = {}          # (manjari name, donor name) -> True
    dest_by_cp = {}      # codepoint -> donor glyph name

    def unique_name(name):
        if name not in names:
            return name
        i = 1
        while f"kallar.{name}.{i}" in names:
            i += 1
        return f"kallar.{name}.{i}"

    def copy_glyph(src, dst):
        if (src, dst) in copied:
            return
        copied[(src, dst)] = True
        # Flatten Manjari's composites.  The donor often has a composite
        # under the target name already, and a composite-of-a-composite
        # would trigger fontbakery's found-nested-components check.
        pen = DecomposingRecordingPen(mglyphset)
        mglyphset[src].draw(pen)
        ttpen = TTGlyphPen(None)
        pen.replay(ttpen)
        glyph = ttpen.glyph()
        glyph.recalcBounds(dglyf)
        dglyf[dst] = glyph
        dhmtx.metrics[dst] = mhmtx.metrics[src]
        if dst not in names:
            order.append(dst)
            names.add(dst)

    for cp, manjari_name in sorted(mcmap.items()):
        if any(lo <= cp <= hi for lo, hi in MALAYALAM_RANGES):
            continue
        if manjari_name in malayalam_glyphs:
            continue
        if cp in dcmap:
            dst = dcmap[cp]
        else:
            dst = unique_name(manjari_name)
        copy_glyph(manjari_name, dst)
        dest_by_cp[cp] = dst

    donor.setGlyphOrder(order)
    dglyf.glyphOrder = order
    donor["maxp"].numGlyphs = len(order)
    donor["maxp"].recalc(donor)

    # Rebuild the Unicode cmaps.  Only subtable formats that can represent
    # the codepoint are touched; format 14 is the variation-sequence table.
    for cp, dst in dest_by_cp.items():
        for table in donor["cmap"].tables:
            if not table.isUnicode() or table.format == 14:
                continue
            if table.format == 4 and cp > 0xFFFF:
                continue
            if table.format in (0, 6):
                continue
            table.cmap[cp] = dst

    # Keep GDEF classes for the transplanted glyphs.  This matters for
    # combining marks such as Manjari's zero-width caron.
    if "GDEF" in donor and "GDEF" in manjari:
        dgdef = donor["GDEF"].table
        mgdef = manjari["GDEF"].table
        dclasses = getattr(dgdef, "GlyphClassDef", None)
        mclasses = getattr(mgdef, "GlyphClassDef", None)
        if dclasses is not None and mclasses is not None:
            for (src, dst) in sorted(copied):
                cls = mclasses.classDefs.get(src)
                if cls is not None:
                    dclasses.classDefs[dst] = cls

    return donor


def merge_latin_kerning(manjari, donor):
    """Use Manjari's Latin kern lookups instead of the donor's.

    The shared Latin outlines and advances are Manjari's, so the donor's
    Latin kerning no longer matches them.  Append Manjari's `kern` lookups to
    the donor's GPOS and point the donor's `latn` language systems at the new
    feature.  The donor's script-specific GPOS is untouched.
    """
    if "GPOS" not in manjari or "GPOS" not in donor:
        return
    mgpos = manjari["GPOS"].table
    dgpos = donor["GPOS"].table

    manjari_latn = next(
        (rec for rec in mgpos.ScriptList.ScriptRecord
         if rec.ScriptTag == "latn"), None
    )
    if manjari_latn is None:
        return
    kern_features = [
        mgpos.FeatureList.FeatureRecord[i]
        for i in manjari_latn.Script.DefaultLangSys.FeatureIndex
        if mgpos.FeatureList.FeatureRecord[i].FeatureTag == "kern"
    ]
    if not kern_features:
        return

    donor_names = set(donor.getGlyphOrder())
    lookup_base = len(dgpos.LookupList.Lookup)
    manjari_lookups = []
    for record in kern_features:
        for lookup_index in record.Feature.LookupListIndex:
            lookup = mgpos.LookupList.Lookup[lookup_index]
            coverage = set()
            for subtable in lookup.SubTable:
                cov = getattr(subtable, "Coverage", None)
                if cov is not None:
                    coverage.update(cov.glyphs)
            # Manjari's kern feature contains a private `xx` helper lookup
            # that is not part of the shared Latin set.  Skip lookups whose
            # coverage is entirely absent from the donor.
            if coverage and not (coverage & donor_names):
                continue
            manjari_lookups.append(lookup)
    if not manjari_lookups:
        return
    imported = copy.deepcopy(manjari_lookups)
    reverse = donor.getReverseGlyphMap()
    for lookup in imported:
        for subtable in lookup.SubTable:
            coverage = getattr(subtable, "Coverage", None)
            if coverage is not None:
                coverage.glyphs.sort(
                    key=lambda name: reverse.get(name, len(reverse))
                )
    dgpos.LookupList.Lookup.extend(imported)

    donor_kern = {
        i for i, rec in enumerate(dgpos.FeatureList.FeatureRecord)
        if rec.FeatureTag == "kern"
    }
    new_feature = copy.deepcopy(kern_features[0].Feature)
    new_feature.LookupListIndex = list(
        range(lookup_base, lookup_base + len(manjari_lookups))
    )
    new_feature.LookupCount = len(new_feature.LookupListIndex)
    new_record = copy.deepcopy(kern_features[0])
    new_record.FeatureTag = "kern"
    new_record.Feature = new_feature
    dgpos.FeatureList.FeatureRecord.append(new_record)
    new_index = len(dgpos.FeatureList.FeatureRecord) - 1

    donor_latn = next(
        (rec for rec in dgpos.ScriptList.ScriptRecord
         if rec.ScriptTag == "latn"), None
    )
    if donor_latn is None:
        return

    def replace(feature_indices):
        return [new_index if i in donor_kern else i
                for i in feature_indices]

    langsys = donor_latn.Script
    if langsys.DefaultLangSys is not None:
        langsys.DefaultLangSys.FeatureIndex = replace(
            langsys.DefaultLangSys.FeatureIndex
        )
        langsys.DefaultLangSys.FeatureCount = len(
            langsys.DefaultLangSys.FeatureIndex
        )
    for record in (langsys.LangSysRecord or []):
        if record.LangSys is not None:
            record.LangSys.FeatureIndex = replace(
                record.LangSys.FeatureIndex
            )
            record.LangSys.FeatureCount = len(record.LangSys.FeatureIndex)


def instantiate_base(script, weight):
    out = os.path.join(
        MASTERS, f"{script['stem']}-{style_for(weight)}-Round.ttf"
    )
    manjari = load_manjari(weight)
    donor = TTFont(script["donor"])
    instantiateVariableFont(
        donor, {"wght": script["wght"][weight], "wdth": 100}, inplace=True
    )
    for tag in DROP_TABLES:
        if tag in donor:
            del donor[tag]
    scale_upem(donor, UPEM)
    font = transplant_manjari(manjari, donor, manjari_malayalam_glyphs())
    merge_latin_kerning(manjari, font)
    style = style_for(weight)
    set_names(
        font, script["family"], style, weight=weight,
        copyright_note=copyright_for(script),
        designer=designer_for(script),
        url=PROJECT_URL,
    )
    set_metrics(font, weight=weight, **script["metrics"])
    # The shared Latin is Manjari's, so its x-height and cap-height belong in
    # OS/2 even though the script donor has different values.
    font["OS/2"].sxHeight = MANJARI_X_HEIGHT[weight]
    font["OS/2"].sCapHeight = MANJARI_CAP_HEIGHT[weight]
    font.recalcTimestamp = False
    font.save(out)
    return out


# ---------------------------------------------------------------------------
# donor helpers
# ---------------------------------------------------------------------------
def script_codepoints(font, ranges):
    cps = set()
    for table in font["cmap"].tables:
        if not table.isUnicode():
            continue
        for cp in table.cmap:
            if any(lo <= cp <= hi for lo, hi in ranges):
                cps.add(cp)
    return cps


def script_glyphs(path, codepoints):
    """Return the GSUB closure of a script's codepoints.

    Using fontTools' subsetter closure means conjuncts, half forms, reph forms
    and contextual variants are all included, while Latin, punctuation and
    unrelated glyphs are left in Manjari's style.
    """
    font = TTFont(path)
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = False
    opts.drop_tables = []
    subsetter = subset.Subsetter(opts)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(font)
    names = set(font.getGlyphOrder())
    names.discard(".notdef")
    return names


def copyright_for(script):
    return (
        "Copyright 2026 The Kallar Project Authors. "
        "Base skeleton: Manjari, Copyright 2018 The Manjari Project Authors "
        "(https://gitlab.com/smc/fonts/manjari, OFL-1.1). "
        f"{script['script_name']} letter structures adapted from "
        f"{script['donor_name']}, Copyright 2022 The Noto Project Authors "
        f"({script['upstream']}, OFL-1.1)."
    )


def designer_for(script):
    return (
        "Kallar Project Authors; base design by Santhosh Thottingal (SMC); "
        f"{script['script_name']} letter structures adapted from the "
        "Noto Project Authors"
    )


def style_for(weight):
    return "Regular" if weight == 400 else "Bold"


def make_petal(round_path, petal_path, glyphs, warp):
    font = TTFont(round_path)
    petal_warp(font, only=glyphs, **warp)
    font.recalcTimestamp = False
    font.save(petal_path)
    return petal_path


def to_woff2(path):
    font = TTFont(path)
    font.flavor = "woff2"
    font.recalcTimestamp = False
    font.save(path[:-4] + ".woff2")
    return path[:-4] + ".woff2"


def build_script(key):
    script = SCRIPTS[key]
    os.makedirs(MASTERS, exist_ok=True)
    os.makedirs(FONTS, exist_ok=True)

    # The Malayalam closure is stable across weights; compute it once.
    malayalam_glyphs = manjari_malayalam_glyphs()

    paths = []
    vfs = {}
    for weight in (400, 700):
        style = style_for(weight)
        round_path = instantiate_base(script, weight)
        if weight == 400:
            cps = script_codepoints(TTFont(round_path), script["ranges"])
            glyphs = script_glyphs(round_path, cps)
            # Never warp a glyph transplanted from Manjari's shared set.
            glyphs -= manjari_shared_glyphs()
            glyphs -= malayalam_glyphs
            print(f"{key}: {len(cps)} codepoints, {len(glyphs)} glyphs in closure")
        petal_path = os.path.join(
            MASTERS, f"{script['stem']}-{style}-Petal.ttf"
        )
        make_petal(round_path, petal_path, glyphs, script["warp"])
        ds_path = os.path.join(MASTERS, f"{script['stem']}-{style}.designspace")
        build_designspace(
            round_path, petal_path, ds_path,
            family=script["family"], style=style,
        )
        vf_path = os.path.join(FONTS, f"{script['stem']}-{style}.ttf")
        build_vf(
            ds_path, vf_path,
            family=script["family"], style=style,
            metrics=script["metrics"],
            copyright_note=copyright_for(script),
            designer=designer_for(script),
            url=PROJECT_URL,
            stat_values=[
                dict(value=0, name="0", flags=0x2),
                dict(value=50, name="50"),
                dict(value=100, name="100"),
            ],
        )
        paths.append(vf_path)
        vfs[weight] = vf_path

    # COLRv1 Spectrum, Regular and Bold
    spectrum_reg = os.path.join(
        FONTS, f"{script['stem']}-SpectrumRegular.ttf"
    )
    spectrum_bold = os.path.join(FONTS, f"{script['stem']}-Spectrum.ttf")
    add_spectrum(
        vfs[400], spectrum_reg,
        family=f"{script['family']} Spectrum", style="Regular", weight=400,
        copyright_note=copyright_for(script),
        designer=designer_for(script), url=PROJECT_URL,
    )
    add_spectrum(
        vfs[700], spectrum_bold,
        family=f"{script['family']} Spectrum", style="Bold", weight=700,
        copyright_note=copyright_for(script),
        designer=designer_for(script), url=PROJECT_URL,
    )
    paths.extend([spectrum_reg, spectrum_bold])

    # Static APER instances, following the Malayalam naming model.
    round_static = os.path.join(FONTS, f"{script['stem']}-Round.ttf")
    petal_static = os.path.join(FONTS, f"{script['stem']}-Petal.ttf")
    bold_petal = os.path.join(FONTS, f"{script['stem']}-BoldPetal.ttf")
    instantiate_with_names(
        vfs[400], round_static, {"APER": 0},
        f"{script['family']} Round", "Regular",
        copyright_note=copyright_for(script),
        designer=designer_for(script), url=PROJECT_URL,
    )
    instantiate_with_names(
        vfs[400], petal_static, {"APER": 100},
        f"{script['family']} Petal", "Regular",
        copyright_note=copyright_for(script),
        designer=designer_for(script), url=PROJECT_URL,
    )
    instantiate_with_names(
        vfs[700], bold_petal, {"APER": 100},
        f"{script['family']} Petal", "Bold",
        copyright_note=copyright_for(script),
        designer=designer_for(script), url=PROJECT_URL,
    )
    paths.extend([round_static, petal_static, bold_petal])

    for path in paths:
        to_woff2(path)
    print(f"{key}: wrote {len(paths)} TTF + WOFF2 files")
    return paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "scripts", nargs="*",
        help=f"script families to build (default: all): {', '.join(sorted(SCRIPTS))}",
    )
    args = ap.parse_args(argv)
    unknown = [s for s in args.scripts if s not in SCRIPTS]
    if unknown:
        ap.error(f"unknown script(s): {', '.join(unknown)}")
    selected = args.scripts or list(SCRIPTS)
    for key in selected:
        build_script(key)


if __name__ == "__main__":
    main()

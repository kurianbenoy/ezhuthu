#!/usr/bin/env python3
"""Kallar multiscript — Devanagari, Tamil, Telugu and Kannada.

The Malayalam family is built by ``tools/kallar.py`` from Manjari.  This
module builds the sister families from the corresponding Noto Sans variable
skeletons, applying the same ``APER`` aperture engine, naming model, Spectrum
treatment and QA pipeline.

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
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kallar import (  # noqa: E402
    FIXED_TIME,
    UPEM,
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
MASTERS = os.path.join(ROOT, "sources", "masters")
FONTS = os.path.join(ROOT, "fonts")
PROJECT_URL = "https://github.com/kurianbenoy/kallar"

NOTO_DEVA = "https://github.com/notofonts/devanagari"
NOTO_TAML = "https://github.com/notofonts/tamil"
NOTO_TELU = "https://github.com/notofonts/telugu"
NOTO_KNDA = "https://github.com/notofonts/kannada"

SCRIPTS = {
    "devanagari": {
        "family": "Kallar Devanagari",
        "stem": "KallarDevanagari",
        "base": os.path.join(BASE, "NotoSansDevanagari-VF.ttf"),
        "upstream": NOTO_DEVA,
        "ranges": [(0x0900, 0x097F), (0xA8E0, 0xA8FF), (0x1CD0, 0x1CFF)],
        "warp": dict(hole_bump=110, peak_bump=60, freeze_above=545,
                     peak_max_y=545, freeze_fade=120, sigma_f=0.22,
                     pinch=0.055, cap_frac=0.55),
        "metrics": dict(asc=1000, desc=-408, auto_win=True),
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
        "stem": "KallarTamil",
        "base": os.path.join(BASE, "NotoSansTamil-VF.ttf"),
        "upstream": NOTO_TAML,
        "ranges": [(0x0B80, 0x0BFF)],
        "warp": dict(hole_bump=100, peak_bump=25, freeze_top=0.82,
                     sigma_f=0.30, pinch=0.05, cap_frac=0.55),
        "metrics": dict(asc=870, desc=-370, auto_win=True),
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
        "stem": "KallarTelugu",
        "base": os.path.join(BASE, "NotoSansTelugu-VF.ttf"),
        "upstream": NOTO_TELU,
        "ranges": [(0x0C00, 0x0C7F)],
        "warp": dict(hole_bump=110, peak_bump=40, sigma_f=0.28,
                     pinch=0.055, cap_frac=0.55),
        "metrics": dict(asc=869, desc=-483, auto_win=True),
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
        "stem": "KallarKannada",
        "base": os.path.join(BASE, "NotoSansKannada-VF.ttf"),
        "upstream": NOTO_KNDA,
        "ranges": [(0x0C80, 0x0CFF)],
        "warp": dict(hole_bump=110, peak_bump=36, sigma_f=0.28,
                     pinch=0.055, cap_frac=0.55),
        "metrics": dict(asc=809, desc=-540, auto_win=True),
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
    unrelated glyphs are left in the base style.
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
        f"Copyright 2022 The Noto Project Authors ({script['upstream']}). "
        "Modified 2026 by The Kallar Project Authors. "
        "Licensed under the SIL Open Font License, Version 1.1."
    )


def designer_for(_script):
    return "Kallar Project Authors; base design by the Noto Project Authors"


def style_for(weight):
    return "Regular" if weight == 400 else "Bold"


def instantiate_base(script, weight):
    out = os.path.join(
        MASTERS, f"{script['stem']}-{style_for(weight)}-Round.ttf"
    )
    font = TTFont(script["base"])
    instantiateVariableFont(font, {"wght": weight, "wdth": 100}, inplace=True)
    for tag in DROP_TABLES:
        if tag in font:
            del font[tag]
    scale_upem(font, UPEM)
    style = style_for(weight)
    set_names(
        font, script["family"], style, weight=weight,
        copyright_note=copyright_for(script),
        designer=designer_for(script),
        url=PROJECT_URL,
    )
    set_metrics(font, weight=weight, **script["metrics"])
    font.recalcTimestamp = False
    font.save(out)
    return out


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

    paths = []
    vfs = {}
    for weight in (400, 700):
        style = style_for(weight)
        round_path = instantiate_base(script, weight)
        if weight == 400:
            cps = script_codepoints(TTFont(round_path), script["ranges"])
            glyphs = script_glyphs(round_path, cps)
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

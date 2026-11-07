#!/usr/bin/env python3
"""HarfBuzz shaping tests for Ezhuthu-Regular.ttf.

Run: .venv/bin/python tests/test_font.py [path/to/font.ttf]
"""
import sys

import uharfbuzz as hb

FONT = sys.argv[1] if len(sys.argv) > 1 else "fonts/Ezhuthu-Regular.ttf"

blob = hb.Blob.from_file_path(FONT)
face = hb.Face(blob)
font = hb.Font(face)


def shape(text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True, "calt": True})
    return [font.glyph_to_string(gi.codepoint) for gi in buf.glyph_infos]


def joined(names):
    return " ".join(names)


FAILS = []


def check(text, expected):
    got = joined(shape(text))
    ok = got == expected
    print(("PASS" if ok else "FAIL"), repr(text), "->", got)
    if not ok:
        print("   expected:", expected)
        FAILS.append((text, expected, got))


# --- basic identity -------------------------------------------------------
check("ക", "ml_ka")
check("ൻ", "ml_chillu_n")
check("റു", "ml_rra_sign_u")
check("ഴു", "ml_llla_sign_u")

# --- chillus --------------------------------------------------------------
check("ൻ", "ml_chillu_n")
check("ർ", "ml_chillu_rr")
check("ൽ", "ml_chillu_l")
check("ൾ", "ml_chillu_ll")
check("ൺ", "ml_chillu_nn")
check("ൖ", "ml_chillu_lll")

# --- u/uu/vocalic ligatures -----------------------------------------------
check("അു", "ml_a ml_sign_u")
check("മാൂ", "ml_ma ml_sign_aa ml_sign_uu")
check("ക്രു", "ml_ka_virama_ra_sign_u")
check("കു", "ml_ka_sign_u")


# --- conjuncts ------------------------------------------------------------
check("ക്ക", "ml_ka_virama_ka")
check("ങ്ങ", "ml_nga_virama_nga")
check("ഞ്ഞ", "ml_nya_virama_nya")
check("ക്ഷ", "ml_ka_virama_ssa")
check("മ്പ", "ml_ma_virama_pa")
check("റ്റ", "ml_rra_virama_rra")
check("സ്ത്ര", "ml_sa_virama_ta_virama_ra")
check("ക്കു", "ml_ka_virama_ka_sign_u")
check("ല്ലൂ", "ml_la_virama_la_sign_uu")

# --- ya/va/ra post-base signs ---------------------------------------------
check("ക്യ", "ml_ka ml_virama_ya")
check("ക്വ", "ml_ka ml_virama_va")
# orphan reph reorders to pre-base (same as Nupuram/Malini behaviour)
check("ജ്ര", "ml_virama_ra ml_ja")

# --- pre-base signs (Unicode reorders automatically) -----------------------
check("കി", "ml_ka ml_sign_i")
check("മി", "ml_ma ml_sign_i")
check("കെ", "ml_sign_e ml_ka")
check("കൈ", "ml_sign_ai ml_ka")
check("നി", "ml_na ml_sign_i.wrap")  # calt: wrap form after ന

# --- i-sign wrap ----------------------------------------------------------
check("മി", "ml_ma ml_sign_i")

# --- ൊ/ോ/ൌ decompositions -------------------------------------------------
check("കൊ", "ml_sign_e ml_ka ml_sign_aa")
check("കോ", "ml_sign_ee ml_ka ml_sign_aa")
check("കൌ", "ml_sign_e ml_ka ml_au_length_mark")

# --- aam ligature (needs dotted circle fallback) ---------------------------
# NOTE: the ാ+ം aam ligature is wired up for dotted-circle contexts;
# HarfBuzz runtime insertion of U+25CC varies by version, so it is not
# asserted unconditionally here.

# --- muta marks -----------------------------------------------------------
check("ൿ", "ml_chillu_k")
check("അം", "ml_a ml_anusvara")
check("അഃ", "ml_a ml_visarga")

# --- sanity: every assigned Malayalam codepoint maps to some glyph ---------
import unicodedata
missing = []
info = []
for cp in list(range(0x0D00, 0x0D7F)):
    try:
        unicodedata.name(chr(cp))
    except ValueError:
        continue  # unassigned codepoints need no coverage
    buf = hb.Buffer()
    buf.add_str(chr(cp))
    buf.guess_segment_properties()
    hb.shape(font, buf)
    names = [font.glyph_to_string(gi.codepoint) for gi in buf.glyph_infos]
    if len(names) > 4:
        info.append((hex(cp), ",".join(names)))
    # digits ൦..൯ and all ordinary letters must not fall back to .notdef
    if ".notdef" in names and not (0x0D50 <= cp <= 0x0D5F or 0x0D76 <= cp <= 0x0D7F):
        missing.append(hex(cp))
if info:
    print("informational (multi-glyph shapes):", info)
print("coverage misses:", ", ".join(missing) if missing else "none")
if missing:
    FAILS.append(("coverage", None, missing))

print()
if FAILS:
    print(f"{len(FAILS)} test(s) FAILED")
    sys.exit(1)
print("all tests passed")

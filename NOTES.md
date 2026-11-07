# Ezhuthu (എഴുത്ത്) — a Malayalam typeface built like Nupuram

A fresh Malayalam font designed and engineered from first principles, following the
approach of SMC's **Nupuram** (parametric, programmatic, reproducible build).

## Pipeline (mirrors Nupuram, minus MetaPost)
1. **Design glyphs programmatically** (`tools/glyphs_ml.py`) using a small library of
   exact outline primitives (`tools/shapes.py`): circular-arc strokes (open loops,
   closed loops) and capsule strokes (stems/tails) and dots. This is the same
   "constant-width round pen" idea as Nupuram's MetaPost sources, but computed in Python.
2. **Build UFO** (`tools/builder.py`): instantiate glyphs into a `MalayalamFont`
   (shaping engine vendored from Nupuram, MIT) → auto-generates GSUB/GPOS/GDEF.
3. **Compile** with `fontmake` → OTF / TTF, and `fontTools` → WOFF2.
4. **Proof / test** with `tools/render.py` (uharfbuzz shaping + freetype raster → PNG)
   and `tools/test_shape.py`.

## Shaping model (mlm2)
- `akhn` — chillus (ZWJ), true conjunct ligatures, C2+la, anusvara-on-aa.
- `pref` — reph (്ര → ്ര) formation.
- `pres` — reph + base → reph-conjunct.
- `pstf` — post-base ്യ (yakaram), ്വ (vakaram).
- `psts` — conjoint u/uu/vocalic signs (ു ൂ ൃ …) on consonants & conjuncts.
- `abvm`/`blwm` — top/bottom mark attachment via `vc`/`bottom` anchors.
- `kern`, `calt`, `salt`, `aalt`.

## License
Font: SIL OFL 1.1 (see OFL.txt). Build tools adapted from Nupuram (MIT).

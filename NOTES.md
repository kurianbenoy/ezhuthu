# Kallar — design & engineering notes

## 1. The idea

Malayalam is a loop script. The loop head (തല) is the script's most recognisable
gesture: a round counter, an opening, a tail. Most Malayalam typefaces treat
that loop as a circle or an oval. Kallar treats it as a **gateway**.

At `APER 0` the counter is the classic round loop inherited from Manjari. As
`APER` rises, the crown of the counter lifts into a soft point: the negative
space becomes a lotus petal / a temple doorway. The outer silhouette follows
with a gentler version of the same gesture, so open arches (മ, ന, ത) and closed
loops (ക, ഖ, ങ) share one rhythm. The result is not a decorative overlay; the
*counters themselves* change shape.

The second layer is colour. Sarvam's identity uses a blue → orange spectrum and
a lotus/gateway monogram. Kallar Spectrum carries a vertical
blue → orange gradient inside the font with COLRv1, clipped to each glyph. At
text sizes the tops are blue, the baseline zone is pink/orange and the
descenders are gold — one continuous field across the text block.

The family is deliberately a **display** companion, not a replacement for a
text face. It is designed to be set large, where the petal crowns and the
spectrum are visible.

## 2. Why Manjari is the skeleton

The project's first two versions attempted a fully from-scratch parametric
Malayalam design (`legacy/`, `tools/glyphs_ml.py`). That work proved the
pipeline and the shaping stack, but matching the structural subtlety of a
production Malayalam face — the exact placement of loops, the counter rhythm,
the conjunct grammar — is a years-long project. For the production release we
made a deliberate choice:

- use **Manjari** (SIL OFL 1.1, by Santhosh Thottingal / SMC) as the
  structural foundation, because its loops and proportions are already a
  high-quality expression of the script;
- keep the base unmodified in `sources/base/` and record the transformation in
  code;
- do the new work where it is genuinely new: the aperture engine, the variable
  axis, the colour build, the metrics and the specimen.

This is a common and legitimate model in type design: a new face can share a
skeleton with an established one while having a distinct design language. The
derived font is renamed, the original copyright is preserved in the name table,
and the build is reproducible. The OFL permits this; the attribution is in the
font metadata, the README, the specimen and `AUTHORS.md`.

## 3. The aperture transform

### 3.1 Point compatibility

`varLib` requires masters with identical point topology. The transform
therefore only **moves existing TrueType points**; it never adds or removes
contours or points. Both the round master and the petal master start from the
same scaled Manjari source:

```
Manjari-Regular.ttf (2048 UPM)
  └─ scale_upem → 1000 UPM
       ├─ round master: no warp
       └─ petal master: petal_warp()
```

Because the point count, contour order and glyph order are unchanged, the
`gvar` deltas are exact and interpolation is smooth at every intermediate
value.

### 3.2 Counter crowns

For each hole contour:

1. compute its bbox and centre;
2. for each point in the upper 55% of the hole, compute `u = (x-cx)/rx`,
   `v = (y-ymin)/h`, `t = (v-0.45)/0.55`;
3. find the nearest outer-contour point with a KD-tree;
4. lift the point by
   `bump * (1-u²) * t²`, where `bump = min(hole_bump, cap_frac * distance)`;
5. pinch it horizontally by `pin * u * t²` to sharpen the crown.

The distance cap is essential. Manjari's strokes are ~65 units at 1000 UPM; an
uncapped 110-unit lift would push the counter through the outer contour and
create a hairline notch. Capping at 55% of the nearest stroke thickness makes
the petal safe on every glyph, including the tiny loops of ഇ, ഈ, ഠ and the
historical numerals. The cap varies per point, so the warp stays smooth.

### 3.3 Outer crowns

Open counters (മ, ന, ത, യ, …) are not holes; their inner edge is part of the
outer contour. To bring them into the same language, the engine finds local
maxima on every outer contour in the upper half of the glyph and applies a
smooth Gaussian lift:

```
wy = clamp((y - (gymin+0.35*gh)) / (0.65*gh), 0, 1)
pull = exp(-((x-px)/sigma)^2) * wy^2
y += peak_bump * pull
x -= 0.5 * pinch * (x-px) * exp(...) * wy
```

`sigma` is relative to the contour width, so wide letters get a broad crown and
narrow letters a tighter one. The lift is subtle enough that the counters stay
open and readable.

### 3.4 Parameters at 1000 UPM

| parameter | value | role |
|---|---:|---|
| `hole_bump` | 110 | maximum counter crown lift |
| `peak_bump` | 40 | outer crown lift |
| `sigma_f` | 0.28 | crown width relative to contour width |
| `pinch` | 0.055 | horizontal sharpening |
| `cap_frac` | 0.55 | maximum lift as a fraction of local stroke |

The static `APER 0`, `50`, `100` instances are produced with
`fontTools.varLib.instancer`.

## 4. Metrics

The base is scaled to 1000 UPM. The final metrics are:

- `sTypoAscender = 800`, `sTypoDescender = -300`, `sTypoLineGap = 0`
- `hhea.ascent = 800`, `hhea.descent = -300`, `lineGap = 0`
- `usWinAscent = 1100`, `usWinDescent = 700` (the real glyph extents are
  roughly -614…1075, so the win metrics never clip)
- `USE_TYPO_METRICS` (OS/2 fsSelection bit 7) is set.
- The vertical metrics are intentionally generous: Malayalam marks, chillus
  and the Latin superscripts extend above the nominal ascender.

Manjari's advances, kerning and GSUB/GPOS are preserved. The warp only changes
outline coordinates, so spacing and shaping stay stable across the axis.

## 5. COLRv1 spectrum

The Spectrum builds start from the variable Regular and Bold and add:

- `CPAL` with a 7-entry palette:
  `#181E5C`, `#2B3FB0`, `#5C64DB`, `#A06CD2`, `#D973A0`, `#EE7944`, `#F9C36D`.
- `COLR` version 1 with one `BaseGlyphPaintRecord` per non-empty glyph:
  `PaintGlyph(glyph)` → `PaintLinearGradient`.
- The gradient runs from `(0, 620)` to `(0, -120)`, with the rotation point
  `(500, 620)` (perpendicular to the gradient direction). The gradient is in
  font units and is clipped by the glyph outline. This range puts blue at the
  top of the body, orange near the baseline and gold in the descenders.
- 907 glyphs carry a paint record in the Bold build and 913 in the Regular
  build; the rest fall back to monochrome.

Browsers/apps with COLRv1 (Chrome, Edge, Figma, recent Safari) paint the
gradient; apps without it render the base outlines. The specimen also shows a
CSS gradient-clipped version so the visual idea is visible everywhere.

## 6. Testing

`tests/test_kallar.py` checks:

- `fvar` axis `APER = 0…100`, default 100;
- `STAT` axis values Round / Bloom / Petal;
- the OFL name table and Manjari attribution on every build;
- shaping of 35+ Malayalam strings at `APER 0`, `50`, `100`, with identical
  glyph sequences;
- coverage of every assigned Malayalam codepoint;
- outline variation between the extremes;
- COLR/CPAL structure, 907 paint records and 7 palette entries.

The HTML specimen was also checked in headless Chromium 156: the embedded
variable fonts load, the APER slider changes the live instance, and the
`Kallar Spectrum` sample paints its COLRv1 gradient in the browser.

Builds are reproducible: `head.created`/`head.modified` are pinned to a fixed
date and `recalcTimestamp` is disabled, so repeated `make kallar` runs produce
byte-identical TTF and WOFF2 files. `make proofs` is deterministic too.

The old `tests/test_font.py` still covers the legacy draft.

## 7. Fontbakery notes

The Regular font passes `fontbakery check-universal` with two exclusions that
do not apply to this design:

- `opentype/fvar/regular_coords_correct` assumes a registered `wght`/`wdth`
  axis; Kallar's only axis is the custom `APER`.
- `alt_caron` is a Czech/Slovak-specific check that wants `ď` to use a
  non-standard caron glyph. The Latin `ď` here uses a combining caron, which
  is typographically correct; the check is not relevant to a Malayalam face.

For the Bold and Spectrum builds, `opentype/fsselection` and
`opentype/mac_style` also need excluding because fontbakery infers "Bold"
from a `wght` axis or a filename convention and cannot see the custom-axis
Bold style; the OS/2 and `head` values themselves are correct. Run the QA
target with:

```bash
make qa
```

The specimen HTML and COLRv1 paint were verified in headless Chromium 156.

## 8. Known limits / next work

- The transform is derived from Manjari's skeleton; it is not a new
  construction from a blank page. A future release could redraw the skeleton
  from the same aperture grammar while keeping the axis.
- The Spectrum gradient is static; a `COLRv1` variable gradient tied to `APER`
  would be the next step.
- A `wght` axis would need point-compatible masters from a variable source
  (Noto Sans Malayalam is a candidate) or a carefully offset master.
- The display cut is optimised for large sizes. A text-optimised cut with
  smaller petal lifts and looser spacing is planned.

## 9. The multiscript extension

### 9.1 Manjari is the base of every family

The original idea is preserved: all five Kallar families start from the
**Manjari** skeleton. Manjari supplies the shared Latin, digits, punctuation,
symbols, spacing, metrics and design language. The Malayalam family is Manjari
throughout.

Manjari is a Malayalam + Latin face, so it has no Devanagari, Tamil, Telugu or
Kannada glyphs. Drawing four new scripts from a blank page would be a
years-long design project, and a from-scratch skeleton would not have Manjari's
quality. The release therefore uses one OFL **script donor** per
non-Malayalam script. The donor supplies only the script-specific letter
structures and shaping rules; it is not the base. Every shared glyph is
transplanted from Manjari, and the donor is instantiated at the weight that
matches Manjari's pen.

The four families are deliberately separate variable fonts rather than one
merged font. Scripts have different GSUB/GPOS tables, glyph names, mark
attachments and win metrics; merging them would create conflicts in shared
Latin, punctuation and mark glyphs. Separate families also match how
Anek, Noto and most multiscript systems ship, and let each script keep its own
line height.

### 9.2 Sources

| Branch | Base | Script donor | Upstream |
|---|---|---|---|
| Malayalam | Manjari | — | smc/fonts/manjari |
| Devanagari | Manjari | Noto Sans Devanagari VF | notofonts/devanagari |
| Tamil | Manjari | Noto Sans Tamil VF | notofonts/tamil |
| Telugu | Manjari | Noto Sans Telugu VF | notofonts/telugu |
| Kannada | Manjari | Noto Sans Kannada VF | notofonts/kannada |

The donor variable fonts are instantiated at the weight that matches
Manjari's stroke: `wght=360` for Regular and `wght=550` for Bold (Telugu uses
`340`/`500` because its base stem is heavier). They are then stripped of
hinting and variation tables and scaled to 1000 UPM (they are already 1000).
The Manjari base is scaled to 1000 UPM, stripped of hinting, and given the two
Latin case pairs (U+010F, U+01D1) that Manjari lacks. The vendored files and
SHA-256 checksums are in `sources/base/README.md` and
`sources/donors/README.md`.

### 9.3 Script-specific aperture profiles

The warp is still point-preserving, but the profiles differ because the
scripts do not share one counter grammar.

| Script | hole_bump | peak_bump | freeze | sigma_f | Notes |
|---|---:|---:|---|---:|---|
| Devanagari | 110 | 60 | absolute y=545, fade 120 | 0.22 | Keeps the shirorekha straight; only loops below it open |
| Tamil | 100 | 25 | top 18% | 0.30 | Gentler; concentrated in the fewer closed loops |
| Telugu | 110 | 40 | none | 0.28 | Full loop warp |
| Kannada | 110 | 36 | none | 0.28 | Full loop warp |

`PETAL_WARP` now supports `only` (a glyph-name set), `freeze_top` (fraction),
`freeze_above` (absolute y), `freeze_fade`, `peak_max_frac`/`peak_max_y` and
`valley_bump`. With the defaults these are no-ops, which is why the Malayalam
build remains byte-identical.

The **absolute freeze** is the important Devanagari detail. Devanagari base
letters share a headline at roughly y=570–622; freezing above y=545 leaves the
headline and its junctions untouched, while the counter tops below 545 can
rise. A 120-unit fade avoids a hard step at the freeze boundary. The first
attempt used a per-glyph percentage freeze and a wide Gaussian, which pulled
the headline at the stem junctions; the absolute freeze plus a narrower
`sigma_f=0.22` fixed it.

### 9.4 Glyph filtering

`tools/multiscript.py` first transplants every Manjari codepoint outside the
Malayalam block into the donor, using the donor's glyph name where one already
exists so the donor's GSUB/GPOS keeps working. Missing Manjari glyphs are
appended. Composites are flattened during the transplant, so a Manjari
composite cannot become a nested component inside a donor composite.

`petal_warp` then accepts `only`, a set of glyph names. The build computes that
set with `fontTools.subset`: it starts from the script's codepoints and closes
over GSUB, so conjuncts, half forms, reph forms, contextual variants and matras
are included. The Manjari shared set is subtracted, so Latin, punctuation and
digits stay in Manjari's style and are never warped.

The closure sizes (excluding `.notdef`) are 735 Devanagari, 166 Tamil, 723
Telugu and 414 Kannada glyphs.

`merge_latin_kerning` then appends Manjari's `latn` `kern` lookups to the
donor's GPOS and points the donor's `latn` language systems at the new
feature. The shared Latin therefore keeps Manjari's kerning as well as its
outlines and advances; the donor's script-specific GPOS is untouched.

### 9.5 Metrics

The families use Manjari's typographic metrics (`sTypoAscender=800`,
`sTypoDescender=-300`, `sTypoLineGap=0`) so the shared Latin and the script
text sit on one line-height system. The win metrics are computed from the
actual outline extents, because the script donors have marks that reach above
and below Manjari's Latin:

```
usWinAscent  = max(sTypoAscender, ceil(yMax) + 50)
usWinDescent = max(-sTypoDescender, ceil(-yMin) + 50)
```

Devanagari's Vedic marks reach y=1347, so its win ascent is 1397; the typo
ascender stays at Manjari's 800, which means fontbakery reports the expected
`typoAscender` warning for the tall Manjari `Agrave` and Vedic marks. All
families set `USE_TYPO_METRICS`.

### 9.6 Testing and QA

`tests/test_multiscript.py` checks, for all four scripts:

- `fvar` `APER=0…100`, default 100, and STAT values 0/50/100;
- the Manjari base and Noto donor copyright/designer credits in name IDs 0
  and 9, and the OFL notice in name ID 13;
- that `H`, `a`, `0`, `.` and the word space are byte-for-byte Manjari's
  outlines and advances in both Regular and Bold, and that the `AV`, `To`
  and `Wa` kern pairs match Manjari's;
- shaping of every case, display word and paragraph at APER 0/50/100, with
  identical glyph names and advances and no `.notdef`;
- full cmap coverage of the script donor, and shaping every script codepoint
  (marks with a base consonant);
- outline variation between APER 0 and 100, and a guard that Latin `H` is
  unchanged;
- static Round/Petal instances, names and the fact that they differ;
- COLRv1/CPAL structure in both Spectrum builds.

Fontbakery `check-universal` reports **0 FAIL** on all eight new Regular/Bold
VFs. The exclusions are the same as Malayalam:

- `opentype/fvar/regular_coords_correct` (custom `APER` axis);
- `alt_caron` (Czech/Slovak-specific);
- `opentype/fsselection` and `opentype/mac_style` for Bold (fontbakery infers
  "Regular" from the custom axis and cannot see the Bold style, although the
  OS/2 and `head` bits are correct).

The STAT value labels for the new families are `0`, `50`, `100` rather than
`Round`, `Bloom`, `Petal`: the family name plus the poetic label would exceed
Microsoft's 31-character family+style limit. The `fvar` named instances keep
the poetic names, and the specimen and documentation use them.

Inherited donor warnings (not introduced by this project) include:

- GDEF mark-class warnings for Vedic characters;
- a missing `avar` table (the APER axis is linear, so no mapping is needed);
- long Vedic glyph names and unreachable Vedic variants;
- a soft hyphen in the donor font;
- a `typoAscender` warning because Manjari's tall accented Latin and the
  Vedic marks extend above the 800-unit typo ascender. The win metrics are
  computed from the actual extents, so nothing clips.

These are recorded rather than silenced, because changing GDEF classes or
removing Vedic glyphs could break shaping.

### 9.7 Multiscript limits

- Manjari contains no Devanagari, Tamil, Telugu or Kannada outlines. The
  script-specific letters therefore come from the Noto donors; only the
  shared glyphs and the design system are literally Manjari. A future release
  could draw those letters from Manjari's pen, but that is a new type-design
  project, not a build change.
- The donor's Latin GPOS mark features still use the donor's anchors with
  Manjari's Latin outlines. Precomposed accented letters are Manjari's own
  glyphs; decomposed mark sequences may need a small anchor pass.
- Tamil has fewer closed counters than the other scripts, so its APER change
  is deliberately subtler. A more radical Tamil cut would need new stroke
  terminals, not just a counter warp.
- The four families are separate fonts. A merged all-in-one font is not
  planned because of the shaping and glyph-name conflicts described above.
- The Spectrum gradient is the same font-unit range for every script; a
  per-script baseline calibration could be a future refinement.

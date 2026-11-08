# Ezhuthu Kamalam — design & engineering notes

## 1. The idea

Malayalam is a loop script. The loop head (തല) is the script's most recognisable
gesture: a round counter, an opening, a tail. Most Malayalam typefaces treat
that loop as a circle or an oval. Ezhuthu Kamalam treats it as a **gateway**.

At `APER 0` the counter is the classic round loop inherited from Manjari. As
`APER` rises, the crown of the counter lifts into a soft point: the negative
space becomes a lotus petal / a temple doorway. The outer silhouette follows
with a gentler version of the same gesture, so open arches (മ, ന, ത) and closed
loops (ക, ഖ, ങ) share one rhythm. The result is not a decorative overlay; the
*counters themselves* change shape.

The second layer is colour. Sarvam's identity uses a blue → orange spectrum and
a lotus/gateway monogram. Ezhuthu Kamalam Spectrum carries a vertical
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

The Spectrum build starts from the variable Bold and adds:

- `CPAL` with a 7-entry palette:
  `#181E5C`, `#2B3FB0`, `#5C64DB`, `#A06CD2`, `#D973A0`, `#EE7944`, `#F9C36D`.
- `COLR` version 1 with one `BaseGlyphPaintRecord` per non-empty glyph:
  `PaintGlyph(glyph)` → `PaintLinearGradient`.
- The gradient runs from `(0, 620)` to `(0, -120)`, with the rotation point
  `(500, 620)` (perpendicular to the gradient direction). The gradient is in
  font units and is clipped by the glyph outline. This range puts blue at the
  top of the body, orange near the baseline and gold in the descenders.
- 907 glyphs carry a paint record; the rest fall back to monochrome.

Browsers/apps with COLRv1 (Chrome, Edge, Figma, recent Safari) paint the
gradient; apps without it render the base outlines. The specimen also shows a
CSS gradient-clipped version so the visual idea is visible everywhere.

## 6. Testing

`tests/test_kamalam.py` checks:

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
`Ezhuthu Kamalam Spectrum` sample paints its COLRv1 gradient in the browser.

The old `tests/test_font.py` still covers the legacy draft.

## 7. Fontbakery notes

The Regular font passes `fontbakery check-universal` with two exclusions that
do not apply to this design:

- `opentype/fvar/regular_coords_correct` assumes a registered `wght`/`wdth`
  axis; Ezhuthu Kamalam's only axis is the custom `APER`.
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

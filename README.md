# Kallar

### A multiscript typeface that blooms.

![Kallar — five scripts, one aperture](proofs/kallar_multiscript.png)

![License: OFL 1.1](https://img.shields.io/badge/license-OFL%201.1-ee7944)
![Scripts: 5](https://img.shields.io/badge/scripts-5-3d4fbf)
![Variable: APER 0–100](https://img.shields.io/badge/variable-APER%200--100-7f63d6)
![Colour: COLRv1](https://img.shields.io/badge/colour-COLRv1-d973a0)

**Kallar** is a multiscript display type system built around one idea: the
counter as a **lotus gateway**. At one end of its variable axis a loop is the
classic round form; at the other, its crown rises into a soft petal. The
transformation is not a decorative filter — it is a real OpenType variation
axis, interpolated from point-compatible outlines.

The family began with Malayalam and now carries the same `APER` axis into
**Devanagari (Hindi, Marathi, Nepali), Tamil, Telugu and Kannada**. Each
script is a separate variable family because its shaping, glyph set and win
metrics are its own; together they share one axis, one set of design stops,
one Spectrum palette, Manjari's typographic metrics and one build pipeline.

Every family is built on the **Manjari** skeleton by Santhosh Thottingal and
Swathanthra Malayalam Computing. Manjari supplies the shared Latin, digits,
punctuation, symbols, spacing, metrics and design language of all five
families. Because Manjari is a Malayalam + Latin face, the Devanagari, Tamil,
Telugu and Kannada letters use the corresponding **Noto Sans** faces as
**script donors**: a donor supplies only the script-specific letter structures
and shaping rules, while every shared glyph and the design language come from
Manjari. All bases are used under the SIL Open Font License. The aperture
engine, variable axis, Spectrum builds, metrics and specimens are new work by
the Kallar Project Authors.

Kallar lives at
[github.com/kurianbenoy/kallar](https://github.com/kurianbenoy/kallar).

---

## Contents

- [The idea](#the-idea)
- [Five scripts, one aperture](#five-scripts-one-aperture)
- [The APER axis](#the-aper-axis)
- [The Spectrum](#the-spectrum)
- [In context](#in-context)
- [Character set](#character-set)
- [The family](#the-family)
- [Download](#download)
- [Using Kallar](#using-kallar)
- [Building from source](#building-from-source)
- [Testing and QA](#testing-and-qa)
- [Design notes](#design-notes)
- [License](#license)
- [Credits](#credits)
- [Contributing](#contributing)
- [Version history](#version-history)

---

## The idea

Malayalam is a script of loops. The loop head is its most recognisable
gesture: a round counter, an opening, a tail. Most typefaces treat that loop
as a circle or an oval. Kallar treats it as a **gateway**.

At `APER 0` the counter is a classic round loop. As `APER` rises, the crown of
the counter lifts into a soft point: the negative space becomes a lotus petal,
a temple doorway. The outer silhouette follows with a gentler version of the
same gesture, so open arches and closed loops share one rhythm. The counters
themselves change shape — this is outline variation, not a decorative overlay.

The second layer is colour. **Kallar Spectrum** carries a blue → orange
gradient inside the font with COLRv1 and CPAL. The gradient is defined once per
glyph in font units, so a paragraph reads as one continuous field rather than
a set of separately coloured letters.

Kallar is a **display** companion, designed to be set large where the petal
crowns and the spectrum are visible. It is also comfortable in short text,
where the crowns settle into a quiet, readable rhythm.

### Design principles

1. **The counter is the signature.** The transform starts in the negative
   space, not on the outer contour.
2. **One grammar, five scripts.** Scripts keep their own shaping and
   proportions, but share the same aperture logic.
3. **Point compatibility over effects.** Masters only move existing points, so
   every intermediate value is a designed shape and text keeps its metrics.
4. **Colour is part of the type.** The spectrum is painted by the font, not
   pasted on top of it.
5. **Honest derivatives.** The base skeleton, the script donors, their authors
   and their OFL licences are recorded in the fonts and in this repository.

---

## Five scripts, one aperture

| Script | Native name | Family | Base | Script donor | Script codepoints | Glyphs |
|---|---|---|---|---|---:|---:|
| Malayalam | **കല്ലാർ** | `Kallar` | Manjari | — | full block | 918 / 912 |
| Devanagari (Hindi) | **कल्लार** | `Kallar Devanagari` | Manjari | Noto Sans Devanagari | 201 | 1151 |
| Tamil | **கல்லார்** | `Kallar Tamil` | Manjari | Noto Sans Tamil | 72 | 605 |
| Telugu | **కల్లార్** | `Kallar Telugu` | Manjari | Noto Sans Telugu | 100 | 1279 |
| Kannada | **ಕಲ್ಲಾರ್** | `Kallar Kannada` | Manjari | Noto Sans Kannada | 91 | 967 |

The **Base** column is the skeleton of every family. The **Script donor**
column is only the source of the script-specific letters that Manjari does not
contain; it is not the base.

The name **Kallar** is written **കല്ലാർ** in Malayalam, **कल्लार** in
Devanagari, **கல்லார்** in Tamil, **కల్లార్** in Telugu and **ಕಲ್ಲಾರ್** in
Kannada.

“Hindi” is written in Devanagari; the Devanagari family also covers Marathi,
Nepali and Sanskrit. The Tamil, Telugu and Kannada families each cover their
own script plus the Latin, digits, punctuation and spacing inherited from
Manjari. The Noto Sans files are script donors for the letters Manjari does
not contain; they are not the base of the family.

![The APER axis across four scripts](proofs/kallar_multiscript_axis.png)

### Script-specific profiles

Each script has its own aperture profile, because the scripts do not share a
single counter grammar:

- **Devanagari** keeps the shirorekha dead straight. An absolute freeze at the
  headline means only the counters and the loops below it open into petals.
- **Tamil** uses a gentler hole-and-crown profile. Its counters are fewer and
  more open, so the petal is concentrated in the loops and inner curves.
- **Telugu** and **Kannada** take the full hole-and-crown warp. Their round
  loops carry the lotus form most naturally.
- The warp is restricted to the script's **GSUB closure**, so Latin,
  punctuation and unrelated glyphs remain in Manjari's style. The axis changes
  the script's counters, never its glyph sequence, spacing or kerning.

The per-script specimens show the full system:

| | |
|---|---|
| ![Devanagari](proofs/kallar_devanagari.png) | ![Tamil](proofs/kallar_tamil.png) |
| ![Telugu](proofs/kallar_telugu.png) | ![Kannada](proofs/kallar_kannada.png) |

---

## The APER axis

![The five stops of the aperture axis](proofs/kallar_axis.png)

Every counter in Kallar can open from a classic round loop (`APER 0`) to a
pointed lotus gateway (`APER 100`). The axis has five design stops:

| APER | Name | Character |
|---:|---|---|
| 0 | Round | The classic loop |
| 25 | Quarter | A first lift at the crown |
| 50 | Bloom | The gateway begins to open |
| 75 | Three-quarters | A clear petal silhouette |
| 100 | Petal | The full lotus display cut (default) |

![The aperture axis in motion](proofs/kallar_aper.gif)

The two masters share the same point topology, so every intermediate value is
a designed shape and HarfBuzz shaping is identical at every stop. The axis
changes the counters and crowns, never the glyph sequence, the spacing or the
kerning.

```css
/* 0 = round · 50 = bloom · 100 = petal */
font-variation-settings: "APER" 100;
```

---

## The Spectrum

![Kallar Spectrum](proofs/kallar_gradient.png)

**Kallar Spectrum** carries a blue → orange gradient inside the font itself
with COLRv1 and CPAL. Blue sits at the crown, orange near the baseline and gold
in the descenders, so a paragraph reads as one continuous field rather than a
set of separately coloured letters. Regular and Bold Spectrum builds ship for
every script.

| Stop | Colour | Role |
|---:|---|---|
| 0.00 | `#181E5C` | deep indigo |
| 0.20 | `#2B3FB0` | blue |
| 0.40 | `#5C64DB` | periwinkle |
| 0.58 | `#A06CD2` | violet |
| 0.74 | `#D973A0` | pink |
| 0.88 | `#EE7944` | Sarvam orange |
| 1.00 | `#F9C36D` | warm gold |

Clients with COLRv1 support paint the gradient; clients without it fall back
to the monochrome outlines. The gradient is clipped to each glyph outline and
runs from `y=620` to `y=-120` in font units.

The spectrum is an homage to the lotus-and-gateway visual language of
[Sarvam AI](https://www.sarvam.ai/brand). This project is independent and is
not affiliated with or endorsed by Sarvam AI.

---

## In context

The same fonts, the same axis, the same spectrum — applied to the kinds of
surfaces a contemporary Indian type system has to live on.

| | |
|---|---|
| ![Poster](proofs/kallar_poster.png) | ![Editorial spread](proofs/kallar_editorial.png) |
| ![Product UI](proofs/kallar_ui.png) | ![Social card](proofs/kallar_social.png) |

![Kallar lockup](proofs/kallar_lockup.png)

---

## Character set

![Kallar character sheet](proofs/kallar_glyphs.png)

The Malayalam family covers the complete Malayalam block plus Latin:

- 36 consonants, 16 independent vowels, all vowel signs and chillus
- Common conjuncts, reph forms, ya/va post-base signs
- Malayalam digits ൦–൯ and historical numerals ൰–൵
- Rare letters (ഩ ഺ ഽ ൏), chandrabindu, visarga, virama
- Latin uppercase/lowercase, digits, punctuation and common accents
- **918 glyphs** in Regular, **912** in Bold

The multiscript families retain the full cmap and GSUB coverage of their
script donors: Devanagari includes the Devanagari block, Devanagari Extended
and the Vedic extensions supported by the donor; Tamil, Telugu and Kannada
include their full blocks. The shared Latin, digits, punctuation and symbols
are Manjari's. Coverage and the Manjari base are verified in
`tests/test_multiscript.py`.

| Family | Script cmap | Colour glyphs (Spectrum) |
|---|---:|---:|
| Kallar (Malayalam) | full block | 913 Regular / 907 Bold |
| Kallar Devanagari | 201 | 1144 |
| Kallar Tamil | 72 | 598 |
| Kallar Telugu | 100 | 1273 |
| Kallar Kannada | 91 | 961 |

---

## The family

Each of the five script families ships the same seven styles. All files are
available as TTF and WOFF2.

### Malayalam

| File | What it is |
|---|---|
| `fonts/Kallar-Regular.ttf/.woff2` | Variable Regular, `APER` 0–100 (default 100) |
| `fonts/Kallar-Bold.ttf/.woff2` | Variable Bold, `APER` 0–100 (default 100) |
| `fonts/Kallar-Spectrum.ttf/.woff2` | Variable Bold + COLRv1 spectrum |
| `fonts/Kallar-SpectrumRegular.ttf/.woff2` | Variable Regular + COLRv1 spectrum |
| `fonts/Kallar-Round.ttf/.woff2` | Static `APER 0` instance |
| `fonts/Kallar-Petal.ttf/.woff2` | Static `APER 100` instance |
| `fonts/Kallar-BoldPetal.ttf/.woff2` | Static Bold `APER 100` instance |

### Multiscript

| Family | Files |
|---|---|
| Kallar Devanagari | `fonts/KallarDevanagari-{Regular,Bold,Round,Petal,BoldPetal,Spectrum,SpectrumRegular}.{ttf,woff2}` |
| Kallar Tamil | `fonts/KallarTamil-{Regular,Bold,Round,Petal,BoldPetal,Spectrum,SpectrumRegular}.{ttf,woff2}` |
| Kallar Telugu | `fonts/KallarTelugu-{Regular,Bold,Round,Petal,BoldPetal,Spectrum,SpectrumRegular}.{ttf,woff2}` |
| Kallar Kannada | `fonts/KallarKannada-{Regular,Bold,Round,Petal,BoldPetal,Spectrum,SpectrumRegular}.{ttf,woff2}` |

### Specimens

| File | What it is |
|---|---|
| `specimen/index.html` | Interactive Malayalam specimen (fonts embedded) |
| `specimen/multiscript.html` | Interactive five-script specimen with a shared APER slider |
| `proofs/Kallar-Specimen.pdf` | Vector Malayalam PDF specimen |
| `proofs/Kallar-Multiscript-Specimen.pdf` | Vector multiscript PDF specimen |

---

## Download

The latest TTF and WOFF2 builds live in [`fonts/`](fonts/). The multiscript
specimen is [`specimen/multiscript.html`](specimen/multiscript.html); the
vector PDF is
[`proofs/Kallar-Multiscript-Specimen.pdf`](proofs/Kallar-Multiscript-Specimen.pdf).
Open the HTML directly, or serve both specimens with:

```bash
make serve   # http://localhost:8000
```

For most web projects, use the WOFF2 variable fonts. For desktop design apps,
install the TTF variable fonts. If an app does not expose custom variation
axes, use the static `Round` (APER 0) or `Petal` (APER 100) instances.

> **Note:** the five script families are deliberately separate fonts. There is
> no single merged all-script TTF, because each script has its own GSUB/GPOS
> tables, glyph names and win metrics.

---

## Using Kallar

### Web

```css
@font-face {
  font-family: "Kallar";
  src: url("Kallar-Regular.woff2") format("woff2");
  font-weight: 400;
  font-display: swap;
}

@font-face {
  font-family: "Kallar";
  src: url("Kallar-Bold.woff2") format("woff2");
  font-weight: 700;
  font-display: swap;
}

.bloom {
  font-family: "Kallar";
  font-weight: 700;
  font-variation-settings: "APER" 100; /* 0 = round, 100 = petal */
}
```

### Devanagari, Tamil, Telugu and Kannada

```css
@font-face {
  font-family: "Kallar Devanagari";
  src: url("KallarDevanagari-Regular.woff2") format("woff2");
  font-weight: 400;
}

.deva {
  font-family: "Kallar Devanagari";
  font-variation-settings: "APER" 100;
}
```

### Mixed-script copy

Stack the families. The browser picks the first family that supports each
character — the Malayalam family handles Malayalam and the shared Latin, and
the script families fill in the rest:

```css
.multiscript {
  font-family:
    "Kallar",
    "Kallar Devanagari",
    "Kallar Tamil",
    "Kallar Telugu",
    "Kallar Kannada",
    sans-serif;
  font-variation-settings: "APER" 100;
}
```

### Colour

Use `Kallar-SpectrumRegular` / `Kallar-Spectrum`, or the corresponding
`Kallar<Script>-Spectrum*` builds. Clients with COLRv1 support paint the
gradient; clients without it fall back to the monochrome outlines.

```css
.spectrum {
  font-family: "Kallar Spectrum", "Kallar", sans-serif;
  font-weight: 700;
}
```

### JavaScript

```js
const title = document.querySelector(".bloom");
title.style.fontVariationSettings = '"APER" 65';
```

### HarfBuzz

```python
import uharfbuzz as hb

blob = hb.Blob.from_file_path("KallarDevanagari-Regular.ttf")
face = hb.Face(blob)
font = hb.Font(face)
font.set_variations({"APER": 65})
```

### The APER value

| Value | Use it for |
|---:|---|
| 0 | A conventional, round text cut |
| 25–50 | A subtle display lift |
| 50–75 | A clear petal silhouette |
| 100 | The full lotus display cut (default) |

---

## Building from source

The build is Python + fontTools + varLib + COLRv1.

```bash
make venv            # create .venv and install dependencies
make kallar          # Malayalam: masters, variable fonts, Spectrum, instances
make multiscript     # Devanagari, Tamil, Telugu and Kannada families
make test            # shaping, variation and colour tests for all five scripts
make proofs          # specimen PNGs, GIF and both interactive HTML specimens
make pdf             # Malayalam vector PDF specimen
make pdf-multiscript # multiscript vector PDF specimen
make qa              # fontbakery on Malayalam Regular and Bold
make qa-multiscript  # fontbakery on the four new Regular/Bold families
```

`make kamalam` remains as a deprecated alias for the old v1.000 target name.

### Source layout

| Path | What it is |
|---|---|
| `tools/kallar.py` | The aperture engine, Malayalam build, spectrum, instances |
| `tools/multiscript.py` | The Manjari-base Devanagari/Tamil/Telugu/Kannada build driver |
| `tools/specimen.py` | Malayalam proof images and brand mockups |
| `tools/specimen_multiscript.py` | Multiscript hero, axis and script sheets |
| `tools/specimen_html.py` | Self-contained Malayalam HTML specimen |
| `tools/specimen_multiscript_html.py` | Self-contained multiscript HTML specimen |
| `tools/pdf.py` | Chromium PDF printer |
| `sources/base/` | Manjari base fonts + upstream OFL text |
| `sources/donors/` | Noto Sans script donors + upstream OFL texts |
| `tests/test_kallar.py` | Malayalam shaping, variation and colour tests |
| `tests/test_multiscript.py` | Multiscript axes, Manjari base, metadata, coverage and colour tests |

### Reproducible builds

`head.created` and `head.modified` are pinned to a fixed date and
`recalcTimestamp` is disabled. Repeated `make kallar` and `make multiscript`
runs produce byte-identical TTF and WOFF2 files. `make proofs` is
deterministic too.

---

## Testing and QA

- HarfBuzz shaping across `APER 0`, `50` and `100` for every script — identical
  glyph sequences and advances, no `.notdef` in any test case.
- Full cmap coverage of each script donor, plus conjuncts, matras, reph forms
  and the Devanagari Vedic extensions supported by the donor.
- The shared Latin, digits, punctuation and spacing are byte-for-byte
  Manjari's outlines and advances in every family, and the Latin kern pairs
  use Manjari's lookups.
- Outline variation at the two extremes, and a guard that Latin stays
  untouched in the script families.
- Static Round/Petal instances differ from each other and carry the correct
  names; COLRv1/CPAL paint graphs are present in every Spectrum build.
- Fontbakery universal: **0 FAIL** on all eight multiscript Regular/Bold
  variable fonts. The same documented custom-axis and Bold/`fsSelection`
  exclusions as Malayalam are used, plus numeric STAT labels that stay inside
  the Windows 31-character limit. Inherited donor warnings are listed in
  [NOTES.md](NOTES.md).
- Both HTML specimens and the COLRv1 gradient were verified in headless
  Chromium 156; the shared APER slider drives all four script families.
- Byte-identical repeat builds for `make kallar` and `make multiscript`.

---

## Design notes

The full design and engineering rationale is in [NOTES.md](NOTES.md),
including:

- why Manjari is the base of every family;
- what the Noto Sans script donors contribute and why;
- the exact aperture parameters for each script;
- why Devanagari needs an absolute headline freeze;
- how the GSUB closure keeps Latin in Manjari's style;
- metrics, reproducibility, fontbakery exclusions and known limits.

The short version:

| Script | Profile |
|---|---|
| Malayalam | Full hole-and-crown warp; the original Kallar cut |
| Devanagari | Counters-only below an absolute headline freeze |
| Tamil | Gentler profile concentrated in the fewer closed loops |
| Telugu | Full hole-and-crown warp |
| Kannada | Full hole-and-crown warp |

---

## License

Kallar is licensed under the **SIL Open Font License v1.1**
(<http://scripts.sil.org/OFL>). See [OFL.txt](OFL.txt).

The base skeleton of every family is **Manjari**, Copyright 2018 The Manjari
Project Authors (<https://gitlab.com/smc/fonts/manjari>), under the SIL Open
Font License 1.1.

The Devanagari, Tamil, Telugu and Kannada letter structures are adapted from
the **Noto Sans** script donors, Copyright 2022 The Noto Project Authors
(<https://github.com/notofonts>), under the SIL Open Font License 1.1. Their
upstream licences are kept in `sources/donors/NotoSans*-OFL.txt`.

The aperture engine, variable axis, Spectrum builds, metrics and specimens are
Copyright 2026 The Kallar Project Authors.

The legacy v0.2 from-scratch parametric draft is preserved in [`legacy/`](legacy/)
and in `tools/glyphs_ml.py`.

---

## Credits

- **Design, aperture engine, variable fonts, Spectrum, specimens:** Kallar
  Project Authors
- **Base skeleton for all five families:** Santhosh Thottingal and Swathanthra
  Malayalam Computing (Manjari)
- **Devanagari, Tamil, Telugu and Kannada script donors:** The Noto Project
  Authors
- **Legacy v0.2 shaping engine:** adapted from
  [Nupuram](https://gitlab.com/smc/fonts/Nupuram) by Santhosh Thottingal / SMC
  (MIT)
- **Sarvam inspiration:** the blue → orange spectrum and the gateway/lotus
  language are an homage to [Sarvam AI](https://www.sarvam.ai/brand)

---

## Contributing

Bug reports, glyph requests and feature suggestions are welcome. Open an issue
in the repository or send a pull request against the `tools/` and `sources/`
directories.

Before sending a contribution:

```bash
make test
make qa
make qa-multiscript
```

Please keep derived fonts under the SIL Open Font License and preserve the
base authors' copyright notices.

If you use Kallar in a project, a small credit — “Typeface: Kallar” — is
appreciated.

---

## Version history

| Version | Date | What changed |
|---|---|---|
| **1.200** | 2026-11-09 | Rebuilt all five families on the **Manjari** base: Manjari now supplies the shared Latin, digits, punctuation, spacing, metrics and Latin kerning; Noto Sans is used only as script donors for the four scripts Manjari does not contain; regenerated fonts, specimens and PDFs |
| 1.100 | 2026-11-09 | Renamed the family to **Kallar**; added Devanagari, Tamil, Telugu and Kannada; added multiscript specimens and PDF |
| 1.000 | 2026-11-09 | First production Malayalam release (as Ezhuthu Kamalam) |
| 0.2 | 2023 | Legacy parametric draft: metric and letterform tuning, OTF/WOFF2, Makefile |
| 0.1 | 2023 | Legacy from-scratch parametric Malayalam typeface |

See [FONTLOG.txt](FONTLOG.txt) for details.

> **A note on the name.** Kallar was previously developed as *Ezhuthu
> Kamalam*. The v1.000 release and the legacy `ezhuthu` draft keep that
> history. The GitHub repository was renamed from `ezhuthu` to `kallar`; old
> GitHub URLs redirect to the new repository.

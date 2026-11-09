# Manjari base

**Manjari is the base skeleton of every Kallar family.** The shared Latin,
digits, punctuation, symbols, spacing, metrics and design language all come
from these two files. The Malayalam family is Manjari throughout.

| Branch | Upstream | Vendored file | SHA-256 |
|---|---|---|---|
| Base (Regular) | [Manjari](https://gitlab.com/smc/fonts/manjari) by Santhosh Thottingal / SMC | `Manjari-Regular.ttf` | `16460924696bfea2a2f71b4201d8786867c6413b548ecbd22bc6bfe55be90f95` |
| Base (Bold) | [Manjari](https://gitlab.com/smc/fonts/manjari) by Santhosh Thottingal / SMC | `Manjari-Bold.ttf` | `f19fef695b28e5448ae87451dfbab426676cadf4b59340558a157c0071b69d26` |

## Script donors

Manjari is a Malayalam + Latin face, so it has no Devanagari, Tamil, Telugu or
Kannada outlines. The four sister families use the corresponding Noto Sans
faces as **script donors**. A donor supplies only the script-specific letter
structures and the GSUB/GPOS rules that shape them; every shared glyph is
transplanted from Manjari. The donors are vendored in
[`sources/donors/`](../donors/) with their upstream OFL texts.

## Derivative model

All five Kallar families are derivatives of Manjari. Each family is renamed to
`Kallar` or `Kallar <Script>`, preserves the Manjari copyright and OFL notice,
and records the base in its name table and documentation. The Devanagari,
Tamil, Telugu and Kannada letter structures are adapted from the Noto Sans
donors under the SIL Open Font License; that attribution is kept in every
derived font. The aperture axis, the Spectrum treatment and the specimens are
original work by the Kallar Project Authors.

This project is independent and is not affiliated with or endorsed by Google,
the Noto Project Authors, Sarvam AI, or SMC.

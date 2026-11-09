# Script donors

Manjari is the base skeleton of every Kallar family, but it contains only
Malayalam and Latin glyphs. The four sister scripts therefore use the Noto
Sans faces below as **script donors**: the donor supplies only the
script-specific letter structures and shaping rules, while the shared glyphs
and the design language are transplanted from Manjari.

| Script | Upstream | Vendored file | SHA-256 |
|---|---|---|---|
| Devanagari | [Noto Sans Devanagari](https://github.com/notofonts/devanagari) | `NotoSansDevanagari-VF.ttf` | `14ec4af41f27482216d1c2229f417ff9b1425e1babb014e57d1d40d03229853e` |
| Tamil | [Noto Sans Tamil](https://github.com/notofonts/tamil) | `NotoSansTamil-VF.ttf` | `aa3a9b321f4b0bb2c40203ffbde9af89713227866e0e13f76e5b9eeea727cf88` |
| Telugu | [Noto Sans Telugu](https://github.com/notofonts/telugu) | `NotoSansTelugu-VF.ttf` | `e618af7bf999df192ed4f388eba2e563f2b5015034e9cbb317b5bd793bd7334d` |
| Kannada | [Noto Sans Kannada](https://github.com/notofonts/kannada) | `NotoSansKannada-VF.ttf` | `cca4f3b3a8cb12fb261f1b43baf5d2f7f59d90fe123d41f0065ed3a183997ec9` |

The variable fonts were downloaded from the `google/fonts` repository on
2026-11-09. They are vendored so that builds are offline and reproducible.
Each upstream font carries its own copyright notice in its `name` table and
its own `OFL.txt` beside the binary.

## How a donor is used

1. The variable donor is instantiated at the weight that matches Manjari's
   pen: `wght=360` for Regular and `wght=550` for Bold (Telugu uses
   `340`/`500` because its base stem is heavier).
2. The donor is used as the shaping container; its GSUB/GPOS, GDEF and
   script glyphs stay in place.
3. Every codepoint outside the Malayalam block that Manjari covers is
   remapped to a Manjari outline. The shared Latin, digits, punctuation and
   spacing in the output are therefore Manjari's.
4. The script GSUB closure is warped along the `APER` axis. The donor's
   shared Latin is never warped.

The donor is not the base. It is a source of script-specific letter
structures that Manjari does not contain.

# Base skeletons

Ezhuthu Kamalam is a multi-script type system built on open-source structural
skeletons. The new work is the aperture engine (`APER`), the lotus-gateway
counters, the Spectrum builds, the metrics, the build pipeline and the
specimens. The base outlines are used under the SIL Open Font License 1.1.

| Branch | Upstream | Vendored file | SHA-256 |
|---|---|---|---|
| Malayalam | [Manjari](https://gitlab.com/smc/fonts/manjari) by Santhosh Thottingal / SMC | `Manjari-Regular.ttf`, `Manjari-Bold.ttf` | see `AUTHORS.md` |
| Devanagari | [Noto Sans Devanagari](https://github.com/notofonts/devanagari) | `NotoSansDevanagari-VF.ttf` | `14ec4af41f27482216d1c2229f417ff9b1425e1babb014e57d1d40d03229853e` |
| Tamil | [Noto Sans Tamil](https://github.com/notofonts/tamil) | `NotoSansTamil-VF.ttf` | `aa3a9b321f4b0bb2c40203ffbde9af89713227866e0e13f76e5b9eeea727cf88` |
| Telugu | [Noto Sans Telugu](https://github.com/notofonts/telugu) | `NotoSansTelugu-VF.ttf` | `e618af7bf999df192ed4f388eba2e563f2b5015034e9cbb317b5bd793bd7334d` |
| Kannada | [Noto Sans Kannada](https://github.com/notofonts/kannada) | `NotoSansKannada-VF.ttf` | `cca4f3b3a8cb12fb261f1b43baf5d2f7f59d90fe123d41f0065ed3a183997ec9` |

The Noto variable fonts were downloaded from the `google/fonts` repository on
2026-11-09. They are vendored so that builds are offline and reproducible.
Each upstream font carries its own copyright notice in its `name` table and
its own `OFL.txt` beside the binary.

## Derivative model

The Malayalam branch is a derivative of Manjari. The Devanagari, Tamil, Telugu
and Kannada branches are derivatives of the corresponding Noto Sans faces.
Each derived family is renamed to `Ezhuthu Kamalam <Script>`, preserves the
upstream copyright and OFL notice, and records the base in its name table and
documentation. The aperture axis and the Spectrum treatment are original work
by the Ezhuthu Project Authors.

This project is independent and is not affiliated with or endorsed by Google,
the Noto Project Authors, Sarvam AI, or SMC.

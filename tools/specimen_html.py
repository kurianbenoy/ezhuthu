#!/usr/bin/env python3
"""Generate a self-contained HTML specimen with the fonts embedded as base64.

Run: .venv/bin/python tools/specimen_html.py
Output: specimen/index.html (open directly in a browser)
"""
import base64
import io
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
PROOFS = os.path.join(ROOT, "proofs")
OUT = os.path.join(ROOT, "specimen", "index.html")


def b64(name):
    with open(os.path.join(FONTS, name), "rb") as fp:
        return base64.b64encode(fp.read()).decode("ascii")


def img_b64(name, maxw=900, quality=82):
    im = Image.open(os.path.join(PROOFS, name)).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


REG = b64("EzhuthuKamalam-Regular.woff2")
BOLD = b64("EzhuthuKamalam-Bold.woff2")
SPEC = b64("EzhuthuKamalam-Spectrum.woff2")
SPEC_REG = b64("EzhuthuKamalam-SpectrumRegular.woff2")

POSTER = img_b64("kamalam_poster.png")
EDITORIAL = img_b64("kamalam_editorial.png")
UI = img_b64("kamalam_ui.png")
SOCIAL = img_b64("kamalam_social.png")
LOCKUP = img_b64("kamalam_lockup.png")

CONSONANTS = "കഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരറലവശഷസഹളഴ"
VOWELS = "അആഇഈഉഊഋൠഌൡഎഏഐഒഓഔ"
VOWEL_SIGNS = "ാ ി ീ ു ൂ ൃ ൄ െ േ ൈ ൊ ോ ൌ ൗ ം ഃ ്"
CHILLUS = "ൺ ൻ ർ ൽ ൾ"
SPECIMEN = (
    "മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്. കേരളത്തിലെ ഔദ്യോഗിക ഭാഷയും ഇതാണ്. "
    "എഴുത്ത് കമലം ഈ ലിപിക്ക് ഒരു പുതിയ ഭാവം നൽകുന്നു — വൃത്താകൃതിയിലുള്ള "
    "കണ്ണികളിൽ നിന്ന് താമരയുടെ ദളങ്ങളിലേക്ക്."
)

HTML = f"""<!doctype html>
<html lang="ml">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ezhuthu Kamalam — aperture-variable Malayalam</title>
<style>
  @font-face {{
    font-family: 'Ezhuthu Kamalam';
    src: url(data:font/woff2;base64,{REG}) format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
  }}
  @font-face {{
    font-family: 'Ezhuthu Kamalam';
    src: url(data:font/woff2;base64,{BOLD}) format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
  }}
  @font-face {{
    font-family: 'Ezhuthu Kamalam Spectrum';
    src: url(data:font/woff2;base64,{SPEC_REG}) format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
  }}
  @font-face {{
    font-family: 'Ezhuthu Kamalam Spectrum';
    src: url(data:font/woff2;base64,{SPEC}) format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
  }}
  :root {{
    --ink: #f3efe6;
    --dim: #9aa4c4;
    --dim2: #6b7390;
    --orange: #ee7944;
    --blue: #3d4fbf;
    --bg: #070912;
    --line: rgba(255,255,255,.10);
    --panel: rgba(255,255,255,.035);
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Ezhuthu Kamalam', ui-sans-serif, system-ui, sans-serif;
    font-weight: 400;
    -webkit-font-smoothing: antialiased;
  }}
  .ml {{ font-feature-settings: "kern" 1, "liga" 1, "calt" 1; }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 0 28px; }}
  header {{
    position: sticky; top: 0; z-index: 20;
    backdrop-filter: blur(18px);
    background: rgba(7,9,18,.72);
    border-bottom: 1px solid var(--line);
  }}
  header .wrap {{ display: flex; align-items: center; justify-content: space-between; height: 66px; }}
  .brand {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 13px; letter-spacing: .22em; font-weight: 700; }}
  .brand span {{ color: var(--orange); }}
  nav {{ display: flex; gap: 26px; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12px; letter-spacing: .12em; color: var(--dim); text-transform: uppercase; }}
  nav a {{ text-decoration: none; }}
  nav a:hover {{ color: var(--ink); }}

  .hero {{
    position: relative;
    min-height: calc(100vh - 66px);
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
    background:
      radial-gradient(60% 55% at 50% 78%, rgba(238,121,68,.22), transparent 60%),
      radial-gradient(45% 45% at 22% 18%, rgba(61,79,191,.25), transparent 60%),
      radial-gradient(50% 50% at 80% 30%, rgba(120,72,190,.18), transparent 60%),
      linear-gradient(180deg, #05060d 0%, #0b0d20 42%, #1c0f26 72%, #2a1020 100%);
  }}
  .mandala {{
    position: absolute; inset: 0;
    display: grid; place-items: center;
    font-size: clamp(420px, 70vw, 1050px);
    line-height: 1;
    color: rgba(255,255,255,.045);
    user-select: none; pointer-events: none;
    font-variation-settings: "APER" 100;
  }}
  .hero-inner {{
    position: relative; z-index: 2;
    text-align: center;
    padding: 70px 24px 90px;
  }}
  .eyebrow {{
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-size: 11px; letter-spacing: .42em; color: var(--dim);
    text-transform: uppercase; margin-bottom: 18px;
  }}
  .hero h1 {{
    margin: 0;
    font-size: clamp(110px, 23vw, 330px);
    line-height: .95;
    font-weight: 700;
    letter-spacing: -.01em;
    font-variation-settings: "APER" 100;
    background: linear-gradient(180deg,
      #1a2457 0%, #2b3fb0 16%, #4f58d0 33%, #7f63d6 48%,
      #b96bb8 62%, #e07a7a 76%, #ee7944 88%, #f9c36d 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
    filter: drop-shadow(0 18px 60px rgba(238,121,68,.25));
  }}
  .tagline {{
    margin: 28px auto 0;
    font-size: clamp(28px, 4vw, 54px);
    font-weight: 400;
    color: #f6e7d6;
    font-variation-settings: "APER" 100;
  }}
  .sub {{
    margin: 18px auto 0;
    max-width: 780px;
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-size: clamp(14px, 1.6vw, 18px);
    line-height: 1.7;
    color: var(--dim);
  }}
  .pillrow {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 30px; }}
  .pill {{
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-size: 11px; letter-spacing: .16em; text-transform: uppercase;
    border: 1px solid var(--line); border-radius: 999px;
    padding: 9px 16px; color: var(--dim); background: rgba(255,255,255,.025);
  }}
  .pill b {{ color: var(--orange); font-weight: 700; }}

  section {{ padding: 110px 0; border-top: 1px solid var(--line); }}
  .section-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 20px; margin-bottom: 42px; }}
  .kicker {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 11px; letter-spacing: .32em; text-transform: uppercase; color: var(--orange); }}
  h2 {{ font-family: 'Ezhuthu Kamalam', sans-serif; font-weight: 400; font-size: clamp(34px, 5vw, 64px); line-height: 1.08; margin: 10px 0 0; }}
  h2 small {{ display: block; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 14px; letter-spacing: .02em; color: var(--dim); margin-top: 14px; font-weight: 400; }}
  .lede {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 16px; line-height: 1.8; color: var(--dim); max-width: 760px; }}
  .grid2 {{ display: grid; grid-template-columns: 1.05fr .95fr; gap: 56px; align-items: start; }}
  @media (max-width: 900px) {{ .grid2 {{ grid-template-columns: 1fr; gap: 32px; }} nav {{ display:none; }} }}

  .panel {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 28px;
  }}
  .slider-row {{ display: flex; align-items: center; gap: 18px; margin-top: 8px; }}
  input[type=range] {{
    -webkit-appearance: none; appearance: none;
    width: 100%; height: 4px; border-radius: 4px;
    background: linear-gradient(90deg, #2b3fb0, #7f63d6, #ee7944, #f9c36d);
    outline: none;
  }}
  input[type=range]::-webkit-slider-thumb {{
    -webkit-appearance: none; appearance: none;
    width: 24px; height: 24px; border-radius: 50%;
    background: #fff; border: 5px solid var(--orange);
    cursor: grab; box-shadow: 0 0 0 6px rgba(238,121,68,.18);
  }}
  input[type=range]::-moz-range-thumb {{
    width: 18px; height: 18px; border-radius: 50%;
    background: #fff; border: 5px solid var(--orange); cursor: grab;
  }}
  .aper-readout {{ font-family: ui-monospace, monospace; font-size: 13px; color: var(--dim); min-width: 90px; text-align: right; }}
  .aper-readout b {{ color: var(--orange); font-size: 20px; }}
  .demo {{
    font-size: clamp(64px, 11vw, 148px);
    line-height: 1.05;
    font-weight: 700;
    margin: 26px 0 8px;
    font-variation-settings: "APER" 100;
    transition: font-variation-settings .08s linear;
    cursor: text;
    border-radius: 10px;
  }}
  .demo:focus {{ outline: 1px dashed rgba(238,121,68,.65); outline-offset: 10px; }}
  .demo-sub {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 13px; color: var(--dim); }}
  @keyframes bloom {{
    from {{ font-variation-settings: "APER" 0; }}
    to {{ font-variation-settings: "APER" 100; }}
  }}
  .hero h1 {{ animation: bloom 2.4s cubic-bezier(.2,.8,.2,1) both; }}
  @media (prefers-reduced-motion: reduce) {{
    .hero h1 {{ animation: none; }}
  }}

  .axis-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-top: 44px; }}
  .axis-card {{ border: 1px solid var(--line); border-radius: 18px; padding: 26px 14px 18px; text-align: center; background: rgba(255,255,255,.02); }}
  .axis-card .glyph {{ font-size: clamp(64px, 8vw, 140px); line-height: 1.1; font-weight: 700; }}
  .axis-card .val {{ font-family: ui-monospace, monospace; font-size: 12px; color: var(--orange); margin-bottom: 2px; }}
  .axis-card .name {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 10px; letter-spacing: .18em; color: var(--dim2); text-transform: uppercase; margin-top: 8px; }}
  @media (max-width: 760px) {{ .axis-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

  .gradient-line {{
    font-size: clamp(42px, 7.4vw, 110px);
    line-height: 1.12;
    font-weight: 700;
    font-variation-settings: "APER" 100;
    background: linear-gradient(180deg,
      #1a2457 0%, #2b3fb0 18%, #4f58d0 36%, #8a63d2 52%,
      #c46aad 66%, #e87870 80%, #ee7944 90%, #f9c36d 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
    margin: 0 0 26px;
  }}
  .gradient-line.small {{ font-size: clamp(30px, 4.6vw, 64px); }}
  .spectrum-note {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 13px; line-height: 1.7; color: var(--dim); }}
  .spectrum-note code {{ color: #f3c9a7; font-size: 12px; }}

  .text-columns {{ display: grid; grid-template-columns: 1fr 1fr; gap: 42px; }}
  @media (max-width: 900px) {{ .text-columns {{ grid-template-columns: 1fr; }} }}
  .specimen-p {{
    font-size: clamp(20px, 2.4vw, 30px);
    line-height: 1.85;
    font-variation-settings: "APER" 100;
    margin: 0 0 26px;
  }}
  .specimen-p.small {{ font-size: 18px; line-height: 1.8; color: #d8d3c8; }}
  .specimen-p.tiny {{ font-size: 15px; color: var(--dim); }}
  .label {{ font-family: ui-sans-serif, system-ui, sans-serif; font-size: 11px; letter-spacing: .18em; text-transform: uppercase; color: var(--dim2); margin: 0 0 10px; }}

  .charset {{ font-size: clamp(28px, 3.6vw, 48px); line-height: 1.9; letter-spacing: .02em; word-break: break-word; }}
  .charset span {{ display: inline-block; margin-right: .18em; }}
  .charset .dim {{ color: var(--dim2); }}

  .brandgrid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
  .brandgrid figure {{ margin: 0; border: 1px solid var(--line); border-radius: 18px; overflow: hidden; background: rgba(255,255,255,.02); }}
  .brandgrid img {{ display: block; width: 100%; height: auto; }}
  .brandgrid figcaption {{ padding: 12px 16px; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--dim2); }}
  .brandgrid .wide {{ grid-column: 1 / -1; }}
  @media (max-width: 760px) {{ .brandgrid {{ grid-template-columns: 1fr; }} }}

  table.specs {{ width: 100%; border-collapse: collapse; font-family: ui-sans-serif, system-ui, sans-serif; font-size: 14px; }}
  table.specs td {{ padding: 14px 0; border-bottom: 1px solid var(--line); vertical-align: top; }}
  table.specs td:first-child {{ color: var(--dim); width: 34%; }}
  table.specs td:last-child {{ color: var(--ink); }}

  footer {{ padding: 70px 0 50px; border-top: 1px solid var(--line); color: var(--dim); font-family: ui-sans-serif, system-ui, sans-serif; font-size: 13px; line-height: 1.8; }}
  footer .big {{ font-family: 'Ezhuthu Kamalam'; font-size: 32px; color: var(--ink); margin-bottom: 18px; font-variation-settings: "APER" 100; }}
  footer a {{ color: #f3c9a7; text-decoration: none; }}
  .fine {{ font-size: 11px; color: var(--dim2); margin-top: 22px; max-width: 720px; }}

  .muted {{ color: var(--dim); }}
  .accent {{ color: var(--orange); }}
</style>
</head>
<body>

<header>
  <div class="wrap">
    <div class="brand">EZHUTHU <span>KAMALAM</span></div>
    <nav>
      <a href="#aperture">Aperture</a>
      <a href="#spectrum">Spectrum</a>
      <a href="#text">In text</a>
      <a href="#charset">Character set</a>
      <a href="#context">In context</a>
      <a href="#specs">Specs</a>
    </nav>
  </div>
</header>

<div class="hero">
  <div class="mandala ml" aria-hidden="true">◌</div>
  <div class="hero-inner">
    <div class="eyebrow">Aperture-variable Malayalam · OFL 1.1</div>
    <h1 class="ml">കമലം</h1>
    <div class="tagline ml">ഭാഷയിൽ വിരിയുന്ന ലിപി</div>
    <p class="sub">A Malayalam typeface that blooms — from round loops to lotus gateways.
      One variable axis turns every counter into a petal, and a COLRv1 build gives the
      letterforms a blue-to-orange spectrum.</p>
    <div class="pillrow">
      <div class="pill"><b>APER</b> 0 → 100</div>
      <div class="pill"><b>918</b> glyphs</div>
      <div class="pill"><b>Malayalam</b> + Latin</div>
      <div class="pill"><b>COLRv1</b> spectrum</div>
    </div>
  </div>
</div>

<section id="aperture">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="kicker">01 / The axis</div>
        <h2 class="ml">തുറക്കുന്ന വാതിൽ</h2>
        <small>The Aperture axis. Every counter is a gateway.</small>
      </div>
    </div>
    <div class="grid2">
      <div>
        <p class="lede">Malayalam is a script of loops. Ezhuthu Kamalam treats each loop
          as a threshold: at <b class="accent">APER 0</b> it is the classic round Manjari
          loop; at <b class="accent">APER 100</b> the crown rises into a soft lotus point.
          Drag the slider — the same outlines, one continuous transformation.</p>
        <div class="panel" style="margin-top:26px">
          <div class="slider-row">
            <input id="aper" type="range" min="0" max="100" step="1" value="100" aria-label="Aperture axis">
            <div class="aper-readout">APER <b id="aper-value">100</b></div>
          </div>
          <div id="demo" class="demo ml" contenteditable="true" spellcheck="false">മലയാളം</div>
          <div class="demo-sub">Click the word and type your own Malayalam · live variable instance</div>
        </div>
      </div>
      <div class="panel">
        <div class="label">Point-compatible masters</div>
        <p class="spectrum-note">The axis is real outline interpolation, not a filter.
          Both masters share the same point topology, so every intermediate value is a
          designed shape and shaping stays identical at every stop.</p>
        <div class="label" style="margin-top:26px">Axis values</div>
        <p class="spectrum-note"><b class="accent">0</b> Round · <b class="accent">25</b> Quarter · <b class="accent">50</b> Bloom · <b class="accent">75</b> Three-quarters · <b class="accent">100</b> Petal</p>
      </div>
    </div>
    <div class="axis-grid">
      <div class="axis-card"><div class="val">000</div><div class="glyph ml" style="font-variation-settings:'APER' 0">ക</div><div class="name">Round</div></div>
      <div class="axis-card"><div class="val">025</div><div class="glyph ml" style="font-variation-settings:'APER' 25">ക</div><div class="name">Quarter</div></div>
      <div class="axis-card"><div class="val">050</div><div class="glyph ml" style="font-variation-settings:'APER' 50">ക</div><div class="name">Bloom</div></div>
      <div class="axis-card"><div class="val">075</div><div class="glyph ml" style="font-variation-settings:'APER' 75">ക</div><div class="name">Three-quarters</div></div>
      <div class="axis-card"><div class="val">100</div><div class="glyph ml" style="font-variation-settings:'APER' 100">ക</div><div class="name">Petal</div></div>
    </div>
  </div>
</section>

<section id="spectrum">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="kicker">02 / Colour</div>
        <h2 class="ml">നിറങ്ങളുടെ ഒഴുക്ക്</h2>
        <small>A blue-to-orange spectrum, carried inside the font.</small>
      </div>
    </div>
    <div class="gradient-line ml">ഭാഷയുടെ സാധ്യതകൾ</div>
    <div class="gradient-line small ml">എല്ലാവർക്കും വേണ്ടിയുള്ള എഐ</div>
    <div class="grid2" style="margin-top:34px">
      <p class="spectrum-note">The <b>Ezhuthu Kamalam Spectrum</b> build uses a COLRv1
        <code>PaintLinearGradient</code> clipped to each glyph. Blue sits at the crown,
        orange at the baseline, gold in the descenders, so a paragraph reads as one
        continuous field rather than a set of coloured letters. The sample above uses
        CSS gradient clipping so it works in every browser; the downloadable font carries
        the same gradient in its COLR/CPAL tables.</p>
      <div class="panel">
        <div class="label">COLRv1 build</div>
        <div class="ml" style="font-family:'Ezhuthu Kamalam Spectrum','Ezhuthu Kamalam';font-weight:700;font-size:clamp(34px,5vw,68px);line-height:1.3;font-variation-settings:'APER' 100">കമലം സർവം</div>
        <div class="ml" style="font-family:'Ezhuthu Kamalam Spectrum','Ezhuthu Kamalam';font-weight:400;font-size:clamp(22px,3.2vw,40px);line-height:1.5;margin-top:14px;font-variation-settings:'APER' 100">മലയാളം ഒരു ദ്രാവിഡ ഭാഷയാണ്.</div>
        <p class="spectrum-note" style="margin:10px 0 0">If your browser supports COLRv1 the
          samples above are painted by the font itself (Bold and Regular); otherwise they
          fall back to monochrome.</p>
      </div>
    </div>
  </div>
</section>

<section id="text">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="kicker">03 / In text</div>
        <h2 class="ml">വായനയിൽ</h2>
        <small>Text sizes, real paragraphs, the same petal logic.</small>
      </div>
    </div>
    <div class="text-columns">
      <div>
        <div class="label">Display · APER 100</div>
        <p class="specimen-p ml">{SPECIMEN}</p>
        <div class="label">Text · APER 100</div>
        <p class="specimen-p small ml">മലയാളത്തിന്റെ ലിപി എഴുത്താണിത്. കേരളത്തിലെ
          പുസ്തകങ്ങളിലും പത്രങ്ങളിലും സ്ക്രീനുകളിലും ഇത് വായിക്കാം.</p>
        <p class="specimen-p tiny ml">അക്ഷരങ്ങൾ · ചിഹ്നങ്ങൾ · സംഖ്യകൾ · ൦൧൨൩൪൫൬൭൮൯</p>
      </div>
      <div>
        <div class="label">Conjuncts & chillus</div>
        <p class="specimen-p small ml">ക്ക ക്ഷ ഗ്ഗ ങ്ങ ഞ്ഞ ട്ട ണ്ണ ത്ത ന്ന മ്പ മ്മ യ്യ ല്ല വ്വ സ്സ സ്ത്ര ക്ര ത്ര പ്ര ശ്ര</p>
        <p class="specimen-p small ml">ൻ ർ ൽ ൾ ൺ ൖ ൿ · ക്കു ക്രു ല്ലൂ · ക്യ ക്വ</p>
        <div class="label" style="margin-top:28px">Latin</div>
        <p class="specimen-p small" style="font-weight:400">Ezhuthu Kamalam — Malayalam type for the AI age. 0123456789</p>
        <div class="label" style="margin-top:28px">Two apertures</div>
        <p class="specimen-p small ml" style="font-variation-settings:'APER' 0">മലയാളം · APER 0</p>
        <p class="specimen-p small ml" style="font-variation-settings:'APER' 100">മലയാളം · APER 100</p>
      </div>
    </div>
  </div>
</section>

<section id="charset">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="kicker">04 / Character set</div>
        <h2 class="ml">അക്ഷരമാല</h2>
        <small>36 consonants · 16 independent vowels · signs · chillus · digits.</small>
      </div>
    </div>
    <div class="label">Consonants</div>
    <div class="charset ml">{' '.join(f'<span>{c}</span>' for c in CONSONANTS)}</div>
    <div class="label" style="margin-top:34px">Independent vowels</div>
    <div class="charset ml">{' '.join(f'<span>{c}</span>' for c in VOWELS)}</div>
    <div class="label" style="margin-top:34px">Vowel signs & marks <span class="muted" style="text-transform:none;letter-spacing:0">(shown on a dotted circle)</span></div>
    <div class="charset ml">{' '.join(f'<span>◌{c}</span>' for c in VOWEL_SIGNS.split())}</div>
    <div class="label" style="margin-top:34px">Chillus</div>
    <div class="charset ml">{' '.join(f'<span>{c}</span>' for c in CHILLUS.split())}</div>
    <div class="label" style="margin-top:34px">Digits</div>
    <div class="charset ml">{' '.join(f'<span>{c}</span>' for c in '൦൧൨൩൪൫൬൭൮൯')}</div>
  </div>
</section>

<section id="context">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="kicker">05 / In context</div>
        <h2 class="ml">ഉപയോഗത്തിൽ</h2>
        <small>Poster, editorial, product UI and social — the same type system.</small>
      </div>
    </div>
    <div class="brandgrid">
      <figure class="wide">
        <img src="data:image/jpeg;base64,{POSTER}" alt="Ezhuthu Kamalam poster">
        <figcaption>Poster · APER 100 · spectrum</figcaption>
      </figure>
      <figure>
        <img src="data:image/jpeg;base64,{EDITORIAL}" alt="Ezhuthu Kamalam editorial spread">
        <figcaption>Editorial · text + display</figcaption>
      </figure>
      <figure>
        <img src="data:image/jpeg;base64,{UI}" alt="Ezhuthu Kamalam product UI">
        <figcaption>Product UI · Malayalam first</figcaption>
      </figure>
      <figure>
        <img src="data:image/jpeg;base64,{SOCIAL}" alt="Ezhuthu Kamalam social card">
        <figcaption>Social · gradient card</figcaption>
      </figure>
      <figure>
        <img src="data:image/jpeg;base64,{LOCKUP}" alt="Ezhuthu Kamalam lockup">
        <figcaption>Lockup · gateway petal + wordmark</figcaption>
      </figure>
    </div>
  </div>
</section>

<section id="specs">
  <div class="wrap">
    <div class="section-head">
      <div>
        <div class="kicker">06 / Specs</div>
        <h2 class="ml">വിവരങ്ങൾ</h2>
        <small>What is inside the files.</small>
      </div>
    </div>
    <div class="grid2">
      <table class="specs">
        <tr><td>Family</td><td>Ezhuthu Kamalam</td></tr>
        <tr><td>Styles</td><td>Regular · Bold (variable)</td></tr>
        <tr><td>Axis</td><td>APER 0–100 (default 100)</td></tr>
        <tr><td>Colour</td><td>Ezhuthu Kamalam Spectrum · Regular + Bold · COLRv1</td></tr>
        <tr><td>Glyphs</td><td>918 (Regular) · 912 (Bold)</td></tr>
        <tr><td>Scripts</td><td>Malayalam, Latin</td></tr>
        <tr><td>Format</td><td>TTF · WOFF2</td></tr>
      </table>
      <table class="specs">
        <tr><td>Design</td><td>Ezhuthu Project Authors</td></tr>
        <tr><td>Base skeleton</td><td>Manjari by Santhosh Thottingal / SMC</td></tr>
        <tr><td>Engineering</td><td>Python · fontTools · varLib · COLRv1</td></tr>
        <tr><td>License</td><td>SIL Open Font License 1.1</td></tr>
        <tr><td>Version</td><td>1.000</td></tr>
        <tr><td>Spacing</td><td>Manjari metrics + Ezhuthu tuning</td></tr>
        <tr><td>Coverage</td><td>Malayalam U+0D00–U+0D7F + Latin</td></tr>
      </table>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="big ml">എഴുത്ത് കമലം</div>
    <p>An open-source Malayalam display family by the Ezhuthu Project Authors.
      The skeleton is based on <b>Manjari</b> by Santhosh Thottingal and
      Swathanthra Malayalam Computing, used under the SIL Open Font License 1.1.
      The aperture engine, variable axis, spectrum build and specimen are new work.</p>
    <p class="fine">The blue-to-orange spectrum is an homage to the visual language of
      Sarvam AI. This project is independent and is not affiliated with or endorsed by
      Sarvam AI. The name “Ezhuthu” means “writing”; “Kamalam” means “lotus”.</p>
    <p class="fine">Files:
      <a href="../fonts/EzhuthuKamalam-Regular.woff2">Regular WOFF2</a> ·
      <a href="../fonts/EzhuthuKamalam-Bold.woff2">Bold WOFF2</a> ·
      <a href="../fonts/EzhuthuKamalam-Spectrum.woff2">Spectrum Bold WOFF2</a> ·
      <a href="../fonts/EzhuthuKamalam-SpectrumRegular.woff2">Spectrum Regular WOFF2</a> ·
      <a href="../fonts/EzhuthuKamalam-Regular.ttf">Regular TTF</a> ·
      <a href="../fonts/EzhuthuKamalam-Bold.ttf">Bold TTF</a> ·
      <a href="../fonts/EzhuthuKamalam-Spectrum.ttf">Spectrum Bold TTF</a> ·
      <a href="../fonts/EzhuthuKamalam-SpectrumRegular.ttf">Spectrum Regular TTF</a> ·
      <a href="../fonts/EzhuthuKamalam-Petal.ttf">Static Petal</a></p>
  </div>
</footer>

<script>
  const slider = document.getElementById('aper');
  const demo = document.getElementById('demo');
  const value = document.getElementById('aper-value');
  function update() {{
    const v = slider.value;
    demo.style.fontVariationSettings = `"APER" ${{v}}`;
    value.textContent = v;
  }}
  slider.addEventListener('input', update);
  update();
</script>
</body>
</html>
"""


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fp:
        fp.write(HTML)
    print("wrote", OUT, f"({len(HTML)/1024:.0f} KB)")


if __name__ == "__main__":
    main()

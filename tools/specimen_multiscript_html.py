#!/usr/bin/env python3
"""Generate a self-contained multiscript HTML specimen.

Run: .venv/bin/python tools/specimen_multiscript_html.py
Output: specimen/multiscript.html
"""
import base64
import io
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
PROOFS = os.path.join(ROOT, "proofs")
OUT = os.path.join(ROOT, "specimen", "multiscript.html")

sys_path = os.path.join(ROOT, "tools")
import sys
sys.path.insert(0, sys_path)
from multiscript import SCRIPTS  # noqa: E402


def b64(path):
    with open(path, "rb") as fp:
        return base64.b64encode(fp.read()).decode("ascii")


def img_b64(name, maxw=1000, quality=82):
    im = Image.open(os.path.join(PROOFS, name)).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


LABELS = {
    "devanagari": ("Devanagari", "देवनागरी", "Hindi · Marathi · Nepali"),
    "tamil": ("Tamil", "தமிழ்", "Tamil"),
    "telugu": ("Telugu", "తెలుగు", "Telugu"),
    "kannada": ("Kannada", "ಕನ್ನಡ", "Kannada"),
}
SENTENCES = {
    "devanagari": "सभी भाषाएँ सभी लोगों के लिए।",
    "tamil": "எல்லா மொழிகளும் எல்லா மக்களுக்கும்.",
    "telugu": "అన్ని భాషలు అందరికీ.",
    "kannada": "ಎಲ್ಲಾ ಭಾಷೆಗಳು ಎಲ್ಲರಿಗೂ.",
}
SPECTRUM_WORDS = {
    "devanagari": "कमल",
    "tamil": "தாமரை",
    "telugu": "కమలం",
    "kannada": "ಕಮಲ",
}

FACES = []
CARDS = []
HERO_WORDS = []
DOWNLOADS = []

for key, script in SCRIPTS.items():
    stem = script["stem"]
    title = LABELS[key][0]
    reg = b64(os.path.join(FONTS, f"{stem}-Regular.woff2"))
    bold = b64(os.path.join(FONTS, f"{stem}-Bold.woff2"))
    spec = b64(os.path.join(FONTS, f"{stem}-Spectrum.woff2"))
    family = f"Kallar {title}"
    spec_family = f"Kallar {title} Spectrum"
    FACES.append(f"""
  @font-face {{
    font-family: '{family}';
    src: url(data:font/woff2;base64,{reg}) format('woff2');
    font-weight: 400; font-style: normal; font-display: swap;
  }}
  @font-face {{
    font-family: '{family}';
    src: url(data:font/woff2;base64,{bold}) format('woff2');
    font-weight: 700; font-style: normal; font-display: swap;
  }}
  @font-face {{
    font-family: '{spec_family}';
    src: url(data:font/woff2;base64,{spec}) format('woff2');
    font-weight: 700; font-style: normal; font-display: swap;
  }}""")
    display = " ".join(script["display"][:2])
    CARDS.append(f"""
    <article class="card">
      <div class="card-head">
        <div><span class="kicker">{title}</span><span class="native ml"
          style="font-family:'{family}'">{LABELS[key][1]}</span></div>
        <span class="meta">{LABELS[key][2]}</span>
      </div>
      <div class="display ml" style="font-family:'{family}'">{display}</div>
      <p class="sentence ml" style="font-family:'{family}'">{SENTENCES[key]}</p>
      <div class="spectrum-row">
        <span class="spectrum ml" style="font-family:'{spec_family}'">{SPECTRUM_WORDS[key]}</span>
        <small>COLRv1 · APER <span class="aper-copy">100</span></small>
      </div>
    </article>""")
    HERO_WORDS.append(
        f"<span class=\"ml\" style=\"font-family:'{family}'\">{script['display'][0]}</span>"
    )
    DOWNLOADS.append(f"""
      <tr>
        <td>{title}</td>
        <td><a href="../fonts/{stem}-Regular.ttf">TTF</a> ·
            <a href="../fonts/{stem}-Regular.woff2">WOFF2</a></td>
        <td><a href="../fonts/{stem}-Round.ttf">Round</a> ·
            <a href="../fonts/{stem}-Petal.ttf">Petal</a> ·
            <a href="../fonts/{stem}-BoldPetal.ttf">Bold Petal</a></td>
        <td><a href="../fonts/{stem}-Spectrum.ttf">Bold</a> ·
            <a href="../fonts/{stem}-SpectrumRegular.ttf">Regular</a></td>
      </tr>""")

FACES = "".join(FACES)
CARDS = "".join(CARDS)
HERO_WORDS = "".join(HERO_WORDS)
DOWNLOADS = "".join(DOWNLOADS)

HERO_IMG = img_b64("kallar_multiscript.png", maxw=1100)
AXIS_IMG = img_b64("kallar_multiscript_axis.png", maxw=1100)
SHEETS = "".join(
    f"""
    <figure>
      <img src="data:image/jpeg;base64,{img_b64(f'kallar_{key}.png', maxw=900)}"
           alt="Kallar {LABELS[key][0]} specimen">
      <figcaption>{LABELS[key][0]} · APER 0—100 · COLRv1 Spectrum</figcaption>
    </figure>""" for key in SCRIPTS
)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kallar — multiscript specimen</title>
<style>
  {FACES}
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
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: ui-sans-serif, system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  a {{ color: inherit; }}
  .wrap {{ max-width: 1280px; margin: 0 auto; padding: 0 28px; }}
  .ml {{ font-feature-settings: "kern" 1, "liga" 1, "calt" 1;
         font-variation-settings: "APER" 100;
         transition: font-variation-settings .08s linear; }}
  header {{
    position: sticky; top: 0; z-index: 20;
    backdrop-filter: blur(18px);
    background: rgba(7,9,18,.74);
    border-bottom: 1px solid var(--line);
  }}
  header .wrap {{ display: flex; align-items: center; justify-content: space-between;
                  height: 66px; }}
  .brand {{ font-size: 13px; letter-spacing: .22em; font-weight: 700; }}
  .brand span {{ color: var(--orange); }}
  nav {{ display: flex; gap: 24px; font-size: 11px; letter-spacing: .14em;
         color: var(--dim); text-transform: uppercase; }}
  nav a {{ text-decoration: none; }}
  nav a:hover {{ color: var(--ink); }}

  .hero {{
    position: relative; overflow: hidden;
    background:
      radial-gradient(60% 55% at 50% 78%, rgba(238,121,68,.22), transparent 60%),
      radial-gradient(45% 45% at 22% 18%, rgba(61,79,191,.25), transparent 60%),
      radial-gradient(50% 50% at 80% 30%, rgba(120,72,190,.18), transparent 60%),
      linear-gradient(180deg, #05060d 0%, #0b0d20 42%, #1c0f26 72%, #2a1020 100%);
  }}
  .hero-inner {{ padding: 90px 0 70px; text-align: center; position: relative; }}
  .eyebrow {{ font-size: 11px; letter-spacing: .42em; color: var(--dim);
              text-transform: uppercase; margin-bottom: 20px; }}
  .hero h1 {{
    margin: 0 auto; max-width: 1100px;
    font-size: clamp(54px, 9vw, 118px); line-height: .94;
    font-weight: 700; letter-spacing: -.03em;
  }}
  .hero h1 em {{
    font-style: normal;
    background: linear-gradient(180deg, #2b3fb0 0%, #7f63d6 35%,
      #d973a0 60%, #ee7944 82%, #f9c36d 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
  }}
  .hero p {{ max-width: 720px; margin: 24px auto 0; color: #c8cfe6;
             font-size: clamp(15px, 1.5vw, 18px); line-height: 1.6; }}
  .hero-words {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 8px; margin: 46px 0 8px; align-items: baseline;
  }}
  .hero-words span {{
    font-size: clamp(34px, 5.6vw, 78px); font-weight: 700;
    line-height: 1.1; white-space: nowrap;
    background: linear-gradient(180deg, #f8f0e2 0%, #ffd7b8 55%, #ee7944 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
  }}
  .slider {{
    margin-top: 30px; display: flex; align-items: center; justify-content: center;
    gap: 18px; color: var(--dim); font-size: 11px; letter-spacing: .18em;
    text-transform: uppercase;
  }}
  .slider input {{ width: min(460px, 60vw); accent-color: var(--orange); }}
  .slider output {{ color: var(--orange); font-weight: 700; min-width: 34px; }}
  .stops {{ display: flex; justify-content: center; gap: 26px; margin-top: 8px;
            color: var(--dim2); font-size: 10px; letter-spacing: .16em;
            text-transform: uppercase; }}

  section {{ padding: 86px 0; border-top: 1px solid var(--line); }}
  .section-head {{ display: flex; justify-content: space-between; align-items: end;
                   gap: 24px; margin-bottom: 34px; }}
  .kicker {{ font-size: 11px; letter-spacing: .28em; color: var(--orange);
             text-transform: uppercase; font-weight: 700; }}
  h2 {{ font-size: clamp(34px, 4.4vw, 58px); line-height: 1.04; margin: 10px 0 0;
        font-weight: 700; letter-spacing: -.02em; }}
  .section-head p {{ max-width: 460px; color: var(--dim); font-size: 14px;
                     line-height: 1.6; margin: 0; }}
  .cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }}
  .card {{
    border: 1px solid var(--line); border-radius: 20px; padding: 26px 26px 20px;
    background: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,.015));
    overflow: hidden;
  }}
  .card-head {{ display: flex; justify-content: space-between; gap: 16px;
                align-items: baseline; }}
  .card-head .kicker {{ color: var(--dim); }}
  .native {{ display: block; font-size: 22px; margin-top: 4px; color: #e9dfcf; }}
  .meta {{ font-size: 10px; letter-spacing: .12em; color: var(--dim2);
           text-transform: uppercase; text-align: right; }}
  .display {{ font-size: clamp(46px, 5.8vw, 88px); font-weight: 700;
              line-height: 1.15; margin: 18px 0 4px; color: #f8f1e4; }}
  .sentence {{ font-size: clamp(17px, 1.8vw, 23px); line-height: 1.5;
               color: #c3cbe4; margin: 10px 0 18px; }}
  .spectrum-row {{ display: flex; justify-content: space-between; align-items: end;
                   border-top: 1px solid var(--line); padding-top: 14px; }}
  .spectrum {{ font-size: 38px; font-weight: 700; line-height: 1.2; }}
  .spectrum-row small {{ color: var(--dim2); font-size: 10px; letter-spacing: .12em;
                         text-transform: uppercase; }}

  .gallery {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
  .gallery figure {{ margin: 0; border: 1px solid var(--line); border-radius: 18px;
                     overflow: hidden; background: var(--panel); }}
  .gallery .wide {{ grid-column: 1 / -1; }}
  .gallery img {{ display: block; width: 100%; height: auto; }}
  .gallery figcaption {{ padding: 12px 16px; font-size: 10px; letter-spacing: .14em;
                         color: var(--dim2); text-transform: uppercase; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--line);
            vertical-align: top; }}
  th {{ color: var(--dim2); font-size: 10px; letter-spacing: .16em;
        text-transform: uppercase; font-weight: 700; }}
  td a {{ color: #ffd0b0; text-decoration: none; }}
  td a:hover {{ color: #fff; }}
  .notes {{ display: grid; grid-template-columns: 1fr 1fr; gap: 26px; color: var(--dim);
            font-size: 14px; line-height: 1.65; }}
  .notes strong {{ color: var(--ink); }}
  footer {{ border-top: 1px solid var(--line); padding: 30px 0 44px; color: var(--dim2);
            font-size: 11px; letter-spacing: .06em; }}
  @media (max-width: 860px) {{
    .cards, .gallery, .notes {{ grid-template-columns: 1fr; }}
    .hero-words {{ grid-template-columns: 1fr 1fr; gap: 18px; }}
    .section-head {{ display: block; }}
    .section-head p {{ margin-top: 14px; }}
  }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <div class="brand">KALLAR</div>
    <nav>
      <a href="#scripts">Scripts</a>
      <a href="#axis">Axis</a>
      <a href="#specimen">Specimen</a>
      <a href="#download">Download</a>
    </nav>
  </div>
</header>

<section class="hero" style="border-top:0">
  <div class="wrap hero-inner">
    <div class="eyebrow">Multiscript · Devanagari · Tamil · Telugu · Kannada</div>
    <h1>Five scripts.<br><em>One aperture.</em></h1>
    <p>The APER axis carries the lotus-gateway idea from Malayalam into four
      more Indian scripts. One variable system, one spectrum, one build
      pipeline — with each script's own shaping and metrics.</p>
    <div class="hero-words">{HERO_WORDS}</div>
    <div class="slider">
      <span>APER</span>
      <input id="aper" type="range" min="0" max="100" value="100"
             aria-label="Aperture axis">
      <output id="aperVal">100</output>
    </div>
    <div class="stops"><span>0 · Round</span><span>50 · Bloom</span>
      <span>100 · Petal</span></div>
  </div>
</section>

<section id="scripts">
  <div class="wrap">
    <div class="section-head">
      <div><div class="kicker">01 / Scripts</div><h2>The same idea,<br>four grammars.</h2></div>
      <p>Move the APER slider above and every script below follows. Devanagari
        keeps its shirorekha straight while the counters open; Telugu and
        Kannada take the full loop treatment; Tamil stays gentler.</p>
    </div>
    <div class="cards">{CARDS}</div>
  </div>
</section>

<section id="axis">
  <div class="wrap">
    <div class="section-head">
      <div><div class="kicker">02 / Axis</div><h2>Round → Bloom → Petal</h2></div>
      <p>The transform moves existing TrueType points, never adds or removes
        them, so every intermediate APER value is a designed, point-compatible
        master.</p>
    </div>
    <div class="gallery">
      <figure class="wide">
        <img src="data:image/jpeg;base64,{AXIS_IMG}" alt="APER axis across four scripts">
        <figcaption>The APER axis across Devanagari, Tamil, Telugu and Kannada</figcaption>
      </figure>
    </div>
  </div>
</section>

<section id="specimen">
  <div class="wrap">
    <div class="section-head">
      <div><div class="kicker">03 / Specimen</div><h2>In context</h2></div>
      <p>Poster, sheets and the five-script hero are generated from the same
        fonts and the same aperture logic.</p>
    </div>
    <div class="gallery">
      <figure class="wide">
        <img src="data:image/jpeg;base64,{HERO_IMG}" alt="Kallar multiscript hero">
        <figcaption>Five scripts · APER 100 · spectrum</figcaption>
      </figure>
      {SHEETS}
    </div>
  </div>
</section>

<section id="download">
  <div class="wrap">
    <div class="section-head">
      <div><div class="kicker">04 / Download</div><h2>Files</h2></div>
      <p>Each script ships as a variable Regular and Bold, static Round/Petal
        instances, and COLRv1 Spectrum builds. WOFF2 for the web, TTF for
        desktop and print.</p>
    </div>
    <table>
      <thead><tr><th>Script</th><th>Variable</th><th>Static</th><th>Spectrum</th></tr></thead>
      <tbody>{DOWNLOADS}</tbody>
    </table>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="notes">
      <div>
        <p><strong>Derivative model.</strong> The Malayalam branch is a
          derivative of Manjari. The Devanagari, Tamil, Telugu and Kannada
          branches are derivatives of the corresponding Noto Sans faces. The
          aperture engine, APER axis, Spectrum treatment, metrics and specimens
          are original work by the Kallar Project Authors. All bases are used
          under the SIL Open Font License 1.1.</p>
        <p><strong>Independence.</strong> This project is independent and is
          not affiliated with or endorsed by Google, the Noto Project Authors,
          Sarvam AI, or SMC. The blue → orange spectrum is an homage to
          Sarvam's visual language.</p>
      </div>
      <div>
        <p><strong>Script notes.</strong> Devanagari uses an absolute freeze at
          the headline so the shirorekha never bends. Tamil uses a gentler
          profile because its counters are fewer and more open. Telugu and
          Kannada take the full hole-and-crown warp, where their round loops
          carry the petal most naturally.</p>
        <p><strong>Technical.</strong> Every master is point-compatible. The
          build is deterministic: repeated runs produce byte-identical TTF and
          WOFF2 files. Fonts are subset-free and retain the full upstream
          coverage, including conjuncts, reph forms, matras and Vedic
          extensions where the base supports them.</p>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    Kallar · v1.100 · SIL Open Font License 1.1 · Malayalam +
    Devanagari + Tamil + Telugu + Kannada · <a href="index.html">Malayalam
    specimen</a> · <a href="../README.md">README</a>
  </div>
</footer>

<script>
  const slider = document.getElementById('aper');
  const out = document.getElementById('aperVal');
  const copies = document.querySelectorAll('.aper-copy');
  function update() {{
    const v = slider.value;
    out.textContent = v;
    copies.forEach(el => el.textContent = v);
    document.querySelectorAll('.ml').forEach(el => {{
      el.style.fontVariationSettings = '"APER" ' + v;
    }});
  }}
  slider.addEventListener('input', update);
  update();
</script>
</body>
</html>
"""

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fp:
    fp.write(HTML)
print(f"wrote {OUT} ({len(HTML) / 1024:.0f} KB)")

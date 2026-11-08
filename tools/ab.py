#!/usr/bin/env python3
"""A/B compare rows: each row shaped with Ezhuthu (top) and reference (bottom)."""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EZHUTHU = os.path.join(ROOT, "fonts/Ezhuthu-Regular.ttf")
REF = "/tmp/manjari-ref/out/Manjari-Regular.otf"


def compare(rows, out="proofs/ab.png", size=90, mine=EZHUTHU, ref=REF):
    imgs = []
    for i, row in enumerate(rows):
        band = []
        for fontpath in (mine, ref):
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as fp:
                tmp = fp.name
            subprocess.run([sys.executable, os.path.join(ROOT, "tools", "render.py"),
                            fontpath, row, tmp, "--size", str(size), "--baseline"],
                           check=True, capture_output=True)
            band.append(Image.open(tmp))
            os.unlink(tmp)
        # normalize heights: crop to ink + baseline, keep line height
        h = max(im.height for im in band)
        w = max(im.width for im in band)
        line = Image.new("L", (w, h), 255)
        off = 0
        px = line.load()
        for im in band:
            line.paste(im, (0, off) if False else (0, 0))
        line = Image.new("RGB", (w, h), (255, 255, 255))
        line.paste(band[0].convert("RGB"), (0, 0))
        d = ImageDraw.Draw(line)
        d.line([(0, band[0].height - 2), (band[1].width, band[0].height - 2)], fill=(150, 150, 150))
        line.paste(band[1].convert("RGB"), (0, band[0].height))
        imgs.append(line)
    W = max(i.width for i in imgs) + 20
    H = sum(i.height for i in imgs) + 10 * len(imgs)
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    y = 0
    for i, line in enumerate(imgs):
        sheet.paste(line, (10, y))
        y += line.height + 10
    sheet.save(out)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    rows = [
        "ക ച ത ബ മ",
        "യ ര ല വ ശ സ",
        "അ ആ ഇ ഉ എ ഒ",
        "കി മാ തു ക്ര ശ്രീ മലയാളം",
    ]
    compare(rows, *sys.argv[1:])

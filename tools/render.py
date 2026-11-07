#!/usr/bin/env python3
"""Render text with a font to PNG using uharfbuzz (shaping) + freetype (rasterize).

Used to proof both reference fonts and the font built by this project.
"""
import argparse
import sys

import uharfbuzz as hb
import freetype
from PIL import Image


def load_hb_font(path, size):
    with open(path, "rb") as f:
        data = f.read()
    face = hb.Face(data)
    font = hb.Font(face)
    upem = face.upem
    font.scale = (size * 64, size * 64)  # 26.6 fixed point
    hb.ot_font_set_funcs(font)
    return font, upem


def shape(font, text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    infos = buf.glyph_infos
    positions = buf.glyph_positions
    return list(zip(infos, positions))


def render(font_path, text, out_path, size=64, pad=20, fg=(30, 30, 30), bg=(255, 255, 255), show_baseline=False):
    hbfont, upem = load_hb_font(font_path, size)
    ftface = freetype.Face(font_path)
    ftface.set_char_size(size * 64)

    shaped = shape(hbfont, text)

    # Single pass: load each glyph, snapshot its pixels immediately (freetype
    # reuses the glyph slot, so we must copy the buffer right away).
    pen_x = 0.0
    top_max = 0.0      # max distance of glyph-top above baseline
    bottom_max = 0.0   # max distance of glyph-bottom below baseline
    glyphs = []
    for info, pos in shaped:
        gid = info.codepoint
        x_adv = pos.x_advance / 64.0
        x_off = pos.x_offset / 64.0
        y_off = pos.y_offset / 64.0  # positive = up

        ftface.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
        bitmap = ftface.glyph.bitmap
        left = ftface.glyph.bitmap_left
        top = ftface.glyph.bitmap_top  # px of bitmap top above baseline
        w, rows, pitch = bitmap.width, bitmap.rows, bitmap.pitch
        data = bytes(bitmap.buffer) if (w and rows) else b""

        gx = pen_x + x_off + left          # x of bitmap left edge
        top_above = top + y_off            # glyph top above baseline
        bottom_below = rows - top - y_off  # glyph bottom below baseline
        top_max = max(top_max, top_above)
        bottom_max = max(bottom_max, bottom_below)
        glyphs.append((data, w, rows, pitch, gx, top, y_off))
        pen_x += x_adv

    width = int(pen_x) + 2 * pad
    height = int(top_max + bottom_max) + 2 * pad
    if width <= 0 or height <= 0:
        print("nothing to render", file=sys.stderr)
        return

    img = Image.new("RGB", (width, height), bg)
    baseline_y = pad + top_max  # baseline position in image coords

    for data, w, rows, pitch, gx, top, y_off in glyphs:
        px = int(round(gx)) + pad
        py = int(round(baseline_y - top - y_off))
        if w == 0 or rows == 0:
            continue
        stride = abs(pitch) if pitch else w
        glyph_img = Image.new("L", (w, rows), 0)
        gp = glyph_img.load()
        for r in range(rows):
            base = r * stride
            for c in range(w):
                v = data[base + c]
                if v:
                    gp[c, r] = v
        img.paste(fg, (px, py), glyph_img)

    if show_baseline:
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        d.line([(0, int(baseline_y)), (width, int(baseline_y))], fill=(255, 0, 0), width=1)

    img.save(out_path)
    print(f"wrote {out_path}  ({width}x{height})  glyphs={len(glyphs)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("text")
    ap.add_argument("out")
    ap.add_argument("--size", type=int, default=64)
    ap.add_argument("--baseline", action="store_true")
    args = ap.parse_args()
    render(args.font, args.text, args.out, size=args.size, show_baseline=args.baseline)


if __name__ == "__main__":
    main()

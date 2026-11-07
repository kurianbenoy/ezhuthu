#!/usr/bin/env python3
"""Render a grid sheet of shaped text cells to PNG (for proofing)."""
import sys
import uharfbuzz as hb
import freetype
from PIL import Image, ImageDraw

sys.path.insert(0, "tools")


def shape_cells(font_path, size=48):
    blob = hb.Blob.from_file_path(font_path)
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (size, size)  # advance values in px for a size-px em
    ftface = freetype.Face(font_path)
    ftface.set_char_size(size * 64)
    return font, ftface


def render_cells(font_path, cells, out_path, size=48, pad=12, baseline=True):
    """cells: list of strings (each shaped independently). Grid montage."""
    font, ftface = shape_cells(font_path, size)
    images = []
    for text in cells:
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(font, buf, {"kern": True, "liga": True, "calt": True})
        pen_x = 0.0
        hi = -1e9
        lo = 1e9
        glyphs = []
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gid = info.codepoint
            ftface.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
            bitmap = ftface.glyph.bitmap
            data = bytes(bitmap.buffer) if (bitmap.width and bitmap.rows) else b""
            glyphs.append({
                "pen_x": pen_x + pos.x_offset / 64.0,
                "y_off": pos.y_offset / 64.0,
                "left": ftface.glyph.bitmap_left,
                "top": ftface.glyph.bitmap_top,
                "w": bitmap.width, "rows": bitmap.rows, "pitch": bitmap.pitch,
                "adv": pos.x_advance / 64.0,
                "data": data,
            })
            pen_x += pos.x_advance / 64.0
            if data:
                # bitmap top: distance above baseline (px, up>0); y_off moves up
                hi = max(hi, -glyphs[-1]["y_off"] + glyphs[-1]["top"])
                lo = min(lo, -glyphs[-1]["y_off"] + glyphs[-1]["top"] - glyphs[-1]["rows"])
        width = pen_x
        if not glyphs:
            hi, lo = 8, -8
            width = 10
        ascent = hi + pad
        height = hi - lo + 2 * pad
        img = Image.new("RGB", (max(2, int(width)) + 2 * pad, max(2, int(height))), (255, 255, 255))
        for g in glyphs:
            if g["w"] == 0 or g["rows"] == 0:
                continue
            stride = abs(g["pitch"]) or g["w"]
            glyph_img = Image.new("L", (g["w"], g["rows"]), 0)
            gp = glyph_img.load()
            for rr in range(g["rows"]):
                base = rr * stride
                for cc in range(g["w"]):
                    v = g["data"][base + cc]
                    if v:
                        gp[cc, rr] = v
            px = int(round(pad + g["pen_x"] + g["left"]))
            py = int(round(ascent - g["y_off"] - g["top"]))
            img.paste((30, 30, 30), (px, py), glyph_img)
        if baseline:
            d = ImageDraw.Draw(img)
            # find baseline y in local coords: ascent - 0
            by = int(ascent)
            if 0 <= by < img.height:
                d.line([(0, by), (img.width, by)], fill=255, width=2)
        images.append(img.convert("RGB"))
    # compose grid 8 wide
    cols = 8
    rows = (len(images) + cols - 1) // cols
    cw = max(i.width for i in images) + 16
    ch = max(i.height for i in images) + 34
    sheet = Image.new("L", (cols * cw, rows * ch), 255)
    d = ImageDraw.Draw(sheet)
    for i, img in enumerate(images):
        r, c = divmod(i, cols)
        x = c * cw + 8
        y = r * ch + 26
        sheet.paste(img, (x, y))
        d.text((c * cw + 10, r * ch + 4), text=cells[i], fill=0)
    sheet.save(out_path)
    print("wrote", out_path, sheet.size)


if __name__ == "__main__":
    fontpath = sys.argv[1]
    out = sys.argv[2]
    textfile = sys.argv[3]
    cells = open(textfile).read().split()
    render_cells(fontpath, cells, out)

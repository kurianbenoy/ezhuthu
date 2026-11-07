#!/usr/bin/env python3
"""ASCII preview tools for glyph design without a GUI.

- preview(glyph)   : rasterize a ufoLib2 Glyph (my parametric outlines) to ASCII
- ref_dump(text)   : shape `text` with a reference font (Manjari) and dump the
                     resulting glyph bitmaps as ASCII, so designs can be compared
                     to correct reference letterforms.
"""
import sys
import math

sys.path.insert(0, "tools")

REF_FONT = "/tmp/manjari-ref/out/Manjari-Regular.otf"


# ---------------------------------------------------------------------------
# tiny even-odd scanline rasterizer over flattened bezier contours
# ---------------------------------------------------------------------------
def _flatten(glyph, scale=1.0, dx=0.0, dy=0.0):
    """Return list of polylines (list of (x,y)) for glyph contours."""
    polys = []
    cur = []
    start = None
    last = None

    def bez(p0, p1, p2, p3, n=12):
        pts = []
        for i in range(1, n + 1):
            t = i / n
            mt = 1 - t
            x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
            y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
            pts.append((x, y))
        return pts

    class _Pen:
        def moveTo(self, p):
            nonlocal cur, start, last
            cur = [(p[0] * scale + dx, p[1] * scale + dy)]
            start = cur[0]
            last = cur[0]

        def lineTo(self, p):
            nonlocal last
            p = (p[0] * scale + dx, p[1] * scale + dy)
            cur.append(p)
            last = p

        def curveTo(self, c1, c2, p):
            nonlocal last
            c1 = (c1[0] * scale + dx, c1[1] * scale + dy)
            c2 = (c2[0] * scale + dx, c2[1] * scale + dy)
            p = (p[0] * scale + dx, p[1] * scale + dy)
            cur.extend(bez(last, c1, c2, p))
            last = p

        def qCurveTo(self, *pts):
            # treat as line chain (we never emit quads)
            for p in pts:
                if p is not None:
                    self.lineTo(p)

        def closePath(self):
            nonlocal cur
            if cur:
                polys.append(cur)
                cur = []

        def endPath(self):
            self.closePath()

        def addComponent(self, baseName, transformation):
            pass

    glyph.draw(_Pen())
    return polys


def _raster(polys, cols=64, rows=None, xmin=None, ymin=None, xmax=None, ymax=None):
    """Even-odd fill polys into an ASCII grid. Returns list of strings."""
    if not polys:
        return ["(empty)"]
    if xmin is None:
        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
    if xmax <= xmin:
        xmax = xmin + 1
    if ymax <= ymin:
        ymax = ymin + 1
    if rows is None:
        rows = max(4, int(cols * (ymax - ymin) / (xmax - xmin) * 0.5))  # 0.5 = char aspect
    grid = [["."] * cols for _ in range(rows)]
    inv = 1.0 / (xmax - xmin)
    for row in range(rows):
        # sample point y (center) in font units, y axis UP (flip for display)
        y = ymax - (row + 0.5) * (ymax - ymin) / rows
        # gather crossings
        xs = []
        for poly in polys:
            n = len(poly)
            for i in range(n):
                x0, y0 = poly[i]
                x1, y1 = poly[(i + 1) % n]
                if (y0 > y) != (y1 > y):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            a, b = xs[i], xs[i + 1]
            ca = int((a - xmin) * inv * cols)
            cb = int((b - xmin) * inv * cols)
            ca = max(0, min(cols - 1, ca))
            cb = max(0, min(cols - 1, cb))
            for c in range(ca, cb + 1):
                grid[row][c] = "#"
    return ["".join(r) for r in grid]


def preview(glyph, cols=64, label=""):
    polys = _flatten(glyph)
    art = _raster(polys, cols=cols)
    if label:
        print(f"--- {label} (width={glyph.width}) ---")
    for line in art:
        print(line)


# ---------------------------------------------------------------------------
# reference font ASCII dump: shape text, rasterize each output glyph
# ---------------------------------------------------------------------------
def ref_dump(text, font_path=REF_FONT, size=48, cols=None):
    import uharfbuzz as hb
    import freetype

    data = open(font_path, "rb").read()
    face = hb.Face(data)
    font = hb.Font(face)
    upem = face.upem
    font.scale = (size * 64, size * 64)
    hb.ot_font_set_funcs(font)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)

    ft = freetype.Face(font_path)
    ft.set_char_size(size * 64)

    from fontTools.ttLib import TTFont

    tt = TTFont(font_path)
    order = tt.getGlyphOrder()

    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gid = info.codepoint
        name = order[gid] if gid < len(order) else f"gid{gid}"
        ft.load_glyph(gid, freetype.FT_LOAD_RENDER)
        b = ft.glyph.bitmap
        w, rws = b.width, b.rows
        print(f"--- ref [{text[info.cluster]}] glyph={name} adv={pos.x_advance/64:.0f} "
              f"xoff={pos.x_offset/64:.0f} yoff={pos.y_offset/64:.0f} "
              f"top={ft.glyph.bitmap_top} left={ft.glyph.bitmap_left} ---")
        if w == 0 or rws == 0:
            continue
        stride = abs(b.pitch) if b.pitch else w
        buf_ = bytes(b.buffer)
        # downsample x2 for aspect
        for row in range(0, rws, 2):
            line = ""
            for c in range(0, w, 2):
                v = max(buf_[row * stride + min(c + 1, w - 1)] if row + 0 < rws else 0,
                        buf_[row * stride + c])
                line += "#" if v > 110 else ("+" if v > 40 else ".")
            print(line)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "ref":
        ref_dump(sys.argv[2])
    else:
        print("usage: preview.py ref '<text>'")

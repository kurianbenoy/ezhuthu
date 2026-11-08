#!/usr/bin/env python3
"""Exact outline primitives for building Malayalam glyphs programmatically.

A glyph is a set of constant-width strokes with round terminals (the same
concept as Nupuram's MetaPost round-pen, computed exactly in Python):

  * arc stroke  - a circular-arc band (open loop / hook / curl)
  * ring        - a closed annulus (loop / "o")
  * capsule     - a straight stroke with semicircular caps (stem / tail / bar)
  * dot         - a filled circle

Strokes are drawn as cubic-bezier closed contours into a ufoLib2 glyph through
its segment pen. `GlyphBuilder.union()` then merges overlaps into a clean
single outline using booleanOperations (same as ufo2ft's RemoveOverlapsFilter).
"""
import math

from booleanOperations import union as _bo_union
from booleanOperations import BooleanOperationsError


# ---------------------------------------------------------------------------
# low-level bezier arc drawing into a *segment* pen
# ---------------------------------------------------------------------------
def _arc_seg(pen, cx, cy, r, a0, a1):
    """Append a single cubic bezier for the arc a0->a1 (radians; signed sweep).
    Assumes the pen's current point is already at the arc start."""
    sweep = a1 - a0
    k = 4.0 / 3.0 * math.tan(sweep / 4.0)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    tx0, ty0 = -math.sin(a0), math.cos(a0)
    tx1, ty1 = -math.sin(a1), math.cos(a1)
    c1 = (x0 + k * r * tx0, y0 + k * r * ty0)
    c2 = (x1 - k * r * tx1, y1 - k * r * ty1)
    pen.curveTo(c1, c2, (x1, y1))


def _arc(pen, cx, cy, r, a0, a1, move=False):
    """Append arc a0->a1 (radians, signed sweep) split into <=90deg beziers.
    If move, moveTo the start point first; else assume pen is at start."""
    sweep = a1 - a0
    if abs(sweep) < 1e-9:
        return
    n = max(1, int(math.ceil(abs(sweep) / (math.pi / 2.0))))
    step = sweep / n
    if move:
        pen.moveTo((cx + r * math.cos(a0), cy + r * math.sin(a0)))
    a = a0
    for _ in range(n):
        _arc_seg(pen, cx, cy, r, a, a + step)
        a += step


def _circle(pen, cx, cy, r, ccw=True):
    a1 = 2 * math.pi if ccw else -2 * math.pi
    _arc(pen, cx, cy, r, 0.0, a1, move=True)
    pen.closePath()


# ---------------------------------------------------------------------------
# primitives (draw into a segment pen)
# ---------------------------------------------------------------------------
def draw_arc_stroke(pen, cx, cy, r, width, a0_deg, a1_deg):
    """Constant-width stroke along a circular arc (degrees, CCW a0->a1)."""
    a0, a1 = math.radians(a0_deg), math.radians(a1_deg)
    ro = r + width / 2.0
    ri = max(1.0, r - width / 2.0)
    cr = width / 2.0
    ex, ey = cx + r * math.cos(a1), cy + r * math.sin(a1)   # end centre
    sx, sy = cx + r * math.cos(a0), cy + r * math.sin(a0)   # start centre
    # outer arc a0 -> a1
    _arc(pen, cx, cy, ro, a0, a1, move=True)
    # end cap (semicircle around end centre), a1 -> a1+pi
    _arc(pen, ex, ey, cr, a1, a1 + math.pi)
    # inner arc back a1 -> a0 (clockwise)
    _arc(pen, cx, cy, ri, a1, a0)
    # start cap (semicircle around start centre), a0+pi -> a0+2pi
    _arc(pen, sx, sy, cr, a0 + math.pi, a0 + 2 * math.pi)
    pen.closePath()


def draw_ring(pen, cx, cy, r, width):
    """Closed annulus (loop)."""
    ro = r + width / 2.0
    ri = max(1.0, r - width / 2.0)
    _circle(pen, cx, cy, ro, ccw=True)
    _circle(pen, cx, cy, ri, ccw=False)


def draw_capsule(pen, x0, y0, x1, y1, width):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1e-6:
        draw_dot(pen, x0, y0, width)
        return
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    r = width / 2.0
    a_perp = math.atan2(py, px)
    pen.moveTo((x0 + px * r, y0 + py * r))
    pen.lineTo((x1 + px * r, y1 + py * r))
    _arc(pen, x1, y1, r, a_perp, a_perp + math.pi)         # end cap
    pen.lineTo((x0 - px * r, y0 - py * r))
    _arc(pen, x0, y0, r, a_perp + math.pi, a_perp + 2 * math.pi)  # start cap
    pen.closePath()


def draw_dot(pen, cx, cy, diameter):
    _circle(pen, cx, cy, diameter / 2.0, ccw=True)


# ---------------------------------------------------------------------------
# builder
# ---------------------------------------------------------------------------
class GlyphBuilder:
    def __init__(self, glyph):
        self.glyph = glyph          # ufoLib2 Glyph
        self.pen = glyph.getPen()

    # fluent primitive wrappers --------------------------------------------
    def arc(self, cx, cy, r, width, a0, a1):
        draw_arc_stroke(self.pen, cx, cy, r, width, a0, a1)
        return self

    def loop(self, cx, cy, r, width):
        draw_ring(self.pen, cx, cy, r, width)
        return self

    def stem(self, x0, y0, x1, y1, width):
        draw_capsule(self.pen, x0, y0, x1, y1, width)
        return self

    def bar(self, x0, y0, x1, y1, width):
        return self.stem(x0, y0, x1, y1, width)

    def dot(self, cx, cy, diameter):
        draw_dot(self.pen, cx, cy, diameter)
        return self

    def raw(self, fn):
        fn(self.pen)
        return self

    # output ----------------------------------------------------------------
    def union(self, round_points=True):
        """Merge all contours into a clean outline in-place."""
        if len(self.glyph) == 0:
            return self
        contours = list(self.glyph)
        self.glyph.clearContours()
        try:
            _bo_union(contours, self.glyph.getPointPen())
        except (BooleanOperationsError, ValueError, TypeError):
            # fall back to the un-merged contours
            for c in contours:
                self.glyph.appendContour(c)
        if round_points:
            from fontTools.misc.roundTools import otRound
            for contour in self.glyph:
                for p in contour.points:
                    p.x = otRound(p.x)
                    p.y = otRound(p.y)
        return self


# ---------------------------------------------------------------------------
# Malayalam stroke macros (attach-friendly, tuned via ASCII iteration)
# ---------------------------------------------------------------------------
import math as _m


def ml_arch(b, x0, x1, y_base, y_top, stroke):
    """Inverted-U arch: legs at x0,x1 from y_base, semicircular top at y_top."""
    r = (x1 - x0) / 2.0
    cy = y_top - r
    b.arc(x0 + r, cy, r, stroke, 0, 180)      # top semicircle (right->top->left)
    b.stem(x0, y_base, x0, cy + stroke * 0.2, stroke)
    b.stem(x1, y_base, x1, cy + stroke * 0.2, stroke)


def ml_arch_ring(b, x0, x1, y_base, y_top, stroke):
    """Stadium ring: arch top + joining bottom cup (legs connected at bottom)."""
    r = (x1 - x0) / 2.0
    cy = y_top - r
    b.arc(x0 + r, cy, r, stroke, 0, 180)
    b.arc(x0 + r, y_base + r, r, stroke, 180, 360)  # bottom cup (left->bottom->right)
    b.stem(x0, y_base + r, x0, cy, stroke)
    b.stem(x1, y_base + r, x1, cy, stroke)


def ml_arch_nested(b, x0, x1, y_top, y_base, stroke, shrink=0.55, inner_drop=100):
    """Nested double arch (tha-style): outer arch with legs, plus a smaller
    inner arch whose own legs stop above the bottom (the two tunnels must be
    clearly separated)."""
    r = (x1 - x0) / 2.0
    cy = y_top - r
    b.arc(x0 + r, cy, r, stroke, 0, 180)
    b.stem(x0, y_base, x0, cy, stroke)
    b.stem(x1, y_base, x1, cy, stroke)
    # inner arch: narrower, hung lower, legs ending well above baseline
    ix0 = x0 + (x1 - x0) * (0.5 - shrink / 2)
    ix1 = x0 + (x1 - x0) * (0.5 + shrink / 2)
    iy_top = y_top - inner_drop
    ir = (ix1 - ix0) / 2.0
    icy = iy_top - ir
    b.arc(ix0 + ir, icy, ir, stroke, 0, 180)
    b.stem(ix0, y_base + 40, ix0, icy, stroke)
    b.stem(ix1, y_base + 40, ix1, icy, stroke)


def ml_loop(b, cx, cy, ri, stroke):
    """Round loop (annulus) with inner radius ri."""
    b.loop(cx, cy, ri + stroke / 2.0, stroke)


def ml_eye(b, cx, cy, ri, stroke):
    ml_loop(b, cx, cy, ri, stroke)


def ml_cup(b, x_att, y_att, r, stroke, a_att=340, a_end=195):
    """Hook/cup hanging from attach point (x_att, y_att): sweeps down and to the
    left, terminal curling up. Band from a_end to a_att (CCW, passing bottom)."""
    cx = x_att - r * _m.cos(_m.radians(a_att))
    cy = y_att - r * _m.sin(_m.radians(a_att))
    b.arc(cx, cy, r, stroke, a_end, a_att)


def ml_curl_foot(b, x, y_base, r, stroke, direction=1):
    """Inward-curling foot at a leg bottom (x, y_base). direction=+1 curls right."""
    if direction > 0:
        cx, cy = x + r * _m.cos(_m.radians(-90)), y_base + r
        b.arc(cx, cy, r, stroke, 270 - 80, 270 + 90)   # from below, curling right-up
    else:
        cx, cy = x - r * _m.cos(_m.radians(-90)), y_base + r
        b.arc(cx, cy, r, stroke, 270 - 90, 270 + 80)


def ml_crook(b, x, y, r, stroke, mirror=False):
    """Top curl at (x, y): stem-top curling over to the left and down
    (shepherd's crook). mirror=True curls to the right."""
    if not mirror:
        b.arc(x - r, y, r, stroke, 0, 240)
    else:
        b.arc(x + r, y, r, stroke, 300, 540)


def ml_flag_down(b, x, y, r, stroke):
    """Small flag at (x, y) curving down to the right (ii-sign bottom tick)."""
    b.arc(x + r, y, r, stroke, 180, 280)


def ml_c_left(b, cx, cy, r, stroke):
    """Big 'C' opening left (aa-sign): from bottom-left terminal, along bottom,
    up the right, over the top, to top-left terminal."""
    b.arc(cx, cy, r, stroke, 225, 495)


def ml_c_right(b, cx, cy, r, stroke):
    """'C' opening right (opens right)."""
    b.arc(cx, cy, r, stroke, 45, 315)


def ml_spiral(b, x_att, y_att, r, stroke):
    """Vocalic-r spiral hook: hangs from attach, sweeps left below, curls up
    into a small inner curl (spiral terminal)."""
    ml_cup(b, x_att, y_att, r, stroke, a_att=350, a_end=185)
    # inner curl at the cup tip
    cx = x_att - r * _m.cos(_m.radians(350))
    cy = y_att - r * _m.sin(_m.radians(350))
    tipx = cx - r * _m.cos(_m.radians(5))
    tipy = cy - r * _m.sin(_m.radians(5))
    b.arc(tipx + r * 0.32, tipy - r * 0.32, r * 0.32, stroke, 160, 420)


def ml_flag_diag(b, x, y, dx, dy, stroke):
    """Chillu flag: diagonal stroke from (x, y) going down-right by (dx, dy)."""
    b.stem(x, y, x + dx, y - dy, stroke)


def ml_bar(b, x0, x1, y, stroke):
    """Horizontal bar (capsule)."""
    b.stem(x0, y, x1, y, stroke)


def ml_zigzag(b, x_att, y_att, w, depth, stroke):
    """uu-hook: from attach descends, sweeps left, turns down at left edge,
    sweeps back right at greater depth (double sweep below baseline)."""
    r = w * 0.22
    # upper sweep: down-left cup
    ml_cup(b, x_att, y_att, w * 0.42, stroke, a_att=345, a_end=190)
    cx = x_att - w * 0.42 * _m.cos(_m.radians(345))
    cy = y_att - w * 0.42 * _m.sin(_m.radians(345))
    tipx = cx - w * 0.42 * _m.cos(_m.radians(10))
    tipy = cy - w * 0.42 * _m.sin(_m.radians(10))
    # lower sweep: turn down at tip then run right
    b.arc(tipx + r, tipy, r, stroke, 90, 270)
    b.stem(tipx, tipy - r, tipx + w * 0.75, tipy - r, stroke)

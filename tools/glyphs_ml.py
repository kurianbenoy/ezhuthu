#!/usr/bin/env python3
"""Ezhuthu Malayalam glyph designs.

Every glyph is drawn from exact geometric strokes (see tools/shapes.py macros)
following the structural vocabulary of modern Malayalam letterforms
(loop heads, arches, stadiums, nested arches, below-baseline hooks,
crooks, spirals), as analysed from reference SMC typefaces.

Draw functions are parameterised by an origin/scale dict `o` so the same
function draws the full-size consonant and its reduced subjoined form in
conjuncts. All strokes use the round-terminal pen for the soft, fluid look.
"""
import sys

sys.path.insert(0, "tools")
from shapes import (  # noqa: E402
    GlyphBuilder,
    ml_arch,
    ml_arch_ring,
    ml_arch_nested,
    ml_loop,
    ml_eye,
    ml_cup,
    ml_crook,
    ml_flag_down,
    ml_c_left,
    ml_c_right,
    ml_spiral,
    ml_flag_diag,
    ml_bar,
    ml_zigzag,
)
from svgglyph import SVGGlyph  # noqa: E402

BODY_TOP = 500


class Design:
    def __init__(self, name, stroke, sub, loop_ri, eye_ri, weight):
        self.name = name
        self.stroke = stroke
        self.sub = sub
        self.loop_ri = loop_ri
        self.eye_ri = eye_ri
        self.weight = weight


DESIGNS = {
    "Thin": Design("Thin", 38, 34, 66, 38, 200),
    "Regular": Design("Regular", 62, 54, 60, 34, 400),
    "Bold": Design("Bold", 92, 80, 48, 26, 700),
}


def O(x=0.0, y=0.0, s=1.0):
    return {"x": x, "y": y, "s": s}


class Ctx:
    """Coordinate context: local -> global transform + stroke selection.

    Design coordinates are 'generous' karshapan (x values up to ~900); the
    global X factor compresses x so that advances match the measured
    reference metrics (~0.47 of design x), while keeping y at body height
    0..500. Radii are NOT compressed (loops stay circular)."""

    X_FACTOR = 0.47
    MARGIN = 24  # lsb/rsb around art x extents

    def __init__(self, b, D, o):
        self.b = b
        self.D = D
        self.o = o
        self.st = D.stroke if o["s"] >= 0.99 else D.sub

    def x(self, v):
        return self.o["x"] + self.o["s"] * self.X_FACTOR * v

    def y(self, v):
        return self.o["y"] + self.o["s"] * v

    def s(self, v):
        return self.o["s"] * v

    # stroke wrappers -----------------------------------------------------
    def stem(self, x0, y0, x1, y1):
        self.b.stem(self.x(x0), self.y(y0), self.x(x1), self.y(y1), self.st)

    def bar(self, x0, x1, y):
        self.b.stem(self.x(x0), self.y(y), self.x(x1), self.y(y), self.st)

    def loop(self, cx, cy, ri):
        ml_loop(self.b, self.x(cx), self.y(cy), ri * self.o["s"], self.st * 0.72)

    def eye(self, cx, cy, ri=None):
        ml_eye(self.b, self.x(cx), self.y(cy), (ri or self.D.eye_ri) * self.o["s"], self.st * 0.78)

    def arch(self, x0, x1, y_base, y_top):
        ml_arch(self.b, self.x(x0), self.x(x1), self.y(y_base), self.y(y_top), self.st)

    def stadium(self, x0, x1, y_base, y_top):
        ml_arch_ring(self.b, self.x(x0), self.x(x1), self.y(y_base), self.y(y_top), self.st * 0.8)

    def nested(self, x0, x1, y_base, y_top, shrink=0.45, inner_drop=60):
        ml_arch_nested(self.b, self.x(x0), self.x(x1), self.y(y_top), self.y(y_base), self.st, shrink, inner_drop)

    def arc(self, cx, cy, r, width, a0, a1):
        self.b.arc(self.x(cx), self.y(cy), r * self.o["s"], width * self.o["s"], a0, a1)
        return self

    def cup(self, x, y, r, a_att=340, a_end=195):
        ml_cup(self.b, self.x(x), self.y(y), r * self.o["s"] * 0.66, self.st * 0.82, a_att, a_end)

    def crook(self, x, y, r, mirror=False):
        ml_crook(self.b, self.x(x), self.y(y), r * self.o["s"] * 0.7, self.st, mirror)

    def flag_down(self, x, y, r):
        ml_flag_down(self.b, self.x(x), self.y(y), r * self.o["s"], self.st)

    def c_left(self, cx, cy, r):
        ml_c_left(self.b, self.x(cx), self.y(cy), r * self.o["s"], self.st)

    def c_right(self, cx, cy, r):
        ml_c_right(self.b, self.x(cx), self.y(cy), r * self.o["s"], self.st)

    def spiral(self, x, y, r):
        ml_spiral(self.b, self.x(x), self.y(y), r * self.o["s"], self.st)

    def zigzag(self, x, y, w, depth):
        ml_zigzag(self.b, self.x(x), self.y(y), w * self.o["s"], depth * self.o["s"], self.st)

    def diag(self, x0, y0, x1, y1):
        self.b.stem(self.x(x0), self.y(y0), self.x(x1), self.y(y1), self.st)

    def dot(self, cx, cy, d):
        self.b.dot(self.x(cx), self.y(cy), d * self.o["s"])


# ---------------------------------------------------------------------------
# consonant bodies. Each takes (c: Ctx). Canonical body box: x 60..700,
# top 500. W (advance) comes from WIDTHS.
# ---------------------------------------------------------------------------
def ka(c):
    c.loop(250, 330, c.D.loop_ri)
    # tail: sweep out of the loop's lower-right, curling left at the end
    c.arc(480, 260, 200, c.st, 170, -40)
    c.cup(633, 121, 110)


def kha(c):
    c.loop(250, 330, c.D.loop_ri)
    c.diag(400, 450, 620, 170)
    c.cup(650, 110, 135)
    c.cup(600, 60, 150, a_att=345, a_end=170)  # below-baseline tail


def ga(c):
    c.loop(200, 350, 70)
    c.loop(520, 330, 92)
    c.bar(110, 615, 40)


def gha(c):
    c.stadium(60, 340, 0, 500)
    c.arch(320, 600, 0, 500)
    c.stem(680, 500, 680, 0)
    c.cup(680, 0, 160, a_att=350, a_end=175)


def nga(c):
    c.loop(230, 330, c.D.loop_ri)
    c.stem(500, 500, 500, 60)
    c.eye(610, 140, 46)


def ca(c):
    c.arch(80, 360, 0, 300)
    c.stem(600, 500, 600, 0)
    c.bar(80, 600, 30)


def cha(c):
    c.arch(80, 360, 0, 300)
    c.stem(560, 500, 560, 0)
    c.bar(80, 560, 30)
    c.cup(600, 40, 150, a_att=345, a_end=175)  # below tail


def ja(c):
    c.arch(90, 380, 0, 500)
    c.eye(470, 380, 46)
    c.bar(90, 560, 30)
    c.cup(560, 20, 120, a_att=345, a_end=180)


def jha(c):
    c.stadium(60, 340, 0, 500)
    c.arch(320, 600, 0, 500)
    c.stem(690, 500, 690, 30)
    c.cup(690, 30, 190, a_att=350, a_end=170)


def nya(c):
    c.loop(200, 330, c.D.loop_ri)
    c.stem(460, 500, 460, 0)
    c.arch(480, 760, 0, 500)


def tta(c):
    c.arch(90, 380, 0, 500)
    c.cup(90, 20, 70, a_att=265, a_end=105)   # left leg curls inward
    c.cup(400, 60, 160, a_att=345, a_end=175)  # right leg sweeps below, curls left


def ttha(c):
    c.loop(280, 270, 170)  # big ring body


def dda(c):
    c.arch(70, 320, 0, 400)
    c.stadium(340, 700, 0, 500)


def ddha(c):
    c.arch(70, 320, 0, 400)
    c.stadium(340, 700, 0, 500)
    c.eye(790, 300, 46)


def nna(c):
    c.arch(80, 340, 0, 500)
    c.cup(80, 25, 60, a_att=262, a_end=100)
    c.cup(340, 25, 60, a_att=278, a_end=80)
    c.stem(600, 500, 600, 0)
    c.arch(620, 940, 0, 500)
    c.cup(940, 25, 60, a_att=280, a_end=100)
    c.cup(620, 25, 60, a_att=260, a_end=80)


def tha(c):
    c.nested(80, 680, 0, 500)


def thha(c):
    c.stem(120, 500, 120, 0)
    c.arch(150, 620, 0, 500)
    c.bar(120, 620, 30)


def da(c):
    c.arch(120, 400, 0, 500)
    c.eye(490, 330, 46)
    c.cup(120, 30, 70, a_att=265, a_end=105)
    c.cup(400, 30, 70, a_att=275, a_end=75)


def dha(c):
    c.arch(70, 290, 0, 400)
    c.arch(310, 530, 0, 500)
    c.eye(600, 330, 46)


def na(c):
    c.arch(80, 330, 0, 500)
    c.stem(360, 500, 360, 0)
    c.crook(360, 500, 70)
    c.arch(390, 660, 0, 500)
    c.cup(80, 25, 60, a_att=262, a_end=100)
    c.cup(660, 25, 60, a_att=278, a_end=80)


def pa(c):
    c.arch(80, 360, 0, 470)
    c.stem(620, 500, 620, 0)
    c.bar(80, 620, 30)


def pha(c):
    c.arch(80, 360, 0, 470)
    c.stem(600, 500, 600, 0)
    c.arch(600, 880, 0, 500)
    c.bar(80, 880, 30)


def ba(c):
    c.loop(200, 330, c.D.loop_ri)
    c.arch(430, 700, 0, 500)
    c.cup(430, 25, 60, a_att=262, a_end=100)
    c.cup(700, 25, 60, a_att=278, a_end=80)
    c.stem(840, 500, 840, 0)
    c.bar(430, 840, 30)


def bha(c):
    c.arch(100, 430, 0, 500)
    c.eye(540, 330, 46)
    c.bar(100, 620, 30)
    c.cup(640, 20, 130, a_att=345, a_end=180)


def ma(c):
    c.arch(80, 620, 0, 500)
    c.diag(540, 440, 190, 90)
    c.bar(80, 620, 30)


def ya(c):
    c.arch(60, 300, 0, 500)
    c.arch(280, 500, 0, 500)
    c.stem(700, 500, 700, 0)
    c.bar(60, 500, 40)
    c.cup(700, 40, 70, a_att=280, a_end=100)


def ra(c):
    c.arch(80, 420, 0, 460)
    c.diag(400, 390, 170, 60)
    c.cup(170, 50, 80, a_att=270, a_end=90)
    c.bar(80, 300, 40)


def rra(c):
    c.arch(80, 380, 0, 460)
    c.cup(420, 60, 150, a_att=345, a_end=175)


def la(c):
    c.stadium(60, 340, 0, 500)
    c.stem(560, 500, 560, 0)
    c.bar(60, 560, 30)


def va(c):
    c.arch(80, 380, 0, 400)
    c.bar(80, 620, 30)
    c.stem(620, 30, 620, -60)
    c.cup(620, -60, 60)


def sha(c):
    c.arch(60, 300, 0, 460)
    c.cup(60, 25, 55, a_att=262, a_end=100)
    c.cup(300, 25, 55, a_att=278, a_end=80)
    c.nested(320, 700, 0, 500)


def ssa(c):
    c.arch(80, 340, 0, 500)
    c.arch(370, 570, 300, 500)   # small arch, top area
    c.stem(620, 500, 620, 0)
    c.bar(80, 620, 30)


def sa(c):
    c.arch(80, 360, 0, 500)
    c.stem(620, 500, 620, 0)
    c.arch(640, 1000, 0, 500)


def ha(c):
    c.arch(70, 300, 0, 400)
    c.arch(340, 740, 0, 500)
    c.bar(70, 740, 25)


def lla(c):
    c.arch(80, 360, 0, 460)
    c.diag(370, 390, 150, 60)
    c.cup(150, 50, 80, a_att=270, a_end=90)
    c.stem(80, 30, 80, -90)
    c.bar(80, 430, -120)


def llla(c):
    c.stem(80, 500, 80, 0)
    c.arch(110, 430, 0, 500)
    c.cup(300, -10, 120, a_att=345, a_end=185)


CONSONANTS = {
    "ക": (ka, 930), "ഖ": (kha, 980), "ഗ": (ga, 890), "ഘ": (gha, 1140),
    "ങ": (nga, 1000), "ച": (ca, 740), "ഛ": (cha, 1060), "ജ": (ja, 740),
    "ഝ": (jha, 1210), "ഞ": (nya, 1060), "ട": (tta, 620), "ഠ": (ttha, 600),
    "ഡ": (dda, 980), "ഢ": (ddha, 1060), "ണ": (nna, 1210), "ത": (tha, 870),
    "ഥ": (thha, 760), "ദ": (da, 640), "ധ": (dha, 930), "ന": (na, 930),
    "പ": (pa, 820), "ഫ": (pha, 1030), "ബ": (ba, 1210), "ഭ": (bha, 760),
    "മ": (ma, 680), "യ": (ya, 940), "ര": (ra, 710), "റ": (rra, 650),
    "ല": (la, 800), "വ": (va, 840), "ശ": (sha, 930), "ഷ": (ssa, 940),
    "സ": (sa, 1210), "ഹ": (ha, 1050), "ള": (lla, 620), "ഴ": (llla, 620),
}


# ---------------------------------------------------------------------------
# chillus: diagonal flag at top right + the consonant body
# ---------------------------------------------------------------------------
CHILLU_BODIES = {
    "ൻ": na, "ർ": ra, "ൽ": la, "ൾ": None, "ൺ": None, "ൖ": llla, "ൿ": ka,
}


def draw_chillu(c, body_fn, flag_x):
    ml_flag_diag(c.b, c.x(flag_x), c.y(560), 90 * c.o["s"], 200 * c.o["s"], c.st * 0.85)
    body_fn(c)


def chillu_ll(c):  # ൾ : flag + big ring
    ml_flag_diag(c.b, c.x(540), c.y(560), 90 * c.o["s"], 200 * c.o["s"], c.st * 0.85)
    c.loop(300, 270, 150)


def chillu_n(c):  # ൺ : flag + loop + stem + arch
    ml_flag_diag(c.b, c.x(640), c.y(560), 90 * c.o["s"], 200 * c.o["s"], c.st * 0.85)
    c.loop(200, 330, c.D.loop_ri)
    c.stem(460, 500, 460, 0)
    c.arch(480, 760, 0, 500)


# ---------------------------------------------------------------------------
# independent vowels
# ---------------------------------------------------------------------------
def va_a(c):
    c.stadium(60, 320, 0, 430)
    c.stem(430, 500, 430, 0)
    c.arch(450, 800, 0, 500)
    c.cup(450, 25, 60, a_att=262, a_end=100)
    c.cup(800, 25, 60, a_att=278, a_end=80)


def va_aa(c):
    va_a(c)
    c.c_left(1030, 270, 205)


def va_i(c):
    # seat hook top-right, long descender, inward curl at the foot
    c.diag(60, 430, 300, 500)
    c.stem(300, 500, 300, -80)
    c.crook(300, -80, 80)


def va_ii(c):
    va_i(c)
    c.crook(300, -80, 55, mirror=True)
    c.stem(60, -140, 60, -220)
    c.bar(60, 320, -260)


def va_u(c):
    # manjari-style "2": loop top, stem below baseline, foot curl
    c.loop(170, 330, 52)
    c.stem(310, 400, 310, -60)
    c.cup(310, -60, 80)


def va_uu(c):
    va_u(c)
    c.loop(430, 330, 52)
    c.stem(570, 400, 570, -60)
    c.cup(570, -60, 70)


def va_r(c):
    c.loop(200, 340, c.D.loop_ri)
    c.eye(470, 340, 60)
    c.cup(590, 300, 280, a_att=350, a_end=190)


def va_rr(c):
    c.loop(160, 340, c.D.loop_ri)
    c.eye(410, 340, 60)
    c.eye(640, 340, 60)
    c.cup(760, 300, 280, a_att=350, a_end=190)


def va_l(c):
    c.loop(220, 340, c.D.loop_ri)
    c.diag(400, 80, 480, -20)
    c.diag(480, -20, 380, -110)
    c.cup(380, -130, 70, a_att=20, a_end=200)


def va_ll(c):
    c.loop(200, 340, c.D.loop_ri)
    c.diag(380, 80, 460, -20)
    c.diag(460, -20, 360, -110)
    c.diag(360, -110, 500, -150)
    c.cup(500, -170, 70, a_att=20, a_end=200)


def va_e(c):
    c.stadium(60, 300, 0, 330)
    c.stadium(280, 560, 0, 500)


def va_ee(c):
    c.stadium(120, 360, 0, 330)
    c.stadium(340, 620, 0, 500)
    c.stem(120, 330, 120, -130)
    c.cup(120, -130, 70, a_att=190, a_end=350)


def va_ai(c):
    c.stadium(60, 300, 0, 330)
    c.stadium(280, 560, 0, 500)
    c.stadium(580, 820, 0, 330)
    c.stadium(800, 1080, 0, 500)


def va_o(c):
    c.nested(80, 560, 0, 500)
    c.cup(80, 30, 90, a_att=262, a_end=100)
    c.cup(560, 30, 90, a_att=278, a_end=80)


def va_oo(c):
    c.nested(240, 720, 0, 500)
    c.cup(240, 30, 90, a_att=262, a_end=100)
    c.cup(720, 30, 90, a_att=278, a_end=80)
    c.stem(80, 500, 80, -60)
    c.flag_down(80, -60, 70)


def va_au(c):
    c.nested(80, 560, 0, 500)
    c.cup(80, 30, 90, a_att=262, a_end=100)
    c.cup(560, 30, 90, a_att=278, a_end=80)
    au_mark(c, 760)


def au_mark(c, x0=0.0):
    """The ൗ au length mark shape at x0: small arch + descending leg + curl."""
    c.arch(x0 + 60, x0 + 220, 200, 460)
    c.stem(x0 + 220, 460, x0 + 220, 120)
    c.cup(x0 + 240, 100, 110, a_att=345, a_end=190)


VOWELS = {
    "അ": (va_a, 1320), "ആ": (va_aa, 1430), "ഇ": (va_i, 960),
    "ഈ": (va_ii, 1100), "ഉ": (va_u, 650), "ഊ": (va_uu, 900),
    "ഋ": (va_r, 820), "ൠ": (va_rr, 1000), "ഌ": (va_l, 1020),
    "ൡ": (va_ll, 1160), "എ": (va_e, 1100), "ഏ": (va_ee, 1100),
    "ഐ": (va_ai, 1750), "ഒ": (va_o, 670), "ഓ": (va_oo, 1100),
    "ഔ": (va_au, 1340),
}


# ---------------------------------------------------------------------------
# vowel signs and combining marks
# ---------------------------------------------------------------------------
def sign_aa(c):
    c.c_left(150, 270, 205)


def sign_i(c):
    # slanted seat with slight negative lsb, hook opening toward the base
    c.diag(-40, 10, 120, 430)
    c.crook(120, 460, 85)


def sign_i_wrap(c):
    # variant for ന: the hook curls back over the tall stem
    c.diag(-30, 400, 120, 690)
    c.crook(120, 690, 90)
    c.b.stem(c.x(120), c.y(690), c.x(120), c.y(500), c.st)
    c.crook(120, 500, 65, mirror=True)


def sign_ii(c):
    sign_i(c)
    c.crook(120, 460, 55, mirror=True)


def sign_u(c):
    # spacing ു: flat-bottom bowl + leg rising to body top
    c.ml_arch_ring(c.b, 20, 290, -260, 60, c.st) if False else None
    c.stadium(20, 290, -260, 80)
    c.stem(290, 80, 290, 330)


def sign_uu(c):
    # twin stacked bowls + leg
    c.stadium(70, 260, -140, 60)
    c.stadium(70, 260, -450, -160)
    c.stem(260, 60, 260, 330)


def sign_vocalic_r(c):
    c.spiral(60, 30, 140)


def sign_vocalic_rr(c):
    c.spiral(60, 30, 120)
    c.spiral(300, 30, 120)


def sign_vocalic_l(c):
    c.cup(90, 20, 90, a_att=345, a_end=195)


def sign_vocalic_ll(c):
    c.cup(90, 20, 90, a_att=345, a_end=195)
    c.cup(90, -60, 90, a_att=345, a_end=195)


def sign_e(c):
    c.stadium(40, 240, 0, 330)
    c.stadium(230, 460, 0, 500)


def sign_ee(c):
    c.stem(70, 500, 70, 30)
    c.eye(200, 430, 62)
    c.cup(300, 60, 100, a_att=335, a_end=185)


def sign_ai(c):
    c.stadium(40, 240, 0, 330)
    c.stadium(230, 460, 0, 500)
    c.stadium(500, 720, 0, 330)
    c.stadium(710, 940, 0, 500)


def virama(c):
    c.loop(-85, 690, 30)


def anusvara(c):
    c.loop(90, 320, 45)


def visarga(c):
    c.c_right(90, 430, 58)
    c.c_right(90, 280, 58)


def dot_reph(c):
    c.loop(60, 660, 26)


def combining_anusvara_above(c):
    c.loop(60, 690, 30)


def candrabindu(c):
    c.loop(60, 700, 28)
    c.crook(60, 760, 45)


def vertical_bar_virama(c):
    c.stem(-60, 760, -60, 620)


def circular_virama(c):
    c.loop(-60, 690, 26)


def virama_ya(c):
    c.diag(20, 480, 110, 140)
    c.cup(150, 110, 85, a_att=335, a_end=185)


def virama_va(c):
    c.stem(150, 500, 150, 20)
    c.bar(-80, 150, 20)


def virama_ra(c):
    c.crook(70, 480, 80)
    c.stem(70, 480, 70, 60)
    c.cup(70, 40, 140, a_att=350, a_end=175)


def virama_la(c):
    c.diag(60, 30, 120, -50)
    c.diag(120, -50, 40, -140)
    c.cup(40, -160, 60, a_att=20, a_end=200)


def u_drop(c):
    c.cup(0, 10, 65, a_att=345, a_end=195)


def uu_drop(c):
    c.zigzag(0, 10, 150, 95)


def r_drop(c):
    c.spiral(0, 10, 85)


def aa_anusvara(c):
    c.c_left(150, 270, 205)
    c.loop(150, 570, 42)


SIGNS = {
    "ാ": (sign_aa, 490), "ി": (sign_i, 155), "ീ": (sign_ii, 155),
    "ു": (sign_u, 390), "ൂ": (sign_uu, 480), "ൃ": (sign_vocalic_r, 190),
    "ൄ": (sign_vocalic_rr, 310), "ൢ": (sign_vocalic_l, 200),
    "ൣ": (sign_vocalic_ll, 200), "െ": (sign_e, 680), "േ": (sign_ee, 500),
    "ൈ": (sign_ai, 1310), "ൗ": (lambda c: au_mark(c, 0), 760),
    "ം": (anusvara, 390), "ഃ": (visarga, 330),
    "്": (virama, 0), "ൎ": (dot_reph, 120),
    "ഀ": (combining_anusvara_above, 120), "ഁ": (candrabindu, 120),
    "ാം": (aa_anusvara, 490),
}

# composite component glyphs (no unicode; anchored for attachment)
COMPONENTS = {
    "്യ": (virama_ya, 300), "്വ": (virama_va, 250),
    "്ര": (virama_ra, 400), "്ല": (virama_la, 220),
    "u_drop_sign": (u_drop, 160), "uu_drop_sign": (uu_drop, 260),
    "r_drop_sign": (r_drop, 200),
}

# o/oo/au cmap glyphs (harfbuzz decomposes these, kept for completeness)
def sign_o(c):
    sign_e(c)
    c.c_left(760, 270, 205)


def sign_oo(c):
    sign_ee(c)
    c.c_left(600, 270, 205)


def sign_au(c):
    sign_e(c)
    au_mark(c, 760)


SIGNS_CMAP_EXTRA = {
    "ൊ": (sign_o, 1310), "ോ": (sign_oo, 1110), "ൌ": (sign_au, 1570),
}


# ---------------------------------------------------------------------------
# conjuncts
# ---------------------------------------------------------------------------
ML_CONS_CONJUNCTS = [
    "ക്ക", "ക്ഷ", "ഗ്ഗ", "ങ്ങ", "ങ്ക", "ച്ച", "ച്ഛ", "ജ്ജ", "ഞ്ച", "ഞ്ഞ",
    "ട്ട", "ണ്ണ", "ണ്ഡ", "ണ്ട", "ഡ്ഡ", "ത്ത", "ത്ഥ", "ദ്ദ", "ദ്ധ", "ന്ന",
    "ന്ത", "ന്ധ", "ന്മ", "ന്റ", "പ്പ", "ബ്ബ", "മ്മ", "മ്പ", "യ്യ", "ല്ല",
    "വ്വ", "ശ്ച", "ശ്ശ", "സ്സ", "സ്റ്റ", "സ്ഥ", "സ്ത", "ഷ്ട", "ള്ള", "റ്റ",
]

ML_REPH_CONJUNCTS = [
    "ക്ര", "ഗ്ര", "ഘ്ര", "ച്ര", "ട്ര", "ഡ്ര", "ത്ര", "ദ്ര", "ധ്ര", "പ്ര",
    "ഫ്ര", "ബ്ര", "ഭ്ര", "മ്ര", "വ്ര", "ശ്ര", "സ്ര", "സ്ത്ര", "ഹ്ര", "ഷ്ര",
]

# subjoin styles: (mode, ox_offset_from_baseW, oy, scale)
SUBJOIN = {
    "റ": ("below", -320, -260, 0.55),
}
DEFAULT_SUBJOIN = ("right", -120, 0, 0.75)


def ra_sweep(c):
    """The rakaram sweep used in reph conjuncts (ക്ര etc.)."""
    c.stem(0, 480, 0, 60)
    c.cup(0, 40, 150, a_att=350, a_end=175)


def art_xmax(g):
    if any(c.points for c in g):
        return max(p.x for c in g for p in c.points)
    return 0


def draw_cons_conjunct(b, D, c1, c2):
    """Base consonant + subjoined second consonant, drawn into builder b."""
    fn1, w1 = CONSONANTS[c1]
    fn2, w2 = CONSONANTS[c2]
    mode, dx, oy, s = SUBJOIN.get(c2, DEFAULT_SUBJOIN)
    fn1(Ctx(b, D, O(0, 0, 1.0)))
    if mode == "right":
        ox = w1 + dx
        fn2(Ctx(b, D, O(ox, oy, s)))
        W = w1 + int(s * w2) - 250
    else:
        ox = w1 + dx
        fn2(Ctx(b, D, O(ox, oy, s)))
        W = w1 + int(s * w2) - 60
    return max(w1 + 80, W)


def draw_reph_conjunct(b, D, lig):
    """Base (consonant or conjunct) + rakaram sweep."""
    base = lig[:-2]  # strip ്ര
    if base in CONSONANTS:
        fn, w = CONSONANTS[base]
        fn(Ctx(b, D, O(0, 0, 1.0)))
    elif len(base) == 3 and base[1] == "്":
        w = draw_cons_conjunct(b, D, base[0], base[2])
    else:
        raise ValueError(f"unknown reph base: {base!r}")
    ra_sweep(Ctx(b, D, O(w - 30, 0, 0.85)))
    return w + 150


# ---------------------------------------------------------------------------
# glyph creation
# ---------------------------------------------------------------------------
def _anchors(g, W, base=False, vc=None, bottom=None, right=None):
    from ufoLib2.objects import Anchor

    if base:
        g.anchors.append(Anchor(name="vc", x=W / 2, y=0))
        g.anchors.append(Anchor(name="bottom", x=W - 80, y=0))
        g.anchors.append(Anchor(name="right", x=W, y=0))
        return
    if vc is not None:
        g.anchors.append(Anchor(name="vc", x=vc, y=0))
    if bottom is not None:
        g.anchors.append(Anchor(name="bottom", x=bottom, y=0))
    if right is not None:
        g.anchors.append(Anchor(name="right", x=right, y=0))


ZERO_WIDTH_MARKS = {"\u0d4d", "\u0d4e", "\u0d00", "\u0d01"}


def measure_width(g, default_W):
    """Auto advance: art x-extent + margins, clamped to W * X_FACTOR."""
    if any(c.points for c in g):
        xs = [p.x for c in g for p in c.points]
        if not xs:
            return int(default_W * Ctx.X_FACTOR)
        xmax = max(xs)
        adv = int(xmax) + Ctx.MARGIN
        return adv
    return int(default_W * Ctx.X_FACTOR)


def make_glyph(font, key, fn, D, W, unicodes=None, base=False,
               vc=None, bottom=None, right=None, overlay_origin=None):
    name = SVGGlyph.get_glyph_name(key)
    g = font.newGlyph(name)
    if unicodes:
        g.unicodes = unicodes
    b = GlyphBuilder(g)
    fn(Ctx(b, D, overlay_origin or O()))
    b.union()
    ch = unicodes[0] if unicodes else key
    if ch in ZERO_WIDTH_MARKS:
        g.width = 0
    else:
        g.width = measure_width(g, W)
    _anchors(g, g.width, base=base, vc=vc, bottom=bottom, right=right)
    return g


def build_ml(font, D):
    """Add all Malayalam glyphs to font. Returns set of glyph names."""
    made = set()
    # consonants ---------------------------------------------------------
    for ch, (fn, W) in CONSONANTS.items():
        make_glyph(font, ch, fn, D, W, unicodes=[ord(ch)], base=True)
        made.add(SVGGlyph.get_glyph_name(ch))
    # chillus ------------------------------------------------------------
    for ch in ["ൻ", "ർ", "ൽ", "ൾ", "ൺ", "ൖ", "ൿ"]:
        body = CHILLU_BODIES[ch]
        if body is None:
            fn = chillu_ll if ch == "ൾ" else chillu_n
            W = 940
            flag_x = 560 if ch == "ൾ" else 640
        else:
            fn = body
            W = CONSONANTS[
                {"ൻ": "ന", "ർ": "ര", "ൽ": "ല", "ൖ": "ഴ", "ൿ": "ക"}[ch]
            ][1]
            flag_x = W - 210
        W = W + 170

        def chillu_fn(c, fn=fn, flag_x=flag_x):
            draw_chillu(c, fn, flag_x)

        make_glyph(font, ch, chillu_fn, D, W, unicodes=[ord(ch)], base=True)
        made.add(SVGGlyph.get_glyph_name(ch))
    # independent vowels ---------------------------------------------------
    for ch, (fn, W) in VOWELS.items():
        make_glyph(font, ch, fn, D, W, unicodes=[ord(ch)], base=True)
        made.add(SVGGlyph.get_glyph_name(ch))
    # signs ---------------------------------------------------------------
    for ch, (fn, W) in SIGNS.items():
        uni = [ord(ch)] if len(ch) == 1 else None
        if ch in ("ൎ", "ഀ"):
            make_glyph(font, ch, fn, D, W, unicodes=uni, vc=60)
        elif ch in ("ൢ", "ൣ"):
            make_glyph(font, ch, fn, D, W, unicodes=uni, bottom=90)
        else:
            make_glyph(font, ch, fn, D, W, unicodes=uni)
        made.add(SVGGlyph.get_glyph_name(ch))
    # fail-safe wrap variant for നി (calt) --------------------------------
    g = font.newGlyph(SVGGlyph.get_glyph_name("ി") + ".wrap")
    g.width = SIGNS["ി"][1]
    b = GlyphBuilder(g)
    sign_i_wrap(Ctx(b, D, O()))
    b.union()
    made.add(g.name)
    # cmap-only o/oo/au signs ---------------------------------------------
    for ch, (fn, W) in SIGNS_CMAP_EXTRA.items():
        make_glyph(font, ch, fn, D, W, unicodes=[ord(ch)])
        made.add(SVGGlyph.get_glyph_name(ch))
    # archaic viramas (overlay marks, explicit names as used by GDEF) ------
    from ufoLib2.objects import Anchor

    for gname, fn, uni in [
        ("ml_vertical_bar_virama", vertical_bar_virama, 0x0D3B),
        ("ml_circular_virama", circular_virama, 0x0D3C),
    ]:
        g = font.newGlyph(gname)
        g.width = 0
        g.unicodes = [uni]
        b = GlyphBuilder(g)
        fn(Ctx(b, D, O()))
        b.union()
        made.add(gname)
    # composite components -------------------------------------------------
    for key, (fn, W) in COMPONENTS.items():
        ax = 60 if key == "്ല" else 0
        ay = 30 if key == "്ല" else 10
        g = make_glyph(font, key, fn, D, W)
        g.anchors.append(Anchor(name="right", x=ax, y=ay))
        made.add(g.name)
    # conjuncts -------------------------------------------------------------
    for lig in ML_CONS_CONJUNCTS:
        name = SVGGlyph.get_glyph_name(lig)
        g = font.newGlyph(name)
        b = GlyphBuilder(g)
        W = draw_cons_conjunct(b, D, lig[0], lig[2])
        g.width = max(W, 300)
        b.union()
        _anchors(g, g.width, base=True)
        made.add(name)
    for lig in ML_REPH_CONJUNCTS:
        name = SVGGlyph.get_glyph_name(lig)
        g = font.newGlyph(name)
        b = GlyphBuilder(g)
        W = draw_reph_conjunct(b, D, lig)
        g.width = max(W, 300)
        b.union()
        _anchors(g, g.width, base=True)
        made.add(name)
    return made

# ---------------------------------------------------------------------------
# rare Malayalam block glyphs (digits, historical numerals, NNNA, TTTA, ...)
# ---------------------------------------------------------------------------
def nnn(c):
    c.arch(80, 330, 0, 500)
    c.stem(360, 500, 360, 0)
    c.crook(360, 500, 70)
    c.arch(390, 660, 0, 500)
    c.cup(660, 25, 60, a_att=278, a_end=80)


def tts(c):
    c.arch(90, 380, 0, 520)
    c.cup(90, 20, 70, a_att=265, a_end=105)
    c.cup(400, 60, 160, a_att=345, a_end=175)


def avagraha(c):
    c.stem(160, 500, 80, 330)
    c.stem(160, 500, 245, 330)
    c.diag(160, 500, 160, 400)
    c.cup(160, 420, 100, a_att=345, a_end=195)


def para_sign(c):
    c.stem(60, 500, 60, 200)
    c.bar(30, 260, 350)
    c.bar(30, 260, 260)


def numbar(c, dots):
    """Historical numeral: vertical bar with `dots` dots above."""
    c.stem(140, 160, 140, 0)
    for i in range(dots):
        c.dot(140, 260 + i * 90, 44)


def old_aa(c):
    c.cup(80, 220, 160, a_att=345, a_end=195)
    c.eye(230, 380, 52)


def frac16(c):
    c.dot(120, 300, 40)
    c.bar(40, 220, 200)


def frac40(c):
    c.dot(120, 320, 44)
    c.dot(120, 230, 44)
    c.bar(40, 220, 140)


def frac80(c):
    for i in range(3):
        c.dot(120, 340 - i * 90, 44)
    c.bar(40, 220, 120)


def numten(c):
    numbar(c, 1)


def numhundred(c):
    numbar(c, 2)


def numthousand(c):
    numbar(c, 3)


def quarter(c):
    c.loop(140, 240, 60)


def half(c):
    c.loop(140, 240, 60)
    c.dot(260, 240, 44)


def threequarters(c):
    c.loop(140, 240, 60)
    c.dot(260, 240, 44)
    c.dot(260, 120, 44)


ML_DIGITS = range(0xB)

def digit_design(c, d):
    """റố digits ൦..൯ - parametric numerals sharing the Latin digit skeletons."""

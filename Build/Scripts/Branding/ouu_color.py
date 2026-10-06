"""Colour utilities for the Open Unreal Utilities brand kit.

Each plugin is told apart by an accent colour. Accents are generated in OKLCH
from one of the three core colours, inheriting its lightness and chroma and
differing only in hue, so the family reads as one system and white band text
stays equally legible across it.
"""
import math


# --------------------------------------------------------------------------- #
# sRGB <-> OKLab/OKLCH
# --------------------------------------------------------------------------- #
def _srgb_to_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lin_to_srgb(c):
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0, min(255, int(round(v * 255))))


def rgb_to_oklch(rgb):
    r, g, b = (_srgb_to_lin(v) for v in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    A = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    B = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(A, B), math.degrees(math.atan2(B, A)) % 360


def oklch_to_rgb(L, C, H):
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(_lin_to_srgb(v) for v in (r, g, b))


def in_gamut(L, C, H):
    A, B = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
    m = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
    s = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return all(-0.001 <= v <= 1.001 for v in (r, g, b))


def fit_chroma(L, H, want):
    """Largest chroma <= `want` that stays inside sRGB at this L and hue."""
    lo, hi = 0.0, want
    for _ in range(30):
        mid = (lo + hi) / 2
        if in_gamut(L, mid, H):
            lo = mid
        else:
            hi = mid
    return lo


# --------------------------------------------------------------------------- #
# contrast
# --------------------------------------------------------------------------- #
def luminance(rgb):
    r, g, b = (_srgb_to_lin(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hexs(rgb):
    return '#%02X%02X%02X' % tuple(rgb)


# --------------------------------------------------------------------------- #
# the extended palette
# --------------------------------------------------------------------------- #
# Rule: the three core colours are a hand-made ramp, not a wheel, so the wheel
# is derived from one of them - its OKLab lightness and chroma are held while
# the hue rotates in 30 deg steps, chroma clipped only where sRGB cannot hold
# it. The anchor's own colour is entry 0 of its wheel, exactly reproduced.
#
# Which core colour anchors the wheel is a switch, because it sets how light
# the whole palette sits and therefore whether white band text stays legible:
#   1  the O   #3260CC   white 5.71:1   strongest contrast
#   2  the U   #2D94E3   white 3.25:1   the chosen default; large text only
#   3  the U   #2BBBD9   white 2.28:1   white text is not legible here
#
# Caveat at any anchor: the warm-yellow and green-cyan sectors are gamut
# limited and come out muted. Fine as accents, weak as primary band colours.
CORE = [(0x32, 0x60, 0xCC), (0x2D, 0x94, 0xE3), (0x2B, 0xBB, 0xD9)]
ANCHOR = 2

# How names are attached to the wheel:
#   'pinned'   "blue" IS the anchor colour, reproduced exactly; every other
#              name keeps its canonical hue at the anchor's lightness and
#              chroma. The house blue is therefore always one the mark already
#              contains, so no extra shade of blue enters the family.
#   'rotated'  the whole wheel starts at the anchor's hue and each name snaps
#              to its nearest slot. Evenly spaced, but off anchor 1 the slot
#              named "blue" lands beside the core colour rather than on it -
#              at anchor 2 that is #7883E7, a fourth blue. Kept as a fallback.
MODE = 'pinned'

# Canonical hue per name. A rotated wheel keeps these names by snapping each
# generated hue to the nearest canonical one - a bijection on a 30 deg grid -
# so symbolic assignments like "amber = the label" survive a change of anchor.
NAMED_HUES = [('blue', 264), ('indigo', 294), ('violet', 324), ('magenta', 354),
              ('red', 24), ('orange', 54), ('amber', 84), ('olive', 114),
              ('green', 144), ('teal', 174), ('cyan', 204), ('azure', 234)]


def set_anchor(n):
    """Base the palette on core colour 1, 2 or 3."""
    global ANCHOR
    if n not in (1, 2, 3):
        raise ValueError('anchor must be 1, 2 or 3, got %r' % (n,))
    ANCHOR = n


def _arc(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def set_mode(m):
    """Select how names map onto the wheel: 'pinned' or 'rotated'."""
    global MODE
    if m not in ('pinned', 'rotated'):
        raise ValueError("mode must be 'pinned' or 'rotated', got %r" % (m,))
    MODE = m


def palette(steps=12, anchor=None, mode=None):
    """[(name, hue, rgb)] - the brand wheel for the selected anchor."""
    core = CORE[(anchor or ANCHOR) - 1]
    L, C, H0 = rgb_to_oklch(core)

    if (mode or MODE) == 'pinned' and steps == 12:
        out = []
        for name, hue in NAMED_HUES:
            if name == 'blue':
                out.append((name, H0, tuple(core)))        # the anchor itself
            else:
                out.append((name, hue, oklch_to_rgb(L, fit_chroma(L, hue, C), hue)))
        return out

    out = []
    for i in range(steps):
        h = (H0 + 360.0 * i / steps) % 360   # unrounded: entry 0 is the anchor
        rgb = oklch_to_rgb(L, fit_chroma(L, h, C), h)
        name = (min(NAMED_HUES, key=lambda nh: _arc(nh[1], h))[0]
                if steps == 12 else 'h%03d' % h)
        out.append((name, h, rgb))
    return out


def by_name(name, anchor=None, mode=None):
    """Resolve a colour name against the selected anchor's wheel."""
    want = dict(NAMED_HUES).get(name)
    if want is None:
        raise KeyError(name)
    wheel = palette(anchor=anchor, mode=mode)
    if (mode or MODE) == 'pinned':
        return dict((n, rgb) for n, _, rgb in wheel)[name]
    return min(wheel, key=lambda e: _arc(e[1], want))[2]

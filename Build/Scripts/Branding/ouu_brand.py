"""Open Unreal Utilities brand-kit generator.

Draws the OUU monogram and the three lockups built on it, on the grid measured
from the original artwork so everything in the family stays dimensionally
identical.

The monogram is 3 glyph cells: pitch 128, cell 154x154, stroke 26 (ring
R_out 77 / R_in 51), 410x154 overall. Its three colours map onto the three
words of the parent name - #3260CC "Open", #2D94E3 "Unreal", #2BBBD9
"Utilities" - so the kicker beneath it spells out the mark.

Each plugin is told apart by an accent colour, not by its monogram: the accent
fills a band carrying the plugin name. Accents come from ouu_color.py.

The mark is fully procedural. Lettering lives in ouu_type.py and needs Poppins
SemiBold installed.
"""
import os

from PIL import Image, ImageDraw

# <repo>/Build/Scripts/Branding/ouu_brand.py  ->  <repo>
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    os.pardir, os.pardir, os.pardir))
PLUG = os.path.join(ROOT, 'Plugins')

C1, C2, C3 = (0x32, 0x60, 0xCC), (0x2D, 0x94, 0xE3), (0x2B, 0xBB, 0xD9)
WHITE = (255, 255, 255)

PITCH, CELL, STROKE = 128, 154, 26
MARK_W, MARK_H = 2 * PITCH + CELL, CELL          # 410 x 154
BANNER_ORIGIN = (307, 54)                        # mark position in the banner


def _ink_rows(img, thresh=128):
    """First and last+1 rows where `img` reaches `thresh` alpha.

    Alpha-bbox would include the faint antialiased fringe, which differs in
    depth between a thick curve and a letter terminal; thresholding makes the
    mark and the lettering comparable.
    """
    a = img.split()[3]
    rows = [y for y in range(img.height)
            if max(a.crop((0, y, img.width, y + 1)).getdata()) >= thresh]
    return (rows[0], rows[-1] + 1) if rows else (0, img.height)


def _glyph(d, kind, i, s):
    """Draw monogram glyph `kind` in cell `i` at supersampled scale `s`."""
    cx, cy = (i * PITCH + CELL / 2.0) * s, (CELL / 2.0) * s
    ro, ri, sw = CELL / 2.0 * s, (CELL / 2.0 - STROKE) * s, STROKE * s
    top, bot, left, right = 0.0, CELL * s, cx - ro, cx + ro

    if kind == 'O':
        d.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], fill=255)
        d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=0)
    elif kind == 'U':
        d.ellipse([cx - ro, cy - ro, cx + ro, cy + ro], fill=255)
        d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=0)
        d.rectangle([left, top, right, cy], fill=0)          # keep bottom bowl
        d.rectangle([left, top, left + sw, cy], fill=255)    # + two stems
        d.rectangle([right - sw, top, right, cy], fill=255)
    else:
        raise ValueError(kind)


def mark(glyphs=('O', 'U', 'U'), colors=(C1, C2, C3), width=MARK_W):
    """RGBA image of the monogram, `width` px wide, on a transparent ground."""
    scale = width / float(MARK_W)
    ss = max(2, int(round(8 / scale)))
    W, H = int(round(MARK_W * scale)), int(round(MARK_H * scale))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for i in (2, 1, 0):                                      # back to front
        big = Image.new('L', (int(MARK_W * scale * ss),
                        int(MARK_H * scale * ss)), 0)
        _glyph(ImageDraw.Draw(big), glyphs[i], i, scale * ss)
        out.paste(Image.new('RGBA', (W, H), colors[i] + (255,)),
                  (0, 0), big.resize((W, H), Image.LANCZOS))
    return out


# --------------------------------------------------------------------------- #
# square icon, "band" layout: uniform OUU mark over a full-bleed colour band
# carrying the plugin name in white
# --------------------------------------------------------------------------- #
BAND_H, BAND_MARK_W, BAND_TEXT_W = 150, 356, 436
# One size for every icon rather than a per-name fit: 0.63 is the largest that
# still fits the longest short form ("BP Validation", 684 px) in BAND_TEXT_W.
ICON_TEXT_SCALE = 0.63


def icon_band(name, band, size=512, mark_w=BAND_MARK_W, band_h=BAND_H):
    """Square plugin icon  ->  Icon512.png / Icon128.png"""
    import ouu_type as T
    c = Image.new('RGB', (512, 512), WHITE)
    ImageDraw.Draw(c).rectangle([0, 512 - band_h, 512, 512], fill=band)
    m = mark(('O', 'U', 'U'), width=mark_w)
    c.paste(m, ((512 - m.width) // 2, (512 - band_h - m.height) // 2), m)
    T.paste_line(c, name, 256, T.band_baseline(512 - band_h, band_h, ICON_TEXT_SCALE),
                 (255, 255, 255), scale=ICON_TEXT_SCALE, max_width=BAND_TEXT_W)
    return c if size == 512 else c.resize((size, size), Image.LANCZOS)


# --------------------------------------------------------------------------- #
# wordmark lockups under the "Open Unreal Utilities - <name>" naming
# --------------------------------------------------------------------------- #
PARENT = 'Open Unreal Utilities'
PARENT_WORDS = ['Open', 'Unreal', 'Utilities']
PARENT_COLORS = [C1, C2, C3]          # Open / Unreal / Utilities <-> O U U

# One type size per asset. In the banner the kicker and the band share
# KICKER_SCALE; in the lockup the stacked words and the band are both set at
# banner size and reduced by the same factor, so every line matches.
KICKER_SCALE = 0.78


def banner(name, accent, band_h=132):
    """1024x512 stacked lockup  ->  <plugin>512_wide.png

    Mark, then the parent name as a kicker whose three words take the three
    mark colours (so it maps onto the O-U-U monogram), then a full-bleed
    accent band carrying the plugin name in white.
    """
    import ouu_type as T
    c = Image.new('RGB', (1024, 512), WHITE)
    ImageDraw.Draw(c).rectangle([0, 512 - band_h, 1024, 512], fill=accent)
    m = mark(('O', 'U', 'U'))
    c.paste(m, BANNER_ORIGIN, m)
    T.paste_line(c, PARENT, 512, 324.0, PARENT_COLORS, scale=KICKER_SCALE,
                 max_width=886)
    T.paste_line(c, name, 512, T.band_baseline(512 - band_h, band_h, KICKER_SCALE),
                 (255, 255, 255), scale=KICKER_SCALE, max_width=1024 - 120)
    return c


def lockup(name, accent, mark_w=160, gap=10, band_h=36, pad=10,
           band_gap=7, scale=1.0):
    """Mark + stacked parent name over an accent band  ->  <plugin>_wide.png

    The parent name stacks one word per line as the original lockup did; the
    plugin name sits in a full-width band underneath, set at the same size.
    Both are set at banner size and reduced together, so every line matches.
    `scale` multiplies the finished size; 1.0 is the README-header lockup.
    """
    import ouu_type as T
    S = 5.0 / scale                              # text is always set at banner size
    mark_w, gap = int(round(mark_w * scale)), int(round(gap * scale))
    band_h, pad = int(round(band_h * scale)), int(round(pad * scale))
    band_gap = int(round(band_gap * scale))
    layers = [(T.line_layer(w, col, 1.0), bl) for w, col, bl in
              zip(PARENT_WORDS, PARENT_COLORS, (74.0, 186.0, 292.5))]
    tw = max(l.width for (l, _), _ in layers)
    # alpha_composite, not paste(..., mask=itself): the latter multiplies the
    # layer's alpha by itself, eroding the antialiased fringe a little more on
    # every paste, which left the lettering lighter than the mark.
    block = Image.new('RGBA', (tw, 310), (0, 0, 0, 0))
    for (l, base), bl in layers:
        block.alpha_composite(l, (0, int(round(bl - base))))
    sw, sh = round(tw / S), round(310 / S)
    block = block.resize((sw, sh), Image.LANCZOS)

    # band text: same size, same reduction, so it matches the stack exactly
    nl, nbase = T.line_layer(name, (255, 255, 255), 1.0)
    bb = nl.split()[3].getbbox()
    # crop width only: keep baseline
    nl = nl.crop((bb[0], 0, bb[2], nl.height))
    nl = nl.resize((max(1, round(nl.width / S)), max(1, round(nl.height / S))),
                   Image.LANCZOS)
    base_in_layer = nbase / S

    # Bottom-align the mark to the lettering's ink instead of centring both
    # boxes. The text block carries empty space below its last baseline, so
    # centring leaves the mark hanging lower than "Utilities" and its gap to
    # the band reads cramped; this gives the two the same gap.
    mk = mark(('O', 'U', 'U'), width=mark_w)
    text_top, text_bot = _ink_rows(block)
    mk_top, mk_bot = _ink_rows(mk)
    mark_y = text_bot - mk_bot                       # ink bottoms coincide
    top = min(mark_y + mk_top, text_top)
    plate_h = text_bot - top

    # The lockup is exactly as wide as its upper half. Letting a long plugin
    # name widen it instead would leave that half padded out with dead space,
    # and the family would stop being dimensionally identical - so an
    # over-long name is a build error rather than a silently wider image.
    W = mark_w + gap + sw
    if nl.width + 2 * pad > W:
        raise ValueError(
            'lockup: "%s" does not fit. The band needs %d px of lettering plus '
            '%d px padding either side (%d px total), but the mark and the '
            'stacked parent name only make the lockup %d px wide. Shorten the '
            'name by about %d px, or widen the lockup via mark_w.'
            % (name, nl.width, pad, nl.width + 2 * pad, W,
               nl.width + 2 * pad - W))
    out = Image.new('RGBA', (W, plate_h + band_gap + band_h), (0, 0, 0, 0))
    out.alpha_composite(mk, (0, mark_y - top))
    out.alpha_composite(block, (mark_w + gap, -top))

    band = Image.new('RGBA', (W, band_h), tuple(accent) + (255,))
    band.alpha_composite(nl, ((W - nl.width) // 2,
                              int(round(T.band_baseline(0, band_h, 1.0 / S)
                                        - base_in_layer))))
    out.alpha_composite(band, (0, plate_h + band_gap))
    return out


# --------------------------------------------------------------------------- #
# editor / game splash
# --------------------------------------------------------------------------- #
# Unreal draws its own startup text over the coloured bands, so their heights
# are fixed; only the white plate between them contains the artwork.
SPLASH_SIZE = (720, 360)
SPLASH_TOP = [(C1, 18), (C3, 7), (C2, 4)]          # 29 px
SPLASH_BOTTOM = [(C2, 4), (C3, 7), (C1, 65)]       # 76 px
SPLASH_NOTICE = 'Copyright (c) 2026 Jonas Reich & Contributors'
SPLASH_NOTICE_BASELINE = 318
SPLASH_NOTICE_RIGHT = 17                           # right margin, px
SPLASH_NOTICE_CAP = 11.0                           # cap height, px


def splash(name, accent, notice=SPLASH_NOTICE, art_scale=2.2, size=SPLASH_SIZE):
    """A UE splash screen, drawn from scratch  ->  Splash.png / EdSplash.png"""
    import ouu_type as T
    W, H = size
    c = Image.new('RGB', (W, H), WHITE)
    d = ImageDraw.Draw(c)

    y = 0
    for col, h in SPLASH_TOP:
        d.rectangle([0, y, W - 1, y + h - 1], fill=col)
        y += h
    plate_top = y

    y = H
    for col, h in reversed(SPLASH_BOTTOM):
        d.rectangle([0, y - h, W - 1, y - 1], fill=col)
        y -= h
    plate_bot = y                                   # first row of bottom border

    art = lockup(name, accent, scale=art_scale)
    c.paste(art, ((W - art.width) // 2,
                  plate_top + (plate_bot - plate_top - art.height) // 2), art)

    if notice:
        scale = SPLASH_NOTICE_CAP / T.CAP
        width = T.set_line(notice, scale)[0].width
        T.paste_line(c, notice, W - SPLASH_NOTICE_RIGHT - width / 2.0,
                     SPLASH_NOTICE_BASELINE, WHITE, scale=scale)
    return c

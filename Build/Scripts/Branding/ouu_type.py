"""Typesetting for the Open Unreal Utilities brand kit.

The artwork is set in Poppins SemiBold. At the 1024x512 banner scale that is
size 101 px with +0.9 px tracking, giving a cap height of 71 px; every other
size in the kit is a `scale` multiple of those.
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_FILE = 'Poppins-SemiBold.ttf'


def _font_roots():
    """Places a system font install could be, on any platform."""
    roots = []
    for var in ('WINDIR', 'SystemRoot'):
        if os.environ.get(var):
            roots.append(os.path.join(os.environ[var], 'Fonts'))
    if os.environ.get('LOCALAPPDATA'):                   # per-user install
        roots.append(os.path.join(os.environ['LOCALAPPDATA'],
                                  'Microsoft', 'Windows', 'Fonts'))
    roots += [os.path.join(os.sep, 'usr', 'share', 'fonts'),
              os.path.join(os.sep, 'usr', 'local', 'share', 'fonts'),
              os.path.join(os.sep, 'Library', 'Fonts'),
              os.path.join(os.sep, 'System', 'Library', 'Fonts')]
    for rel in ('.fonts', '.local/share/fonts', 'Library/Fonts'):
        roots.append(os.path.join(os.path.expanduser('~'), *rel.split('/')))
    return [r for r in roots if os.path.isdir(r)]


def font_path():
    """Locate the installed Poppins SemiBold, or explain how to get it."""
    for root in _font_roots():
        direct = os.path.join(root, FONT_FILE)
        if os.path.exists(direct):
            return direct
        for dirpath, _, names in os.walk(root):
            if FONT_FILE in names:
                return os.path.join(dirpath, FONT_FILE)
    raise FileNotFoundError(
        '%s is not installed on this system.\n'
        'The Open Unreal brand artwork is set in Poppins SemiBold. Install the\n'
        'Poppins family (SIL Open Font License) from\n'
        'https://fonts.google.com/specimen/Poppins and re-run.\n'
        'Searched: %s'
        % (FONT_FILE, ', '.join(_font_roots()) or '(no font directories found)'))


SIZE, TRACKING = 101.0, 0.9      # at banner scale; see module docstring
CAP = 71.0                       # cap height at SIZE
SS = 4                           # supersampling


def set_line(text, scale=1.0):
    """Set `text`; returns (mask, baseline_row, [(x0, x1) per word]).

    The mask is cropped to the ink horizontally, so mask.width is the ink
    width; `baseline_row` is where the baseline sits inside it. Word spans are
    ink x-ranges within the mask, for colouring words independently.
    """
    size = SIZE * scale
    f = ImageFont.truetype(font_path(), int(round(size * SS)))
    pad = int(size * SS)
    H = int(size * SS * 2.4)
    base = int(size * SS * 1.6)
    im = Image.new('L', (int(size * SS * 0.75 * len(text)) + 4 * pad, H), 0)
    d = ImageDraw.Draw(im)

    x = float(pad)
    words, start = [], None
    for ch in text:
        if ch == ' ':
            if start is not None:
                words.append((start, x - TRACKING * SS * scale))
                start = None
        else:
            if start is None:
                start = x
            d.text((x, base), ch, font=f, fill=255, anchor='ls')
        x += f.getlength(ch) + TRACKING * SS * scale
    if start is not None:
        words.append((start, x - TRACKING * SS * scale))

    im = im.resize((im.width // SS, im.height // SS), Image.LANCZOS)
    b = im.getbbox()
    im = im.crop((b[0], 0, b[2], im.height))
    return im, base / float(SS), [((a / SS) - b[0], (c / SS) - b[0]) for a, c in words]


def line_layer(text, colors, scale=1.0, max_width=None):
    """RGBA layer of `text` on a transparent ground, plus its baseline row.

    `colors` is one colour, or one per word. If the line would exceed
    `max_width` it is set smaller instead of being squashed.
    """
    mask, base_row, words = set_line(text, scale)
    if max_width and mask.width > max_width:
        mask, base_row, words = set_line(text, scale * max_width / float(mask.width))
    if not isinstance(colors, (list, tuple)) or isinstance(colors[0], int):
        colors = [colors] * len(words)

    layer = Image.new('RGBA', mask.size, (0, 0, 0, 0))
    for (wx0, wx1), col in zip(words, colors):
        a, b = max(0, int(round(wx0)) - 2), min(mask.width, int(round(wx1)) + 2)
        strip = Image.new('L', mask.size, 0)
        strip.paste(mask.crop((a, 0, b, mask.height)), (a, 0))
        layer.paste(Image.new('RGBA', mask.size, tuple(col) + (255,)), (0, 0), strip)
    return layer, base_row


def band_baseline(band_top, band_h, scale):
    """Baseline that centres the cap-height block in a band.

    Centring the raw ink instead would push names with descenders ("Tags")
    higher than names without ("Standard"), so the family would not share a
    baseline. Cap-height centring is identical for every name.
    """
    return band_top + (band_h + CAP * scale) / 2.0


def paste_line(canvas, text, center_x, baseline, colors, scale=1.0, max_width=None):
    """Paste `text` centred on `center_x` with its baseline at `baseline`."""
    layer, base_row = line_layer(text, colors, scale, max_width)
    canvas.paste(layer,
                 (int(round(center_x - layer.width / 2.0)),
                  int(round(baseline - base_row))),
                 layer)
    return layer.width

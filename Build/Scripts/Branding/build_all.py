"""Generate the logo set for every Open Unreal plugin.

Run:  python build_all.py [--install] [--anchor 1|2|3] [--palette pinned|rotated]

Without --install the files are written to ./out/<plugin>/ for review.
With --install they are copied into each plugin's Resources/ folder.
Nothing is ever deleted; remove superseded files yourself.

--anchor picks which of the three core colours the accent wheel is built on
(1 = the O, 2 and 3 = the two Us; 2 is the default). It sets how light every
accent sits, and so whether white band text stays legible - see ouu_color.py.

--palette picks how names map onto that wheel. 'pinned' (default) makes the
house blue the anchor colour itself, so the family never gains a fourth shade
of blue; 'rotated' is the earlier evenly-spaced wheel, kept as a fallback.
"""
import os
import pathlib
import sys

import ouu_brand as B
import ouu_color as K

# Accent hues are assigned by association, not by spreading them evenly:
#   red     the red pen - style violations, lint errors
#   orange  tools, machinery, build pipelines
#   amber   the label / luggage tag
#   green   pass / validated
#   cyan    data, storage, serialisation
#   violet  the showcase
# blue is reserved for the core plugin and is not reassigned.
#
# resources dir,                                          subtitle (D/E),         short (A/B),      colour
# fmt: off
TARGETS = [
    (os.path.join(B.PLUG, 'OpenUnrealUtilities'),         'Misc. Utilities',      'Misc. Utils',    'blue'),
    (os.path.join(B.PLUG, 'OUUTags'),                     'Gameplay Tags',        'Tags',           'orange'),
    (os.path.join(B.PLUG, 'OUUCodingStandard'),           'C++ Coding Standard',  'C++ Standard',   'red'),
    (os.path.join(B.PLUG, 'OUUJsonDataAssets'),           'Json Data Assets',     'Json Data',      'cyan'),
    (os.path.join(B.PLUG, 'OUUBlueprintValidation'),      'Blueprint Validation', 'BP Validation',  'green'),
    # not plugins: the tooling repo and the sample project that hosts everything
    (os.path.join(B.ROOT, 'OpenUnrealAutomationTools'),    'Automation Tools',     'Automation',     'amber'),
    (B.ROOT,                                               'Sample Project',       'Sample Proj.',   'blue'),
]
# fmt: on


def build(subtitle, short, colour):
    accent = K.by_name(colour)
    return {
        'Icon512.png':      B.icon_band(short, accent, 512).convert('RGBA'),
        'Icon128.png':      B.icon_band(short, accent, 128).convert('RGBA'),
        'ouu_wide.png':     B.lockup(subtitle, accent),
        'ouu512_wide.png':  B.banner(subtitle, accent).convert('RGBA'),
    }


def palette_review(banners, anchor=1, mode='pinned', scale=0.5, cols=2,
                   gutter=16, pad=24, bg=(243, 243, 246), swatch_h=96,
                   head_h=54):
    """Tile every banner into one sheet, for judging the accents side by side.

    `banners` is [(label, colour name, RGBA banner)]. A strip of the assigned
    accents with their hex and white-text contrast runs along the bottom.
    """
    from PIL import Image, ImageDraw
    import ouu_type as T

    w, h = int(1024 * scale), int(512 * scale)
    rows = -(-len(banners) // cols)
    W = pad * 2 + cols * w + (cols - 1) * gutter
    H = pad * 2 + head_h + rows * h + (rows - 1) * gutter + swatch_h + gutter
    sheet = Image.new('RGB', (W, H), bg)

    anchor_rgb = K.CORE[anchor - 1]
    ImageDraw.Draw(sheet).rectangle(
        [pad, pad, pad + 34, pad + 34], fill=anchor_rgb)
    T.paste_line(sheet, 'anchor %d  %s  %s  white %.2f to 1' % (
        anchor, K.hexs(anchor_rgb), mode,
        K.contrast(anchor_rgb, (255, 255, 255))),
        pad + 46 + 330, pad + 26, (60, 60, 75), scale=0.3)

    for i, (_, _, banner) in enumerate(banners):
        x = pad + (i % cols) * (w + gutter)
        y = pad + head_h + (i // cols) * (h + gutter)
        sheet.paste(banner.convert('RGB').resize(
            (w, h), Image.LANCZOS), (x, y))

    sw = (W - pad * 2 - (len(banners) - 1) * gutter) // len(banners)
    top = H - pad - swatch_h
    for i, (label, name, _) in enumerate(banners):
        accent = K.by_name(name)
        x = pad + i * (sw + gutter)
        ImageDraw.Draw(sheet).rectangle([x, top, x + sw - 1, top + swatch_h - 1],
                                        fill=accent)
        for j, line in enumerate((label, K.hexs(accent),
                                  '%.2f:1' % K.contrast(accent, (255, 255, 255)))):
            T.paste_line(sheet, line, x + sw / 2.0, top + 26 + j * 26,
                         (255, 255, 255), scale=0.24, max_width=sw - 16)
    return sheet


def color_chart(anchor=2, mode='pinned', cols=6, sw=172, sh=118, gutter=10,
                pad=24, bg=(243, 243, 246), head_h=54):
    """The full accent wheel as a reference chart, for picking future hues."""
    from PIL import Image, ImageDraw
    import ouu_type as T

    wheel = K.palette(anchor=anchor, mode=mode)
    rows = -(-len(wheel) // cols)
    W = pad * 2 + cols * sw + (cols - 1) * gutter
    H = pad * 2 + head_h + rows * sh + (rows - 1) * gutter + gutter + 84
    chart = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(chart)

    core = K.CORE[anchor - 1]
    d.rectangle([pad, pad, pad + 34, pad + 34], fill=core)
    T.paste_line(chart, 'accent wheel  -  anchor %d  %s  %s' % (
        anchor, K.hexs(core), mode), pad + 46 + 330, pad + 26,
        (60, 60, 75), scale=0.3)

    for i, (name, hue, rgb) in enumerate(wheel):
        x = pad + (i % cols) * (sw + gutter)
        y = pad + head_h + (i // cols) * (sh + gutter)
        d.rectangle([x, y, x + sw - 1, y + sh - 1], fill=rgb)
        label = name + (' = anchor' if tuple(rgb) == tuple(core) else '')
        for j, line in enumerate((label, K.hexs(rgb),
                                  '%.2f:1' % K.contrast(rgb, (255, 255, 255)))):
            T.paste_line(chart, line, x + sw / 2.0, y + 32 + j * 30,
                         (255, 255, 255), scale=0.26, max_width=sw - 16)

    y = H - pad - 60
    T.paste_line(chart, 'core ramp', pad + 70,
                 y - 10, (60, 60, 75), scale=0.26)
    for i, c in enumerate(K.CORE):
        x = pad + 160 + i * 190
        d.rectangle([x, y - 30, x + 180, y + 30], fill=c)
        T.paste_line(chart, '%s%s' % (K.hexs(c), '  *' if i == anchor - 1 else ''),
                     x + 90, y + 6, (255, 255, 255), scale=0.26, max_width=170)
    return chart


def main(install=False, anchor=2, mode='pinned'):
    K.set_anchor(anchor)
    K.set_mode(mode)
    banners = []
    for root, subtitle, short, colour in TARGETS:
        files = build(subtitle, short, colour)
        label = os.path.basename(root.rstrip('/')) or 'SampleProject'
        dst = os.path.join(root, 'Resources') if install \
            else os.path.join(pathlib.Path(__file__).parent, 'out', label)

        print(f"Writing brand images to {dst}")
        if not install:
            os.makedirs(dst, exist_ok=True)
        for name, im in files.items():
            im.save(os.path.join(dst, name), optimize=True)
        print('%-26s %-20s %-8s %s' % (
            label, subtitle, colour, K.hexs(K.by_name(colour))))
        banners.append((subtitle, colour, files['ouu512_wide.png']))

    # The sample project additionally needs the editor and game splash screens.
    # Unreal reads these straight off disk, so they are plain PNGs rather than
    # imported assets.
    _, subtitle, _, colour = TARGETS[-1]
    dst = os.path.join(B.ROOT, 'Content', 'Splash') if install \
        else os.path.join(pathlib.Path(__file__).parent, 'out', 'Splash')
    print(f"Writing splash screens to {dst}")
    os.makedirs(dst, exist_ok=True)
    sp = B.splash(subtitle, K.by_name(colour))
    for name in ('Splash.png', 'EdSplash.png'):
        sp.save(os.path.join(dst, name), optimize=True)
    print('%-26s %-20s %-8s %s' % (
        'Splash + EdSplash', subtitle, colour, K.hexs(K.by_name(colour))))

    # Review sheet: never a shipped asset, so it always lands in ./out
    out = os.path.join(pathlib.Path(__file__).parent, 'out')
    os.makedirs(out, exist_ok=True)
    review = os.path.join(
        out, 'palette_review_anchor%d_%s.png' % (anchor, mode))
    palette_review(banners, anchor=anchor, mode=mode).save(
        review, optimize=True)
    print(f"Writing palette review to {review}")

    chart = os.path.join(out, 'color_chart.png')
    color_chart(anchor, mode).save(chart, optimize=True)
    print(f"Writing colour chart to {chart}")


if __name__ == '__main__':
    argv = sys.argv[1:]
    anchor = 2
    if '--anchor' in argv:
        anchor = int(argv[argv.index('--anchor') + 1])
    mode = 'pinned'
    if '--palette' in argv:
        mode = argv[argv.index('--palette') + 1]
    for arg in argv:
        if arg.startswith('--anchor='):
            anchor = int(arg.split('=', 1)[1])
        if arg.startswith('--palette='):
            mode = arg.split('=', 1)[1]
    main('--install' in argv, anchor, mode)

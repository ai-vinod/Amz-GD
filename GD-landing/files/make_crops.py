"""
Pulls the usable photography out of the long GoDivinely infographic.

Two outputs, for two different jobs:

  ads/      fitted to Meta feed sizes, safe zones respected, ready to upload
  sources/  clean photographs at native aspect, to drop into Images/web/ and
            compose with adgen

Coordinates are source pixels of Artboard_1.png (1333 x 8000).
"""

from PIL import Image, ImageFilter, ImageDraw
import os

SRC = '/mnt/user-data/uploads/Artboard_1.png'
ROOT = '/home/claude/crops'
ADS = os.path.join(ROOT, 'ads')
SOURCES = os.path.join(ROOT, 'sources')
PROOFS = os.path.join(ROOT, 'proofs')
CREAM = (255, 241, 220)

# Regions that survive as standalone ads. Only the hero has enough vertical
# photograph to fill a feed frame without a huge stretched fill.
AD_REGIONS = {
    'hero': ((0, 0, 1333, 1245), (19, 620, 1290, 1200)),
    'artisan': ((505, 5240, 1333, 5920), (560, 5300, 1300, 5880)),
}

# Clean photographs, cropped to exclude every piece of baked-in text and every
# overlay. Native aspect, no fitting — adgen does the composition.
SOURCE_REGIONS = {
    'hero-strip': (0, 585, 1333, 1245),
    'hero-full': (0, 0, 1333, 1245),
    'artisan': (505, 5240, 1333, 5920),
    'vastu-shelf': (0, 3520, 490, 3960),
}

SIZES = {
    '4x5': (1080, 1350, {'top': 250, 'bottom': 250, 'side': 100}),
    '1x1': (1080, 1080, {'top': 100, 'bottom': 100, 'side': 100}),
}

MAX_EXTEND = 0.32   # past this a stretched edge reads as a smear


def extend_vertical(img, target_h, top_share=0.35):
    """Grow to target_h by stretching the top and bottom edge rows.

    Only sane where those edges are smooth — out-of-focus background above, a
    marble surface below. The blur hides the banding a plain resize leaves.
    """
    w, h = img.size
    if h >= target_h:
        return img
    extra = target_h - h
    top = int(extra * top_share)
    bot = extra - top
    canvas = Image.new('RGB', (w, target_h), CREAM)
    if top > 0:
        s = img.crop((0, 0, w, 12)).resize((w, top), Image.BILINEAR)
        canvas.paste(s.filter(ImageFilter.GaussianBlur(7)), (0, 0))
    canvas.paste(img, (0, top))
    if bot > 0:
        s = img.crop((0, h - 12, w, h)).resize((w, bot), Image.BILINEAR)
        canvas.paste(s.filter(ImageFilter.GaussianBlur(7)), (0, top + h))
    return canvas


def build_ad(src, region, subject, tw, th):
    l, t, r, b = region
    crop = src.crop(region)
    rw, rh = crop.size

    scale = tw / rw
    nh = round(rh * scale)
    crop = crop.resize((tw, nh), Image.LANCZOS)

    sub_top = (subject[1] - t) * scale
    sub_bot = (subject[3] - t) * scale

    if nh >= th:
        centre = (sub_top + sub_bot) / 2
        y = int(max(0, min(centre - th / 2, nh - th)))
        out = crop.crop((0, y, tw, y + th))
        fill = 0.0
        sub_top -= y
        sub_bot -= y
    else:
        need = th - nh
        fill = need / th
        top_share = 0.35
        out = extend_vertical(crop, th, top_share)
        sub_top += int(need * top_share)
        sub_bot += int(need * top_share)

    return out, scale, fill, (sub_top, sub_bot)


def proof(img, safe, sub):
    p = img.copy()
    d = ImageDraw.Draw(p, 'RGBA')
    w, h = p.size
    red = (220, 20, 60, 70)
    d.rectangle([0, 0, w, safe['top']], fill=red)
    d.rectangle([0, h - safe['bottom'], w, h], fill=red)
    d.rectangle([0, 0, safe['side'], h], fill=red)
    d.rectangle([w - safe['side'], 0, w, h], fill=red)
    d.rectangle([safe['side'], safe['top'], w - safe['side'], h - safe['bottom']],
                outline=(0, 120, 220, 255), width=4)
    d.rectangle([12, max(0, sub[0]), w - 12, min(h, sub[1])],
                outline=(0, 170, 90, 255), width=4)
    return p


def main():
    for d in (ADS, SOURCES, PROOFS):
        os.makedirs(d, exist_ok=True)
    src = Image.open(SRC).convert('RGB')

    print('ADS')
    print(f'  {"file":32} {"scale":>7} {"fill":>6}  subject')
    for name, (region, subject) in AD_REGIONS.items():
        for sname, (tw, th, safe) in SIZES.items():
            img, scale, fill, sub = build_ad(src, region, subject, tw, th)
            fn = f'{name}--{sname}.png'
            img.save(os.path.join(ADS, fn))
            proof(img, safe, sub).save(os.path.join(PROOFS, fn))
            ok = sub[0] >= safe['top'] - 4 and sub[1] <= th - safe['bottom'] + 4
            print(f'  {fn:32} {scale:6.2f}x {fill*100:5.0f}%  '
                  f'{"inside safe zone" if ok else "bleeds (fine for full-bleed photo)"}')

    print('\nSOURCES  (drop these in Images/web/)')
    print(f'  {"file":32} {"size":>12}  {"upscale to 1080":>16}')
    for name, region in SOURCE_REGIONS.items():
        crop = src.crop(region)
        fn = f'{name}.jpg'
        crop.save(os.path.join(SOURCES, fn), quality=94, subsampling=0)
        w, h = crop.size
        print(f'  {fn:32} {w:5} x {h:<4}  {1080/w:15.2f}x'
              f'{"   SOFT" if 1080/w > 1.6 else ""}')


if __name__ == '__main__':
    main()

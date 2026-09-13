# adgen — Meta ad creative generator

Turns one HTML frame plus a list of headlines into finished PNG ad creatives,
safe-zone compliant, in every placement size, in one command.

## Where to put this folder

Next to your `Images` folder, inside the landing page project:

```
godivinely/
├── index.html
├── Images/web/...
└── adgen/          ← this folder
```

The image paths in `copy.json` are written as `../Images/web/hero.jpg`,
which assumes this layout.

## One-time setup

```
npm install
npx playwright install chromium
```

The second command downloads a headless Chromium, about 150 MB. Once, ever.

## Every run after that

```
node generate.js            renders to out/
node generate.js --guides   also writes annotated proofs to out/_guides/
```

Run `--guides` the first time and whenever you change a `safe` value. The
proofs show the unsafe bands in red over the actual creative, so you can see
what Meta's interface will cover. They are for checking only. Never upload one.

## Safe zones

Meta unified its Stories and Reels safe zone specs in March 2026. These are
the figures baked into `copy.json`.

| Size | Canvas | Top | Bottom | Sides |
|---|---|---|---|---|
| 4:5 Feed | 1080×1350 | 250 | 250 | 100 |
| 1:1 carousel | 1080×1080 | 100 | 100 | 100 |
| 9:16 Reels | 1080×1920 | 270 (14%) | 670 (35%) | 90 |

**Why 9:16 bottom is so large.** Reels stacks the like, comment and share
buttons, the audio label and the creator caption over the lower third. Stories
only needs 20% (380px) for its CTA button. That 290px gap is the single most
common creative failure: design to the Stories margin, run on Reels, and your
price and code vanish. The template designs to the Reels margin, so one asset
is safe on both.

**Why sides are 90 and not 65.** Meta's published side margin is 6% (65px),
but on ultra-tall 20:9 phones it applies either Smart Zoom, which crops the
left and right edges, or letterboxing, and you don't get to choose which.
90px absorbs the zoom.

**Why 4:5 has margins at all**, given nothing overlays a Feed image: with
Advantage+ placements on, Meta reformats your creative across placements and
crops top and bottom equally. The 250px margin is what survives that.

**The centre square.** On the 9:16 proofs you'll see a blue 1080×1080 outline.
Anything inside it survives Meta re-cropping the vertical asset down to 4:5 or
1:1 for Feed. If you ever cut down to a single master asset, that's the box to
design inside.

**Carousel cards must be 1:1.** Meta crops carousel cards to square and cuts
off the top and bottom of a 4:5. That's why the square size exists here.

## What the script checks

Two safe-zone mechanisms, deliberately. The band padding comes from the `safe`
values, so text cannot be positioned into an unsafe area. Then after each frame
renders, the script measures where the logo, headline, subline and footer
actually landed and compares that against the safe rectangle — which catches
the case padding can't, a headline long enough to push the footer past the
bottom edge. Those print as `UNSAFE`.

It also checks two things that are legal but weak, and prints them as `weak`:

- **Headline over two lines.** A third line is more than a scroll-past reads.
  Shorten it or set `"headlineSize"` on that variant.
- **Product under 16% of the frame.** Some source shots have a lot of empty
  margin around the product, and after `contain` fits them to the middle strip
  the product ends up a stamp. Crop the source, or set `"photo": true`.
  Photo-mode variants are exempt, since the image fills the canvas by
  definition.

Every run prints the product share and headline line count per frame, so you
can see these drifting before they trip the threshold.

## Two layout modes

**Panel mode** is the default. The product sits on the cream ground and gets
the whole middle of the frame. The type sits above and below it.

Panel mode applies `mix-blend-mode: multiply` to the product image. This is
the thing that makes your white-background shots usable: white multiplied
against the cream ground *becomes* the cream ground, so the pasted-rectangle
edge disappears with no cutout work. The product darkens very slightly, which
on silver is invisible. Set `"blend": false` on a variant to turn it off if a
particular shot looks muddy.

**Photo mode** is for shots that are genuinely photographic rather than a
product on a plain ground — the mandir shelf with the diyas, the wrapped-gift
scene. Set `"photo": true` on the variant. The image fills the whole canvas
and the type sits on solid cream bands with a hard gold edge.

There is no gradient anywhere. An earlier version faded the product out behind
the text and it looked like a rendering fault. If a shot needs the type to sit
over it, it goes in photo mode and gets a band with a real edge.

**Why 9:16 has plain cream at the bottom.** That band is the 670px Reels
covers with the caption, buttons and audio label. It looks empty in the raw
PNG and is completely hidden in the actual placement. Don't try to fill it.

## Logo placement

The logo is off on 4:5 and 1:1, on for 9:16. In Feed your Page name and avatar
already sit directly above the creative, so a logo inside the image repeats
that and costs the product about 150px of height. Reels shows the account name
small and low-contrast over the video, so there it earns its place.

## Adding a variant

Copy a block inside `variants` in `copy.json`:

```json
{
  "id": "06-your-idea",
  "headline": "Your headline here.",
  "subline": "Optional second line.",
  "image": "../Images/web/hero.jpg"
}
```

`id` becomes the filename. Leave `subline` as `""` to hide it. Add
`"showCode": false` to drop the discount tag — worth testing, since a visible
code sometimes pulls the click before the product has done its job. Add
`"headlineSize": 54` to override the size for one variant.

## Before you spend money

Upload one creative, open the Ads Manager placement preview, and look at Reels
and Stories specifically. The pixel figures above are current as of the March
2026 spec update, but Meta moves its interface without announcing it, and the
preview is the only source that reflects what's live today. If something is
covered, adjust the `safe` value in `copy.json` and re-run — that's a
thirty-second fix rather than a redesign.

Then open `out/` in Explorer on Extra Large Icons. That thumbnail size is
roughly a creative in a feed at arm's length. Any headline you can't read
there won't get read.

## When something fails

A `FAIL` is almost always a wrong image path. The script names the file and
the reason and carries on with the rest.

If the headline renders in a plain serif instead of Fraunces, the machine was
offline when the font tried to load. Reconnect and re-run, or download the
Fraunces `.ttf` into this folder and swap the Google Fonts `<link>` in
`template.html` for an `@font-face` rule. That also makes renders faster and
repeatable offline.

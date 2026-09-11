# Landing page brief — silver-plated Ganesh shankh

## What this page is

A single-page bridge between a Meta ad and an Amazon.in product listing.
It has no form, no backend, no lead capture. Its only jobs are:

1. Warm the visitor up so they arrive on Amazon already sold.
2. Show the discount code clearly.
3. Send the click to Amazon.
4. Fire tracking events, because the Amazon listing itself cannot be tracked.

## Build constraints

- Single static `index.html`. No React, no build step, no framework.
- Inline CSS in a `<style>` block. Inline JS in a `<script>` block.
- Mobile-first. Assume 90%+ of traffic is a phone in portrait.
- Must load in under 2 seconds on 4G. Compress every image; no web fonts over 2 files.
- Meta Pixel ID lives in ONE constant at the top of the script. Never hardcoded elsewhere.
- Amazon product URL lives in ONE constant. Never hardcoded elsewhere.
- No Amazon logos, no "official partner" language. "Available on Amazon.in" is fine.

## Product facts

- Silver-plated Ganesh shankh, decorative / gifting item
- Listed on Amazon.in at approx Rs 1,899 (after the planned Rs 200 increase)
- Discount code gives Rs 300 off, applied at Amazon checkout
- Positioned as a **year-round gift**, not a Ganesh Chaturthi seasonal item:
  housewarming, weddings, new business openings, corporate gifting, Diwali

## Brand

GoDivinely. Logo exists: a crimson sun/chakra roundel with "Go Divinely"
set beside it. Place it small in the header and once in the footer. Nothing else.

Product size: 13.5 cm / 5.5 inch. Fits in the palm — state this early,
because at Rs 1,899 people assume it is larger and a size surprise causes returns.

## Assets

Filenames as supplied.

**Clean product shots, no baked-in text — use these freely**

- `Exact_Product_2.jpeg` — three-quarter view on warm beige. Hero candidate.
- `Exact_Product_1.jpeg` — upright front view on white. Good for the detail block.
- `Exact_Product_3.jpeg` — low angle on white.
- `1.png` — product seated in the open red velvet box. **This is the hero.**
  It says "gift" in one glance, which is the entire campaign strategy.

**A+ modules with text burned into the image**

Everything else. Use the photography, never the baked-in text — at 380px wide
that text renders unreadable and it repeats what the page already says in HTML.
Crop to the photograph and set the words as real text.

- `2.png` — shankh on a mandir shelf with diyas and marigolds. Setting shot.
- `5.png` — beside a wrapped gift, party bokeh behind. Occasions section.
- `6.png` — certificate and quality card. Trust section.
- `7.png` — shiny finish vs antique dual-tone, side by side. The real
  differentiator; rebuild this comparison as two cropped images plus HTML labels.
- `9.png` — held in a palm, size called out. Crop to the hand shot for scale.
- `3.png` — everything included in the box.

**Do not use**

- `16.png`, `17.png` — the wedding couple and the artisan's hands are
  AI-generated and read as such at full width on a phone. Fine on Amazon,
  a trust liability in a Meta funnel where the visitor is already sceptical.

## Design direction

The brand already has a visual language in the A+ content: warm cream ground,
deep maroon type, gold accents, silver-and-gold product. Match it. The visitor
goes from this page to the Amazon listing in seconds — a palette change between
the two would read as a different seller at the exact moment they decide to pay.

**Colour**

- Cream `#FBEAD4` — page ground, taken from the A+ modules
- Maroon `#7B1420` — headings and the primary CTA
- Crimson `#E31E52` — the logo only, nowhere else
- Gold `#C79A3E` — hairline rules and the code chip edge
- Near-black `#1A1A1A` — body text

Silver photographs badly on white but reads well on this cream, which is why
the client's own shots already sit on it. No dark sections.

**Type**

- Display: a high-contrast serif in maroon, matching the A+ headline style —
  Playfair Display, weights 600 and 700
- Body: system sans stack, no download —
  `-apple-system, "Segoe UI", Roboto, sans-serif`
- One font file total, to protect the 2-second load budget

**Layout**

- Single column throughout. Content max-width 480px, centred on wider screens.
  Do not build a separate desktop layout.
- Hero: `1.png` full-bleed, headline below it
- All text left-aligned. The code chip is the only centred element.

**Principles**

- The product is the only ornate thing on the page. Every surface around it
  stays plain — no decorative borders, no gold flourishes, no mandala motifs.
  The carving is already doing that work.
- The code chip is the one designed object — treat it as a gift tag with a
  physical edge, not a dashed-border coupon rectangle.
- No section entrance animations, no hover transitions on cards.
  One motion moment only: the "Copied" confirmation on the code chip.

## Page sections, in order

### 1. Hero
- One strong product photograph, filling most of the first screen
- Headline naming the gift occasion, not the festival
- Price shown with the code visible immediately below it — do not make anyone scroll to find the code
- Primary CTA button: "Buy on Amazon"
- The code is a tap-to-copy element with a visible "Copied" confirmation

### 2. Trust strip
Thin band directly under the hero. Delivery, returns, and the fact that
payment happens on Amazon. Three short items, no icons-in-circles treatment.

### 3. What makes it worth gifting
Three or four points. Material and finish, the packaging, the size,
who it suits. Written as plain sentences, not feature bullets with bold labels.

### 4. Photo detail
Two or three close-up images. Finish, base, scale against a hand or shelf.

### 5. Occasions
The year-round argument, made concretely. Name the occasions.
This section exists to move the product out of the festival window.

### 6. How the code works
Three steps, genuinely sequential so numbering is justified:
copy the code, tap through to Amazon, apply it at checkout.

### 7. Closing CTA
Code repeated, button repeated. Nothing new.

### 8. Sticky mobile bar
Fixed to the bottom of the viewport on screens under 768px.
Shows the price and the button. Appears after the visitor scrolls past the hero.

## Events to fire

| Event | Trigger | Notes |
|---|---|---|
| `PageView` | automatic | Base pixel |
| `ViewContent` | 3s after load | Filters out bounces and misclicks |
| `Scroll50` | 50% scroll depth | Custom event |
| `Scroll90` | 90% scroll depth | Custom event |
| `CopyCode` | tap on the code | Custom event, strong intent signal |
| `InitiateCheckout` | tap on any Amazon button | **The money event.** Standard event so Meta can optimise on it |

Every event fires once per session only. Scroll events must not re-fire on scroll-up.
`InitiateCheckout` carries a `button_position` parameter (`hero`, `steps`, `closing`, `sticky`)
so it becomes visible which placement actually earns the click.

## Tracking script

Paste this inside `<head>`, replacing the two constants.

```html
<script>
  const PIXEL_ID = 'YOUR_PIXEL_ID_HERE';
  const AMAZON_URL = 'https://www.amazon.in/dp/YOUR_ASIN_HERE';

  // --- Meta base pixel ---
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', PIXEL_ID);
  fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
  src="https://www.facebook.com/tr?id=YOUR_PIXEL_ID_HERE&ev=PageView&noscript=1"/></noscript>
```

Paste this before `</body>`.

```html
<script>
(function () {
  const fired = new Set();

  function once(key, fn) {
    if (fired.has(key)) return;
    fired.add(key);
    fn();
  }

  // Engaged view — 3 seconds on page
  setTimeout(function () {
    once('view', function () {
      fbq('track', 'ViewContent', {
        content_name: 'Silver Ganesh Shankh',
        content_type: 'product'
      });
    });
  }, 3000);

  // Scroll depth
  window.addEventListener('scroll', function () {
    const doc = document.documentElement;
    const depth = (window.scrollY + window.innerHeight) / doc.scrollHeight * 100;

    if (depth >= 50) once('s50', function () { fbq('trackCustom', 'Scroll50'); });
    if (depth >= 90) once('s90', function () { fbq('trackCustom', 'Scroll90'); });
  }, { passive: true });

  // Tap to copy the discount code
  const codeEl = document.querySelector('[data-code]');
  if (codeEl) {
    codeEl.addEventListener('click', function () {
      const code = codeEl.dataset.code;
      navigator.clipboard.writeText(code).then(function () {
        codeEl.classList.add('is-copied');
        setTimeout(function () { codeEl.classList.remove('is-copied'); }, 2000);
      });
      once('copy', function () {
        fbq('trackCustom', 'CopyCode', { code: code });
      });
    });
  }

  // Outbound click to Amazon — the money event
  document.querySelectorAll('[data-cta]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const position = btn.dataset.cta;

      fbq('track', 'InitiateCheckout', {
        content_name: 'Silver Ganesh Shankh',
        button_position: position,
        value: 1599,
        currency: 'INR'
      });

      // Small delay so the event reaches Meta before the page unloads
      setTimeout(function () { window.location.href = AMAZON_URL; }, 300);
    });
  });
})();
</script>
```

Markup the buttons and code element like this:

```html
<span data-code="GANESH300">GANESH300</span>
<a href="#" data-cta="hero">Buy on Amazon</a>
<a href="#" data-cta="sticky">Buy on Amazon</a>
```

## Before going live

- Install the Meta Pixel Helper Chrome extension and confirm every event fires once
- Check Events Manager → Test Events with a real phone on mobile data
- Confirm the Amazon link opens the correct listing and the code applies at checkout
- Run the page through PageSpeed Insights on mobile

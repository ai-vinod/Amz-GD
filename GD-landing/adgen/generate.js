// Renders every variant in copy.json at every size, checks each frame against
// Meta's safe zones, and flags frames that are technically legal but weak.
//
//   node generate.js            normal run
//   node generate.js --guides   also writes annotated proofs to out/_guides/

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, 'copy.json');
const TEMPLATE_FILE = path.join(__dirname, 'template.html');
const OUT_DIR = path.join(__dirname, 'out');
const GUIDE_DIR = path.join(OUT_DIR, '_guides');

// Slack for font metrics and rounding.
const TOLERANCE = 3;
// Below this share of the canvas the product reads as a stamp at feed size.
const MIN_PRODUCT_SHARE = 0.16;
// A third line is more than a scroll-past will read.
const MAX_HEADLINE_LINES = 2;

function checkSafeZone(box, size) {
  if (!box) return [];
  const safe = size.safe;
  const out = [];
  const over = (label, amount) => {
    if (amount > TOLERANCE) out.push(`${label} by ${Math.round(amount)}px`);
  };
  over('overflows the top safe zone', safe.top - box.top);
  over('overflows the bottom safe zone', box.bottom - (size.h - safe.bottom));
  over('overflows the left margin', safe.side - box.left);
  over('overflows the right margin', box.right - (size.w - safe.side));
  return out;
}

function checkQuality(q, variant) {
  const out = [];
  if (q.headlineLines > MAX_HEADLINE_LINES) {
    out.push(`headline runs to ${q.headlineLines} lines`);
  }
  // Photo mode fills the canvas by definition, so the share test is moot.
  if (!variant.photo && q.productShare < MIN_PRODUCT_SHARE) {
    out.push(`product fills only ${Math.round(q.productShare * 100)}% of the frame`);
  }
  return out;
}

async function main() {
  const wantGuides = process.argv.includes('--guides');
  const cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));

  fs.mkdirSync(OUT_DIR, { recursive: true });
  if (wantGuides || cfg.guides) fs.mkdirSync(GUIDE_DIR, { recursive: true });

  const browser = await chromium.launch();
  const templateUrl = 'file://' + TEMPLATE_FILE.split(path.sep).join('/');

  let written = 0;
  const safeWarn = [];
  const qualityWarn = [];
  const failures = [];

  for (const size of cfg.sizes) {
    console.log(`\n${size.name}  ${size.w}x${size.h}` +
      `   safe: top ${size.safe.top} / bottom ${size.safe.bottom} / sides ${size.safe.side}`);

    const page = await browser.newPage({
      viewport: { width: size.w, height: size.h },
      deviceScaleFactor: 1
    });
    await page.goto(templateUrl, { waitUntil: 'networkidle' });

    for (const variant of cfg.variants) {
      const name = `${variant.id}--${size.name}.png`;

      try {
        await draw(page, cfg.brand, variant, size, false);
        await page.screenshot({ path: path.join(OUT_DIR, name) });
        written += 1;

        const box = await page.evaluate(() => window.measureText());
        const q = await page.evaluate(s => window.measureQuality(s), size);

        const unsafe = checkSafeZone(box, size);
        const weak = checkQuality(q, variant);

        unsafe.forEach(p => safeWarn.push(`${name} — text ${p}`));
        weak.forEach(p => qualityWarn.push(`${name} — ${p}`));

        const flag = unsafe.length ? 'UNSAFE' : (weak.length ? 'weak  ' : 'ok    ');
        console.log(`  ${flag} ${name}` +
          (variant.photo ? '' : `   product ${Math.round(q.productShare * 100)}%`) +
          `   headline ${q.headlineLines}L`);

        if (wantGuides || cfg.guides) {
          await draw(page, cfg.brand, variant, size, true);
          await page.screenshot({ path: path.join(GUIDE_DIR, name) });
        }
      } catch (err) {
        failures.push(`${name} — ${err.message.split('\n')[0]}`);
        console.log('  FAIL   ' + name);
      }
    }

    await page.close();
  }

  await browser.close();

  console.log(`\n${written} creatives written to ${OUT_DIR}`);
  if (wantGuides || cfg.guides) {
    console.log(`Annotated proofs in ${GUIDE_DIR} — for checking only, never upload these.`);
  }

  if (safeWarn.length) {
    console.log('\nSafe zone problems (fix before running):');
    safeWarn.forEach(w => console.log('  ' + w));
  }

  if (qualityWarn.length) {
    console.log('\nWeak frames (legal, but they will underperform):');
    qualityWarn.forEach(w => console.log('  ' + w));
    console.log('\n  Long headline  -> shorten it, or set "headlineSize" on that variant.');
    console.log('  Small product  -> the source image has a lot of empty margin. Crop it,');
    console.log('                    or set "photo": true to let it fill the canvas.');
  }

  if (failures.length) {
    console.log('\nFailed:');
    failures.forEach(f => console.log('  ' + f));
    console.log('\nA failure is almost always a wrong image path in copy.json.');
  }

  if (!safeWarn.length && !qualityWarn.length && !failures.length) {
    console.log('All frames clear.');
  }
}

async function draw(page, brand, variant, size, guides) {
  await page.evaluate(
    ([b, v, s, g]) => window.render(b, v, s, { guides: g }),
    [brand, variant, size, guides]
  );
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => window.__imagesReady === true, null, { timeout: 15000 });
}

main().catch(err => {
  console.error('\nRun stopped: ' + err.message);
  process.exit(1);
});

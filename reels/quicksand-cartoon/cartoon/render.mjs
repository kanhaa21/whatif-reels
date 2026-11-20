// node render.mjs <outdir> "<frames>"   frames: "0-1092" or "5,40,90"
import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs';
const [outDir, spec] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
let frames = [];
for (const part of spec.split(',')) { const [a, b] = part.split('-').map(Number); if (b === undefined) frames.push(a); else for (let f = a; f <= b; f++) frames.push(f); }
if (process.env.RESUME) frames = frames.filter(f => !fs.existsSync(`${outDir}/f${String(f).padStart(4, '0')}.jpg`));
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('console', m => { if (m.type() === 'error') console.error('PAGE:', m.text()); });
page.on('pageerror', e => { console.error('PAGEERR:', e.message); process.exit(2); });
await page.goto('http://127.0.0.1:8765/index.html');
await page.waitForFunction(() => window.ready === true, null, { timeout: 120000 });
const t0 = Date.now(); let n = 0;
for (const f of frames) {
  const url = await page.evaluate(f => window.renderFrame(f), f);
  fs.writeFileSync(`${outDir}/f${String(f).padStart(4, '0')}.jpg`, Buffer.from(url.split(',')[1], 'base64'));
  n++; if (n % 25 === 0 || n === frames.length) console.log(`frame ${f} (${n}/${frames.length}) ${((Date.now() - t0) / n / 1000).toFixed(2)} s/frame`);
}
await browser.close();

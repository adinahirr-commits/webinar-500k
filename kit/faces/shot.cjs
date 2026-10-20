const puppeteer = require('/Users/adisomech/bank-sync/node_modules/puppeteer-core');
(async () => {
  const b = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new', args: ['--no-sandbox','--font-render-hinting=none']
  });
  const p = await b.newPage();
  await p.setViewport({width: +(process.argv[4]||390), height: 1200, deviceScaleFactor: 2, isMobile: (process.argv[4]||'390')==='390'});
  await p.goto('file://' + process.argv[2], {waitUntil: 'networkidle0'});
  // לכבות lazy כדי שהפריסה לא תזוז בזמן הצילום
  await p.evaluate(async () => {
    document.querySelectorAll('img[loading="lazy"]').forEach(i => i.loading = 'eager');
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 1200));
    window.scrollTo(0, 0);
    await Promise.all([...document.images].filter(i=>!i.complete).map(i=>new Promise(r=>{i.onload=i.onerror=r})));
  });
  await new Promise(r => setTimeout(r, 1000));
  const box = await p.evaluate(() => {
    const e = document.querySelector('#team'); const r = e.getBoundingClientRect();
    return {x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height};
  });
  await p.screenshot({path: process.argv[3], clip: box, captureBeyondViewport: true});
  const bad = await p.evaluate(() => {
    const out = {overflow: document.documentElement.scrollWidth > window.innerWidth + 1, broken: [], small: []};
    document.querySelectorAll('#team img').forEach(i => { if (!i.complete || i.naturalWidth === 0) out.broken.push(i.getAttribute('src')); });
    document.querySelectorAll('#team *').forEach(n => { const s = parseFloat(getComputedStyle(n).fontSize); if (n.children.length===0 && n.textContent.trim() && s < 14) out.small.push(n.textContent.trim().slice(0,30)+' @'+s); });
    return out;
  });
  console.log(JSON.stringify(bad, null, 1));
  await b.close();
})();

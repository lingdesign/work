"""Link-preview images (2400×1260): the headline beside the Goals phones, in the site's own fonts.
The title shrinks until it clears the first phone and fits the height."""
import asyncio, html, pathlib

HERE = pathlib.Path(__file__).resolve().parent / "og"
CHROME = "/usr/bin/google-chrome"
PHONE_LEFT = 1128          # where the first phone starts
GAP = 110                  # clear space kept before it

PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
{idealist}
@font-face{{font-family:"Instrument Sans";src:url(instrument-sans-latin-wght-normal.woff2) format("woff2");font-weight:400 700}}
html,body{{margin:0}}
body{{width:2400px;height:1260px;background:url(bg.png) 0 0/2400px 1260px;position:relative;overflow:hidden;color:#17151F}}
.t{{position:absolute;left:128px;top:0;bottom:0;width:{width}px;display:flex;flex-direction:column;justify-content:center}}
h1{{font-family:"Idealist",serif;font-weight:400;font-synthesis:none;font-size:var(--fs);line-height:1.02;letter-spacing:-.012em;margin:0;text-wrap:balance}}
.n{{font-family:"Instrument Sans",sans-serif;font-size:46px;line-height:1.25;margin:64px 0 0;letter-spacing:-.003em}}
.n b{{font-weight:500;display:block}}.n span{{color:#5D5970}}
</style></head><body>
<div class="t"><h1>{title}</h1><p class="n"><b>Ling-Hsuan Wang</b><span>Senior product designer</span></p></div>
</body></html>"""

FIT = """async () => {
  await document.fonts.ready;
  const h = document.querySelector('h1'), t = document.querySelector('.t');
  for (let fs = 122; fs >= 84; fs -= 2) {
    h.style.setProperty('--fs', fs + 'px');
    const r = document.createRange(); r.selectNodeContents(h);
    const right = Math.max(...[...r.getClientRects()].map(x => x.right));
    const kids = [...t.children].map(e => e.getBoundingClientRect());
    if (right <= %d && kids[0].top >= 140 && kids[1].bottom <= 1120) return fs;
  }
  return 0;
}""" % (PHONE_LEFT - GAP)


def render(jobs):
    """jobs: [(output_path, title)]"""
    asyncio.run(_render(jobs))


async def _render(jobs):
    from playwright.async_api import async_playwright
    idealist = (HERE / "idealist.css").read_text()
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME)
        page = await browser.new_page(viewport={"width": 2400, "height": 1260})
        for out, title in jobs:
            tmp = HERE / "_render.html"
            tmp.write_text(PAGE.format(idealist=idealist, width=PHONE_LEFT - GAP - 128, title=html.escape(title, quote=False)))
            await page.goto(tmp.as_uri())
            fs = await page.evaluate(FIT)
            if not fs:
                raise SystemExit(f"build stopped: link-preview title doesn't fit: {title}")
            png = out.with_suffix(".png")
            await page.screenshot(path=str(png))
            tmp.unlink()
            from PIL import Image
            Image.open(png).convert("RGB").save(out, quality=88)
            png.unlink()
        await browser.close()

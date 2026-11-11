"""Check every page in docs/ the way GitHub Pages will serve it (under /work/), on a phone and a desktop.

    python3 check.py [screenshot-folder]

Fails if any page has a missing file, a script error, a headline wider than the screen or longer than
4 lines on a phone, sideways scrolling, a company name in its visible text, or a link that goes nowhere.
"""
import asyncio, functools, http.server, pathlib, re, shutil, sys, tempfile, threading

ROOT = pathlib.Path(__file__).resolve().parent
COMPANIES = ["Anthropic", "Duolingo", "Meta", "Google", "DoorDash"]
SIZES = {"phone": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2),
         "desktop": dict(viewport={"width": 1440, "height": 900})}


def serve():
    site = pathlib.Path(tempfile.mkdtemp())
    shutil.copytree(ROOT / "docs", site / "work")
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=str(site))
    class Server(http.server.ThreadingHTTPServer):
        def handle_error(self, *a): pass   # a closed video stream is not a problem
    srv = Server(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_port}/work/"


async def main(shots):
    from playwright.async_api import async_playwright
    base = serve()
    landing = [""] + sorted(p.parent.name + "/" for p in (ROOT / "docs").glob("*/index.html") if p.parent.name != "assets")
    pages = landing + ["goals.html", "provider.html", "monument.html"]
    problems = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        for size, opts in SIZES.items():
            ctx = await browser.new_context(**opts)
            # Google Fonts can't be reached from the build machine; skip the wait (live pages load them)
            await ctx.route(re.compile(r"https://(fonts\.googleapis|fonts\.gstatic|cdn\.jsdelivr)"), lambda r: r.abort())
            for path in pages:
                pg = await ctx.new_page()
                name = path.rstrip("/") or "work"
                bad, errs = [], []
                pg.on("response", lambda r: bad.append(f"{r.status} {r.url}") if r.status >= 400 else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                await pg.goto(base + path, wait_until="load")
                await pg.wait_for_timeout(1200)
                for b in bad: problems.append(f"{name} ({size}): missing file {b}")
                for e in errs: problems.append(f"{name} ({size}): script error {e}")
                if await pg.evaluate("document.documentElement.scrollWidth > innerWidth + 1"):
                    problems.append(f"{name} ({size}): scrolls sideways")

                # every link to another page on this site must load
                links = await pg.evaluate("[...document.querySelectorAll('a[href]')].map(a => a.href)")
                for href in sorted({l.split('#')[0] for l in links if l.startswith(base.rsplit('/work/', 1)[0])}):
                    r = await ctx.request.get(href)
                    if r.status >= 400: problems.append(f"{name}: link to {href} is {r.status}")

                if path in landing:
                    h = await pg.evaluate("""(() => { const h = document.getElementById('hero-h');
                        const r = document.createRange(); r.selectNodeContents(h);
                        const tops = new Set([...r.getClientRects()].map(x => Math.round(x.top)));
                        return {lines: tops.size, wide: h.scrollWidth > h.clientWidth + 1}; })()""")
                    if h["wide"]: problems.append(f"{name} ({size}): headline wider than the screen")
                    if size == "phone" and h["lines"] > 4: problems.append(f"{name} (phone): headline runs {h['lines']} lines")
                    if path:
                        text = await pg.evaluate("document.body.innerText")
                        for c in COMPANIES:
                            if re.search(rf"\b{c}\b", text): problems.append(f"{name}: page text names {c}")
                        og = await pg.evaluate("document.querySelector('meta[property=\"og:image\"]').content")
                        local = og.replace("https://lingdesign.github.io/work/", base)
                        if (await ctx.request.get(local)).status >= 400: problems.append(f"{name}: link-preview image missing")
                    if shots and size == "phone":
                        await pg.screenshot(path=str(shots / f"{name}-phone.png"))
                await pg.close()
            await ctx.close()
        await browser.close()
    return problems


if __name__ == "__main__":
    shots = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if shots: shots.mkdir(parents=True, exist_ok=True)
    problems = asyncio.run(main(shots))
    if problems:
        print("\n".join(problems)); sys.exit(f"{len(problems)} problem(s)")
    print("all pages pass")

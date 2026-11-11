"""Build lingdesign.github.io/work from the main site, plus one landing page per company.

    python3 build.py ../lingdesign.github.io

Reads the main site (case studies, assets, homepage) and writes everything GitHub Pages serves into docs/:
  docs/index.html            /work: the industry-neutral landing page
  docs/<page>/index.html     /work/<page>: one per file in pages/, same layout, its own wording
  docs/goals.html ...        case studies, shared by every landing page

Every text edit must match exactly once, so a change on the main site that would leave an edit with
nowhere to land stops the build instead of publishing a half-edited page.
"""
import html, pathlib, re, shutil, sys

from wording import WORK_EDITS, CASE_EDITS, NOINDEX
import ogimage

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "docs"
BASE_URL = "https://lingdesign.github.io/work/"
CASE_STUDIES = ["goals.html", "provider.html", "monument.html"]
PROJECTS = {"goals": "p1", "provider": "p2", "monument": "p3"}   # article ids on the landing page


class BuildError(Exception):
    pass


def edit_once(text, old, new, where):
    n = text.count(old)
    if n != 1:
        raise BuildError(f"{where}: expected 1 match, found {n}:\n  {old[:90]}")
    return text.replace(old, new)


# ── pages/<name>.txt ─────────────────────────────────────────────────────────

def parse_page(path):
    """key: value lines, '- ' list items under 'lines:', '#' comments. Straight quotes become curly."""
    page, key = {"lines": []}, None
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- "):
            if key != "lines":
                raise BuildError(f"{path.name}:{n}: a '- ' item outside 'lines:'")
            page["lines"].append(curly(line[2:].strip()))
            continue
        if ":" not in line:
            raise BuildError(f"{path.name}:{n}: expected 'key: value'")
        key, value = (s.strip() for s in line.split(":", 1))
        if key != "lines":
            page[key] = curly(value)
    for need in ["headline", "headline2", "hello", "order", "lines"]:
        if not page.get(need):
            raise BuildError(f"{path.name}: missing '{need}'")
    page["order"] = [s.strip() for s in page["order"].split(",")]
    if sorted(page["order"]) != sorted(PROJECTS):
        raise BuildError(f"{path.name}: order must list {', '.join(PROJECTS)} once each")
    return page


def curly(s):
    s = re.sub(r"(?<=\w)'", "’", s)
    s = re.sub(r"'(?=\w)", "‘", s)
    return re.sub(r'"(?=\w)', "“", s).replace('"', "”")


# ── the landing pages ────────────────────────────────────────────────────────

def work_page(main_index):
    t = main_index.read_text()
    for old, new in WORK_EDITS:
        t = edit_once(t, old, new, "work landing page")
    return t


def company_page(work_html, slug, page):
    t, where = work_html, f"pages/{slug}.txt"
    esc = lambda s: html.escape(s, quote=False)
    attr = lambda s: html.escape(s, quote=True)

    # headline
    t, n = re.subn(r'<span class="lead">[^<]*</span> <span class="rest">[^<]*</span>',
                   f'<span class="lead">{esc(page["headline"])}</span> <span class="rest">{esc(page["headline2"])}</span>', t)
    if n != 1: raise BuildError(f"{where}: headline not found")

    # rotating lines under the headline
    items = "\n".join(f'          <li class="side{" on" if i == 0 else ""}">{esc(s)}</li>' for i, s in enumerate(page["lines"]))
    t, n = re.subn(r'(<ul class="sides-list">\n).*?(\n\s*</ul>)', lambda m: m.group(1) + items + m.group(2), t, flags=re.S)
    if n != 1: raise BuildError(f"{where}: rotating lines not found")

    # the bio's first paragraph
    t, n = re.subn(r'(<div class="pre-copy">\s*<p class="pre-text">)[^<]*(</p>)',
                   lambda m: m.group(1) + esc(page["hello"]) + m.group(2), t)
    if n != 1: raise BuildError(f"{where}: bio not found")

    # project one-liners, then project order
    for name, pid in PROJECTS.items():
        if page.get(name):
            t, n = re.subn(rf'(aria-labelledby="{pid}">.*?<p class="thesis">)[^<]*(</p>)',
                           lambda m: m.group(1) + esc(page[name]) + m.group(2), t, count=1, flags=re.S)
            if n != 1: raise BuildError(f"{where}: one-liner for {name} not found")
    blocks = {pid: re.search(rf'      <article class="project grid" aria-labelledby="{pid}">.*?</article>\n', t, re.S)
              for pid in PROJECTS.values()}
    if not all(blocks.values()): raise BuildError(f"{where}: project blocks not found")
    first = min(b.start() for b in blocks.values()); last = max(b.end() for b in blocks.values())
    t = t[:first] + "".join(blocks[PROJECTS[name]].group(0) for name in page["order"]) + t[last:]

    # link preview
    title = f'{page["headline"]} {page["headline2"]}'
    t = edit_once(t, '<meta property="og:url" content="https://lingdesign.github.io/work/">',
                  f'<meta property="og:url" content="{BASE_URL}{slug}/">', where)
    t = edit_once(t, '<meta property="og:image" content="https://lingdesign.github.io/work/assets/og.jpg">',
                  f'<meta property="og:image" content="{BASE_URL}{slug}/og.jpg">', where)
    t = re.sub(r'<meta property="og:title" content="[^"]*">',
               f'<meta property="og:title" content="Ling-Hsuan Wang · {attr(title.rstrip("."))}">', t, count=1)
    t = re.sub(r'<meta property="og:image:alt" content="[^"]*">',
               f'<meta property="og:image:alt" content="“{attr(title)}” Ling-Hsuan Wang, senior product designer, beside three screens from the Fay Goals redesign.">', t, count=1)

    # this page lives one folder down: point its own files back up to /work
    t = re.sub(r'''((?:src|href|poster)=["'])(?=assets/|(?:goals|provider|monument|sculpture|index)\.html)''', r"\1../", t)
    t = re.sub(r'url\((["\']?)(?=assets/)', r"url(\1../", t)
    return t, title


def main(main_dir):
    main_dir = pathlib.Path(main_dir).resolve()
    if not (main_dir / "index.html").exists():
        raise BuildError(f"main site not found at {main_dir}")

    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(main_dir / "assets", OUT / "assets")
    for f in CASE_STUDIES + ["sculpture.html", ".nojekyll"]:
        shutil.copy2(main_dir / f, OUT / f)

    for f in CASE_STUDIES:
        p = OUT / f
        t = p.read_text()
        t = edit_once(t, "</title>", "</title>\n" + NOINDEX, f)
        for old, new in CASE_EDITS:
            t = edit_once(t, old, new, f)
        p.write_text(t)

    work_html = work_page(main_dir / "index.html")
    (OUT / "index.html").write_text(work_html)
    images = [(OUT / "assets" / "og.jpg", "Designing products people trust, from onboarding to daily habit.")]

    for src in sorted((ROOT / "pages").glob("*.txt")):
        slug = src.stem
        page = parse_page(src)
        out_html, title = company_page(work_html, slug, page)
        (OUT / slug).mkdir()
        (OUT / slug / "index.html").write_text(out_html)
        images.append((OUT / slug / "og.jpg", title))
        print(f"  /work/{slug}/")

    ogimage.render(images)
    print(f"built {OUT}")


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "../lingdesign.github.io")
    except BuildError as e:
        sys.exit(f"build stopped: {e}")

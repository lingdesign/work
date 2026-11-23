"""A cover letter that unfolds over a company landing page on arrival, and folds away when dismissed.

pages/<slug>.letter.txt holds the words; this module turns them into markup, styles and a script that the
build injects into that one page. Without JavaScript the letter never shows and the page works as usual.
"""
import html, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ICON = (HERE / "og" / "letter-icon.svg").read_text().strip()


def parse(path, curly):
    data, paras, buf = {}, [], []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line.startswith("#"):
            continue
        m = re.match(r"^(label|greeting|closing|signature|name|button):\s*(.*)$", line)
        if m:
            data[m.group(1)] = curly(m.group(2))
            continue
        if not line:
            if buf: paras.append(" ".join(buf)); buf = []
            continue
        buf.append(line)
    if buf: paras.append(" ".join(buf))
    for need in ["greeting", "closing", "signature", "button"]:
        if not data.get(need):
            raise ValueError(f"{path.name}: missing '{need}'")
    if not paras:
        raise ValueError(f"{path.name}: no paragraphs")
    data["paras"] = [curly(p) for p in paras]
    return data


def render(data):
    esc = lambda s: html.escape(s, quote=False)
    glue = lambda s: re.sub(r"\b(I|a|A) ", "\\1\u00a0", s)   # never leave "I" or "a" alone at the end of a line
    body = "\n".join(f"        <p>{esc(glue(p))}</p>" for p in data["paras"])
    label = f'<p class="lt-label">{esc(data["label"])}</p>' if data.get("label") else ""
    name_line = f'        <p class="lt-name">&mdash; {esc(data["name"])}</p>\n' if data.get("name") else ""
    markup = f"""
<div class="lt" id="letter" hidden>
  <div class="lt-bg" data-close></div>
  <div class="lt-stage">
    <article class="lt-sheet" role="dialog" aria-modal="true" aria-labelledby="lt-greeting" tabindex="-1">
      <button class="lt-x" type="button" data-close aria-label="Close the letter"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
      <div class="lt-scroll" tabindex="0">
        <div class="lt-mark">{ICON}</div>
        {label}
        <h2 class="lt-greeting" id="lt-greeting">{esc(data["greeting"])}</h2>
{body}
        <p class="lt-closing">{esc(data["closing"])}</p>
        <div class="lt-foot">
          <div><p class="lt-sig">{esc(data["signature"])}</p>
{name_line}          </div>
          <button class="lt-go" type="button" data-close>{esc(data["button"])}<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10h11m-4-4.5L15.5 10 11 14.5"/></svg></button>
        </div>
      </div>
    </article>
  </div>
</div>
<button class="lt-reopen" id="letter-reopen" type="button" hidden aria-label="Open my letter again"><span class="lt-reopen-mark" aria-hidden="true">{ICON}</span><span>Letter</span></button>
"""
    return markup, CSS, JS


CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mrs+Saint+Delafield&display=swap">
<style id="letter-css">
.lt{position:fixed;inset:0;z-index:1000;display:grid;place-items:center}
.lt[hidden],.lt-reopen[hidden]{display:none}
.lt-bg{position:absolute;inset:0;background:color-mix(in srgb,var(--paper,#F6F5FB) 62%,transparent);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);opacity:0;transition:opacity .45s ease}
.lt.on .lt-bg{opacity:1}
.lt-stage{position:relative;perspective:1800px;width:min(600px,calc(100vw - 32px))}
.lt-sheet{position:relative;max-height:min(92vh,980px);display:flex;flex-direction:column;
  background:#FFFEFC var(--paper-grain,none);color:#17151F;border-radius:14px;
  box-shadow:0 1px 0 #ECE9F4,0 2px 0 #E2DEEE,0 3px 0 #D9D4E8,0 30px 80px -20px rgba(120,100,210,.35),0 10px 30px -10px rgba(23,21,31,.18)}
.lt-sheet:focus{outline:none}
.lt-sheet::before{content:"";position:absolute;inset:10px;border:1px solid rgba(23,21,31,.08);border-radius:8px;pointer-events:none;z-index:1}
.lt-sheet::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;z-index:1;
  background:linear-gradient(to bottom,transparent calc(33.33% - 18px),rgba(23,21,31,.028) 33.33%,rgba(255,255,255,.35) calc(33.33% + 2px),transparent calc(33.33% + 22px),
    transparent calc(66.66% - 18px),rgba(23,21,31,.028) 66.66%,rgba(255,255,255,.35) calc(66.66% + 2px),transparent calc(66.66% + 22px))}
.lt-scroll{position:relative;z-index:2;overflow:auto;overscroll-behavior:contain;padding:44px 56px 34px;outline:none;border-radius:inherit}
.lt-scroll:focus-visible{box-shadow:inset 0 0 0 2px #17151F}
.lt-mark{display:flex;justify-content:center;margin-bottom:14px}
.lt-mark svg{width:48px;height:48px;color:#111!important}
.lt-label{font:500 12px/1.4 "Instrument Sans",system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;text-align:center;color:#5D5970;margin:0 0 18px}
.lt-greeting{font-family:"Idealist",Georgia,serif;font-weight:400;font-size:clamp(30px,5vw,40px);line-height:1.08;letter-spacing:-.01em;margin:0 0 16px}
.lt-scroll p{font:400 17px/1.58 "Instrument Sans",system-ui,sans-serif;margin:0 0 14px;text-wrap:pretty}
.lt-closing{margin-top:18px!important}
.lt-foot{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-top:22px}
.lt-sig{font-family:"Mrs Saint Delafield",cursive!important;font-size:58px!important;line-height:1!important;margin:0 0 0 -4px!important;padding-top:4px;transform:rotate(-4deg);transform-origin:left;color:#111}
.lt-name{font-weight:600!important;margin-top:2px!important}
.lt-go{display:inline-flex;align-items:center;gap:8px;margin:0 0 6px;padding:12px 18px 12px 20px;flex:none;border:0;border-radius:999px;cursor:pointer;
  background:#17151F;color:#fff;font:500 15px/1 "Instrument Sans",system-ui,sans-serif}
.lt-go svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;transition:transform .2s ease}
.lt-go:hover svg{transform:translateX(3px)}
.lt-go:focus-visible,.lt-x:focus-visible,.lt-reopen:focus-visible{outline:2px solid #17151F;outline-offset:3px}
.lt-x{position:absolute;top:18px;right:18px;z-index:3;width:40px;height:40px;border-radius:999px;border:0;background:transparent;cursor:pointer;display:grid;place-items:center;color:#5D5970}
.lt-x:hover{background:rgba(23,21,31,.06);color:#17151F}
.lt-x svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round}
/* the fold: three strips of the sheet, hinged at the creases */
.lt-fold{position:absolute;left:0;top:0;width:100%;transform-style:preserve-3d;pointer-events:none}
.lt-panel{position:absolute;left:0;width:100%;transform-style:preserve-3d;transition:transform .8s cubic-bezier(.3,.7,.2,1)}
.lt-face,.lt-back{position:absolute;inset:0;overflow:hidden;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:#FFFEFC var(--paper-grain,none)}
.lt-back{transform:rotateX(180deg);background:#FBFAF7 var(--paper-grain,none);display:grid;place-items:center;align-content:center;gap:10px}
.lt-back svg{width:44px;height:44px;color:#111!important}
.lt-back span{font:500 11px/1.4 "Instrument Sans",system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#5D5970}
.lt-p0{transform-origin:50% 100%}.lt-p2{transform-origin:50% 0}
.lt-p0 .lt-face{border-radius:14px 14px 0 0}.lt-p2 .lt-face{border-radius:0 0 14px 14px}
.lt-p0 .lt-back{border-radius:0 0 14px 14px}.lt-p2 .lt-back{border-radius:14px 14px 0 0}
.lt-face>.lt-copy{position:absolute;left:0;width:100%}
.lt.folded .lt-p0{transform:rotateX(-179.5deg)}
.lt.folded .lt-p2{transform:rotateX(179deg)}
.lt-move{transition:transform .55s cubic-bezier(.3,.7,.2,1),opacity .55s ease}
.lt-reopen{position:fixed;left:20px;bottom:20px;z-index:900;display:inline-flex;align-items:center;gap:8px;padding:8px 14px 8px 10px;border-radius:999px;
  border:1px solid rgba(23,21,31,.1);background:#FFFEFC;color:#17151F;cursor:pointer;font:500 14px/1 "Instrument Sans",system-ui,sans-serif;
  box-shadow:0 8px 24px -8px rgba(120,100,210,.4);opacity:0;transform:translateY(8px);transition:opacity .4s ease,transform .4s ease}
.lt-reopen.on{opacity:1;transform:none}
.lt-reopen-mark svg{width:22px;height:22px;display:block;color:#111!important}
@media (max-width:600px){.lt-scroll{padding:40px 26px 32px}.lt-scroll p{font-size:16px}.lt-sig{font-size:54px!important}.lt-reopen{left:14px;bottom:14px}}
@media (prefers-reduced-motion:reduce){.lt-panel,.lt-move,.lt-bg,.lt-reopen{transition:none!important}}
</style>
"""

JS = """
<script>
(() => {
  const root = document.getElementById('letter'), reopen = document.getElementById('letter-reopen');
  if (!root) return;
  const sheet = root.querySelector('.lt-sheet'), stage = root.querySelector('.lt-stage'), scroller = root.querySelector('.lt-scroll');
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const seen = () => { try { return sessionStorage.getItem('letter-seen') === '1'; } catch (e) { return false; } };
  const markSeen = () => { try { sessionStorage.setItem('letter-seen', '1'); } catch (e) {} };
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const frame = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  let opener = null, busy = false;

  // three strips of the sheet as it looks now, hinged at the creases
  function buildFold() {
    const h = sheet.offsetHeight, third = h / 3, top = scroller.scrollTop;
    const fold = document.createElement('div');
    fold.className = 'lt-fold'; fold.setAttribute('aria-hidden', 'true'); fold.style.height = h + 'px';
    for (let i = 0; i < 3; i++) {
      const p = document.createElement('div');
      p.className = 'lt-panel lt-p' + i; p.style.top = (i * third) + 'px'; p.style.height = third + 'px';
      const face = document.createElement('div'); face.className = 'lt-face';
      const copy = sheet.cloneNode(true);
      copy.removeAttribute('role'); copy.removeAttribute('aria-modal'); copy.className = 'lt-sheet lt-copy';
      copy.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
      copy.style.cssText = 'position:absolute;left:0;width:100%;height:' + h + 'px;top:' + (-i * third) + 'px;box-shadow:none;border-radius:14px';
      copy.querySelector('.lt-scroll').scrollTop = top;
      face.appendChild(copy);
      if (i !== 1) { const back = document.createElement('div'); back.className = 'lt-back';
        if (i === 0) { const m = sheet.querySelector('.lt-mark svg'), l = sheet.querySelector('.lt-label');
          if (m) back.appendChild(m.cloneNode(true)); if (l) { const s = document.createElement('span'); s.textContent = l.textContent; back.appendChild(s); } }
        p.appendChild(back); }
      p.appendChild(face); fold.appendChild(p);
      requestAnimationFrame(() => { copy.querySelector('.lt-scroll').scrollTop = top; });
    }
    stage.appendChild(fold);
    return fold;
  }

  function trap(e) {
    if (e.key === 'Escape') { e.preventDefault(); close(); return; }
    if (e.key !== 'Tab') return;
    const f = [...sheet.querySelectorAll('button, [tabindex="0"]')];
    const first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  async function open() {
    if (busy) return; busy = true;
    opener = document.activeElement;
    reopen.classList.remove('on'); reopen.hidden = true;
    root.hidden = false; document.documentElement.style.overflow = 'hidden';
    document.addEventListener('keydown', trap);
    if (calm) { root.classList.add('on'); sheet.focus(); busy = false; return; }
    sheet.style.visibility = 'hidden';
    await frame();
    root.classList.add('folded');          // arrive already folded: the strips start shut, with no transition
    const fold = buildFold();
    fold.classList.add('lt-move'); fold.style.opacity = '0'; fold.style.transform = 'translateY(40px) scale(.96)';
    await frame();
    root.classList.add('on'); fold.style.opacity = '1'; fold.style.transform = 'none';
    await wait(500);
    fold.querySelector('.lt-p0').style.transitionDelay = '0s';
    fold.querySelector('.lt-p2').style.transitionDelay = '.22s';
    root.classList.remove('folded');
    await wait(1050);
    sheet.style.visibility = ''; fold.remove();
    sheet.focus({ preventScroll: true });
    busy = false;
  }

  async function close() {
    if (busy || root.hidden) return; busy = true;
    markSeen();
    document.removeEventListener('keydown', trap);
    if (!calm) {
      const fold = buildFold(); sheet.style.visibility = 'hidden';
      await frame();
      fold.querySelector('.lt-p2').style.transitionDelay = '0s';
      fold.querySelector('.lt-p0').style.transitionDelay = '.18s';
      root.classList.add('folded');
      await wait(900);
      const r = reopen.getBoundingClientRect(), s = stage.getBoundingClientRect();
      reopen.hidden = false;
      const rr = reopen.getBoundingClientRect();
      const dx = (rr.left + rr.width / 2) - (s.left + s.width / 2), dy = (rr.top + rr.height / 2) - (s.top + sheet.offsetHeight / 2);
      fold.classList.add('lt-move'); fold.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(.12)'; fold.style.opacity = '0';
      root.classList.remove('on');
      await wait(560);
      fold.remove(); root.classList.remove('folded');
    } else { reopen.hidden = false; root.classList.remove('on'); }
    sheet.style.visibility = ''; root.hidden = true; document.documentElement.style.overflow = '';
    reopen.hidden = false; await frame(); reopen.classList.add('on');
    if (opener && opener !== document.body && document.contains(opener)) opener.focus({ preventScroll: true });
    busy = false;
  }

  root.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', close));
  reopen.addEventListener('click', open);
  if (seen()) { reopen.hidden = false; requestAnimationFrame(() => reopen.classList.add('on')); }
  else if (document.readyState === 'complete') open();
  else addEventListener('load', () => setTimeout(open, 250), { once: true });
})();
</script>
"""

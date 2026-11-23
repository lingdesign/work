"""A cover letter that unfolds over a company landing page on arrival, and folds away when dismissed.

pages/<slug>.letter.txt holds the words; this module turns them into markup, styles and a script that the
build injects into that one page. Without JavaScript the letter never shows and the page works as usual.
"""
import html, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ICON = (HERE / "og" / "letter-rocker.svg").read_text().strip()   # the rocker from the main site's "New sculpture" button
ARROW = (HERE / "og" / "letter-arrow.svg").read_text().strip()  # the dot and arrow from "Read the case study"


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
          <button class="cta lt-go" type="button" data-close>{esc(data["button"])}{ARROW}</button>
        </div>
      </div>
    </article>
  </div>
</div>
"""
    return markup, CSS, JS


CSS = """
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Mrs+Saint+Delafield&display=swap">
<style id="letter-css">
.lt{position:fixed;inset:0;z-index:1000;display:grid;place-items:center}
.lt[hidden]{display:none}
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
.lt-mark svg{width:30px;height:30px;color:#111!important;fill:currentColor;overflow:visible}
.lt-scroll .lt-label{font-family:var(--text,"Instrument Sans",system-ui,sans-serif);font-weight:400;font-size:var(--fs-label,.8333rem);line-height:1.3;letter-spacing:.08em;text-transform:uppercase;text-align:center;color:var(--ink-2,#5D5970);margin:0 0 18px}
.lt-greeting{font-family:"Idealist",Georgia,serif;font-weight:400;font-size:clamp(30px,5vw,40px);line-height:1.08;letter-spacing:-.01em;margin:0 0 16px}
.lt-scroll p{font-family:var(--text,"Instrument Sans",system-ui,sans-serif);font-weight:400;font-size:var(--fs-body,17px);line-height:1.58;margin:0 0 14px;text-wrap:pretty}
.lt-closing{margin-top:18px!important}
.lt-foot{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-top:22px}
.lt-sig{font-family:"Mrs Saint Delafield",cursive!important;font-size:58px!important;line-height:1!important;margin:0 0 0 -4px!important;padding-top:4px;transform:rotate(-4deg);transform-origin:left;color:#111}
.lt-name{font-weight:600!important;margin-top:2px!important}
.lt-scroll .lt-go{margin:0 0 6px;flex:none;align-self:auto}
.lt-go svg{fill:currentColor;overflow:visible}
.lt-go:focus-visible,.lt-x:focus-visible{outline:2px solid #17151F;outline-offset:3px}
.lt-x{position:absolute;top:18px;right:18px;z-index:3;width:40px;height:40px;border-radius:999px;border:0;background:transparent;cursor:pointer;display:grid;place-items:center;color:#5D5970}
.lt-x:hover{background:rgba(23,21,31,.06);color:#17151F}
.lt-x svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round}
/* the fold: three strips of the sheet, hinged at the creases */
.lt-fold{position:absolute;left:0;top:0;width:100%;transform-style:preserve-3d;pointer-events:none}
.lt-panel{position:absolute;left:0;width:100%;transform-style:preserve-3d}
.lt-face,.lt-back{position:absolute;inset:0;overflow:hidden;backface-visibility:hidden;-webkit-backface-visibility:hidden;background:#FFFEFC var(--paper-grain,none)}
.lt-back{transform:rotateX(180deg);background:#FBFAF7 var(--paper-grain,none);display:grid;place-items:center;align-content:center;gap:10px}
.lt-back svg{width:28px;height:28px;color:#111!important;fill:currentColor;overflow:visible}
.lt-back span{font:500 11px/1.4 "Instrument Sans",system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:#5D5970}
.lt-p0{transform-origin:50% 100%}.lt-p2{transform-origin:50% 0}
.lt-p0 .lt-face{border-radius:14px 14px 0 0}.lt-p2 .lt-face{border-radius:0 0 14px 14px}
.lt-p0 .lt-back{border-radius:0 0 14px 14px}.lt-p2 .lt-back{border-radius:14px 14px 0 0}
.lt-face>.lt-copy{position:absolute;left:0;width:100%}
.lt-shade{position:absolute;left:0;top:0;width:100%;height:100%;border-radius:14px;pointer-events:none;
  box-shadow:0 1px 0 #ECE9F4,0 2px 0 #E2DEEE,0 3px 0 #D9D4E8,0 30px 80px -20px rgba(120,100,210,.35),0 10px 30px -10px rgba(23,21,31,.18);
  transition:top .8s cubic-bezier(.3,.7,.2,1),height 1s cubic-bezier(.3,.7,.2,1)}
/* the folded letter casts its shadow from the packet it is folded into */
.lt.folded .lt-shade{top:33.333%;height:33.334%;border-radius:4px}
.lt-move{transition:transform .55s cubic-bezier(.3,.7,.2,1),opacity .55s ease}
@media (max-width:600px){.lt-scroll{padding:40px 26px 32px}.lt-sig{font-size:54px!important}}
@media (prefers-reduced-motion:reduce){.lt-move,.lt-bg,.lt-shade{transition:none!important}}
</style>
"""

JS = """
<script>
(() => {
  const root = document.getElementById('letter');
  if (!root) return;
  const sheet = root.querySelector('.lt-sheet'), stage = root.querySelector('.lt-stage'), scroller = root.querySelector('.lt-scroll');
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const seen = () => { try { return localStorage.getItem('letter-seen') === '1'; } catch (e) { return false; } };
  const markSeen = () => { try { localStorage.setItem('letter-seen', '1'); } catch (e) {} };
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const frame = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  let opener = null, busy = false;
  // play an icon's motion once, as the main site does
  const play = svg => { if (!svg || calm) return; svg.querySelectorAll('animateTransform').forEach(a => { try { a.beginElement(); } catch (e) {} }); };
  const mark = root.querySelector('.lt-mark svg'), go = root.querySelector('.lt-go'), arrow = go && go.querySelector('svg');
  if (mark) mark.addEventListener('pointerenter', () => play(mark));
  if (go) { go.addEventListener('pointerenter', () => play(arrow)); go.addEventListener('focus', () => play(arrow)); }
  // the sheen follows the mouse, as on the site's other buttons
  if (go && !calm) {
    go.addEventListener('pointermove', e => { if (e.pointerType !== 'mouse') return; const r = go.getBoundingClientRect();
      go.style.setProperty('--sx', (100 - (e.clientX - r.left) / r.width * 100) + '%'); });
    go.addEventListener('pointerleave', () => go.style.removeProperty('--sx'));
  }

  // three strips of the sheet as it looks now, hinged at the creases
  const SHUT = [-179.5, 0, 179];
  function turn(p, a) {
    p.style.transform = 'rotateX(' + a + 'deg)';
    const away = Math.abs(a) > 90, face = p.querySelector('.lt-face'), back = p.querySelector('.lt-back');
    face.style.visibility = away ? 'hidden' : 'visible';
    if (back) back.style.visibility = away ? 'visible' : 'hidden';
  }
  const ease = t => 1 - Math.pow(1 - t, 3);
  function swing(p, from, to, ms, delay) {
    return new Promise(done => {
      let t0 = null;
      const step = now => { if (t0 === null) t0 = now + delay;
        const t = Math.min(1, Math.max(0, (now - t0) / ms));
        turn(p, from + (to - from) * ease(t));
        if (t < 1) requestAnimationFrame(step); else done(); };
      requestAnimationFrame(step);
    });
  }
  function buildFold() {
    const h = sheet.offsetHeight, third = h / 3, top = scroller.scrollTop;
    const fold = document.createElement('div');
    fold.className = 'lt-fold'; fold.setAttribute('aria-hidden', 'true'); fold.style.height = h + 'px';
    const shade = document.createElement('div'); shade.className = 'lt-shade'; fold.appendChild(shade);
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
      if (i !== 1) turn(p, root.classList.contains('folded') ? SHUT[i] : 0);
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
    root.classList.remove('folded');   // the shadow opens with the letter
    await Promise.all([swing(fold.querySelector('.lt-p0'), SHUT[0], 0, 800, 0), swing(fold.querySelector('.lt-p2'), SHUT[2], 0, 800, 220)]);
    sheet.style.visibility = ''; fold.remove();
    sheet.focus({ preventScroll: true });
    busy = false;
    setTimeout(() => play(mark), 150);
  }

  async function close() {
    if (busy || root.hidden) return; busy = true;
    markSeen();
    document.removeEventListener('keydown', trap);
    if (!calm) {
      const fold = buildFold(); sheet.style.visibility = 'hidden';
      await frame();
      root.classList.add('folded');
      await Promise.all([swing(fold.querySelector('.lt-p2'), 0, SHUT[2], 700, 0), swing(fold.querySelector('.lt-p0'), 0, SHUT[0], 700, 180)]);
      fold.classList.add('lt-move'); fold.style.transform = 'translateY(48px) scale(.9)'; fold.style.opacity = '0';
      root.classList.remove('on');
      await wait(560);
      fold.remove(); root.classList.remove('folded');
    } else { root.classList.remove('on'); }
    sheet.style.visibility = ''; root.hidden = true; document.documentElement.style.overflow = '';
    if (opener && opener !== document.body && document.contains(opener)) opener.focus({ preventScroll: true });
    root.remove();   // once closed, the letter is gone for good
  }

  root.querySelectorAll('[data-close]').forEach(el => el.addEventListener('click', close));
  if (seen()) root.remove();
  else if (document.readyState === 'complete') open();
  else addEventListener('load', () => setTimeout(open, 250), { once: true });
})();
</script>
"""

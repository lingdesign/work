"""The wording that turns the main (healthcare) site into /work. Each pair: text on the main site → text on /work.
Each old text must appear exactly once on the main site, or the build stops."""

NOINDEX = '<meta name="robots" content="noindex, nofollow">'

# /work landing page
WORK_EDITS = [
  # meta
  ('<meta name="description" content="Ling-Hsuan Wang, product designer in New York. Selected work.">',
   '<meta name="description" content="Ling-Hsuan Wang, senior product designer in New York. Consumer apps and expert tools. Selected work.">'),
  ('<meta property="og:url" content="https://lingdesign.github.io/">',
   '<meta property="og:url" content="https://lingdesign.github.io/work/">'),
  ('<meta property="og:title" content="Ling-Hsuan Wang · Designing for every side of care">',
   '<meta property="og:title" content="Ling-Hsuan Wang · Designing products people trust">'),
  ('<meta property="og:description" content="Senior product designer in healthcare, based in New York. Selected work.">',
   '<meta property="og:description" content="Senior product designer, based in New York. Selected work.">'),
  # header role
  ('<span class="role-long">Senior product designer in healthcare, based in New York</span>',
   '<span class="role-long">Senior product designer, based in New York</span>'),
  ('Sr. product designer<span class="hc"> in healthcare</span>',
   'Sr. product designer'),
  # hero
  ('<span class="lead">Designing for</span> <span class="rest">every side of care.</span>',
   '<span class="lead">Designing products people trust,</span> <span class="rest">from onboarding to daily habit.</span>'),
  ('aria-label="Sides of care I design for"', 'aria-label="What I’ve designed"'),
  ('<li class="side on">Simplified onboarding, more patients starting care.</li>',
   '<li class="side on">Simplified onboarding, signup-to-paid conversion from 26.7% to 56%.</li>'),
  ('<li class="side">Designed upfront pricing, patients booking at ease.</li>',
   '<li class="side">Designed upfront pricing, people booking at ease.</li>'),
  ('<li class="side">Mapped patient and provider journeys, MVPs built around real needs.</li>',
   '<li class="side">Mapped both sides of the product, MVPs built around real needs.</li>'),
  ('<li class="side">Visualized progress, keeping patients on track between visits.</li>',
   '<li class="side">Replaced a prize draw with real progress, a daily habit that counts.</li>'),
  ('<li class="side">Redesigned provider to-dos, every note on time and every license current.</li>',
   '<li class="side">Redesigned to-dos for experts, every deadline met.</li>\n          <li class="side">Prototyped in code with Claude, a feature shipped in a day.</li>'),
  # about
  ('<p class="pre-text">Hi, I’m Ling. I make healthcare products work better for the people receiving care, the people delivering it, and the business making it possible.</p>',
   '<p class="pre-text">Hi, I’m Ling. I design products people trust: for the people who use them, the experts who serve them, and the business making it possible.</p>'),
  ('<p class="pre-text">I own projects from setting product strategy to crafting the final details in production. Over six years, I’ve designed for mental health, physical health, sports, sleep, and nutrition. I&nbsp;bring patient insights and data into business decisions to shape where the experience goes next, protect what patients value, and help more people reach the care they need.</p>',
   '<p class="pre-text">I own projects from setting product strategy to crafting the final details in production. Over eight years, I’ve designed consumer apps and expert tools, mostly in healthcare, where trust is hard to earn and easy to lose. I&nbsp;bring research and data into product decisions, and I prototype in code with Claude Code, so teams react to working versions, not static mockups.</p>'),
  ('<div><dt>Domain</dt><dd>Consumer, healthcare, expert tools</dd></div>',
   '<div><dt>Domain</dt><dd>Consumer apps, expert tools, healthcare</dd></div>'),
  ('<div><dt>Strengths</dt><dd>Problem framing, complex workflows, end-to-end&nbsp;craft</dd></div>',
   '<div><dt>Strengths</dt><dd>Problem framing, design systems, end-to-end&nbsp;craft</dd></div>\n          <div><dt>Tools</dt><dd>Figma, Claude Code</dd></div>'),
  # project 1
  ('<p class="thesis">From a dopamine hit to strengthening the patient–provider relationship.</p>',
   '<p class="thesis">From a prize draw to progress that counts.</p>'),
  ('I owned visual, interaction and motion design, and added its patterns to the design system.</p>',
   'I owned visual, interaction and motion design, prototyped AI-assisted goal writing with Claude, and added its patterns to the design system.</p>'),
  # project 2
  ('<p class="thesis">From one nudge to a notification system providers can act on.</p>',
   '<p class="thesis">From one nudge to a notification system, built in code.</p>'),
  ('<p>Asked for one nudge, I redesigned the appointment blade around each provider’s main task, built it in code, and turned two separate asks into one notification system. By the end, every provider was compliant and every appointment was submitted within 72 hours.</p>',
   '<p>Asked for one nudge, I used our data to redefine the ask, redesigned the appointment blade around each provider’s main task, and built it with Claude Code. Two separate asks became one pattern in the design system. By the end, every provider was compliant and every appointment was submitted within 72 hours.</p>'),
  # project 3
  ('<p class="caps">Health and wellness<i class="dot"></i>Consumer product</p>',
   '<p class="caps">Consumer product<i class="dot"></i>Onboarding and conversion</p>'),
  ('<p class="thesis">From signup to treatment in 2 days, down from 11.</p>',
   '<p class="thesis">Signup-to-paid conversion from 26.7% to 56%, in the first week.</p>'),
  ('<p>I led the onboarding redesign for people starting alcohol recovery treatment, fixing the three biggest drop-off points we found in funnel analysis. In the first week after launch, signup-to-paid conversion rose from 26.7% to 56%.</p>',
   '<p>I led the onboarding redesign for people starting alcohol recovery treatment, from funnel analysis to four rounds of usability testing, and fixed the three biggest drop-off points. People went from signup to treatment in 2 days, down from 11.</p>'),
  # side projects
  ('<h2 id="side-h">Beyond healthcare</h2>', '<h2 id="side-h">Built from zero</h2>'),
  # footer
  ('I’m looking for my next Staff or Senior role on a team building care people can rely on. Always happy to talk about healthcare products, design, and creative practice.',
   'I’m looking for my next Staff or Senior role on a team building products people rely on. Always happy to talk about product, design, and creative practice.'),
]

WORK_EDITS += [
  # rotating lines under the headline: wrap within the headline's column instead of running under the sculpture
  ('.sides.rotating .sides-list{display:grid;grid-template-columns:minmax(0,1fr)}',
   '.sides.rotating .sides-list{display:grid;grid-template-columns:minmax(0,1fr)}\n.hero-sub .sides-list{max-width:56ch}'),

  ('<title>Ling-Hsuan Wang</title>', '<title>Ling-Hsuan Wang</title>\n' + NOINDEX),
  ('<meta property="og:image" content="https://lingdesign.github.io/assets/og.jpg">',
   '<meta property="og:image" content="https://lingdesign.github.io/work/assets/og.jpg">'),
  ('<meta property="og:image:alt" content="“Designing for every side of care.” Ling-Hsuan Wang, senior product designer in healthcare, beside three screens from the Fay Goals redesign.">',
   '<meta property="og:image:alt" content="“Designing products people trust, from onboarding to daily habit.” Ling-Hsuan Wang, senior product designer, beside three screens from the Fay Goals redesign.">'),
]

# case studies: same pages as the main site, without the healthcare label
CASE_EDITS = [
  ('<span class="role-long">Senior product designer in healthcare, based in New York</span>',
   '<span class="role-long">Senior product designer, based in New York</span>'),
  ('Sr. product designer<span class="hc"> in healthcare</span>', 'Sr. product designer'),
  ('I’m looking for my next Staff or Senior role on a team building care people can rely on. Always happy to talk about healthcare products, design, and creative practice.',
   'I’m looking for my next Staff or Senior role on a team building products people rely on. Always happy to talk about product, design, and creative practice.'),
]

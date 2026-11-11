# lingdesign.github.io/work

The portfolio for product teams outside healthcare, plus one landing page per company.
Not linked from lingdesign.github.io, and every page asks search engines not to list it.

## What's where

| | |
|---|---|
| `pages/<name>.txt` | One company's wording. This is the file you edit. |
| `wording.py` | How /work differs from the main site (headline, bio, project lines, case-study header). |
| `build.py` | Builds everything into `docs/` from the main site. |
| `check.py` | Loads every page on a phone and a desktop and fails on any problem. |
| `ogimage.py`, `og/` | Draws each page's link-preview image. |
| `docs/` | What GitHub Pages serves. Never edit by hand: the next build replaces it. |

The case studies and images come from the main site at build time, so a fix there reaches /work and
every company page on the next build.

## A company page

```
headline: Designing tools people trust,
headline2: from prototype to production.
hello: Hi, I'm Ling. …            (the bio's first paragraph)
order: provider, goals, monument  (which project comes first)
goals: …                          (optional: a different one-liner for a project)
lines:
- One rotating line under the headline.
- Another.
```

Lines starting with `#` are notes and never appear on the page. Keep the company's name out of the
wording: the address names them, the page doesn't (the check fails if it does).

## Updating

```
python3 build.py ../lingdesign.github.io
python3 check.py screenshots/
```

Review the phone screenshots, then commit and push. The build stops, and says why, if any edit no
longer finds its text on the main site.

## What could break

- Rewording a headline, bio or project line on the main site: `wording.py` stops the build until its
  matching line is updated.
- Restructuring the main site's landing page (headline, rotating lines, bio or project markup): the
  company pages stop building until `build.py` matches the new markup.
- Changing the main site's fonts or headline size: company headlines may run long, which the check
  catches (no more than 4 lines on a phone).

## Pages sent

| Address | Role | Sent | Status |
|---|---|---|---|
| /work/anthropic | Product Designer, Safeguards | | |
| /work/duolingo | Senior Product Designer | | |
| /work/meta | Product Designer, Human Interface | | |
| /work/google | Staff UX Designer, Google Cloud | | |

When a role closes for good, keep its page a few months (recruiters reopen links), then delete its
`pages/` file and add a redirect to /work.

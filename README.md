# cairnco.cloud

The website for **CAIRNCO HOLDINGS LLP** (UEN T26LL0983A), a Singapore tech
consultancy trading as CairnCo.

Hand-written static HTML and CSS. No framework, no runtime dependencies. A
single Python script assembles the English and Simplified Chinese static pages
from templates, injects SEO/AEO metadata, and inlines the artwork.

The hero terrain is drawn live on a canvas with marching squares over a scalar
field; the contour backgrounds are generated from a sum of gaussians rather
than hand-drawn.

## The buttons

Everything you do to this site is a double-click in **`Lazy Commands\`**:

| Button | What it does |
|---|---|
| `BUILD-AND-DEPLOY.bat` | build `src\` into pages, then publish (asks first) |
| `PREVIEW.bat` | look at the built site on this computer |
| `SAVE-TO-GITHUB.bat` | send your work **up** to GitHub |
| `PULL-LATEST.bat` | bring Emmanuel's work **down** |

`Lazy Commands\README - what each button does.md` explains each one.

**Previewing it:** run `Lazy Commands\PREVIEW.bat`, then open
http://localhost:8000.

Double-clicking a built page does **not** work. Every link starts with `/`, and
a browser reading off the disk resolves that to the top of your C: drive rather
than the top of the site, so every link dies. `HOW-TO-PREVIEW.md` has the full
explanation, plus the browser width some effects need.

## Structure

```
index.html            the English home page
contact/  faq/        crawlable English pages
landmarks/ kit/ newsroom/   holding pages, noindex until written
zh/                   crawlable Simplified Chinese pages
en/                   noindex redirects to the English pages at the root
contact.html  kit.html  landmarks.html  newsroom.html
                      noindex redirects, for older links
sitemap.xml           language-aware sitemap with hreflang alternates
dist/                 what actually gets deployed; gitignored, rebuilt each time
Lazy Commands/        the double-click buttons
HOW-TO-PREVIEW.md     how to preview, edit, rebuild and deploy
src/
  index.template.html   edit this for the home page, then run build.py
  contact.template.html edit this for the contact page
  faq.template.html     edit this for the FAQ page
  sub.template.html     edit this for ALL THREE holding pages at once
  nav.js                the header script, shared by every page
  build.py              builds every page in both languages
  contours.py           regenerates the section background contours
  pins_anim.py          regenerates the landmark pin drop, writes into the
                        home template between ==PINS== markers
  pins.anim.css         that generator's output, kept for reference
  rocks.py              regenerates rock silhouettes (not used on the site now)
  topo-dense.svg        generated contour field, hero and upper page
  topo-open.svg         generated contour field, lower page
  rocks.json            generated rock geometry
  archive/              superseded art, kept for reference only
```

## One source of truth

Everything shared lives in exactly one place and `build.py` injects it:

| What | Where it lives | Injected as |
|---|---|---|
| Tokens, reset, buttons, header styling | `index.template.html`, `==SHELL-A==` | `__SHELL_CSS__` |
| Footer styling | `index.template.html`, `==SHELL-B==` | `__SHELL_CSS__` |
| Header markup | `index.template.html`, `==NAV==` | `__NAV_HTML__` |
| Footer markup | `index.template.html`, `==FOOT==` | `__FOOT_HTML__` |
| Header hide-on-scroll script | `src/nav.js` | `__NAV_JS__` |

So a colour, a nav link, a footer line or the wordmark is a single edit and all
five pages pick it up on the next build.

The published URLs are directory-style paths: `/`, `/faq/`, `/contact/`,
`/zh/`, `/zh/contact/`. **English lives at the root**, not under `/en/`; the
`/en/` tree is a set of redirects kept for older links, and the root is the
`x-default`. The FAQ is English-only for now, so it has no `/zh/` twin and is
deliberately absent from the Chinese hreflang set.

**Do not delete or rename those marker comments.** `build.py` stops with an
error if a region or a placeholder is missing, rather than shipping a broken
page.

Two things are generated and must not be hand-edited:

- **The pin animation CSS** is written *into* `index.template.html` between the
  `==PINS:START==` and `==PINS:END==` markers by `src/pins_anim.py`. Editing
  that block by hand is overwritten on the next run. Change the constants at the
  top of the generator instead.
- **The FAQ questions** exist twice: as visible text in `faq.template.html`, and
  in the `FAQ` list in `build.py` that the structured data is built from.
  `build.py` compares them and refuses to build if they disagree, naming the
  question that drifted.

## Adding another holding page

One line in `HOLDING_PAGES` near the top of `build.py`:

```python
('pricing.html', 'pricing', 'Pricing'),
```

Filename, URL slug, and the English heading shown above the lock. Then add its
localized metadata to `PAGE_META`, and add it to the `==NAV==` and `==FOOT==`
regions so it is reachable.

## Social icons

`src/icons/` holds one file per platform, named `linkedin`, `github`,
`instagram`, `tiktok`. An `.svg` is inlined; a `.png` is embedded as an alpha
mask, which is what lets the mark take the site's teal and flip to cream on the
terracotta hover. Anything missing falls back to a mono initial and `build.py`
prints which ones are still placeholders.

One gotcha: the PNGs are embedded as base64, so if a file is ever re-saved by
another tool the built `contact.html` changes bytes even when the image looks
identical. Compare the decoded image, not the md5, before assuming something
broke.

## Connected

The contact form posts to Formspree and is live. The endpoint is the `action`
on the form in `src/contact.template.html`. Instagram and TikTok are linked on
both contact pages.

A Formspree endpoint in a static page is public by design, so anyone who reads
the source can post to it. The hidden `_gotcha` honeypot stops crude bots;
turn on reCAPTCHA in the Formspree dashboard before relying on it.

## Not connected yet

On the contact page: the booking link (`#bookLink`), the Open discovery button
(`#discoveryLink`), and the LinkedIn and GitHub icons, which have no accounts
behind them yet. Each is marked with an HTML comment in
`src/contact.template.html` saying what to change. See `HOW-TO-PREVIEW.md`.

On the home page: the four sector cards (Retail, Education, Professional,
Trades) are `href="#"` and go nowhere.

Three pages are still `noindex` holding pages with roughly 400 words each:
Landmarks, The Kit and Newsroom. That is the biggest structural limit on the
site's search visibility.

## Licence

No licence granted. All rights reserved, CAIRNCO HOLDINGS LLP.

## Housekeeping

The `.bat` files moved into `Lazy Commands/` on 22 Sep 2026. Each one finds the
site by its own location, so they work from in there and nowhere else. Do not
move one out on its own.

`Lazy Commands/DELETE-OLD-FILES.bat` has done its job; run it once more and it
removes itself.

`MERGE-EMMANUEL-AND-SAVE.bat` was written for one specific day and should be
deleted once it has been run.

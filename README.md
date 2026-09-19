# cairnco.cloud

The website for **CAIRNCO HOLDINGS LLP** (UEN T26LL0983A), a Singapore tech
consultancy trading as CairnCo.

Hand-written static HTML and CSS. No framework, no runtime dependencies. A
single Python script assembles the English and Simplified Chinese static pages
from templates, injects SEO/AEO metadata, and inlines the artwork.

The hero terrain is drawn live on a canvas with marching squares over a scalar
field; the contour backgrounds are generated from a sum of gaussians rather
than hand-drawn.

**Previewing it:** open `index.html`. See `HOW-TO-PREVIEW.md` for the details,
including the browser width some effects need.

## Structure

```
index.html            language chooser; redirects by browser language
contact.html          noindex redirect to /en/contact/
landmarks.html        noindex redirect to /en/landmarks/
kit.html              noindex redirect to /en/kit/
newsroom.html         noindex redirect to /en/newsroom/
en/                   crawlable English pages
zh/                   crawlable Simplified Chinese pages
sitemap.xml           language-aware sitemap with hreflang alternates
HOW-TO-PREVIEW.md     how to preview, edit, rebuild and deploy
src/
  index.template.html   edit this for the home page, then run build.py
  contact.template.html edit this for the contact page
  sub.template.html     edit this for ALL THREE holding pages at once
  nav.js                the header's hide-on-scroll script, shared by every page
  build.py              builds all five pages
  contours.py           regenerates the section background contours
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

The published language URLs are directory-style paths such as `/en/`,
`/zh/`, `/en/contact/` and `/zh/contact/`. The root `index.html` is the
`x-default` language chooser.

**Do not delete or rename those marker comments.** `build.py` stops with an
error if a region or a placeholder is missing, rather than shipping a broken
page.

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
on the form in `src/contact.template.html`.

A Formspree endpoint in a static page is public by design, so anyone who reads
the source can post to it. The hidden `_gotcha` honeypot stops crude bots;
turn on reCAPTCHA in the Formspree dashboard before relying on it.

## Not connected yet

On `contact.html`: the booking link (`#bookLink`), the Open discovery button
(`#discoveryLink`), and the four Follow us links. Each is marked with an HTML
comment in `src/contact.template.html` saying what to change. See
`HOW-TO-PREVIEW.md`.

## Licence

No licence granted. All rights reserved, CAIRNCO HOLDINGS LLP.

## Housekeeping

The stale duplicates that used to sit at the folder root are gone.
`DELETE-OLD-FILES.bat` has done its job; run it once more and it removes itself.

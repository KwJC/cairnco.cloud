# Previewing the site locally

## The short version

Open **`index.html`** at the top of this folder. It is the lightweight language
chooser and redirects to `/en/` or `/zh/` from browser language settings when
served over HTTP.

For direct file preview, open the generated language pages instead:

- `en/index.html`
- `zh/index.html`
- `en/contact/index.html`
- `zh/contact/index.html`

In VS Code: right-click `index.html` in the file tree, then **Open with Live
Server**. For browser-language switching and directory URLs, use Live Server or
Wrangler preview rather than double-clicking from `file://`.

## The two things that will make effects look broken

**1. Never preview anything in `src/`.**
Those are source files. They still contain the placeholders `__TOPO_OPEN__`,
`__SHELL_CSS__`, `__NAV_HTML__`, `__FOOT_HTML__` and `__NAV_JS__` where the
artwork, the shared stylesheet, the header and the footer get injected. Opened
directly they render with no styling, no header and no footer. This is the most likely reason an effect "isn't working". Only
the generated root files and language folders are real pages.

**2. Make the browser window at least 900px wide.**

Some effects are width-gated on purpose, and fall back to a plain readable list
below the gate:

| Effect | Needs |
|---|---|
| Hero contour field | any width |
| The review wheel in The Issue | 820px or wider |
| Our path to building | 900px or wider |
| Who we build for, two-column grid | 900px or wider |

A browser window docked beside the VS Code editor is often 700 to 850px wide,
which is exactly the band where those sections drop to their static fallback.
Widen the window before assuming the code is broken.

## What each effect needs to be triggered

- **Hero field** draws immediately. Move the mouse across the hero; the summit
  follows it and the contour lines bend around it
- **The review wheel** is scroll-driven for **one pass only**. Scroll down
  through The Issue and the cards turn as you go. Once you reach the end of that
  section the scroll driver switches off for good and two chevrons appear at the
  right of the card stack. From then on the wheel is button-driven, and it wraps
  at both ends. **Refresh the page to get the scroll pass back.** This is
  deliberate: it stops the page recomputing the stack on every later scroll
- **Who we build for** rises in four layers as you scroll into it: heading, then
  each row of cards, then the "Not on this list?" card. Each layer fires once
  and stays. Scrolling back up and down again does nothing
- **Our path to building** draws the path and lights each step as you scroll
  down. It only ever moves forward. Scrolling back up leaves it in its final
  form, and once the path is fully drawn the listener switches off
- **Nothing animates** if your OS has "reduce motion" enabled. That is
  deliberate. Turn it off to see the effects

## The contact page, and what is not wired yet

Three things on `contact.html` are built but deliberately not connected. Each is
marked with an HTML comment in `src/contact.template.html` saying exactly what
to change.

| Thing | To connect it |
|---|---|
| **Open the calendar** | Set the `href` on `#bookLink` to your booking page |
| **Send us a message** | Put `action="https://formspree.io/f/XXXXXXXX" method="post"` on the form, then delete the submit handler at the bottom of the page. The field names already match what Formspree expects |
| **Open discovery** | Set the `href` on `#discoveryLink` to the blueprint builder |

The four **Follow us** links also point at `#` until the account URLs are in.

Until the form has an `action`, submitting it validates the fields and then says
"Not connected yet" rather than silently doing nothing. The moment an `action`
is set, the handler stands aside and the browser posts normally.

The **What do you need** dropdown is a custom listbox, because a native
`<select>`'s open panel is drawn by the operating system and cannot be styled to
match the site. The real `<select>` is still in the form and still carries the
value, so submission is identical with the script on or off, and it works with a
keyboard: arrows to move, Enter to pick, Escape to close. To change the options,
edit the `<option>` list in `src/contact.template.html`. The listbox is built
from it.

Form field names, for whatever handler you wire up: `name`, `email`, `phone`,
`need`, `company`, `message`.

## The header on narrow screens

Below 700px the nav links wrap under the wordmark and the header grows to about
150px, then 200px below 500px. At that size it stops being fixed and simply sits
at the top of the document, so it never covers the first heading and never eats
a quarter of a phone screen. This is why the header does not hide on scroll on a
phone.

## Editing

Edit the files in **`src/`**, never the built pages at the root or in `en/` and
`zh/`.

- Home page: `src/index.template.html`
- Contact page: `src/contact.template.html`
- All three holding pages: `src/sub.template.html` (one file, three pages)
- Header and footer **markup**: the `==NAV==` and `==FOOT==` regions inside
  `src/index.template.html`. Every page uses that one copy
- Colours, fonts, buttons, the footer's styling: the `==SHELL-A==` and
  `==SHELL-B==` regions inside `src/index.template.html`
- The header's hide-on-scroll script: `src/nav.js`

Then:

```
cd src
python build.py
```

It prints the language trees, redirect pages and their sizes. Live Server picks
them up on save. If a placeholder was left unfilled it stops with an error
instead of writing a broken page.

If you edit a built page directly, your next build silently overwrites it.

## Regenerating the artwork

```
cd src
python contours.py   # the section background contours
python build.py      # inject them into the pages
```

`contours.py` needs `numpy` and `matplotlib`. The hero field needs neither: it
is drawn live in the browser with canvas.

## Deploying to Cloudflare Workers

The site runs on Cloudflare Workers with Static Assets, deployed with Wrangler.
`wrangler.jsonc` at the root holds the whole configuration.

**One-time setup, in this folder:**

```
npm install -D wrangler
```

Then create a file called `.env` next to `wrangler.jsonc` containing one line:

```
CLOUDFLARE_API_TOKEN=your-token-here
```

The token is created in the Cloudflare dashboard with the **Edit Cloudflare
Workers** preset. `.env` is in `.gitignore` and must never be committed.

**Every deploy:**

```
python src/build.py
npx wrangler deploy
```

`build.py` writes the root chooser, legacy redirect pages and the `/en/` and
`/zh/` language trees to the repo root, then mirrors them into `dist/`.
Wrangler publishes **only `dist/`**, which is what keeps `src/`, `build.py` and
these docs off the public site. `dist/` is gitignored, so always run the build
before deploying.

To check the configuration without publishing:

```
npx wrangler deploy --dry-run
```

The custom domain `cairnco.cloud` is declared in `wrangler.jsonc` as a Custom
Domain, so Cloudflare creates the DNS record and the certificate itself. Do not
add a `www` record unless you decide you want one; it is deliberately not there.

### The old route: Cloudflare Pages

Pages is the alternative if Workers is ever a problem. It needs no build
command and a build output directory of `/`.


Cloudflare Pages, Upload assets. Drop in the generated root files plus the
`en/` and `zh/` folders. No build command, no output directory. `src/` does not
need to be uploaded.

Missing a page out is the easy mistake here: the header links to all of them, so
an unuploaded page is a dead link in the nav.

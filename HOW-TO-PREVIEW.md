# Previewing the site locally

## The short version

Run **`Lazy Commands\PREVIEW.bat`**, then open **http://localhost:8000**.

Run `Lazy Commands\BUILD-AND-DEPLOY.bat` first if you have edited anything in
`src\`. Answer **N** when it asks to publish. That builds without touching the
live site.

## Why double-clicking a page does not work

Every link and asset in the built pages starts with a slash: `/faq/`,
`/contact/`, `/favicon.ico`. That slash means "the top of the site", which is
correct for a website.

Open a page by double-clicking it and there is no site. The browser is reading
off your disk, so it treats the slash as the top of your **C: drive**:

| Link | Written as | Where a double-click sends it |
|---|---|---|
| Landmarks | `/landmarks/` | `file:///landmarks/` |
| FAQ | `/faq/` | `file:///faq/` |
| The logo | `/` | `file:///` (your C: drive) |

The home page paints fine, then every link is dead and the favicon is missing.

Serving the folder over http makes the slash mean the `dist` folder again, which
is exactly what Cloudflare does.

**Preview `dist\`, not the repo root.** `dist\` is what actually gets deployed.

### Doing it by hand, without the button

```
cd dist
python -m http.server 8000
```

Then http://localhost:8000. `Ctrl+C` in that window stops it.

VS Code's Live Server extension also works, pointed at `dist`.

## The three things that make effects look broken

**1. Never preview anything in `src\`.**
Those are source files. They still contain the placeholders `__TOPO_OPEN__`,
`__SHELL_CSS__`, `__NAV_HTML__`, `__FOOT_HTML__` and `__NAV_JS__` where the
artwork, the shared stylesheet, the header and the footer get injected. Opened
directly they render with no styling, no header and no footer. This is the most
likely reason an effect "isn't working".

**2. The first page takes about 6 seconds.**
That is the arrival sequence, not a hang. Typing, then the wordmark walks into
the header, then the landmark pins drop and topple. Click to another page and
back and you get the shorter 4 second version instead. A fresh browser session
resets it to the long one.

**3. Make the browser window at least 900px wide.**

Some effects are width-gated on purpose and fall back to a plain readable list
below the gate:

| Effect | Needs |
|---|---|
| Hero contour field | any width |
| The review wheel in The Issue | 820px or wider |
| Our path to building | 900px or wider |
| Who we build for, two-column grid | 900px or wider |

A browser docked beside the VS Code editor is often 700 to 850px wide, which is
exactly the band where those drop to their static fallback.

## What each effect needs to be triggered

- **Hero field** draws immediately. Move the mouse across the hero; the summit
  follows it and the contour lines bend around it
- **The review wheel** is scroll-driven for **one pass only**. Scroll down
  through The Issue and the cards turn as you go. At the end of that section the
  scroll driver switches off for good and two chevrons appear at the right of
  the card stack. From then on it is button-driven and wraps at both ends.
  **Refresh to get the scroll pass back.** This is deliberate: it stops the page
  recomputing the stack on every later scroll
- **Who we build for** rises in four layers as you scroll into it: heading, then
  each row of cards, then the "Not on this list?" card. Each layer fires once
  and stays
- **Our path to building** draws the path and lights each step as you scroll
  down. It only ever moves forward, and the listener switches off once drawn
- **The FAQ accordion** opens at most two answers at once. Opening a third
  closes whichever was opened first. Every page starts with all of them closed
- **Nothing animates** if your OS has "reduce motion" enabled, including the
  arrival sequence. That is deliberate. Turn it off to see the effects

## On a phone

Resize the browser below 700px, or use the device toolbar in Chrome's dev tools.

The nav links collapse into a dropdown panel behind the hamburger. It dims the
page behind it, closes on a tap outside, on a link, on Escape, and when the
window grows back past 700px. The header stops hiding itself while the panel is
open. Every link in it is at least 48px tall.

Same-page `#` links ease into place rather than jumping, and stop below the
fixed header instead of underneath it.

## The contact page: what is and is not wired

| Thing | State |
|---|---|
| **Send us a message** | **Live.** Posts to Formspree |
| **Instagram, TikTok** | **Live.** Linked to the CairnCo accounts |
| **LinkedIn, GitHub** | Not connected. No accounts exist yet, both are `#` |
| **Open the calendar** (`#bookLink`) | Not connected. Set its `href` to the booking page |
| **Open discovery** (`#discoveryLink`) | Not connected. Set its `href` to the blueprint builder |

Each unconnected one is marked with an HTML comment in
`src\contact.template.html` saying exactly what to change.

A Formspree endpoint in a static page is public by design, so anyone reading the
source can post to it. The hidden `_gotcha` honeypot stops crude bots; turn on
reCAPTCHA in the Formspree dashboard before relying on it.

The **What do you need** dropdown is a custom listbox, because a native
`<select>`'s open panel is drawn by the operating system and cannot be styled to
match the site. The real `<select>` is still in the form and still carries the
value, so submission is identical with the script on or off, and it works with a
keyboard: arrows to move, Enter to pick, Escape to close. To change the options,
edit the `<option>` list in `src\contact.template.html`. The listbox is built
from it.

Form field names: `name`, `email`, `phone`, `need`, `company`, `message`.

## Editing

Edit the files in **`src\`**, never the built pages at the root or in `en\`,
`zh\`, `faq\` or `contact\`. If you edit a built page directly, your next build
silently overwrites it.

- Home page: `src\index.template.html`
- Contact page: `src\contact.template.html`
- FAQ page: `src\faq.template.html`
- All three holding pages: `src\sub.template.html` (one file, three pages)
- Header and footer **markup**: the `==NAV==` and `==FOOT==` regions inside
  `src\index.template.html`. Every page uses that one copy
- Colours, fonts, buttons, footer styling: the `==SHELL-A==` and `==SHELL-B==`
  regions inside `src\index.template.html`
- The header script: `src\nav.js`
- The arrival sequence timings: the `var T = full ? {...}` table in
  `src\index.template.html`

Then run `Lazy Commands\BUILD-AND-DEPLOY.bat`, or by hand:

```
python src\build.py
```

It stops with an error rather than writing a broken page if a placeholder was
left unfilled.

### Two generated regions you must not hand-edit

**The pin animation.** `src\pins_anim.py` writes its CSS *into*
`src\index.template.html`, between the `==PINS:START==` and `==PINS:END==`
markers. Editing that block by hand is pointless; it is overwritten on the next
run. Change the constants at the top of `pins_anim.py` and re-run it instead.

**The FAQ questions.** They are written twice: as visible text in
`src\faq.template.html`, and in the `FAQ` list in `src\build.py` that the search
engine data is generated from. `build.py` compares the two and **refuses to
build** if they disagree, naming the question that drifted. Change both.

**Do not delete or rename any `==MARKER==` comment.** `build.py` stops with an
error if a region or placeholder is missing.

## Regenerating the artwork

```
cd src
python contours.py   # the section background contours
python pins_anim.py  # the landmark pin drop and topple
python build.py      # inject them into the pages
```

`contours.py` needs `numpy` and `matplotlib`. `pins_anim.py` and `build.py` need
neither: both are pure standard library. The hero field needs nothing at all, it
is drawn live in the browser on a canvas.

## Deploying to Cloudflare

Use `Lazy Commands\BUILD-AND-DEPLOY.bat`. It builds, checks, and asks before
publishing.

By hand:

```
python src\build.py
npx wrangler deploy
```

The site runs on Cloudflare Workers with Static Assets. `wrangler.jsonc` at the
root holds the whole configuration, and declares `cairnco.cloud` as a Custom
Domain, so Cloudflare creates the DNS record and certificate itself. There is
deliberately no `www` record.

Wrangler publishes **only `dist\`**, which is what keeps `src\`, `build.py` and
these docs off the public site. `dist\` is gitignored, so always build before
deploying.

To check the configuration without publishing:

```
npx wrangler deploy --dry-run
```

**One-time setup:** `npm install -D wrangler`, then a `.env` file next to
`wrangler.jsonc` holding one line, `CLOUDFLARE_API_TOKEN=your-token-here`. The
token comes from the Cloudflare dashboard with the **Edit Cloudflare Workers**
preset. `.env` is gitignored and must never be committed.

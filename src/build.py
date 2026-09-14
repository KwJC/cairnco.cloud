"""Builds every page from its template. Edit the templates in src/, never the
built .html files at the root.

  src/index.template.html    ->  index.html
  src/contact.template.html  ->  contact.html
  src/sub.template.html      ->  landmarks.html, kit.html, newsroom.html

Anything shared lives in exactly ONE place and is injected at build time:

  the stylesheet shell   index.template.html, between the ==SHELL-A== and
                         ==SHELL-B== markers (tokens, reset, header, buttons,
                         footer)
  the head (charset, viewport, fonts)   index.template.html, ==HEAD== markers
  the header markup      index.template.html, between the ==NAV== markers
  the footer markup      index.template.html, between the ==FOOT== markers
  the header script      src/nav.js

So a colour, a nav link or a footer line is a single edit and every page picks
it up on the next build.

Run it from anywhere:  python build.py
"""
import base64
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE
ROOT = HERE.parent if HERE.name == 'src' else HERE
if SRC == ROOT and (ROOT / 'src').is_dir():
    SRC = ROOT / 'src'

ASSET_DIRS = [SRC, ROOT / 'assets', ROOT]

# Brand marks are supplied, never drawn here. Put each platform's own file into
# src/icons/ as <slug>.svg or <slug>.png. An SVG is inlined; a PNG is embedded as
# an alpha mask so the mark takes the site's colour and flips to cream on hover.
# Anything missing falls back to a mono initial so the row keeps its size.
SOCIAL_ICONS = [
    ('linkedin', 'in'),
    ('github', 'gh'),
    ('instagram', 'ig'),
    ('tiktok', 'tt'),
]

HOLDING_PAGES = [
    ('landmarks.html', 'Landmarks | CairnCo', 'Landmarks'),
    ('kit.html', 'The Kit | CairnCo', 'The Kit'),
    ('newsroom.html', 'Newsroom | CairnCo', 'Newsroom'),
]


def read(name):
    return (SRC / name).read_text(encoding='utf-8')


def asset(name):
    for d in ASSET_DIRS:
        f = d / name
        if f.is_file():
            return f.read_text(encoding='utf-8').strip()
    sys.exit('missing asset: %s (looked in %s)' % (name, ', '.join(str(d) for d in ASSET_DIRS)))


def region(text, tag, comment=False):
    o, c = ('<!--==', '==-->') if comment else ('/*==', '==*/')
    pat = re.escape(o + tag + ':START' + c) + '(.*?)' + re.escape(o + tag + ':END' + c)
    m = re.search(pat, text, re.S)
    if not m:
        sys.exit('missing %s region in index.template.html' % tag)
    return m.group(1).strip()


def finish(path, text):
    left = re.findall(r'__[A-Z_]+__', text)
    if left:
        sys.exit('unfilled placeholder(s) in %s: %s' % (path.name, ', '.join(sorted(set(left)))))
    path.write_text(text, encoding='utf-8')
    print('  %-16s %6d bytes' % (path.name, len(text)))


home = read('index.template.html')

SHARED = {
    '__SHELL_CSS__': region(home, 'SHELL-A') + '\n\n' + region(home, 'SHELL-B'),
    '__HEAD__': region(home, 'HEAD', comment=True),
    '__NAV_HTML__': region(home, 'NAV', comment=True),
    '__FOOT_HTML__': region(home, 'FOOT', comment=True),
    '__NAV_JS__': read('nav.js').strip(),
    '__TOPO_OPEN__': asset('topo-open.svg'),
    '__TOPO_DENSE__': asset('topo-dense.svg'),
}

_found = []
for _slug, _ph in SOCIAL_ICONS:
    _svg = SRC / 'icons' / (_slug + '.svg')
    _png = SRC / 'icons' / (_slug + '.png')
    if _svg.is_file():
        _mark = _svg.read_text(encoding='utf-8').strip()
        _found.append(_slug)
    elif _png.is_file():
        _b64 = base64.b64encode(_png.read_bytes()).decode('ascii')
        _mark = ('<span class="ico__m" style="--m:url(data:image/png;base64,%s)"></span>'
                 % _b64)
        _found.append(_slug)
    else:
        _mark = '<span class="ico__ph">%s</span>' % _ph
    SHARED['__ICON_%s__' % _slug.upper()] = _mark


def fill(text, extra=None):
    for k, v in SHARED.items():
        text = text.replace(k, v)
    for k, v in (extra or {}).items():
        text = text.replace(k, v)
    return text


print('building cairnco.cloud')
_missing = [s for s, _ in SOCIAL_ICONS if s not in _found]
if _missing:
    print('  social icons still placeholders: %s' % ', '.join(_missing))
    print('  drop the official SVGs into src/icons/ and rebuild')
finish(ROOT / 'index.html', fill(home))
finish(ROOT / 'contact.html', fill(read('contact.template.html')))

sub = read('sub.template.html')
for filename, title, name in HOLDING_PAGES:
    finish(ROOT / filename,
           fill(sub, {'__PAGE_TITLE__': title, '__PAGE_NAME__': name}))

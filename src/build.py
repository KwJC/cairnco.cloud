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


# ---------------------------------------------------------------- SEO / AEO
# One place for everything a search engine or an answer engine reads. Every
# fact here is verifiable: the UEN is the registered one, the address is the
# country only because the registered street address is not settled yet, and
# there is no founding claim beyond the ACRA registration date.
SITE = 'https://cairnco.cloud'

LEGAL_NAME = 'CAIRNCO HOLDINGS LLP'
UEN = 'T26LL0983A'
EMAIL = 'hello@cairnco.cloud'
FOUNDED = '2026-09-10'          # ACRA registration
SAME_AS = [
    'https://www.tiktok.com/@cairnco_holdings',
    'https://www.instagram.com/cairnco.holdings',
    # LinkedIn and GitHub go here when the accounts exist
]
SERVICES = ['Websites', 'SEO & AEO', 'Marketing', 'Internal Tools',
            'AI Workflows', 'Automation', 'Cloud']

# noindex is deliberate on the three holding pages. Three near-identical
# 23-word pages in the index is a quality signal problem, not a win. Remove
# the flag the moment a page has real content, and it joins the sitemap.
PAGE_META = {
    'index.html': dict(
        path='/',
        title='Websites, Automation & AI for Singapore Businesses | CairnCo',
        desc=('CairnCo builds and runs the tech behind Singapore small businesses: '
              'websites, internal tools, AI workflows, automation and cloud. '
              'Built, launched, kept running.'),
        index=True, priority='1.0'),
    'contact.html': dict(
        path='/contact.html',
        title='Contact CairnCo | Tell us what is breaking',
        desc=('Tell CairnCo what is breaking and we will tell you whether we can fix it. '
              'Singapore-registered LLP. Replies within one working day.'),
        index=True, priority='0.8'),
    'landmarks.html': dict(
        path='/landmarks.html', title='Landmarks | CairnCo',
        desc='The work CairnCo has built. This page is being written.',
        index=False, priority='0.3'),
    'kit.html': dict(
        path='/kit.html', title='The Kit | CairnCo',
        desc='Reusable pieces CairnCo builds with. This page is being written.',
        index=False, priority='0.3'),
    'newsroom.html': dict(
        path='/newsroom.html', title='Newsroom | CairnCo',
        desc='News from CairnCo. This page is being written.',
        index=False, priority='0.3'),
}


def _esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def jsonld_home():
    import json
    org = {
        '@type': 'ProfessionalService',
        '@id': SITE + '/#org',
        'name': 'CairnCo',
        'legalName': LEGAL_NAME,
        'identifier': UEN,
        'url': SITE,
        'email': EMAIL,
        'foundingDate': FOUNDED,
        'description': PAGE_META['index.html']['desc'],
        'address': {'@type': 'PostalAddress', 'addressCountry': 'SG',
                    'addressLocality': 'Singapore'},
        'areaServed': {'@type': 'Country', 'name': 'Singapore'},
        'knowsAbout': SERVICES,
        'sameAs': SAME_AS,
        'hasOfferCatalog': {
            '@type': 'OfferCatalog', 'name': 'Services',
            'itemListElement': [
                {'@type': 'Offer', 'itemOffered':
                    {'@type': 'Service', 'name': s, 'provider': {'@id': SITE + '/#org'}}}
                for s in SERVICES]},
    }
    site = {'@type': 'WebSite', '@id': SITE + '/#site', 'url': SITE,
            'name': 'CairnCo', 'inLanguage': 'en',
            'publisher': {'@id': SITE + '/#org'}}
    doc = {'@context': 'https://schema.org', '@graph': [org, site]}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
            + '</script>')


def jsonld_crumb(name, path):
    import json
    doc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
           'itemListElement': [
               {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
               {'@type': 'ListItem', 'position': 2, 'name': name, 'item': SITE + path}]}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
            + '</script>')


def head_meta(filename):
    m = PAGE_META[filename]
    url = SITE + m['path']
    out = ['<title>%s</title>' % _esc(m['title']),
           '<meta name="description" content="%s">' % _esc(m['desc']),
           '<link rel="canonical" href="%s">' % url]
    if not m['index']:
        out.append('<meta name="robots" content="noindex,follow">')
    out += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="CairnCo">',
        '<meta property="og:locale" content="en_SG">',
        '<meta property="og:title" content="%s">' % _esc(m['title']),
        '<meta property="og:description" content="%s">' % _esc(m['desc']),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s/og-image.png">' % SITE,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="CairnCo. You run the business, we run the tech.">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % _esc(m['title']),
        '<meta name="twitter:description" content="%s">' % _esc(m['desc']),
        '<meta name="twitter:image" content="%s/og-image.png">' % SITE,
    ]
    if filename == 'index.html':
        out.append(jsonld_home())
    else:
        out.append(jsonld_crumb(m['title'].split(' | ')[0], m['path']))
    return '\n'.join(out)


def write_sitemap(root, dist):
    from datetime import date
    today = date.today().isoformat()
    rows = []
    for f, m in PAGE_META.items():
        if not m['index']:
            continue
        rows.append('  <url><loc>%s%s</loc><lastmod>%s</lastmod>'
                    '<changefreq>weekly</changefreq><priority>%s</priority></url>'
                    % (SITE, m['path'], today, m['priority']))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + '\n'.join(rows) + '\n</urlset>\n')
    for d in (root, dist):
        (d / 'sitemap.xml').write_text(xml, encoding='utf-8')
    return len(rows)


# ---- metadata stripping -------------------------------------------------
# Files that arrive here through the desktop bridge carry a C2PA content
# credentials manifest: a signed record that Claude produced them. It is
# roughly +7.7KB on every SVG and +5.8KB on every PNG, and because the icons
# and contours are inlined it lands in the HTML too.
#
# The SOURCE files keep theirs. Only the published copies are stripped, so the
# provenance record survives on disk and the bytes do not ship. This is the
# same pass any build does on EXIF and colour profiles.
_C2PA_SVG = re.compile(
    r'\s*xmlns:c2pa="[^"]*"|<metadata>\s*<c2pa:manifest>.*?</c2pa:manifest>\s*</metadata>',
    re.S)


def strip_svg(text):
    return _C2PA_SVG.sub('', text)


def clean_png(raw):
    """Return PNG bytes with only the chunks a browser needs."""
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        return raw
    keep = {b'IHDR', b'PLTE', b'IDAT', b'IEND', b'tRNS', b'gAMA', b'cHRM', b'sRGB'}
    out, i = [raw[:8]], 8
    while i < len(raw) - 8:
        ln = int.from_bytes(raw[i:i + 4], 'big')
        typ = raw[i + 4:i + 8]
        if typ in keep:
            out.append(raw[i:i + 12 + ln])
        i += 12 + ln
        if typ == b'IEND':
            break
    return b''.join(out)


def strip_png(src, dst):
    raw = src.read_bytes()
    dst.write_bytes(clean_png(raw))
    return 0


def strip_ico(src, dst):
    """ICO holds PNGs inside it; nothing we add is stripped, so copy as-is."""
    dst.write_bytes(src.read_bytes())
    return 0


def read(name):
    return (SRC / name).read_text(encoding='utf-8')


def asset(name):
    for d in ASSET_DIRS:
        f = d / name
        if f.is_file():
            text = f.read_text(encoding='utf-8').strip()
            return strip_svg(text) if name.endswith('.svg') else text
    sys.exit('missing asset: %s (looked in %s)' % (name, ', '.join(str(d) for d in ASSET_DIRS)))


def region(text, tag, comment=False):
    o, c = ('<!--==', '==-->') if comment else ('/*==', '==*/')
    pat = re.escape(o + tag + ':START' + c) + '(.*?)' + re.escape(o + tag + ':END' + c)
    m = re.search(pat, text, re.S)
    if not m:
        sys.exit('missing %s region in index.template.html' % tag)
    return m.group(1).strip()


# Wrangler serves this directory and nothing else, which is what keeps src/
# and the docs off the public site. The same pages are also written to the
# repo root so the site can still be opened straight off disk.
DIST = None


def finish(path, text):
    left = re.findall(r'__[A-Z_]+__', text)
    if left:
        sys.exit('unfilled placeholder(s) in %s: %s' % (path.name, ', '.join(sorted(set(left)))))
    path.write_text(text, encoding='utf-8')
    if DIST is not None:
        (DIST / path.name).write_text(text, encoding='utf-8')
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
        _mark = strip_svg(_svg.read_text(encoding='utf-8').strip())
        _found.append(_slug)
    elif _png.is_file():
        _b64 = base64.b64encode(clean_png(_png.read_bytes())).decode('ascii')
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


DIST = ROOT / 'dist'
DIST.mkdir(exist_ok=True)

print('building cairnco.cloud')
_missing = [s for s, _ in SOCIAL_ICONS if s not in _found]
if _missing:
    print('  social icons still placeholders: %s' % ', '.join(_missing))
    print('  drop the official SVGs into src/icons/ and rebuild')
finish(ROOT / 'index.html', fill(home, {'__META__': head_meta('index.html')}))
finish(ROOT / 'contact.html',
       fill(read('contact.template.html'), {'__META__': head_meta('contact.html')}))

sub = read('sub.template.html')
for filename, title, name in HOLDING_PAGES:
    finish(ROOT / filename,
           fill(sub, {'__PAGE_NAME__': name, '__META__': head_meta(filename)}))

# ---- robots.txt ----------------------------------------------------------
# No robots.txt at all already allows every crawler, so spelling that out
# changes nothing. The AI crawlers are named explicitly so the decision is
# visible: flip any Allow to Disallow to shut one out. Being readable by them
# is the point of AEO, so they are allowed.
ROBOTS = '''User-agent: *
Allow: /

# Answer engines. Named so the choice is explicit rather than accidental.
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Google-Extended
Allow: /

Sitemap: %s/sitemap.xml
''' % SITE
for _d in (ROOT, DIST):
    (_d / 'robots.txt').write_text(ROBOTS, encoding='utf-8')
_n = write_sitemap(ROOT, DIST)

# ---- static assets: favicon, share card ----------------------------------
_saved = 0
for _a in ('favicon.ico', 'favicon-32.png', 'og-image.png',
           'apple-touch-icon.png', 'icon-512.png'):
    _src = SRC / _a
    if not _src.is_file():
        print('  %-16s MISSING' % _a)
        continue
    _before = _src.stat().st_size
    for _d in (ROOT, DIST):
        if _a.endswith('.png'):
            strip_png(_src, _d / _a)
        elif _a.endswith('.ico'):
            strip_ico(_src, _d / _a)
        else:
            (_d / _a).write_text(strip_svg(_src.read_text(encoding='utf-8')), encoding='utf-8')
    _after = (DIST / _a).stat().st_size
    _saved += _before - _after
    print('  %-16s %6d bytes%s' % (_a, _after,
          '  (-%d stripped)' % (_before - _after) if _before != _after else ''))
if _saved:
    print('  %-16s %6d bytes of metadata removed from the published assets' % ('', _saved))
print('  %-16s %6d bytes' % ('robots.txt', len(ROBOTS)))
print('  %-16s %6d urls' % ('sitemap.xml', _n))

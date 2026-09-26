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
import shutil
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
    ('landmarks.html', 'landmarks', 'Landmarks'),
    ('kit.html', 'kit', 'The Kit'),
    ('newsroom.html', 'newsroom', 'Newsroom'),
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

LANGS = {
    'en': dict(
        label='English',
        html='en-SG',
        schema='en',
        locale='en_SG',
        prefix='',
        home='Home',
        root_title='Choose Language | CairnCo',
        root_desc='Choose English or Chinese for CairnCo.',
        og_alt='CairnCo. You run the business, we run the tech.',
        services=SERVICES),
    'zh': dict(
        label='中文',
        html='zh-Hans-SG',
        schema='zh-Hans',
        locale='zh_SG',
        prefix='/zh',
        home='首页',
        root_title='选择语言 | CairnCo',
        root_desc='选择英文或中文浏览 CairnCo。',
        og_alt='CairnCo。你专注经营，我们负责技术。',
        services=['网站建设', 'SEO 与 AEO', '营销', '内部工具',
                  'AI 工作流', '自动化', '云服务']),
}

# noindex is deliberate on Landmarks and Newsroom, which are still holding
# pages. Near-identical 30-word pages in the index are a quality signal problem,
# not a win. Remove the flag the moment a page has real content, and it joins
# the sitemap. The Kit came off it on 26 Sep: the English page is full, and the
# Chinese one is indexed with it at JC's decision while its copy is written.
# The FAQ page's questions, in the order they appear: the first five fill the
# left column, the last five the right. Answers are written so the opening
# sentence answers the question outright, because that is the part an answer
# engine lifts. Editing one here changes both the page and its FAQPage schema,
# so the two can never drift apart.
FAQ = [
    ('What happens on a discovery call?',
     'Thirty minutes, no obligation, and no pitch. You describe what is slow, '
     'breaking or done by hand, and we ask questions until we understand it. You '
     'leave with a written picture of what is actually wrong, whether or not you '
     'hire us. If it is not something we should build, we will say so.'),
    ('What does CairnCo actually do?',
     'We are the tech department for businesses that do not have one. That covers '
     'websites, internal tools, AI workflows, automation, cloud setup, and getting '
     'found in search and in AI assistants. One team for the whole stack, rather '
     'than a web agency, an IT guy and a marketing freelancer who never speak to '
     'each other.'),
    ('Does CairnCo charge a monthly fee, or is it one payment?',
     'Both, depending on what we build. A one-off site can be a single project fee. '
     'A system that keeps running, or search work that needs maintaining, is a build '
     'fee plus a monthly amount. We tell you which shape applies before you commit, '
     'and we do not take a percentage of your sales.'),
    ('Does CairnCo only build websites?',
     'No. Websites are the most visible part, but most of the work is the '
     'unglamorous kind: the spreadsheet that four people edit at once, the order '
     'form somebody retypes into another system, the report that takes a morning to '
     'assemble. If it is repetitive and done by hand, it is probably something we '
     'can automate.'),
    ('Who owns what CairnCo builds?',
     'Your content, your data and your customer information are yours and leave '
     'with you if we part ways. For custom work built for you, ownership is set in '
     'writing in the engagement, so nobody has to guess later. If you use one of our '
     'existing platforms, you hold a licence while you subscribe rather than owning '
     'the engine.'),
    ('What is AEO, and how is it different from SEO?',
     'SEO is being found on a search results page. AEO, answer engine optimisation, '
     'is being the source an AI assistant quotes when someone asks it a question. '
     'Increasingly people ask ChatGPT or Google\u2019s AI summary instead of scrolling '
     'results, and those answers cite a handful of sources. AEO is the work of being '
     'one of them.'),
    ('Can CairnCo take over a website or system somebody else built?',
     'Usually yes. We will look at what exists before quoting, because inheriting '
     'someone else\u2019s code is sometimes cheaper to rebuild than to repair, and you '
     'deserve to know which before you pay. We will tell you honestly which one it '
     'is, including when the honest answer is to leave it alone.'),
    ('What happens after the site or system launches?',
     'This is the part most people get burned on. A build that ships and is then '
     'left alone stops working within a year: search rankings drift, dependencies '
     'break, and the thing nobody owns becomes the thing nobody fixes. We stay on '
     'for the running, and the engagement says what that covers before you sign it.'),
    ('Where is CairnCo based, and does it work with businesses outside Singapore?',
     'We are based in Singapore and most of our work is with Singapore businesses, '
     'which matters for things like PayNow, PDPA and local search. We work remotely '
     'and can take on work elsewhere, but we will be straight about it when local '
     'knowledge is part of what you are buying.'),
    ('How quickly does CairnCo reply?',
     'Within one working day, to hello@cairnco.cloud or the form on the contact '
     'page. Both partners see it.'),
]

PAGE_META = {
    'index.html': dict(
        slug='',
        priority='1.0',
        index=True,
        en=dict(
            title='Websites, Automation & AI for Singapore Businesses | CairnCo',
            desc=('CairnCo builds and runs the tech behind Singapore small businesses: '
                  'websites, internal tools, AI workflows, automation and cloud. '
                  'Built, launched, kept running.')),
        zh=dict(
            title='新加坡企业网站、自动化与 AI 技术服务 | CairnCo',
            desc=('CairnCo 为新加坡中小企业建设并运营网站、内部工具、AI 工作流、'
                  '自动化和云服务。负责上线，也负责长期运行。'))),
    'faq.html': dict(
        slug='faq',
        priority='0.8',
        index=True,
        # English only for now. The Chinese answers are a separate job, and a
        # sitemap or hreflang entry for a page that does not exist is worse than
        # no entry at all, so the whole page is scoped to one language.
        langs=('en',),
        en=dict(
            title='FAQ | Working with CairnCo in Singapore',
            desc=('Answers about working with CairnCo: discovery calls, how we bill, '
                  'who owns what we build, AEO versus SEO, and what happens after '
                  'launch.'))),
    'contact.html': dict(
        slug='contact',
        priority='0.8',
        index=True,
        en=dict(
            title='Contact CairnCo | Tell us what is breaking',
            desc=('Tell CairnCo what is breaking and we will tell you whether we can fix it. '
                  'Singapore-registered LLP. Replies within one working day.')),
        zh=dict(
            title='联系 CairnCo | 告诉我们哪里卡住了',
            desc=('告诉 CairnCo 你的业务技术哪里出问题。我们会判断能否修复，以及需要什么。'
                  '新加坡注册 LLP，一个工作日内回复。'))),
    'landmarks.html': dict(
        slug='landmarks',
        priority='0.3',
        index=False,
        en=dict(title='Landmarks | CairnCo',
                desc='The work CairnCo has built. This page is being written.'),
        zh=dict(title='作品地标 | CairnCo',
                desc='CairnCo 已完成的作品。页面正在撰写中。')),
    'kit.html': dict(
        slug='kit',
        # a real page now, not a holding page: same weight as FAQ and contact
        priority='0.8',
        index=True,
        en=dict(title='The Kit | What CairnCo builds for Singapore businesses',
                # 141 characters. Google truncates a snippet around 155 to 160,
                # and a cut description reads as carelessness on a page whose
                # whole job is to look like a company that finishes things.
                desc='Websites, internal tools, AI workflows, automation, SEO and AEO, '
                     'marketing and cloud. The seven things CairnCo builds for '
                     'Singapore businesses.'),
        zh=dict(title='工具箱 | CairnCo 为新加坡企业提供的七项服务',
                desc='网站建设、内部工具、AI 工作流、自动化、SEO 与 AEO、营销、云服务。'
                     'CairnCo 为新加坡中小企业做的七件事，以及每一项里具体包含什么。')),
    'newsroom.html': dict(
        slug='newsroom',
        priority='0.3',
        index=False,
        en=dict(title='Newsroom | CairnCo',
                desc='News from CairnCo. This page is being written.'),
        zh=dict(title='新闻室 | CairnCo',
                desc='CairnCo 的最新消息。页面正在撰写中。')),
}


def _esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


def page_path(lang, filename):
    slug = PAGE_META[filename]['slug']
    base = LANGS[lang]['prefix']
    return base + ('/' + slug if slug else '') + '/'


def page_url(lang, filename):
    return SITE + page_path(lang, filename)


def page_out(lang, filename):
    # The default language is served from the site root, so it gets no folder
    # of its own. Any other language keeps its prefix as a folder.
    slug = PAGE_META[filename]['slug']
    base = LANGS[lang]['prefix'].strip('/')
    return pathlib.Path(base) / (slug or '') / 'index.html'


def localized_meta(filename, lang):
    m = PAGE_META[filename]
    d = m[lang].copy()
    d.update(slug=m['slug'], index=m['index'], priority=m['priority'])
    return d


def page_langs(filename):
    """Which languages a page exists in. Absent means all of them."""
    return PAGE_META[filename].get('langs', tuple(LANGS))

def alternates(filename):
    rows = []
    for lang in page_langs(filename):
        cfg = LANGS[lang]
        rows.append('<link rel="alternate" hreflang="%s" href="%s">'
                    % (cfg['html'], page_url(lang, filename)))
    rows.append('<link rel="alternate" hreflang="x-default" href="%s">' % x_default_url(filename))
    return rows


def x_default_url(filename):
    if filename == 'index.html':
        return SITE + '/'
    return page_url(page_langs(filename)[0], filename)


def jsonld_home(lang):
    import json
    cfg = LANGS[lang]
    m = localized_meta('index.html', lang)
    org = {
        '@type': 'ProfessionalService',
        '@id': SITE + '/#org',
        'name': 'CairnCo',
        'legalName': LEGAL_NAME,
        'identifier': UEN,
        'url': page_url(lang, 'index.html'),
        'email': EMAIL,
        'foundingDate': FOUNDED,
        'description': m['desc'],
        'address': {'@type': 'PostalAddress', 'addressCountry': 'SG',
                    'addressLocality': 'Singapore'},
        'areaServed': {'@type': 'Country', 'name': 'Singapore'},
        'knowsAbout': cfg['services'],
        'sameAs': SAME_AS,
        'hasOfferCatalog': {
            '@type': 'OfferCatalog', 'name': 'Services',
            'itemListElement': [
                {'@type': 'Offer', 'itemOffered':
                    {'@type': 'Service', 'name': s, 'provider': {'@id': SITE + '/#org'}}}
                for s in cfg['services']]},
    }
    site = {'@type': 'WebSite', '@id': SITE + '/#site-' + lang,
            'url': page_url(lang, 'index.html'),
            'name': 'CairnCo', 'inLanguage': cfg['schema'],
            'publisher': {'@id': SITE + '/#org'}}
    doc = {'@context': 'https://schema.org', '@graph': [org, site]}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
            + '</script>')


def jsonld_crumb(lang, name, path):
    import json
    home = LANGS[lang]['home']
    doc = {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
           'itemListElement': [
               {'@type': 'ListItem', 'position': 1, 'name': home,
                'item': page_url(lang, 'index.html')},
               {'@type': 'ListItem', 'position': 2, 'name': name,
                'item': SITE + path}]}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
            + '</script>')


def jsonld_faq():
    import json
    doc = {'@context': 'https://schema.org', '@type': 'FAQPage',
           'mainEntity': [
               {'@type': 'Question', 'name': q,
                'acceptedAnswer': {'@type': 'Answer', 'text': a}}
               for q, a in FAQ]}
    return ('<script type="application/ld+json">'
            + json.dumps(doc, ensure_ascii=False, separators=(',', ':'))
            + '</script>')


def head_meta(filename, lang):
    m = localized_meta(filename, lang)
    cfg = LANGS[lang]
    path = page_path(lang, filename)
    url = SITE + path
    out = ['<title>%s</title>' % _esc(m['title']),
           '<meta name="description" content="%s">' % _esc(m['desc']),
           '<link rel="canonical" href="%s">' % url]
    out += alternates(filename)
    if not m['index']:
        out.append('<meta name="robots" content="noindex,follow">')
    out += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="CairnCo">',
        '<meta property="og:locale" content="%s">' % cfg['locale'],
        '<meta property="og:title" content="%s">' % _esc(m['title']),
        '<meta property="og:description" content="%s">' % _esc(m['desc']),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s/og-image.png">' % SITE,
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="%s">' % _esc(cfg['og_alt']),
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % _esc(m['title']),
        '<meta name="twitter:description" content="%s">' % _esc(m['desc']),
        '<meta name="twitter:image" content="%s/og-image.png">' % SITE,
    ]
    if filename == 'index.html':
        out.append(jsonld_home(lang))
    else:
        out.append(jsonld_crumb(lang, m['title'].split(' | ')[0], path))
    if filename == 'faq.html':
        out.append(jsonld_faq())
    return '\n'.join(out)


def write_sitemap(root, dist):
    from datetime import date
    today = date.today().isoformat()
    rows = []
    for f, m in PAGE_META.items():
        if not m['index']:
            continue
        for lang in page_langs(f):
            alt = ''.join(
                '<xhtml:link rel="alternate" hreflang="%s" href="%s" />'
                % (LANGS[code]['html'], page_url(code, f))
                for code in page_langs(f))
            alt += '<xhtml:link rel="alternate" hreflang="x-default" href="%s" />' % x_default_url(f)
            rows.append('  <url><loc>%s</loc><lastmod>%s</lastmod>'
                        '<changefreq>weekly</changefreq><priority>%s</priority>%s</url>'
                        % (page_url(lang, f), today, m['priority'], alt))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
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


def svg_inner(name):
    """An asset SVG's paths with the <svg> wrapper removed, so a page can define
    the field once in a hidden <defs> and pull it in with <use> wherever it is
    needed. The Kit shows eight contour fields; eight inline copies of
    topo-dense.svg would add about 400KB to that page for no visual gain."""
    raw = asset(name)
    m = re.search(r'<svg[^>]*>(.*)</svg>', raw, re.S)
    if not m:
        sys.exit('%s does not look like an SVG' % name)
    return re.sub(r'<metadata>.*?</metadata>', '', m.group(1), flags=re.S).strip()


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


# Attributes whose values are identifiers, never prose. localize() holds these
# so the Chinese substring replace cannot rewrite an id or a form field name.
ID_ATTRS = ('id', 'for', 'name', 'aria-labelledby', 'aria-controls', 'aria-describedby')

ZH_TEXT = {
    'Menu': '菜单',
    'Home': '首页',
    'Landmarks': '作品地标',
    'The Kit': '工具箱',
    'Newsroom': '新闻室',
    'Contact us': '联系我们',
    'Book a discovery call': '预约咨询',
    'See what we build': '看看我们建设什么',
    'You run the business.': '你专注经营。',
    'We make it <span class="hero__key">seen</span>.': '我们让客户<span class="hero__key">看见</span>你。',
    'We find your <span class="hero__key">buyers</span>.': '我们帮你找到<span class="hero__key">买家</span>。',
    'We get you <span class="hero__key">chosen</span>.': '我们让你成为<span class="hero__key">首选</span>。',
    'We <span class="hero__key">automate</span> the rest.': '我们把其余流程<span class="hero__key">自动化</span>。',
    'We put <span class="hero__key">AI</span> to work.': '我们让 <span class="hero__key">AI</span> 真正工作。',
    'We <span class="hero__key">kit</span> you out.': '我们配齐你的<span class="hero__key">工具</span>。',
    'We even the <span class="hero__key">odds</span>.': '我们帮你拉平<span class="hero__key">差距</span>。',
    'We build it to <span class="hero__key">scale</span>.': '我们建设能<span class="hero__key">扩展</span>的系统。',
    'The tech department that makes you hard&nbsp;to&nbsp;beat.': '让你更难被超越的技术团队。',
    'Websites <b>&middot;</b> SEO &amp; AEO <b>&middot;</b> Marketing <b>&middot;</b> Internal Tools <b>&middot;</b> AI Workflows <b>&middot;</b> Automation <b>&middot;</b> Cloud': '网站建设 <b>&middot;</b> SEO 与 AEO <b>&middot;</b> 营销 <b>&middot;</b> 内部工具 <b>&middot;</b> AI 工作流 <b>&middot;</b> 自动化 <b>&middot;</b> 云服务',
    'Websites': '网站建设',
    'Internal Tools': '内部工具',
    'AI Workflows': 'AI 工作流',
    'Automation': '自动化',
    'SEO &amp; AEO': 'SEO 与 AEO',
    'Marketing': '营销',
    'Cloud': '云服务',
    'Hover a pin to see what we build': '悬停标记查看我们建设的内容',
    'Registered Singapore LLP': '新加坡注册 LLP',
    'Based in Singapore': '总部位于新加坡',
    'Replies within one working day': '一个工作日内回复',
    'What we keep finding': '我们经常看到的问题',
    'Nobody sets out to end up here. It happens one reasonable decision at a time. A freelancer for the site. Someone else for payments. A tool signed up for in 2022 that nobody has logged into since.': '没有人一开始就想把系统弄成这样。它通常是一连串看似合理的决定慢慢堆出来的：网站找一个自由职业者，付款交给另一个人，2022 年注册的工具从此没人登录。',
    'Every choice made sense on its own. Nobody was ever responsible for the whole.': '每个选择单独看都合理。只是从来没有一个人负责整体。',
    'That is the job. Not a website. The whole thing.': '这才是工作本身。不是一个网站，而是整个系统。',
    'Fragments of the problem': '问题的碎片',
    '3 weeks ago': '3 周前',
    'a month ago': '1 个月前',
    '2 months ago': '2 个月前',
    '4 months ago': '4 个月前',
    '5 months ago': '5 个月前',
    '6 months ago': '6 个月前',
    '7 months ago': '7 个月前',
    'one star out of five': '五星中的一星',
    'Tried the contact form three times. Never heard back. Assumed they had shut down.': '联系表单试了三次，一直没有回复。还以为他们已经停业了。',
    'Site looks like nothing has been touched since 2017. Could not tell if they were still trading.': '网站看起来像 2017 年之后就没人维护。不确定他们是否还在营业。',
    'Got three separate emails about one booking, from three different systems.': '一个预约收到了三封邮件，来自三个不同系统。',
    'They still had my old address on file. Delivery went to a flat I left two years ago.': '他们系统里还是我的旧地址。货送到了我两年前搬离的公寓。',
    'Waited four days for a quote. Was told someone has to work them out by hand.': '等报价等了四天。对方说还得有人手动计算。',
    'Half the site still says coming soon. It has said that for a year.': '网站一半页面还写着即将上线，已经这样一年了。',
    'Booking page has been down all week. Nobody there seems able to fix it.': '预约页面整周都打不开。看起来没人能修好。',
    'Ended up phoning the owner directly. He apologised and said he would sort it out himself.': '最后只能直接打电话给老板。他道歉说会自己处理。',
    'Reviewed: a business like yours': '评价对象：类似你的企业',
    'Who we build for': '我们服务谁',
    'We are not specialists in your industry. We are specialists in what breaks in it.': '我们不是你的行业专家。我们专门处理行业里最容易卡住的技术问题。',
    'Retail &amp; F&amp;B': '零售与餐饮',
    'Stock, orders and bookings that stop disagreeing with each other.': '让库存、订单和预约不再互相打架。',
    'Online ordering and reservations': '线上点单与预约',
    'POS and inventory that sync': 'POS 与库存同步',
    'Loyalty and repeat campaigns': '会员与复购活动',
    'Delivery platform reconciliation': '外卖平台对账',
    'Explore Retail and F&amp;B solutions': '查看零售与餐饮方案',
    'Education': '教育',
    'Enrolment, attendance and fees, without the spreadsheet in the middle.': '招生、出勤和收费，不再靠表格居中协调。',
    'Enrolment and class scheduling': '报名与排课',
    'Parent portals and comms': '家长入口与沟通',
    'Attendance and fee collection': '出勤与收费',
    'Course and programme sites': '课程与项目网站',
    'Explore Education solutions': '查看教育方案',
    'Professional Services': '专业服务',
    'Less admin between winning the work and actually getting paid.': '从赢得客户到收到款项，中间少一点行政消耗。',
    'Client portals and documents': '客户入口与文档',
    'Proposal and invoice automation': '方案与发票自动化',
    'A CRM people actually use': '团队真的会用的 CRM',
    'A site that wins enquiries': '能带来询盘的网站',
    'Explore Professional Services solutions': '查看专业服务方案',
    'Trades &amp; Home Services': '工程与上门服务',
    'From enquiry to quote to job, without losing anyone in a thread.': '从询盘、报价到派工，不再把客户丢在聊天记录里。',
    'Quote-to-job pipelines': '报价到工单流程',
    'Scheduling and dispatch': '排班与派工',
    'Photo reports and sign-offs': '照片报告与签收',
    'Deposits and payments': '订金与付款',
    'Explore Trades and Home Services solutions': '查看工程与上门服务方案',
    'Not on this list?': '不在列表里？',
    'The work underneath is the same. Tell us what is broken and we will tell you if we can fix it.': '底层工作其实相同。告诉我们哪里出问题，我们会告诉你是否能修。',
    'Start Here': '从这里开始',
    'Our path to building': '我们的建设路径',
    'From the first call to still working a year later.': '从第一次通话，到一年后仍然稳定运行。',
    'Survey': '勘察',
    'We learn how your business actually works before touching anything.': '动手前，我们先理解你的业务实际如何运转。',
    'You get a written picture of what is broken and what it is costing you.': '你会得到一份书面梳理，说明哪里坏了，以及正在造成什么成本。',
    'Mark the route': '标出路线',
    'Scope, cost and plan, agreed before anything gets built.': '先确定范围、成本和计划，再开始建设。',
    'You get a fixed scope and a fixed price. No surprise invoices.': '你会得到固定范围和固定价格，不会突然冒出账单。',
    'Stack': '搭建',
    'We build it in the open, not behind a curtain.': '我们公开推进建设，不躲在幕后。',
    'You get a live link from the first week, not a reveal at the end.': '第一周你就能看到实时链接，而不是最后才揭晓。',
    'Stress the stack': '压力测试',
    'We try to break it before your customers do.': '在客户遇到问题前，我们先尝试把它测坏。',
    'You get something that works on their phone, not just on ours.': '你得到的是能在客户手机上运行的东西，不只是在我们设备上正常。',
    'Plant the marker': '上线',
    'We launch it, and we are the ones awake during the cutover.': '我们负责上线，切换时醒着盯住的人也是我们。',
    'You get no lost data and no downtime anyone notices.': '你得到的是数据不丢、用户几乎无感的上线。',
    'Keep the trail': '持续维护',
    'We keep it running, and we keep people arriving.': '我们让系统持续运行，也让客户持续到来。',
    'Most builds stop at launch. This is the step that makes the rest worth it.': '大多数项目止步于上线。这一步，才让前面的投入真正值得。',
    "Nobody owns your tech. Let's fix that.": '没人真正负责你的技术。我们来修好这件事。',
    'One call, and someone finally does.': '一次通话之后，终于有人接手。',
    'No pitch, no obligation. You leave with a written summary either way.': '不推销，无义务。无论是否合作，你都会拿到一份书面总结。',
    'Or email us at ': '也可以发邮件给我们：',
    'Contact us': '联系我们',
    'Either route reaches both of us. Expect a reply within one working day.': '两种方式都会同时到达我们这里。一个工作日内回复。',
    'Get in touch': '取得联系',
    'Tell us what is broken. We will tell you whether we can fix it, and what it would take.': '告诉我们哪里卡住了。我们会告诉你能否修复，以及需要什么。',
    'Schedule a meeting': '预约会议',
    'Pick a time that suits you. Thirty minutes, no pitch.': '选择适合你的时间。30 分钟，不推销。',
    'Open the calendar': '打开日历',
    'Email us': '给我们发邮件',
    'If you would rather write it down, this reaches both of us.': '如果你更想写下来，这封邮件会同时到达我们这里。',
    'Follow us': '关注我们',
    'Send us a message': '发送消息',
    'The more specific you are about what is breaking, the more useful our first reply will be.': '你描述得越具体，我们第一次回复就越有用。',
    'Name': '姓名',
    'Email': '邮箱',
    'Phone': '电话',
    'What do you need': '你需要什么',
    'Choose one': '请选择',
    'General enquiries': '一般咨询',
    'Request a quote': '获取报价',
    'Support': '支持',
    'Partnership': '合作',
    'Business': '公司 / 业务',
    'What is breaking': '哪里卡住了',
    'Send message': '发送消息',
    'Message sent': '消息已发送',
    'Thank you. We will come back to you within one working day, usually sooner.': '谢谢。我们会在一个工作日内回复，通常会更快。',
    'Build your brief before we talk': '通话前先整理你的需求',
    'Pick the software and interfaces you want, arrange them into the shape your business needs, and send it over. The call then starts from your plan, not a blank page.': '选择你想要的软件和界面，组合成适合业务的形状后发给我们。这样通话会从你的计划开始，而不是从空白页开始。',
    'Opening soon': '即将开放',
    'Open discovery': '打开需求梳理',
    'Coming soon': '即将上线',
    'Locked': '已锁定',
    'Not connected yet. Email hello@cairnco.cloud in the meantime.': '表单暂未连接。请先发送邮件到 hello@cairnco.cloud。',
    'Sending': '发送中',
    'That did not send.': '消息没有发送成功。',
    ' Please email hello@cairnco.cloud.': ' 请发送邮件到 hello@cairnco.cloud。',

    # ---- The Kit. Adapted rather than translated word for word: the
    # Chinese market searches different phrases, and the 25 Sep sweep found
    # the Chinese side is where CairnCo already ranks first and where the
    # competition is measurably weaker.
    "The manual processes worth automating first are the boring ones. Retyping between two systems. The report someone assembles every Tuesday. The quote that becomes an invoice by hand. Each one is small enough to tolerate, and together they are a day a week, which is why business process automation pays back faster in a small company than a large one. E-invoicing is the one with a deadline attached: InvoiceNow is Singapore's Peppol network, and GST registered businesses are being phased onto it.": '最值得先自动化的，是那些无聊的流程。在两个系统之间重复录入。每周二有人手工拼出来的报表。手工把报价改成发票。每一件都小到可以忍，加起来就是一周一天。这就是业务流程自动化在小公司回本比大公司更快的原因。其中电子发票有明确的时间表：InvoiceNow 是新加坡的 Peppol 网络，GST 注册企业正在分阶段接入。',
    'Cloud is the part nobody thinks about until it breaks: where the site lives, where the backups are, who can get in, and what happens when the person who set it up leaves. We run it on Cloudflare, we set up company email and the records that keep it out of spam, and the domain, the hosting account and the DNS stay registered in your name, not ours. That is what website ownership actually means, and it is the difference between changing supplier and starting again.': '云服务是出事之前没有人会想到的那一块：网站放在哪里、备份在哪里、谁能登录，以及当初把这些设置好的人离职以后怎么办。我们用 Cloudflare 运维，帮你配好企业邮箱和让邮件不进垃圾箱的那几条记录，而域名、主机账号和 DNS 都登记在你的名下，不在我们名下。这才是网站所有权真正的意思，也是换一家供应商和推倒重来之间的差别。',
    "Being found in Singapore now happens in two places: search results, and the answers ChatGPT, Gemini and Google's AI Overviews give when somebody asks instead of searching. That second one is answer engine optimisation, also called AEO or GEO. In September 2026 we ran 44 searches a Singapore buyer might type and Google returned an AI Overview on 40 of them. Both halves are won the same way: a site a machine can read, and content worth quoting.": '在新加坡被找到，现在发生在两个地方：搜索结果，以及有人直接提问时 ChatGPT、Gemini 和 Google AI 摘要给出的答案。后者叫答案引擎优化，也写作 AEO 或 GEO。2026 年 9 月，我们实测了 44 个新加坡买家可能输入的搜索，其中 40 个 Google 返回了 AI 摘要。两边的打法是同一套：一个机器读得懂的网站，加上值得被引用的内容。',
    'CairnCo designs, builds and maintains websites for small businesses in Singapore. Most agencies hand over a folder of files and disappear, so the site goes live and then quietly stops working: the plugin breaks, the rankings drift, nobody owns it. We stay on for the maintenance, and the domain and hosting stay registered in your name. Every site is hand built, in English and Chinese, so there is no theme to break and no licence to renew.': 'CairnCo 为新加坡的中小企业设计、开发并长期维护网站。多数公司交付一个文件夹就消失了：网站上线之后慢慢出问题，插件坏掉、排名下滑、没有人负责。我们把网站建好，放在我们自己运维的基础设施上，并在上线之后继续维护，域名和主机都登记在你的名下。每一个网站都是手写代码，中英双语，没有模板会坏，也没有授权费要续。',
    'Internal tools are the systems a business runs on inside: customer records, job and work order tracking, stock. Most Singapore SMEs run those on a spreadsheet four people edit at once, and a process someone holds in their head. It works until the team grows, the file gets copied, or that person goes on leave. We build the tool that replaces it, with a login, one version of the truth, and a record of who changed what.': '内部工具就是一家公司内部真正在用的系统：客户资料、工单与任务追踪、库存。新加坡大多数中小企业把这些放在一份四个人同时编辑的表格里，再加上某个人脑子里记着的流程。团队一变大、文件一被复制、那个人一请假，它就撑不住了。我们把它换成一套有登录、有唯一数据、有修改记录的系统。',
    'AI workflow automation earns its place where the work is reading, sorting and drafting. It does not earn it where the work is deciding. So we build the reading and the drafting and leave a person holding the decision, because a system that guesses without a check is worse than doing it by hand. Everything runs against your own documents and records, not the open internet.': 'AI 工作流自动化真正有价值的地方，是阅读、分类和起草，而不是替你做决定。所以我们把阅读和起草交给系统，把决定留给人：一个没有复核就自行猜测的系统，比手工做还糟。所有处理都只针对你自己的文档和记录，不接入公开互联网。',
    'A site nobody visits is a brochure in a drawer. This is the work that brings people to it and turns arrivals into enquiries. It sits on top of everything else here, because traffic pointed at a slow site or an unanswered form is money spent annoying people.': '没有人访问的网站，就是抽屉里的一本宣传册。这部分工作负责把人带过来，并把访问变成询价。它建立在前面所有东西之上：把流量导向一个很慢的网站，或者一个没人回复的表单，只是花钱惹人烦。',
    'Seven things we build for Singapore businesses: websites, internal tools, AI workflows, automation, SEO and AEO, marketing and cloud. Most jobs use three or four at once. That is the argument for one tech partner rather than three suppliers.': '我们为新加坡企业做的七件事：网站建设、内部工具、AI 工作流、自动化、SEO 与 AEO、营销、云服务。大多数项目会同时用到其中三到四项。这就是找一个技术伙伴、而不是三家供应商的理由。',
    'That is what the first call is for. Thirty minutes, no obligation, and you leave with a written picture of what is actually wrong, whether or not you hire us.': '第一次通话就是用来把这件事问清楚的。三十分钟，没有任何义务。无论最后是否合作，你都会带走一份关于问题究竟出在哪里的书面说明。',
    'Not sure which of these you need?': '不确定自己需要哪一项？',
    'AI assistant over your documents': '基于内部文档的 AI 助手',
    'Invoice and receipt data capture': '发票与收据数据提取',
    'WhatsApp enquiries into your CRM': 'WhatsApp 询单接入 CRM',
    'Answer engine optimisation (AEO)': '答案引擎优化 AEO',
    'Email security: SPF, DKIM, DMARC': '邮件安全：SPF、DKIM、DMARC',
    'Website maintenance and support': '网站维护与技术支持',
    'Xero and QuickBooks integration': 'Xero 与 QuickBooks 集成',
    'Google Ads setup and management': 'Google Ads 开户与代运营',
    'Migration off your old provider': '从旧供应商迁移',
    'Inventory and stock management': '库存管理系统',
    'Landing pages built to convert': '高转化落地页',
    'Tap to explore Internal Tools': '点击查看内部工具',
    'Google Business Profile setup': 'Google 商家资料设置',
    'Technical SEO audit and fixes': '技术 SEO 审计与修复',
    'Business email on your domain': '企业域名邮箱',
    'English and Chinese websites': '中英双语网站',
    'Restaurant ordering systems': '餐饮在线点餐系统',
    'Custom software development': '定制软件开发',
    'Job and work order tracking': '工单与任务追踪',
    'Tap to explore AI Workflows': '点击查看AI 工作流',
    'InvoiceNow and Peppol setup': 'InvoiceNow 与 Peppol 对接',
    'Business process automation': '业务流程自动化',
    'Getting named in AI answers': '让 AI 答案提到你',
    'Conversion tracking and GA4': '转化追踪与 GA4',
    'Managed hosting and domains': '托管与域名代管',
    'Web design and development': '网站设计与开发',
    'Tap to explore SEO and AEO': '点击查看SEO 与 AEO',
    'Lead capture and follow-up': '线索收集与跟进',
    'Tap to explore Automation': '点击查看自动化',
    'Design. Build. Maintain.': '设计。建站。维护。',
    'CRM and customer records': 'CRM 客户管理系统',
    'Customer enquiry chatbot': '客户咨询聊天机器人',
    'Tap to explore Marketing': '点击查看营销',
    'Tap to explore Websites': '点击查看网站建设',
    'Connect. Trigger. Done.': '连接。触发。完成。',
    'Reach. Convert. Repeat.': '触达。转化。复购。',
    'Explore Internal Tools': '查看内部工具',
    'AI workflow automation': 'AI 工作流自动化',
    'Ranked. Quoted. Found.': '排名。引用。被找到。',
    'Scroll down to explore': '向下滚动查看',
    'Clients. Staff. Jobs.': '客户。员工。工单。',
    'Host. Secure. Own it.': '托管。安全。归你所有。',
    'Talk to us about this': '就这一项聊聊',
    'Explore AI Workflows': '查看AI 工作流',
    'Tap to explore Cloud': '点击查看云服务',
    'Explore SEO and AEO': '查看SEO 与 AEO',
    'Read. Sort. Draft.': '阅读。分类。起草。',
    'Explore Automation': '查看自动化',
    'Explore Marketing': '查看营销',
    'Tap to<br>explore': '点击<br>查看',
    'Explore Websites': '查看网站建设',
    'Explore Cloud': '查看云服务',
    'Read the FAQ': '查看常见问题',
    'Talk to us': '联系我们',
    'Close': '关闭',
}


def strip_en_only(text, lang):
    """<!--EN-ONLY--> ... <!--/EN-ONLY--> survives on English pages and is cut
    out of every other language. It exists so the shared nav can carry a link to
    a page that is only built in English, without pointing Chinese readers at a
    URL that 404s."""
    if lang == 'en':
        return text.replace('<!--EN-ONLY-->', '').replace('<!--/EN-ONLY-->', '')
    return re.sub(r'<!--EN-ONLY-->.*?<!--/EN-ONLY-->', '', text, flags=re.S)


def localize(text, lang):
    cfg = LANGS[lang]
    text = text.replace('<html lang="en">', '<html lang="%s">' % cfg['html'])
    text = strip_en_only(text, lang)
    head, sep, body = text.partition('</head>')
    if not sep:
        head, body = '', text
    body = rewrite_links(body, lang)
    body = add_language_links(body, lang)
    if lang == 'zh':
        held = []

        def hold(match):
            held.append(match.group(0))
            return '@@HOLD_%d@@' % (len(held) - 1)

        # Scripts are code, not copy.
        body = re.sub(r'<script\b.*?</script>', hold, body, flags=re.S)

        # Identifier attributes are held as well. ZH_TEXT is a blind substring
        # replace, so without this an id like kitSheetName becomes kitSheet姓名
        # the moment 'Name' is in the table, and every getElementById against it
        # returns null. That is exactly how it broke.
        #
        # Only these, and deliberately NOT class: several translation keys carry
        # their own markup, for example the rotating hero lines, which are keyed
        # on 'We <span class="hero__key">kit</span> you out.'. Holding class
        # values stops those keys matching and the page silently reverts to
        # English. ID_ATTRS is guarded against that below.
        body = re.sub(r'\s(?:%s)="[^"]*"' % '|'.join(ID_ATTRS), hold, body)

        for src, dst in sorted(ZH_TEXT.items(), key=lambda item: len(item[0]), reverse=True):
            body = body.replace(src, dst)
        for i, chunk in enumerate(held):
            body = body.replace('@@HOLD_%d@@' % i, chunk)
    return head + sep + body if sep else body


def rewrite_links(text, lang):
    repl = {
        'href="index.html"': 'href="%s/"' % LANGS[lang]['prefix'],
        'href="contact.html"': 'href="%s/contact/"' % LANGS[lang]['prefix'],
        'href="landmarks.html"': 'href="%s/landmarks/"' % LANGS[lang]['prefix'],
        'href="kit.html"': 'href="%s/kit/"' % LANGS[lang]['prefix'],
        'href="newsroom.html"': 'href="%s/newsroom/"' % LANGS[lang]['prefix'],
        'href="faq.html"': 'href="%s/faq/"' % LANGS[lang]['prefix'],
    }
    for a, b in repl.items():
        text = text.replace(a, b)
    return text


def add_language_links(text, lang):
    other = 'zh' if lang == 'en' else 'en'
    here = LANGS[lang]['prefix']
    there = LANGS[other]['prefix']
    switch = ('<a href="%s/" hreflang="%s" lang="%s">%s</a>'
              % (there, LANGS[other]['html'], LANGS[other]['html'], LANGS[other]['label']))
    text = text.replace('<a class="btn" href="%s/contact/">' % here,
                        switch + '\n    <a class="btn" href="%s/contact/">' % here,
                        1)
    text = text.replace('</div></footer>', '    %s\n  </div>\n</div></footer>' % switch, 1)
    return text


def chooser_page():
    alts = '\n'.join(alternates('index.html'))
    return '''<!DOCTYPE html>
<html lang="en-SG">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<link rel="canonical" href="%s/">
%s
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#EDE6D8;color:#1F2A26;font:17px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{width:min(92vw,34rem);padding:2rem}
h1{margin:0 0 .75rem;font:600 clamp(2rem,6vw,3.1rem)/1.1 Georgia,serif}
p{margin:.4rem 0 1.5rem;color:#5E6560}
a{display:inline-block;margin:.25rem .5rem .25rem 0;padding:.78em 1.15em;border-radius:6px;background:#3D5A50;color:#F5F0E5;text-decoration:none}
a+a{background:transparent;color:#2A3F38;border:1px solid rgba(61,90,80,.38)}
</style>
<script>
(function(){
  var langs=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'']).join(',');
  location.replace(/^zh/i.test(langs)?'/zh/':'/en/');
})();
</script>
</head>
<body>
<main>
<h1>CairnCo</h1>
<p>Choose your language. 请选择语言。</p>
<a href="/en/" hreflang="en-SG" lang="en-SG">English</a>
<a href="/zh/" hreflang="zh-Hans-SG" lang="zh-Hans-SG">中文</a>
</main>
</body>
</html>
''' % (_esc(LANGS['en']['root_title']), _esc(LANGS['en']['root_desc']), SITE, alts)


def redirect_page(target, title='Redirecting | CairnCo'):
    return '''<!DOCTYPE html>
<html lang="en-SG">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<meta name="robots" content="noindex,follow">
<link rel="canonical" href="%s%s">
<meta http-equiv="refresh" content="0; url=%s">
<script>location.replace('%s');</script>
</head>
<body><p><a href="%s">Continue to CairnCo</a></p></body>
</html>
''' % (_esc(title), SITE, target, target, target, target)


# Wrangler serves this directory and nothing else, which is what keeps src/
# and the docs off the public site. The same pages are also written to the
# repo root so the site can still be opened straight off disk.
DIST = None


def finish(path, text):
    left = re.findall(r'__[A-Z_]+__', text)
    if left:
        sys.exit('unfilled placeholder(s) in %s: %s' % (path.name, ', '.join(sorted(set(left)))))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')
    if DIST is not None:
        out = DIST / path.relative_to(ROOT)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    print('  %-24s %6d bytes' % (str(path.relative_to(ROOT)), len(text)))


home = read('index.template.html')

SHARED = {
    '__SHELL_CSS__': region(home, 'SHELL-A') + '\n\n' + region(home, 'SHELL-B'),
    '__HEAD__': region(home, 'HEAD', comment=True),
    '__NAV_HTML__': region(home, 'NAV', comment=True),
    '__FOOT_HTML__': region(home, 'FOOT', comment=True),
    '__NAV_JS__': read('nav.js').strip(),
    '__TOPO_OPEN__': asset('topo-open.svg'),
    '__TOPO_DENSE__': asset('topo-dense.svg'),
    '__TOPO_DENSE_DEFS__': svg_inner('topo-dense.svg'),
    # drawn at the shapes The Kit uses: a wide short hero band, and an
    # upright field the banners each show a different window of
    '__TOPO_BAND_DEFS__': svg_inner('topo-band.svg'),
    '__TOPO_CARD_DEFS__': svg_inner('topo-card.svg'),
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
# Empty dist, but never remove the directory itself. On Windows a folder that
# any running process is sitting in cannot be deleted, and the local preview
# server sits in exactly this one. Removing the contents is all the build
# needs; rmtree's final rmdir was the only part that ever failed.
DIST.mkdir(exist_ok=True)
for _stale in DIST.iterdir():
    try:
        if _stale.is_dir() and not _stale.is_symlink():
            shutil.rmtree(_stale)
        else:
            _stale.unlink()
    except OSError as _err:
        sys.exit(
            'could not clear dist\\%s: %s\n'
            'Something has that file open. The usual cause is the local preview:\n'
            'close the "CairnCo preview server" window, then build again.'
            % (_stale.name, _err))

print('building cairnco.cloud')
_missing = [s for s, _ in SOCIAL_ICONS if s not in _found]
if _missing:
    print('  social icons still placeholders: %s' % ', '.join(_missing))
    print('  drop the official SVGs into src/icons/ and rebuild')

# A translation key that carried an identifier attribute would never match,
# because localize() holds those before replacing. Fail loudly rather than
# quietly shipping an English string on a Chinese page.
_clash = sorted({k for k in ZH_TEXT for a in ID_ATTRS if (' %s="' % a) in k})
if _clash:
    print('ZH_TEXT keys contain an identifier attribute, which localize() holds:')
    for k in _clash:
        print('  %s' % k[:90])
    sys.exit('drop the attribute from the key, or remove it from ID_ATTRS')

sub = read('sub.template.html')
_faq_tpl = read('faq.template.html')

# The questions are written twice: once as visible text in faq.template.html,
# and once in FAQ above, which is what the FAQPage schema is built from. If the
# two ever drift, the page says one thing and the structured data says another,
# which is worse than having no schema at all. Fail the build instead.
_tpl_qs = re.findall(r'<span class="qa__text">(.*?)</span>', _faq_tpl, re.S)
_list_qs = [q for q, _ in FAQ]
if _tpl_qs != _list_qs:
    print('FAQ questions do not match between the page and the schema:')
    for i in range(max(len(_tpl_qs), len(_list_qs))):
        a = _tpl_qs[i] if i < len(_tpl_qs) else '(missing)'
        b = _list_qs[i] if i < len(_list_qs) else '(missing)'
        if a != b:
            print('  %2d  page:   %s' % (i + 1, a))
            print('      schema: %s' % b)
    sys.exit('fix faq.template.html or the FAQ list in build.py, then rebuild')

pages = [
    ('index.html', home, {}),
    ('contact.html', read('contact.template.html'), {}),
    ('faq.html', _faq_tpl, {}),
    ('kit.html', read('kit.template.html'), {}),
]
for filename, slug, name in HOLDING_PAGES:
    if filename == 'kit.html':
        continue          # a real page now, built from its own template above
    pages.append((filename, sub, {'__PAGE_NAME__': name}))

for lang in LANGS:
    for filename, template, extra in pages:
        if lang not in page_langs(filename):
            continue
        data = dict(extra)
        if filename in ('landmarks.html', 'kit.html', 'newsroom.html') and lang == 'zh':
            data['__PAGE_NAME__'] = localized_meta(filename, lang)['title'].split(' | ')[0]
        data['__META__'] = head_meta(filename, lang)
        html = localize(fill(template, data), lang)
        finish(ROOT / page_out(lang, filename), html)

# Redirects, not content. Two generations of old address are kept alive:
# the original flat .html files, and the /en/ prefix that briefly held the
# English pages. Both are noindex so they never compete with the real page.
legacy = {
    'contact.html': '/contact/',
    'landmarks.html': '/landmarks/',
    'kit.html': '/kit/',
    'newsroom.html': '/newsroom/',
}
for filename, target in legacy.items():
    finish(ROOT / filename, redirect_page(target))

for _f in PAGE_META:
    _slug = PAGE_META[_f]['slug']
    _to = '/' + (_slug + '/' if _slug else '')
    finish(ROOT / 'en' / (_slug or '') / 'index.html', redirect_page(_to))

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
# ---- search-engine ownership proofs --------------------------------------
# Google and Bing prove you control this domain by looking for a file they
# issued, served byte-for-byte at the site root. Copied verbatim, never
# templated, never localized, and deliberately kept out of the sitemap.
# Removing one un-verifies the property, so they live in src/ and are
# re-copied on every build.
#
# DIST is wiped at the start of every build, so only ROOT can accumulate a
# stale proof. A retired proof keeps a retired account verified, so it is
# swept out. Deletion can be blocked on some hosts, hence the fallback.
VERIFY_GLOBS = ('google*.html', 'BingSiteAuth.xml', 'yandex_*.html')

_current = set()
for _g in VERIFY_GLOBS:
    _current.update(f.name for f in SRC.glob(_g))

_park = SRC / '_superseded'
for _g in VERIFY_GLOBS:
    for _old in sorted(ROOT.glob(_g)):
        if _old.name in _current:
            continue
        try:
            _old.unlink()
            print('  %-16s removed (superseded ownership proof)' % _old.name[:16])
        except OSError:
            _park.mkdir(exist_ok=True)
            _old.replace(_park / _old.name)
            print('  %-16s parked in src/_superseded/' % _old.name[:16])

_v = []
for _g in VERIFY_GLOBS:
    for _f in sorted(SRC.glob(_g)):
        _raw = _f.read_bytes()
        for _d in (ROOT, DIST):
            (_d / _f.name).write_bytes(_raw)
        _v.append(_f.name)
        print('  %-16s %6d bytes  (ownership proof, copied verbatim)'
              % (_f.name[:16], len(_raw)))
if not _v:
    print('  %-16s none found in src/' % 'verification')

print('  %-16s %6d bytes' % ('robots.txt', len(ROBOTS)))
print('  %-16s %6d urls' % ('sitemap.xml', _n))

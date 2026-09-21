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

# noindex is deliberate on the three holding pages. Three near-identical
# 23-word pages in the index is a quality signal problem, not a win. Remove
# the flag the moment a page has real content, and it joins the sitemap.
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
        priority='0.3',
        index=False,
        en=dict(title='The Kit | CairnCo',
                desc='Reusable pieces CairnCo builds with. This page is being written.'),
        zh=dict(title='工具箱 | CairnCo',
                desc='CairnCo 常用的可复用组件。页面正在撰写中。')),
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


def alternates(filename):
    rows = []
    for lang, cfg in LANGS.items():
        rows.append('<link rel="alternate" hreflang="%s" href="%s">'
                    % (cfg['html'], page_url(lang, filename)))
    rows.append('<link rel="alternate" hreflang="x-default" href="%s">' % x_default_url(filename))
    return rows


def x_default_url(filename):
    return SITE + '/' if filename == 'index.html' else page_url('en', filename)


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
    return '\n'.join(out)


def write_sitemap(root, dist):
    from datetime import date
    today = date.today().isoformat()
    rows = []
    for f, m in PAGE_META.items():
        if not m['index']:
            continue
        for lang in LANGS:
            alt = ''.join(
                '<xhtml:link rel="alternate" hreflang="%s" href="%s" />'
                % (cfg['html'], page_url(code, f))
                for code, cfg in LANGS.items())
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
}


def localize(text, lang):
    cfg = LANGS[lang]
    text = text.replace('<html lang="en">', '<html lang="%s">' % cfg['html'])
    head, sep, body = text.partition('</head>')
    if not sep:
        head, body = '', text
    body = rewrite_links(body, lang)
    body = add_language_links(body, lang)
    if lang == 'zh':
        held = []
        def hold_script(match):
            held.append(match.group(0))
            return '@@SCRIPT_%d@@' % (len(held) - 1)
        body = re.sub(r'<script\b.*?</script>', hold_script, body, flags=re.S)
        for src, dst in sorted(ZH_TEXT.items(), key=lambda item: len(item[0]), reverse=True):
            body = body.replace(src, dst)
        for i, script in enumerate(held):
            body = body.replace('@@SCRIPT_%d@@' % i, script)
    return head + sep + body if sep else body


def rewrite_links(text, lang):
    repl = {
        'href="index.html"': 'href="%s/"' % LANGS[lang]['prefix'],
        'href="contact.html"': 'href="%s/contact/"' % LANGS[lang]['prefix'],
        'href="landmarks.html"': 'href="%s/landmarks/"' % LANGS[lang]['prefix'],
        'href="kit.html"': 'href="%s/kit/"' % LANGS[lang]['prefix'],
        'href="newsroom.html"': 'href="%s/newsroom/"' % LANGS[lang]['prefix'],
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
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir(exist_ok=True)

print('building cairnco.cloud')
_missing = [s for s, _ in SOCIAL_ICONS if s not in _found]
if _missing:
    print('  social icons still placeholders: %s' % ', '.join(_missing))
    print('  drop the official SVGs into src/icons/ and rebuild')

sub = read('sub.template.html')
pages = [
    ('index.html', home, {}),
    ('contact.html', read('contact.template.html'), {}),
]
for filename, slug, name in HOLDING_PAGES:
    pages.append((filename, sub, {'__PAGE_NAME__': name}))

for lang in LANGS:
    for filename, template, extra in pages:
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

# -*- coding: utf-8 -*-
"""Production pin choreography for cairnco.cloud's hero map.

Unlike the review boards (a fixed 1280x800 artboard) the real .hero__map is
fluid, so every distance that has to clear the viewport is expressed in vh and
every distance that is about the pin itself stays in px.

Real-site DOM, which differs from the boards:
    button.pin  > span.pin__stick > svg.pin__svg
                > span.pin__label
  .pin        travels   (x along the skip path, y for the fall and hop arcs)
  .pin__stick tumbles   (upright at first contact -> its resting angle)
  .pin__svg   is free for the hover-stand, so it can ease instead of fighting
  .pin::after is the ground shadow (cancels the hop to stay on the floor)

.hero has overflow:hidden and .nav is z-index 60 over the map's 3, so a pin
released above the hero is clipped until it enters, and falls in behind the nav.
"""
import json, pathlib

# The seven landmark pins, in the order they appear in index.template.html.
# x/y must match the --x/--y on each button; rot is where it comes to rest.
PINS = json.loads('''[{"i": 0, "x": "24%", "y": "70%", "lab": "Websites", "rot": -67.3, "dx": -17.7, "dy": 0.1, "a": 0.635}, {"i": 1, "x": "45%", "y": "34%", "lab": "Internal Tools", "rot": 57.2, "dx": -2.7, "dy": -7.7, "a": 0.648}, {"i": 2, "x": "63%", "y": "57%", "lab": "AI Workflows", "rot": 58.8, "dx": -3.0, "dy": 5.9, "a": 0.661}, {"i": 3, "x": "81%", "y": "26%", "lab": "Automation", "rot": -59.8, "dx": -11.1, "dy": 2.3, "a": 0.674}, {"i": 4, "x": "18%", "y": "45%", "lab": "SEO &amp; AEO", "rot": 85.4, "dx": 3.1, "dy": -1.9, "a": 0.687}, {"i": 5, "x": "52%", "y": "86%", "lab": "Marketing", "rot": 86.3, "dx": -18.1, "dy": 6.5, "a": 0.7}, {"i": 6, "x": "88%", "y": "74%", "lab": "Cloud", "rot": -65.0, "dx": -14.2, "dy": -6.9, "a": 0.713}]''')
INTRO_MS = 4325.0          # typing -> hero readable (intro off at 4000 + a 325ms beat)
TOTAL_MS = 6750.0          # ...through to the last pin settling (2425ms of pin action, unchanged)

# The map is fluid, so the run-in is a share of the map box rather than px.
HOPS  = {0: 4, 1: 3, 2: 2, 3: 4, 4: 3, 5: 3, 6: 2}
FRACS = {2: [0, .66, 1.0], 3: [0, .58, .86, 1.0], 4: [0, .52, .80, .93, 1.0]}
HOPH  = [34.0, 15.0, 6.0, 2.0]      # apex heights px, as on the boards
UP    = [180.0, 120.0, 76.0, 44.0]  # contact -> apex, ms (board 7)
DOWN  = [149.0, 100.0, 63.0, 36.0]  # apex -> next contact, ms (board 7)
FALL_MS   = 700.0                   # the drop itself (board 7 averaged ~700ms)
ENTRY_0   = INTRO_MS + 30.0         # first pin crosses the hero's top edge
ENTRY_STEP = 190.0                  # board 7's spacing between entries
HIT     = [1.70, 1.42, 1.24, 1.12]
APEXF   = [0.30, 0.50, 0.70, 0.85]
APEXO   = ['.26', '.42', '.58', '.72']
SQUASH  = [0.88, 0.94, 0.97, 0.99]
STRETCH = [1.03, 1.02, 1.01, 1.00]
EASE_FALL = 'cubic-bezier(.62,0,1,.36)'
EASE_RISE = 'cubic-bezier(0,.78,.32,1)'
FALL_P1, FALL_P2 = (.62, 0.0), (1.0, .36)
RELEASE_VH = 96.0                   # released this far above its landing spot

def _bz(p1, p2, s):
    return 3 * (1 - s) ** 2 * s * p1 + 3 * (1 - s) * s * s * p2 + s ** 3

def _solve_s(p1y, p2y, target):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if _bz(p1y, p2y, mid) < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def _split(p1, p2, t):
    P0, P3 = (0.0, 0.0), (1.0, 1.0)
    L = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    A, B, C = L(P0, p1), L(p1, p2), L(p2, P3)
    D, E = L(A, B), L(B, C)
    F = L(D, E)
    nm = lambda q, o, sp: ((q[0] - o[0]) / sp[0], (q[1] - o[1]) / sp[1])
    span = (P3[0] - F[0], P3[1] - F[1])
    left  = (nm(A, P0, F), nm(D, P0, F)) if min(F) > 1e-9 else ((0., 0.), (1., 1.))
    right = (nm(E, F, span), nm(C, F, span)) if min(span) > 1e-9 else ((0., 0.), (1., 1.))
    return left, right

def cb(p):
    return 'cubic-bezier(%.4f,%.4f,%.4f,%.4f)' % (
        max(0., min(1., p[0][0])), p[0][1], max(0., min(1., p[1][0])), p[1][1])

def rnd(seed):
    s = seed
    while True:
        s = (s * 1103515245 + 12345) & 0x7fffffff
        yield s / 0x7fffffff

def fmt(v):
    s = '%.2f' % v
    return s.rstrip('0').rstrip('.') if '.' in s else s

def pct(ms):
    return fmt(ms / TOTAL_MS * 100.0)

def pin_tf(tx, hop_vh, hop_px):
    """x in px, y as a vh drop plus px hop, on top of the pin's own
    translate(-50%,-100%) anchoring, which the animation has to restate."""
    y = 'calc(-100%'
    if hop_vh: y += ' - %svh' % fmt(hop_vh)
    if hop_px: y += ' - %spx' % fmt(hop_px)
    y += ')'
    x = 'calc(-50%' + (' + %spx' % fmt(tx) if tx else '') + ')'
    return 'translate(%s,%s)' % (x, y)

def sh_tf(hop_vh, hop_px, sx, sy):
    y = '0px' if not (hop_vh or hop_px) else 'calc(%s%s)' % (
        ('%svh' % fmt(hop_vh)) if hop_vh else '0px',
        (' + %spx' % fmt(hop_px)) if hop_px else '')
    return 'translate(-50%%,%s) scale(%s,%s)' % (y, fmt(sx), fmt(sy))

R = rnd(7)
plan = []
for p in PINS:
    i, rot, n = p['i'], p['rot'], HOPS[p['i']]
    sgn = 1.0 if rot > 0 else -1.0
    fx = float(p['x'].rstrip('%'))
    # Run-in in px, NOT %, because a percentage inside a CSS translate resolves
    # against the element's own width (the 40px pin), not the map box.
    D = 44.0 + next(R) * 28.0
    s_e = _solve_s(FALL_P1[1], FALL_P2[1], 0.30)   # visible after 30% of the drop
    fall_L, fall_R = _split(FALL_P1, FALL_P2, s_e)
    above = _bz(FALL_P1[0], FALL_P2[0], s_e) * FALL_MS
    total = FALL_MS + sum(UP[:n]) + sum(DOWN[:n])
    plan.append(dict(i=i, lab=p['lab'].replace('&amp;', '&'), n=n, rot=rot,
                     tvx=D * sgn, fall_L=fall_L, fall_R=fall_R, above=above,
                     total=total, after_entry=total - above))

for slot, q in enumerate(sorted(plan, key=lambda q: q['after_entry'])):
    q['entry']  = ENTRY_0 + ENTRY_STEP * slot
    q['a']      = q['entry'] - q['above']
    q['settle'] = q['a'] + q['total']

out = []
for q in sorted(plan, key=lambda q: q['i']):
    i, n, rot, tvx = q['i'], q['n'], q['rot'], q['tvx']
    a, entry = q['a'], q['entry']
    fr = FRACS[n]
    nodes, t = [(FALL_MS, fr[0], 0.0, 'hit', 0)], FALL_MS
    for k in range(n):
        t += UP[k];   nodes.append((t, (fr[k] + fr[k + 1]) / 2.0, HOPH[k], 'apex', k))
        t += DOWN[k]; nodes.append((t, fr[k + 1], 0.0, 'hit', k + 1))
    off  = lambda u: -(1.0 - u) * tvx
    turn = lambda u: rot * (u ** 0.7)

    kf = ['0%%,%s%%{opacity:0;transform:%s}' % (pct(a - 1), pin_tf(off(0), RELEASE_VH, 0)),
          '%s%%{opacity:1;animation-timing-function:%s;transform:%s}'
          % (pct(a), EASE_FALL, pin_tf(off(0), RELEASE_VH, 0))]
    for idx, (dt, u, h, kind, k) in enumerate(nodes):
        last = idx == len(nodes) - 1
        if last:
            kf.append('%s%%,100%%{opacity:1;transform:%s}' % (pct(a + dt), pin_tf(0, 0, 0)))
        else:
            kf.append('%s%%{opacity:1;animation-timing-function:%s;transform:%s}'
                      % (pct(a + dt), EASE_RISE if kind == 'hit' else EASE_FALL,
                         pin_tf(off(u), 0, h)))
    out.append('@keyframes pinDrop%d{%s}' % (i, ''.join(kf)))

    tk = ['0%%,%s%%{transform:rotate(0deg) scaleY(1.06)}' % pct(a + FALL_MS)]
    for idx, (dt, u, h, kind, k) in enumerate(nodes[1:], start=1):
        last = idx == len(nodes) - 1
        sy = 1.0 if last else (SQUASH[min(k, 3)] if kind == 'hit' else STRETCH[min(k, 3)])
        tk.append('%s%%%s{transform:rotate(%sdeg) scaleY(%s)}'
                  % (pct(a + dt), ',100%' if last else '', fmt(turn(u)), fmt(sy)))
    out.append('@keyframes pinTumble%d{%s}' % (i, ''.join(tk)))

    sk = ['0%%,%s%%{opacity:0;animation-timing-function:%s;transform:%s}'
          % (pct(a), cb(q['fall_L']), sh_tf(RELEASE_VH, 0, 0.15, 0.5)),
          '%s%%{opacity:0;animation-timing-function:%s;transform:%s}'
          % (pct(entry), cb(q['fall_R']), sh_tf(RELEASE_VH * 0.7, 0, 0.18, 0.5))]
    for idx, (dt, u, h, kind, k) in enumerate(nodes):
        last = idx == len(nodes) - 1
        stretch = 1.0 + 0.55 * (u ** 0.7)
        if last:
            sk.append('%s%%,100%%{opacity:.62;transform:%s}' % (pct(a + dt), sh_tf(0, 0, stretch, 0.50)))
        elif kind == 'hit':
            sk.append('%s%%{opacity:1;animation-timing-function:%s;transform:%s}'
                      % (pct(a + dt), EASE_RISE, sh_tf(0, 0, stretch * HIT[k], 0.62)))
        else:
            sk.append('%s%%{opacity:%s;animation-timing-function:%s;transform:%s}'
                      % (pct(a + dt), APEXO[k], EASE_FALL, sh_tf(0, h, stretch * APEXF[k], 1.0)))
    out.append('@keyframes pinShadow%d{%s}' % (i, ''.join(sk)))

for q in sorted(plan, key=lambda q: q['i']):
    i = q['i']
    # Scoped to .intro-full, so the whole thing is first-visit-only with no JS:
    # on a return the html element has .intro-quiet and none of this applies, so
    # the pins stand upright with their normal hover exactly as they do today.
    # `both` fill is what leaves them lying toppled once the drop has finished.
    sel = '.intro-full .hero__map .pin:nth-of-type(%d)' % (i + 1)
    out.append('%s{--rot:%sdeg;animation:pinDrop%d %sms linear both}' % (sel, fmt(q['rot']), i, fmt(TOTAL_MS)))
    out.append('%s .pin__stick{animation:pinTumble%d %sms linear both}' % (sel, i, fmt(TOTAL_MS)))
    out.append('%s::after{animation:pinShadow%d %sms linear both}' % (sel, i, fmt(TOTAL_MS)))

OUT = pathlib.Path(__file__).with_name('pins.anim.css')
CSS = '\n'.join(out) + '\n'
OUT.write_text(CSS, encoding='utf-8')

# Install it straight into the template. The stylesheet is inlined into the
# page, so writing only the .css file would silently leave the site running an
# older copy -- which is exactly what happened once.
TPL = pathlib.Path(__file__).with_name('index.template.html')
A, B = '/* ==PINS:START==', '/* ==PINS:END== */'
_t = TPL.read_text(encoding='utf-8')
_i, _j = _t.index(A), _t.index(B)
_head = _t[_i:_t.index('*/', _i) + 2]
TPL.write_text(_t[:_i] + _head + '\n' + CSS + B + _t[_j + len(B):], encoding='utf-8')
print('  installed into index.template.html')

last = max(q['settle'] for q in plan)
assert min(q['entry'] for q in plan) >= INTRO_MS, 'a pin enters before the hero is readable'
assert last <= TOTAL_MS, 'a pin is still moving when the animation ends'
_ls = sorted(q['settle'] for q in plan)
assert min(b - a for a, b in zip(_ls, _ls[1:])) > 40, 'two pins land together'
assert last <= 8750, 'pins run past the end of the animation'
print('  hero readable %.0fms   first pin enters %.0fms   last lands %.0fms   total %.0fms'
      % (INTRO_MS, min(q['entry'] for q in plan), last, TOTAL_MS))
print('  landing gaps: %s ms' % [round(b - a) for a, b in zip(_ls, _ls[1:])])
for q in sorted(plan, key=lambda q: q['entry']):
    print('   p%d %-15s skips %d  enters %4.0fms  lands %4.0fms  run-in %3.0fpx'
          % (q['i'], q['lab'], q['n'], q['entry'], q['settle'], abs(q['tvx'])))
print('  -> %s  (%d rules)' % (OUT.name, len(out)))

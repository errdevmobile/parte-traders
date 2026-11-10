"""Escenas originales de meme bursátil con Velito. Se elige una al azar (estable por día)
entre las que encajan con el tono del mercado: g = verde, a = ámbar/lateral, r = rojo."""
import hashlib

K = '#111'


def body(mood, arms='mid'):
    """Velito en coordenadas 64x100 (sin <svg>)."""
    c = {'g': '#2fd17a', 'a': '#ffc24b', 'r': '#ff5d5d'}.get(mood, '#ffc24b')
    ay = {'up': 30, 'mid': 50, 'down': 66}[arms]
    s = (f'<line x1="32" y1="3" x2="32" y2="22" stroke="{K}" stroke-width="4" stroke-linecap="round"/>'
         f'<line x1="32" y1="78" x2="32" y2="97" stroke="{K}" stroke-width="4" stroke-linecap="round"/>'
         f'<line x1="14" y1="50" x2="2" y2="{ay}" stroke="{K}" stroke-width="4" stroke-linecap="round"/>'
         f'<line x1="50" y1="50" x2="62" y2="{ay}" stroke="{K}" stroke-width="4" stroke-linecap="round"/>'
         f'<rect x="12" y="20" width="40" height="60" rx="9" fill="{c}" stroke="{K}" stroke-width="3"/>')
    if mood == 'g':
        s += (f'<rect x="16" y="36" width="14" height="8" rx="3" fill="{K}"/><rect x="34" y="36" width="14" height="8" rx="3" fill="{K}"/>'
              f'<line x1="30" y1="39" x2="34" y2="39" stroke="{K}" stroke-width="2"/>'
              f'<path d="M22 56 Q32 66 42 56" fill="none" stroke="{K}" stroke-width="3" stroke-linecap="round"/>')
    elif mood == 'r':
        s += (f'<circle cx="24" cy="40" r="5" fill="#fff" stroke="{K}" stroke-width="2"/><circle cx="40" cy="40" r="5" fill="#fff" stroke="{K}" stroke-width="2"/>'
              f'<circle cx="24" cy="40" r="1.6" fill="{K}"/><circle cx="40" cy="40" r="1.6" fill="{K}"/>'
              f'<ellipse cx="32" cy="60" rx="6" ry="7" fill="{K}"/><path d="M47 30 q4 6 0 9 q-4 -3 0 -9z" fill="#7cc7ff"/>')
    else:
        s += (f'<circle cx="24" cy="41" r="4" fill="#fff" stroke="{K}" stroke-width="2"/><circle cx="40" cy="41" r="4" fill="#fff" stroke="{K}" stroke-width="2"/>'
              f'<circle cx="25" cy="42" r="1.8" fill="{K}"/><circle cx="41" cy="42" r="1.8" fill="{K}"/>'
              f'<line x1="19" y1="33" x2="28" y2="35" stroke="{K}" stroke-width="2.5" stroke-linecap="round"/>'
              f'<line x1="36" y1="35" x2="45" y2="31" stroke="{K}" stroke-width="2.5" stroke-linecap="round"/>'
              f'<path d="M24 60 q4 -3 8 0 q4 3 8 0" fill="none" stroke="{K}" stroke-width="3" stroke-linecap="round"/>')
    return s


def vel(mood, x, y, s=1.0, arms='mid', rot=0):
    r = f' rotate({rot} 32 50)' if rot else ''
    return f'<g transform="translate({x} {y}) scale({s}){r}">{body(mood, arms)}</g>'


def candle(x, top, h, up, w=12):
    c = '#3ddc84' if up else '#ff6b6b'
    return (f'<line x1="{x+w/2}" x2="{x+w/2}" y1="{top-7}" y2="{top+h+7}" stroke="{c}" stroke-width="2"/>'
            f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="2" fill="{c}" stroke="{K}" stroke-width="1"/>')


def s_cohete():
    stars = ''.join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#fff" opacity=".8"/>' for x, y in [(30, 20), (70, 50), (250, 30), (280, 90), (200, 15), (120, 25)])
    return (stars + '<path d="M10 170 L80 150 L130 120 L190 95 L260 40" fill="none" stroke="#3ddc84" stroke-width="4" stroke-dasharray="7 6"/>'
            '<g transform="translate(150 95) rotate(-35)">'
            '<path d="M-20 -6 Q-30 0 -20 6 L-44 0z" fill="#ffc24b"/><path d="M-22 -4 Q-28 0 -22 4 L-36 0z" fill="#ff6b6b"/>'
            f'<path d="M-20 -14 H40 Q62 0 40 14 H-20z" fill="#eef5ea" stroke="{K}" stroke-width="3"/>'
            f'<circle cx="30" cy="0" r="6" fill="#7cc7ff" stroke="{K}" stroke-width="2"/>'
            f'<path d="M-14 -14 L-24 -26 L-4 -14z M-14 14 L-24 26 L-4 14z" fill="#ff6b6b" stroke="{K}" stroke-width="2"/></g>'
            + vel('g', 128, 18, .72, 'up'))


def s_surf():
    return ('<path d="M0 180 L0 150 Q60 140 110 120 T220 70 Q260 50 300 30 L300 180z" fill="#3ddc84" opacity=".85" stroke="#111" stroke-width="2"/>'
            '<path d="M0 160 Q70 150 120 132 T230 85 Q270 65 300 52" fill="none" stroke="#c6f68d" stroke-width="3"/>'
            f'<ellipse cx="160" cy="98" rx="46" ry="7" fill="#ffc24b" stroke="{K}" stroke-width="3" transform="rotate(-24 160 98)"/>'
            + vel('g', 128, 4, .82, 'up', -12))


def s_billetes():
    notes = ''
    for i, (x, y, r) in enumerate([(30, 30, -20), (70, 90, 15), (230, 25, 25), (260, 100, -15), (100, 20, 10), (205, 120, -30), (40, 140, 20), (270, 160, 5)]):
        sym = '€' if i % 2 else '$'
        notes += (f'<g transform="translate({x} {y}) rotate({r})"><rect x="-16" y="-9" width="32" height="18" rx="3" fill="#3ddc84" stroke="{K}" stroke-width="2"/>'
                  f'<text x="0" y="5" text-anchor="middle" font-size="13" font-weight="700" fill="{K}" font-family="Arial">{sym}</text></g>')
    return notes + vel('g', 118, 30, 1.25, 'up')


def s_hamaca():
    return ('<line x1="0" y1="150" x2="300" y2="150" stroke="#a9bba9" stroke-width="2" stroke-dasharray="6 6"/>'
            + candle(40, 40, 110, True, 16) + candle(244, 40, 110, False, 16) +
            f'<path d="M56 60 Q150 140 244 60" fill="none" stroke="#ffc24b" stroke-width="4"/>'
            f'<path d="M64 66 Q150 130 236 66" fill="none" stroke="{K}" stroke-width="2" stroke-dasharray="3 5"/>'
            + vel('a', 118, 60, .72, 'down', -75) +
            '<text x="200" y="40" font-size="22" fill="#fff" font-family="Arial" font-weight="700">Z</text>'
            '<text x="220" y="24" font-size="16" fill="#fff" font-family="Arial" font-weight="700" opacity=".8">z</text>'
            '<text x="236" y="12" font-size="12" fill="#fff" font-family="Arial" font-weight="700" opacity=".6">z</text>')


def s_palomitas():
    return (f'<rect x="20" y="20" width="150" height="100" rx="8" fill="#0b1a0d" stroke="{K}" stroke-width="3"/>'
            '<polyline points="30,90 50,60 70,95 90,45 110,85 130,55 150,75 160,65" fill="none" stroke="#ffc24b" stroke-width="3"/>'
            '<text x="140" y="45" font-size="26" fill="#ff6b6b" font-family="Arial" font-weight="900">?</text>'
            f'<line x1="95" y1="120" x2="95" y2="150" stroke="{K}" stroke-width="4"/><line x1="70" y1="150" x2="120" y2="150" stroke="{K}" stroke-width="4"/>'
            + vel('a', 190, 30, 1.1, 'mid') +
            f'<path d="M236 92 L262 92 L256 130 L242 130z" fill="#fff" stroke="{K}" stroke-width="2"/>'
            '<path d="M241 92 L245 130 M250 92 L249 130 M258 92 L253 130" stroke="#ff6b6b" stroke-width="3"/>'
            + ''.join(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff6c8" stroke="{K}" stroke-width="1"/>' for x, y in [(240, 88), (249, 84), (258, 88), (245, 80), (254, 79)]))


def s_montana():
    pts = [(0, 160), (40, 100), (80, 150), (130, 70), (170, 165), (210, 100), (250, 140), (300, 80)]
    track = ' '.join(f'L{x} {y}' for x, y in pts)[1:]
    low = ' '.join(f'L{x} {y+8}' for x, y in pts)[1:]
    return (''.join(f'<line x1="{x}" y1="{y+6}" x2="{x}" y2="180" stroke="#a9bba9" stroke-width="2" opacity=".6"/>' for x, y in pts[1:-1]) +
            f'<path d="M{track}" fill="none" stroke="#ffc24b" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M{low}" fill="none" stroke="#111" stroke-width="2"/>'
            + vel('a', 113, 2, .55, 'up') +
            f'<rect x="102" y="40" width="56" height="26" rx="6" fill="#ff6b6b" stroke="{K}" stroke-width="3"/>'
            f'<circle cx="116" cy="68" r="5" fill="{K}"/><circle cx="144" cy="68" r="5" fill="{K}"/>'
            '<text x="190" y="40" font-size="24" fill="#fff" font-family="Arial" font-weight="900">!!</text>')


def s_paraguas():
    rain = ''.join(candle(x, y, 14 + (i * 7) % 12, False, 8) for i, (x, y) in enumerate([(20, 20), (60, 60), (100, 10), (210, 30), (250, 70), (280, 15), (40, 120), (265, 130), (190, 5)]))
    return (rain + f'<path d="M86 70 Q150 -10 214 70 Q198 58 182 70 Q166 58 150 70 Q134 58 118 70 Q102 58 86 70z" fill="#7cc7ff" stroke="{K}" stroke-width="3"/>'
            f'<line x1="150" y1="22" x2="150" y2="98" stroke="{K}" stroke-width="3"/>'
            + vel('r', 124, 72, 1.0, 'up'))


def s_paracaidas():
    return ('<path d="M10 20 L80 50 L140 110 L210 140 L290 170" fill="none" stroke="#ff6b6b" stroke-width="5"/>'
            '<path d="M276 160 L292 171 L274 176" fill="none" stroke="#ff6b6b" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M120 50 Q170 -20 220 50 Q195 38 170 50 Q145 38 120 50z" fill="#ffc24b" stroke="{K}" stroke-width="3"/>'
            f'<path d="M122 50 L158 92 M218 50 L182 92 M170 50 L170 90" stroke="{K}" stroke-width="2"/>'
            + vel('r', 148, 84, .9, 'up'))


def s_calma():
    return (f'<rect x="150" y="18" width="134" height="90" rx="8" fill="#0b1a0d" stroke="{K}" stroke-width="3"/>'
            '<polyline points="160,35 180,45 195,40 215,65 235,60 255,88 275,98" fill="none" stroke="#ff6b6b" stroke-width="4"/>'
            + vel('r', 50, 40, 1.2, 'mid') +
            f'<path d="M116 92 h22 v24 q0 8 -8 8 h-6 q-8 0 -8 -8z" fill="#fff" stroke="{K}" stroke-width="2"/>'
            f'<path d="M138 98 q8 0 8 7 q0 7 -8 7" fill="none" stroke="{K}" stroke-width="2"/>'
            '<path d="M122 86 q-4 -8 0 -14 M130 86 q-4 -8 0 -14" fill="none" stroke="#fff" stroke-width="2" opacity=".7"/>')


SCENES = {
    'cohete': ('g', s_cohete), 'surf': ('g', s_surf), 'billetes': ('g', s_billetes),
    'hamaca': ('a', s_hamaca), 'palomitas': ('a', s_palomitas), 'montana': ('a', s_montana),
    'paraguas': ('r', s_paraguas), 'paracaidas': ('r', s_paracaidas), 'calma': ('r', s_calma),
}


def _raw(opts, seed, day):
    h = lambda d: int(hashlib.sha256(f'{seed}|{d}'.encode()).hexdigest(), 16) % len(opts)
    if not day:
        return h('')
    # Recorre desde una fecha fija para que el resultado de cada día sea siempre el mismo
    # y nunca coincida con el del día anterior.
    from datetime import date, timedelta
    d = max(date(2026, 1, 1), day - timedelta(days=3650))
    prev = None
    while d <= day:
        i = h(d.isoformat())
        if i == prev and len(opts) > 1:
            i = (i + 1) % len(opts)
        prev, d = i, d + timedelta(days=1)
    return prev


def pick(mood, seed, avoid=None, day=None):
    """Escena al azar para ese tono. Mismo día -> misma escena (no cambia al recargar) y,
    con fecha, nunca repite la del día anterior."""
    opts = sorted(k for k, (m, _) in SCENES.items() if m == mood) or sorted(SCENES)
    if avoid in opts and len(opts) > 1:
        opts.remove(avoid)
    return opts[_raw(opts, seed, day)]


def scene_svg(name):
    return f'<svg class="sc" viewBox="0 0 300 180" aria-hidden="true">{SCENES[name][1]()}</svg>'

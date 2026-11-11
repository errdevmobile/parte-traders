#!/usr/bin/env python3
"""Genera El Parte de las 7 (o una alerta con el mismo diseño) como UN solo archivo HTML.

Campos opcionales en data.json: "title" (por defecto "El Parte de las 7") y
"subtitle" (por defecto "Para el grupo Traders").

Uso: python3 build_parte.py data.json salida.html

- Todo el contenido va pre-renderizado en el HTML: se lee aunque el visor
  del móvil no ejecute JavaScript (vista previa de WhatsApp / Quick Look).
- Con JavaScript activo se añaden pestañas, filtros, acordeones y el botón
  de tema claro/oscuro.
- Las fuentes van incrustadas (no necesita internet).
"""
import base64, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import pick, scene_svg, SCENES
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
E = lambda s: html.escape(str(s), quote=True)
DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
PAISES = {'ES': 'España', 'US': 'EE. UU.', 'DE': 'Alemania', 'FR': 'Francia', 'GB': 'Reino Unido', 'IT': 'Italia',
          'NL': 'Países Bajos', 'CH': 'Suiza', 'JP': 'Japón', 'CN': 'China', 'HK': 'Hong Kong', 'KR': 'Corea del Sur',
          'TW': 'Taiwán', 'BR': 'Brasil', 'CA': 'Canadá', 'MX': 'México', 'DK': 'Dinamarca', 'SE': 'Suecia',
          'BE': 'Bélgica', 'PT': 'Portugal', 'IE': 'Irlanda', 'IN': 'India', 'AU': 'Australia', 'NO': 'Noruega', 'FI': 'Finlandia'}


def flag(cc):
    cc = str(cc).upper()
    return ''.join(chr(0x1F1E6 + ord(c) - 65) for c in cc) if len(cc) == 2 and cc.isalpha() else '🏳️'


MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']


def font(name):
    p = os.path.join(HERE, 'fonts', name)
    return base64.b64encode(open(p, 'rb').read()).decode()


def rich(s):
    """Escapa todo salvo <b>...</b>."""
    s = E(s)
    return s.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')


def velito(mood):
    c = {'g': '#2fd17a', 'a': '#ffc24b', 'r': '#ff5d5d'}.get(mood, '#ffc24b')
    arm = 38 if mood == 'g' else (36 if mood == 'r' else 58)
    s = ('<svg viewBox="0 0 64 100" width="100%" height="100%" aria-hidden="true">'
         '<line x1="32" y1="3" x2="32" y2="22" stroke="#111" stroke-width="4" stroke-linecap="round"/>'
         '<line x1="32" y1="78" x2="32" y2="97" stroke="#111" stroke-width="4" stroke-linecap="round"/>'
         f'<line x1="14" y1="50" x2="4" y2="{arm}" stroke="#111" stroke-width="4" stroke-linecap="round"/>'
         f'<line x1="50" y1="50" x2="60" y2="{arm}" stroke="#111" stroke-width="4" stroke-linecap="round"/>'
         f'<rect x="12" y="20" width="40" height="60" rx="9" fill="{c}" stroke="#111" stroke-width="3"/>')
    if mood == 'g':
        s += ('<rect x="16" y="36" width="14" height="8" rx="3" fill="#111"/><rect x="34" y="36" width="14" height="8" rx="3" fill="#111"/>'
              '<line x1="30" y1="39" x2="34" y2="39" stroke="#111" stroke-width="2"/>'
              '<path d="M22 56 Q32 66 42 56" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/>')
    elif mood == 'r':
        s += ('<circle cx="24" cy="40" r="5" fill="#fff" stroke="#111" stroke-width="2"/><circle cx="40" cy="40" r="5" fill="#fff" stroke="#111" stroke-width="2"/>'
              '<circle cx="24" cy="40" r="1.6" fill="#111"/><circle cx="40" cy="40" r="1.6" fill="#111"/>'
              '<ellipse cx="32" cy="60" rx="6" ry="7" fill="#111"/><path d="M47 30 q4 6 0 9 q-4 -3 0 -9z" fill="#7cc7ff"/>')
    else:
        s += ('<circle cx="24" cy="41" r="4" fill="#fff" stroke="#111" stroke-width="2"/><circle cx="40" cy="41" r="4" fill="#fff" stroke="#111" stroke-width="2"/>'
              '<circle cx="25" cy="42" r="1.8" fill="#111"/><circle cx="41" cy="42" r="1.8" fill="#111"/>'
              '<line x1="19" y1="33" x2="28" y2="35" stroke="#111" stroke-width="2.5" stroke-linecap="round"/>'
              '<line x1="36" y1="35" x2="45" y2="31" stroke="#111" stroke-width="2.5" stroke-linecap="round"/>'
              '<path d="M24 60 q4 -3 8 0 q4 3 8 0" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
              '<path d="M49 24 q5 7 0 11 q-5 -4 0 -11z" fill="#7cc7ff" stroke="#111" stroke-width="1"/>')
    return s + '</svg>'


def meme(m, mood, cls='', seed='', avoid=None, day=None):
    """Meme con una escena original elegida al azar según el tono (o la fijada en "scene")."""
    md = m.get('mood', mood)
    name = m.get('scene') if m.get('scene') in SCENES else pick(md, seed, avoid, day)
    html_ = (f'<div class="meme {cls}" data-scene="{name}"><span class="tag">{E(m.get("tag",""))}</span>'
             f'<div class="cap">{E(m["top"])}</div>{scene_svg(name)}'
             f'<div class="cap">{E(m["bottom"])}</div></div>')
    return html_, name


V = {'in': ('ENTRAR', 'v-in', 'up'), 'wait': ('ESPERAR', 'v-wait', ''), 'no': ('NO ENTRAR', 'v-no', 'down')}


def build(D):
    css = open(os.path.join(HERE, 'parte.css')).read()
    css = re.sub(r"src:url\(fonts/Anton-Regular\.ttf\)", "src:url(data:font/ttf;base64,%s) format('truetype')" % font('Anton-Regular.ttf'), css)
    css = re.sub(r"src:url\(fonts/Bangers-Regular\.ttf\)", "src:url(data:font/ttf;base64,%s) format('truetype')" % font('Bangers-Regular.ttf'), css)
    # Sin JS: todo visible. Con JS (html.js): pestañas y acordeones.
    css += """
  section{display:block}
  html.js section{display:none} html.js section.on{display:block}
  .stock .body{display:block}
  html.js .stock .body{display:none} html.js .stock.open .body{display:block}
  .chips,.tools,nav{display:none}
  html.js .chips,html.js .tools{display:flex} html.js nav{display:block}
  .wrap{padding-bottom:40px} html.js .wrap{padding-bottom:96px}
  .stock .chev{display:none} html.js .stock .chev{display:inline}
"""
    mood = D['mood']['light']
    seed = f"{D.get('title','parte')}|{D.get('edition','')}"
    try:
        day = date.fromisoformat(D.get('editionDate', ''))
    except ValueError:
        day = None
    m1, n1 = meme(D['meme'], mood, '', seed + '|1', day=day)
    m2, _ = meme(D['meme2'], mood, 'fun', seed + '|2', avoid=n1, day=day)
    out = []
    out.append(f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light">
<title>{E(D.get("title","El Parte de las 7"))} · {E(D["edition"])}</title>
<style>
{css}</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">
      <div class="logo">{E(D.get("title","EL PARTE DE LAS 7").upper())}<small>{E(D.get("subtitle","Para el grupo Traders"))} · {E(D["edition"])}</small></div>
      <div class="tools">
        <button class="toggle" id="themeBtn" title="Tema">🌗 Auto</button>
        <button class="toggle" id="modeBtn" aria-pressed="false">Modo serio</button>
      </div>
    </div>
    {f'<div class="draft">{E(D["draft"])}</div>' if D.get("draft") else ''}
  </header>
''')
    # HOY
    ticks = ''
    for t in D['ticks']:
        c = t['c']
        cls = 'up' if c > 0 else ('down' if c < 0 else 'flat')
        sign = '▲ +' if c > 0 else ('▼ ' if c < 0 else '')
        ticks += f'<div class="tick"><div class="n">{E(t["n"])}</div><div class="v">{E(t["v"])}</div><div class="{cls}">{sign}{str(c).replace(".", ",")}%</div></div>'
    today = ''.join(f'<li>{rich(x)}</li>' for x in D['today'])
    out.append(f'''
  <section id="hoy" class="on">
    <div class="card mood"><div class="mascot">{velito(mood)}</div><div><b>{E(D["mood"]["title"])}</b><p>{E(D["mood"]["text"])}</p></div></div>
    {m1}
    <h2>El mercado ayer</h2>
    <div class="grid">{ticks}</div>
    <div class="note">{E(D.get("ticksNote",""))}</div>
    <h2>Lo que importa hoy</h2>
    <div class="card"><ul class="clean">{today}</ul></div>
    <h2 class="fun">La frase del día</h2>
    <div class="card fun"><div class="quip" style="margin:0">“{E(D["quote"])}”</div></div>
  </section>
''')
    # VALORES
    base_v = date.fromisoformat(D['editionDate'])
    friday = base_v + timedelta(days=4 - base_v.weekday()) if base_v.weekday() < 5 else base_v
    def card(s):
        v15, v1m = V[s['v15']], V[s['v1m']]
        price = f'{E(s["p"])} · ' if s.get('p') and s['p'] != '—' else ''
        cc = str(s.get('c') or {'es': 'ES', 'us': 'US'}.get(s['m'], '')).upper()
        fl = f'<span class="sfl" title="{E(PAISES.get(cc, cc))}">{flag(cc)}</span>' if cc else ''
        return (f'<div class="stock" data-m="{E(s["m"])}" data-v="{E(s["v15"])}" data-r="{1 if s.get("earn") else 0}"><button class="head" aria-expanded="false">'
                f'<div class="nm">{fl}<b>{E(s["n"])}</b>{f'<em class="rz">{E(s["tag"])}</em>' if s.get("tag") else ''}<span>{price}{E(s["ev"])}</span></div>'
                f'<span class="verd {v15[1]}">{v15[0]}</span><span class="chev">›</span></button>'
                f'<div class="body"><p class="why">{E(s["why"])}</p><div class="row2">'
                f'<div class="kv"><small>A 15 días</small><span class="{v15[2]}">{v15[0]}</span></div>'
                f'<div class="kv"><small>A 1 mes</small><span class="{v1m[2]}">{v1m[0]}</span></div>'
                f'<div class="kv" style="grid-column:1/-1"><small>Nivel clave</small><span>{E(s["lvl"])}</span></div></div>'
                f'<p class="quip fun">{E(s["quip"])}</p></div></div>')
    wk = sorted([s for s in D['stocks'] if s.get('earn')], key=lambda s: s['earn'])
    rest = [s for s in D['stocks'] if not s.get('earn')]
    stocks = ''
    if wk:
        stocks += f'<div class="grp">Presentan resultados de {["lunes","martes","miércoles","jueves","viernes"][base_v.weekday()]} a viernes</div>' if base_v < friday else '<div class="grp">Presentan resultados hoy</div>'
        stocks += ''.join(card(s) for s in wk)
        if rest:
            stocks += '<div class="grp">Además en el radar</div>'
    stocks += ''.join(card(s) for s in rest)
    # Aviso si falta en el radar alguna empresa que presenta entre hoy y el viernes
    names = {re.sub(r'\W', '', s['n'].lower()) for s in D['stocks']}
    missing = [e['n'] for e in D.get('earnings', []) if base_v.isoformat() <= e['d'] <= friday.isoformat()
               and re.sub(r'\W', '', e['n'].lower()) not in names]
    if missing:
        print('AVISO: faltan en el radar (presentan de hoy a viernes): ' + ', '.join(missing), file=sys.stderr)
    mk = {s['m'] for s in D['stocks']}
    opts = [('all', 'Todos')] + ([('r', 'Resultados semana')] if wk else []) + [('es', 'España'), ('us', 'EE. UU.')] \
        + ([('eu', 'Europa')] if 'eu' in mk else []) + ([('as', 'Asia')] if 'as' in mk else []) \
        + [('in', 'Entrar ya'), ('wait', 'Esperar'), ('no', 'No entrar')]
    chips = ''.join(f'<button class="chip{" on" if k=="all" else ""}" data-f="{k}">{n}</button>' for k, n in opts)
    out.append(f'''
  <section id="valores">
    <h2>Radar de valores</h2>
    <div class="chips" id="filters">{chips}</div>
    <div id="stocks">{stocks}</div>
    <div class="note">{E(D.get("stocksNote","Veredicto a 15 días / a 1 mes y nivel clave de cada valor."))}</div>
  </section>
''')
    # AGENDA
    base = date.fromisoformat(D['editionDate'])
    evs = ''
    for e in D['events']:
        d = date.fromisoformat(e['d'])
        n = (d - base).days
        cd = 'HOY' if n == 0 else ('MAÑANA' if n == 1 else (f'en {n} días' if n > 1 else 'pasado'))
        evs += (f'<div class="ev{" hot" if e.get("hot") else ""}"><div class="d"><b>{d.day}</b><span>{MESES[d.month-1]}</span></div>'
                f'<div class="t"><b>{E(e["t"])}</b><span>{E(e["s"])}</span><br><span class="cd">{cd}</span></div></div>')
    # Resultados de la semana (opcional: "earnings")
    week = ''
    if D.get('earnings'):
        byday = {}
        for x in D['earnings']:
            byday.setdefault(x['d'], []).append(x)
        for k in sorted(byday):
            d = date.fromisoformat(k)
            n = (d - base).days
            st = 'HOY' if n == 0 else ('MAÑANA' if n == 1 else ('ya publicado' if n < 0 else ''))
            rows = ''
            for x in byday[k]:
                cc = str(x.get('c', '')).upper()
                sub = f'<span>{E(x["s"])}</span>' if x.get('s') else ''
                rows += (f'<div class="er{" hot" if x.get("hot") else ""}"><span class="fl" title="{E(PAISES.get(cc, cc))}">{flag(cc)}</span>'
                         f'<span class="cc">{E(cc)}</span><div class="en"><b>{E(x["n"])}</b>'
                         f'{sub}</div><span class="hr">{E(x.get("h", "sin hora"))}</span></div>')
            week += (f'<div class="eday{" past" if n < 0 else ""}"><div class="dh">{DIAS[d.weekday()]} {d.day} {MESES[d.month-1]}'
                     f'{f" <i>{st}</i>" if st else ""}</div>{rows}</div>')
        week = f'''
    <h2>Resultados de esta semana</h2>
    <div class="card week">{week}</div>
    <div class="note">{E(D.get("earningsNote", "Hora de España. Bandera y siglas: país de la sede de la empresa."))}</div>'''
    out.append(f'''
  <section id="agenda">{week}
    <h2>{"Agenda a 15 días y 1 mes" if D.get("earnings") else "Agenda bursátil"}</h2>
    <div class="card">{evs}</div>
  </section>
''')
    # FONDOS
    plan = ''.join(f'<div style="margin:12px 0"><div style="display:flex;justify-content:space-between"><b>{E(f["b"])}</b><span>{f["w"]}%</span></div>'
                   f'<div class="bar"><i style="width:{f["w"]}%"></i></div><div class="note" style="margin-top:4px">{E(f["t"])}</div></div>' for f in D['fundPlan'])
    funds = ''.join(f'<tr><td><b>{E(f["n"])}</b><br><span class="note">{E(f["isin"])}</span></td><td>{E(f["ter"])}</td><td>{E(f["u"])}</td></tr>' for f in D['funds'])
    out.append(f'''
  <section id="fondos">
    <h2>Rincón del indexado</h2>
    <div class="card"><p style="margin:0 0 6px"><b>Reparto orientativo</b> para quien empieza o aporta ahora:</p>{plan}</div>
    <div class="card"><table><thead><tr><th>Fondo</th><th>TER</th><th>Para</th></tr></thead><tbody>{funds}</tbody></table></div>
    {m2}
  </section>

  <footer>
    <b>ESTO NO ES ASESORAMIENTO FINANCIERO</b>
    Lo escribe una IA con datos públicos. Haz tus propios deberes antes de mover un euro.
  </footer>
</div>

<nav><div class="in" id="tabs">
  <button data-t="hoy" class="on"><span class="ic">☀️</span>Hoy</button>
  <button data-t="valores"><span class="ic">🎯</span>Valores</button>
  <button data-t="agenda"><span class="ic">📅</span>Agenda</button>
  <button data-t="fondos"><span class="ic">🧺</span>Fondos</button>
</div></nav>

<script>
(function(){{
  var R=document.documentElement; R.classList.add('js');
  var $=function(i){{return document.getElementById(i)}};
  function ls(k,v){{try{{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}}catch(e){{return null}}}}
  // Pestañas
  var tabs=['hoy','valores','agenda','fondos'];
  function show(t){{ if(tabs.indexOf(t)<0)t='hoy';
    tabs.forEach(function(x){{$(x).classList.toggle('on',x===t)}});
    [].forEach.call(document.querySelectorAll('#tabs button'),function(b){{b.classList.toggle('on',b.getAttribute('data-t')===t)}});
    window.scrollTo(0,0);}}
  $('tabs').addEventListener('click',function(e){{var b=e.target.closest('button');if(b)show(b.getAttribute('data-t'))}});
  show('hoy');
  // Filtros y acordeones
  $('filters').addEventListener('click',function(e){{var b=e.target.closest('.chip');if(!b)return;var f=b.getAttribute('data-f');
    [].forEach.call(document.querySelectorAll('.chip'),function(c){{c.classList.toggle('on',c===b)}});
    [].forEach.call(document.querySelectorAll('.stock'),function(s){{var ok=f==='all'||s.getAttribute('data-m')===f||s.getAttribute('data-v')===f||(f==='r'&&s.getAttribute('data-r')==='1');s.style.display=ok?'':'none'}});
    [].forEach.call(document.querySelectorAll('.grp'),function(g){{g.style.display=f==='all'?'':'none'}});}});
  $('stocks').addEventListener('click',function(e){{var h=e.target.closest('.head');if(!h)return;var o=h.parentNode.classList.toggle('open');h.setAttribute('aria-expanded',o)}});
  // Tema
  var th=ls('pt-theme')||'auto',order=['auto','light','dark'],nm={{auto:'🌗 Auto',light:'☀️ Claro',dark:'🌙 Oscuro'}};
  function at(){{if(th==='auto')R.removeAttribute('data-theme');else R.setAttribute('data-theme',th);$('themeBtn').textContent=nm[th]}}
  $('themeBtn').addEventListener('click',function(){{th=order[(order.indexOf(th)+1)%3];ls('pt-theme',th);at()}});at();
  // Modo serio
  var se=ls('pt-serio')==='1';
  function am(){{document.body.classList.toggle('serio',se);$('modeBtn').textContent=se?'Modo meme':'Modo serio'}}
  $('modeBtn').addEventListener('click',function(){{se=!se;ls('pt-serio',se?'1':'0');am()}});am();
}})();
</script>
</body>
</html>
''')
    return ''.join(out)


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'parte.html'
    D = json.load(open(src, encoding='utf-8'))
    open(dst, 'w', encoding='utf-8').write(build(D))
    print('OK', dst, os.path.getsize(dst) // 1024, 'KB')

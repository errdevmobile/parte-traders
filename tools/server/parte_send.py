#!/usr/bin/env python3
"""Envía el aviso diario de «El Parte de las 7» al grupo de WhatsApp.

Se ejecuta en el servidor a las 7:00 (hora de Madrid) desde un temporizador
de systemd. Lee data.json de GitHub Pages, comprueba que es de hoy y manda el
mensaje a través del servicio whatsapp-mcp local (http://127.0.0.1:8765/mcp).

Configuración en ~/parte/parte.env:
  GROUP_JID=1203...@g.us     # grupo destino
  OWNER_PHONE=34600000000    # tu número, para avisarte si algo falla
  PAGE_URL=https://errdevmobile.github.io/parte-traders/

Uso:
  python3 parte_send.py                 # envío normal
  python3 parte_send.py --dry-run       # solo muestra el mensaje
  python3 parte_send.py --to 346...     # envía a otro destinatario (pruebas)
  python3 parte_send.py --any-date      # no exige que el parte sea de hoy
"""
import argparse, datetime, json, os, re, sys, time, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
MCP = os.environ.get('WHATSAPP_MCP_URL', 'http://127.0.0.1:8765')


def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def log(*a):
    print(datetime.datetime.now().strftime('%H:%M:%S'), *a, flush=True)


def http(url, data=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'User-Agent': 'parte-traders/1.0',
        'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode('utf-8', 'replace')


def fetch_data(page_url):
    url = page_url.rstrip('/') + '/data.json?t=%d' % int(time.time())
    _, body = http(url)
    return json.loads(body)


def mcp_call(tool, args):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                          'params': {'name': tool, 'arguments': args}}).encode()
    status, body = http(MCP + '/mcp', payload, timeout=60)
    env = None
    try:
        env = json.loads(body)
    except ValueError:  # respuesta en formato SSE
        for line in body.splitlines():
            line = line.strip()
            if line.startswith('data:'):
                try:
                    env = json.loads(line[5:].strip())
                    break
                except ValueError:
                    pass
    if env is None:
        raise RuntimeError('Respuesta MCP ilegible (%s): %s' % (status, body[:300]))
    if env.get('error'):
        raise RuntimeError('Error MCP: %s' % env['error'].get('message'))
    res = env.get('result', {})
    text = ''.join(c.get('text', '') for c in res.get('content', []))
    if res.get('isError'):
        raise RuntimeError('WhatsApp rechazó el envío: %s' % text[:300])
    return text


def wait_ready(max_wait=180):
    t0 = time.time()
    while time.time() - t0 < max_wait:
        try:
            status, _ = http(MCP + '/readyz', timeout=10)
            if status == 200:
                return True
        except Exception:
            pass
        time.sleep(10)
    return False


def strip_html(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()


def compose(D, page_url):
    icon = {'g': '🟢', 'a': '🟡', 'r': '🔴'}.get(D['mood'].get('light'), '🟡')
    lines = ['☀️ *EL PARTE DE LAS 7* · %s' % D['edition'],
             '%s *%s*' % (icon, D['mood']['title']),
             D['mood']['text'], '']
    for item in D.get('today', [])[:2]:
        lines.append('📌 ' + strip_html(item))
    meme = D.get('meme') or {}
    if meme.get('top'):
        lines += ['', '😂 %s / %s' % (meme['top'], meme.get('bottom', ''))]
    lines += ['', '👉 Parte completo: ' + page_url, '_No es asesoramiento financiero._']
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--to')
    ap.add_argument('--any-date', action='store_true')
    ap.add_argument('--env', default=os.path.join(HERE, 'parte.env'))
    a = ap.parse_args()

    cfg = load_env(a.env)
    page = cfg.get('PAGE_URL', 'https://errdevmobile.github.io/parte-traders/')
    group = a.to or cfg.get('GROUP_JID')
    owner = cfg.get('OWNER_PHONE')
    today = datetime.datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat()

    # 1) Esperar a que el parte de hoy esté publicado (hasta ~16 minutos)
    D, last_err = None, ''
    for attempt in range(9):
        try:
            D = fetch_data(page)
            if a.any_date or D.get('editionDate') == today:
                break
            last_err = 'el parte publicado es del %s' % D.get('editionDate')
        except Exception as e:  # red, JSON, etc.
            last_err = str(e)
        D = None
        log('Parte de hoy aún no disponible (%s). Reintento en 2 min.' % last_err)
        time.sleep(120)

    if D is None:
        msg = '⚠️ Hoy el parte no se ha actualizado (%s). No he enviado nada al grupo.' % last_err
        log(msg)
        notify_owner(owner, msg, a.dry_run)
        return 1

    text = compose(D, page)
    if a.dry_run:
        print(text)
        return 0
    if not group:
        log('Falta GROUP_JID en %s' % a.env)
        return 1

    # 2) Esperar a que WhatsApp esté conectado y enviar
    if not wait_ready():
        log('whatsapp-mcp no está listo (¿sesión caducada? vuelve a vincular con login).')
        return 1
    try:
        mcp_call('send_message', {'recipient': group, 'message': text})
        log('Enviado a', group)
        return 0
    except Exception as e:
        log('Fallo al enviar:', e)
        notify_owner(owner, '⚠️ No he podido enviar el parte al grupo: %s' % e, a.dry_run)
        return 1


def notify_owner(owner, msg, dry):
    if not owner or dry:
        return
    try:
        mcp_call('send_message', {'recipient': owner, 'message': msg})
    except Exception as e:
        log('Tampoco he podido avisarte:', e)


if __name__ == '__main__':
    sys.exit(main())

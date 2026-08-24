#!/usr/bin/env python3
"""Fruit Ninja — servidor PWA (só stdlib).
Escolhe a primeira porta livre começando em 8080.
Uso: python3 server.py [porta inicial]
"""
import http.server
import random
import socket
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).parent
START_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
MAX_TRIES = 20

CY = '\033[96m'; YE = '\033[93m'; GR = '\033[92m'; DI = '\033[2m'; RS = '\033[0m'

TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.json': 'application/manifest+json',
    '.js':   'text/javascript',
    '.png':  'image/png',
    '.ico':  'image/x-icon',
}

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, **TYPES}

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def log_message(self, fmt, *args):
        # log limpo: só GET/POST com status e caminho
        path = args[0].split('?')[0].split(' ')[-1]
        code = args[1]
        color = GR if str(code).startswith('2') else YE
        sys.stdout.write(f'  {DI}{self.address_string()}{RS}  {color}{code}{RS}  {path}\n')

def find_port(start):
    for port in range(start, start + MAX_TRIES):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                print(f'  {YE}· porta {port} ocupada{RS}')
    # nenhuma pré-definida livre: pede uma aleatória pro SO
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('0.0.0.0', 0))
        port = s.getsockname()[1]
        print(f'  {YE}· usando porta aleatória {port}{RS}')
        return port

def lan_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    port = find_port(START_PORT)
    ip = lan_ip()
    print(f'''
{CY}  🗡️  FRUIT NINJA{RS}
  {DI}servidor PWA · sem dependências{RS}

  {GR}➜ Local{RS}  http://localhost:{port}
  {GR}➜ Celular{RS} http://{ip}:{port}

  {DI}Ctrl+C para sair{RS}''')
    try:
        with Server(('0.0.0.0', port), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n  tchau! 👋')

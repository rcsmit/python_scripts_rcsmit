"""
Lokale webserver voor kassabonnen.html
Zet dit bestand in dezelfde map als kassabonnen.html en receipts.db

Gebruik:
    python serve.py

Dan open je browser op http://localhost:8765

# version : 20260526-115000 - Initial version: local dev server for kassabonnen
"""

current_version = "20260526-115000"

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8765
FOLDER = Path(__file__).parent   # serve from same folder as this script


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FOLDER), **kwargs)

    def log_message(self, fmt, *args):
        # suppress noisy 304/favicon lines, keep errors
        if args and str(args[1]) not in ("200", "304", "404"):
            super().log_message(fmt, *args)
        elif str(args[1]) == "200":
            super().log_message(fmt, *args)

    def end_headers(self):
        # Required for sql.js WASM to load cross-origin
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()


if __name__ == "__main__":
    os.chdir(FOLDER)
    url = f"http://localhost:{PORT}/kassabonnen.html"

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✅  Server draait op {url}")
        print(f"📁  Serveert bestanden vanuit: {FOLDER}")
        print(f"⏹   Stop met Ctrl+C\n")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer gestopt.")

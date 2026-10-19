"""零依赖的本地 Web 服务：JSON API + 静态页面。"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from .models import Store
from .search import search as do_search

_STATIC = os.path.join(os.path.dirname(__file__), "web", "static")

_CTYPE = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


class Handler(BaseHTTPRequestHandler):
    store: Store = None  # 由 serve() 注入

    def _json(self, obj, code: int = 200) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, name: str) -> None:
        fp = os.path.join(_STATIC, os.path.basename(name))
        if not os.path.exists(fp):
            self._json({"error": "not found"}, 404)
            return
        with open(fp, "rb") as f:
            data = f.read()
        ext = os.path.splitext(fp)[1]
        self.send_response(200)
        self.send_header("Content-Type", _CTYPE.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self._static("index.html")
        elif path.startswith("/static/"):
            self._static(path[len("/static/"):])
        elif path == "/api/notes":
            self._json([n.to_dict() for n in self.store.all()])
        elif path.startswith("/api/search"):
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            self._json(do_search(self.store, q, 10))
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/api/notes":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            n = self.store.add(
                data.get("title", ""), data.get("content", ""), data.get("tags", [])
            )
            self._json(n.to_dict(), 201)
        else:
            self._json({"error": "not found"}, 404)

    def log_message(self, *args):
        return  # 静默


def serve(store: Store, host: str = "127.0.0.1", port: int = 8000) -> None:
    Handler.store = store
    srv = ThreadingHTTPServer((host, port), Handler)
    print(f"Vellum 已启动：http://{host}:{port}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()

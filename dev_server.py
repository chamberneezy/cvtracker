#!/usr/bin/env python3
"""Local dev server with no-cache headers and auto-reload on file change.

Polls the project directory for the newest file mtime; any HTML page it
serves gets a tiny injected script that polls /__reload_check and reloads
the page as soon as something on disk changes. No external dependencies.
"""

import json
import os
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

LIVERELOAD_SNIPPET = b"""
<script>
(function(){
  var last = null;
  setInterval(function(){
    fetch('/__reload_check').then(function(r){return r.json();}).then(function(data){
      if (last !== null && data.mtime !== last) location.reload();
      last = data.mtime;
    }).catch(function(){});
  }, 700);
})();
</script>
"""


def latest_mtime(root):
    latest = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for name in filenames:
            if name.startswith('.'):
                continue
            path = os.path.join(dirpath, name)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            if mtime > latest:
                latest = mtime
    return latest


class DevHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path == '/__reload_check':
            body = json.dumps({'mtime': latest_mtime('.')}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            for index in ('index.html', 'index.htm'):
                candidate = os.path.join(path, index)
                if os.path.exists(candidate):
                    path = candidate
                    break

        if path.endswith('.html') and os.path.isfile(path):
            with open(path, 'rb') as f:
                content = f.read()
            idx = content.lower().rfind(b'</body>')
            if idx != -1:
                content = content[:idx] + LIVERELOAD_SNIPPET + content[idx:]
            else:
                content += LIVERELOAD_SNIPPET
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        super().do_GET()

    def log_message(self, format, *args):
        if self.path == '/__reload_check':
            return
        super().log_message(format, *args)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(('', port), DevHandler)
    print(f"Serving with live-reload on http://localhost:{port}")
    server.serve_forever()

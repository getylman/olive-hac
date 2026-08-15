#!/usr/bin/env python3
"""Vibecoding preview server.

Usage:  python3 preview/serve.py [landing/config.json] [port]
        (defaults: landing/config.json, port 8787)

Serves the repo root, renders the config on start, and re-renders automatically
whenever the config / render.py / saved CSS change. Open http://localhost:8787/
for a 390x844 mobile frame side by side with a full-width desktop view; both
auto-reload on change.
"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "preview"))
import render  # noqa: E402

CONFIG = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "landing" / "config.json"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8787

WATCH = [CONFIG, REPO / "preview" / "render.py",
         REPO / "research" / "client.css", REPO / "research" / "landing.css"]

_last_stamp = 0.0


def stamp():
    return max((p.stat().st_mtime for p in WATCH if p.exists()), default=0.0)


def rerender_if_stale():
    global _last_stamp
    s = stamp()
    if s != _last_stamp:
        try:
            render.build(CONFIG)
            print(f"  re-rendered ({CONFIG.name} changed)")
        except Exception as e:  # keep serving the old output; report in console
            print(f"  RENDER ERROR: {e}")
        _last_stamp = s
    return _last_stamp


FRAME = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>gosura vibecoding</title>
<style>
  body{margin:0;background:#20242A;color:#E8EAED;font:13px/1.4 ui-monospace,Menlo,Consolas,monospace;
    display:flex;gap:24px;padding:20px;height:100vh;box-sizing:border-box;overflow:hidden}
  .col{display:flex;flex-direction:column;gap:10px;min-width:0}
  .col--mob{flex:0 0 auto}
  .col--desk{flex:1 1 auto}
  .lbl{color:#9AA0A6;text-transform:uppercase;letter-spacing:.08em;font-size:11px}
  .lbl b{color:#C4F139}
  .device{width:390px;height:844px;max-height:calc(100vh - 70px);border-radius:28px;
    border:10px solid #0C0E10;box-shadow:0 20px 60px rgba(0,0,0,.5);overflow:hidden;background:#fff}
  .device iframe{width:390px;height:100%;border:0}
  .desk{flex:1;border-radius:10px;border:1px solid #3A4048;overflow:hidden;background:#fff}
  .desk iframe{width:100%;height:100%;border:0}
  .foot{color:#9AA0A6;font-size:11px}
</style></head><body>
  <div class="col col--mob">
    <div class="lbl">mobile <b>390 × 844</b> — the viewport that matters</div>
    <div class="device"><iframe id="m" src="/preview/out/index.html"></iframe></div>
  </div>
  <div class="col col--desk">
    <div class="lbl">desktop / full width</div>
    <div class="desk"><iframe id="d" src="/preview/out/index.html"></iframe></div>
    <div class="foot">auto-reload: watches landing config + render.py + saved CSS ·
      edit &amp; save → both frames refresh</div>
  </div>
<script>
  let v=null;
  setInterval(async()=>{
    try{
      const r=await fetch('/__version',{cache:'no-store'});
      const t=await r.text();
      if(v===null){v=t;return}
      if(t!==v){v=t;m.contentWindow.location.reload();d.contentWindow.location.reload();}
    }catch(e){}
  },1000);
</script>
</body></html>"""


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            body = FRAME.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/__version"):
            body = str(rerender_if_stale()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, fmt, *args):  # quiet static noise, keep errors
        if "__version" not in (args[0] if args else ""):
            super().log_message(fmt, *args)


def main():
    rerender_if_stale()
    server = ThreadingHTTPServer(("127.0.0.1", PORT),
                                 lambda *a, **kw: Handler(*a, directory=str(REPO), **kw))
    print(f"vibecoding preview: http://localhost:{PORT}/  (config: {CONFIG})")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

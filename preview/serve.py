#!/usr/bin/env python3
"""Vibecoding preview server.

Usage:  python3 preview/serve.py [landing/config.json] [port]
        (defaults: landing/config.json, port 8787)

Renders the config on start and re-renders automatically whenever the config /
render.py / saved CSS change. Open http://localhost:8787/ for a 390x844 mobile
frame side by side with a full-width desktop view; both auto-reload on change.

Serving is **allowlisted**: only `preview/out/` (the render output) and the two
`research/` stylesheets the render links are reachable. Everything else in the
repo — `.git/`, `.claude/`, `landing/`, `tools/` — returns 404.
"""
import argparse
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "preview"))
import render  # noqa: E402

DEFAULT_PORT = 8787

# --- what the preview is allowed to serve -----------------------------------
# The render output lives in preview/out/ and links ../../research/*.css, which
# resolves to /research/*.css over HTTP — so exactly those two files, no more.
OUT_DIR = (REPO / "preview" / "out").resolve()
ALLOWED_FILES = {(REPO / "research" / "client.css").resolve(),
                 (REPO / "research" / "landing.css").resolve()}

CONFIG = REPO / "landing" / "config.json"

_last_stamp = 0.0


def watch_paths():
    return [CONFIG, REPO / "preview" / "render.py",
            REPO / "research" / "client.css", REPO / "research" / "landing.css"]


def stamp():
    return max((p.stat().st_mtime for p in watch_paths() if p.exists()), default=0.0)


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
    def _send(self, body, ctype, no_store=False):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        if no_store:
            self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _is_allowed(self, path):
        """True only for the render output and the two stylesheets it links."""
        try:
            # translate_path() already strips the query, unquotes and collapses
            # '..'; resolve() additionally refuses to follow symlinks out.
            fs = Path(self.translate_path(path)).resolve()
        except OSError:
            return False
        if fs in ALLOWED_FILES:
            return True
        return fs == OUT_DIR or OUT_DIR in fs.parents

    def _route(self):
        """Handle the synthetic routes; return True if the request is done."""
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("/", "/index.html"):
            self._send(FRAME.encode(), "text/html; charset=utf-8")
            return True
        if path == "/__version":
            self._send(str(rerender_if_stale()).encode(), "text/plain", no_store=True)
            return True
        if not self._is_allowed(self.path):
            self.send_error(404, "Not Found")
            return True
        return False

    def do_GET(self):
        if not self._route():
            super().do_GET()

    def do_HEAD(self):
        if not self._route():
            super().do_HEAD()

    def list_directory(self, path):  # never expose directory indexes
        self.send_error(404, "Not Found")
        return None

    def log_message(self, fmt, *args):  # quiet static noise, keep errors
        # log_error() passes an int code as args[0], so never assume a string:
        # the old `"__version" not in args[0]` raised TypeError and killed the
        # connection mid-404.
        if "__version" not in (str(args[0]) if args else ""):
            super().log_message(fmt, *args)


def port_arg(value):
    try:
        port = int(value, 10)
    except ValueError:
        raise argparse.ArgumentTypeError(f"port must be a whole number, got {value!r}")
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(f"port must be between 1 and 65535, got {port}")
    return port


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="preview/serve.py",
        description="Local preview server for the landing config (127.0.0.1 only).",
        epilog="Serves preview/out/ and research/{client,landing}.css — nothing else.")
    parser.add_argument("config", nargs="?", default=str(CONFIG),
                        help="landing config to render (default: landing/config.json)")
    parser.add_argument("port", nargs="?", type=port_arg, default=DEFAULT_PORT,
                        help=f"TCP port, 1-65535 (default: {DEFAULT_PORT})")
    args = parser.parse_args(argv)
    if not Path(args.config).is_file():
        parser.error(f"config not found: {args.config}")
    return args


def main(argv=None):
    global CONFIG
    args = parse_args(argv)
    CONFIG = Path(args.config)

    rerender_if_stale()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port),
                                     lambda *a, **kw: Handler(*a, directory=str(REPO), **kw))
    except OSError as e:
        print(f"cannot bind 127.0.0.1:{args.port} — {e}", file=sys.stderr)
        return 1
    print(f"vibecoding preview: http://localhost:{args.port}/  (config: {CONFIG})")
    print("serving preview/out/ + research/client.css + research/landing.css only")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

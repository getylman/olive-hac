#!/usr/bin/env python3
"""Olive MCP client — thin CLI over the landings MCP endpoint.

Usage:
  ./tools/olive.py list-tools
  ./tools/olive.py call <tool> '<json-args>'
  ./tools/olive.py show <slug>
  ./tools/olive.py save <slug> <file> [--label L] [--status draft|active|archive]
  ./tools/olive.py activate <version_id>

`save` and `activate` also accept `--dry-run`: print exactly what would be sent and
exit without touching the network — the way to check argument parsing without
writing a version.

The endpoint (token and all) comes from $OLIVE_MCP_URL — it is a credential, so it
never lives in the repo, and error messages mask it. Export it before using this tool.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

STATUSES = ("draft", "active", "archive")
TIMEOUT = 90
UA = (
    # the edge WAF rejects the default urllib agent with 403
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

_id = [0]


def endpoint():
    """The MCP URL, or a clean error. Resolved per request, never at import."""
    url = os.environ.get("OLIVE_MCP_URL")
    if not url:
        raise SystemExit(
            "OLIVE_MCP_URL is not set — export the landings MCP endpoint\n"
            "  export OLIVE_MCP_URL='https://olive.kz/mcp/landings/<token>'"
        )
    return url


def safe_url(url):
    """The endpoint with its token segment masked — errors must never leak it."""
    head, sep, _token = url.rstrip("/").rpartition("/")
    return head + sep + "<token>" if sep else url


def snippet(text, limit=500):
    flat = " ".join(text.split())
    return flat[:limit] + ("…" if len(flat) > limit else "")


def iter_sse_data(raw):
    """Yield each SSE event's data payload, in order (RFC-ish: `data:` lines join
    with newlines, a blank line dispatches the event, `:` lines are comments)."""
    data = []
    for line in raw.splitlines():
        if not line.strip():
            if data:
                yield "\n".join(data)
                data = []
            continue
        if line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        if field == "data":
            data.append(value[1:] if value.startswith(" ") else value)
    if data:
        yield "\n".join(data)


def decode_response(raw, want_id=None):
    """Return the JSON-RPC document in `raw`, or None if there is none.

    The live endpoint answers with plain JSON; the SSE branch is defensive. It
    iterates every event and returns the first that carries a result/error (the
    one whose id matches, when we know it), so keep-alives, notifications and
    progress events no longer hide the real answer the way taking only the first
    `data:` line did.
    """
    head = raw.lstrip()
    if not head.startswith(("event:", "data:", ":")):
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return doc if isinstance(doc, dict) else None

    fallback = None
    for payload in iter_sse_data(raw):
        try:
            doc = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict) or ("result" not in doc and "error" not in doc):
            continue
        if want_id is None or doc.get("id") == want_id:
            return doc
        if fallback is None:
            fallback = doc
    return fallback


def http_error_message(exc, url):
    """Turn an HTTPError into the clean `MCP error:` path, keeping its body."""
    try:
        body = exc.read().decode("utf-8", "replace")
    except Exception:
        body = ""
    lines = ["MCP error: HTTP %s %s from %s" % (exc.code, exc.reason, safe_url(url))]
    doc = decode_response(body) if body.strip() else None
    if isinstance(doc, dict) and "error" in doc:
        lines.append("  " + json.dumps(doc["error"], ensure_ascii=False))
    elif body.strip():
        lines.append("  body: " + snippet(body))
    else:
        lines.append("  (empty response body)")
    if exc.code in (401, 403):
        lines.append("  check $OLIVE_MCP_URL — the token may be wrong, expired or revoked")
    return "\n".join(lines)


def rpc(method, params=None):
    url = endpoint()
    _id[0] += 1
    want_id = _id[0]
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": want_id, "method": method, "params": params or {}}
    ).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise SystemExit(http_error_message(exc, url))
    except urllib.error.URLError as exc:
        raise SystemExit("MCP error: cannot reach %s — %s" % (safe_url(url), exc.reason))
    except TimeoutError:
        raise SystemExit("MCP error: %s did not answer within %ss" % (safe_url(url), TIMEOUT))

    doc = decode_response(raw, want_id)
    if doc is None:
        raise SystemExit(
            "MCP error: could not parse the response from %s\n  body: %s"
            % (safe_url(url), snippet(raw))
        )
    if "error" in doc:
        raise SystemExit("MCP error: " + json.dumps(doc["error"], ensure_ascii=False))
    if "result" not in doc:
        raise SystemExit("MCP error: response carries neither result nor error\n  " + snippet(raw))
    return doc["result"]


def call(tool, args=None):
    res = rpc("tools/call", {"name": tool, "arguments": args or {}})
    out = []
    for part in res.get("content", []):
        if part.get("type") == "text":
            out.append(part["text"])
    text = "\n".join(out)
    if res.get("isError"):
        raise SystemExit("TOOL ERROR: " + text)
    try:
        return json.loads(text)
    except Exception:
        return text


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def parse_json_args(text):
    try:
        args = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit("invalid JSON arguments: %s\n  got: %s" % (exc, snippet(text, 200)))
    if not isinstance(args, dict):
        raise SystemExit(
            "JSON arguments must be an object, got %s: %s" % (type(args).__name__, snippet(text, 200))
        )
    return args


def read_config(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise SystemExit("no such config file: " + path)
    except IsADirectoryError:
        raise SystemExit("not a file: " + path)
    except OSError as exc:
        raise SystemExit("cannot read %s: %s" % (path, exc))
    except json.JSONDecodeError as exc:
        raise SystemExit("invalid JSON in %s: %s" % (path, exc))


def dry_run(tool, params):
    shown = dict(params)
    config = shown.get("config")
    if isinstance(config, dict):
        shown["config"] = "<%d section(s), %d bytes>" % (
            len(config.get("sections") or []),
            len(json.dumps(config, ensure_ascii=False)),
        )
    print("DRY RUN — nothing sent.\n  tool: %s\n  args: %s"
          % (tool, dump(shown).replace("\n", "\n  ")))


def build_parser():
    p = argparse.ArgumentParser(
        prog="olive.py",
        description="Thin CLI over the Olive landings MCP endpoint.",
        epilog="$OLIVE_MCP_URL must be exported; it carries the token, so it never lives in the repo.",
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="command")

    sub.add_parser("list-tools", help="list the tools the endpoint exposes")

    c = sub.add_parser("call", help="call a tool with JSON arguments")
    c.add_argument("tool")
    c.add_argument("args", nargs="?", default="{}", metavar="JSON",
                   help="JSON object of arguments (default: {})")

    s = sub.add_parser("show", help="show a landing and its versions")
    s.add_argument("slug")

    sv = sub.add_parser("save", help="save a new version (draft by default)")
    sv.add_argument("slug")
    sv.add_argument("file", metavar="FILE", help="config JSON to upload")
    sv.add_argument("--label", default="auto", metavar="L", help="version label (default: auto)")
    sv.add_argument("--status", default="draft", choices=STATUSES,
                    help="version status (default: draft)")
    sv.add_argument("--dry-run", action="store_true",
                    help="print what would be sent and exit; no network call")

    a = sub.add_parser("activate", help="make a version live")
    a.add_argument("version_id", type=int)
    a.add_argument("--dry-run", action="store_true",
                   help="print what would be sent and exit; no network call")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.cmd == "list-tools":
        for t in rpc("tools/list")["tools"]:
            first = ((t.get("description") or "").splitlines() or [""])[0]
            print(f"{t['name']:22} {first}")
        return

    if args.cmd == "call":
        print(dump(call(args.tool, parse_json_args(args.args))))
        return

    if args.cmd == "show":
        print(dump(call("landing_show", {"slug": args.slug})))
        return

    if args.cmd == "save":
        params = {
            "slug": args.slug,
            "config": read_config(args.file),
            "label": args.label,
            "status": args.status,
        }
        if args.dry_run:
            return dry_run("landing_save_version", params)
        print(dump(call("landing_save_version", params)))
        return

    if args.cmd == "activate":
        params = {"version_id": args.version_id}
        if args.dry_run:
            return dry_run("landing_activate", params)
        print(dump(call("landing_activate", params)))
        return


if __name__ == "__main__":
    main()

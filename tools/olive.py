#!/usr/bin/env python3
"""Olive MCP client — thin CLI over the landings MCP endpoint.

Usage:
  ./tools/olive.py list-tools
  ./tools/olive.py call <tool> '<json-args>'
  ./tools/olive.py show gosura
  ./tools/olive.py save gosura landing/config.json --label "v2" [--status draft|active]
  ./tools/olive.py activate <version_id>

The endpoint (token and all) comes from $OLIVE_MCP_URL — it is a credential, so it
never lives in the repo. Export it before using this tool.
"""
import json
import os
import sys
import urllib.request

URL = os.environ.get("OLIVE_MCP_URL")
if not URL:
    sys.exit(
        "OLIVE_MCP_URL is not set — export the landings MCP endpoint\n"
        "  export OLIVE_MCP_URL='https://olive.kz/mcp/landings/<token>'"
    )

_id = [0]


def rpc(method, params=None):
    _id[0] += 1
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": _id[0], "method": method, "params": params or {}}
    ).encode()
    req = urllib.request.Request(
        URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            # the edge WAF rejects the default urllib agent with 403
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        raw = r.read().decode()
    # endpoint may answer as SSE
    if raw.lstrip().startswith("event:") or raw.lstrip().startswith("data:"):
        for line in raw.splitlines():
            if line.startswith("data:"):
                raw = line[5:].strip()
                break
    doc = json.loads(raw)
    if "error" in doc:
        raise SystemExit("MCP error: " + json.dumps(doc["error"], ensure_ascii=False))
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


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]

    if cmd == "list-tools":
        for t in rpc("tools/list")["tools"]:
            print(f"{t['name']:22} {t.get('description','').splitlines()[0]}")
        return

    if cmd == "call":
        tool = sys.argv[2]
        args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(call(tool, args), ensure_ascii=False, indent=2))
        return

    if cmd == "show":
        print(json.dumps(call("landing_show", {"slug": sys.argv[2]}), ensure_ascii=False, indent=2))
        return

    if cmd == "save":
        slug, path = sys.argv[2], sys.argv[3]
        rest = sys.argv[4:]
        label = "auto"
        status = "draft"
        if "--label" in rest:
            label = rest[rest.index("--label") + 1]
        if "--status" in rest:
            status = rest[rest.index("--status") + 1]
        config = json.load(open(path, encoding="utf-8"))
        res = call(
            "landing_save_version",
            {"slug": slug, "config": config, "label": label, "status": status},
        )
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    if cmd == "activate":
        print(json.dumps(call("landing_activate", {"version_id": int(sys.argv[2])}),
                         ensure_ascii=False, indent=2))
        return

    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

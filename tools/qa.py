#!/usr/bin/env python3
"""QA a rendered gosura landing version against the config that produced it.

Usage:
  python3 tools/qa.py 1069                     # fetch ?v=1069 and check it
  python3 tools/qa.py 1069 --save              # also keep research/preview-v<id>.html
  python3 tools/qa.py --file research/x.html   # check an already-saved render
  python3 tools/qa.py --file x.html --config c.json   # compare against a specific config

Why this exists: `validate.py` checks the config is *legal*; this checks the page
the server actually *built* from it. Those differ — `home_quality` validated fine
and rendered nothing at all. Every check here earned its place by catching a real bug.

Exit 0 = all checks pass, 1 = at least one FAIL.
"""
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 "
             "Mobile/15E148 Safari/604.1")

# Prebuilt server blocks -> a string that must appear if the block really rendered.
# Unknown blocks are skipped with a warning rather than silently assumed fine.
BLOCK_MARKERS = {
    "order_funnel": 'id="orderFunnel"',
    "order_menu": "sf-menu-plans",
    "order_filters": "sf-filters",
    "home_advantages": "sf-features",
    "home_faq": "sf-faq__accordion",
    "home_map": "deliveryMap",
    "home_marquee": "sf-marquee",
    "faq": "accordion",
    "cta": "l-cta",
    "hero": "l-hero",
    "features": "l-features",
    "testimonials": "l-testimonials",
    "text": "l-text",
    "lead_form": "l-lead",
}

# Blocks proven unusable on a landing — configuring them is always a mistake.
KNOWN_BAD = {
    "home_quality": "renders nothing at all on a landing (verified 2026-08-15) — "
                    "use a gs- html block with Olive's published quality claims instead",
    "home_result": "publishes «400 блюд» while the meals API reports 297 — inflated claim",
}

# Claims that must never appear — inflated or unverifiable.
FORBIDDEN = ["400 блюд", "гарантируем", "гарантия результата", "похудеете на"]

# A real attribute, not the bare substring: `[data-cta]{color:red}` in a stylesheet is
# not instrumentation (B1). Both quote styles, value must be non-empty.
CTA_ATTR = re.compile(r"""data-cta\s*=\s*(?:"([^"]+)"|'([^']+)')""")
CODE_BLOCK = re.compile(r"(?is)<(script|style)\b[^>]*>.*?</\1>")
# `/` separates attributes just like whitespace: <div/onclick="…"> executes (B3).
INLINE_HANDLER = re.compile(r"[\s/]on[a-z]+\s*=", re.I)

fails, warns, passes = [], [], []


def strip_code(html):
    """Drop <script>/<style> bodies — an attribute quoted in there is not markup."""
    return CODE_BLOCK.sub(" ", html)


def cta_values(text):
    return [a or b for a, b in CTA_ATTR.findall(text)]


def walk_strings(value, path="props"):
    """Yield (dotted-path, string) for every string anywhere in a props structure."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk_strings(v, f"{path}[{i}]")


def selector_in_render(selector, html):
    """Does the first id/class token of an override selector exist in the render?"""
    tokens = re.findall(r"[#.]([A-Za-z_][\w-]*)", selector)
    if not tokens:
        return True  # element/attribute selectors (e.g. `html`) — nothing cheap to check
    t = tokens[0]
    return (f'id="{t}"' in html) or re.search(
        r'class="[^"]*(?<![\w-])' + re.escape(t) + r'(?![\w-])[^"]*"', html) is not None


def check(ok, label, extra="", fail_hint=""):
    """extra prints either way; fail_hint only when the check fails."""
    (passes if ok else fails).append(label)
    note = extra or ""
    if not ok and fail_hint:
        note = f"{note}; {fail_hint}" if note else fail_hint
    print(("  PASS  " if ok else "  FAIL  ") + label + (f" — {note}" if note else ""))


def warn(label):
    warns.append(label)
    print("  warn  " + label)


def fetch(vid):
    url = f"https://olive.kz/l/gosura?v={vid}"
    req = urllib.request.Request(url, headers={"User-Agent": UA_MOBILE})
    with urllib.request.urlopen(req, timeout=60) as r:
        return url, r.read().decode("utf-8", "replace")


def mcp(tool):
    out = subprocess.run([sys.executable, str(REPO / "tools" / "olive.py"), "call", tool, "{}"],
                         capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except Exception:
        return None


def main():
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit(__doc__)

    if "--file" in argv:
        path = Path(argv[argv.index("--file") + 1])
        html, src = path.read_text(encoding="utf-8", errors="replace"), str(path)
    else:
        vid = argv[0]
        src, html = fetch(vid)
        if "--save" in argv:
            (REPO / "research" / f"preview-v{vid}.html").write_text(html, encoding="utf-8")

    cfg_path = (Path(argv[argv.index("--config") + 1]) if "--config" in argv
                else REPO / "landing" / "config.json")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    sections = cfg.get("sections", [])

    print(f"=== QA {src} ({len(html)} bytes) ===\n--- structure ---")

    title = re.search(r"<title>(.*?)</title>", html, re.S)
    title = title.group(1).strip() if title else ""
    check(bool(title) and title != "Gosura", "page title is set and not the default", repr(title))

    h1 = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    check(len(h1) == 1, "exactly one <h1>", f"{len(h1)} found")

    # --- every configured section actually produced output (the home_quality bug) ---
    print("--- did each section actually render? ---")
    for i, sec in enumerate(sections):
        t = sec.get("type")
        if t in KNOWN_BAD:
            check(False, f"sections[{i}] {t} is a known-bad block", fail_hint=KNOWN_BAD[t])
            continue
        if t == "html":
            content = sec.get("props", {}).get("content", "")
            m = re.search(r'class="(gs-[\w-]+)', content)
            marker = m.group(1) if m else None
            if not marker:
                warn(f"sections[{i}] html: no gs- class to verify by")
                continue
            check(marker in html, f"sections[{i}] html .{marker} rendered")
        elif t in BLOCK_MARKERS:
            check(BLOCK_MARKERS[t] in html, f"sections[{i}] {t} rendered",
                  fail_hint=f"marker {BLOCK_MARKERS[t]!r} missing — this block renders "
                            f"nothing on a landing (see home_quality); replace it")
        else:
            warn(f"sections[{i}] {t}: no known marker, not verified")

    # --- conversion instrumentation: the platform counts [data-cta] only ---
    # B1: this used to be `html.count("data-cta")`, which matches the substring anywhere.
    # A page whose only occurrence was `[data-cta]{color:red}` in CSS — with zero real
    # attributes — printed "PASS … 1 found", green-lighting the exact CR-0 failure this
    # tool exists to prevent. Count attributes, and only outside <script>/<style>.
    print("--- tracking ---")
    cta_vals = cta_values(strip_code(html))
    check(bool(cta_vals), "page emits real data-cta attributes (platform counts clicks by this)",
          f"{len(cta_vals)} found",
          fail_hint='no data-cta="…" attribute in the delivered markup — every CTA click on '
                    "this page is invisible to conversion metrics (CR-0)")
    if cta_vals:
        print("        values: " + ", ".join(sorted(set(cta_vals))))
        dupes = sorted({v for v in cta_vals if cta_vals.count(v) > 1})
        if dupes:
            warn(f"duplicate data-cta value(s): {', '.join(dupes)} — clicks merge in reporting")
    ghosts = len(cta_values(html)) - len(cta_vals)
    if ghosts:
        warn(f"{ghosts} data-cta attribute(s) occur only inside <script>/<style> — not counted")

    # --- B2: the whole override layer used to ship completely unchecked ---
    print("--- overrides delivered? ---")
    overrides = (cfg.get("meta") or {}).get("overrides") or []
    m = re.search(r"var\s+rules\s*=\s*(\[.*?\])\s*;", html, re.S)
    embedded = None
    if m:
        try:
            embedded = json.loads(m.group(1))
        except Exception:
            embedded = None

    if not overrides:
        if embedded:
            warn(f"config declares no overrides but the render embeds {len(embedded)} — "
                 "this render was built from a different config")
        else:
            check(True, "config declares no overrides, and none are embedded")
    else:
        check(embedded is not None, "override payload is embedded in the render",
              fail_hint="no `var rules = [...]` applier found — the override layer did not ship")
        if embedded is not None:
            check(len(embedded) == len(overrides),
                  f"all {len(overrides)} configured override rule(s) embedded",
                  f"{len(embedded)} embedded")

    for i, o in enumerate(overrides):
        sel = o.get("selector", "")
        otag = f"overrides[{i}] ({sel})"
        check(selector_in_render(sel, html), f"{otag}: selector matches the render",
              fail_hint="no element with that id/class in the delivered markup — rule is a no-op")
        emb = next((e for e in (embedded or []) if e.get("selector") == sel), None)
        if embedded is not None:
            check(o in embedded, f"{otag}: rule delivered verbatim",
                  fail_hint="embedded payload differs from config — render is from another version")
        # Overrides run once at DOMContentLoaded, so curl can only prove they *shipped*.
        if "text" in o:
            check(bool(emb) and emb.get("text") == o["text"],
                  f"{otag}: text mutation shipped", repr(o["text"][:48]))
        if "addClass" in o:
            check(bool(emb) and emb.get("addClass") == o["addClass"],
                  f"{otag}: addClass {o['addClass']!r} shipped")
        attrs = o.get("attrs")
        if isinstance(attrs, dict):
            for k, v in attrs.items():
                check(bool(emb) and (emb.get("attrs") or {}).get(k) == v,
                      f"{otag}: attrs {k}={v!r} shipped")
                print(f'        browser-check: {sel} must carry {k}="{v}" after DOMContentLoaded')
                if k == "href" and isinstance(v, str) and v.startswith("#"):
                    check(f'id="{v[1:]}"' in html, f"{otag}: href target {v} exists in the page",
                          fail_hint="override would point at a non-existent anchor (the A3 bug)")

    # This round moved every cosmetic OUT of overrides into a static <style class="gs-fixes">
    # block: overrides are a one-shot DCL pass, so they flash on slow mobile and never reach
    # nodes rebuilt by innerHTML (A2/A5).
    declares_fixes = any(s.get("type") == "html" and "gs-fixes" in (s.get("props") or {}).get(
        "content", "") for s in sections)
    if declares_fixes:
        check("gs-fixes" in html, "static gs-fixes style block rendered",
              fail_hint="the migrated cosmetics (header contrast, gift accent) never shipped")
        head_end = html.lower().find("</head>")
        if "gs-fixes" in html and head_end != -1:
            check(html.find("gs-fixes") > head_end,
                  "gs-fixes style block sits in <body>, after </head>",
                  fail_hint="rules 1-3 win their ties by source order — head position breaks them")
    else:
        warn("config declares no gs-fixes static style block — cosmetics would rely on the "
             "DOMContentLoaded override pass (flashes; misses innerHTML-rebuilt nodes)")
    n_cosmetic = sum(1 for o in overrides if "style" in o)
    if n_cosmetic:
        warn(f"{n_cosmetic} override(s) still carry cosmetic `style` — these cannot reach "
             "nodes injected after DOMContentLoaded (A2); prefer static CSS")

    # --- order machinery intact ---
    print("--- order flow ---")
    check('id="orderFunnel"' in html or 'id="order"' in html, "an order block is present")
    check("epay.homebank.kz" in html or "send-code" in html, "payment/verification wiring present")

    # --- truthfulness ---
    print("--- truthfulness ---")
    for bad in FORBIDDEN:
        check(bad not in html, f"no forbidden claim {bad!r}")
    ov = mcp("overview")
    if ov:
        cust, orders, meals = ov["customers"], ov["orders"]["total"], ov["meals"]
        for num, label in ((cust, "customers"), (orders, "orders"), (meals, "dishes")):
            spaced = f"{num:,}".replace(",", " ")
            if str(num) in html or spaced in html:
                check(True, f"{label} figure {num} matches live API")
        stale = re.findall(r"\b(\d{3,5})\s+(?:клиент|заказ)", html)
        for s in stale:
            if int(s.replace(" ", "")) not in (cust, orders):
                warn(f"number {s} near клиент/заказ does not match API ({cust}/{orders})")
    else:
        warn("could not reach overview API to cross-check numbers")

    # --- hygiene ---
    print("--- hygiene ---")
    check("fonts.googleapis" not in html and "cdn.jsdelivr" not in html,
          "no external font/CDN introduced")
    # B3/B4 mirror: `/` also separates attributes (<div/onclick=…>), and markup lives in
    # more props than html.content (text.body, faq/testimonials items).
    handlers = []
    for i, sec in enumerate(sections):
        for path, val in walk_strings(sec.get("props") or {}):
            mh = INLINE_HANDLER.search(val)
            if mh:
                handlers.append(f"sections[{i}] {path} ({mh.group(0).strip()})")
    check(not handlers, "no inline on* handlers in our content", "; ".join(handlers))

    print(f"\n=== {len(passes)} passed, {len(fails)} failed, {len(warns)} warning(s) ===")
    if fails:
        print("FAILED:")
        for f in fails:
            print("  - " + f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

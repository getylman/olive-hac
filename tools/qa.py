#!/usr/bin/env python3
"""QA a rendered gosura landing version against the config that produced it.

Usage:
  python3 tools/qa.py 1069                     # fetch ?v=1069 and check it
  python3 tools/qa.py 1069 --save              # also keep research/preview-v<id>.html
  python3 tools/qa.py --file research/x.html   # check an already-saved render

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

fails, warns, passes = [], [], []


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

    cfg_path = REPO / "landing" / "config.json"
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
    print("--- tracking ---")
    n_cta = html.count("data-cta")
    check(n_cta > 0, "page emits data-cta (platform counts clicks by this)", f"{n_cta} found")
    print("        values: " + ", ".join(sorted(set(re.findall(r'data-cta="([^"]+)"', html)))))

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
    for sec in sections:
        c = sec.get("props", {}).get("content", "") if sec.get("type") == "html" else ""
        if re.search(r"\son\w+\s*=", c):
            check(False, "html block contains inline on* handler")
            break
    else:
        check(True, "no inline on* handlers in our html blocks")

    print(f"\n=== {len(passes)} passed, {len(fails)} failed, {len(warns)} warning(s) ===")
    if fails:
        print("FAILED:")
        for f in fails:
            print("  - " + f)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

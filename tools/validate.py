#!/usr/bin/env python3
"""Validate a gosura landing config BEFORE any MCP save.

Usage:  python3 tools/validate.py [landing/config.json]

Checks (ground truth = research/BRIEF.md + the live block registry):
  * every section `type` exists in the registry, props are registry-declared
  * meta.theme keys are valid and values are #RRGGBB
  * every override has a selector; only legal rule keys; attrs never set
    id / name / data-* / on*; `html` overrides never target the protected
    order-form scope (#order, #order-menu, #orderFunnel, .of, .sf-form)
  * EVERY markup-bearing string prop (not just html.content — also text.body,
    faq/testimonials/features items, …): no external CDN/script/font/image
    imports, no inline on* handlers, no ids colliding with order machinery
Exit code 0 = safe to save, 1 = errors (do not save).
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# ---- block registry (verified via landing_list / research/landings.txt) ----
REGISTRY = {
    "home": [],
    "order": [],
    "order_menu": ["heading", "subheading", "banner"],
    "order_filters": [],
    "order_funnel": ["offer", "hero_title", "hero_sub"],
    "home_map": [],
    "home_faq": [],
    "home_banner": [],
    "home_result": [],
    "home_marquee": [],
    "home_menu": [],
    "home_advantages": [],
    "home_quality": [],
    "home_promo": [],
    "hero": ["heading", "subheading", "image", "cta_text", "cta_href", "align"],
    "text": ["heading", "body", "align"],
    "html": ["content"],
    "features": ["heading", "items"],
    "cta": ["heading", "subheading", "cta_text", "cta_href"],
    "testimonials": ["heading", "items"],
    "faq": ["heading", "items"],
    "lead_form": ["heading", "subheading", "button_text"],
}

THEME_KEYS = {"primary", "primaryHover", "primaryDark", "ink", "bgSoft", "bgAccent"}
OVERRIDE_KEYS = {"selector", "text", "html", "style", "addClass", "attrs"}
FORBIDDEN_ATTR = re.compile(r"^(id|name|data-.*|on.*)$", re.I)
# protected order-form scope: token followed by non-identifier char
PROTECTED_SEL = re.compile(
    r"(#order(?![A-Za-z0-9])|#orderFunnel(?![A-Za-z0-9])|\.of(?![A-Za-z0-9])|\.sf-form(?![A-Za-z0-9]))"
)
# ids that live INSIDE the form (from research/gosura.html) — html/text overrides on
# them are either rejected server-side or break live price bindings
ORDER_IDS = {
    "order", "order-menu", "orderFunnel", "orderPlan", "orderPriceFrom", "orderPrice",
    "orderReplacementCost", "orderReplacementCostValue", "orderTpCost", "orderTpCostValue",
    "orderDiscount", "orderDiscountValue", "orderPriceTotal", "orderDeliveryDate",
    "orderDeliveryTime", "orderDeliveryEdit", "orderStep1", "orderStep2", "orderStep3",
    "orderBtn", "orderBtnPrice", "promoInput", "promoApplyBtn", "promoRemoveBtn",
    "formComment", "deliveryZoneStatus", "deliveryMap",
}
# "External" = absolute or protocol-relative. `//host/x` loads cross-origin just like
# `https://host/x`, so both forms count. Media tags were missing entirely (B3): a page
# could ship `<img src="https://…">` / `<iframe>` and validate clean.
EXTERNAL_REF = re.compile(
    r"(<script[^>]+src\s*=|"
    r"<link[^>]+href\s*=\s*[\"']?\s*(?:https?:|//)|"
    r"<(?:img|iframe|source|video|audio|embed|object|track|input)\b[^>]*?"
    r"(?:src|srcset|poster|data|href)\s*=\s*[\"']?\s*(?:https?:|//)|"
    r"srcset\s*=\s*[\"'][^\"']*(?:https?:|//)|"
    r"@import\s|@font-face|"
    r"url\(\s*[\"']?\s*(?:https?:|//))", re.I)
# Attributes may be separated by `/` as well as whitespace — `<div/onclick="…">` is valid
# HTML and browsers execute it, but the old `\son…` form missed it (B3).
INLINE_HANDLER = re.compile(r"[\s/]on[a-z]+\s*=", re.I)
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def selector_in_saved_dom(selector, dom):
    """Best-effort: does the first id/class token of the selector exist in the saved page?"""
    tokens = re.findall(r"[#.]([A-Za-z_][\w-]*)", selector)
    if not tokens:
        return True  # element/attr selectors — cannot cheaply verify
    t = tokens[0]
    if t.startswith("gs-"):
        return True  # our own blocks add these
    return (f'id="{t}"' in dom) or re.search(
        r'class="[^"]*(?<![\w-])' + re.escape(t) + r'(?![\w-])[^"]*"', dom) is not None


def check_meta(meta):
    if not isinstance(meta, dict):
        err("meta must be an object")
        return
    for k in meta:
        if k not in {"title", "theme", "overrides"}:
            warn(f"meta.{k}: unknown key (server may ignore it)")
    title = meta.get("title")
    if title is not None and (not isinstance(title, str) or not title.strip()):
        err("meta.title must be a non-empty string")
    if title is None:
        warn('meta.title missing — the tab will show the internal slug ("Gosura")')

    theme = meta.get("theme", {})
    if not isinstance(theme, dict):
        err("meta.theme must be an object")
    else:
        for k, v in theme.items():
            if k not in THEME_KEYS:
                err(f"meta.theme.{k}: unknown token (valid: {', '.join(sorted(THEME_KEYS))})")
            elif not (isinstance(v, str) and HEX.match(v)):
                err(f"meta.theme.{k}: value {v!r} is not #RRGGBB")

    check_overrides(meta.get("overrides", []))


def check_overrides(ovr):
    if not isinstance(ovr, list):
        err("meta.overrides must be an array")
        return
    dom = ""
    saved = REPO / "research" / "gosura.html"
    if saved.exists():
        dom = saved.read_text(encoding="utf-8", errors="replace")
    for i, o in enumerate(ovr):
        tag = f"overrides[{i}]"
        if not isinstance(o, dict):
            err(f"{tag}: must be an object")
            continue
        sel = o.get("selector")
        if not (isinstance(sel, str) and sel.strip()):
            err(f"{tag}: 'selector' is required and must be a non-empty string")
            continue
        tag = f"overrides[{i}] ({sel})"
        for k in o:
            if k not in OVERRIDE_KEYS:
                err(f"{tag}: unknown rule key '{k}' (valid: {', '.join(sorted(OVERRIDE_KEYS))})")
        if not any(k in o for k in ("text", "html", "style", "addClass", "attrs")):
            warn(f"{tag}: no action key — override does nothing")

        attrs = o.get("attrs")
        if attrs is not None:
            if not isinstance(attrs, dict):
                err(f"{tag}: attrs must be an object")
            else:
                for a in attrs:
                    if FORBIDDEN_ATTR.match(a):
                        err(f"{tag}: attrs may never set '{a}' (id/name/data-*/on* carry order logic)")

        style = o.get("style")
        if style is not None and not isinstance(style, (str, dict)):
            err(f"{tag}: style must be a string or object")

        protected = bool(PROTECTED_SEL.search(sel)) or any(
            re.search(r"#" + re.escape(x) + r"(?![\w-])", sel) for x in ORDER_IDS)
        if "html" in o and protected:
            err(f"{tag}: 'html' override targets the protected order scope — "
                "only text/style/addClass apply there (payment structure is protected)")
        if "text" in o and re.search(r"#orderBtn(?![\w-])", sel):
            err(f"{tag}: text-override on #orderBtn would destroy the live "
                "#orderBtnPrice span — restyle or leave it alone")
        if dom and not selector_in_saved_dom(sel, dom):
            warn(f"{tag}: selector not found in research/gosura.html — "
                 "verify it against the live DOM before saving")


def check_sections(sections):
    if not isinstance(sections, list) or not sections:
        err("sections must be a non-empty array")
        return
    for i, s in enumerate(sections):
        tag = f"sections[{i}]"
        if not isinstance(s, dict):
            err(f"{tag}: must be an object")
            continue
        t = s.get("type")
        if t not in REGISTRY:
            err(f"{tag}: unknown type {t!r} — valid types: {', '.join(sorted(REGISTRY))}")
            continue
        tag = f"sections[{i}] <{t}>"
        props = s.get("props", {})
        if props in ([], None):
            props = {}
        if not isinstance(props, dict):
            err(f"{tag}: props must be an object")
            continue
        allowed = REGISTRY[t]
        for p in props:
            if p not in allowed:
                err(f"{tag}: prop '{p}' is not registry-declared "
                    f"(allowed: {', '.join(allowed) or 'none'})")
        if t == "html" and not (isinstance(props.get("content"), str)
                                and props["content"].strip()):
            err(f"{tag}: 'content' is required and must be non-empty HTML")
        # B4: html.content is not the only prop emitted raw — text.body, faq/testimonials
        # items and any other nested string carry markup too. Check every one of them.
        for path, value in walk_strings(props):
            check_markup(f"{tag} {path}", value)


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


def check_markup(tag, content):
    """Content-hygiene checks for any string the renderer may emit as raw markup."""
    if not (isinstance(content, str) and content.strip()):
        return
    m = EXTERNAL_REF.search(content)
    if m:
        err(f"{tag}: external resource reference ({m.group(0).strip()!r}) — "
            "no CDNs, external scripts, or font imports (design system rule)")
    mh = INLINE_HANDLER.search(content)
    if mh:
        err(f"{tag}: inline handler {mh.group(0).strip()!r} found — forbidden "
            "(carries logic; will be rejected)")
    for i in re.findall(r'id="([^"]+)"', content):
        if i in ORDER_IDS:
            err(f"{tag}: content declares id=\"{i}\" which collides with order machinery")
    if re.search(r"\.(sf|of)-[\w-]+\s*\{", content):
        warn(f"{tag}: block CSS styles sf-*/of-* classes — allowed only for deliberate, "
             "reviewed restyles (e.g. .active plan state); keep everything else gs-scoped")
    if "<script" in content.lower():
        warn(f"{tag}: contains <script> — allowed, but it must never write into the "
             "order form; review before saving")


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else REPO / "landing" / "config.json")
    if not path.exists():
        print(f"ERROR: {path} does not exist")
        return 1
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: {path}: invalid JSON — {e}")
        return 1
    if not isinstance(cfg, dict):
        print("ERROR: config root must be an object")
        return 1
    for k in cfg:
        if k not in {"meta", "sections"}:
            warn(f"root.{k}: unknown key")
    check_meta(cfg.get("meta", {}))
    check_sections(cfg.get("sections"))

    for w in warnings:
        print(f"  warn: {w}")
    for e in errors:
        print(f" ERROR: {e}")
    n_sec = len(cfg.get("sections") or [])
    if errors:
        print(f"\nFAIL — {len(errors)} error(s), {len(warnings)} warning(s). Do NOT save.")
        return 1
    print(f"\nOK — {n_sec} sections, {len(warnings)} warning(s). Safe to save as draft.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

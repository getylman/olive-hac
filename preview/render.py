#!/usr/bin/env python3
"""Render landing/config.json to a standalone local HTML preview.

Usage:  python3 preview/render.py [landing/config.json] [preview/out/index.html]

Approximates the real /l/gosura composition: pulls in the saved production CSS
(research/client.css + landing.css), applies meta.theme as CSS variables, renders
every free-form block (hero/text/html/features/cta/testimonials/faq/lead_form)
with the site's real l-* classes, and renders labelled PLACEHOLDER boxes for
server-only blocks (order_*, home_*) that only exist server-side.
meta.overrides are applied client-side by a small script that mirrors the
server's rules (html never applied inside the protected order scope).
"""
import html as H
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SERVER_ONLY = {
    "home": "Главная целиком (все секции + заказ)",
    "order": "Полный блок заказа (планы, календарь, меню, оформление)",
    "order_menu": "Заказ: планы + меню блюд + форма",
    "order_filters": "Заказ: фильтры предпочтений + модалки",
    "order_funnel": "Пошаговый мастер заказа (мобайл-фёрст)",
    "home_map": "Карта зон доставки (Leaflet)",
    "home_faq": "FAQ с вкладками",
    "home_banner": "Баннер «Каждый приём пищи»",
    "home_result": "«Про реальный результат»",
    "home_marquee": "Бегущая строка",
    "home_menu": "Баннер «Питайся правильно»",
    "home_advantages": "«O-live — это» (4 преимущества)",
    "home_quality": "Качество и безопасность",
    "home_promo": "Промо «Успей заказать»",
}

THEME_TO_VAR = {
    "primary": "--l-lime",
    "primaryHover": "--l-lime-hover",
    "primaryDark": "--l-green-dark",
    "ink": "--l-ink",
    "bgSoft": "--l-bg-soft",
    "bgAccent": "--l-bg-lime",
}


def esc(s):
    return H.escape(str(s if s is not None else ""))


def items_of(props):
    """Normalize a block's `items` prop: accept list of dicts or strings."""
    items = props.get("items") or []
    if isinstance(items, str):
        items = [items]
    out = []
    for it in items:
        out.append(it if isinstance(it, dict) else {"text": str(it)})
    return out


def r_hero(p):
    align = " l-hero--center" if p.get("align") == "center" else ""
    img = p.get("image")
    style = f' style="background-image:url({esc(img)})"' if img else ""
    cls = " l-hero--image" if img else ""
    cta = ""
    if p.get("cta_text"):
        cta = (f'<a class="l-btn" href="{esc(p.get("cta_href") or "#order")}">'
               f'{esc(p["cta_text"])}</a>')
    return (f'<section class="l-hero{align}{cls}"{style}><div class="l-container">'
            f'<div class="l-hero__inner">'
            f'<h1 class="l-hero__title">{esc(p.get("heading"))}</h1>'
            f'<p class="l-hero__subtitle">{esc(p.get("subheading"))}</p>{cta}'
            f'</div></div></section>')


def r_text(p):
    a = p.get("align")
    tcls = " l-title--left" if a == "left" else ""
    h = f'<h2 class="l-title{tcls}">{esc(p["heading"])}</h2>' if p.get("heading") else ""
    return (f'<section class="l-section"><div class="l-container l-container--narrow">{h}'
            f'<div class="l-text__body">{p.get("body") or ""}</div></div></section>')


def r_features(p):
    cards = "".join(
        f'<div class="l-feature">'
        + (f'<div class="l-feature__icon">{esc(i.get("icon"))}</div>' if i.get("icon") else "")
        + f'<div class="l-feature__title">{esc(i.get("title") or i.get("text"))}</div>'
        + (f'<p class="l-feature__text">{esc(i.get("text"))}</p>' if i.get("title") else "")
        + '</div>'
        for i in items_of(p))
    h = f'<h2 class="l-title">{esc(p["heading"])}</h2>' if p.get("heading") else ""
    return (f'<section class="l-section l-section--soft"><div class="l-container">{h}'
            f'<div class="l-features__grid">{cards}</div></div></section>')


def r_cta(p):
    return (f'<section class="l-section l-cta"><div class="l-container">'
            f'<h2 class="l-cta__title">{esc(p.get("heading"))}</h2>'
            f'<p class="l-cta__subtitle">{esc(p.get("subheading"))}</p>'
            f'<a class="l-btn" href="{esc(p.get("cta_href") or "#order")}">'
            f'{esc(p.get("cta_text") or "Заказать")}</a></div></section>')


def r_testimonials(p):
    cards = "".join(
        f'<div class="l-testimonial"><p class="l-testimonial__text">{esc(i.get("text"))}</p>'
        f'<div class="l-testimonial__author">'
        + (f'<img class="l-testimonial__photo" src="{esc(i["photo"])}" alt="">' if i.get("photo") else "")
        + f'<span class="l-testimonial__name">{esc(i.get("name"))}</span></div></div>'
        for i in items_of(p))
    h = f'<h2 class="l-title">{esc(p["heading"])}</h2>' if p.get("heading") else ""
    return (f'<section class="l-section"><div class="l-container">{h}'
            f'<div class="l-testimonials__grid">{cards}</div></div></section>')


def r_faq(p):
    qs = "".join(
        f'<details style="border-bottom:1px solid #E2E2E2;padding:14px 0">'
        f'<summary style="font-weight:700;cursor:pointer;font-size:17px">'
        f'{esc(i.get("q") or i.get("question") or i.get("title"))}</summary>'
        f'<div class="l-text__body" style="padding-top:8px">'
        f'{esc(i.get("a") or i.get("answer") or i.get("text"))}</div></details>'
        for i in items_of(p))
    h = f'<h2 class="l-title">{esc(p.get("heading") or "Вопросы и ответы")}</h2>'
    return (f'<section class="l-section"><div class="l-container l-container--narrow">'
            f'{h}{qs}</div></section>')


def r_lead_form(p):
    return (f'<section class="l-section l-section--soft"><div class="l-container">'
            f'<div class="l-lead__card">'
            f'<div class="l-lead__title">{esc(p.get("heading"))}</div>'
            f'<div class="l-lead__subtitle">{esc(p.get("subheading"))}</div>'
            f'<div class="l-lead__form">'
            f'<input class="l-lead__input" placeholder="Имя">'
            f'<input class="l-lead__input" placeholder="+7 ___ ___-__-__">'
            f'<button class="l-btn" type="button">{esc(p.get("button_text") or "Отправить")}</button>'
            f'</div><p style="text-align:center;color:#5E5E5E;font-size:12px;margin-top:10px">'
            f'(preview: форма не отправляется)</p></div></div></section>')


def r_placeholder(t, props):
    label = SERVER_ONLY.get(t, "server-side block")
    pj = esc(json.dumps(props, ensure_ascii=False, indent=2)) if props else "—"
    return (
        f'<section class="gsp-ph"><div class="gsp-ph__head">SERVER BLOCK&nbsp;'
        f'<code>{esc(t)}</code></div><div class="gsp-ph__label">{esc(label)}</div>'
        f'<pre class="gsp-ph__props">props: {pj}</pre>'
        f'<div class="gsp-ph__note">рендерится только сервером — на live-странице здесь '
        f'настоящий блок</div></section>')


RENDERERS = {
    "hero": r_hero, "text": r_text, "features": r_features, "cta": r_cta,
    "testimonials": r_testimonials, "faq": r_faq, "lead_form": r_lead_form,
    "html": lambda p: p.get("content") or "",
}

PREVIEW_CSS = """
.gsp-ph{margin:10px;padding:18px;border:2px dashed #8AA;border-radius:12px;
  background:repeating-linear-gradient(45deg,#F4F7F5,#F4F7F5 12px,#EDF2EE 12px,#EDF2EE 24px);
  font-family:ui-monospace,Menlo,Consolas,monospace;color:#194536}
.gsp-ph__head{font-weight:700;font-size:14px;letter-spacing:.05em}
.gsp-ph__head code{background:#194536;color:#C4F139;padding:2px 8px;border-radius:6px}
.gsp-ph__label{font-size:13px;margin-top:6px}
.gsp-ph__props{font-size:11px;white-space:pre-wrap;margin:8px 0 0;color:#5E5E5E;
  max-height:140px;overflow:auto}
.gsp-ph__note{font-size:11px;color:#8A8A8A;margin-top:6px}
.gsp-chrome{background:#fff;border-bottom:1px solid #E4E4E4;padding:10px 16px;display:flex;
  align-items:center;gap:10px;font-family:Arial,sans-serif}
.gsp-chrome b{color:#194536}
.gsp-chip{position:fixed;right:8px;bottom:8px;z-index:9999;background:#181717;color:#fff;
  font:11px/1.2 ui-monospace,monospace;padding:4px 8px;border-radius:6px;opacity:.75}
"""

APPLY_OVERRIDES_JS = """
(function(){
  var PROTECTED='#order,#order-menu,#orderFunnel,.of,.sf-form';
  var rules=window.__GSP_OVERRIDES||[];
  rules.forEach(function(r){
    var els;
    try{els=document.querySelectorAll(r.selector);}catch(e){console.warn('bad selector',r.selector);return;}
    els.forEach(function(el){
      var prot=el.closest(PROTECTED)!==null;
      if(r.text!==undefined)el.textContent=r.text;
      if(r.html!==undefined){if(prot){console.warn('html override skipped (protected):',r.selector);}else{el.innerHTML=r.html;}}
      if(r.addClass)String(r.addClass).split(/\\s+/).forEach(function(c){if(c)el.classList.add(c);});
      if(r.style){
        if(typeof r.style==='string'){el.style.cssText+=';'+r.style;}
        else{for(var k in r.style)el.style.setProperty(k.replace(/[A-Z]/g,function(m){return '-'+m.toLowerCase();}),r.style[k]);}
      }
      if(r.attrs){for(var a in r.attrs){if(/^(id|name|data-|on)/i.test(a)){console.warn('forbidden attr skipped:',a);continue;}el.setAttribute(a,r.attrs[a]);}}
    });
  });
})();
"""


def build(config_path=None, out_path=None):
    cfg_p = Path(config_path or REPO / "landing" / "config.json")
    out_p = Path(out_path or REPO / "preview" / "out" / "index.html")
    cfg = json.loads(cfg_p.read_text(encoding="utf-8"))
    meta = cfg.get("meta") or {}
    theme = meta.get("theme") or {}
    overrides = meta.get("overrides") or []
    title = meta.get("title") or "gosura preview (no meta.title!)"

    theme_vars = "".join(
        f"{THEME_TO_VAR[k]}:{v};" for k, v in theme.items() if k in THEME_TO_VAR)
    theme_css = f":root{{{theme_vars}}}" if theme_vars else ""

    out_p.parent.mkdir(parents=True, exist_ok=True)
    css_client = "../../research/client.css"
    css_landing = "../../research/landing.css"

    body = []
    # site chrome approximation (real page wraps sections in header/footer)
    body.append('<div class="gsp-chrome"><b>O-live</b> <span style="color:#8A8A8A">'
                '(site header renders here on live — fixed, currently lime/white)</span></div>')
    for s in cfg.get("sections") or []:
        t = s.get("type")
        props = s.get("props") or {}
        if not isinstance(props, dict):
            props = {}
        if t in RENDERERS:
            body.append(RENDERERS[t](props))
        else:
            body.append(r_placeholder(t, props))
    body.append('<footer class="l-footer"><div class="l-container l-footer__inner">'
                '<span>ООО ФУДВЕНДИНГ · Алматы, ул. Кожина 11</span>'
                '<a class="l-footer__phone" href="tel:+77008702626">+7 700 870-26-26</a>'
                '</div></footer>')
    body.append('<div class="gsp-chip">preview · шрифты Loos Wide/Museo — fallback локально</div>')

    doc = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{css_client}">
<link rel="stylesheet" href="{css_landing}">
<style>{theme_css}{PREVIEW_CSS}
body{{margin:0;font-family:"Museo Sans Cyrl",-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
background:#fff;color:#181717}}
h1,h2,h3,.l-title,.l-hero__title{{font-family:"Loos Wide",Arial,sans-serif}}</style>
</head><body>
{''.join(body)}
<script>window.__GSP_OVERRIDES={json.dumps(overrides, ensure_ascii=False)};</script>
<script>{APPLY_OVERRIDES_JS}</script>
</body></html>"""
    out_p.write_text(doc, encoding="utf-8")
    return out_p


def main():
    cfg = sys.argv[1] if len(sys.argv) > 1 else None
    out = sys.argv[2] if len(sys.argv) > 2 else None
    p = build(cfg, out)
    print(f"rendered -> {p}")


if __name__ == "__main__":
    main()

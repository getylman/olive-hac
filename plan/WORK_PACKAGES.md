# Gosura Landing v2 — Work Packages

Six packages. **Each package owns its own files — no two packages write the same file.**
`landing/config.json` is generated; only WP6 writes it (via the assembler). Read
`plan/ARCHITECTURE.md` first; it is the contract. Global rules for every WP:

- **Never** run `landing_activate`; **never** save with `--status active`. Drafts only (WP6 saves).
- All numbers/claims must trace to MCP output or the live page. No inventions.
- All custom CSS scoped under `gs-` classes; colors via `var(--l-*, #fallback)`;
  fonts only `"Loos Wide"` / `"Museo Sans Cyrl"` via the token vars; no external resources
  (validate.py rejects them).
- Reference DOMs: `research/gosura.html` (old page), `research/funnel-1058.html` (funnel
  recon render), `research/order-funnel.css` (funnel styles).
- A section fragment file contains ONE JSON object `{"type": "...", "props": {...}}`
  (or an array of such objects). No comments in JSON.

---

## Assembler contract — `tools/assemble.py` (built by WP6, spec fixed here)

Deterministic merge, stdlib only (~60 lines):

1. Read `landing/meta/meta.json` → object with keys `title` (string) and `theme` (object).
2. Read `landing/meta/overrides.json` → array of override objects.
3. Glob `landing/sections/*.json`, keep only files matching `^\d\d-[\w.-]+\.json$`,
   sort lexicographically by filename. Each file parses to an object or array of objects;
   append in order to `sections`.
4. Output `landing/config.json`:
   `{"meta": {"title": ..., "theme": ..., "overrides": [...]}, "sections": [...]}`
   (UTF-8, `ensure_ascii=False`, 2-space indent).
5. Fail (non-zero exit, no output file) on: missing/invalid meta files, invalid JSON in any
   fragment, a fragment that is not object/array-of-objects, or an object without `"type"`.
   Warn on duplicate 2-digit prefixes.
6. Print the final section type list so the runner can eyeball the order.

Usage: `python3 tools/assemble.py` then `python3 tools/validate.py landing/config.json`.

---

## WP1 — Funnel section (hero copy V1)

**Owns:** `landing/sections/10-funnel.json`

**Contents:** exactly one section:
```json
{
  "type": "order_funnel",
  "props": {
    "hero_title": "Готовые рационы для снижения веса — с доставкой по Алматы",
    "hero_sub": "ПП-меню 1 200–2 500 ккал: КБЖУ уже посчитаны, меню составляют нутрициологи. Выберите цель — остальное сделаем мы.",
    "offer": {
      "badge": "дни ×2",
      "title": "Плати за 5 дней — ешь 10",
      "subtitle": "Каждый тариф удваивается: 5+5, 14+14 или 30+30 дней в подарок"
    }
  }
}
```
**Critical:** `offer` MUST be an object `{badge, title, subtitle}` — the server rejects a
string (recon save error: «props.offer должен быть объектом {badge, title, subtitle}»).
Copy verbatim from above / ARCHITECTURE Decision 3 (V1). Do not add other props.

**Components:** none (server-rendered block).
**Data pull:** none — copy is fixed; prices are server-computed inside the block
(verified: plan cards render «от 5 000 ₸/день» etc. in `research/funnel-1058.html`).

**Acceptance criteria:**
- File is byte-equivalent in content to the spec above (whitespace free).
- `python3 -c "import json;json.load(open('landing/sections/10-funnel.json'))"` passes.
- No «похудеете на», no promised kg, no invented discount anywhere.

**Verify:** after WP6 assembles — `python3 tools/validate.py landing/config.json` shows the
section as `order_funnel` with only registry props (`offer`, `hero_title`, `hero_sub`).

---

## WP2 — Trust strip + How-it-works

**Owns:** `landing/sections/20-trust.json`, `landing/sections/30-steps.json`

**20-trust.json** — `html` section. Content, in this order:
1. **The shared `gs-` token block** (this is the page's FIRST `html` section, so the
   `:root{--gs-*}` style block from DESIGN_SYSTEM §4 lives here, verbatim).
2. `gs-trust` markup per DESIGN_SYSTEM §5.3, with EXACT copy:
   - `<b>717</b> клиентов в Алматы`
   - `<b>1 130</b> заказов`  ← **never «выполненных»** (only 648 are `sent`)
   - `Оплата картой через Halyk Bank ePay`
   - `<a href="tel:+77008702626">+7 700 870-26-26</a>` (white link on green)

**Data pull (must re-verify before shipping, numbers may have grown):**
```
./tools/olive.py call overview '{}'
```
Use `customers` and `orders.total` from the response; format with thin spaces (1 130).

**30-steps.json** — `html` section: `<h2 class="l-title">Как это работает</h2>` +
`gs-steps` per DESIGN_SYSTEM §5.6, three steps with EXACT copy from ARCHITECTURE
Decision 3 ("Steps copy"). Delivery prices inside step 2 must match:
```
./tools/olive.py call delivery_zones '{}'
```
(currently: free zone, then 600 / 1 100 / 1 600 / 2 100 ₸).

**Components:** token block (DS §4), `gs-trust` (DS §5.3), `gs-steps` (DS §5.6).

**Acceptance criteria:**
- Token block appears once, before any `gs-` markup, only in 20-trust.json.
- Contrast rules respected: on the green `gs-trust` surface only white/lime text; numbers
  in Loos Wide via `--gs-display`; no white-on-lime anywhere.
- All CSS scoped under `.gs-trust` / `.gs-steps` / `:root` custom properties.
- No `<script>`, no external URLs, no ids.

**Verify:** `python3 tools/validate.py` (0 errors); `python3 preview/render.py` and read
`preview/out/index.html` — both sections render, text matches spec.

---

## WP3 — Real-dish proof

**Owns:** `landing/sections/40-dishes.json`

**Contents:** `html` section: `<h2 class="l-title">Что внутри рациона</h2>` + `gs-dishes`
horizontal snap-scroll row (DESIGN_SYSTEM §5.5) with **6 real dishes**, text-only cards
(no `<img>` — MCP exposes no image URLs; stock photos are forbidden).

**Data pull:**
```
./tools/olive.py call meals '{"per_page":60}'
```
Select 6 dishes: 2 breakfast, 2 lunch/dinner-type, 2 others — spread across categories,
favor high-protein/character dishes (e.g. «Скрембл с индейкой» 220 г / 355 ккал /
Б28 Ж24 У6). For each card render verbatim from the API: `name`, `kcal`, `mass`,
`proteins/fats/carbohydrates` as «Б n · Ж n · У n» pills. **No dish prices** (dish
`selling_price` is the à-la-carte replacement price; showing it beside subscription pricing
misleads). Record the 6 dish `id`s in a JSON trailer comment file? No — record them in the
commit message / PR text instead (JSON carries no comments).

**Components:** `gs-dish`/`gs-dishes` (DS §5.5, image element removed; card starts with
`gs-dish__body`).

**Acceptance criteria:**
- Every number matches the `meals` response exactly; 6 distinct real dishes.
- Cards ≥ 44px tap-safe, scroll container has `-webkit-overflow-scrolling:touch` and
  `scroll-snap-type:x mandatory`; page body never scrolls horizontally at 390px.
- CSS scoped under `gs-dishes`/`gs-dish`; no external refs; no scripts.

**Verify:** validate + render as in WP2; in the rendered preview confirm the row overflows
horizontally inside its own container at narrow widths.

---

## WP4 — Support sections: advantages, quality, FAQ, final CTA

**Owns:** `landing/sections/50-advantages.json`, `landing/sections/55-quality.json`,
`landing/sections/60-faq.json`, `landing/sections/70-cta.json`

**50-advantages.json:** `{"type": "home_advantages", "props": {}}`
**55-quality.json:** `{"type": "home_quality", "props": {}}`

**60-faq.json** — free-form `faq`, heading «Вопросы и ответы», EXACT items:
1. q «Как работают дни в подарок?» — a «Каждый многодневный тариф удваивается: оплачиваете
   5 дней — получаете 10, оплачиваете 14 — получаете 28, оплачиваете 30 — получаете 60.
   Подарочные дни включаются автоматически, промокод не нужен.»
2. q «Сколько стоит доставка?» — a «В Алматы есть зона бесплатной доставки; в остальных
   зонах — от 600 до 2 100 ₸. Точную стоимость по вашему адресу покажем сразу при
   оформлении заказа.»
3. q «Как проходит оплата?» — a «Банковской картой онлайн: платёж обрабатывает процессинг
   Halyk Bank (ePay). Телефон подтверждается SMS-кодом, состав и сумма заказа видны до
   оплаты.»
4. q «Какие рационы есть?» — a «Четыре плана: 1 200 и 1 500 ккал (4 блюда в день), 1 800
   ккал (5 блюд) и 2 500 ккал (6 блюд). Всего в меню 297 блюд, КБЖУ рассчитаны для каждого.»
5. q «Как вы следите за качеством?» — a «Блюда готовятся на собственном производстве в
   Алматы; продукция регулярно проверяется в независимых лабораториях, на всех этапах
   работает холодная цепь хранения.» *(paraphrase of the live page's published FAQ — do not
   strengthen the claims)*
6. q «Можно ли заменить блюдо?» — a «Да, замена блюд доступна прямо при оформлении заказа —
   в меню на каждый день.»

**70-cta.json** — free-form `cta`:
```json
{
  "type": "cta",
  "props": {
    "heading": "Готовы попробовать?",
    "subheading": "5 дней питания + 5 в подарок — от 5 000 ₸ в день",
    "cta_text": "Собрать рацион",
    "cta_href": "#orderFunnel"
  }
}
```

**Data pull (verify FAQ numbers):**
```
./tools/olive.py call pricing_periods '{}'
./tools/olive.py call delivery_zones '{}'
./tools/olive.py call meals '{"per_page":1}'   # response carries total count = 297
```

**Acceptance criteria:** JSON valid; FAQ text verbatim from this spec; no medical claims,
no invented guarantees («100 % свежесть» etc. forbidden); `cta_href` is exactly
`#orderFunnel` (the funnel root id — verified in `research/funnel-1058.html`).

**Verify:** validate + render; FAQ items appear; CTA button renders with href
`#orderFunnel`.

---

## WP5 — Chrome: meta, theme, overrides, sticky order bar

**Owns:** `landing/meta/meta.json`, `landing/meta/overrides.json`,
`landing/sections/80-orderbar.json`

**meta.json:**
```json
{
  "title": "Готовое ПП-меню с доставкой по Алматы — O-live",
  "theme": {
    "primary": "#C4F139",
    "primaryHover": "#D5FA6B",
    "primaryDark": "#194536",
    "ink": "#181717",
    "bgSoft": "#F2F2F2",
    "bgAccent": "#EAF3DF"
  }
}
```
(Theme deliberately equals defaults — see ARCHITECTURE Decision 4. Do not "improve" colors.)

**overrides.json** — exactly these seven, in this order:
```json
[
  { "selector": ".sf-notice", "style": "display:none" },
  { "selector": "html", "style": "--sf-notice-h:0px" },
  { "selector": ".sf-header", "style": "background:#fff;color:#194536" },
  { "selector": "#orderFunnel", "style": "--of-green:#194536;--of-green-d:#0f3527;--of-lime:#C4F139" },
  { "selector": ".of-offer", "style": "background:#194536" },
  { "selector": ".of-dd__gift", "style": "color:#194536" },
  { "selector": ".of-gift-accent", "style": "color:#194536" }
]
```
Rationale per rule: ARCHITECTURE Decision 4. Expect `validate.py` **warnings** (not
errors) for the four `of-`/funnel selectors — they exist in `research/funnel-1058.html`,
not in `research/gosura.html`. Exactly 4 such warnings are acceptable; any *error* is not.

**80-orderbar.json** — `html` section: `gs-orderbar` (DESIGN_SYSTEM §5.8) with:
- offer text «5 + 5 дней<br>в подарок», button «Собрать рацион», href **`#orderFunnel`**
  (not `#order` — that id does not exist on the funnel page);
- extra CSS class + rule: `.gs-orderbar--hidden{transform:translateY(110%)}` with
  `transition:transform .25s` on the bar and a `@media (prefers-reduced-motion: reduce)`
  block disabling the transition;
- the visibility script (read-only, never touches the form):
```html
<script>
(function(){
  var bar=document.querySelector('.gs-orderbar');
  var f=document.getElementById('orderFunnel');
  if(!bar||!f||!('IntersectionObserver' in window))return;
  new IntersectionObserver(function(es){
    bar.classList.toggle('gs-orderbar--hidden',es[0].isIntersecting);
  }).observe(f);
})();
</script>
```
This keeps the bar off-screen while the funnel (and its own `of-mbar`, z-index 60) is
visible — no double-bar collision; z-index stays 900 (< site modals at 1000+).

**Acceptance criteria:**
- validate.py: 0 errors; warnings limited to: the 4 funnel-selector warnings + the
  `<script>` advisory on 80-orderbar.
- Script contains no `on*=` attributes, no writes into `#orderFunnel`/`.of`/`.sf-form`,
  no new ids.
- Bar button ≥ 56px tall, `env(safe-area-inset-bottom)` padding, hidden on ≥768px.

**Verify:** validate + render; in `preview/out/index.html` the bar renders and the
override JSON appears in `window.__GSP_OVERRIDES`.

---

## WP6 — Assembler, assembly & QA (RUNS LAST)

**Owns:** `tools/assemble.py`, `landing/config.json` (generated),
`landing/config.b.json` (generated, optional A/B)

**Steps:**
1. Build `tools/assemble.py` to the contract at the top of this file.
2. `python3 tools/assemble.py` → `landing/config.json`. Confirm printed section order:
   `order_funnel, html, html, html, home_advantages, home_quality, faq, cta, html`.
3. `python3 tools/validate.py landing/config.json` → must be **0 errors**; allowed
   warnings: 4 funnel selectors + 1 script advisory (+ possible `l-title`/`sf-`-styling
   advisories if any).
4. `python3 preview/render.py landing/config.json` → open/read
   `preview/out/index.html`; check section order, copy, and that wide content
   (dish row) scrolls in its own container.
5. Save draft:
   `./tools/olive.py save gosura landing/config.json --label "v2 funnel-first A" --status draft`
   → record the returned `version id` and `preview_url`. **Draft only. Never activate.**
6. Fetch the real render (WAF needs a browser UA):
   `curl -sS -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1" "<preview_url>" -o research/preview-v2.html`
7. **QA checklist on `research/preview-v2.html`** (390px viewport of record; static
   checks since no browser here — flag anything unverifiable):
   - [ ] exactly **one** `<h1>` (`grep -c '<h1'` == 1) and it contains the V1 hero title
   - [ ] funnel offer card shows «Плати за 5 дней — ешь 10» and badge «дни ×2»
   - [ ] plan cards show «от 5 000 ₸», «от 5 500 ₸», «от 6 000 ₸», «от 6 500 ₸»
   - [ ] section order in DOM: `#orderFunnel` → `gs-trust` → `gs-steps` → `gs-dishes` →
         advantages → quality → faq → cta (`data-cta`) → `gs-orderbar`
   - [ ] `grep -c 'data-cta'` ≥ 12 (funnel CTAs + cta block + hero)
   - [ ] overrides delivered: page contains the 7 override rules (grep `--of-green:#194536`
         and `display:none` near `.sf-notice` in the embedded config/overrides payload)
   - [ ] no `home_map`, no `home_marquee`, no `order_menu` markup (`grep -c 'sf-menu-plans'` == 0)
   - [ ] trust strip numbers match a fresh `./tools/olive.py call overview '{}'`
   - [ ] no external font/CDN refs introduced by our blocks
8. Optional A/B: copy `landing/sections/10-funnel.json` aside, swap in Hero V2 (see
   ARCHITECTURE Decision 3), re-assemble to `landing/config.b.json`, validate, save as
   `--label "v2 funnel-first B (hero V2)" --status draft`, restore V1 file, re-run
   `python3 tools/assemble.py`. Record both version ids.
9. Final report: version ids + preview URLs + checklist results + any deviation. **Do not
   activate anything; activation is a user decision** (weights for A/B likewise).

**Acceptance criteria:** checklist fully executed with evidence (grep outputs quoted);
live version 871 still active (`./tools/olive.py show gosura` shows 871 active, new
versions draft).

---

## Dependency & conflict map

```
WP1  10-funnel.json          ─┐
WP2  20-trust, 30-steps      ─┤
WP3  40-dishes               ─┼─→  WP6 assemble → validate → render → draft → QA
WP4  50,55,60,70             ─┤
WP5  meta/, 80-orderbar      ─┘
```
WP1–WP5 are fully parallel (disjoint files). WP6 starts when all five land.

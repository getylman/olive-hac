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

---

# Fix round 1 — bug register of 2026-08-16 (`plan/BUGS.md`)

Four packages, disjoint files, all **buildable in parallel**. `landing/config.json` stays
generated — nobody edits it. Drafts only; live baseline stays **871**; never `--status active`.

**Sequencing constraint (read first):** B1/B2 are bugs in `tools/qa.py` itself — a page with
zero real `data-cta` attributes currently passes, and overrides are never checked. **qa.py
output is untrusted until WP-F2 lands and its repros pass.** Build all four packages in
parallel, but do not run the re-QA gate below until WP-F2 is verified.

**Out of scope here:** A1 (offer/pricing copy) awaits `plan/OFFER_STRATEGY.md` from the
marketing audit. Do not touch offer copy in this round. When it lands, the copy edit is a
small follow-up touching exactly: `landing/sections/10-funnel.json` (`offer.badge/title`,
subtitle), `70-cta.json` (subheading «5 дней питания + 5 в подарок…»), `60-faq.json`
(«Как работают дни в подарок?» item), `80-orderbar.json` (offer `<span>`). Sequence it after
WP-F1 so `80-orderbar.json` has one owner at a time.

**Report to Olive (not work packages):**
- A1 — pricing matrix ships `gift: 0` for the 5-day period at 10 000 ₸/день while
  `pricing_periods` says `gift_days: 5` and the funnel's built-in copy says «5 + 5»;
  `order-funnel.js` reads only the matrix. Platform-wide (same on olive.kz).
- A6 — Swiper CSS loaded twice, Swiper JS twice (second copy unversioned, no cache reuse),
  `leaflet.min.js` loaded with no map on the page.
- `#sfOrderBtn` (template element) carries no `data-cta`, so desktop floating-button clicks
  are invisible to conversion metrics. We cannot add it: overrides may never set `data-*`
  (validate.py rule, mirrors platform).

## Architectural decision — overrides vs static CSS (A2/A5 root cause)

Overrides are a **single client-side pass at `DOMContentLoaded`** (verified: emitted applier
script). Two structural consequences: they cannot style nodes injected later (A2 —
`.of-gift-accent` is rebuilt by `innerHTML` on every `applyPeriod()`), and everything they fix
flashes un-fixed until DCL on slow mobile (A5).

**Decision: all 7 current overrides migrate to static CSS in a new `gs-` block
(`05-style.json`). The overrides layer keeps exactly one rule — the new A3 `#sfOrderBtn`
href fix, an attribute mutation CSS cannot express.** Recorded rule of thumb: *overrides are
only for DOM mutations (text/attrs) on static template nodes; every cosmetic belongs in
static CSS, which applies at first paint and to future nodes alike.*

Specificity proof that each migrated rule still wins (checked against
`research/order-funnel.css`, `research/client.css`, template head styles in
`research/funnel-1058.html`):

| # | must beat | their spec | our static rule | our spec | why we win |
|---|---|---|---|---|---|
| 1 | template head `<style>` `.sf-notice` | (0,1,0) | `.sf-notice{display:none}` | (0,1,0) | tie → body `<style>` comes after head → source order |
| 2 | head `:root{--sf-notice-h:36px}` + 32px media query | (0,1,0) | `:root{--sf-notice-h:0px}` | (0,1,0) | tie → source order (also beats the MQ copy — same spec, ours later) |
| 3 | `client.css:165` `.sf-header{color:#fff;background:rgb(196 241 57/65%)}`; `:178` `.sf-header.scrolled{background:#fff}` | (0,1,0) / (0,2,0) | `.sf-header,.sf-header.scrolled{background:#fff;color:#194536}` | (0,1,0)+(0,2,0) | base: tie+order; scrolled state covered explicitly at equal spec+order. **This is the P0 contrast fix — do not weaken.** |
| 4 | `order-funnel.css:12` `.of{--of-green:#4CAF50;--of-green-d:#43a047;…}` | (0,1,0) | `#orderFunnel{--of-green:#194536;--of-green-d:#0f3527;--of-lime:#C4F139}` | (1,0,0) | higher specificity — order-independent (same element: `class="of" id="orderFunnel"`, funnel-1058.html:184) |
| 5 | `order-funnel.css:256` `.of-offer{background:linear-gradient(105deg,#5cb85c…)}` | (0,1,0) | `#orderFunnel .of-offer{background:#194536}` | (1,1,0) | higher spec; `background` shorthand also clears the gradient image |
| 6 | `order-funnel.css:1142` `.of-dd__gift{color:#e53935}` | (0,1,0) | `#orderFunnel .of-dd__gift{color:#194536}` | (1,1,0) | higher spec |
| 7 | `order-funnel.css:1145` `.of-gift-accent{color:#e53935}` | (0,1,0) | `#orderFunnel .of-gift-accent{color:#194536}` | (1,1,0) | higher spec — and static CSS reaches the innerHTML-rebuilt nodes (the A2 fix) |

Rules 4–7 are deliberately **ID-scoped, not order-dependent**: the funnel block injects its own
CSS in-body (A6), possibly *after* our early style block, so ties there are not safe.
**Inference flagged:** that the live server emits our html-block `<style>` at its body position
(after head CSS) is verified in the preview renderer and consistent with the known fact "server
emits html block content raw"; the round-1 draft render must confirm it (re-QA step 4). If it
ever fails, rules 1–3 lose their tie-break and must be re-scoped (e.g. `html .sf-header`) — but
rule 3's scrolled fix and all of-* rules survive regardless.

Note: `validate.py` will emit its deliberate-restyle **warning** (not error) for sf-*/of-*
selectors in block CSS — expected; this is exactly the reviewed-restyle case. WP-F2 must keep
it a warning.

## WP-F1 — Page: static-CSS migration, orderbar, dead desktop link (A2 A3 A4 A5)

**Owns:** `landing/sections/05-style.json` (new), `landing/sections/80-orderbar.json`,
`landing/meta/overrides.json`.

1. **Create `05-style.json`** — `{"type":"html","props":{"content":"<style class=\"gs-fixes\">…</style>"}}`
   containing exactly the 7 rules from the table above, in that order. The `class="gs-fixes"`
   on the style tag gives qa.py a render marker. No markup besides the style tag.
2. **Rewrite `landing/meta/overrides.json`** to exactly:
   `[ { "selector": "#sfOrderBtn", "attrs": { "href": "#orderFunnel" } } ]`
   (`href` is a legal attr; element is outside the protected scope; present in
   research/gosura.html so validate's DOM check passes). Do **not** attempt `data-cta` — the
   validator forbids it.
3. **Edit `80-orderbar.json`:**
   - Ship the bar hidden: `class="gs-orderbar gs-orderbar--hidden"` in the markup (A5 —
     no flash over the hero); the observer reveals it.
   - Observer callback: use `es[es.length-1].isIntersecting`, not `es[0]` (A5).
   - Fallback: if `IntersectionObserver` is missing (but the bar exists), remove
     `gs-orderbar--hidden` and return — never leave the bar permanently hidden.
   - Replace `body{scroll-padding-bottom:90px}` with `:root{scroll-padding-bottom:96px}`
     (A4 — the scroller is `html`, so the body rule was a no-op).
   - Add `@media (max-width:767px){body{padding-bottom:96px}}` (A4 — footer no longer
     occluded; ≥768px the bar is `display:none` so no desktop padding).

**Acceptance:** `python3 tools/assemble.py && python3 tools/validate.py landing/config.json`
→ 0 errors (sf/of restyle warnings expected). Config contains exactly 1 override.
**Verify:** covered by the re-QA gate below (steps 3–5); A2/A4/A5 behaviors are
browser-confirmed (listed there).

## WP-F2 — Verification tools (B1 B2 B3 B4) — gates the re-QA

**Owns:** `tools/qa.py`, `tools/validate.py`.

1. **B1** (`qa.py:140`): replace `html.count("data-cta")` with
   `len(re.findall(r'data-cta="[^"]+"', html))`; FAIL when 0.
   *Repro:* fixture page whose only occurrence is `[data-cta]{color:red}` in CSS → must now
   FAIL (today it prints `PASS … 1 found`).
2. **B2** (`qa.py`): new `--- overrides delivered? ---` section. For each override in
   `config.json`: assert its selector's first id/class token appears in the render (reuse the
   token approach from validate's `selector_in_saved_dom`); for `text` rules assert the text
   appears; for `addClass` assert the class appears; for `attrs` print the expected pairs as
   a browser-check reminder (applied only at DCL — curl cannot see them). Also assert the
   override JSON payload itself is embedded in the page.
   *Repro:* `grep -i override tools/qa.py` → currently nothing; afterwards the section runs
   against the round-1 draft.
3. **B3** (`validate.py` `EXTERNAL_REF`/`INLINE_HANDLER`): extend EXTERNAL_REF with
   `<img/<iframe/<source` external `src=` and `srcset=` forms; change handler regex to
   `[\s/]on[a-z]+\s*=` so `<div/onclick=…>` is caught. Mirror the handler fix in qa.py's
   hygiene check (`\son\w+\s*=` at qa.py:173).
   *Repro (from the audit):* config with `<img src="https://x/y.png">`, an `<iframe>`, and
   `<div/onclick="…">` in an html block currently passes with 0 warnings → must now error.
4. **B4** (`validate.py`): run the html-content checks over every markup-bearing string prop,
   not just `html.content` — at minimum `text.body`, `faq` items, `testimonials` items.
   *Repro (from the audit):* `text` block whose `body` has `<script src="https://…">` and
   `<img src=x onerror=…>`, and a `faq` answer with `onerror=` — all currently pass → must
   now error.

**Acceptance:** all four repro fixtures flip to FAIL/error; the current assembled config still
validates with 0 errors; qa.py against saved render `research/preview-v2.html` still passes its
legitimate checks. **Until this lands, treat every qa.py PASS as noise.**

## WP-F3 — Pipeline & MCP client (B5 B6 B9)

**Owns:** `tools/olive.py`, `tools/assemble.py`.

1. **B5** (`olive.py`): port CLI to `argparse` subcommands; `--status` restricted to
   `{draft, active, archive}`; dangling `--label` is a clean usage error.
   *Repro:* `./tools/olive.py save gosura cfg --label --status draft` currently sets
   label=`"--status"` silently → must now exit with a usage error.
2. **B9** (`olive.py`): catch `urllib.error.HTTPError`, read its body, surface via the clean
   `MCP error:` path with the JSON-RPC error content; make the SSE parser iterate events
   instead of taking only the first `data:` line.
   *Repro:* call with a broken token path → today a raw urllib traceback; must become
   `MCP error: …` with body.
3. **B6** (`assemble.py`): hard-error (non-zero, no output) if `meta.json` contains an
   `overrides` key (today silently lost — overrides come only from `overrides.json`);
   a `.json` file in `sections/` that fails `FRAGMENT_RE` (`5-x.json`, `100-x.json`) becomes
   an **error**, not a stdout warning.
   *Repro:* add `"overrides": []` to meta.json → must exit non-zero; `touch
   landing/sections/5-x.json` → must exit non-zero (clean up fixtures after).

**Acceptance:** repros flip; `python3 tools/assemble.py` on the clean tree still produces
byte-identical `config.json` (diff against a pre-change copy).

## WP-F4 — Preview hygiene (B7 B8)

**Owns:** `preview/serve.py`, `preview/render.py`.

1. **B7** (`serve.py`): serve only `preview/out/` plus the `research/` CSS the preview
   references — never the repo root; validate the port arg (int, 1–65535) with a clean error.
   *Repro:* `curl -s -o /dev/null -w '%{http_code}' localhost:8787/.git/config` → today 200;
   must be 404. Non-int port must print usage, not a traceback.
2. **B8** (`render.py:251`): escape the inlined JSON —
   `json.dumps(overrides, ensure_ascii=False).replace("</", "<\\/")` — so a literal
   `</script>` in an override value cannot close the tag early.
   *Repro:* temporary override with value containing `</script>` → rendered preview HTML
   keeps one balanced script tag.

**Acceptance:** repros flip; preview still renders the assembled config.

## Re-QA gate (after WP-F1 lands and WP-F2 is verified — WP-F2 first, always)

1. `python3 tools/assemble.py` → regenerates `landing/config.json`.
2. `python3 tools/validate.py landing/config.json` → 0 errors (deliberate sf/of warnings OK).
3. `export OLIVE_MCP_URL='https://olive.kz/mcp/landings/…'` (from the runner's environment;
   never committed), then
   `./tools/olive.py save gosura landing/config.json --label "fix-round-1" --status draft`.
   **Draft only. Never activate. Live stays 871.**
4. `python3 tools/qa.py <new_vid> --save` with the **fixed** qa.py — must pass, including the
   new override-delivery and real-attribute data-cta checks. Confirm in the saved render:
   `gs-fixes` style block present at body position with `#orderFunnel .of-gift-accent`
   rule; orderbar markup ships `gs-orderbar--hidden`; exactly 1 override in the embedded
   payload (`#sfOrderBtn`).
5. **Real-browser-only confirmations** (curl cannot see these): A2 — tap a plan/duration,
   gift accent stays `#194536`; A3 — desktop ≥992px, scroll 40px, click «Заказать», lands on
   `#orderFunnel`; A4 — scroll to document end at ≤767px, footer requisites fully visible
   above the bar; A5 — no orderbar flash over the hero on a throttled first paint, and no
   un-styled flash of header/notice/funnel colors (they are static CSS now).

**Biggest risk of the round:** the migration silently reverting the P0 header-contrast fix if
the source-order assumption for rules 1–3 fails on the live renderer — mitigated by the
ID-scoping of all funnel rules, the explicit `.sf-header.scrolled` coverage, and re-QA step 4
confirming the style block's body position before any browser check.

---

# Fix round 2 — restyle, surcharge reframe, prefs-limit state (planned 2026-08-16)

Inputs: `design/VISUAL_REFRESH.md` + `design/DESIGN_SYSTEM.md` §7 (restyle, verbatim rule
source), `plan/SURCHARGE_STRATEGY.md` (R1–R5), and the prefs-limit fix specced below (new).
Baseline: draft **1133** (round 1 verified, QA 32/32). Drafts only; live stays **871**;
never `--status active`. `landing/config.json` stays generated.

## Architectural decision — the CSS fragment split (the crux of this round)

All three streams write static CSS, and until now all static CSS lived in
`landing/sections/05-style.json` (DESIGN_SYSTEM §7: "one place"). **Decision: split the
restyle layer into per-package band fragments `06`–`09`; `05-style.json` is FROZEN this
round (still exactly round-1 rules 1–7).** Rationale:

1. **The split is forced, not optional.** The pseudo-content rules must be a *separately
   droppable package* (see gate below), and the no-shared-files rule means a droppable
   package must own its own fragment. Once one band file exists, giving each stream its own
   band is strictly simpler than serialising two streams into a shared file and splitting
   out a third.
2. **Cascade safety, proven not assumed.** Three independent guarantees:
   - Every funnel rule in `06`–`09` is `#orderFunnel`-scoped — (1,x,0) beats the funnel
     CSS's (0,x,0) **order-independently**, so fragment position relative to the funnel's
     in-body stylesheet cannot matter (same argument as WP-F1 rules 4–7).
   - **Disjointness audit (done against the final rule sets below):** no selector+property
     pair is declared in two fragments. `#orderFunnel{}` appears in 05 (`--of-green*`,
     `--of-lime`) and 06 (`font-family`, `--of-muted`) — different properties, no
     interaction. `of-total` (06: border/shadow) vs `of-total::after` (09) are different
     boxes; likewise `of-subnote` (07) vs `of-subnote::after` (09). So same-specificity
     source-order ties **between our fragments never arise**.
   - If a future edit does double-declare, filename order gives a deterministic winner
     (later band wins) — documented here, not left to chance.
3. **Numbering is load-bearing — 06/07/08/09, nothing else.** Fragments assemble
   lexicographically. A band numbered **below 05** would silently *lose* every
   same-specificity tie to round-1 (e.g. a (1,1,0) `.of-gift-accent` recolor in an `04-`
   file loses to rule 7 by source order — no error, just the wrong color). A band numbered
   **10+** would render after the funnel markup, reintroducing the A5 first-paint-flash
   class of bug on funnel screens. All style bands sit strictly inside (05, 10).

Each band's `<style>` tag carries a distinct marker class for qa.py: `gs-fixes` (05,
unchanged), `gs-restyle` (06), `gs-surcharge` (07), `gs-prefs` (08), `gs-pseudo` (09).

**Recorded deviations from the input specs (intent preserved):**
- VISUAL_REFRESH C1 said "merge `--of-muted:#6B6B6B` into round-1 rule 4's block" and §6.2
  said "the refresh band renders inside `gs-fixes` after rules 1–7" — both assumed
  appending to 05. Superseded: C1 ships as its own `#orderFunnel{--of-muted:#6B6B6B}`
  declaration in 06 (same (1,0,0) specificity, different property — identical effect), and
  the refresh band is the separate `gs-restyle` block.
- SURCHARGE_STRATEGY's note "update the re-QA gate to 9 rules / 2–3 overrides" assumed
  appending rules 8–9 to 05. Superseded: 05 stays at exactly 7 rules; the counts that
  change are **overrides 1 → 2 (3 with R5)** and **style bands 1 → 4–5**.
- DESIGN_SYSTEM §7's "one place" wording is amended to "one *layer*, one owner per band
  fragment, never overrides" — everything else in §7 (ID-scoping, constants, red lines)
  stands and binds every band below.

## Package map — 5 packages, disjoint files, WP-R1..R4 fully parallel

```
WP-R1  06-restyle.json, 80-orderbar.json, 40-dishes.json ─┐
WP-R2  07-surcharge.json, meta/overrides.json, 60-faq.json ─┤
WP-R3  08-prefs.json                                       ─┼─→ WP-R5 assemble → validate
WP-R4  09-pseudo.json   [DROPPABLE — see gate]             ─┘        → draft → re-QA
```

## WP-R1 — Funnel restyle core + own-block amplifiers

**Owns:** `landing/sections/06-restyle.json` (new), `landing/sections/80-orderbar.json`,
`landing/sections/40-dishes.json`.

1. **Create `06-restyle.json`** — `{"type":"html","props":{"content":"<style class=\"gs-restyle\">…</style>"}}`
   containing, in this order and **verbatim from `design/VISUAL_REFRESH.md` §3** (specificity
   proofs and computed ratios live there; do not re-derive, do not restate copy here):
   - T1–T3 (type continuity + money prominence; T1 `#orderFunnel{font-family:…}`),
   - C1–C5 (contrast repairs; C1 as its own `#orderFunnel{--of-muted:#6B6B6B}` rule — see
     deviation note above),
   - S1–S4 (selection washes `#EAF3DF`),
   - O1 (lime offer badge),
   - E1 **only** (`of-total` border+shadow — E2 belongs to WP-R4),
   - D (promo de-emphasis).
   **No pseudo-content in this file** (P and E2 are WP-R4's). No `display`/`visibility`/
   `position` on any functional funnel node; no rules on `of-btn` geometry, `of-mbar`
   positioning, `.d-none`, `of-screen` switching; button labels never touched (they wrap
   the live price span).
2. **`80-orderbar.json`** — apply VISUAL_REFRESH §2.1 exactly: offer span becomes
   `<b class="gs-orderbar__price">от 5 000 ₸/день</b><br>+14 дней в подарок` plus the
   `.gs-orderbar__price` rule. Keep button text «Собрать рацион», `data-cta="orderbar"`,
   the `--hidden` ship-state and observer from WP-F1 untouched. Re-verify the from-price
   against the rendered matrix before shipping (DS §5.8 addendum).
3. **`40-dishes.json`** — apply §2.2 exactly: `.gs-dish__kcal{font-size:var(--gs-fs-h2,1.5625rem)}`,
   `.gs-dish__body{gap:var(--gs-sp-3,12px)}`. No other change; data stays verbatim.

**Acceptance:** 06 contains only `#orderFunnel`-prefixed selectors, zero `content:`
declarations, zero `display/visibility/position` declarations; every hex in the file
appears in VISUAL_REFRESH §3 or DESIGN_SYSTEM §1/§7 (никаких новых цветов); assemble+validate
0 errors (of-* deliberate-restyle warnings expected).
**Verify:** WP-R5 steps 1–4; browser items in step 5 (marked B).

## WP-R2 — Surcharge reframe (SURCHARGE_STRATEGY R1, R3, R4, R5-optional)

**Owns:** `landing/sections/07-surcharge.json` (new), `landing/meta/overrides.json`,
`landing/sections/60-faq.json`.

1. **Create `07-surcharge.json`** — `<style class="gs-surcharge">` with exactly R1:
   `#orderFunnel .of-subnote{color:#194536;background:#EAF3DF}` (9.45:1, de-errors the
   note; beats `order-funnel.css:1339` (0,1,0) with (1,1,0)). **R2's `::after` explanation
   is NOT here — it is WP-R4's.**
2. **`overrides.json`** — append R3 verbatim (the prefs-screen `.of-head__sub` `text`
   override, funnel-1058.html:457 — the `[data-screen="prefs"]` scope is what excludes the
   JS-written `.of-head__sub` at :287). Optionally append R5 (checkout row label). Keep the
   `#sfOrderBtn` rule first and untouched. Legal: `text` on a static template node — the
   recorded overrides rule of thumb.
3. **`60-faq.json`** — insert R4's item verbatim after «Как проходит оплата?». No other
   item changes (round-1/offer copy is settled).

**Acceptance:** overrides.json has 2 (or 3) rules, `#sfOrderBtn` first; validate.py 0
errors — expect its "selector not found" **warnings** for R3/R5 (checked against
funnel-less `gosura.html`); FAQ JSON valid, item text byte-equal to SURCHARGE R4.
**Verify:** WP-R5; R3/R5 are DCL-applied so the curl render shows the *original* text —
their delivery is asserted via the embedded overrides payload (qa.py B2) + browser (B).

## WP-R3 — Prefs limit: visible disabled state (new spec — this is the buildable source)

**Owns:** `landing/sections/08-prefs.json` (new).

**Verified mechanics:** funnel JS caps prefs at `MAX_PREFS = 3` and, once 3 are checked,
sets `disabled` on every unchecked `[data-of-pref]` checkbox (`enforcePrefLimit`,
order-funnel.js:917–924); ships **zero** disabled styling (`research/order-funnel.css` has
no `of-prefs` disabled rule). Markup (funnel-1058.html:500–540, 24 instances):
`<label class="of-prefs__opt"><input type="checkbox" data-of-pref value="N"><span>…</span></label>`
— so `input:disabled + span` addresses the label text; `:has()` addresses the whole label.

**Create `08-prefs.json`** — `<style class="gs-prefs">` with exactly:

```css
/* prefs limit: JS disables unchecked boxes at 3 selected with no visual state */
#orderFunnel .of-prefs__opt input[data-of-pref]:disabled{opacity:.45;cursor:not-allowed}
#orderFunnel .of-prefs__opt input[data-of-pref]:disabled+span{color:#9E9E9E}
#orderFunnel .of-prefs__opt:has(>input[data-of-pref]:disabled){cursor:not-allowed}
```

- `#9E9E9E` on white = **2.68 — computed, deliberate, legal**: WCAG 1.4.3 exempts inactive
  UI components; the point is to be visibly distinct from active ink `#181717` (17.89) and
  from informational muted `#6B6B6B` (5.33) so the state reads as *disabled*, not broken.
- Specificity (1,2,1)/(1,2,2) beats `.of-prefs__opt input` (0,2,1) order-independently.
- `opacity` on a disabled input hides nothing tappable (disabled inputs ignore taps);
  the red-line ban on `display/visibility/position` is respected.
- Line 3 is progressive enhancement: without `:has()` support the first two rules still
  deliver the full disabled state.
- The *limit explanation* line is pseudo-content → WP-R4. If WP-R4 is dropped, the limit is
  still communicated by WP-R2's R3 override text («…предпочтения (до 3)…») plus this
  visible state — acceptable degradation.

**Acceptance:** file contains exactly the three rules; only `#orderFunnel`-prefixed
selectors; no `content:`; validate 0 errors.
**Verify:** browser-only (B) — the disabled state exists only after user interaction;
curl can never see it. WP-R5 step 5.

## WP-R4 — Pseudo-content band [SEPARATELY DROPPABLE — needs user sign-off]

**Owns:** `landing/sections/09-pseudo.json` (new).

**Create `09-pseudo.json`** — `<style class="gs-pseudo">` containing every CSS-generated-copy
rule of the round, verbatim from the source specs:
1. **P** — the four step labels + base `of-topbar::after` rule (VISUAL_REFRESH §3-P).
2. **E2** — «Платёж обрабатывает Halyk Bank ePay» `of-total::after` line (§3-E).
3. **R2** — the surcharge explanation `of-subnote::after` (SURCHARGE_STRATEGY R2 verbatim —
   survives the funnel's `textContent` rewrites because generated content is CSS-owned;
   order-funnel.js:742–752 rewrites text and toggles classList only).
4. **Prefs limit hint** (new, pairs with WP-R3):

```css
#orderFunnel .of-prefs:has(input[data-of-pref]:disabled)::after{
  content:"Максимум — 3 предпочтения. Чтобы выбрать другое, снимите одно из выбранных.";
  display:block;margin-top:10px;font:400 13px/1.4 "Museo Sans Cyrl",Arial,sans-serif;
  color:#6B6B6B}
```

True whenever shown: the `:has()` guard renders it exactly when `enforcePrefLimit` has
disabled boxes, i.e. exactly at 3 selected; no numbers CSS can't know. `#6B6B6B` ≥4.68 on
every ground it can sit on. `display:block` on a generated child of a non-interactive
container is inside the red lines (which ban display changes on functional *nodes*).
Degrades silently without `:has()`.

**The gate, honestly stated:** copy in CSS `content` is invisible to find-in-page and text
selection, announced inconsistently by screen readers, brittle against funnel class renames,
and it puts words where maintainers don't look — that is why VISUAL_REFRESH flags P/E2 as
sign-off-needed, and for those two the mechanism is merely *convenient* (dropping them loses
step labels and a reassurance line, nothing breaks). For R2 the same mechanism is the **only**
honest option we own: JS rewrites the note's `textContent` on every recalc, so a `text`
override is futile and any static wording would misstate a dynamic amount — dropping R2 means
the ₸96k lump sum stays a bare unexplained number until the FAQ. One package, one yes/no:
decline it and WP-R1/R2/R3 ship untouched (delete this one file, re-run WP-R5); accept it and
all four rules arrive together.

**Acceptance:** all `content:` declarations of the round live in this file and nowhere else;
copy byte-equal to the source specs; only `#orderFunnel`-scoped selectors.
**Verify:** browser-only (B) for R2 and the limit hint (state-dependent); P/E2 visible on
any funnel walk-through (still browser — pseudo-content never appears in curl'd DOM text).

## WP-R5 — Assembly, draft, re-QA (RUNS LAST; sole writer of generated files)

**Owns:** `landing/config.json` (generated), the QA run.

1. `python3 tools/assemble.py` → expect printed order
   `html, html, html, html, html, order_funnel, html, html, html, home_advantages, home_quality, faq, cta, html`
   (bands 05–09 before the funnel; 4 `html` bands if WP-R4 was declined).
2. `python3 tools/validate.py landing/config.json` → **0 errors**; expected warnings only:
   of-*/sf-* deliberate-restyle per band + "selector not found" for R3/R5 + the WP-F1
   script advisory.
3. `export OLIVE_MCP_URL=…` then
   `./tools/olive.py save gosura landing/config.json --label "fix-round-2" --status draft`.
   Record vid + preview_url. **Draft only. Never activate. Live stays 871.**
4. `python3 tools/qa.py <vid> --save` (round-1-fixed qa.py) — static assertions on the
   saved render: five (or four) marker style blocks present in `<body>` **before**
   `#orderFunnel`; `gs-fixes` byte-identical to round 1 (7 rules — the freeze held);
   embedded overrides payload has 2–3 rules incl. R3's text; FAQ contains R4's question;
   no `content:` outside `gs-pseudo`.
5. **Browser-only (B) checklist, 390×844** — none of these are curl-visible:
   - VISUAL_REFRESH §6.3 walk-through (washes, 21px mbar price, bordered `of-total`,
     22px sum, live pay-button price intact, no horizontal scroll, motion + reduced-motion).
   - **Prefs:** check 3 boxes → remaining 22 grey out (`#9E9E9E` text, dimmed box), taps on
     them do nothing visibly broken, limit hint appears under the list; un-check one →
     re-enable + hint gone; «Очистить» resets all.
   - **Surcharge:** pick a pref that forces replacements → note is green-on-wash with the
     R2 explainer beneath the dynamic sum; remove pref → note hides entirely (`d-none`
     untouched); prefs screen subtitle shows R3's text (DCL applied).
   - Step labels on all four `of-topbar`s; ePay line under the pay button.
   - Round-1 stragglers still pending from 1133: A2 gift-accent after interaction, A3
     desktop click target, A4 footer clearance, A5 no-flash. Close them in the same session.
6. If the user declines WP-R4 after the draft: `rm landing/sections/09-pseudo.json`,
   re-run steps 1–4, save a new draft. Nothing else changes — that is the point of the split.

**Sequencing note:** any future copy round touching `60-faq.json` / `80-orderbar.json`
(e.g. offer tweaks) must sequence after WP-R1/WP-R2 land — one owner at a time.

**Biggest risk of the round:** the highest-value rules are **state-dependent and
browser-only** — the disabled-prefs state, the `:has()` hint and the surcharge note exist
only after user interaction, so a typo'd selector ships green through assemble/validate/qa
and fails silently in the field; `:has()` support and Olive renaming funnel classes are the
same failure shape. Mitigated by: markup anchors file:line-verified today (funnel-1058.html
:425/:457/:500–540), base disabled styling not depending on `:has()`, and re-QA step 5's
explicit interaction repros being **mandatory**, not optional, before any activation talk.

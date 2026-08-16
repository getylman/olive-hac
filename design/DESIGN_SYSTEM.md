# Gosura Landing Design System

The contract implementers code against. Everything here is compatible with the block
system (BRIEF §3): `gs-` blocks ship as self-contained `html` sections; global knobs go
through `meta.theme`; site chrome is touched only via legal `meta.overrides`.

Naming: **every class we author is prefixed `gs-`** (gosura). Never author `sf-`, `l-`,
Bootstrap, or bare element selectors inside block CSS — scope every rule under a `gs-` root.

---

## 1. Color tokens & legal usage (ratios computed, WCAG 2.1)

The site's `landing.css` already exposes the theme as CSS variables. **Always consume
colors as `var(--l-*, fallback)`** so `meta.theme` re-skins our blocks for free:

| var | hex | role |
|---|---|---|
| `--l-lime` | `#C4F139` | accent: button fills, highlights, selected states |
| `--l-lime-hover` | `#D5FA6B` | accent hover |
| `--l-green-dark` | `#194536` | headings, text-on-lime, dark surfaces |
| `--l-ink` | `#181717` | body text |
| `--l-muted` | `#5E5E5E` | secondary text |
| `--l-bg-soft` | `#F2F2F2` | soft section background |
| `--l-bg-lime` | `#EAF3DF` | light accent wash |
| (no var) | `#FFFFFF` | card/base ground |

### Computed contrast matrix

| pair | ratio | verdict |
|---|---|---|
| green on lime / lime on green | 8.22 | **legal everywhere** (AAA body) |
| ink on lime / lime on ink | 13.62 | legal everywhere |
| green on white / white on green | 10.79 | legal everywhere |
| green on bg-soft | 9.64 | legal everywhere |
| green on bg-lime | 9.45 | legal everywhere |
| ink on white / bg-soft / bg-lime | 17.89 / 15.98 / 15.66 | legal everywhere |
| muted on white | 6.48 | body AA ✓ (AAA ✗) — fine ≥14px |
| muted on bg-soft | 5.79 | body AA ✓ — fine ≥14px |
| **white on lime / lime on white** | **1.31** | **ILLEGAL — all uses**, incl. icons/borders that carry meaning (needs 3:1) |
| white on #FF2600 | 3.80 | large text (≥24px / ≥19px bold) only; avoid — off-brand |

Funnel-restyle pairs (computed 2026-08-16; funnel grounds: card `#fff`, bg `#f0f0f0`,
wash `#EAF3DF`):

| pair | ratio | verdict |
|---|---|---|
| funnel `--of-muted` #888 on white | **3.54** | FAIL AA — carries `of-dd__price` (price text, 13px) |
| funnel hint #aaa on white | **2.32** | FAIL |
| funnel error #e53935 on white | **4.23** | FAIL at its 12px size |
| **#6B6B6B** (muted repair) on white / #f0f0f0 / #EAF3DF | 5.33 / 4.68 / 4.67 | PASS body AA everywhere it sits |
| **#B42318** (error repair) on white / #EAF3DF | 6.57 / 5.76 | PASS |
| white on #0f3527 (green-d hover) | 13.47 | PASS |
| green #194536 on #f2fbdf (weekday wash) | 10.09 | PASS |
| #555 on #EAF3DF · #194536 on #f3f9f0 | 6.53 · 10.08 | PASS |
| white on offer-badge blend #4c6e62 (`rgba(255,255,255,.22)` over green) | 5.65 | PASS (18px/800) — lime-chip variant (green on lime 8.22) preferred for brand |

### Rules

1. **Lime is a ground or a decoration, never a text color on light.** Text on lime =
   `--l-green-dark` or `--l-ink` only.
2. Lime as text/icon only on `--l-green-dark` or `--l-ink` grounds.
3. **Never pair lime with white in either direction** — not text, not icons, not
   meaningful borders. A lime border on a white card may exist only when redundant with
   another cue (background shift, checkmark).
4. Secondary text `--l-muted` at ≥14px on white/bg-soft; never on lime or bg-lime
   (unverified pair — use green instead).
5. Dark surfaces (`--l-green-dark`): text white or lime; CTA on dark = lime fill + green text.
6. Semantic red only for genuine errors, ≥19px bold if on red fill; promos use lime/green,
   not red.

## 2. Typography

Families (already loaded by the site — **never add font files or imports**):

- **Display:** `"Loos Wide", Arial, sans-serif` — headings, prices, the offer. Weights
  400/500/700 (100–300 exist; don't use below 400 on mobile).
- **Text:** `"Museo Sans Cyrl", -apple-system, "Segoe UI", Roboto, Arial, sans-serif` —
  body, UI, captions.

In the local preview the woff2 files 404 and fallbacks render — expected; on olive.kz the
real faces load.

### Mobile-first scale (rem; px shown at root 16px on a 390px viewport)

| token | rem | px | role | family/weight | line-height |
|---|---|---|---|---|---|
| `--gs-fs-hero` | 1.875 | 30 | hero H1 (≤2 lines) | Loos Wide 700, uppercase | 1.05 |
| `--gs-fs-h2` | 1.5625 | 25 | section titles | Loos Wide 700, uppercase | 1.1 |
| `--gs-fs-h3` | 1.3125 | 21 | card titles | Loos Wide 500 | 1.15 |
| `--gs-fs-lead` | 1.125 | 18 | hero sub, intro | Museo 500 | 1.4 |
| `--gs-fs-body` | 1.0 | 16 | body | Museo 300/500 | 1.5 |
| `--gs-fs-sm` | 0.875 | 14 | secondary, macros | Museo 500 | 1.4 |
| `--gs-fs-xs` | 0.75 | 12 | uppercase labels only, +0.04em tracking | Museo 700 | 1.3 |

Desktop enlargement via clamp on the two display roles only:
`--gs-fs-hero: clamp(1.875rem, 1rem + 3.6vw, 3.375rem)`;
`--gs-fs-h2: clamp(1.5625rem, 1.1rem + 2vw, 2.5rem)`. Everything else stays fixed.

Rules: uppercase Loos Wide never below 20px; body measure ≤ 65ch (`max-width: 60ch` on
paragraphs); prices set in Loos Wide 700 with `font-variant-numeric: tabular-nums`;
headings get `text-wrap: balance`; 12px only for uppercase labels, never sentences.

## 3. Spacing, radius, elevation

**Spacing (4px base):** `--gs-sp-1..8` = 4, 8, 12, 16, 24, 32, 48, 64. Section padding
mobile: 48px top/bottom (matches site's 50px rhythm); card padding 16–24px; gap between
sibling cards 12px. Use flex/grid `gap`, not margins.

**Radius:** `--gs-r-btn: 6px` (matches `.sf-green-btn--classic`), `--gs-r-input: 10px`,
`--gs-r-card: 16px` (matches plan chips), `--gs-r-big: 18px` (`--l-radius`),
`--gs-r-pill: 999px`.

**Elevation:** `--gs-sh-card: 0 10px 30px rgba(0,0,0,.08)` (site token);
`--gs-sh-raised: 0 16px 36px rgba(0,0,0,.12)`; `--gs-sh-bar: 0 -4px 20px rgba(0,0,0,.12)`
(sticky bottom bar). No other shadows.

**Tap targets:** every interactive element ≥44px tall; the sticky bar button ≥56px;
`env(safe-area-inset-bottom)` on anything fixed to the bottom edge.

**Motion:** transitions ≤300ms on color/transform only; wrap any transform hover in
`@media (prefers-reduced-motion: reduce)` off-switch (site does this — match it).

---

## 4. Block skeleton pattern

Every `gs-` component ships as one `html` section:

```html
<style>/* all rules scoped under .gs-xxx */</style>
<section class="gs-xxx">…</section>
```

Self-contained, zero dependencies, colors via `var(--l-*, #fallback)`. A shared token
block (define once, in the **first** `html` section of the page):

```html
<style>
:root{
  --gs-sp-1:4px;--gs-sp-2:8px;--gs-sp-3:12px;--gs-sp-4:16px;--gs-sp-5:24px;
  --gs-sp-6:32px;--gs-sp-7:48px;--gs-sp-8:64px;
  --gs-r-btn:6px;--gs-r-input:10px;--gs-r-card:16px;--gs-r-big:18px;--gs-r-pill:999px;
  --gs-sh-card:0 10px 30px rgba(0,0,0,.08);--gs-sh-bar:0 -4px 20px rgba(0,0,0,.12);
  --gs-fs-hero:clamp(1.875rem,1rem + 3.6vw,3.375rem);
  --gs-fs-h2:clamp(1.5625rem,1.1rem + 2vw,2.5rem);
  --gs-fs-h3:1.3125rem;--gs-fs-lead:1.125rem;--gs-fs-body:1rem;--gs-fs-sm:.875rem;--gs-fs-xs:.75rem;
  --gs-display:"Loos Wide",Arial,sans-serif;
  --gs-text:"Museo Sans Cyrl",-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
}
</style>
```

## 5. Component specs

Copy in the skeletons is placeholder-shaped but factual (real plans, real gift-days, real
contacts). Anything in `[square brackets]` must be replaced with real MCP data before use.

### 5.1 Offer badge — `gs-badge`

```html
<style>
.gs-badge{display:inline-flex;align-items:center;gap:8px;background:var(--l-lime,#C4F139);
  color:var(--l-green-dark,#194536);border-radius:var(--gs-r-pill);padding:10px 18px;
  font:700 var(--gs-fs-sm)/1.3 var(--gs-text);text-transform:uppercase;letter-spacing:.04em}
</style>
<span class="gs-badge">Плати за 5 дней — ешь 10</span>
```
Green-on-lime (8.22:1). Usable inside hero, plan cards, order bar.

### 5.2 Hero — `gs-hero`

```html
<style>
.gs-hero{background:var(--l-bg-lime,#EAF3DF);padding:var(--gs-sp-7) 20px;text-align:left}
.gs-hero__in{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:var(--gs-sp-4)}
.gs-hero h1{font:700 var(--gs-fs-hero)/1.05 var(--gs-display);color:var(--l-green-dark,#194536);
  text-transform:uppercase;margin:0;max-width:16ch;text-wrap:balance}
.gs-hero__sub{font:500 var(--gs-fs-lead)/1.4 var(--gs-text);color:var(--l-ink,#181717);
  margin:0;max-width:36ch}
.gs-hero__cta{display:inline-flex;justify-content:center;align-items:center;min-height:56px;
  background:var(--l-lime,#C4F139);color:var(--l-green-dark,#194536);border-radius:var(--gs-r-pill);
  padding:16px 38px;font:500 1.3125rem/1.05 var(--gs-text);text-decoration:none}
.gs-hero__cta:hover{background:var(--l-lime-hover,#D5FA6B);color:#0A1C14}
@media (max-width:560px){.gs-hero__cta{width:100%}}
</style>
<section class="gs-hero"><div class="gs-hero__in">
  <span class="gs-badge">Плати за 5 дней — ешь 10</span>
  <h1>[Заголовок про результат для сегмента 1200/1500]</h1>
  <p class="gs-hero__sub">Готовое ПП-меню с доставкой по Алматы. Рационы 1 200–2 500 ккал.</p>
  <a class="gs-hero__cta" href="#order">Собрать рацион</a>
</div></section>
```

### 5.3 Trust strip — `gs-trust`

```html
<style>
.gs-trust{background:var(--l-green-dark,#194536);padding:var(--gs-sp-5) 20px}
.gs-trust__in{max-width:1120px;margin:0 auto;display:flex;flex-wrap:wrap;gap:var(--gs-sp-4) var(--gs-sp-6);
  justify-content:center}
.gs-trust__item{display:flex;align-items:center;gap:10px;color:#fff;
  font:500 var(--gs-fs-sm)/1.4 var(--gs-text)}
.gs-trust__item b{color:var(--l-lime,#C4F139);font:700 var(--gs-fs-h3)/1 var(--gs-display);
  font-variant-numeric:tabular-nums}
</style>
<section class="gs-trust"><div class="gs-trust__in">
  <span class="gs-trust__item"><b>717</b> клиентов в Алматы</span>
  <span class="gs-trust__item"><b>1 130</b> выполненных заказов</span>
  <span class="gs-trust__item">Оплата картой через Halyk Bank ePay</span>
  <span class="gs-trust__item"><a href="tel:+77008702626" style="color:#fff">+7 700 870-26-26</a></span>
</div></section>
```
White/lime on green — both legal. Numbers are real (`overview`); update them from MCP, never round up.

### 5.4 Price / plan card — `gs-plan`

```html
<style>
.gs-plans{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:var(--gs-sp-3);
  max-width:1120px;margin:0 auto;padding:0 20px}
.gs-plan{position:relative;background:#fff;border:2px solid #E0E0E0;border-radius:var(--gs-r-card);
  padding:var(--gs-sp-4);display:flex;flex-direction:column;gap:var(--gs-sp-2);box-shadow:var(--gs-sh-card)}
.gs-plan--hot{border-color:var(--l-green-dark,#194536);background:var(--l-bg-lime,#EAF3DF)}
.gs-plan__flag{position:absolute;top:-12px;left:12px;background:var(--l-green-dark,#194536);
  color:var(--l-lime,#C4F139);border-radius:var(--gs-r-pill);padding:4px 12px;
  font:700 var(--gs-fs-xs)/1.3 var(--gs-text);text-transform:uppercase;letter-spacing:.04em}
.gs-plan__name{font:700 var(--gs-fs-h3)/1.15 var(--gs-display);color:var(--l-ink,#181717);margin:0}
.gs-plan__meta{font:500 var(--gs-fs-sm)/1.4 var(--gs-text);color:var(--l-muted,#5E5E5E);margin:0}
.gs-plan__price{font:700 var(--gs-fs-h3)/1 var(--gs-display);color:var(--l-green-dark,#194536);
  font-variant-numeric:tabular-nums;margin-top:auto}
.gs-plan__price small{font:500 var(--gs-fs-xs)/1 var(--gs-text);color:var(--l-muted,#5E5E5E)}
</style>
<div class="gs-plans">
  <article class="gs-plan gs-plan--hot">
    <span class="gs-plan__flag">Выбор 42% клиентов</span>
    <h3 class="gs-plan__name">1 200 ккал</h3>
    <p class="gs-plan__meta">4 блюда в день · для снижения веса</p>
    <div class="gs-plan__price">[₸ цена/день] <small>при 5+5 дней</small></div>
  </article>
  <!-- …1500 / 1800 / 2500 -->
</div>
```
Selected/hot state = green border + bg-lime wash + flag (never a lone lime border on
white). «Выбор 42% клиентов» is the real order share — recompute before shipping.

### 5.5 Dish card with real macros — `gs-dish`

```html
<style>
.gs-dishes{display:grid;grid-auto-flow:column;grid-auto-columns:78%;gap:var(--gs-sp-3);
  overflow-x:auto;padding:4px 20px 16px;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch}
@media (min-width:768px){.gs-dishes{grid-auto-columns:280px}}
.gs-dish{scroll-snap-align:start;background:#fff;border-radius:var(--gs-r-card);
  box-shadow:var(--gs-sh-card);overflow:hidden;display:flex;flex-direction:column}
.gs-dish__img{aspect-ratio:4/3;width:100%;object-fit:cover;background:var(--l-bg-soft,#F2F2F2)}
.gs-dish__body{padding:var(--gs-sp-4);display:flex;flex-direction:column;gap:var(--gs-sp-2)}
.gs-dish__name{font:500 var(--gs-fs-body)/1.3 var(--gs-text);color:var(--l-ink,#181717);margin:0}
.gs-dish__kcal{font:700 var(--gs-fs-h3)/1 var(--gs-display);color:var(--l-green-dark,#194536);
  font-variant-numeric:tabular-nums}
.gs-dish__kcal small{font:500 var(--gs-fs-xs)/1 var(--gs-text);color:var(--l-muted,#5E5E5E)}
.gs-dish__macros{display:flex;gap:var(--gs-sp-2);margin:0;padding:0;list-style:none}
.gs-dish__macros li{background:var(--l-bg-soft,#F2F2F2);border-radius:var(--gs-r-pill);
  padding:4px 10px;font:500 var(--gs-fs-xs)/1.3 var(--gs-text);color:var(--l-ink,#181717);
  font-variant-numeric:tabular-nums}
</style>
<div class="gs-dishes">
  <article class="gs-dish">
    <img class="gs-dish__img" src="[real image url]" alt="Скрембл с индейкой" loading="lazy">
    <div class="gs-dish__body">
      <h3 class="gs-dish__name">Скрембл с индейкой</h3>
      <div class="gs-dish__kcal">355 ккал <small>· 220 г</small></div>
      <ul class="gs-dish__macros"><li>Б 28</li><li>Ж 24</li><li>У 6</li></ul>
    </div>
  </article>
</div>
```
Data straight from `meals` (name/mass/kcal/Б-Ж-У shown are the real dish id 10). Never
invent a dish or a macro; omit the image before using a stock photo.

### 5.6 How it works — `gs-steps`

```html
<style>
.gs-steps{display:grid;gap:var(--gs-sp-3);max-width:1120px;margin:0 auto;padding:0 20px}
@media (min-width:768px){.gs-steps{grid-template-columns:repeat(3,1fr)}}
.gs-step{background:#fff;border-radius:var(--gs-r-card);box-shadow:var(--gs-sh-card);
  padding:var(--gs-sp-5);display:flex;gap:var(--gs-sp-4);align-items:flex-start}
.gs-step__n{flex:0 0 44px;height:44px;border-radius:50%;background:var(--l-lime,#C4F139);
  color:var(--l-green-dark,#194536);display:flex;align-items:center;justify-content:center;
  font:700 var(--gs-fs-h3)/1 var(--gs-display)}
.gs-step h3{font:500 var(--gs-fs-h3)/1.15 var(--gs-display);color:var(--l-ink,#181717);margin:0 0 4px}
.gs-step p{font:300 var(--gs-fs-body)/1.5 var(--gs-text);color:var(--l-muted,#5E5E5E);margin:0}
</style>
<div class="gs-steps">
  <div class="gs-step"><span class="gs-step__n">1</span><div><h3>Выберите рацион</h3>
    <p>1 200–2 500 ккал, меню на каждый день уже составлено.</p></div></div>
  <!-- шаги 2–3 -->
</div>
```
Numbers are legitimate here — it is a real sequence.

### 5.7 Review card — `gs-review` (ONLY for verified real reviews)

```html
<style>
.gs-review{background:#fff;border-radius:var(--gs-r-card);box-shadow:var(--gs-sh-card);
  padding:var(--gs-sp-5);display:flex;flex-direction:column;gap:var(--gs-sp-3);max-width:60ch}
.gs-review__text{font:300 var(--gs-fs-body)/1.5 var(--gs-text);color:var(--l-ink,#181717);margin:0}
.gs-review__meta{display:flex;align-items:center;gap:var(--gs-sp-2);
  font:700 var(--gs-fs-sm)/1.3 var(--gs-text);color:var(--l-green-dark,#194536)}
.gs-review__src{font:500 var(--gs-fs-xs)/1.3 var(--gs-text);color:var(--l-muted,#5E5E5E)}
</style>
<article class="gs-review">
  <p class="gs-review__text">[дословный текст реального отзыва]</p>
  <div class="gs-review__meta">[Имя] <span class="gs-review__src">[источник, дата]</span></div>
</article>
```
**Do not ship this component until Olive provides verifiable reviews.** Source attribution
is mandatory.

### 5.8 Sticky bottom order bar — `gs-orderbar`

```html
<style>
.gs-orderbar{position:fixed;left:0;right:0;bottom:0;z-index:900;background:#fff;
  box-shadow:var(--gs-sh-bar);padding:10px 16px calc(10px + env(safe-area-inset-bottom));
  display:flex;align-items:center;gap:var(--gs-sp-3)}
.gs-orderbar__offer{font:700 var(--gs-fs-xs)/1.3 var(--gs-text);color:var(--l-green-dark,#194536);
  text-transform:uppercase;letter-spacing:.04em}
.gs-orderbar__btn{flex:1;display:flex;justify-content:center;align-items:center;min-height:56px;
  background:var(--l-lime,#C4F139);color:var(--l-green-dark,#194536);border-radius:var(--gs-r-btn);
  font:500 1.125rem/1.05 var(--gs-text);text-decoration:none}
.gs-orderbar__btn:hover{background:var(--l-lime-hover,#D5FA6B);color:#0A1C14}
@media (min-width:768px){.gs-orderbar{display:none}}
body{scroll-padding-bottom:90px}
</style>
<nav class="gs-orderbar" aria-label="Заказ">
  <span class="gs-orderbar__offer">5 + 5 дней<br>в подарок</span>
  <a class="gs-orderbar__btn" href="#order">Собрать рацион</a>
</nav>
```
Pure anchor — zero interaction with order logic. z-index 900 stays under the site's modals
(1000+). Optional later: hide it while `#order` is in view via a tiny IntersectionObserver;
read-only, never write into the form. A simplified top variant (`gs-sticky-cta`, same
button, `top:0`) may be used on desktop instead; never both on one viewport.

## 6. Do-not list

- **No external fonts, CDNs, imports, or new JS libraries.** The page already ships its
  fonts; `gs-` blocks are pure HTML+CSS.
- **No fabricated content**: reviews, counts, prices, discounts, certifications, medical
  claims («похудеешь на N кг» is a medical claim — never). Every number traces to MCP data
  or the live page.
- **Never restructure the order form** (`#order`, `#order-menu`, `#orderFunnel`, `.of`,
  `.sf-form`): no `html` overrides there, no DOM writes from any script, no `id`/`name`/
  `data-*`/`on*` attrs anywhere. `#orderBtn`'s label wraps the live price span — never
  text-override it.
- No unscoped selectors in block CSS (nothing that could hit `sf-*`); the only `body`-level
  rule allowed is the `scroll-padding-bottom` above.
- No white-on-lime / lime-on-white, ever (1.31:1).
- No autoplaying motion; transform transitions need a `prefers-reduced-motion` guard.
- Run `python3 tools/validate.py landing/config.json` before every MCP save.

## 7. Funnel restyle layer (owner: `landing/sections/05-style.json`)

All cosmetics applied to Olive's funnel live in **one place**: the static
`<style class="gs-fixes">` block in `05-style.json` — never in `meta.overrides` (single
DCL pass: flashes, misses innerHTML-rebuilt nodes). Rules are **`#orderFunnel`-scoped**
(funnel internals are single-class `(0,1,0)` and its CSS is injected in-body, so ID-scoping
wins independent of source order). Full rule set, per-rule specificity proofs and priorities:
**`design/VISUAL_REFRESH.md` §3** — build against it verbatim.

Non-token constants of this layer (record here so nobody re-derives them):

| constant | value | role |
|---|---|---|
| funnel muted repair | `#6B6B6B` | replaces `--of-muted:#888` and literal `#aaa`/`#888` hints |
| funnel error repair | `#B42318` | replaces `#e53935` at 12px |
| selection wash | `#EAF3DF` (= `--l-bg-lime`) | background for every `is-selected` state |
| funnel families | Museo Sans Cyrl base via `#orderFunnel{font-family:…}`; Loos Wide only on 20–22px money/titles | `.of` declares `font-family` exactly once (order-funnel.css:25) — one rule rebrands all screens |

Restyle red lines: no `display`/`visibility`/`position` changes on functional funnel nodes;
no rules on `.d-none`, `of-screen` switching, `of-mbar` positioning or `of-btn` geometry;
CSS pseudo-content only on non-interactive containers (`of-topbar`, `of-total`) and only
with copy that is true regardless of funnel state. The funnel's own reduced-motion guard
(order-funnel.css:1303) and the per-day price in `of-mbar` already exist — never duplicate.

### 5.8 addendum — orderbar price line

`gs-orderbar__offer` gains a first line `<b class="gs-orderbar__price">от 5 000 ₸/день</b>`
(Loos Wide 700 1rem, green, `tabular-nums`) above «+14 дней в подарок». The from-price must
equal the rendered matrix `perDay` of the cheapest plan's 14/30-day cells — re-verify
against `window.OLIVE_PRICING` before every ship.

### 5.5 addendum — dish card numeral

`gs-dish__kcal` is the card's visual anchor in place of photography: size
`var(--gs-fs-h2)` (25px), body gap `--gs-sp-3`. No images, no invented dishes — data
verbatim from `meals`.

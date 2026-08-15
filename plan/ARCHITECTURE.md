# Gosura Landing v2 — Architecture

**Status:** decided, evidence-backed. Live version **id 871 stays active**; everything below
ships as drafts only. Reconnaissance draft: **id 1058** (`https://olive.kz/l/gosura?v=1058`,
status draft — does not affect visitors). Its rendered HTML is archived at
`research/funnel-1058.html`, the funnel stylesheet at `research/order-funnel.css`.

---

## Decision 1 — Order machinery: `order_funnel`, placed first. (`order_menu` is out.)

The recon draft rendered the real funnel. Evidence, all from `research/funnel-1058.html`
unless noted:

1. **`order_menu` cannot register CTA clicks; the funnel instruments every step.**
   The platform counts `cta_clicks` via a global listener:
   `document.addEventListener('click', … closest('[data-cta]') … send('cta_click', …))`.
   `research/gosura.html` (the current order_menu page) contains **zero `data-cta`
   attributes** — the current page's measured `0 CTA clicks` is structural, not behavioral.
   The funnel emits `data-cta` on every meaningful action: `plan-5..8`, `menu-next`,
   `menu-next-mobile`, `check-zone`, `send-code`, `verify-code`, `pay`, plus its own
   Yandex.Metrika counter (`data-ym-counter="104935856"`). **The contest is scored on
   tracked conversions; only the funnel feeds the tracker.**

2. **The funnel's first screen IS the audit's prescribed above-the-fold.** It renders, in
   order: our `hero_title` as the page's only `<h1>`, our `hero_sub`, our offer card
   (`offer.title/subtitle/badge`), then four plan cards each showing a **server-computed
   doubled price** — «от 5 000 ₸/день» (1200), 5 500 (1500), 6 000 (1800), 6 500 (2500) —
   with real daily macros («4 блюда · Б70 · Ж71 · У117») and a goal label per card
   («Похудей активно →», «Похудей легко →», «Удержание формы →», «Набор массы →»).
   Audit P0 #1 (no offer, no price anchor, no single action above the fold) is solved by
   the block itself, with zero scroll to the first price.

3. **The funnel's checkout directly attacks the 43 % `pending_payment` leak** (audit P0 #2):
   - itemized total card **including a delivery row** (`data-co-delivery`) — the
     unexpected-cost trigger is answered in-flow;
   - first **and last** delivery date displayed (`data-co-firstdate` / `data-co-lastdate`)
     — the doubled period becomes tangible at the pay moment;
   - duration options carry gift labels (`data-opt-gift`);
   - compact one-line promo field (input + «Применить») instead of order_menu's open promo
     block sitting above the pay button;
   - explicit payment method tile «Банк. картой»;
   - phone verified by SMS code before payment («Получить код» / «Подтвердить») and the
     delivery step checks the address zone inline (`data-cta="check-zone"`, `.of-zone`
     shows the zone result) — the visitor never leaves the flow to a map.

4. **Mobile-first is native.** The funnel is a 5-screen wizard
   (`menu → preview → prefs → delivery → checkout`), has its own fixed mobile bar with the
   live per-day price (`of-mbar`, `data-price-perday` + «Далее»), sticky summary column on
   desktop, and 45 KB of dedicated CSS (`order-funnel.css`). This matches the KZ
   mobile-dominant paid traffic.

5. **The H1 pathology disappears.** order_menu shipped 3 `<h1>` (main + two modal titles).
   The funnel page renders exactly one `<h1 class="of-hero__title">` — ours. (Recon page
   had a second h1 only because we tested a free-form `hero` block; the final page uses
   **no free-form `hero` block** for exactly this reason.)

6. **What we give up and why it's fine:** order_menu's browsable dish menu on page one.
   The funnel loads the same real menu at screen 2 (`data-meals`, with dish replacement
   modal), and section 40 (`gs-dishes`) shows real dishes with macros before commitment.
   `order_filters` also becomes unnecessary — the funnel has its own prefs screen
   (`data-screen="prefs"`).

**Risk noted (inference):** the funnel appears freshly built («по прототипу») and has
0 production impressions to date; there may be undiscovered bugs in later screens we cannot
click-test from this sandbox. Mitigation: QA package walks the preview URL, and rollback is
one `activate 871` away (user-approved only).

## Decision 1a — funnel first, support content below (ordering rationale)

The audit prescribes value → proof → ask for a *page whose ask is a commitment*. The
funnel's screen 1 is not a commitment — it is the value screen (headline, offer, prices,
goal labels); payment is 4 progressive steps deeper. Screen 1 sits in normal document flow,
so a cold visitor can scroll straight past it into trust/proof content and return via the
sticky bar. Placing the funnel first also means **every support section below it is
adjacent to the checkout screens**: when the visitor reaches the pay screen, the trust
strip (section 20) is the very next thing under the pay button. The audit itself lists
"lead with the `order_funnel` block" as prescription 1 for the fold.

---

## Decision 2 — Target page: ordered section table

| # | file | block `type` | funnel stage | purpose / content |
|---|------|--------------|--------------|-------------------|
| 10 | `landing/sections/10-funnel.json` | `order_funnel` | attention → value → action | Hero copy V1 (below), offer object «Плати за 5 дней — ешь 10», plan cards with real doubled prices, full order wizard |
| 20 | `landing/sections/20-trust.json` | `html` | proof / payment-anxiety | `gs-` token block (first html section) + `gs-trust` strip: 717 клиентов, 1 130 заказов, «Оплата картой через Halyk Bank ePay», phone. Sits directly under the funnel ⇒ visible beneath the pay button |
| 30 | `landing/sections/30-steps.json` | `html` | value clarity | `gs-steps` «Как это работает», 3 steps; states gift-doubling and the real delivery pricing (бесплатная зона; далее 600–2 100 ₸) |
| 40 | `landing/sections/40-dishes.json` | `html` | proof (product) | `gs-dishes`: 6 real dishes from `meals` with verbatim kcal/mass/Б-Ж-У. No images (MCP exposes none; no stock photos), no à-la-carte prices |
| 50 | `landing/sections/50-advantages.json` | `home_advantages` | value | Platform's prebuilt «O-live — это» advantages |
| 55 | `landing/sections/55-quality.json` | `home_quality` | objection (quality/safety) | Prebuilt: нутрициологи, ISO/Халал production, MAP packaging, lab checks — platform's own published claims |
| 60 | `landing/sections/60-faq.json` | `faq` | objection | 6 custom truthful Q&A: gift mechanics, delivery cost, payment security (Halyk ePay + SMS), состав рационов, качество, замена блюд |
| 70 | `landing/sections/70-cta.json` | `cta` | action (2nd ask) | Final CTA anchored `#orderFunnel`; the rendered `l-btn` emits `data-cta` (verified on recon: hero/cta block buttons carry `data-cta`) |
| 80 | `landing/sections/80-orderbar.json` | `html` | action (persistent) | `gs-orderbar` sticky bottom bar → `#orderFunnel`, hidden while the funnel is in view (IntersectionObserver, read-only) so it never collides with the funnel's own `of-mbar` (z-60) |

**Excluded, with reasons:**
- `order_menu`, `order_filters` — replaced by the funnel (Decision 1).
- `home_map` — Leaflet init + tile fetches for reference material (audit §7); the funnel
  checks the zone inline and FAQ states real zone prices. Perf win.
- `home_marquee` — motion noise (audit P2).
- `home_result` — its chip claims «Более 400 разных блюд»; MCP `meals` says **297**. We do
  not ship a number our own data contradicts.
- `home_banner`, `home_menu`, `home_promo` — generic promos that would dilute the single
  offer; `home_banner`'s «до 160 г белка» is not corroborated by the funnel's own per-plan
  macros (max Б91/day).
- free-form `hero` — would add a second `<h1>` (verified on recon).
- `testimonials`, `lead_form`, `gs-review` — no verifiable reviews exist in MCP; BRIEF §8
  forbids inventing any. Ready to add if Olive supplies real ones.

---

## Decision 3 — Offer & copy (Russian, all numbers real)

**Anchor logic from measured data:** 68 % of buyers take 1200/1500 kcal (weight-loss);
5 days is the #1 period (477 orders), 14 days #2 (341); every multi-day period doubles
(`pricing_periods`: 5+5, 14+14, 30+30); effective price «от 5 000 ₸/день» is
server-computed in the funnel itself (plan 5, period 2: total 50 000 ₸ / 10 days) and
matches the site's own claim «День еды от 5 000₸». The 43 % pending-payment leak is
handled by structure (funnel checkout + trust strip), not copy alone.

**Funnel props — server-validated shape** (recon save with a string `offer` was rejected:
`props.offer должен быть объектом {badge, title, subtitle}`):

### Hero V1 — PRIMARY (segment + offer)
```json
{
  "hero_title": "Готовые рационы для снижения веса — с доставкой по Алматы",
  "hero_sub": "ПП-меню 1 200–2 500 ккал: КБЖУ уже посчитаны, меню составляют нутрициологи. Выберите цель — остальное сделаем мы.",
  "offer": {
    "badge": "дни ×2",
    "title": "Плати за 5 дней — ешь 10",
    "subtitle": "Каждый тариф удваивается: 5+5, 14+14 или 30+30 дней в подарок"
  }
}
```
Rationale: speaks to the 68 % segment first («снижение веса» is goal wording the platform
itself uses; **not** a medical claim — no promised kg/results), doubling offer as the
price-anchor mechanism, badge kept short because `of-offer__badge` renders at 18px bold.
«меню составляют нутрициологи» paraphrases the platform's own published quality text.

### Hero V2 — alternate A/B (price-anchor first)
```json
{
  "hero_title": "День правильного питания — от 5 000 ₸",
  "hero_sub": "Готовые рационы 1 200–2 500 ккал с доставкой по Алматы. Для снижения веса — и не только.",
  "offer": {
    "badge": "5+5 дней",
    "title": "Каждый второй день — в подарок",
    "subtitle": "Оплачиваете 5 дней — получаете 10. Также 14+14 и 30+30"
  }
}
```

### Hero V3 — alternate A/B (low-friction trial first)
```json
{
  "hero_title": "Попробуйте 5 дней ПП — получите 10",
  "hero_sub": "Готовое меню для снижения веса: 1 200–2 500 ккал, доставка по Алматы. 5-дневный рацион — самый популярный формат у наших клиентов.",
  "offer": {
    "badge": "от 5 000 ₸/день",
    "title": "5 дней + 5 в подарок",
    "subtitle": "Дальше — как удобно: 14+14 или 30+30"
  }
}
```
«самый популярный формат» is true: 477 of 1 130 orders are 5-day.

**A/B mechanics:** versions carry a `weight` field (seen in `landing_show`). Ship V1 as
draft A and V2 as draft B (identical except `10-funnel.json`); activation and weighting
require explicit user approval, never ours.

**Trust strip copy (section 20)** — exact: «**717** клиентов в Алматы», «**1 130**
заказов», «Оплата картой через Halyk Bank ePay», «+7 700 870-26-26».
⚠ Never «выполненных заказов» — only 648 are `sent`; 1 130 is *orders placed*. The ePay
claim is true: `epay.homebank.kz/payform/payment-api.js` loads on the page.

**Steps copy (section 30):**
1. «Выберите рацион и длительность» — 1 200–2 500 ккал; каждый тариф от 5 дней
   удваивается: 5+5, 14+14, 30+30.
2. «Подтвердите адрес и оплатите картой» — есть зона бесплатной доставки, дальше от 600 до
   2 100 ₸; оплата через Halyk Bank ePay.
3. «Получайте готовую еду каждый день» — КБЖУ посчитаны, блюда можно заменять при
   оформлении.

**FAQ copy (section 60)** — 6 items, final text in WORK_PACKAGES WP4. Sources: doubling —
`pricing_periods`; delivery — `delivery_zones` (0 / 600 / 1 100 / 1 600 / 2 100 ₸); payment
— ePay script + funnel SMS flow; рационы — funnel plan meta (4/4/5/6 блюд, real macros);
качество — paraphrase of the live page's own published FAQ (лаборатории, холодная цепь);
замена блюд — funnel replace-modal exists.

**CTA block (section 70):** heading «Готовы попробовать?», subheading «5 дней питания + 5
в подарок — от 5 000 ₸ в день», button «Собрать рацион» → `#orderFunnel`.

---

## Decision 4 — Theme + overrides

### Theme: all six tokens stay at brand defaults, set explicitly.

Evidence: `meta.theme` maps to `--l-*` variables only (render.py mapping; `landing.css`
defines only `--l-*`; the rendered funnel page contains **zero** `var(--l-*` inside the
funnel — it runs on its own `--of-*` scope defined on `.of`). Changing theme tokens would
restyle our `gs-` blocks and free-form blocks but **not** the `sf-` chrome (hardcoded
colors) nor the funnel (`--of-*`) — guaranteeing drift. The brand palette already passes
every contrast pair we use (design-system matrix). So: theme = defaults, written out
explicitly for stability; all real color work happens in overrides below.

### Overrides (`meta.overrides`) — the complete list

| # | selector | rule | fixes | evidence |
|---|----------|------|-------|----------|
| 1 | `.sf-notice` | `style: "display:none"` | P0: fixed 36px maintenance banner owns the fold | banner is dated «17 августа»; the funnel's own `data-first-date="2026-08-18"` means every order placed now is delivered **after** the maintenance window — the notice is irrelevant to our buyer. Conservative alternative (keep visible, unfixed): `{"selector":".sf-notice--fixed","style":"position:static"}` — accepted trade-off: 36px transparent strip above the fixed header after scrolling |
| 2 | `html` | `style: "--sf-notice-h:0px"` | header offset | page CSS: `.sf-header { top: var(--sf-notice-h) }` (36px/32px) — zeroing the var pulls the fixed header flush to the top; inline style on `html` beats both `:root` stylesheet blocks |
| 3 | `.sf-header` | `style: "background:#fff;color:#194536"` | P0: white-on-lime header, **1.31:1** | audit §4; white bg → green text = 10.79:1 |
| 4 | `#orderFunnel` | `style: "--of-green:#194536;--of-green-d:#0f3527;--of-lime:#C4F139"` | funnel off-brand + AA failures | funnel buttons are `#fff` on `--of-green:#4CAF50` = **2.78:1 FAIL** (16px bold needs 4.5). Re-pointing the custom properties rebrands every `of-` button/border/selected-state in one rule: white on #194536 = **10.79**, hover #0f3527 = 13.47. `style` is legal inside the protected scope; only `html` is banned (verified in `overrides_schema` and validate.py) |
| 5 | `.of-offer` | `style: "background:#194536"` | offer card gradient | hardcoded `linear-gradient(#5cb85c, #7dc93a)` with white text = **2.48 / 2.04 FAIL**; on #194536 → 10.79 |
| 6 | `.of-dd__gift` | `style: "color:#194536"` | gift label red #e53935 at 12px = 4.23 < 4.5 | funnel CSS; also on-brand |
| 7 | `.of-gift-accent` | `style: "color:#194536"` | same red accent | funnel CSS |
| 8 | *(meta, not override)* `meta.title` | `"Готовое ПП-меню с доставкой по Алматы — O-live"` | tab currently shows «Gosura» | audit P0 #1.4 |

Notes: selectors #4–#7 don't exist in `research/gosura.html`, so `validate.py` emits
**warnings** for them — expected; they are verified against `research/funnel-1058.html`.
Optional P2 (not in v1): hiding header nav exits — deferred because `.sf-header__menu`
also lives inside the burger `nav.sf-menu`; a naive `display:none` empties the burger.

The audit's order_menu-specific fixes (selected-plan lime border, promo de-emphasis,
`#orderBtn`) are moot — order_menu is not on the page. The funnel's selected state
(`.of-plan.is-selected` border = `--of-green`) is fixed by override #4 (#194536 on white =
10.79 ≥ 3:1 non-text).

---

## NOT buildable in the block system (flag to Olive)

1. **pending_payment recovery loop** (SMS/email retry links, saved carts) — backend.
2. **Vendor script bloat** (jQuery, Bootstrap, double-loaded Leaflet, webvisor, 4 analytics
   stacks) — lives in the base layout, ships regardless of sections. The duplicate Leaflet
   include is a free win for Olive.
3. **Funnel's own copy inside screens 2–5** (button labels, step titles) — только text/style
   overrides there; we deliberately touch only colors.
4. **Real reviews** — no MCP surface exposes any; `testimonials` stays off the page until
   Olive supplies verifiable ones.
5. **Dish images** — `meals` returns no image URLs; `gs-dishes` ships text-only cards
   rather than stock photos (BRIEF §8).

## Rules restated for every implementer

Never `landing_activate`, never `--status active`. No fabricated numbers, reviews, or
medical claims. Never restructure `#orderFunnel` / `.of` / `.sf-form` (style/text/addClass
only; no `html` overrides there; no scripts writing into the form). Validate before every
save: `python3 tools/validate.py landing/config.json`.

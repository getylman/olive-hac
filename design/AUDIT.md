# Mobile Design + Conversion Audit — olive.kz/l/gosura

**Scope.** Active version id 871 ("Дубль главной"), audited against the saved markup
(`research/gosura.html`), the saved CSS (`research/client.css`, `research/landing.css`),
and the business data in `research/BRIEF.md`. Measured stats of this page: 9 impressions,
0 CTA clicks, 0 conversions, CR 0. Viewport of record: **390 × 844** (iPhone 12/13/14 class),
which matches the mobile-dominant KZ ad traffic.

**Method.** Each finding names the heuristic it violates, states the evidence (file + selector
or computed value), and gives a prescription that is actually buildable with the block system
(BRIEF §3): section list, `meta.theme`, `meta.overrides`, or a self-contained `html` block.
Anything the block system cannot fix is flagged as such. Contrast ratios are **computed**
(WCAG 2.x relative luminance), not estimated. Where a claim is inference rather than
measurement it is marked **[inference]**.

Severity = expected revenue impact: **P0** directly gates whether a paid visitor can buy;
**P1** materially depresses CR; **P2** polish.

---

## 1. Above the fold at 390 × 844 — P0

**Heuristics:** 5-second message test; Attention Ratio (one page, one goal); primacy effect.

**What a paid-ad visitor actually sees** (reconstructed from the saved DOM order and the
CSS breakpoint values — not a device screenshot):

| element | height (from CSS) |
|---|---|
| `sf-notice` — fixed maintenance banner "17 августа … технические работы" | 36px, `position:fixed` |
| `.sf-header` — fixed, lime `rgb(196 241 57 / 65%)`, white text | ~64px |
| H1 «Правильное питание с доставкой в Алматы» (25px uppercase at ≤576px) | ~60–80px over 2–3 lines |
| Subtitle «ПП меню и сбалансированные рационы…» | ~70px |
| «Выберите меню:» + 4 plan chips «1 200 Ккал / 4 блюда» … | remainder |

So the first screen contains: a *maintenance warning*, a generic headline, and a
configurator asking the visitor to choose a calorie plan **with no prices anywhere**
(the chips carry only «N Ккал / N блюд» — verified in the markup). There is:

- **No value proposition tuned to the actual buyer.** 68% of orders are 1200/1500 kcal
  weight-loss plans (BRIEF §4); the headline says generic "правильное питание".
- **No price anchor.** The first price a visitor can see requires configuring the order.
  `#orderBtn` starts as `Оплатить (0 ₸)` and `disabled`.
- **No offer.** The genuinely strong, *true* offer — every period doubles: **5 дней + 5 в
  подарок** (real `pricing_periods` data) — appears nowhere above the fold.
- **No single obvious action.** The first interactive elements are four plan chips — a
  decision, not an action. Attention ratio is poor: fixed header carries a full site menu,
  city switcher, phone, burger — all exits.

**Prescription (P0, fully buildable):**
1. Replace the top of the page. Either lead with the `order_funnel` block (it exists for
   exactly this: props `offer`, `hero_title`, `hero_sub`, "пошаговый мастер, мобайл-фёрст"),
   or an `html` hero (spec: `gs-hero` in DESIGN_SYSTEM.md) followed by the order block.
2. Hero copy: weight-loss-first headline + the doubling offer as the price anchor, e.g.
   headline about результат/похудение + «Плати за 5 дней — ешь 10» offer badge
   (`gs-badge`), + one CTA anchored to the order block. All content is real (plans, gift
   days, kcal come from MCP data).
3. Neutralize the maintenance notice's fixed positioning via override:
   `{"selector":".sf-notice--fixed","style":"position:static"}` — it still informs, but no
   longer owns the top 36px of every screen. (Removing it entirely with `display:none` is
   possible but hides a true service notice — keep it, unfixed.)
4. `meta.title` is currently the internal codename — the tab shows **"Gosura"**. Set a real
   title («Правильное питание с доставкой — O-live Алматы»). One line in `meta`.

---

## 2. Payment-step friction — the 43% leak — P0

**Heuristics:** Baymard checkout findings (unexpected costs = the #1 stated abandonment
reason; lack of trust in the payment step is top-5); peak-end rule; labor illusion.

**Fact base:** 482 of 1130 orders (43%, ₸39.1M of pipeline) die in `pending_payment`
(BRIEF §4). On-page evidence from the saved markup:

- **Zero trust signals at the payment moment.** The word «безопасность» occurs once on the
  whole page — as a FAQ question about food freshness. No payment-method marks, no
  «безопасная оплата», no mention that payment runs through **Halyk Bank ePay**
  (`epay.homebank.kz/payform/payment-api.js` is literally loaded on the page — the page
  *has* a bank-grade processor and never says so). **[inference:** absent reassurance at a
  ₸80K+ average check plausibly suppresses payment completion — this is the standard
  Baymard trust finding, we cannot A/B-prove it from here.**]**
- **Price assembles late and piecewise.** `#orderPriceFrom`, `#orderReplacementCost`,
  `#orderTpCost`, `#orderDiscount`, `#orderPriceTotal` — the total emerges at the end from
  parts, at an average of ₸81,694. A cold visitor meets this number for the first time at
  the pay button. **[inference:** sticker shock at final step.**]**
- **Delivery cost is a link, not a number:** «Подробнее о тарифах доставки» points at the
  map. Unresolved delivery cost at checkout is the classic unexpected-cost abandonment
  trigger.
- **The promo-code field sits directly above the pay button** (`#promoInput`,
  `#promoApplyBtn`, then `#orderBtn`). An open coupon field is a documented exit ramp:
  visitors leave to hunt codes and don't come back.
- The pay button itself: `Оплатить (0 ₸)`, `disabled`. Before configuration it reads as
  broken. **[inference]**

**Prescriptions (P0):**
1. **Trust strip `html` block (`gs-trust`) immediately adjacent to the order section** —
   outside the protected form, so fully legal: «Оплата через Halyk Bank ePay» (true — the
   script is on the page), real contacts (+7 700 870-26-26), «717 клиентов, 1130 заказов»
   (real MCP `overview` numbers), ООО ФУДВЕНДИНГ requisites. No invented guarantees.
2. **Answer «сколько стоит доставка?» before the form**, not behind a map link: an `html`
   price/plan section (`gs-plans`) using real per-plan pricing pulled via MCP, and a line on
   delivery zones from `delivery_zones`. Real numbers only.
3. **De-emphasize the promo field** via override (allowed inside `.sf-form`: `style` only):
   reduce its visual weight (muted border, smaller) so it stops competing with the pay
   button. Full collapse-behind-a-link would need `html` restructuring — **not allowed
   inside `.sf-form`; say so and don't do it.**
4. **Do not text-override `#orderBtn`.** Its label wraps the live `#orderBtnPrice` span; a
   `text` override would destroy the price binding. Reassurance copy goes *next to* the
   form (allowed), never *into* it.
5. What the block system cannot fix: the pending_payment → paid recovery loop (SMS/email
   retry links, saved carts) is backend territory. **Not buildable here — flag to Olive.**

---

## 3. Information scent & section order — P0

**Heuristics:** information scent (Pirolli/Card); Krug's "Don't make me think";
serial-position effect.

Current order (verified in the DOM): `order_menu → home_map → home_faq → home_banner →
home_result → home_marquee → home_menu → home_advantages → home_quality → home_promo →
order_filters`. A cold ad visitor who scrolls past the configurator hits a **delivery-zone
map** and then **FAQ tabs** before ever seeing a benefit, a dish, proof of quality, or a
price. Map and FAQ answer questions nobody has asked yet; the sections that create desire
(menu, advantages, quality, result) are buried 6–10 screens down. The order block asks for
commitment *before* value is established — backwards for cold traffic (it duplicates the
homepage, which serves warm/returning visitors).

**Prescribed order for a cold ad visitor (pure config change — trivially buildable):**

1. Hero: offer + price anchor + one CTA (`html` or `order_funnel`)
2. Trust strip (`gs-trust`): payment processor, real counts, contacts
3. How it works, 3 steps (`gs-steps`): выбери план → мы готовим и привозим → ешь и худей *(wording must stay non-medical)*
4. Real menu proof (`gs-dish` cards): actual dishes with actual macros from `meals`
5. Value/quality sections (`home_advantages`, `home_quality`, `home_result`)
6. **The order block** (`order_menu` + `order_filters`, or `order_funnel`) — now that value exists
7. FAQ (`home_faq`) — objection handling *after* the ask
8. Map (`home_map`) — reference material, last
9. Footer contacts

Rationale: value → proof → ask → objections. FAQ and map are objection-handlers and
reference; they support the ask, they don't precede it.

---

## 4. Color & accessibility — P1 (one P0 sub-item)

**Heuristic:** WCAG 2.1 §1.4.3 (4.5:1 body, 3:1 large text ≥24px / ≥18.66px bold) and
§1.4.11 (3:1 non-text UI). Ratios computed with the standard relative-luminance formula:

| fg on bg | ratio | body AA | large AA | non-text UI (3:1) |
|---|---|---|---|---|
| #194536 green on #C4F139 lime | **8.22** | PASS | PASS | PASS |
| #181717 ink on lime | **13.62** | PASS | PASS | PASS |
| **#FFFFFF white on lime** | **1.31** | FAIL | FAIL | **FAIL** |
| **lime on #FFFFFF white** | **1.31** | FAIL | FAIL | **FAIL** |
| lime on green | 8.22 | PASS | PASS | PASS |
| green on white | 10.79 | PASS | PASS | PASS |
| white on green | 10.79 | PASS | PASS | PASS |
| green on #F2F2F2 grey | 9.64 | PASS | PASS | PASS |
| green on #EAF3DF accent | 9.45 | PASS | PASS | PASS |
| ink on white / grey / accent | 17.89 / 15.98 / 15.66 | PASS | PASS | PASS |
| #5E5E5E muted on white / grey | 6.48 / 5.79 | PASS (AAA fail) | PASS | PASS |
| white on #FF2600 red (price badge) | **3.80** | FAIL | PASS | PASS |

**Violations found on the live page:**
- **P0 sub-item — `.sf-header` sets `color:#fff` on `rgb(196 241 57/65%)` lime.** White on
  lime is 1.31:1 — the header text/icons are effectively invisible in sunlight, on the very
  element that persists on every screen. Fix via override:
  `{"selector":".sf-header","style":"background:#fff;color:#194536"}` (header is outside
  the protected form; `style` is legal).
- **Selected plan state is a 2px lime border on a white card** (`.sf-menu-plans__type-item.active`).
  1.31:1 fails the 3:1 non-text requirement — the *current selection*, a state that feeds
  directly into what the buyer pays, is nearly indistinguishable. Fix without touching form
  DOM: a `<style>` rule from an `html` block —
  `.sf-menu-plans__type-item.active{border-color:#194536;background:#EAF3DF}` (CSS only, no
  structural change; states toggle correctly because it's a stylesheet rule, not a one-shot
  inline patch).
- `.sf-banner__price` white on #FF2600 at 31px passes large-text only; any smaller use fails.

**Legal-use rules derived from the math** (full table in DESIGN_SYSTEM.md): lime is a
*background or decoration* color — text on lime must be green or ink; lime as text only on
green/ink grounds; never lime⇄white in either direction, not even for icons or borders that
carry meaning.

---

## 5. Visual hierarchy & typography — P1

**Heuristics:** modular scale consistency; 45–75ch line length; single-H1 document outline.

- **Three `<h1>` elements** on the page («Правильное питание…», «Замена блюд», «Добавить
  товар» — the latter two are modal titles marked up as h1). Hierarchy collapse for both
  SEO and screen readers. Modal titles are inside order machinery — `text` overrides can't
  change the tag. **Not fixable in the block system; flag to Olive.**
- The homepage h1 drops 55 → 45 → 35 → 25px across breakpoints; at 390px the uppercase
  Loos Wide 25px headline has less presence than the plan chips below it — display type
  loses exactly where ad traffic lives. The landing blocks (`landing.css`) are better
  (`clamp(30px, 6vw, 58px)` hero) — build the new top in landing blocks, not homepage ones.
- Loos Wide (display, wide grotesque, weights 100–700 available) + Museo Sans Cyrl (text)
  is a solid pairing already loaded by the site — **use it, never import fonts** (also a
  CSP/perf rule). Uppercase Loos Wide below ~20px becomes unreadable in Cyrillic at
  low-DPI — reserve uppercase for ≥20px [inference from face geometry; verify on device].
- Body text on the homepage sections runs 16–17px/140% — fine; some `.sf-menu-order__hint`
  and muted small text at 13–14px sits on grey — passes AA (5.79) but not AAA; keep ≥14px.
- Prescription: adopt the fixed mobile type scale in DESIGN_SYSTEM.md §3 for every new
  `gs-` block so the new page has one scale, not three.

## 6. Thumb reach & tap targets — P1

**Heuristics:** 44×44px minimum (Apple HIG / WCAG 2.5.8's 24px is the floor, 44 the
target); Hoober's thumb-zone: bottom third = natural, top corners = stretch.

- Plan chips (`min-width:144px`, ~19px padding) and `sf-green-btn` (≥50px tall) pass.
- `Подробнее о тарифах доставки`, `Снять промокод` are plain links ~17px tall — below
  target size, and they sit inside the *payment* card. `style` override can raise
  `padding`/`min-height` legally.
- **The primary CTA lives at the top of a very long page and nowhere else.** After the
  visitor scrolls into menu/FAQ/map territory there is no persistent way to act — the
  fixed header holds navigation exits but no order button. **This is the single biggest
  thumb-reach failure: the one action we want is never in the thumb zone.**
- Prescription (fully buildable): **sticky bottom order bar** (`gs-orderbar`,
  DESIGN_SYSTEM.md §5.8) as an `html` block — fixed to the bottom edge, full-width lime
  button «Собрать рацион» anchoring to `#order`, offer text «5 + 5 дней в подарок» (real),
  ≥56px tall, `env(safe-area-inset-bottom)` padded. Hidden on desktop via media query.
  CSS/anchor only — it never touches form logic.

## 7. Performance & perceived speed — P1

**Facts (counted in the saved page):** 14 external scripts — jQuery, Bootstrap bundle,
Swiper, **Leaflet loaded twice** (`assets/vendors/leaflet/leaflet.js` *and*
`assets/js/leaflet.min.js`), Toastify, SweetAlert2, phone-mask, client.js, order.js,
Amplitude, Halyk ePay, Cloudflare email-decode — plus 4 analytics stacks (Yandex Metrika
**with webvisor**, GTM, Meta Pixel, Amplitude) and 10 stylesheets (Bootstrap, Font Awesome,
client.css 69KB, swiper, leaflet, hover-slide, toastify…). 25 `<script>` tags total.

- Webvisor alone typically adds hundreds of KB and main-thread recording cost; Leaflet
  (double-loaded) plus map tiles serve a section most visitors never reach. **[inference:
  we cannot run Lighthouse from this sandbox; byte counts are from the saved HTML.]**
- **What the block system can do:** drop `home_map` from the section list → no map init, no
  tile fetches, no Leaflet *execution* for the main scroll (or move it last). Fewer
  homepage sections = fewer images and swiper instances. Keep new `gs-` blocks
  zero-dependency (pure CSS, no new libraries, system-loaded fonts only).
- **What it cannot do:** the vendor `<script>`/`<link>` tags live in the base layout and
  ship regardless of sections. Removing jQuery/Bootstrap/duplicate Leaflet requires a
  server-side template change. **Not buildable here — flag the duplicate Leaflet include
  to Olive; it's a free win.**

## 8. P2 items

- **No social proof anywhere on the page** — no reviews section exists in the current
  section list, and the MCP surface exposes no reviews data. Constraint §8 forbids
  inventing any. P2 only because the *legal* fix is limited: use real, verifiable numbers
  (717 клиентов, 1130 заказов — `overview`) in the trust strip, and real dish macros as
  product proof. If Olive supplies genuine reviews (2GIS/Instagram), a `testimonials`
  block is ready for them; until then, ship none.
- `home_marquee` (running text) between content sections adds motion noise near the
  configurator; drop it from the section list.
- Red `#FF2600` price flash (3.80:1) — restyle promos onto green/lime tokens via theme
  rather than red; large-text-only if kept.
- FAQ tab labels and small hint text at 13px — raise to 14px via override where they sit
  on grey.
- `sf-header` city/phone links wrap awkwardly at 390px [inference from flex-wrap rules];
  reduce header contents on the landing via `display:none` overrides on nav items to cut
  attention-ratio exits (keep phone — it's a real conversion path: 24 callback requests).

---

## Summary priority table

| # | finding | sev | lever |
|---|---|---|---|
| 1 | No offer/price/single CTA above fold; maintenance bar owns top 36px | P0 | new hero (`html`/`order_funnel`), `.sf-notice` override, `meta.title` |
| 2 | 43% pending_payment: no trust signals, late price, promo-field exit, delivery-cost mystery | P0 | `gs-trust` + `gs-plans` blocks beside form; `style` overrides inside form; backend recovery flagged |
| 3 | Map/FAQ before value; ask before desire | P0 | reorder `sections` array |
| 4 | White-on-lime header (1.31:1); invisible selected-plan state | P0/P1 | `style` override + stylesheet rule from `html` block |
| 5 | No persistent CTA in thumb zone on a long page | P1 | `gs-orderbar` sticky bottom bar |
| 6 | Type hierarchy collapse at 390px; 3×H1 | P1 | build new top in `gs-`/landing blocks; H1s not fixable → flag |
| 7 | 14 scripts, 4 analytics, Leaflet ×2, webvisor | P1 | drop `home_map`/`home_marquee`; vendor tags not fixable → flag |
| 8 | No social proof; red badge contrast; 13px hints; header exits | P2 | real-number trust strip; theme colors; overrides |

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

---

# Warm round — architecture decisions (2026-08-16, over draft 1418)

Spec authority: `design/WARM_ROUND.md` (design auditor, same day). Data authority:
`research/WARM_DATA.md` (chosen day: plan 5 · 2026-08-20). Build plan:
`plan/WORK_PACKAGES.md` "Warm round" (WP-W1..W4). Base draft: **1418**
(`research/preview-v1418.html`).

## Decision W1 — Section order: adopt WARM_ROUND §5 unchanged; three free slots, zero renumbering

`03 hero → 04 skin → 05–09 funnel bands → 10 funnel → **20-personas** → 40 dishes →
45 marquee → **50-day** → 60 faq → **65-ask** → 70 plans → 80 orderbar`.

Evidence the seam map holds against the *actual* page (not just the spec's claims):
- Funnel ground is soft `#F4F8EE` — `05-style.json` sets `--of-bg:#F4F8EE` and
  `order-funnel.css` paints `.of{background:var(--of-bg)}`. So gs-who's gradient top
  (soft) is continuous with the band above at 390px.
- 40-dishes is `gs-sec--soft`; 45-marquee is a green `#3F6B39` ribbon; the FAQ is the
  page's only `l-section l-section--soft` (`--l-bg-soft:#F4F8EE` from `meta.theme.bgSoft`,
  render :1648); 70-plans is white `gs-sec`. Every seam ratio in WARM_ROUND §1/§5 was
  computed against exactly these grounds.
- Slots 20/50/65 are free (`ls landing/sections/`), and `assemble.py` sorts fragments
  lexicographically, so the three new files land in the intended positions with no edit
  to any existing fragment.

Narrative for the cold mobile visitor: attention (hero) → action (funnel) → self-ID
pushing back to action (personas) → proof-breadth (dishes) → facts (marquee) →
proof-depth/warmth (day) → objections (faq) → human fallback (ask/WhatsApp, also the
payment-anxiety lever: 43% die at `pending_payment`) → price close (plans) → persistent
bar. If any future round re-orders sections, the two gradients are neighbour-tuned and the
§5 seam table must be re-derived.

## Decision W2 — No existing fragment is touched; 65-ask is fully self-contained

Verified, not assumed: gs-ask consumes only what `04-skin.json` already defines
(`--gs7-*` tokens, `.gs-wrap`, `.gs-btn`, `--gs-r-big`, `--gs-sh-card` — all present) and
brings its own `<section class="gs-ask">` with `background:var(--gs7-soft,#F4F8EE)` and
zero top padding. The "merge with the FAQ" is achieved purely by ground identity: the FAQ's
`#F4F8EE` comes from `meta.theme.bgSoft`, which equals `--gs7-soft`. The residual gap is
the FAQ's own bottom padding (`.l-section` 70px, 50px ≤768px — landing.css:45/:358) on
continuous soft ground; it reads as intra-unit spacing. **60-faq.json and 04-skin.json are
not edited**, which keeps the round at exactly three new files + the generated config.

## Decision W3 — Copy: adopt WARM_ROUND final drafts verbatim; em-dash rule is byte-level

Russian, short sentences, no em dashes; time ranges «с 6:00 до 9:00». All figures verbatim
from WARM_DATA / the 1418 funnel render; scenario copy carries zero numbers; no date in
visible copy («реальное меню одного дня» framing; provenance lives in an HTML comment).
To make the acceptance check mechanical, the three new fragment files must contain **zero
em-dash bytes anywhere, comments included** — a plain `grep` then settles it. Dish names
ship byte-verbatim from WARM_DATA (including «Зеленый»/«запеченным» without «ё») — an
orthography "fix" would break the data trace.

## Decision W4 — The gs-day spine is a background gradient, not `::before` (spec deviation, intent preserved)

WARM_ROUND §2.4 draws the timeline spine with `.gs-day__line::before`, but a rendered
pseudo-element requires a `content:""` declaration — and §6.7 of the same spec (and the
band-09 droppability rule from Fix round 2) requires zero `content:` in the new fragments.
The same 2px `rgba(44,78,40,.28)` rule is drawn instead as a sized no-repeat
`background-image:linear-gradient(...)` on the `<ol>` (`7px 0/2px 100% no-repeat`). Zero
pseudo-elements, identical pixels. Note the page-wide phrasing of §6.7 is already untrue
for the *existing* page — `45-marquee.json` ships a grandfathered `content:"\2733"` — so
the acceptance check is scoped to the three new fragments.

## Decision W5 — Conversion instrumentation

Six new `data-cta` values: `day-order`, `persona-1200`, `persona-1500`, `persona-1800`,
`persona-2500`, `faq-whatsapp`. Checked against the full 1418 inventory (19 values,
grep-verified) — no collisions; expected post-round inventory is 25. The WhatsApp anchor is
legal: `validate.py`'s EXTERNAL_REF matches `src/href` only on media/embed tags
(`img|iframe|source|video|audio|embed|object|track|input`), never `<a>` — verified by
reading the regex, and the footer already links `wa.me/77008702626`.

## Flags (spec vs repo ground truth)

1. **Internal spec contradiction, resolved:** §2.4 `::before` spine vs §6.7 no-`content:`
   — see Decision W4.
2. **§6.7's page-wide "no content: outside 09-pseudo" is stale** — 45-marquee's ✳ is
   grandfathered from the LK round. Scope the check to the new files.
3. **Persona price floors are matrix-true only because of «от»** — «от 5 000 ₸ в день» is
   the halved 14/30-day rate (BRIEF §4: 1–5 days cost double, no gift days). The funnel
   prints the identical strings (render :757–819). Implementers must keep «от» and must
   not attach the floor to any specific duration.
4. **Desktop flank nuance (inference, accepted):** `.of` is a max-width column
   (480px/1120px), so at ≥900px the funnel's soft ground is centered on the white body
   while gs-who's gradient starts soft full-bleed. Invisible at the 390×844 viewport of
   record; not worth a rule.
5. No conflict with CLAUDE.md hard limits: no fabricated figures (all trace to
   WARM_DATA/render/matrix), no order-form changes, no overrides added, drafts only,
   no white-on-lime, gold only as aria-hidden decor on deep (4.38).

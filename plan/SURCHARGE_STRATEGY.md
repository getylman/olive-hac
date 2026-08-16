# Surcharge strategy — «Доплата за замены»

**Date:** 2026-08-16 · **Role:** conversion/UX strategist · **Status:** spec only — nothing in
`landing/` was modified; implementation is a follow-up work package.

**Principle up front: the number is honest — its presentation is broken.** We change zero
tenge of what the customer pays and zero timing of when the funnel computes it. We fix three
presentation failures: (1) the fee is styled as an *error*, (2) it carries no explanation of
what it is, (3) no expectation is set before the customer configures preferences. Everything
below is CSS restyling, `addClass`-compatible static CSS, `text` overrides on static template
nodes, and our own `gs-` content — the only levers we own (BRIEF §3; funnel markup/JS are
protected).

---

## 0. Verified mechanics (all file:line-checked, 2026-08-16)

| fact | source |
|---|---|
| Note element `<div class="of-subnote d-none" data-replace-note>` is **static template markup** on the menu screen, above the «Далее →» CTA | `research/funnel-1058.html:425` |
| JS writes `note.textContent = 'Доплата за замены: ' + fmt(diff) + ' ₸'` and toggles **only** `classList` — it never resets `className` or innerHTML → static CSS (incl. `::after` generated content) and `addClass` survive every recalc; `text` overrides do **not** | live `order-funnel.js:742–752` |
| Surcharge = `total_price_diff` from `/api/meal-plans/{id}/replacements/all` — literally the summed dish-price difference; no other component | `order-funnel.js:759–773` |
| Basis: `full = periodDays + periodGift` — gift days included; the menu also *renders* all full days, i.e. food is genuinely delivered on gift days | `order-funnel.js:759, 216` |
| Current styling: `#e53935` on `#fdecea` — error semantics; **3.7:1 contrast at 13px/600 — fails WCAG AA** (needs 4.5:1) | `order-funnel.css:1339–1347` |
| The visible «Цена в день» (`data-price-perday`) shows the **base** rate only (`'от ' + cell.perDay`); the note's lump sum is folded into no visible total on that screen (`[data-total-sum]` doesn't exist in this markup) — it dangles context-free | `order-funnel.js:304–306`; grep of funnel-1058.html |
| The prefs screen **already** has a live preview `[data-prefs-preview]` (green box): «Заменим N блюд · X ₸/день», where ₸/день **includes** the diff over full days; «Все блюда подходят — замен не требуется» when nothing changes | `order-funnel.js:928–991`; `order-funnel.css:540` |
| Preferences are capped at `MAX_PREFS = 3` (all `[data-of-pref]` checkboxes); «Очистить» resets; replaced dishes get a marker icon in the menu | `order-funnel.js:917–924, 1004`; `order-funnel.css:1512` |
| Checkout itemizes it neutrally: row «Замена блюд +X ₸» before «Итого» and the pay button | `funnel-1058.html:899`; `order-funnel.js:1254–1255` |
| Prefs-screen subtitle `.of-head__sub` («Выберите дни, предпочтения и ограничения…») is a static node the JS never rewrites → a `text` override sticks | `funnel-1058.html:457`; JS grep: no writes to `of-head__sub` |
| Observed case (brief): 3 prefs (= the max) on the 30-day plan → 96 083 ₸ = **+29%** of ₸330 000. Naive division by 30 *paid* days = 3 203 ₸/день; true basis is 60 delivered days = **1 601 ₸/день** | brief; basis verified in JS |

Diagnosis: the shock is manufactured by presentation. The customer meets an unexplained lump
sum, in error styling, summed over a 60-day basis they don't know about, next to a per-day
price that pretends the fee doesn't exist. Olive's own prefs preview already does honest
per-day framing — the red note just contradicts it.

---

## 1. Recommendation (buildable now)

### R1 — De-error the note · `landing/sections/05-style.json`, appended rule 8

```css
/* 8 - surcharge note: information, not an error (was #e53935 on #fdecea, 3.7:1 AA-fail) */
#orderFunnel .of-subnote{color:#194536;background:#EAF3DF}
```

Specificity (1,1,0) beats `order-funnel.css`'s (0,1,0) order-independently — the exact
pattern already proven for rules 4–7 in WP-F1. Deep green on the brand wash is **9.45:1** —
*more* legible than today, deliberately. The note stays bold, in place, shown at the same
moment. We change semantics (error → information), not salience.

### R2 — Explain what the number is · same file, appended rule 9

```css
/* 9 - persists across textContent rewrites: generated content is CSS-owned */
#orderFunnel .of-subnote::after{
  content:"Это разница в цене заменённых блюд — за все дни подписки, включая подарочные. Уберите или измените предпочтения — сумма пересчитается.";
  display:block;margin-top:4px;font-weight:400;font-size:12px;line-height:1.35;color:#194536}
```

Every clause is verifiable: diff = dish-price difference (JS:771), basis includes gift days
(JS:759), recalculation on every change (JS:279, 1004). No numbers — CSS cannot compute them,
and inventing them is forbidden. The second sentence is the agency move: it turns a verdict
into a decision the customer controls.

### R3 — Set the expectation *before* configuring · `landing/meta/overrides.json`, new rule

```json
{ "selector": "#orderFunnel [data-screen=\"prefs\"] .of-head__sub",
  "text": "Выберите дни и предпочтения (до 3) — мы автоматически заменим блюда в меню. Если замена дороже, разница в цене блюд добавится к заказу — вы увидите её сразу, ещё до оплаты." }
```

Static node, never JS-rewritten, `text` is legal inside the protected scope. This is the
progressive-disclosure fix: the customer learns the *rule* at the moment of decision, then the
live preview («Заменим N блюд · X ₸/день») and the note *confirm* rather than surprise. «до 3»
is `MAX_PREFS`; «увидите сразу» is the 250ms-debounced preview; «до оплаты» is the menu note +
checkout row. Expect validate.py's "selector not found in research/gosura.html" **warning**
(that file is the funnel-less 871 page) — verify manually against `funnel-1058.html:457`.

### R4 — FAQ item · `landing/sections/60-faq.json`, new item (place after «Как проходит оплата?»)

```json
{ "q": "Что за «Доплата за замены» при выборе предпочтений?",
  "a": "Когда вы исключаете продукты (например, выпечку или белый сахар), мы заменяем блюда меню на подходящие. Доплата — это разница в цене блюд по меню. Она считается за каждый день доставки, включая подарочные дни, потому что блюда мы привозим и в эти дни. Если все блюда подходят, доплаты нет. Заменённые блюда отмечены в меню, сумма видна до оплаты, а если убрать предпочтение — доплата пересчитается или исчезнет." }
```

Examples are real preference options (the observed case). Every claim maps to a JS/CSS fact in
§0. Note deliberately absent: «мы не берём плату за саму замену» — `total_price_diff` is
computed server-side and we cannot audit that it contains no margin, so we don't claim it.

### R5 (optional, low value) — checkout row label · `landing/meta/overrides.json`

```json
{ "selector": "#orderFunnel [data-co-replace-row] span:first-child",
  "text": "Замена блюд — разница в цене" }
```

True regardless of whether the diff came from preferences or a manual per-dish swap (both feed
`replaceDiff`). Skip if override count is a concern.

**Implementation notes:** this supersedes WP-F1's "exactly the 7 rules" / "exactly 1 override"
acceptance counts — the re-QA gate (WORK_PACKAGES step 4) must be updated to 9 rules / 2–3
overrides. `80-orderbar.json` and `10-funnel.json` are untouched (no ownership conflict; the
hero does not mention the surcharge — see refusal #5). Browser check after drafting: toggle a
pref, confirm the note renders green with the `::after` line, then remove the pref and confirm
it disappears.

---

## 2. Evidence (all verified against primary sources, 2026-08-16)

1. **Unexpected costs are the #1 abandonment cause.** Baymard Institute (running average of 50
   studies): 70.22% average cart abandonment; among US shoppers with an actionable reason, ~39–40%
   cite "extra costs too high (shipping, tax, fees)" and a further 12% "couldn't see/calculate
   total order cost up-front". https://baymard.com/lists/cart-abandonment-rate — grounds R2/R3
   and the Olive asks. (The oft-quoted "48%" is an outdated secondary figure — don't use it.)
2. **Late-revealed fees do move short-term revenue up — by impairing comparison.** Blake,
   Moshary, Sweeney & Tadelis, *Marketing Science* 40(4), 2021: StubHub field experiment,
   millions of users; checkout-stage fee reveal → ~21% more spend, ~14% higher completion than
   all-in upfront pricing, with degraded purchase quality (≥28% of the revenue delta).
   https://pubsonline.informs.org/doi/10.1287/mksc.2020.1261 — this is the honest counter-
   evidence; see §4 for why it doesn't transfer here.
3. **Per-day reframing works — within limits.** Gourville, *JCR* 24(4), 1998 ("Pennies-a-Day"):
   per-day framing invites comparison to trivial daily expenses. Boundary: Gourville,
   *Marketing Letters* 14(2), 2003 — the effect reverses at large per-day magnitudes. At
   ₸1 601/день (coffee-order territory against a ₸5 000+/день product) PAD applies; that's why
   the *per-day* ask to Olive (§3.1) is the highest-value change.
4. **Partitioned pricing lowers recalled total cost.** Morwitz, Greenleaf & Johnson, *JMR*
   35(4), 1998: base + surcharge presentation decreases recalled total and can increase demand —
   Olive's checkout already partitions correctly; our job is to keep the mid-funnel note
   consistent with it, total always visible (never per-day *instead of* total).
5. **Cost-justified fees are judged fair; unexplained ones are not.** Kahneman, Knetsch &
   Thaler, *AER* 76(4), 1986 (dual entitlement): passing on real costs is perceived fair;
   exploiting position is not. The surcharge *is* a cost pass-through — but only if we say so.
   Grounds R2/R4 wording «разница в цене блюд». Homburg, Hoyer & Koschate, *JAMS* 33(1), 2005:
   acceptance of a price increase depends on magnitude and perceived motive fairness.
6. **Agency raises acceptance.** Franke, Schreier & Kaiser, *Management Science* 56(1), 2010:
   self-configuration increases willingness to pay. The customer *chose* the preferences; R2's
   «уберите или измените — сумма пересчитается» keeps the fee inside their locus of control.
7. **Deferring nonstandard fees is an anti-pattern.** NN/g (Flaherty 2018,
   nngroup.com/articles/ecommerce-taxes-fees/): significant nonstandard surcharges must be
   acknowledged at the decision point, not discovered at checkout — users who feel tricked
   abandon. NN/g's progressive-disclosure guidance (Nielsen 2006) explicitly does **not**
   license hiding mandatory costs.
8. **Regulatory direction.** FTC Rule on Unfair or Deceptive Fees, 16 CFR 464 (final Dec 2024,
   effective May 2025): total-price-upfront now mandatory for US tickets/lodging. Doesn't cover
   KZ food subscriptions — cited only as the direction of travel. Airbnb's total-price display
   (2022→ default worldwide 2025) is the market analogue; downstream effect was *hosts cutting
   fees* (~300k listings dropped/lowered cleaning fees, Skift 2025; CESifo WP 11574 finds fees
   fell 2–4% under transparency) — transparency pressures the fee itself, which is exactly §3.4.

---

## 3. Report to Olive (funnel-logic changes we cannot make)

1. **Put the basis and per-day figure into the note text** (one line in `renderReplaceCost`):
   `Доплата за замены: 96 083 ₸ · +1 601 ₸/день за 60 дней (30 + 30 в подарок)`.
   Strongest case: a customer on the "30-day" plan mentally divides by 30 paid days →
   3 203 ₸/день, **double** the true figure (basis is 60 delivered days). Showing the real
   basis halves the perceived cost at zero pricing change, and Gourville's PAD condition holds
   at this magnitude. The JS already has `full`, `days`, `gift` in scope.
2. **Show the diff during preference selection**: extend the existing `[data-prefs-preview]`
   message «Заменим N блюд · X ₸/день» with «(+Y ₸ к заказу)». The preview endpoint already
   returns `total_price_diff` — the number is computed and then not shown at the exact moment
   of decision (Baymard's 12%: people abandon when they can't compute the total).
3. **Stop shipping the note as an error**: `order-funnel.css:1339` `#e53935`/`#fdecea` is error
   semantics and a WCAG AA failure (3.7:1 at 13px). We've overridden it on our landing;
   olive.kz's own funnel still shows it.
4. **Gift-day surcharge: defensible — if labeled; reconsiderable — as marketing.** Defense:
   food is genuinely delivered on gift days (the menu renders all `full` days), and the diff is
   a real cost of real dishes — dual entitlement says customers accept cost pass-throughs *when
   the justification is visible*. Today nothing tells the customer the basis is 60 days, so it
   reads as a ×2 markup instead. Minimum ask = label the basis (item 1). Stronger marketing
   option (their pricing call, not ours): waive the diff on gift days — «предпочтения на
   подарочные дни — без доплаты» is a far better gift story and halves the headline number;
   costs real margin, so we flag it without pushing.
5. Minor: when replacements are *cheaper* (`total_price_diff < 0`) the total silently drops but
   the note stays hidden — showing «Замены дешевле: −X ₸» would be free goodwill.

---

## 4. Honest risk assessment

- **Better disclosure can reduce started checkouts.** The StubHub result (§2.2) is real: hiding
  fees until checkout raised completion 14% and spend 21%. Three reasons it doesn't transfer:
  (a) StubHub's fee was mandatory and unavoidable; ours is optional and self-configured —
  disclosure changes *when* the customer learns, not *whether* they can avoid it; (b) Olive's
  funnel **already** reveals the fee mid-funnel, before any payment click — we are not moving a
  reveal earlier across the purchase decision, we are adding context above an existing reveal;
  (c) StubHub measured completed purchases with payment attached at click-time — our funnel's
  known failure mode is the opposite: **43% of completed orders never get paid**
  (BRIEF §4). A shock survivable at the menu step resurfaces as a cold invoice at payment.
- **Which metric does the contest reward?** Unconfirmed (architect.md open question): the
  platform's `conversions` stat counts `[data-cta]` clicks — including `pay`, which fires
  *before* the charge succeeds — while the business counts paid orders. Our moves are upstream
  of `menu-next` and `pay` alike (the red note currently sits *before* both), so softening the
  shock should help the click metric and the paid metric in the same direction. That alignment
  is the safety margin; if judging counted raw funnel *entries*, none of our changes touch
  those anyway (nothing surcharge-related was added above the fold — see refusal #5).
- **Preference adoption may drop.** R3 warns before configuring; some customers will pick fewer
  prefs (less surcharge revenue for Olive) or skip prefs. Counterweight: fewer surprised
  customers at the payment step, and customers who proceed are pre-consented. Net paid-order
  effect should be positive but is **unproven** — with 9 lifetime impressions we cannot A/B
  anything yet; this is a judgment call, recorded as such.
- **Fragility:** R1/R2 key off `.of-subnote`/`[data-replace-note]` and R3 off screen markup —
  an Olive funnel update can orphan them silently. Add to the re-QA browser checklist.
- **`::after` caveat:** generated content is announced by most screen readers but isn't
  selectable text; acceptable for an explanatory line, and strictly better than no explanation.

---

## 5. What we refused to do — so the reasoning survives

1. **Hide, shrink, de-contrast, or delay the note** (`display:none`, tiny font, grey-on-grey,
   moving it below the CTA). It's a dark pattern (BRIEF §8), NN/g names late fee reveal as the
   trick users punish, and the fee would resurface at checkout anyway — feeding the exact 43%
   pending-payment leak we're trying to close. Our restyle *increases* contrast (3.7 → 9.45).
2. **`text`-override the note itself.** Futile — JS rewrites `textContent` on every recalc —
   and any static wording would misstate a dynamic amount.
3. **Put computed numbers in static copy** (per-day figures, percentages, «≈1 601 ₸/день»).
   CSS can't compute; a hardcoded number is wrong the moment plan/period/prefs change =
   fabrication under BRIEF §8. Numbers appear only where JS computes them (hence §3.1 is an
   Olive ask, not a build item).
4. **Minimizing language** («небольшая доплата», «всего», «копейки»). The fee reached +29% in
   the observed case; Gourville 2003 shows minimization backfires at large magnitudes, and it's
   editorializing, not information.
5. **Pre-funnel/hero warning about the surcharge.** The fee is conditional on a choice most
   visitors haven't made; a global warning suppresses funnel entry without informing anyone.
   NN/g places fee acknowledgment at the decision point — that's R3's placement, and exactly
   why the hero (`10-funnel.json`) is untouched.
6. **Changing the charge** (waiving gift days, capping the diff). Funnel logic and pricing are
   Olive's; ours would be both impossible (protected scope) and dishonest to preview. It's
   argued on the report list instead (§3.4), where it can actually happen.

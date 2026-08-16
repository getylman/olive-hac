# Offer strategy — decision on the A1 pricing-matrix conflict

**Status: decision document.** Audited 2026-08-16 against the live matrix in `plan/BUGS.md` §A1
(`window.OLIVE_PRICING`, verified identical on olive.kz itself) and the business data in
`research/BRIEF.md` §4. Every piece of recommended copy below is checked against the matrix —
nothing is promised that the checkout will not display and charge.

The matrix we cannot change (1200 ккал plan; the ×2 structure is identical on all four plans):

| period | total ₸ | gift days | ₸/day shown at checkout |
|---|---|---|---|
| 1 день | 10 000 | 0 | 10 000 |
| 5 дней | 50 000 | **0** | 10 000 |
| 14 дней | 140 000 | **14** | **5 000** |
| 30 дней | 300 000 | **30** | **5 000** |

Only **14 and 30 days** deliver the "×2" doubling. The current page promise —
«Плати за 5 дней — ешь 10», badge «5 + 5 дней в подарок» — is not honoured at checkout and
**must be removed regardless of anything else in this document.**

---

## 1. Recommendation

**Move the doubling promise to where it is true: lead with the 14-day offer,
keep the 5-day period as an honestly-priced trial, and anchor everything in the
per-day price the checkout itself displays.**

### Hero (props `hero_title` / `hero_sub` of `order_funnel`)

```
hero_title: "Рационы для снижения веса — с доставкой по Алматы, от 5 000 ₸ в день"
hero_sub:   "КБЖУ уже посчитаны, меню составляют нутрициологи. На тарифах от 14 дней
             каждый второй день — в подарок: платите за 14, получаете 28."
```

- «от 5 000 ₸ в день» is literally the `perDay` value the funnel prints for the 14/30-day
  cells of the cheapest plan — a true "from" price, immediately qualified in the subtitle.
- «платите за 14, получаете 28» — exactly what the matrix charges and the gift chip shows.
- Weight-loss-first wording is kept: 68% of orders are 1200/1500 ккал (BRIEF §4).

### `offer` object

```json
{
  "badge": "+14 дней в подарок",
  "title": "Плати за 14 дней — ешь 28",
  "subtitle": "На тарифах 14 и 30 дней день выходит вдвое дешевле, чем на пробных 1–5 днях"
}
```

Truth check against the matrix, per plan: 14-day `gift` is 14 on every plan; `perDay` on 14/30
is exactly half the 1/5-day `perDay` on every plan (5 000 vs 10 000; 5 500 vs 11 000; 6 000 vs
12 000; 6 500 vs 13 000). «вдвое дешевле» is exact, plan-independent, and is confirmed by the
funnel's own price display at the moment of selection — full message match through to payment.

### Period selector framing

- **Do not rewrite the option labels via overrides.** Inside the funnel only
  `text`/`style`/`addClass` are allowed, and a `text` override on `.of-dd__opt` would replace
  the node's textContent including the `.of-dd__gift` chip span, breaking the one element that
  proves the offer. The chips already appear automatically for 14/30 (`refreshDurationPrices`
  shows them when `gift > 0`) — with the new copy the page finally *agrees* with them.
- Frame the periods in the copy layer instead: in the offer block and in a short `text`/`html`
  block placed **before** the funnel, present the ladder as:
  - **1–5 дней — «пробный тариф»**: познакомиться с меню, полная цена за день;
  - **14 дней — рекомендуемый**: +14 дней в подарок, день вдвое дешевле;
  - **30 дней — максимум выгоды**: +30 дней в подарок, та же цена за день, дольше без забот.
- If a visual "recommended" mark is wanted on the 14-day option, use `addClass`/`style` only
  (allowed in the funnel) — never text replacement.

This uses the structure the matrix already implements: 5 days at 10 000 ₸/день is a natural
anchor/decoy that makes 14 days the dominant choice. We did not invent it; we stop hiding it.

---

## 2. Why

### The old promise is dead on arrival at the money step
`order-funnel.js` prices **only** from the matrix; the gift chip is hidden when `gift <= 0`.
A buyer sold on «плати за 5 — ешь 10» reaches the duration step and sees: no gift, 10 000
₸/день. That is a textbook promise-delivery mismatch:

- Drip-pricing research (Santana, Dallas & Morwitz, *Marketing Science* 39(1), 2020) shows
  costs revealed late in the funnel damage satisfaction and choices even when the full total
  is shown before purchase — https://pubsonline.informs.org/doi/10.1287/mksc.2019.1207
- Baymard's aggregate of checkout studies: ~70% average cart abandonment; the top *fixable*
  reason is unexpected/extra cost at checkout (~40% of non-browsing abandoners) —
  https://baymard.com/lists/cart-abandonment-rate
- Advertising an offer the seller does not honour is per-se deceptive under bait-advertising
  rules (FTC 16 CFR Part 238 — the regulatory logic, not the jurisdiction, is the point) —
  https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-238

So removing the false 5+5 promise is mandatory on honesty grounds alone.

### But — read the data carefully — the mismatch does **not** explain the 43% leak
This must be stated plainly, because the intuition is tempting and the data cuts against it.

From `research/orders.txt`: `pending_payment` = 482 orders / ₸39,100,977 → **avg ₸81,122**;
`sent` = 648 / ₸53,213,233 → **avg ₸82,119**. The averages differ by ~1.2%.

If the broken gift promise were the dominant abandonment driver, unpaid orders would be
concentrated in the 5-day cohort (tickets of ₸50–65k), and the pending average would sit
visibly **below** the sent average. It does not. Abandonment appears roughly uniform across
ticket sizes — consistent with a *generic* payment-step problem (a ₸50–300k single card
prepayment, trust, payment-method coverage), not with the 5-day cohort rage-quitting over a
missing gift.

Caveats, honestly: there is no status×period cross-tab in the data, and plan-mix effects could
in principle mask a skew, so this is evidence against the causal story, not proof of its
absence. **Conclusion: fix the offer honesty because it is false, and because message match is
cheap insurance — but do not sell it as the fix for the payment leak, and do not expect the
43% to move much from copy alone.** Ask Olive for a status×period breakdown to settle it.

### What actually addresses the 43% leak (recommendations beyond copy)
- **Kaspi рассрочка.** ~70–77% of KZ e-commerce runs through Kaspi, and its installment tiers
  mean a ₸100k+ ticket qualifies for 12–24-month рассрочка — exactly our 14/30-day totals
  (https://guide.kaspi.kz/partner/ru/marketing/campaign_QR/q1469,
  https://unimall.ai/guides/markets/kazakhstan). Almaty's average salary is ~₸539k/mo
  (https://kz.kursiv.media/2025-12-17/tksh-srednyaya-zarplata-v-almaty-539-tysyach-tenge/),
  so ₸140–300k prepaid is 26–56% of a monthly salary — рассрочка converts that into a familiar
  monthly mental model. Stripe's published testing: each added *relevant* local payment method
  lifts conversion ~+7.4% on average
  (https://stripe.com/blog/testing-the-conversion-impact-of-50-plus-global-payment-methods).
  A KZ payments survey (directional, methodology unnamed) reports 70%+ of Kazakhstanis abandon
  at the payment step over trust/fraud fears
  (https://24.kz/ru/news/social/769697-70-kazakhstantsev-otkazyvayutsya-ot-onlajn-pokupok-na-etape-oplaty).
  **Constraint: only claim Kaspi/рассрочка on the page if it actually exists at Olive's
  checkout — verify first; if absent, this is a request to Olive, not page copy.**
- **Total-price transparency early**: show the full period total next to the per-day figure
  from the first pricing touch (the funnel already does; our copy must too). This is the
  Baymard "no surprises at checkout" finding applied in reverse.
- Trust framing near the payment action (perceived security is driven by visual framing of the
  card area, not actual TLS — https://baymard.com/blog/perceived-security-of-payment-form).

### Why lead with 14 days rather than the best-selling 5-day trial
- **Revenue already lives at 14 days.** 5 дней is #1 by count (477) but at ~₸50–65k tickets;
  14 дней (341 orders at ~₸140–182k) contributes roughly twice the revenue. The contest metric
  is sales, and average order is ₸81,694 — steering even a fraction of trial buyers one step up
  moves revenue more than any tweak to trial volume.
- **It is the only period where a strong offer is true.** The single most compelling honest
  claim available on this page is «плати за 14 — ешь 28, день вдвое дешевле». The 5-day period
  has literally no honest hook beyond "try it" at full price.
- **Operator behaviour and published economics agree.** No scaled meal-kit operator runs a
  free or cheap short trial: all use a *paid* discounted first box with the discount spread
  across subsequent boxes to bridge into commitment (HelloFresh "16 free meals across 7
  boxes"; Factor 50% off box 1 + 20% off next 4; Blue Apron $180 across 6 boxes —
  https://www.hellofresh.com/eat/coupon-codes-and-promotions,
  https://couponfollow.com/site/factor75.com). Bernstein's HelloFresh deep-dive quantifies why
  cheap-entry acquisition fails: >20% average discounting produced 3-yr CLTV €59 vs CAC €75
  (CLTV:CAC 0.8x), with ~90% of a cohort gone by Q4 — "paying people to eat"
  (https://www.bernsteinresearch.com/CMSObjectBR/Files/Recruiting/Hello%20Fresh%20-%20Paying%20People%20to%20Eat%202022.pdf);
  category retention is ~10–15% at 12 months (https://secondmeasure.com/datapoints/meal-kit-competitors-blue-apron-nyse-aprn-hellofresh-customer-retention-market-share/).
  A randomized field experiment (SaaS, labeled as such) found shorter trials push users toward
  discount-sensitivity while longer engagement produces durable, feature-driven conversion
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC12217587/). RU players (Level Kitchen, BeFit,
  justfood, Grow Food) sell per-day-priced programs whose discounts *scale with commitment
  length* — e.g. BeFit +5% for 2 weeks / 7.5% for a month vs 9% first-order
  (https://letbefit.ru/, https://promocode.levelkitchen.com/). Almaty competitors sell trial
  days at full price and reserve gifts for commitment — Organic Monsta's trial day carries no
  discount at ₸6,500–7,700 (https://organicmonsta.kz/), Hello Food runs «3 дня по цене 2»
  (https://hello-food.kz/). Full-price trial + reward-on-commitment **is the norm at every
  scale**; Olive's matrix already implements it — the page just never said so.
- **Per-day framing is the right anchor — with the total alongside.** Gourville's pennies-a-day
  research (JCR 24(4), 1998, https://academic.oup.com/jcr/article-abstract/24/4/395/1797969)
  shows daily reframing improves evaluation, but his follow-up shows it reverses at high daily
  amounts — so «5 000 ₸ в день» must always appear next to the honest period total, never
  instead of it (https://www.dhruvgrewal.com/wp-content/uploads/2014/09/2011-JR-Temporal-Prices.pdf).
  The funnel already shows both; the hero copy above does too.

Expected effects, honestly sized: message match through the funnel should recover some of the
drop at the duration step for gift-motivated buyers (direction supported by the drip-pricing
and Baymard evidence; magnitude unknowable in advance); the 14-day steer raises revenue per
completed order; the 43% leak itself will mainly respond to payment-step changes (Kaspi,
trust framing), which are Olive-side asks.

---

## 3. Runner-up options and when each would win

**B. Trial-first: lead with «Пробный тариф — 5 дней», no gift language at all.**
Hero sells the low-friction start; 14 days appears as the upsell inside the funnel only.
*Wins if:* Olive's data (status×period cross-tab, repeat-purchase chains) shows most 14/30-day
buyers **started** as 5-day trialists — then the page's only job is starting relationships,
and maximizing trial starts beats steering. Also wins if ad creatives promise a trial (message
match with the ad outranks on-page anchoring). *Loses now because:* it forfeits the only
strong true claim, anchors the page at 10 000 ₸/день, and we have no evidence trial→commit
conversion is high.

**C. Restore «Плати за 5 — ешь 10» — only after Olive fixes the matrix.**
`pricing_periods` says `gift_days: 5` and the funnel's built-in copy says «5 + 5» — if that is
Olive's true intent and they patch the matrix, this becomes the best offer on the page:
a doubled low-friction trial beats everything above for entry conversion, and the 477-order
demand for 5 days is proven. *Wins if and only if:* `window.OLIVE_PRICING` on the live render
shows `gift: 5` / halved perDay for period 2. Until then this copy is bait.

**D. 30-day maximization: «60 дней питания одним решением», рассрочка-led.**
*Wins if:* Kaspi рассрочка 0-0-12/24 is actually live at Olive's checkout (₸300k+ qualifies
for 24 months ≈ ₸12.5k/мес — a transformative frame). With only 43 lifetime 30-day orders and
no installment option verified, it cannot lead today.

---

## 4. What to tell Olive

1. **Three of your own sources disagree on the 5-day gift:** `pricing_periods` says
   `gift_days: 5`; the `order_funnel` block's built-in copy says «5 + 5 дней в подарок»;
   the pricing matrix (the only source the funnel charges from) says `gift: 0` at double the
   per-day rate. Decide which is the truth:
   - If **5+5 is intended**: patch the matrix (`plan × period 2`: gift 5, perDay halved).
     We will switch the page to option C — likely the strongest entry offer available.
   - If **the matrix is intended**: purge «5 + 5» from the funnel's built-in copy and from
     `pricing_periods`, so no future landing repeats the bait. As things stand, any page using
     your own default copy advertises an offer your checkout does not honour — a consumer-
     protection exposure (bait-advertising logic) and a trust cost at the payment step.
2. **Request a status×period cross-tab** of orders (pending_payment vs sent, by period).
   Our averages analysis (pending ₸81.1k vs sent ₸82.1k) suggests abandonment is uniform
   across ticket sizes, but only the cross-tab settles what drives the 43%.
3. **Payment step**: if Kaspi (QR / рассрочка) is not currently offered, that is the single
   highest-leverage change available for the 43% leak — ₸100k+ tickets qualify for 12–24-month
   installments, and ~three-quarters of KZ e-commerce payment volume is Kaspi-side.
4. **Gift-days fulfilment**: confirm operations actually deliver 28/60 days of food on the
   14/30-day periods as the matrix promises — the page will now say it loudly.

**What changes if they fix the matrix (5+5 restored):** switch to option C as the lead offer
(«Плати за 5 — ешь 10», badge «5 + 5 дней в подарок»), demote the 14-day story to the value
ladder («каждый тариф удваивается» becomes true again), keep the hero's per-day anchor at the
new 5-day effective rate (5 000 ₸/день). The current draft copy in
`landing/sections/10-funnel.json` becomes correct again almost verbatim.

---

## 5. Risks — honestly stated

1. **Higher entry commitment may cost top-of-funnel starts.** ₸140k is ~26% of an average
   Almaty monthly salary as a single prepayment. Leading with 14 days may reduce the number of
   started checkouts vs a trial-led page, even if revenue per completion rises. Mitigation:
   the trial stays visible and honestly priced; watch started-checkout counts after launch.
2. **The causality question stays open.** Our uniform-abandonment inference rests on two
   averages; if Olive's cross-tab shows pending orders do skew 5-day, the mismatch mattered
   more than we credit, and option B/C rise in value. The recommendation is robust to this
   (honest copy helps in either world), but the *expected leak impact* would need revising.
3. **Matrix dependency.** Every number in the copy («вдвое дешевле», «+14 дней», «от 5 000 ₸»)
   is read from today's matrix. If Olive edits pricing (including fixing 5+5), the copy must be
   re-verified the same day. Keep the truth-check table in §1 as the checklist.
4. **Fulfilment risk.** If gift days are a pricing-display artifact and operations do not
   actually ship 28 days on the 14-day period, the new copy would inherit a worse version of
   the same honesty problem. We flagged verification to Olive (§4.4) — do not ship the copy
   without their confirmation.
5. **Evidence limits.** The drip-pricing and Baymard findings are directionally strong but not
   meal-kit-specific; no published A/B exists for "gift promised on landing, absent at
   checkout" (we looked). The KZ 70%-abandonment figure is a survey of unnamed methodology.
   Meal-kit retention figures are analyst work (Bernstein, Second Measure), not filings, and
   the trial-length RCT is from SaaS, not food. None of the copy depends on these numbers
   being exact; the strategy depends only on the matrix (verified) and the order data (ours).

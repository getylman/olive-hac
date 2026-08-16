# WARM_ROUND — «по-домашнему» round over draft 1418

**Written:** 2026-08-16, landing-design-auditor. Base: draft 1418 (`research/preview-v1418.html`).
**User brief:** add warmth («по-домашнему, мило, тепло и здорово») via three approved
directions: (1) `gs-day` — a day-in-the-life timeline from a REAL day menu; (2) `gs-personas`
— goal/scenario cards; (3) warm polish — a WhatsApp closer after the FAQ, spring washes,
decorative gold. Data authority: `research/WARM_DATA.md` (6 verified candidate days).

This is a **spec, not an implementation**. No fragment was edited in this round.

---

## 0. Hard constraints (restated — implementers must not miss these)

1. **Viewport of record is 390×844.** Mobile first; desktop ≥900px is the secondary pass.
2. **NO animation** in the new blocks (user ban from the LK round). No `@keyframes`, no
   `transition`, no scroll reveal. The restored hero marquee (03) is the user's own exception;
   do not extend it.
3. **No external fonts, CDNs, libraries or assets.** Inline SVG only.
4. **olive.kz images are written ROOT-RELATIVE** (`/meals_uploads/…`). `validate.py`
   hard-errors on absolute `https:` URLs even for olive.kz's own assets. Every image URL in
   WARM_DATA is absolute — **strip `https://olive.kz` before use**. They 404 in the local
   preview (expected); they resolve on olive.kz.
5. **Lime `#C4F139` never carries white text** (1.31:1). **Gold `#E0A73C` is decorative-only,
   never text, never on light as a meaningful mark** (2.15 on white, 2.00 on soft, 1.71 on
   spring — all computed, all fail even the 3:1 non-text bar). The one legal gold-on-dark
   ground is deep `#2C4E28` (4.38 — passes 3:1 non-text; still no small text).
6. **Every CTA carries `data-cta`.** New values this round: `day-order`,
   `persona-1200|1500|1800|2500`, `faq-whatsapp`. Checked against the full 1418 inventory
   (19 values) — no collisions.
7. **Copy rules (user, LK round 2):** Russian; no em dashes anywhere in page copy; short
   sentences, no clause chains. Time ranges are written «с 6:00 до 9:00», never with a dash.
8. **Never fabricate** numbers, dishes, prices, reviews, certifications, claims. Every figure
   below traces to WARM_DATA (kcal/mass agree with the `meals` API 24/24), the 1418 render,
   or the pricing matrix. Scenario copy («после зала», «в офис») is interpretive marketing
   and must carry **zero numbers**.
9. Blocks are self-contained `gs-` (never `sf-`/`of-`), bring their own `<section>` +
   padding, consume colors as `var(--gs7-*, #fallback)` (tokens live in `04-skin.json`).
   `<a href="https://wa.me/…">` is legal — validate.py's EXTERNAL_REF covers media-asset
   attributes, not anchors (the footer already links wa.me).
10. Keep new blocks **transition-free**; hover states are instant color swaps.

---

## 1. Contrast — computed 2026-08-16 (WCAG 2.1, script in scratchpad)

Every pairing the new sections introduce, plus re-verified grounds:

| pair | ratio | verdict / use |
|---|---|---|
| ink `#20271A` on spring `#DCEBC4` | **12.24** | AAA — body text on spring card/section |
| muted `#4E5748` on spring `#DCEBC4` | **6.01** | AA — secondary text on spring, ≥13px |
| deep `#2C4E28` on spring `#DCEBC4` | 7.51 | AAA — titles/chips on spring (re-verified) |
| green `#3F6B39` on spring `#DCEBC4` | 4.96 | AA ≥14px bold (re-verified) |
| white on deep `#2C4E28` | 9.43 | AAA — delivery card body |
| spring `#DCEBC4` on deep `#2C4E28` | **7.51** | AAA — time label in delivery card |
| white on green `#3F6B39` | 6.22 | AA — buttons (re-verified) |
| green `#3F6B39` on white | 6.22 | AA — kcal numerals, links |
| muted `#4E5748` on white / soft | 7.55 / 7.02 | AAA (re-verified) |
| ink `#20271A` on white / soft | 15.37 / 14.28 | AAA (re-verified) |
| **gold `#E0A73C` on white / soft / spring** | **2.15 / 2.00 / 1.71** | **BANNED for text and meaningful marks** |
| gold `#E0A73C` on deep `#2C4E28` | **4.38** | legal decor/non-text on deep only |
| gold `#E0A73C` on green `#3F6B39` | 2.89 | aria-hidden decor only (existing marquee ✳) |
| white on WhatsApp brand `#25D366` | **1.98** | why the WA button stays OUR green, never brand green |
| spring2 `#C3DF9C` on white / spring | 1.46 / 1.16 | decorative lines only |
| section edge: spring vs soft `#F4F8EE` | 1.17 | weak seam — see placement mitigation §5 |
| section edge: spring vs green | 4.96 | strong seam |
| section edge: white card on spring | 1.26 | card needs shadow + hairline border |

---

## 2. `gs-day` — «Один день с Olive» (new fragment, recommend `50-day.json`)

### 2.1 Data decision — which day

**Chosen: plan 5 (рацион 1 200 ккал) · day 2026-08-20.** Reasons, in order:
- 1 200 ккал is the volume leader (474/1130 orders = 42%, BRIEF §4) — the timeline speaks to
  the dominant weight-loss segment.
- Its day total, **1 237 ккал**, is the closest of all six candidates to its plan label
  (plan 6 · 08-20 sums 1 412 vs a «1 500» label — a 6% gap a cold visitor may read as a
  catch; plan 5 · 08-18 has an 85-kcal smoothie as «Обед», which reads like starvation).
- The four names read appetizing and warm without a weak link: кесадилья, запечённый
  картофель, салат с цитрусами, поке.

The four dishes, **verbatim from WARM_DATA** (kcal/mass agree with `meals` 4/4; images
converted to root-relative):

| # | приём | блюдо (verbatim) | масса | ккал | Б/Ж/У | img (root-relative) |
|---|---|---|---|---|---|---|
| 1 | Завтрак | Кесадилья с яичным паштетом | 230 г | 459 | 36/18/39 | `/meals_uploads/6b650fd8-d551-4785-b7a5-78fdd7fd714e.png` |
| 2 | Обед | Куриная грудинка с запеченным картофелем | 230 г | 318 | 37/11/18 | `/meals_uploads/af1732f8-646f-4451-b7b7-c2dab279ff87.png` |
| 3 | Полдник | Зеленый салат с брокколи и цитрусами | 85 г | 97 | 1/8/5 | `/meals_uploads/7065d577-c00b-47b4-a370-a2fe47511c40.png` |
| 4 | Ужин | Поке с курицей | 285 г | 363 | 13/23/27 | `/meals_uploads/319ac4ae-4842-4ce3-b17c-310e34afdc4e.png` |

Day total **1 237 ккал** = 459+318+97+363 (simple sum of verified figures — legal; keep the
arithmetic in the fragment's HTML comment). **No date in visible copy** — «меню на 20
августа» goes stale in a week; the evergreen framing is «реальное меню одного дня».
Provenance (plan 5, 2026-08-20, WARM_DATA) lives in the fragment comment.

**Delivery moment:** the only real times on the page are the two slots `6:00–9:00` and
`20:00–22:00` (verified in the 1418 funnel, `data-start`/`data-end`). Never invent per-meal
clock times, and never claim which day's food the evening slot carries (unverified) — state
the slots neutrally.

### 2.2 Copy (final draft, follows copy rules)

- H2: **«Один день с Olive»**
- Lead: **«Так выглядит день на рационе 1 200 ккал. Настоящее меню, вес и КБЖУ у каждого
  блюда.»**
- Delivery card — time label: **«Утро, с 6:00 до 9:00»**; body: **«Курьер привозит сумку с
  едой на день. Слоты доставки: с 6:00 до 9:00 и с 20:00 до 22:00.»**
- Meal cards: chip = приём verbatim (Завтрак/Обед/Полдник/Ужин), name verbatim, facts line
  `459 ккал · 230 г · Б36 Ж18 У39` (funnel's own Б/Ж/У format — scent continuity).
- Total chip: **«Итого за день: 1 237 ккал»**
- CTA: **«Собрать свой день»** → `#orderFunnel`, `data-cta="day-order"`.

### 2.3 Markup skeleton

```html
<style class="gs-day-css">…</style>
<section class="gs-sec gs-day" id="gsDay">
  <div class="gs-wrap">
    <div class="gs-center">
      <h2 class="gs-h2">Один день с Olive</h2>
      <p class="gs-lead">Так выглядит день на рационе 1&nbsp;200&nbsp;ккал. Настоящее меню, вес и КБЖУ у каждого блюда.</p>
    </div>
    <ol class="gs-day__line" role="list">
      <li class="gs-day__stop">
        <span class="gs-day__dot" aria-hidden="true"></span>
        <div class="gs-day__card gs-day__card--start">
          <span class="gs-day__time"><span class="gs-day__spark" aria-hidden="true">&#10035;</span>Утро, с 6:00 до 9:00</span>
          <p class="gs-day__text">Курьер привозит сумку с едой на день. Слоты доставки: с 6:00 до 9:00 и с 20:00 до 22:00.</p>
        </div>
      </li>
      <li class="gs-day__stop">
        <span class="gs-day__dot" aria-hidden="true"></span>
        <article class="gs-day__card">
          <img class="gs-day__img" src="/meals_uploads/6b650fd8-d551-4785-b7a5-78fdd7fd714e.png"
               alt="Кесадилья с яичным паштетом" width="340" height="250" loading="lazy" decoding="async">
          <div class="gs-day__body">
            <span class="gs-day__meal">Завтрак</span>
            <h3 class="gs-day__name">Кесадилья с яичным паштетом</h3>
            <p class="gs-day__facts">459&nbsp;ккал · 230&nbsp;г · Б36 Ж18 У39</p>
          </div>
        </article>
      </li>
      <!-- Обед, Полдник, Ужин: same shape -->
    </ol>
    <div class="gs-day__total">
      <span class="gs-day__sum">Итого за день: 1&nbsp;237&nbsp;ккал</span>
      <a class="gs-btn gs-btn--big" href="#orderFunnel" data-cta="day-order">Собрать свой день</a>
    </div>
  </div>
</section>
```

Notes: `<ol>` because a day genuinely is a sequence (numbering stays invisible — the meal
labels carry order); `role="list"` restores list semantics that `list-style:none` drops in
Safari/VO. Meal cards are **not links** — no fake affordance; the one action is the CTA.
`loading="lazy"` is correct here (vertical, below the fold) — unlike the carousel, where
lazy is banned (handoff/implementer LK-2 note).

### 2.4 Visual spec (mobile 390)

- **Section ground:** solid spring with a soft fade-out into the FAQ below:
  `background:linear-gradient(180deg, var(--gs7-spring,#DCEBC4) 0, var(--gs7-spring,#DCEBC4) calc(100% - 96px), var(--gs7-soft,#F4F8EE) 100%)`.
  This is the round's «spring wash»: the strong seam is at the top (green marquee above,
  4.96), the weak spring/soft seam (1.17) is dissolved into a deliberate fade.
- **Spine:** `.gs-day__line{list-style:none;margin:28px 0 0;padding:0 0 0 26px;position:relative;display:flex;flex-direction:column;gap:14px}`
  with `::before` vertical rule `left:7px;width:2px;background:rgba(44,78,40,.28)` (decor).
- **Dots:** 14px circle, `background:var(--gs7-green,#3F6B39)`, `box-shadow:0 0 0 3px rgba(255,255,255,.85)`,
  absolutely positioned on the spine, vertically centered on the card's first line.
  Green on spring = 4.96 ≥ 3:1, legal as a UI mark.
- **Meal card:** white, `border-radius:var(--gs-r-card,22px)`, `border:1px solid rgba(32,39,26,.08)`,
  `box-shadow:var(--gs-sh-card)`, `display:flex;gap:12px;padding:12px;align-items:center`.
  Photo `width:96px;height:71px` (340:250 kept), `border-radius:12px;object-fit:cover;flex:0 0 auto`.
  Meal chip: spring bg, deep text (7.51), `font:700 11px/1.3 var(--gs-text)`, uppercase,
  `letter-spacing:.04em`, pill radius — same vocabulary as `.gs-dish__cat`.
  Name: `font:700 1rem/1.3 var(--gs-text)`, ink. Facts: `font:600 .8125rem/1.4 var(--gs-text)`,
  muted `#4E5748` (6.01 on spring, but it sits on the WHITE card = 7.55), `font-variant-numeric:tabular-nums`.
- **Delivery card (`--start`):** deep `#2C4E28` bg, same radius/shadow. Time label:
  `color:var(--gs7-spring,#DCEBC4)` (7.51), `font:800 .9375rem/1.3 var(--gs-display)`.
  Body: white (9.43), `font:500 .9375rem/1.5 var(--gs-text)`. The `✳` spark before the time
  label is `color:var(--gs7-gold,#E0A73C)` — gold on deep = 4.38, the only legal gold ground;
  it is `aria-hidden` decor. **This is the round's entire gold budget inside gs-day.**
- **Total row:** `.gs-day__total{display:flex;flex-direction:column;gap:14px;align-items:center;margin-top:26px}`.
  Sum chip: white bg pill, deep text `font:800 1.0625rem var(--gs-display)`, tabular-nums,
  padding `10px 18px` (white pill on the fading ground keeps 7.51+ everywhere).
  CTA is the shared `.gs-btn--big` (white on green 6.22, min-height 58px ≥ 44px target).
  `@media (max-width:560px){.gs-day__total .gs-btn{width:100%}}` — matches other sections.
- **Spacing:** section keeps `.gs-sec` 56px (88px ≥1024). Card gap 14px. No transitions.

### 2.5 Desktop ≥900px

Keep the timeline **vertical and centered**: `.gs-day__line, .gs-day__total{max-width:640px;margin-left:auto;margin-right:auto}`;
photo grows to 116×85; type unchanged. A horizontal 5-stop timeline was considered and
rejected: photos + КБЖУ don't fit 5-across under 1200px without shrinking below legibility,
and the vertical read is the honest chronology.

---

## 3. `gs-personas` — «Рацион под вашу цель» (new fragment, recommend `20-personas.json`)

### 3.1 Data (all verified in the 1418 funnel render, lines 757–819)

The four goal labels are the funnel's own plan-card CTAs — reuse them **verbatim** so the
cards scent-match the configurator one screen up:

| goal label (verbatim) | ration | блюд/день | price floor (funnel prints it) | data-cta |
|---|---|---|---|---|
| Похудей активно | 1 200 ккал | 4 | от 5 000 ₸ в день | `persona-1200` |
| Похудей легко | 1 500 ккал | 4 | от 5 500 ₸ в день | `persona-1500` |
| Удержание формы | 1 800 ккал | 5 | от 6 000 ₸ в день | `persona-1800` |
| Набор массы | 2 500 ккал | 6 | от 6 500 ₸ в день | `persona-2500` |

«от» is load-bearing: the floor is the halved 14/30-day rate (matrix-true; the funnel prints
the identical string). Dish counts also match the FAQ answer. **No popularity badge on any
card** — the funnel's own (platform-emitted) «Популярное» badge sits on 1 500, while orders
data says 1 200 leads; adding our own badge either duplicates or contradicts it. Deliberate
omission.

### 3.2 Copy (final draft)

- H2: **«Рацион под вашу цель»**
- Lead: **«Нет времени готовить, после зала или обед в офис. Выберите цель, меню соберём мы.»**
  (all three approved scenarios in one line, zero numbers)
- Card notes (scenario voice, zero invented numbers):
  - 1 200: **«Самый лёгкий рацион. Четыре блюда в день.»** («самый лёгкий» = true min of range)
  - 1 500: **«Мягкий режим на каждый день. Четыре блюда в день.»**
  - 1 800: **«После зала и в офис. Пять блюд в день.»**
  - 2 500: **«Самый плотный рацион. Шесть блюд в день.»** (true max of range)
- Card affordance: **«Выбрать →»** (the whole card is the link).

### 3.3 Markup skeleton

```html
<style class="gs-who-css">…</style>
<section class="gs-sec gs-who" id="gsWho">
  <div class="gs-wrap gs-center">
    <h2 class="gs-h2">Рацион под вашу цель</h2>
    <p class="gs-lead">Нет времени готовить, после зала или обед в офис. Выберите цель, меню соберём мы.</p>
    <div class="gs-who__grid">
      <a class="gs-who__card" href="#orderFunnel" data-cta="persona-1200">
        <span class="gs-who__goal">Похудей активно</span>
        <span class="gs-who__kcal">1&nbsp;200 <small>ккал в день</small></span>
        <span class="gs-who__note">Самый лёгкий рацион. Четыре блюда в день.</span>
        <span class="gs-who__price">от 5&nbsp;000&nbsp;₸ в&nbsp;день</span>
        <span class="gs-who__go" aria-hidden="true">Выбрать →</span>
      </a>
      <!-- 3 more cards, same shape -->
    </div>
  </div>
</section>
```

### 3.4 Visual spec (mobile 390)

- **Section ground — the second «spring wash»:** melt into both soft neighbours instead of
  hard white seams:
  `background:linear-gradient(180deg, var(--gs7-soft,#F4F8EE) 0, #fff 120px, #fff calc(100% - 120px), var(--gs7-soft,#F4F8EE) 100%)`.
  The funnel above and the dish carousel below are both `#F4F8EE`; today they merge directly
  (soft-on-soft). This section inserts a white breath between them and fades at both edges,
  so there is no hard seam anywhere — the cards carry the structure (donor precedent,
  SKIN_V7 §5).
- **Grid:** `display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:28px;text-align:left`
  (same rhythm as `.gs-plans`); `@media (min-width:900px){grid-template-columns:repeat(4,1fr)}`.
- **Card:** white, `border:2px solid #E3E8DE;border-radius:18px;padding:16px 14px;min-height:150px`,
  `display:flex;flex-direction:column;gap:6px`, `box-shadow:var(--gs-sh-card)`,
  `text-decoration:none`. Hover/focus-visible: `border-color:var(--gs7-green,#3F6B39)` —
  instant, no transition. Whole card ≈171×150px at 390px, far over the 44px target.
- **Type in card:** goal `font:800 1.0625rem/1.15 var(--gs-display)`, ink, `letter-spacing:-.02em`
  («Удержание формы» wraps to two lines at 171px — reserve `min-height:2.3em` so the four
  cards' kcal lines align). Kcal `font:800 1.375rem/1 var(--gs-display)`, green (6.22),
  tabular-nums; its `small` = `font:600 .75rem var(--gs-text)`, muted. Note
  `font:500 .8125rem/1.45 var(--gs-text)`, muted (7.55). Price `font:700 .8125rem var(--gs-text)`,
  deep. `Выбрать →` `font:700 .9375rem var(--gs-text)`, green, `margin-top:auto`.
- **Differentiation from gs-plans** (both are 2×2 white-card grids to #orderFunnel): personas
  lead with the goal *words* and a spring-chip-free, text-first face; plans lead with day
  numerals and badges. No gold here — the round's boldness is spent in gs-day.

### 3.5 Desktop ≥900px

4 columns, `max-width` inherited from `.gs-wrap` (1200px). Goal font may step to 1.1875rem.
Nothing else changes.

---

## 4. `gs-ask` — WhatsApp closer (new fragment, recommend `65-ask.json`) + polish rules

### 4.1 Copy (final draft)

- Title: **«Остались вопросы?»**
- Text: **«Напишите нам в WhatsApp. Поможем выбрать рацион и ответим про доставку.»**
  (service promise, no response-time claim — response times are unverified)
- Button: **«Написать в WhatsApp»** → `https://wa.me/77008702626`, `target="_blank"
  rel="noopener"`, `data-cta="faq-whatsapp"`.
- Phone, plain text: **«+7 700 870-26-26»** (number verified: footer wa.me link + trust copy
  in the 1418 render).

### 4.2 Markup skeleton

```html
<style class="gs-ask-css">…</style>
<section class="gs-ask">
  <div class="gs-wrap">
    <div class="gs-ask__card">
      <span class="gs-ask__icon" aria-hidden="true"><!-- inline SVG bubble, see 4.3 --></span>
      <div class="gs-ask__body">
        <h2 class="gs-ask__title">Остались вопросы?</h2>
        <p class="gs-ask__text">Напишите нам в WhatsApp. Поможем выбрать рацион и ответим про доставку.</p>
      </div>
      <a class="gs-btn gs-ask__btn" href="https://wa.me/77008702626" target="_blank" rel="noopener" data-cta="faq-whatsapp">Написать в WhatsApp</a>
      <span class="gs-ask__phone">+7&nbsp;700&nbsp;870-26-26</span>
    </div>
  </div>
</section>
```

### 4.3 Visual spec

- **Section:** `background:var(--gs7-soft,#F4F8EE);padding:0 0 56px` — zero top padding so it
  reads as the FAQ's own closing card (the FAQ block above is `l-section--soft`, same
  `#F4F8EE`; this soft-on-soft merge is **intentional** — one visual unit).
- **Card:** spring `#DCEBC4` bg, `border-radius:var(--gs-r-big,26px)`, `padding:24px 20px`,
  `display:flex;flex-direction:column;gap:12px;align-items:flex-start;max-width:560px;margin:0 auto`.
  Spring card on soft ground: the 1.17 edge is carried by radius + `box-shadow:var(--gs-sh-card)`.
- **Icon:** 44px white circle, inside a simple hand-drawn bubble glyph, green stroke —
  suggested minimal path (implementer may refine, keep it this simple):
  `<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 3a9 9 0 0 0-7.8 13.5L3 21l4.7-1.2A9 9 0 1 0 12 3Z" stroke="#3F6B39" stroke-width="2" stroke-linejoin="round"/><circle cx="12" cy="12" r="1.6" fill="#3F6B39"/><circle cx="8.4" cy="12" r="1.6" fill="#3F6B39"/><circle cx="15.6" cy="12" r="1.6" fill="#3F6B39"/></svg>`
- **Type:** title `font:800 1.375rem/1.1 var(--gs-display)`, deep (7.51 AAA on spring);
  text `font:500 .9375rem/1.5 var(--gs-text)`, ink (12.24); phone `font:700 .9375rem var(--gs-text)`,
  deep, tabular-nums.
- **Button:** the shared `.gs-btn` — OUR green `#3F6B39` (white 6.22), full-width under 560px.
  **Never WhatsApp brand green `#25D366`** — white on it is 1.98 (computed), and an
  off-palette green would be the only alien hue on the page.
- **h2 is fine here** (qa.py enforces exactly one `h1`; the FAQ accordion itself emits h2s).

### 4.4 Warm-polish rules for the whole round

- **Spring washes** are implemented as the two section gradients (§2.4, §3.4) plus this
  spring card — not as blanket recoloring. Do not add further spring grounds without
  re-checking the §5 seam table.
- **Gold budget:** exactly one meaningful-adjacent use (the ✳ on the deep delivery card,
  4.38, aria-hidden) plus the pre-existing marquee ✳ (2.89 on green, aria-hidden,
  grandfathered). Optional P2: a short (≤64px) gold underline SVG swash under the gs-day H2,
  `aria-hidden`, pure decoration — legal because decorative, but skip it if in doubt; gold
  fails 3:1 on every light ground.
- **No new fonts, no new hues.** The round introduces zero new hex values — it recombines
  the SKIN_V7 palette.

---

## 5. Placement map for the architect

Recommended slots (new fragments in bold):

| slot | fragment | ground | seam above → below |
|---|---|---|---|
| 03 | hero | white + spring arc | — |
| 05–09 | funnel bands | — | — |
| 10 | order_funnel | soft `#F4F8EE` | white→soft: weak, existing, accepted |
| **20** | **20-personas.json** `gs-who` | soft→white→soft gradient | **both seams dissolved by design** (fixes today's funnel→dishes soft-on-soft merge) |
| 40 | dishes carousel | soft | gradient→soft: continuous |
| 45 | facts row | green `#3F6B39` | soft→green: strong (4.96) |
| **50** | **50-day.json** `gs-day` | spring→soft fade | green→spring: strong (4.96); spring→soft: dissolved by the fade |
| 60 | faq | soft | continuous |
| **65** | **65-ask.json** `gs-ask` | soft (spring card) | soft→soft: **intentional merge** with FAQ |
| 70 | plans | white | soft→white: weak, existing precedent (cards carry rhythm) |
| 80 | summary bar + footer | soft footer | existing |

- Slots 20, 50, 65 are free (20-trust / 50-advantages were deleted in the LK round; 65 is
  unused). No renumbering of existing fragments is needed. 45-marquee stays where it is —
  the green ribbon is the divider between the two food sections.
- Narrative check (cold visitor): attention (hero) → action (funnel) → self-ID pushing back
  to action (personas) → proof-breadth (dishes) → facts → proof-depth/warmth (day) →
  objections (faq) → human fallback (ask/WhatsApp) → price closing (plans).
- `gs-ask` also serves the payment-anxiety lever: a visible human channel right before the
  price block (43% of orders die at `pending_payment`; a reachable human is an on-page trust
  signal that costs nothing).
- **Body bottom padding / summary bar:** unchanged — new sections sit above 70/80 and add
  no fixed elements.

## 6. Acceptance checklist (for the ship loop)

1. `grep` the three new fragments for `@keyframes|animation|transition` → **zero hits**.
2. `grep -o 'https://olive.kz' landing/sections/{20,50,65}-*` → **zero hits** (root-relative
   images only); the 4 gs-day images 404 in local preview — expected.
3. `grep -o '—'` (em dash) over the three fragments' visible copy → zero hits.
4. New `data-cta` set present in the server render: `day-order`, `persona-1200`,
   `persona-1500`, `persona-1800`, `persona-2500`, `faq-whatsapp` — and the old 19 intact.
5. Dish data byte-matches §2.1 (names/mass/kcal/Б-Ж-У verbatim; total printed only as
   «1 237»).
6. Goal labels byte-match the funnel's own (`Похудей активно` etc.).
7. No `content:` declarations outside `09-pseudo.json` (repo rule); the new blocks use
   `content` for nothing — the ✳ is a markup character, not pseudo-content, precisely so the
   droppable-band rule holds.
8. 390×844 browser pass: no horizontal scroll; card text ≥13px; every seam reads per §5;
   `wa.me` opens the chat with the number prefilled.

## 7. Open questions / risks for the architect

- **Menu rotation risk (P2):** the four gs-day dishes are real, but the visible day-menu on
  olive.kz rotates. Copy deliberately says «реальное меню одного дня», not «завтра вы
  получите» — do not strengthen that claim. If Olive prunes old `/meals_uploads/` files the
  images could 404 someday; the card layout must not collapse without the image
  (width/height attrs reserve space; a `background:#F4F8EE` on `.gs-day__img` keeps the slot
  clean).
- **«Самый лёгкий рацион» wording** was chosen over any outcome promise («быстрый
  результат» would be a weight-loss claim). Keep it.
- **Page weight:** +4 images (~300–450 KB), all `loading="lazy"`, below the fold — no LCP
  impact. Do not promote them to eager.
- **If the architect re-orders sections**, re-derive the §5 seam table — the two gradients
  are tuned to their specific neighbours (green above gs-day; soft above and below gs-who).
- **Not buildable inside the block system, so not specced:** injecting the WhatsApp card
  *inside* the platform FAQ accordion (overrides can't insert html into a rendered block
  reliably) — the attached-section approach in §4.3 is the honest equivalent.

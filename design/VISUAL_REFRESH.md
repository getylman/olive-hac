# Visual refresh — ordering UX to best-in-class

**Status: buildable spec.** Written 2026-08-16 by the landing-design-auditor against draft
**v1133** (`research/preview-v1133.html`), the funnel source (`research/funnel-1058.html`,
`research/order-funnel.css`) and web research performed this run. Viewport of record 390×844.
Every contrast ratio below is **computed** (WCAG 2.x relative luminance), never estimated.

Implements nothing. Implementer edits the named fragments; `landing/config.json` stays
generated. Drafts only; never `--status active`.

---

## 0. Reference base — what was actually observed vs merely published

| source | status | what it gave |
|---|---|---|
| **dodopizza.ae (+ /dubai/product/pepperoni) / dodopizza.pl** (Dodo IS ordering front-end) | **observed 2026-08-16** — raw SSR markup + styled-components CSS fetched | product card anatomy, segmented control with sliding indicator (`data-testid="size-selector-indicator"`, 200ms ease-out), total-in-button, sticky blurred footer. `dodopizza.kz/.ru/.by/.kg/.uz` all serve a Servicepipe JS challenge to non-browser agents; .ae/.pl run the identical front-end (same bundle and testids; .ae even ships a `ru-RU` locale). The "from-price" pattern was observed in English («from AED 29»); the KZ «от X ₸» form is inferred, not seen. |
| **Drinkit** | ordering is **app/kiosk-only** (observed: drinkit.io is a Tilda marketing site, drinkit.ru a Webflow franchise site) | documented concepts only: «100% of our orders are placed digitally» (dodobrands.io/franchising/drinkit/); «guests can customise drinks in the app, while our team monitors ingredients, calories, and allergens» (drinkit.io); ingredient-level composition editing + saved «Mixes» (App Store id1495622004). Palette: deep blues `#182DA8`/`#334CDB` — deliberately opposite Dodo's orange, same Shift family. **No visual claims about the app's ordering UI are made — we could not observe it.** |
| shift.dodobrands.io | fetched | Shift design system exists (covers Dodo Pizza + Drinkit); tokens not public. |
| surf.ru/cases/dodo-pizza | fetched | Dodo app is geolocation-first: delivery zone is resolved *before* cart-building; post-launch the app took 40% of online orders. |
| vc.ru/design/172523 | fetched | Dodo's design process; their redesign **merged two checkout screens into one** under a «minimize time from login to purchase» strategy — fewer perceived steps, not more. |
| Baymard Institute (checkout & mobile studies) | published research, fetched by the evidence run | surprise costs = top abandonment driver; order summary visible throughout; **visual encapsulation** of the payment area (border, shading, one recognizable mark) raises perceived security; ~19% abandon over gut-level trust; open promo fields are an exit ramp. |
| NN/g (wizards, progress) | published | label the current step; perceived effort matters more than raw step count. |
| Gourville, *«pennies-a-day»* (J. Consumer Research) | published | per-day reframing lifts acceptance (52% vs 30% in the canonical study); caveat — aggregate framing wins when the per-day number itself is large. |
| GrowthRock mobile sticky-CTA test | published | +5.2% from a slide-up sticky order bar; implementation quality decides the sign. |
| GoodUI pattern tests (#487 et al.) | published | «most popular» tier badges and price anchors are repeatedly-tested winners. |

Anything below marked **[own observation]** is my design judgment, not a sourced claim.

---

## 1. What we're borrowing, from whom, for which part of our page

**B1 — Total lives in/at the action, always visible.** Dodo's add-to-cart is literally
«Add to Cart for <span class="money">AED 46</span>» inside a sticky footer
(`.bhHBTV{position:sticky;bottom:0}`, `padding-bottom:calc(env(safe-area-inset-bottom)+12px)`)
— observed. Baymard: keep the order summary visible throughout. **Ours:** the funnel already
has the right skeleton (`of-mbar` prints the per-day price above «Далее»; `of-total__sum` at
checkout) — it is set at 16px/20px system font, visually weaker than the buttons around it.
We make the money the loudest thing on the screen (§3 T-rules).

**B2 — Price as a quiet pill, "from" framing, no description noise.** Dodo product cards
carry no bare price text and **no description at all**: photo → title → price inside a grey
secondary pill button «from AED 29» (`border-radius:9999px`, surface `#F1F3F6`, ink
`#171717`, min-height 28px) — observed. Regular cards have no border or shadow; only
promo cards get a ground. Struck old prices use an orange SVG stroke at 0.55 opacity —
a pattern we deliberately do **not** copy: we have no real discounts to strike, and
inventing one is fraud. **Ours:** plan cards already print «от 5 000 ₸/день»; we raise it
from 14px to a weighted tabular element (§3 T3) and add nothing else to the card.

**B3 — Per-day framing everywhere, totals only at checkout.** Gourville's pennies-a-day
plus the Dodo "from" pattern. Our matrix-true per-day price (5 000 ₸/день on 14/30) is the
good number; the 140 000 ₸ total is the alarming one. Keep per-day in hero, plan cards,
mbar, orderbar; the full total appears at checkout where Baymard demands an itemised
summary. This is already mostly true on v1133 — the refresh only amplifies it.

**B4 — Selection is a fill, never a lone border.** Dodo's segmented control moves a solid
sliding thumb (`.hvpbAq`, 200ms ease-out) and topping tiles change border *and* show a
selected-icon — observed. Matches our computed rule (lone lime border = 1.31, illegal).
**Ours:** washed backgrounds added to every `is-selected` state the funnel paints with a
border or off-brand tint (§3 S-rules).

**B5 — Encapsulate the payment moment.** Baymard: users judge payment-field safety by
*visual* robustness of the enclosure. **Ours:** the checkout `of-total` card gets a
distinct border + elevated shadow, and a truthful reassurance line «Платёж обрабатывает
Halyk Bank ePay» (§3 E-rules). Attacks the 43% `pending_payment` leak directly.

**B6 — Labeled progress, never added steps.** NN/g: show where the user is; Baymard: steps
must map 1:1 to what actually happens; Dodo's own redesign *merged* two checkout screens
into one to cut perceived effort (vc.ru). The funnel's 4-step main path (menu → preview →
delivery → checkout) has zero step indication. CSS-only «Шаг N из 4» labels (§3 P-rules) —
labelling what exists, adding nothing.

**B7 — One accent, calm neutrals.** Dodo uses its orange `rgb(255,100,0)` on the primary
CTA and almost nowhere else; secondary controls are grey pills — observed. **Ours:** lime
stays reserved for the primary action (orderbar button, offer chip); the funnel's neutral
grey scheme is kept, its illegal greys repaired (§3 C-rules).

**B8 — Brand type continuity through the money step.** **[own observation]** Our page sets
Loos Wide/Museo, then the funnel switches to `-apple-system/SF Pro` at the exact moment
money appears — the checkout looks like a different (cheaper) product than the ad landing.
Baymard's trust findings are about gut feeling at payment; type discontinuity is a gut
signal. One rule fixes it: `.of` declares `font-family` exactly once (order-funnel.css:25),
so a single `#orderFunnel` override rebrands every screen (§3 T1).

**B9 — Imageless cards carried by composition data at typographic scale.** MCP exposes no
dish images and we invent none. Drinkit's documented position — guests customise while the
brand «monitors ingredients, calories, and allergens» (drinkit.io) — makes composition
transparency itself the product surface, which is exactly the data we *do* have (297 dishes
with kcal/Б-Ж-У). Plus **[own observation]**: let the number do the work — the kcal numeral
becomes the card's "image" at display scale, category chip as the color cue (§2.2).

**B10 — Motion budget 150–200ms ease-out, color/transform only.** Dodo transitions:
buttons 200ms, tiles 150ms — observed. The funnel already animates screen-entry and guards
`prefers-reduced-motion` (order-funnel.css:1303) — **verified; do not duplicate the guard,
do not add new animation.**

---

## 2. Specs — our own blocks (low risk: pure `gs-`, no funnel contact)

### 2.1 `gs-orderbar` — price into the bar (fragment `landing/sections/80-orderbar.json`)

Borrow B1/B3. Replace the offer span content (markup of *our own* block):

```html
<span class="gs-orderbar__offer">
  <b class="gs-orderbar__price">от 5 000 ₸/день</b><br>+14 дней в подарок
</span>
```

CSS added to the block's `<style>`:

```css
.gs-orderbar__price{display:block;font:700 1rem/1.2 var(--gs-display,"Loos Wide",Arial,sans-serif);
  color:var(--l-green-dark,#194536);font-variant-numeric:tabular-nums;text-transform:none;letter-spacing:0}
```

Truth check: 5 000 ₸/день is the rendered matrix `perDay` for 14/30-day on the cheapest
plan — the same "from" price the hero states. Green on white 10.79. Keep button text
«Собрать рацион» and `data-cta="orderbar"` untouched.
*Considered and rejected:* Dodo's blur-gradient footer (`backdrop-filter`) — contrast of
lime button and green text over a blurred, content-dependent ground cannot be verified;
the solid white bar stays.

### 2.2 `gs-dish` — kcal numeral as the image (fragment `landing/sections/40-dishes.json`)

Borrow B9. Two CSS changes in the block's own `<style>` (no markup change needed):

```css
.gs-dish__kcal{font-size:var(--gs-fs-h2,1.5625rem)}       /* 21px → 25px display numeral */
.gs-dish__body{gap:var(--gs-sp-3,12px)}                    /* air around the numeral */
```

Green `#194536` numeral on white 10.79; `small` mass stays 14px muted 6.48. Cards remain
data-verbatim from `meals` — no images, no invented content.

### 2.3 No other `gs-` block changes

Trust strip, steps, quality, FAQ, CTA already follow the system. Do not add sections: the
funnel-first order on v1133 is correct (value → proof → ask → objections).

---

## 3. Specs — restyling Olive's funnel (CSS-only, higher risk, separate risk profile)

**Mechanism:** every rule ships as **static CSS appended to
`landing/sections/05-style.json`** inside the existing `<style class="gs-fixes">` tag, as a
clearly-commented "Visual refresh" band *after* round-1 rules 1–7. Never via
`meta.overrides` (single DCL pass — flashes and misses rebuilt nodes). Never touching
funnel markup or JS. All selectors are `#orderFunnel`-scoped: funnel internals are
single-class `(0,1,0)` and the funnel injects its CSS in-body, so ID-scoping `(1,x,0)` wins
independent of source order (WP-F1 table). `validate.py` will warn on `of-*` selectors —
expected, deliberate-restyle case.

### T — typography continuity (B8, B1)

| # | rule | must beat | their spec | ours |
|---|---|---|---|---|
| T1 | `#orderFunnel{font-family:"Museo Sans Cyrl",-apple-system,"Segoe UI",Roboto,Arial,sans-serif}` | `.of` font-family (order-funnel.css:25 — the **only** family declaration; `.of-textarea` inherits) | (0,1,0) | (1,0,0) |
| T2 | `#orderFunnel .of-plan__num,#orderFunnel .of-mbar__val,#orderFunnel .of-total__sum,#orderFunnel .of-fcard__total-val,#orderFunnel .of-head__title{font-family:"Loos Wide",Arial,sans-serif;font-variant-numeric:tabular-nums}` | each target (0,1,0) | (0,1,0) | (1,1,0) |
| T3 | `#orderFunnel .of-mbar__val{font-size:21px}` · `#orderFunnel .of-total__sum{font-size:22px}` · `#orderFunnel .of-plan__price{font-size:15px}` · `#orderFunnel .of-plan__perday{font-size:12px}` · `#orderFunnel .of-hero__title{font-size:20px;font-weight:700;line-height:1.25}` | (0,1,0) each | — | (1,1,0) |

Notes: Loos Wide only at sizes ≥20px and never uppercase below 20px — T2 targets are 20–22px
digits/titles, compliant. `of-plan__price` stays Museo (15px is below the Loos floor) —
the *weight* hierarchy (700 + tabular) carries it. Hero title stays Museo: Loos Wide's wide
letterforms would wrap the 69-char `hero_title` to ~5 lines at 390px **[own observation]**.

### C — contrast repairs (P0 — this is price text on the payment path)

Computed failures in the funnel as shipped (all on white cards unless noted):

| text | color | size | ratio | verdict |
|---|---|---|---|---|
| `of-dd__price` — **the period's price in the duration picker** | `#888` via `--of-muted` | 13px | **3.54** | FAIL AA |
| `of-total__plansub`, `of-fcard__total` label, `of-datecard__time`, `of-pay__hint` (11px) | `#888` | 11–14px | **3.54** | FAIL AA |
| `of-hint`, pending `of-step__title` | `#aaa` | 12–15px | **2.32** | FAIL |
| `of-err` error text | `#e53935` | 12px | **4.23** | FAIL AA |

Verified replacements: `#6B6B6B` = 5.33 on white, 4.68 on `#f0f0f0` bg, 4.67 on `#EAF3DF`
wash — passes everywhere it will sit. Error `#B42318` = 6.57 on white, 5.76 on wash.

| # | rule | must beat | ours wins |
|---|---|---|---|
| C1 | `#orderFunnel{--of-muted:#6B6B6B}` (merge into round-1 rule 4's declaration block) | `.of{--of-muted:#888}` (0,1,0) | (1,0,0); fixes every `var(--of-muted)` consumer at once |
| C2 | `#orderFunnel .of-hint{color:#6B6B6B}` | `.of-hint` (0,1,0) | (1,1,0) |
| C3 | `#orderFunnel .of-step.is-pending .of-step__title{color:#6B6B6B}` | (0,3,0) | (1,2,1) — ID outranks any class count |
| C4 | `#orderFunnel .of-err{color:#B42318}` | `.of-err` (0,1,0) | (1,1,0) |
| C5 | `#orderFunnel .of-pay__hint{color:#6B6B6B}` (literal `#888`, not var) | (0,1,0) | (1,1,0) |

Already fixed by round-1 rule 4 (vars): buttons, step numbers, plan borders, calendar
selected day (white on `#194536` = 10.79), pay-opt selected, radio dots. Do not re-declare.

### S — selection states (B4)

| # | rule | must beat | note |
|---|---|---|---|
| S1 | `#orderFunnel .of-plan.is-selected{background:#EAF3DF}` | `.of-plan` bg (0,1,0) | border already brand-green via vars (10.79 non-text); wash adds the redundant cue. All card text re-verified on `#EAF3DF`: ink 15.66–16.53, `#555` perday 6.53, muted `#6B6B6B` 4.67 — pass |
| S2 | `#orderFunnel .of-dd__opt.is-selected{background:#EAF3DF}` | (0,2,0) hard-codes `#f3f9f0` | brand-consistent wash; green text 9.45 |
| S3 | `#orderFunnel .of-menucal__time.is-selected{background:#EAF3DF;color:#194536;border-color:#194536}` | (0,2,0) hard-codes `#eef6e9`/`--of-green-d` | 9.45 |
| S4 | `#orderFunnel .of-weekday.is-on{color:#194536}` | (0,2,0) hard-codes `#2f7d33` (4.79 — legal but prototype green) | brand green on `#f2fbdf` = 10.09 |

### O — offer banner accent (B7)

| # | rule | must beat | note |
|---|---|---|---|
| O1 | `#orderFunnel .of-offer__badge{background:var(--l-lime,#C4F139);color:#194536}` | `.of-offer__badge` (0,1,0) white-on-`rgba(255,255,255,.22)` | current blend over the green banner computes to `#4c6e62`, white on it = 5.65 — *legal*, so this is a brand upgrade, not a compliance fix. Lime chip on green banner, green text 8.22. The **one** lime moment on screen 1 |

### P — progress labels (B6) — P1, ships with a caveat

The funnel's 4 `of-topbar`s (screens `preview`, `prefs`, `delivery`, `checkout`) hold only
a back button. Pseudo-content on a flex container becomes a flex item:

```css
#orderFunnel .of-topbar::after{flex:1;text-align:center;margin-right:36px;
  font:600 13px/1.3 "Museo Sans Cyrl",Arial,sans-serif;color:#6B6B6B}
#orderFunnel .of-screen[data-screen="preview"]  .of-topbar::after{content:"Шаг 2 из 4"}
#orderFunnel .of-screen[data-screen="prefs"]    .of-topbar::after{content:"Настройка меню"}
#orderFunnel .of-screen[data-screen="delivery"] .of-topbar::after{content:"Шаг 3 из 4"}
#orderFunnel .of-screen[data-screen="checkout"] .of-topbar::after{content:"Шаг 4 из 4"}
```

`#6B6B6B` on `#f0f0f0` topbar = 4.68. `prefs` is an optional detour off step 2 — it gets a
name, not a number (Baymard: steps must map 1:1 to reality). **Caveat:** copy inside CSS
`content` is brittle against funnel renames and is announced by most screen readers (here
that is accurate information, so acceptable). If Olive ever adds real steppers, delete.

### E — payment encapsulation (B5) — P0 core + P1 pseudo-line

```css
/* E1 — P0: the money card looks like a vault, not another list item */
#orderFunnel .of-total{border:1.5px solid #d7ddd8;box-shadow:0 10px 30px rgba(0,0,0,.08)}
/* E2 — P1: truthful processor line under the pay button (pseudo-content caveat as in P) */
#orderFunnel .of-total::after{content:"Платёж обрабатывает Halyk Bank ePay";
  text-align:center;font:500 12px/1.4 "Museo Sans Cyrl",Arial,sans-serif;color:#6B6B6B}
```

Beats `.of-total` (0,1,0) with (1,1,0). `of-total` is a flex column, so `::after` lands
below the pay button. The claim is true: the ePay script ships on the page (AUDIT §2) and
the FAQ states it. E2 carries the same CSS-content caveat as P — flag both to the user
before shipping if in doubt; E1 is unconditional.

### D — promo de-emphasis (Baymard exit-ramp) — P2

```css
#orderFunnel .of-promo__input{background:#f7f7f7;border-color:transparent}
#orderFunnel .of-promo__btn{background:transparent;color:#194536;border:1.5px solid #d7ddd8}
```

Quiet, still discoverable, still functional. Full collapse-behind-a-link needs markup —
**not allowed in the funnel; not attempted.**

### What we deliberately do NOT touch in the funnel

- `of-btn` geometry, `of-mbar` positioning/stacking, `.d-none`, `of-screen` display logic,
  modal sheet, calendar layout — anything whose failure blocks a tap or hides a control.
- No `display`/`visibility`/`position` changes on any functional node. Every rule above is
  color, font, background, border, shadow, or pseudo-content on non-interactive containers.
- `#orderBtn` / `of-btn` labels — text wraps the live price span; never overridden.
- No new animation; the funnel's own motion + reduced-motion guard (verified present) stand.

---

## 4. Priorities — by expected effect on completed orders

**P0**
1. **C1–C5 contrast repairs** — the *price of the period* (`of-dd__price`, 3.54:1 at 13px)
   is currently the least-legible text on the payment path. WCAG + Baymard clarity; zero risk.
2. **T1–T3 money prominence + type continuity** — total-in-context (Dodo B1, Baymard
   summary-visible, Gourville per-day) and no font-switch at the money step (B8).
3. **E1 payment encapsulation** — Baymard perceived-security, aimed square at the 43%
   `pending_payment` leak. (E2 processor line: P1 — pseudo-content caveat.)

**P1**
4. O1 lime offer chip (B7, brand accent where the offer is argued).
5. P step labels (NN/g B6) — with the stated caveat.
6. §2.1 orderbar per-day price (B1/B3, GrowthRock; our own block, trivially safe).
7. S1–S3 selection washes (B4, redundant selected cues).

**P2**
8. S4 weekday brand green; D promo de-emphasis; §2.2 dish numeral scale-up.

**Single highest-impact change if only one ships:** P0-1 + P0-2 as one band in
`05-style.json` — ~20 declarations that make the running price the clearest, most brand-
trustworthy element on every funnel screen. Same mechanism, one fragment, one review.

---

## 5. Cannot be done inside the block system — for the report to Olive

1. **`aria-live` on `of-mbar__val` / `of-total__sum`** — price changes are announced to no
   one; overrides cannot set attrs inside the funnel and CSS cannot. Funnel JS should own it.
2. **Real stepper markup** (numbered dots with labels) — needs funnel DOM; our CSS labels
   are the ceiling.
3. **Bank/payment marks at the pay step** (Halyk/Visa/Mastercard logos) — Baymard's
   strongest trust cue needs imagery we cannot add (no external assets, no funnel markup).
4. **Price-change micro-feedback** (Dodo-style 200ms tick/slide when the total updates) —
   needs JS on funnel nodes.
5. **Promo field collapsed behind a link** — markup restructuring, protected.
6. **Delivery cost before screen 4** — Dodo resolves the zone *first* (surf.ru case); our
   funnel asks address at step 3/4. Structural.
7. **`pending_payment` recovery loop** (retry links via SMS/email) — backend.
8. Duplicate `<h1>`s in order modals — template-level (already flagged in AUDIT §5).

---

## 6. Acceptance gates for the implementer

1. `python3 tools/assemble.py && python3 tools/validate.py landing/config.json` → 0 errors
   (`of-*` deliberate-restyle warnings expected).
2. Draft save + `tools/qa.py <vid> --save`: confirm the refresh band renders inside
   `gs-fixes` at body position; round-1 rules 1–7 unchanged and first.
3. Browser at 390×844, all five screens: plan tap → wash + border; duration picker prices
   legible; mbar shows 21px price; checkout `of-total` bordered, sum 22px Loos Wide; pay
   button's live price intact (never text-overridden); back buttons work; no horizontal
   scroll; screens still animate (and don't under reduced motion).
4. Re-run the contrast script on any hex not in this document or DESIGN_SYSTEM §1 —
   **never estimate.**

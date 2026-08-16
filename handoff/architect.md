# Handoff — landing-architect

**Owner:** `.claude/agents/landing-architect.md` (Fable)
**Last updated:** 2026-08-16 · after planning Fix round 1 (see `plan/WORK_PACKAGES.md`)

Living state for the architecture role. Read at the start of a run; update at the end.

## Decisions in force (with the evidence that settled them)

1. **`order_funnel`, placed first; `order_menu` is out.**
   Evidence from rendered recon draft 1058: the platform counts conversions via a global
   `[data-cta]` click listener, and the `order_menu` page contained **zero** `data-cta`
   attributes — its measured CR of 0 was structural, not cosmetic. The funnel instruments every
   step (`plan-5..8`, `menu-next`, `check-zone`, `send-code`, `verify-code`, `pay`).
2. **Section order:** funnel → trust → steps → dishes → advantages → quality → FAQ → CTA →
   sticky order bar.
3. **Offer:** «Плати за 5 дней — ешь 10», badge «5 + 5 дней в подарок».
   5 days is the #1 seller (477 orders); 14 days is #2 (341).
4. **Hero targets weight loss** — 68% of buyers take 1200/1500 kcal.
5. **Theme stays at brand defaults.**
6. **REVERSED (2026-08-16): the P0 fixes no longer live in overrides.** All 7 cosmetic
   overrides migrate to static CSS in a new `05-style.json` `gs-` block; the overrides layer
   keeps exactly one rule (`#sfOrderBtn` `attrs.href` → `#orderFunnel`, bug A3). Evidence:
   overrides are a one-shot DCL pass, so they never reach the innerHTML-rebuilt
   `.of-gift-accent` (A2) and flash un-fixed before DCL (A5). Specificity proof per rule is in
   `plan/WORK_PACKAGES.md` "Fix round 1": funnel-scoped rules are ID-scoped
   (`#orderFunnel …`, (1,1,0) beats the funnel CSS's (0,1,0) order-independently); head-CSS
   targets win ties by body-after-head source order, with `.sf-header.scrolled` (0,2,0)
   covered explicitly. Rule of thumb now in force: **overrides only for DOM mutations
   (text/attrs) on static template nodes; all cosmetics go to static `gs-` CSS.**
7. **Fix round 1 planned** — 4 conflict-free packages (WP-F1 page fixes A2/A3/A4/A5;
   WP-F2 `qa.py`+`validate.py` B1–B4; WP-F3 `olive.py`+`assemble.py` B5/B6/B9;
   WP-F4 preview B7/B8). **WP-F2 gates re-QA**: qa.py's own B1/B2 mean its PASS output is
   untrusted until fixed. A1 copy is on hold for `plan/OFFER_STRATEGY.md`; the later copy
   edit touches only 10-funnel, 60-faq, 70-cta, 80-orderbar. A6 + A1 + `#sfOrderBtn`'s
   missing `data-cta` go on the report-to-Olive list.

## Hard-won platform facts

- `order_funnel`'s `offer` prop is an **object** `{badge, title, subtitle}`, not a string.
- The funnel ships **strong defaults** already matching a "pay 5 / eat 10" offer. Check
  `research/funnel-1058.html` before "improving" copy — an early attempt replaced the default
  badge with something *less* informative.
- A `style` override on `#orderFunnel` re-pointing `--of-green` rebrands the entire funnel;
  `style` is legal inside the protected scope, `html` is not.
- **Overrides run as a single client-side pass at `DOMContentLoaded`** (verified by reading the
  emitted `<script>`). They are not server-rendered CSS. Consequences: a flash before they
  apply, and no effect at all on elements injected later.
- Known-bad blocks: `home_quality` renders **nothing** on a landing; `home_result` claims
  «400 блюд» against 297 in the API. Both hard-fail in `tools/qa.py`.
- `cta` block **does** emit `data-cta="cta_block"` (verified in the 1069 render).
- The funnel root is one element: `class="of" id="orderFunnel"` (funnel-1058.html:184) — so
  `#orderFunnel{--of-*}` outranks the `.of` var block regardless of stylesheet order.
- `order-funnel.css` hardcodes: `.of-offer` green gradient (:256), `.of-dd__gift` /
  `.of-gift-accent` red `#e53935` (:1142/:1145) — all (0,1,0), beatable by ID-scoped rules.
- `.sf-notice` sizing and `--sf-notice-h` come from an inline `<style>` in the template
  **head** (`:root{--sf-notice-h:36px}`, media-query 32px) — not from JS — so a body-level
  `:root{--sf-notice-h:0px}` wins by source order.
- Overrides may never set `data-*` (validate.py, mirrors platform) — the desktop
  `#sfOrderBtn` therefore cannot be instrumented by us; platform issue.
- **Unconfirmed inference:** the live server emits an html-block `<style>` at its body
  position (verified only in the preview renderer). Re-QA step 4 of Fix round 1 must confirm
  it in the round-1 draft render before trusting the tie-break rules for `.sf-*`/`:root`.

## Live state

| version | status | note |
|---|---|---|
| **871** | **active** | homepage duplicate — the rollback baseline |
| **1133** | draft | **v3 — fix round 1: static-CSS migration + matrix-true 14+14 offer. QA 32/32.** |
| 1069 | draft | v2 funnel-first, quality fix — superseded (fails QA: no gs-fixes, old 7 overrides) |
| 1065 | draft | v2 before the quality fix |
| 1058 | draft | recon |

Nothing has been activated. **Activation is the user's decision.**

## Open questions

- Contest rules, deadline and judging criteria are still **unconfirmed** — the Instagram post
  returned only the profile. Unknown whether judging reads the platform's `conversions` stat or
  actual paid orders.
- A/B hero variants V2 (price anchor) and V3 (trial first) are specified in
  `plan/ARCHITECTURE.md` but not built. With 9 lifetime impressions, a split test needs traffic
  before it can say anything.
- `plan/OFFER_STRATEGY.md` (marketing audit) not yet landed — A1 offer copy frozen until then.
- **Fix round 1 is implemented and verified in draft 1133 (QA 32/32, 0 failures).** The
  flagged inference is now CONFIRMED: the server does emit our html-block `<style>` in
  `<body>` after `</head>`, so the source-order tie-breaks for rules 1–3 hold.
- Browser-only confirmations still pending on 1133: A2 post-interaction colour, A3 click
  target, A4 footer clearance, A5 first-paint flash.
- A1 is fixed on our side (copy is matrix-true) but the **platform matrix itself is still
  wrong** — report to Olive stands, along with A6 and `#sfOrderBtn`'s missing `data-cta`.

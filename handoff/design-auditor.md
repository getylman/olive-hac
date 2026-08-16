# Handoff — landing-design-auditor

**Owner:** `.claude/agents/landing-design-auditor.md` (Fable)
**Last updated:** 2026-08-16 · after the visual-refresh research run (Dodo/Drinkit study →
`design/VISUAL_REFRESH.md`)

Living state for the design role. Read it at the start of a run; update it at the end.

## Current state

Three documents, in build order: `design/AUDIT.md` (P0–P2 findings, implemented in v2/v1133),
`design/DESIGN_SYSTEM.md` (tokens, type scale, `gs-` specs, **new §7 funnel-restyle layer**),
`design/VISUAL_REFRESH.md` (**new** — Dodo/Drinkit-referenced restyle specs, prioritised,
with per-rule specificity proofs; nothing implemented yet). Current draft v1133.

## Verified facts — do not re-derive

- **Round-1 contrast table still stands** (white-on-lime 1.31 illegal; green-on-lime 8.22;
  ink-on-lime 13.62; white-on-green 10.79; white on funnel-default `#4CAF50` 2.78).
- **New computed (2026-08-16), full table in DESIGN_SYSTEM §1:** funnel `--of-muted:#888`
  = **3.54** on white — and it colors `of-dd__price`, i.e. *price text at 13px on the
  payment path*; hints `#aaa` = **2.32**; error `#e53935` = **4.23** at 12px. Verified
  repairs: muted `#6B6B6B` (5.33/4.68/4.67 on white/`#f0f0f0`/`#EAF3DF`), error `#B42318`
  (6.57). Offer-badge white-on-blend `#4c6e62` = 5.65 (legal; lime chip 8.22 preferred).
- **Funnel structure** (funnel-1058.html): root `class="of" id="orderFunnel"`; 5 screens
  `data-screen="menu|preview|prefs|delivery|checkout"` (prefs = optional detour; main path
  is 4 steps); `of-topbar`s hold only a back button — room for CSS `::after` step labels.
- **`.of` declares `font-family` exactly once** (order-funnel.css:25) → a single
  `#orderFunnel{font-family:…}` rebrands every funnel screen.
- **Already present in the funnel — never duplicate:** `prefers-reduced-motion` guard
  (order-funnel.css:1303); per-day price in the sticky `of-mbar` (`data-price-perday`);
  «Популярное» badge on the 1500 plan; plan cards printing «от 5 000 ₸/день» + macros.
- **Reference base** (details + URLs in VISUAL_REFRESH §0): dodopizza.kz is Servicepipe-
  blocked headless, but **dodopizza.ae/.pl run the identical Dodo IS front-end** — observed:
  total-in-CTA («Add to Cart for AED 46») in a sticky safe-area footer; price-as-secondary-
  pill «from AED 29»; segmented controls with a 200ms sliding indicator; selection = fill +
  icon, never lone border; orange `#FF6400` reserved for the primary CTA. **Drinkit ordering
  is app/kiosk-only** — borrow its documented composition-transparency concept, never its
  unobserved UI. Published evidence set (Baymard/NN/g/Gourville/GrowthRock) cited in §0.

## Open design risks

- **CSS pseudo-content rules** (step labels on `of-topbar`, ePay line on `of-total`) put
  copy in CSS: brittle vs funnel renames, announced by screen readers (content is accurate,
  so acceptable), invisible to the overrides validator. Shipped only as P1 with the caveat
  stated in VISUAL_REFRESH §3; get user sign-off before implementing E2/P rules.
- Overrides remain a single DCL pass — cosmetics stay in static CSS (`05-style.json`), which
  is also where the whole refresh band lands. One fragment, one owner at a time (WP rule).
- Loos Wide is a wide face: refresh deliberately keeps it off text <20px and off the long
  funnel hero title (wrap risk at 390px) — resist "brand it harder" pressure.
- `home_advantages` still pulls unaudited raster images from olive.kz.

## Next time

1. After implementation: browser-verify VISUAL_REFRESH §6 gates at 390×844 (all 5 screens,
   live price intact, no horizontal scroll, reduced-motion path).
2. Re-run the contrast script on any new hex; re-check if `meta.theme` changes.
3. Report-to-Olive list is consolidated in VISUAL_REFRESH §5 (aria-live prices, real
   stepper, payment marks, price-change feedback, promo collapse, delivery-cost timing,
   pending_payment recovery, modal H1s).

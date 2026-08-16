# Handoff — landing-design-auditor

**Owner:** `.claude/agents/landing-design-auditor.md` (Fable)
**Last updated:** 2026-08-16 · after the v2 build and the override-mechanism audit

Living state for the design role. Read it at the start of a run; update it at the end.
Keep it factual — record what was *verified*, and mark inference as inference.

## Current state

`design/AUDIT.md` (P0–P2 findings) and `design/DESIGN_SYSTEM.md` (tokens, type scale,
8 `gs-` component specs) are written and were implemented in landing version **1069** (draft).

## Verified facts — do not re-derive

- **Computed contrast** (real WCAG maths, not estimates):
  | pair | ratio | verdict |
  |---|---|---|
  | white on lime `#C4F139` | **1.31** | illegal everywhere, even non-text UI |
  | white on `#4CAF50` (funnel default green) | **2.78** | fails for 16px bold |
  | white on `#194536` | 10.79 | AAA |
  | green `#194536` on lime | 8.22 | AAA |
  | ink `#181717` on lime | 13.62 | AAA |
  | white on `#FF2600` | 3.80 | large text only |
- Lime is a **ground/decoration**, never a background for white text.
- Type scale (mobile, 390px): 12 / 14 / 16 / 18 / 21 / 25 / 30px, rem-based; hero clamps up on
  desktop. "Loos Wide" only at ≥20px and uppercase.
- Spacing 4px scale; radii 6 / 10 / 16 / 18 / pill.
- The server emits `html` block content **raw, no wrapper** — every block supplies its own
  `<section>` and padding.
- `meta.theme` compiles to `:root { --l-* }` **and** `body .of { --of-lime/--of-green/--of-green-d }`.
  Note the server maps `primaryDark` to *both* `--of-green` and `--of-green-d`, so the funnel's
  hover state collapses to the base colour unless an override re-points `--of-green-d`.

## Open design risks

- **Overrides are applied by client-side JS at `DOMContentLoaded`, once.** Every cosmetic P0 fix
  (hiding the maintenance banner, recolouring the header) therefore lands *after* first paint —
  a visible flash on slow mobile connections, which is exactly the audience. Design fixes that
  depend on overrides are structurally weaker than fixes baked into a `gs-` block.
- Anything the funnel injects *after* load never receives its override (same single-pass reason).
- `home_advantages` pulls raster images from olive.kz — outside our control, unaudited for weight.

## Next time

1. Re-check contrast if `meta.theme` changes — the funnel derives its palette from it.
2. Audit real mobile performance (the page carries Bootstrap + swiper + leaflet + 3 analytics tags).
3. Keep `design/DESIGN_SYSTEM.md` the single source for `gs-` components; implementers build
   against it verbatim.

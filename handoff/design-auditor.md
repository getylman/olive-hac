# Handoff — landing-design-auditor

**Owner:** `.claude/agents/landing-design-auditor.md` (Fable)
**Last updated:** 2026-08-16 · warm-round spec written (`design/WARM_ROUND.md`), no fragments touched

Living state for the design role. Read it at the start of a run; update it at the end.

## Current state

Docs, in build order: `design/AUDIT.md` (P0–P2, implemented v2), `design/DESIGN_SYSTEM.md`,
`design/VISUAL_REFRESH.md`, `design/SKIN_V7.md` (**palette/type authority**), and **new
`design/WARM_ROUND.md`** — full spec for the user-approved warm round (gs-day timeline,
gs-personas, gs-ask WhatsApp closer, spring washes, gold rules). Current draft **1418**
(`research/preview-v1418.html`); live baseline 871. Warm round is spec-only — architect
should slot it as `20-personas.json`, `50-day.json`, `65-ask.json` (all free slots, no
renumbering).

## Verified facts — do not re-derive

- **Round-1 contrast table stands** (white-on-lime 1.31 illegal; white on funnel-default
  `#4CAF50` 2.78). SKIN_V7 §1 has the v7 matrix (white/green 6.22, deep/spring 7.51,
  gold banned on light 2.15).
- **New computed 2026-08-16 (full table WARM_ROUND §1):** ink `#20271A` on spring = 12.24;
  muted `#4E5748` on spring = **6.01** (AA ≥13px); spring text on deep `#2C4E28` = 7.51;
  **gold on deep = 4.38 — the only legal gold ground** (on white/soft/spring it is
  2.15/2.00/1.71, banned even as a meaningful non-text mark); white on WhatsApp brand
  `#25D366` = **1.98** — the WA button must stay our green. Section-edge ratios:
  spring/soft 1.17 (weak — dissolve with gradients, never butt them), spring/green 4.96.
- **Funnel plan cards (1418 render :757–819):** goal labels verbatim = «Похудей активно»
  (1 200, 4 блюда, от 5 000 ₸/день, plan-5), «Похудей легко» (1 500, 4, от 5 500, plan-6,
  platform emits «Популярное» here), «Удержание формы» (1 800, 5, от 6 000, plan-7),
  «Набор массы» (2 500, 6, от 6 500, plan-8). **Never add our own popularity badge** —
  it would duplicate or contradict the platform's.
- **Warm data:** `research/WARM_DATA.md` — 6 verified days (plans 5/6), kcal/mass agree
  with `meals` 24/24, photos all 200. **Chosen for gs-day: plan 5 · 2026-08-20**
  (кесадилья 459 / грудинка 318 / салат 97 / поке 363 = 1 237 ккал — closest to the 1 200
  label; no smoothie-lunch weirdness). Image URLs in WARM_DATA are absolute — **convert to
  root-relative `/meals_uploads/…`** or validate.py hard-errors.
- **Contacts verified in 1418:** `wa.me/77008702626` + «+7 700 870-26-26»; delivery slots
  6:00–9:00 / 20:00–22:00 (`data-start/end`). FAQ block renders as
  `l-section--soft` = `--l-bg-soft` `#F4F8EE`.
- `data-cta` inventory in 1418 = 19 values; warm round adds `day-order`,
  `persona-1200/1500/1800/2500`, `faq-whatsapp` — checked, no collisions.
- 21st.dev context (kept short): React/Tailwind registry, patterns only, cold visual
  language — warmth comes from our palette + real photos. **Testimonials remain
  data-blocked, not design-blocked** (no MCP reviews source; never invent).

## Design decisions in force (warm round)

- Animation ban holds for all NEW blocks (hero marquee is the user's restored exception).
- Spring washes = two tuned section gradients (gs-who soft→white→soft; gs-day
  spring→soft fade) + the spring ask-card — not blanket recoloring. Gradients are tuned to
  their §5 neighbours; re-derive seams if order changes.
- gs-day meal cards are **not links** (no fake affordance); the day total «1 237» is a sum
  of verified figures, and **no date appears in visible copy** (menu rotates; evergreen
  framing «реальное меню одного дня»).
- No new hex values introduced; gold budget = one aria-hidden ✳ on the deep delivery card
  (+ grandfathered marquee ✳ at 2.89).
- gs-ask deliberately merges with the FAQ's soft section (one visual unit) and doubles as a
  payment-anxiety lever (human channel before the price block; 43% die at pending_payment).

## Open design risks

- Spring/soft seams at 1.17 merge if ever butted directly — placement map in WARM_ROUND §5
  is the guard.
- `/meals_uploads/` files could be pruned by Olive someday: gs-day images need
  width/height + a soft background so a 404 degrades clean (specced).
- CSS pseudo-content rules (09-pseudo) unchanged; warm blocks use zero `content:` so the
  droppable-band rule holds.
- `home_advantages` (unaudited rasters) is deleted from the page — risk closed.

## Next time

1. After implementation: 390×844 browser pass per WARM_ROUND §6 (seams, no horizontal
   scroll, wa.me deep link, lazy images below fold, new data-cta set in server render).
2. Re-run the contrast script on any new hex; re-check §1 if `meta.theme` changes.
3. VISUAL_REFRESH §6 funnel gates and the §5 report-to-Olive list still stand.

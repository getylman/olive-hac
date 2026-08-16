# Handoff — landing-architect

**Owner:** `.claude/agents/landing-architect.md` (Fable)
**Last updated:** 2026-08-16 · warm round planned (WP-W1..W4 in WORK_PACKAGES; base draft 1418)

Living state for the architecture role. Read at the start of a run; update at the end.

## Decisions in force (with the evidence that settled them)

0. **v7-skin round (2026-08-16, supersedes parts of 2 and 5 below).** User directive: adopt
   the donor visual from github.com/dorab1/olive-hac (`research/donor-v7.html`) while keeping
   our machinery. In force now:
   - **Section order:** hero (03) → [style bands 04–09] → funnel (10) → cals (15) → trust
     (20) → steps (30) → plans (35) → dishes (40) → marquee (45) → feats (50) → quality
     (55) → FAQ (60) → promo (70) → sticky bar (80). Funnel-first survives: the donor hero
     is compact (~1 viewport) and every CTA anchors `#orderFunnel`.
   - **Theme is no longer brand defaults:** `meta.theme` = donor palette (spring/deep
     mapping — SKIN_V7 §1); the funnel is pinned by 05-style rule 4 regardless of the
     `body .of` theme compilation (ID-scoped wins).
   - `70-cta.json` (block `cta`) replaced by `70-promo.json` (html): `l-cta` locks button
     text to primaryDark, which can't express the donor's white-on-green button.
   - Hero targets (decision 4) preserved via the hero SUB line, not the slogan.
   - Implemented inline (single hand for skin coherence), not via the WP pipeline: the
     donor file fixed all design decisions, so the architect/implementer split would have
     transferred a whole-page context to every agent for a value-only translation.

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
   *(Landed: implemented + verified in draft 1133, QA 32/32; offer copy is matrix-true.)*
8. **AMENDED (2026-08-16): the static-CSS layer is split into band fragments; the
   single-file rule of DESIGN_SYSTEM §7 becomes "one layer, one owner per band, never
   overrides".** Trigger: Fix round 2 has three streams (visual refresh, surcharge reframe,
   prefs-limit fix) all writing CSS, plus a hard requirement that pseudo-content be a
   *separately droppable* package — under the no-shared-files rule that forces at least one
   extra fragment, and per-stream bands are then strictly simpler. Fragments:
   `05` gs-fixes (**frozen**, rules 1–7), `06` gs-restyle, `07` gs-surcharge, `08` gs-prefs,
   `09` gs-pseudo (droppable). Cascade-safety proof (WORK_PACKAGES "Fix round 2"):
   (a) all band rules are `#orderFunnel`-scoped (1,x,0) → order vs the funnel's in-body CSS
   irrelevant; (b) selector+property disjointness audited across bands → no inter-band ties
   exist; (c) any future double-declaration resolves deterministically (later band wins);
   (d) band numbers must sit strictly inside (05, 10) — lower loses ties to round-1,
   `10+` re-creates the A5 flash. C1's "merge into rule 4" and SURCHARGE's "9 rules in 05"
   are superseded accordingly (intent preserved; 05 stays at exactly 7 rules).
9. **Fix round 2 planned** — 5 packages: WP-R1 restyle core (06 + 80-orderbar §2.1 +
   40-dishes §2.2); WP-R2 surcharge (07 + overrides R3/R5 + FAQ R4); WP-R3 prefs disabled
   state (08 — new spec, lives in WORK_PACKAGES); WP-R4 pseudo-content band (09 — P, E2,
   R2, prefs-limit hint; **user sign-off gate, droppable via `rm` + re-assemble**);
   WP-R5 assembly/draft/re-QA last. R1–R4 fully parallel. Disabled-state grey `#9E9E9E`
   (2.68 on white — computed, legal: WCAG 1.4.3 exempts inactive components; chosen to be
   distinct from ink 17.89 and informational muted 5.33). Overrides go 1 → 2 (3 with R5).

10. **LK rounds (2026-08-16, user-directed, implemented inline — recorded here for state
    accuracy; details in handoff/implementer.md).** The page evolved past decision 0's
    section list: 15/20/30/35/50/55 fragments deleted; now 03-hero (restored marquee hero —
    the user's own animation exception), 04-skin (tokens + primitives + chrome recolors),
    05–09 funnel bands (09-zconfigurator turns funnel screen 1 into a configurator; also
    the desktop `min-height:0` zoom-gap fix), 10-funnel, 40-dishes (photo carousel, real
    `/meals_uploads/` images), 45-marquee (static fact row), 60-faq, 70-plans (pricing
    closer), 80-orderbar. Page-wide animation ban (hero excepted); no em dashes in copy.
    Current draft **1418** (qa 42/0/2, the 2 are the permanent counter warns).
11. **Warm round planned (2026-08-16) — spec `design/WARM_ROUND.md` adopted intact; build
    plan WORK_PACKAGES "Warm round" (WP-W1..W4); decisions W1–W5 + flags in
    ARCHITECTURE "Warm round".** In force:
    - **Order:** three new fragments in free slots, zero renumbering, zero edits to
      existing fragments: 10 funnel → **20-personas** (`gs-who`, soft→white→soft gradient)
      → 40 dishes → 45 marquee → **50-day** (`gs-day`, spring→soft fade) → 60 faq →
      **65-ask** (`gs-ask`, spring card on soft, zero top padding) → 70 plans. Seam map
      verified against actual grounds (funnel soft via 05-style `--of-bg`; FAQ is the only
      `l-section--soft`; marquee green; plans white).
    - **65-ask is fully self-contained** — consumes only 04-skin tokens/primitives; the
      FAQ merge is pure ground identity (`theme.bgSoft` = `--gs7-soft` = #F4F8EE). 60-faq
      and 04-skin stay untouched.
    - **Copy:** WARM_ROUND final drafts verbatim; day = plan 5 · 2026-08-20 (1 237 kcal
      sum of verified figures; no date in visible copy); persona labels/prices are the
      funnel's own strings («от» is load-bearing — floor is the halved 14/30-day rate);
      em-dash rule enforced byte-level per new file (comments included) so acceptance is
      a plain grep; dish names byte-verbatim incl. non-«ё» spellings.
    - **Spec deviation (recorded):** the gs-day timeline spine is a sized no-repeat
      background gradient on the `<ol>`, not the spec's `::before` — a rendered pseudo
      needs `content:`, banned outside band 09. Same pixels, zero pseudo.
    - New `data-cta`: `day-order`, `persona-1200/1500/1800/2500`, `faq-whatsapp` —
      19 → 25 values, no collisions (1418 inventory grep-verified).
    - Gold budget: exactly one aria-hidden ✳ on the deep delivery card (4.38) + the
      grandfathered marquee ✳. No new hex values page-wide.

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
- **CONFIRMED (was inference):** the server emits an html-block `<style>` at its body
  position after `</head>` — the source-order tie-breaks for `.sf-*`/`:root` rules hold.
- `validate.py` EXTERNAL_REF matches `src/srcset/poster/data/href` **only on media/embed
  tags** (`img|iframe|source|video|audio|embed|object|track|input`) plus script/link —
  so `<a href="https://wa.me/…">` is legal while `<img src="https://olive.kz/…">`
  hard-errors. Olive's own images must be written root-relative `/meals_uploads/…`.
- `qa.py` verifies an `html` section by the **first** `class="gs-…"` match in its content
  — keep the `<style class="gs-<name>-css">` tag first so the marker is stable.
- A rendered `::before/::after` requires a `content:` declaration; `content:` is banned
  outside band 09 (droppability rule) — decorative rules therefore go in as sized
  no-repeat `background-image` gradients. NB: 45-marquee's `content:"\2733"` is a
  grandfathered LK-round exception; scope any "no content:" check to new fragments.
- Implementers can verify without touching generated files:
  `tools/assemble.py --out <scratch>/x.json` + `validate.py <scratch>/x.json` +
  `preview/render.py <scratch>/x.json <scratch>/x.html`. Only the final WP writes
  `landing/config.json`.
- `.of` is a max-width column (480px mobile / 1120px ≥ desktop, order-funnel.css:1188) on
  `--of-bg` (soft #F4F8EE via 05-style) — the funnel "ground" is that column, not a
  full-bleed band; flanks are body white on desktop.
- The FAQ block renders as the page's only `l-section l-section--soft`
  (`--l-bg-soft` = `theme.bgSoft`); `.l-section` pads 70px (50px ≤768px, landing.css:45/:358).

## Live state

| version | status | note |
|---|---|---|
| **871** | **active** | homepage duplicate — the rollback baseline |
| **1418** | draft | **current — LK round 2 + desktop-zoom fix; qa 42/0/2 (2 = permanent counter warns). Base for the warm round.** |
| 1274 | draft | v7-skin QA reference (`research/preview-v1274.html` per git log) |
| 1133 | draft | fix round 1: static-CSS migration + matrix-true offer (QA 32/32) — superseded |
| 1058–1069 | draft | recon / v2 iterations — superseded |

Nothing has been activated. **Activation is the user's decision.**

## Open questions

- Contest rules, deadline and judging criteria are still **unconfirmed** — the Instagram post
  returned only the profile. Unknown whether judging reads the platform's `conversions` stat or
  actual paid orders.
- A/B hero variants (weighted versions) remain unbuilt — traffic is still too thin for a
  split test to say anything.
- **Warm round is planned, not implemented.** WP-W1..W3 (20-personas / 50-day / 65-ask) are
  parallel; WP-W4 assembles, saves the draft and QAs. After it lands: the 390×844 browser
  pass per WARM_ROUND §6.8 (seams, wa.me deep link, lazy images, 25 data-cta values in the
  server render) is mandatory before any activation talk.
- **Menu-rotation risk on gs-day (P2):** the four dishes are real for plan 5 · 2026-08-20,
  but the visible day menu rotates and `/meals_uploads/` files may be pruned someday. Copy
  is evergreen by design; images degrade to clean soft tiles. If Olive prunes them, swap in
  a fresher verified day from WARM_DATA's six candidates.
- Round-2/LK browser-only confirmations that remain open ride along with the warm-round
  browser pass (disabled prefs, surcharge note, `:has()` hint — state-dependent).
- The **platform pricing matrix discrepancy** (funnel default copy promises 5+5 the matrix
  doesn't honour) is fixed in our copy but still stands as a report-to-Olive item, along
  with A6 and `#sfOrderBtn`'s missing `data-cta`.

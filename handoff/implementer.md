# Handoff — landing-implementer

**Owner:** `.claude/agents/landing-implementer.md` (Opus)
**Last updated:** 2026-08-16 · after the v2 build

Living state for the implementation role. Read at the start of a run; update at the end.
Record gotchas that cost you time — that is what this file is for.

## Files and who owns what

`landing/config.json` is **generated**; never hand-edit it. Edit fragments:

| file | contents |
|---|---|
| `landing/sections/10-funnel.json` | `order_funnel` + hero copy + offer object |
| `landing/sections/20-trust.json` | `gs-` design tokens (defined **once page-wide**) + trust strip |
| `landing/sections/30-steps.json` | «Как это работает», 3 steps |
| `landing/sections/40-dishes.json` | 6 real dishes, snap-scroll row |
| `landing/sections/50-advantages.json` | `home_advantages` (no props) |
| `landing/sections/55-quality.json` | `gs-qual` — replaced dead `home_quality` |
| `landing/sections/60-faq.json` | 6 objection-handling Q&A |
| `landing/sections/70-cta.json` | final `cta` |
| `landing/sections/80-orderbar.json` | sticky bottom bar |
| `landing/meta/meta.json` | title + 6 theme tokens |
| `landing/meta/overrides.json` | 7 override rules |

Then: `python3 tools/assemble.py` → `tools/validate.py` → `tools/qa.py <version_id>`.

## Gotchas that already cost time

- **The `gs-` token `<style>` block lives in `20-trust.json` and must exist exactly once.**
  Other blocks consume `var(--gs-*)` with literal fallbacks, so they still render standalone.
- The server emits `html` content **raw with no wrapper** — supply your own `<section>` + padding.
- **Every CTA needs `data-cta`** or the platform counts nothing. This is the single highest-value
  rule in the repo.
- Overrides apply **once, client-side, at `DOMContentLoaded`**. Anything injected later is never
  restyled — prefer baking styling into your own `gs-` block over relying on an override.
- Never text-override `#orderBtn`: it wraps the live price `<span>`, and replacing its text
  destroys the price.
- Inside `#order`, `#order-menu`, `#orderFunnel`, `.of`, `.sf-form` only `text`/`style`/`addClass`
  apply; `html` is silently dropped. Overrides may never set `id`, `name`, `data-*`, `on*`.
- `validate.py` proves the config is *legal*; only `qa.py` proves the server *built* something.
  `home_quality` passed validation and rendered nothing.
- The edge WAF 403s default HTTP agents — pass a browser UA to `curl`.
- `OLIVE_MCP_URL` must be exported; the token is a credential and is not in the repo.

## Truthfulness rules that have already caught mistakes

- "orders" ≠ "fulfilled orders": 1130 placed, but 482 never paid. The trust strip says
  «1 130 заказов» and deliberately never says «выполненных».
- Real figures: 717 customers, 1130 orders, 297 dishes. Never «400 блюд».
- Dishes must come from `meals` verbatim (name, mass, kcal, protein/fat/carbs). MCP exposes no
  dish images, so cards are designed imageless — do not add stock photography.

## Fix round 1 gotchas (2026-08-16)

- **Specificity when your `gs-` block restyles funnel/template classes:** `of-*` rules are all
  single-class (0,1,0) in `order-funnel.css`, and the funnel injects that CSS in-body — possibly
  *after* your style block — so never rely on source order for `of-*` fixes. Scope them under the
  ID: `#orderFunnel .of-…` (the funnel root is `class="of" id="orderFunnel"`, one element).
  For head-CSS targets (`.sf-header`, `.sf-notice`, `:root` vars) a body `<style>` wins ties by
  order, but cover higher-specificity states explicitly (`.sf-header.scrolled` is (0,2,0)).
- `validate.py` warns (deliberately, not errors) when block CSS touches `sf-*`/`of-*` — expected
  for the reviewed restyles in `05-style.json`. Keep it a warning.
- A style-only html block gets no qa.py render marker unless something carries a `gs-` class —
  put it on the tag itself: `<style class="gs-fixes">`.
- The `background` **shorthand** is what kills `.of-offer`'s hardcoded gradient; `background-color`
  alone would lose to the gradient image.
- Until WP-F2 lands, `qa.py` PASS lines are untrustworthy (B1: counts `data-cta` as a substring
  anywhere; B2: never checks overrides). Verify with the repro fixtures, not with qa.py.

## A1 offer-copy round (WP-A1, 2026-08-16)

- Live matrix re-verified straight from `research/funnel-1058.html` (`window.OLIVE_PRICING`), not
  just from BUGS.md: period **2 (5 дней) is `gift:0`, `perDay` = full rate on all four plans**
  (10 000 / 11 000 / 12 000 / 13 000). Periods 3–4 carry gift 14/30 at **exactly half** the
  per-day rate. So: «от 5 000 ₸ в день» is a true floor; «вдвое дешевле» is exact and
  plan-independent; the trial floor is **10 000 ₸/день**. Never write «5 000 ₸ в день»
  unqualified.
- `research/BRIEF.md` §4 is **stale and wrong**: it still asserts «every multi-day period doubles
  — 5+5, 14+14, 30+30» from `pricing_periods` (also stale: `research/pricing.txt` has
  `days:5, gift_days:5`). `order-funnel.js` charges from the matrix only. Treat the matrix as
  ground truth and BRIEF §4 gift claims as superseded by `plan/OFFER_STRATEGY.md`.
- `data-cta` on the `cta` block is emitted **server-side from the block type**
  (`data-cta="cta_block"`), not from a prop — editing `heading`/`subheading`/`cta_text` cannot
  drop it. Same for the funnel's `plan-*` / `pay` values.
- `offer` in `10-funnel.json` must stay an **object** `{badge,title,subtitle}`; a bare string
  passes validate.py but is not what the block reads.
- **Still-open A1 leftover, not mine to edit:** `30-steps.json` step 1 says «каждый тариф от
  5 дней удваивается: 5+5, 14+14, 30+30» — false against the matrix. Needs its owner to fix.

### WP-F1 (2026-08-16) — overrides → static CSS

- `landing/sections/05-style.json` is **new** and owns all 7 migrated cosmetics; `landing/meta/overrides.json`
  now holds exactly **one** rule (`#sfOrderBtn` → `href="#orderFunnel"`). Do not re-add cosmetics there.
- The `05-` prefix matters: the block must assemble **before** `10-funnel.json` so the fix CSS precedes the
  funnel. It carries no `var(--gs-*)` (tokens live in `20-trust.json`, which loads later) — literal hex only.
- `validate.py`'s sf/of warning regex is `\.(sf|of)-[\w-]+\s*\{`, so `.sf-header.scrolled{…}` and
  `#orderFunnel .of-…` chains do **not** all trip it. One warning for the whole block is normal, not a sign
  that rules went missing — count `{` blocks instead (should be 7).
- `.sf-header.scrolled` (client.css:178) sets `background:#fff` but leaves `color:#fff` from :165 — scrolled
  header is white-on-white today. Rule 3 fixes both states; never drop the `.scrolled` half.
- Orderbar now ships `gs-orderbar--hidden` in markup. Consequence: **any JS failure leaves the bar invisible**,
  so the observer guard reveals it when `#orderFunnel` or `IntersectionObserver` is missing. Keep that branch.
- `80-orderbar.json` offer text is now «+14 дней в подарок» (OFFER_STRATEGY §1). The old «5 + 5» is false —
  the live matrix ships `gift: 0` for the 5-day period. The remaining A1 copy edits (10-funnel, 70-cta,
  60-faq) are still open and are owned by whoever picks up the follow-up.

### WP-F4 · preview hygiene (B7 B8) — 2026-08-16

- `preview/serve.py` is now **allowlisted**, not root-serving: only `preview/out/**` and
  `research/{client,landing}.css` return 200; everything else (`.git/`, `.claude/`, `landing/`,
  `tools/`, `research/*.md`) is a clean 404, directory indexes included. If you add an asset the
  preview links, add it to `ALLOWED_FILES`/`OUT_DIR` or it will 404 and the page will look broken.
- Args go through `argparse`: bad/out-of-range port and a missing config exit 2 with a usage
  message instead of a traceback. `preview/serve.py --help` documents what is served.
- **Latent trap that cost time:** the old `log_message` filter did `"__version" not in args[0]`,
  but `log_error()` passes an int code as `args[0]` → `TypeError` inside `send_error`, so every
  404 died as an *empty reply* (curl `000`), not a 404. Fixed with `str(args[0])`. Any handler
  you add that calls `send_error` depends on this.
- `render.py` inlines the override payload with `<` escaped to `<` (B8). Before the fix an
  override value containing `</script>` closed the tag early: the payload became invalid JS, so
  **no override applied at all**, and the rest of the value became live DOM. Same guard on
  `meta.theme` values (`<` → CSS `\3c `), which could break out of the `<style>` block the same way.
- Both v2 paths verified in the local render: the single `attrs` rule round-trips through the
  payload and the `r.attrs` branch, and the static `<style class="gs-fixes">` block from
  `05-style.json` is emitted raw in body order exactly as the server does.
- The preview now prints per-rule match counts (console + a bottom badge). `#sfOrderBtn` matches
  **0 nodes locally** — it is platform template chrome, not ours, so that override can only be
  confirmed on the server render. Same for `#orderFunnel .of-*` rules: the funnel is a
  PLACEHOLDER box locally, so funnel CSS is never exercised. Don't read those as regressions.

## WP-F3 — `olive.py` / `assemble.py` (B5 B6 B9, 2026-08-16)

- **`olive.py` is on `argparse` now; the command surface is unchanged on purpose.**
  `.claude/settings.json` allowlists literal prefixes (`call overview *`, `show *`, …) and
  `qa.py:81` shells out as `olive.py call <tool> {}` — renaming or reordering anything there
  breaks the allowlist silently (you get a permission prompt, not an error). Verified all 8
  allowlisted prefixes + qa.py's argv form still parse.
- `save`/`activate` gained **`--dry-run`**: prints the exact tool + args and returns without a
  network call. Use it to check parsing — never test `save`/`activate` by running them.
  (`--dry-run` is additive; no existing invocation changes.)
- argparse consequence: `--label --status draft` is now a clean usage error (exit 2) instead of
  silently setting label=`"--status"`. To pass a label that really starts with `-`, use
  `--label="--status"` — the space form can't work, by design.
- **`$OLIVE_MCP_URL` is masked in every error message** (`…/landings/<token>`). If you add an
  error path, run it through `safe_url()` — the URL *is* the credential.
- HTTP errors now surface the JSON-RPC body: a bad token prints
  `MCP error: HTTP 401 Unauthorized … "Ссылка недействительна."` instead of a urllib traceback.
- The SSE branch is **defensive only** — the live endpoint answers plain JSON. It now iterates
  events, because the old "first `data:` line" grab would return a progress notification and
  then `KeyError` on `result`.
- **`assemble.py` fails hard where it used to warn:** an `overrides` key in `meta.json` and any
  mis-numbered `sections/*.json` (`5-x.json`, `100-x.json`) are now errors — non-zero exit, no
  output file. Both previously produced a *wrong config* while exiting 0. `overrides` come from
  `overrides.json` only.
- Test assembler changes in a **fixture tree in the scratchpad** (copy `tools/` + `landing/`;
  `ROOT` follows the script's own path), not by editing `landing/meta/` or `landing/sections/`.
  Those belong to other implementers and you will race them.
- Live `overview` now reads **719 customers / 1137 orders** (was 717/1130). `20-trust.json` still
  says 717/1130 — re-verify before the next draft; the numbers grow.

### WP-F2 (2026-08-16) — verification tools (B1–B4)

- **`qa.py` PASS lines are trustworthy again.** The `data-cta` check now counts real attributes
  (`data-cta="…"`, both quote styles) **outside `<script>`/`<style>`** and FAILs at zero. All 14
  live CTA attributes sit in delivered markup, so stripping code blocks costs nothing — but if you
  ever build CTAs from a JS template string they will not count here, and the platform will not
  count them either. A warn tells you when attributes hide only inside script/style.
- **New `--- overrides delivered? ---` section.** It parses the applier payload out of the render
  (`var rules = [...]`) and compares parsed objects, not raw text — so Cyrillic `text` values are
  encoding-independent. It also verifies a `#`-fragment `attrs.href` actually resolves to an
  `id=` in the page: that is the A3 dead-link class of bug, caught automatically from now on.
- **This check found A2 by itself:** against both `preview-v2.html` and the 1069 render,
  `overrides[6] (.of-gift-accent): selector matches the render` FAILs — zero nodes at load. If you
  ever write an override whose selector only exists after user interaction, qa.py will now say so.
- **New `qa.py --config <path>`** so you can QA a render against an arbitrary config instead of
  whatever `landing/config.json` currently holds. Use it to check a saved render from an older
  draft without touching the repo config (which other implementers own).
- **`validate.py` now checks every markup-bearing prop, not just `html.content`** — `text.body`,
  `faq`/`testimonials` items, anything nested. Error messages carry a dotted path
  (`sections[1] <faq> props.items[0].a`). If you put markup in any prop, it is checked now.
- `EXTERNAL_REF` covers `<img|iframe|source|video|audio|embed|object|track>` `src/srcset/poster/
  data/href` and protocol-relative `//host` everywhere; `INLINE_HANDLER` is `[\s/]on[a-z]+\s*=`
  so `<div/onclick=…>` is caught. Both are strict supersets of the old patterns (proved by test).
  Relative assets (`/img/x.png`, `url(/a.png)`) stay legal.
- **The sf-*/of-* restyle rule is still a `warn`, and its regex is untouched** — WP-F1's note that
  `05-style.json` produces exactly one warning still holds. Do not promote it to an error.
- Expect `qa.py 1069` to FAIL 5 checks: draft 1069 predates WP-F1, so it has no `gs-fixes` block
  and still embeds the old 7 overrides. That is the tool correctly reporting a stale draft, not a
  regression — it clears once a fix-round draft is saved.

## Live counters drift (2026-08-16, orchestrator)

`20-trust.json` hardcodes real API figures. They **grow over time**, so a stale value understates
rather than lies — but refresh before any activation:
`./tools/olive.py call overview '{}'` → `customers`, `orders.total`, `meals`.
Refreshed this round 717→**719** clients, 1 130→**1 137** orders (dishes still 297). `qa.py`
cross-checks these against the live API, so a stale strip shows up as a QA failure, not silently.

Still say «заказов», never «выполненных»: 489 of 1 137 are `pending_payment` and never shipped.

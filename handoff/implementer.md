# Handoff — landing-implementer

**Owner:** `.claude/agents/landing-implementer.md` (Opus)
**Last updated:** 2026-08-16 · warm round (WP-W1 personas, WP-W2 day timeline)

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
| `landing/sections/50-advantages.json` | `gs-adv` html block (v5: replaced `home_advantages`, which prints «400+ блюд») |
| `landing/sections/55-quality.json` | `gs-qual` — replaced dead `home_quality` |
| `landing/sections/60-faq.json` | 6 objection-handling Q&A |
| `landing/sections/70-cta.json` | final `cta` |
| `landing/sections/80-orderbar.json` | sticky bottom bar |
| `landing/meta/meta.json` | title + 6 theme tokens |
| `landing/meta/overrides.json` | 3 override rules (v5: #sfOrderBtn attrs · prefs text · 14-day addClass) |
| `landing/sections/08-tapfix.json` | band `gs-tapfix` (v5): scroll-margin-top + calendar 44px tap targets |

Then: `python3 tools/assemble.py` → `tools/validate.py` → `tools/qa.py <version_id>`.

## v7-skin round (2026-08-16) — donor visual port

Full spec: `design/SKIN_V7.md`. Donor page: `research/donor-v7.html` (from
github.com/dorab1/olive-hac). User directive: donor's look, our machinery.

**Shipped as draft 1274** (preview https://olive.kz/l/gosura?v=1274, render saved to
`research/preview-v1274.html`). Server QA: **47 passed / 0 failed / 2 warnings** — the two
warnings are the deliberate evergreen understatements in 20-trust (live overview on save
day: **734 customers / 1147 orders**; the strip says 700+ / 1 100+, still true). Verified
in the server render: funnel pinned to #3F6B39, theme compiled --l-lime:#DCEBC4,
root-relative hero image emitted, all 23 data-cta values (ours + the funnel's own,
no collisions).

- **The gs- token block MOVED: it now lives in `04-skin.json`, not `20-trust.json`.**
  04 also owns shared primitives (`.gs-sec/.gs-wrap/.gs-h2/.gs-lead/.gs-btn/.gs-imgbox/
  .gs-tag`) that sections 15–70 consume — dropping 04 unstyles half the page.
- New fragments: `03-hero` (headline is a `<p>` — the page's one `<h1>` is the funnel's,
  qa.py enforces exactly one), `15-cals`, `35-plans`, `45-marquee`, `70-promo`
  (replaces the deleted `70-cta.json` — the `l-cta` block can't do a green button with
  white text: its text color is locked to `--l-primaryDark`).
- **`validate.py` hard-errors on `url("https:…")` even for olive.kz's own assets.**
  Its own definition says external = absolute/protocol-relative, so same-origin images go
  ROOT-RELATIVE: `url("/assets/images/…")`. They 404 in the local preview (gradient
  fallback shows) and resolve on olive.kz. Never `<img>`+`onerror` — inline handlers are
  rejected; photos ride as `background-image` over a spring gradient so failure is silent.
- Funnel bands 05–09: structure frozen, **values recolored** to the donor palette
  (`--of-green:#3F6B39`, `--of-green-d:#2C4E28`, `--of-lime:#DCEBC4`, `--of-bg:#F4F8EE`);
  05 gained rule 8 (`of-prefs__preview` hardcoded `#194536` → `#2C4E28`). The round-2
  contrast repairs (#6B6B6B/#B42318) were RE-COMPUTED on the new grounds and still pass
  (table in SKIN_V7 §1) — re-verify again if any ground hex changes.
- Local `qa.py --file preview/out/index.html` shows 10 structural FAILs (no h1, funnel
  marker, all override checks): the local render builds the funnel as a placeholder and
  embeds overrides as `window.__GSP_OVERRIDES`, not the server's `var rules=[…]` form.
  Expected — only `qa.py <version_id>` against the server render is authoritative.
- Soft-on-soft adjacent sections visually merge (funnel bg is now soft): cals deliberately
  sits on white. Keep the alternation rule from SKIN_V7 §5 when inserting sections.
- Donor claims NOT ported (don't reintroduce): «160 г белка», «меню не повторяется 30
  дней», «Доставим бесплатно», «Популярный» on the 14-day plan (5-day leads by volume),
  «лабораторный контроль каждой партии» («регулярный» is what's verifiable), RU/KZ
  toggle, tel:-order, reveal-on-scroll JS (hides content when JS fails).

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
Refreshed 717→**719** clients, 1 130→**1 137** orders (dishes still 297); the API moved again
to 720/1138 within the same session — these drift constantly, so treat a small gap as normal.
`qa.py` cross-checks against the live API and **warns** (not fails) when the page understates.
Workflow: leave small drift alone, but **refresh immediately before activating** — the QA
warning is the reminder. Understating is never a falsehood; overstating would be.

The number check itself was a false pass until 2026-08-16: it substring-matched the raw HTML,
so live `720` "matched" inside the SVG coordinate `72.0195` while the page really said 719.
It now compares whole numeric tokens against **visible text only** (script/style/svg stripped).
Same lesson as B1 — if a check can match something other than the thing it claims to test, it
will eventually do exactly that.

Still say «заказов», never «выполненных»: 489 of 1 137 are `pending_payment` and never shipped.

## Fix round 2 — band-fragment discipline (2026-08-16, landing-architect)

- Static CSS is now a **layered set of band fragments**, one owner each: `05` gs-fixes
  (FROZEN — round-1 rules 1–7, byte-identical), `06` gs-restyle, `07` gs-surcharge,
  `08` gs-prefs, `09` gs-pseudo. **All style bands must sort strictly between `05-` and
  `10-`**: a lower number silently loses same-specificity ties to round-1 (no error, wrong
  color); `10+` puts CSS after the funnel markup and re-creates the A5 first-paint flash.
- Every funnel rule in a band must be `#orderFunnel`-prefixed. Never add a bare `.of-*`
  selector to a band: at (0,x,0) it tie-breaks against the funnel's in-body CSS by document
  position, which depends on fragment number — exactly the silent breakage the ID-scoping
  rule exists to prevent.
- `content:` declarations live **only** in `09-pseudo.json` (the droppable sign-off band).
  Adding pseudo-content copy to any other band breaks the drop path (`rm 09` + re-assemble).
- Prefs markup fact: `<label class="of-prefs__opt"><input type="checkbox" data-of-pref
  value="N"><span>…</span></label>` (funnel-1058.html:500–540) — `input:disabled+span`
  reaches the label text; `:has()` rules are progressive enhancement only, never the sole
  carrier of a state.
- The round-2 acceptance counts: overrides go 1 → 2 (3 with R5); `05-style.json` stays at
  exactly 7 rules. SURCHARGE_STRATEGY's "9 rules in 05" note is superseded by the split.

### WP-R3 (2026-08-16) — `08-prefs.json`, prefs disabled state

- **`research/order-funnel.js` does not exist in this repo** — the funnel JS is loaded from
  `https://olive.kz/js/order-funnel.js?v=1786535059` (funnel-1058.html:1126). Specs cite it by
  line number, so if you need to verify a funnel mechanic, `curl` it with a browser UA (the WAF
  403s default agents) rather than assuming the file is missing/stale. Verified this round:
  `:917 var MAX_PREFS = 3` and `:920-925 enforcePrefLimit()` →
  `if (!i.checked) i.disabled = checked >= MAX_PREFS;`. The spec's mechanic is accurate.
- **WP-R3's specificity arithmetic in WORK_PACKAGES is slightly wrong, conclusion unaffected.**
  It calls the new rules (1,2,1)/(1,2,2) and the incumbent `.of-prefs__opt input` (0,2,1). Actual:
  new rules are (1,3,1)/(1,3,2)/(1,3,1) (`.of-prefs__opt` + `[data-of-pref]` + `:disabled`), the
  incumbent is (0,1,1). The ID wins regardless — don't "fix" the rules to match the note.
- `:has()` in this band deliberately carries **only `cursor`**, never the colour/opacity. That is
  the invariant to preserve: a `:has()` failure must degrade to *no* state change, never to a live
  control that looks disabled. If you extend this band, keep colour/opacity out of `:has()`.
- This band produces **no** sf/of validate warning: the warn regex is `\.(sf|of)-[\w-]+\s*\{` and
  every selector here continues past the class (`… input[…]`, `…:has(…)`), so it never matches.
  Only `05`/`07` trip it. Don't read the absent warning as the band having gone missing.
- **The effect is state-dependent and invisible to static QA**: the `disabled` attribute exists
  only after a user checks 3 preferences, so `curl`/`qa.py`/the local preview can never render it.
  Browser-only verification. The local preview is doubly blind here — the funnel is a PLACEHOLDER
  box (see WP-F4 note), so no `of-*` rule is exercised locally at all.

### WP-R2 (2026-08-16) — surcharge reframe: R1 band, R3 override, R4 FAQ

- **New owner row:** `landing/sections/07-surcharge.json` (`<style class="gs-surcharge">`, exactly
  one rule: `#orderFunnel .of-subnote{color:#194536;background:#EAF3DF}`). `overrides.json` is now
  **2 rules** — `#sfOrderBtn` first (untouched), then the prefs-subtitle `text`. `60-faq.json` is
  **7 items** (surcharge item inserted 4th, right after «Как проходит оплата?»).
- **The live funnel JS is fetchable and worth fetching** — every §0 claim in SURCHARGE_STRATEGY was
  re-verified against it in ~2 minutes, rather than trusted:
  `curl -A "Mozilla/5.0 … Chrome/124.0" https://olive.kz/js/order-funnel.js?v=1786535059` (200,
  71 649 B; the `?v=` comes from `research/preview-v1133.html`). Confirmed: `of-head__sub` has
  **zero** occurrences in the whole file → the R3 `text` override can never be clobbered;
  `renderReplaceCost` (:742) writes only `textContent` + `classList`; basis `full = periodDays +
  periodGift` (:759); `MAX_PREFS = 3` (:917); `is_replaced` → `of-meal--swapped` + icon (:404).
- **Line numbers in SURCHARGE_STRATEGY §0 are against `funnel-1058.html`, not the 1133 baseline.**
  The prefs subtitle is :457 there but **:482** in `research/preview-v1133.html`; the checkout
  replace row is :924. Same nodes, so the spec is right — just don't `sed -n '457p'` the new file
  and conclude the node moved.
- Contrast recomputed from the hexes, not copied: `#194536`/`#EAF3DF` = **9.45**, incumbent
  `#e53935`/`#fdecea` = **3.70**. `#EAF3DF` is not a new colour (AUDIT.md:161, VISUAL_REFRESH S1/S2).
- **R5 (checkout row label) deliberately skipped**, not blocked: its selector
  `#orderFunnel [data-co-replace-row] span:first-child` does match static markup
  (`preview-v1133.html:924`, JS touches only `[data-co-replace]` and the row's `d-none`), so it is a
  safe pickup if anyone wants a 3rd override. Overrides stay at 2.
- `validate.py` warns `overrides[1] … selector not found in research/gosura.html` — **expected and
  permanent** for any funnel-scoped override: `gosura.html` is the funnel-less 871 page. Verify
  those against `preview-v1133.html` instead. Total: 0 errors, 4 warnings, exit 0.
- **Open, not mine to edit:** `60-faq.json`'s last item «Можно ли заменить блюдо?» answers «Да,
  замена блюд доступна…» with no hint that a replacement can cost money. It is not false, and the
  new item now explains the charge three items earlier — but that answer read alone implies free.
  Its owner should fold in «разница в цене блюд может добавиться к заказу».

### WP-R4 · `09-pseudo.json` — the droppable pseudo-content band (2026-08-16)

- **Every `content:` declaration of the round is in this one file (7 of them).** Verified with a
  strict `(?<![-\w])content\s*:` scan across all fragments — 09 is the only hit.
  **Gotcha for the WP-R5 gate:** a naive `grep 'content:'` reports **6 false positives** from
  `justify-content:` in `20-/30-/40-/80-` gs- blocks. Use the negative-lookbehind form or you will
  "fail" the no-content-outside-gs-pseudo check on blocks that ship no generated copy at all.
- **Drop test executed and passed** (`rm 09-pseudo.json` → assemble 12 sections exit 0 → validate
  exit 0, 4 warnings, `gs-pseudo` absent; restored byte-identical, md5 `858e8c37…`). Nothing else
  depends on this band: WP-R3 ships the disabled *state*, 09 only adds the *explanation*.
- **`validate.py` does not warn on this band**, unlike 05/07/08. Its regex is
  `\.(sf|of)-[\w-]+\s*\{` and every selector here ends `::after{`, so it never matches. A band with
  zero warnings is not evidence the rules are absent — count `{` blocks (8 here).
- Markup facts re-verified in `research/preview-v1133.html` (not just funnel-1058): funnel root is
  `<div class="of" id="orderFunnel">` (:209); **5** `of-screen`s — menu(:214, `is-active`, **no
  topbar**), preview(:302), prefs(:475), delivery(:670), checkout(:841); all four topbars contain
  only `.of-back` and `of-topbar__title` occurs **0 times** in the render, so `::after` is the sole
  label and clobbers nothing. Step numbering is truthful: the spine is menu→preview→delivery→
  checkout (`data-next="delivery"` at :452), prefs is a detour entered at :360 → it gets a name,
  not a number.
- `.of-subnote` (:450) lives on the **preview** screen, not the menu screen — the strategy doc's
  "menu screen" means the menu *preview*. `.d-none` is `display:none!important`
  (order-funnel.css:802), so the explainer is hidden with the note; it can never appear alone.
- Pseudo-element boxes land correctly because the parents are flex: `.of-topbar` flex row (css:136),
  `.of-total` flex column whose last child is the pay button (css:1148, render :928),
  `.of-prefs` flex column (css:482). None of these had an existing `::before/::after` — checked.
- **ePay claim is evidenced, not assumed:** the render loads
  `https://epay.homebank.kz/payform/payment-api.js` (:1460) and states the same in the FAQ (:1199)
  and trust strip (:988).
- **Known cosmetic imprecision, shipped verbatim on purpose:** P's `margin-right:36px` balances
  `.of-back` (36px, css:153) but ignores `.of-topbar`'s `gap:8px`, so the label sits ~4px off
  optical centre; at ≥900px `.of-back` becomes 40px (css:1194) while the margin stays 36px. Text
  only, no layout risk — do not "fix" it without re-verifying the spec.

### WP-R1 (2026-08-16) — restyle core, band `06-restyle.json`

- `06-restyle.json` ships VISUAL_REFRESH §3 T1–T3, C1–C5, S1–S4, O1, E1, D: **20 rule blocks,
  23 selectors, all `#orderFunnel`-scoped, zero `content:`, zero `display/visibility/position`.**
  Marker class `gs-restyle`. Assembles at section index 1, right after `gs-fixes`. 05 stayed
  byte-identical (7 rules). Zero selector+property collisions with bands 05/07/08/09 — re-run the
  disjointness check if you add a rule.
- **C1 is safe to ship as a var swap:** all 13 `var(--of-muted)` consumers in `order-funnel.css`
  are `color:` — none is a background or border, so `#6B6B6B` cannot change a surface.
- **`of-*` sizes have a desktop twin at `@media (min-width:900px)` (order-funnel.css:1187–1302),
  and media queries add no specificity.** T3's unconditional (1,1,0) rules therefore win there
  too: `.of-hero__title` 44px→20px and `.of-plan__price` 22px→15px on ≥900px. VISUAL_REFRESH
  computed at 390px only and did not account for this block. Shipped verbatim as specced —
  if it reads wrong in the browser, the one-line fix is wrapping those two declarations in
  `@media (max-width:899px)`. `of-total__sum` (22px) and `of-plan__perday` (12px) already match
  their desktop values, so only those two rules are affected.
- **`<br>` after a `display:block` element yields a blank line.** VISUAL_REFRESH §2.1 specs both
  `display:block` on `.gs-orderbar__price` *and* a `<br>` after it. Kept the markup verbatim
  (WORK_PACKAGES quotes it) and dropped `display:block`; `<br>` alone gives the line break, so
  the rendered result is what §2.1 intended. Same trap for any future two-line `gs-` label.
- **`--gs-fs-h2` is `clamp(1.5625rem,1.1rem + 2vw,2.5rem)`, not a flat 25px.** VISUAL_REFRESH §2.2
  and DS §5.5 both gloss it as "25px" — true at 390px (25.4px), but it reaches **40px** at
  ≥1120px, so `.gs-dish__kcal` is a 40px numeral on desktop cards that are 280px wide. Used the
  token as specced; check the desktop card in the browser pass. Any spec that quotes a `--gs-fs-*`
  value in px is quoting the *fallback*, not the token.
- Re-verified this round: cheapest plan's 14/30-day `perDay` is **5 000** (`window.OLIVE_PRICING`
  plan 5, periods 3–4), so «от 5 000 ₸/день» in the orderbar is true; all six dish cards in
  `40-dishes.json` still match the live `meals` payload verbatim (name/mass/kcal/Б-Ж-У).

## Round 3 — «v5 checkout fixes», draft **1202** (2026-08-16, orchestrator + 3 Opus implementers)

Shipped against JOURNEY_AUDIT §8. Draft id **1202** (`?v=1202`), qa.py: **42 PASS / 0 FAIL /
2 warns** (both by design, see below). validate: 0 errors, 7 warnings, exit 0. NOT activated.

What landed (marker-verified on the server render `research/preview-v1202.html`):

- **Default duration 30 → 14**: `overrides.json` rule 3
  `{"[data-duration][data-days=\"14\"]" addClass "is-selected"}`. Mechanics: static markup
  still ships `is-selected` on the 30-day option (:526) — that is EXPECTED. The override adds
  the class to option 14 (:521, earlier in DOM) at DOMContentLoaded; `ensurePeriod` (js:309)
  takes the FIRST `.is-selected` in DOM order → 14; `applyPeriod` strips the rest. The funnel
  JS is parser-blocking (:1614) and the applier runs at DCL (:1714), while `ensurePeriod`
  fires only on a user tap — timing is safe. **Browser-verify on a device before activation**
  (curl cannot show a client-side class).
- **Price step + honest delivery copy**: 30-steps step 2 now carries «Полный тариф 14 дней —
  от 140 000 ₸ (на рационе 1 200 ккал): это 28 дней еды, по 5 000 ₸ в день» + delivery
  «от 600 до 2 100 ₸ за каждый день доставки … покажем до оплаты». FAQ delivery answer
  matches. Numbers re-verified this round: OLIVE_PRICING plan 5 period 3 = 140000/14/5000;
  MCP delivery_zones = free + 600/1100/1600/2100.
- **FAQ SMS → WhatsApp** («кодом в WhatsApp»; funnel hint :833 says WhatsApp; zero «SMS» on
  the page now).
- **T1 palliative**: 09-pseudo new rule `#orderFunnel [data-step="2"] .of-step__body::after`
  «Код не пришёл? Напишите нам в WhatsApp: +7 700 870-26-26» (number = footer wa.me + trust).
- **08-tapfix band** (new): `#orderFunnel{scroll-margin-top:64px}` (scrollIntoView vs fixed
  header) + `#orderFunnel .of-cal__day{width:44px;max-width:100%;height:44px}` (was 34px).
- **gs-adv** replaced `home_advantages` (50-advantages.json): 297 блюд / 4 рациона /
  delivery slots 6:00–9:00 & 20:00–22:00 / персонализация до 3 предпочтений — all verbatim
  from verified data. The false «400+ блюд» is gone from the page.
- **Trust counters rounded down**: 700+ / 1 100+ (live at save time: 725 / 1142 — rounding is
  from real, freeze-safe).
- **qa.py FORBIDDEN** += «400+ блюд». **BUGS.md** new section C (C1 no resend/change-phone —
  regression vs 871's own form; C2 no `.catch` on send/verify/check-zone rejections only —
  5xx/bad JSON ARE survivable, `post()` js:128-144 resolves them; C3 money decisions carry no
  `data-cta`).

### Gotchas new this round

- **`assemble.py` warns `duplicate prefix 08` (08-prefs + 08-tapfix)** — expected, order is by
  full name and is the intended one. There is no free 2-digit slot between 08 and 09.
- **validate warning count is now 7**, all benign: overrides[1] funnel selector (permanent),
  sf/of-restyle warns on 05, 06, 07, 08-tapfix, 09, and the orderbar `<script>` advisory.
  Earlier notes claiming 06 and 09 «don't trip the regex» are WRONG/stale: 06 always matched
  (15 bare `.of-*{` rule heads after the `#orderFunnel ` prefix), and 09 now matches via a
  *comment* whose prose wraps as `.of-step__body\n   {display:none}` — `\s*` spans the
  newline. Comment text can trip the warn regex; don't chase ghosts.
- **qa.py permanently warns customers/orders «stale»** after the 700+/1 100+ rounding (it
  greps whole tokens, `700` ≠ live `725`). By design — understating is freeze-safe. Do NOT
  «fix» it by restoring exact figures. The `+` also keeps the stale-adjacency regex silent.
- **The `content:`-outside-09 gate now has comment false-positives**: prose «No content: …» in
  06 and 08-tapfix comments. Count actual declarations (strict scan minus comments): 9, all
  in 09-pseudo.
- 08-tapfix's unconditional 44px **also overrides the desktop calendar twin**
  (order-funnel.css:1273, 38px @≥900px) — deliberate; 44px is fine there. Same media-query
  specificity class as WP-R1 T3.
- `40-dishes.json` `.gs-dish__kcal` declares `font-variant-numeric` BEFORE the `font:`
  shorthand → the shorthand resets it (dead tabular-nums). Not fixed this round (not our
  file); one-line fix for its owner: move the shorthand first.
- BUGS.md preamble still says «Two independent audits» and sections read A → C → B — cosmetic,
  left for the register's owner.
- Suggestion not acted on (out of scope): add `home_advantages` to qa.py `KNOWN_BAD` so nobody
  re-adds the «400+ блюд» block; FORBIDDEN only catches it after a render.

## LK round — 2026-08-16 (draft 1337)

User brief: hero from `hero.txt` (21st.dev *AnimatedMarqueeHero*), the funnel made to read
like Level Kitchen's `program-configurator` (levelkitchen.com/spb «Выбор программы»), five
sections deleted, gsDishes + gsPlans given the LK treatment, LK's `summary-container` added,
plus more contrast / bigger type / fade-in. Four scope questions were put to the user first;
all four came back on the recommended option (real Olive photos in the marquee; CSS-only
funnel restyle; delete but fold the trust proof into the funnel/summary; LK treatment for
dishes and plans).

### Verified facts new this round

- **`window.OLIVE_PRICING` is on the page** and is what `order-funnel.js` charges from.
  Re-verified against the LIVE page (not the saved render) on 2026-08-16: plan 5 = 10 000 /
  50 000 / 140 000 (+14) / 300 000 (+30). Every plan halves its per-day price on periods 3
  and 4, so **«день еды −50%» is plan-independent** — that is why it can be a static CSS
  badge in 09-pseudo.
- **`[data-total-sum]` exists only on the checkout screen.** On menu/preview the live price
  node is `[data-price-perday]`. The summary bar's first cut gated on `[data-total-sum]` and
  therefore never synced for a user who had chosen a ration but not reached checkout — the
  exact state it exists for. It now falls back to per-day.
- **`meals` exposes no images, but the funnel's menu endpoint does** (`m.images`,
  order-funnel.js `mealImages()`). Unused this round; a future dish grid could pull real
  photography from there instead of emoji tiles.
- **Usable Olive photography** (all curl-verified 200): `quality/1-3.webp` (real production),
  `promo-food.webp` (tray), `banner-menu-food.webp` (1204x351 dish spread — three
  background-position slices give three distinct tiles), `form.webp` (1981x816, lime + trays).
  `features/1-4.webp` are 160x160 **icons, not photos** (50-advantages had been using three of
  them as photos); `banner-olive`, `promo-olive`, `result` are mascot art.
- **The site header is `position:fixed`, 49.75px at 390px.** Any section placed first must
  carry its own top padding — the previous hero's tagline sat behind the chrome.

### Changes

- **03-hero.json** rebuilt: tagline pill, word-staggered headline (framer-motion variants →
  keyframes), description, two CTAs sharing one row, and a photo marquee (8 tiles duplicated,
  `translateX(-50%) → 0`). Headline stays a `<p>`; the single `<h1>` is still the funnel's.
- **04-skin.json**: `--gs7-muted` #697260 → **#4E5748** (5.03 → 7.55 on white), body/lead/h2
  sizes up one step, and the new **`.gs-reveal`** scroll-in utility + its script.
- **09-zconfigurator.json** (new band, sorts last of ours): the funnel restyled into the LK
  configurator. Screen 1 → «Объём» 2-col chip grid; screen 2 → duration popover promoted to a
  static chip grid, LK card geometry, and `.of-mbar` turned into the floating dark summary.
- **09-pseudo.json** += «Продолжительность» heading, the −50% badges, and the folded trust
  strip under the calorie grid.
- **35-plans / 40-dishes** rebuilt in LK form (duration chips with economy badges; dark
  nutrition panel + 2-col dish cards). **80-orderbar** → `.gs-summary`, LK's floating summary.
- **Deleted**: 15-cals, 20-trust, 30-steps, 50-advantages, 55-quality.

### Gotchas new this round

- **Fragment names must match `^\d\d-[\w.-]+\.json$`** — `09z-configurator.json` is rejected
  by assemble.py (two digits then a hyphen). Use `09-z…` to sort after `09-pseudo`.
- **The `.d-none` override needs both `!important` and higher specificity.** Bootstrap ships
  `.d-none{display:none!important}`; `#orderFunnel [data-pdd] > .of-dd__menu` (1,1,1) with
  `!important` wins. Scope it to `[data-pdd]` — the checkout dropdown `[data-cdays]` must keep
  its popover behaviour.
- **The duration trigger is inert once the menu is always open** and is now `display:none`.
  Its `[data-pdd-label]` node still receives `applyPeriod()`'s text and the summary bar reads
  it — do not remove the node from consideration just because it is not painted.
- **Do not build reveal-on-scroll on IntersectionObserver here.** The page's CTAs are anchor
  jumps; a jump straight past a section can move it from below the viewport to above it with
  no intersecting frame, and the section stays at `opacity:0` forever. The band uses a
  rAF-throttled "top above the reveal line" test, which is also true for anything already
  scrolled past. First pass runs synchronously (a background tab gets no rAF ticks).
- **Verifying in a hidden browser pane is misleading**: rAF is suspended, so reveal and the
  summary-bar sync both read as broken until a screenshot forces a frame. Screenshot, then
  re-query.
- **qa.py's customers/orders warnings are now permanent and expected** — those figures left
  the page with 20-trust. Nothing to refresh; ignore the "Refresh 20-trust.json" hint.
- `body` now carries `padding-bottom` for the floating bar **and** the footer wash, otherwise a
  white band shows under `.sf-footer`.

## LK round 2 — 2026-08-16 (draft 1363)

User brief: drop `gs-promo` and put gsPlans in its slot with «Начни уже сегодня»; turn
gsDishes into a carousel with real dish photos; retitle the funnel («4 шага до здорового
рациона»); plus five global notes — no em dashes and no compound sentences, don't make the
reader wait for images, replace «доставка каждый день» with «Нужный КБЖУ каждый день с
доставкой по Алматы», remove animation and even up the shapes, and deep green instead of
lime in the bottom block.

### Verified facts new this round

- **Dish photography exists, just not in the `meals` tool.** `GET /api/meal-plans/<planId>/day/<iso>`
  (order-funnel.js:513) returns each meal with an `images` array of
  `https://olive.kz/meals_uploads/*.png|jpg`, 340x250 studio shots on white. Sweeping plans 5
  and 6 over 2026-08-19..26 yielded **47 distinct dishes with photos**, and all 47 join the
  `meals` API by name with **kcal and mass agreeing dish for dish**. Eight were taken for the
  carousel; every one sits in all four rations. All eight URLs curl-verified 200.
- **The footer's lime was a real contrast bug**, not just a preference: client.css:1990 paints
  `.sf-footer__title` #C4F139 on the footer's own #F4F8EE wash, about 1.5:1. The section
  headings were effectively unreadable. #2C4E28 takes them to 8.9. The logo and contact icons
  carry the same lime as `fill` presentation attributes and are swapped by attribute selector.
- **The funnel animates its menu screen from opacity 0** (order-funnel.css:118-133, staggered
  delays on `.of-body > *` and `.of-plan`). Cancelling `animation` alone would leave the cards
  invisible — the rule must restore `opacity:1` and `transform:none` too.

### Changes

- **70-plans.json** (was 35-plans) took the deleted 70-promo's slot: heading «Начни уже
  сегодня», CTA to `#orderFunnel`. Number groups and unit phrases carry `&nbsp;` so «2 500»
  and «за день еды» never break across lines.
- **40-dishes.json**: scroll-snap carousel, eight real photos, arrows on ≥768px that disable
  at each end. Nothing is `loading="lazy"` — in a horizontal scroller a lazy card is one swipe
  from being looked at.
- **03-hero.json**: photo strip is static, unrotated, one uniform 4:3 size, swipeable, and the
  tiles are real `<img>` with width/height and `fetchpriority` so the preload scanner starts
  them with the HTML (a CSS `background-image` cannot be discovered that early).
- **04-skin.json**: `.gs-reveal` + its script deleted with the rest of the animation; so were
  `.gs-imgbox` / `.gs-tag`, now that every picture on the page is a real photograph. Footer
  recolors added.
- **45-marquee.json**: the scrolling ribbon became a static wrapping row; «Доставка каждый
  день» dropped, the promise now lives in the hero tagline.
- Copy pass over 10-funnel, 60-faq, 09-pseudo, overrides and every gs- section: no em dashes
  in prose, two or three short sentences instead of clause chains.

### Gotchas new this round

- **`meals` and the day endpoint agree on kcal/mass but only `meals` has Б/Ж/У**, and only the
  day endpoint has images. Any dish card needs both; join them by name and check the numbers
  match before trusting the pair.
- **Reserve `loading="lazy"` for vertical content.** A lazy image inside a horizontal
  scroller is not "below the fold" in any way the browser can reason about usefully.
- **Verifying interactivity in a hidden browser pane keeps lying.** rAF is suspended, so
  `scrollBy({behavior:'smooth'})` does nothing and `scroll` events never fire, which reads as
  a dead carousel. Dispatch the event directly (`el.dispatchEvent(new Event('scroll'))`) to
  test the handler, or force a frame with a screenshot first.
- **`window.scrollTo` on the live page is unreliable while the funnel is mounted** — the funnel
  calls `root.scrollIntoView()` on every screen change and pulls the viewport back. To inspect
  a section below it, hide the sections above instead of trying to scroll past them.

## Desktop-zoom gap fix — 2026-08-16 (draft 1418, qa 42/0/2 — the 2 are the permanent counter warns)

- **`order-funnel.css:28` gives `.of` `min-height:70vh`.** Invisible at 390×844 (screen 1 is
  taller than 70vh there), but the LK 4-column grid makes desktop screen 1 short, and browser
  zoom-out grows the CSS viewport — so 70vh inflates into a blank band between the funnel and
  gsDishes that widens with every zoom step (user-reported with a screenshot). Fix in
  `09-zconfigurator.json`: `@media (min-width:900px){#orderFunnel{min-height:0}}` — desktop-only
  so mobile keeps the platform's screen-switch reserve; the ID out-specifies `.of` regardless of
  source order. If a future round rebuilds the funnel band, carry this rule or the gap returns.
- The only other viewport-height rules in the platform CSS are modal `max-height`s and the
  `.sf-filters` fixed overlay (`display:none` by default) — neither contributes to page flow, so
  this one rule is the whole fix.

## Warm-round planning notes — 2026-08-16 (architect; spec design/WARM_ROUND.md, WPs "Warm round")

- **`<a href="https://wa.me/…">` passes validate.py; `<img src="https://…">` does not.**
  EXTERNAL_REF matches src/srcset/poster/data/href only on media/embed tags
  (`img|iframe|source|video|audio|embed|object|track|input`) plus `<script src>`/`<link href>`
  — plain anchors are exempt (regex read, tools/validate.py:70-77). Olive's own dish images
  must therefore be root-relative `/meals_uploads/…`; they 404 in the local preview and
  resolve on olive.kz.
- **A rendered `::before/::after` needs a `content:` declaration** — and `content:` is
  banned outside `09-pseudo.json` (droppable-band rule). Decorative lines go in as sized
  no-repeat background gradients instead, e.g. the gs-day spine:
  `background:linear-gradient(rgba(44,78,40,.28),rgba(44,78,40,.28)) 7px 0/2px 100% no-repeat`
  on the `<ol>`. (45-marquee's `content:"\2733"` predates the warm round and is
  grandfathered — don't copy that pattern.)
- **qa.py identifies an `html` section by the FIRST `class="gs-…"` in its content** — keep
  the `<style class="gs-<name>-css">` tag first in the fragment so the marker is stable.
- **Verify without writing generated files:** `python3 tools/assemble.py --out <scratch>/x.json`
  then validate + `preview/render.py <scratch>/x.json <scratch>/x.html`. Only the final
  assembly WP writes `landing/config.json`.
- **Warm-round copy acceptance is byte-level:** zero `—` bytes per new fragment (comments
  included — keep even CSS/HTML comments dash-free), dish names byte-verbatim from
  WARM_DATA (no «ё» fixes: «Зеленый», «запеченным»), «от» kept in every persona price
  floor. WARM_DATA.md itself uses `—` as a field separator — never paste its lines wholesale.
- **gs-day images: `loading="lazy"` is correct** (vertical, below the fold) — the opposite
  of the carousel rule. Keep `width="340" height="250"` + `background:#F4F8EE` on the img
  so a future 404 degrades to a clean tile.

### WP-W1 (2026-08-16) — `20-personas.json`, gs-who persona cards

- **New owner row:** `landing/sections/20-personas.json` (`<style class="gs-who-css">` first, then
  `<section class="gs-sec gs-who" id="gsWho">`). Four cards, `data-cta="persona-1200|1500|1800|2500"`,
  every card a whole-card `<a href="#orderFunnel">`. `gsWho` collides with nothing: the only `gs*` ids
  in the 1418 render are `gsDishes` and `gsPlans`.
- Goal labels and price floors were re-verified byte-for-byte against `research/preview-v1418.html`
  :757-819 (`of-plan__cta` / `of-plan__price`): «Похудей активно / Похудей легко / Удержание формы /
  Набор массы» and «от 5 000 / 5 500 / 6 000 / 6 500 ₸». Dish counts in the notes match the funnel's
  own `of-plan__meta` lines (4 / 4 / 5 / 6 блюд) and are spelled out, so the notes carry zero digits.
- **`grep -c` acceptance criteria in a WP are line counts, not occurrence counts.** WP-W1 asks for
  `grep -c 'data-cta' <fragment>` → 4, which is **unsatisfiable by construction**: a JSON string
  cannot contain a raw newline, so every fragment's whole `content` is one physical line and the
  answer is always 1. Use `grep -o … | wc -l` (or a python check) for occurrence counts. The
  `→ 0` criteria (`transition|animation|@keyframes|content:`, `—`, `https://`) are unaffected —
  0 lines and 0 occurrences agree.
- **`justify-content:` is banned in the warm-round bands, not just the linting of it.** The
  no-`content:` acceptance grep here is a plain substring, so a single `justify-content` would fail
  the file. Use `align-items`/`margin-top:auto` instead (the WP CSS already does).
- Comments count too: keep the CSS comment free of `—`, `https://`, and the words
  `transition`/`animation`/`@keyframes` (I wrote "no motion of any kind" instead).
- **The price string differs between the two specs.** WARM_ROUND §3.3 writes
  `от 5&nbsp;000&nbsp;₸ в&nbsp;день` (plain space after «от»); WORK_PACKAGES WP-W1 markup and the
  shared «Digit groups» rule both write `от&nbsp;5&nbsp;000&nbsp;₸ в&nbsp;день`. Shipped the
  WORK_PACKAGES form (identical rendering, and it also stops «от» ending a line). If a future round
  diffs against WARM_ROUND, this is not a typo.
- `.gs-who{background:linear-gradient(…)}` and `.gs-sec{background:#fff}` are both (0,1,0); the
  gradient wins only because fragment 20 assembles after `04-skin`. Any future skin rule that raises
  `.gs-sec` specificity kills the soft→white→soft wash silently.
- Self-check without touching generated files worked exactly as the shared rule describes:
  `tools/assemble.py --out <scratch>/warm.json` → validate **0 errors / 10 warnings** (all
  pre-existing: 2 duplicate-prefix, 7 sf/of + script advisories, 1 permanent override warn) →
  `preview/render.py`. `landing/config.json` md5 unchanged. `qa.py --file … --config …` on the local
  render: `PASS sections[10] html .gs-who-css rendered` and all four persona values in the
  14-value `data-cta` inventory; its 10 FAILs are the documented local-render artifacts (funnel
  placeholder, `window.__GSP_OVERRIDES` instead of `var rules`).

### WP-W3 (2026-08-16) — `65-ask.json`, the WhatsApp closer

- **Two of the WP's own acceptance greps contradict its own "exact" CSS.** Both resolved in
  favour of the mechanical gate, intent preserved:
  1. `grep -cE 'transition|animation|@keyframes|content:' → 0` vs the specced
     `.gs-ask__icon{…display:inline-flex;justify-content:center}`. Shipped
     `display:grid;place-items:center` instead — same 24px glyph centred in the 44px white
     circle, zero `content:` substrings. **Any warm-round fragment that centres with
     `justify-content` will "fail" the WP-W4 preflight grep**; use `place-items`, or expect
     the false positive (same class of trap as the round-2 note above).
  2. `grep -c '25D366' → 0` while the reason *not* to use WhatsApp brand green belongs in
     the block comment. The comment names it in words only, never as a hex.
- **The local preview understates the FAQ merge; the server render does not.**
  `preview/render.py:135` emits the `faq` block as `<section class="l-section">` (no
  `--soft`), but the server emits `l-section l-section--soft`
  (`research/preview-v1418.html:1648`, ground `#F4F8EE` from `meta.theme.bgSoft`). So the
  local scratch render shows a white→soft seam directly above `.gs-ask` that **does not
  exist on olive.kz**. Never "fix" a soft-on-soft seam from a local screenshot — WP-W3
  acceptance item 5 is checkable on the server render only.
- Data re-verified against the 1418 server render rather than trusted from the spec:
  `https://wa.me/77008702626` (:1963) and visible `+7 700 870-26-26` (:1968, ASCII hyphens,
  hexdumped). `data-cta="faq-whatsapp"` collides with nothing — the 1418 inventory is
  exactly 19 values.
- `font-variant-numeric:tabular-nums` is declared **after** the `font:` shorthand here, on
  purpose. `40-dishes.json` still has it before the shorthand, where the shorthand resets it.
- Scratch check (no generated file touched): assemble `--out` scratchpad → 17 sections
  (20-personas had landed, 50-day had not), validate **0 errors / 10 warnings, exit 0**;
  65-ask contributes no warning of its own, and `landing/config.json` md5 was identical
  before and after.

### WP-W2 (2026-08-16) — `50-day.json`, the day timeline

- **A subagent shell has no `$OLIVE_MCP_URL`** (it is not in `~/.bashrc`/`~/.profile` either),
  so `olive.py call meals` is unavailable inside a delegated run. Plan dish verification around
  the **public, unauthenticated** endpoints instead — both answer with a browser UA:
  - `GET /api/meal-plans/<plan>/day/<iso>` → per-slot `id/type/name/mass/kcal/images` **and a
    day-level `total_kcal`**. That field made the gs-day total a *reported* number, not our
    arithmetic: it returns exactly `1237` for plan 5 · 2026-08-20, matching 459+318+97+363.
  - `GET /api/day-meals/<slotId>/replacements` (funnel js:790) → for every replacement
    candidate a full `{mass,kcal,proteins,fats,carbohydrates,images}`. **This is the only
    token-free source of Б/Ж/У I found**, and it re-confirmed WARM_DATA for «Кесадилья с
    яичным паштетом» (Б36 Ж18 У39) and «Куриная грудинка с запеченным картофелем»
    (Б37 Ж11 У18). Sweeping plans 5–8 × 2026-08-17..26 (190 slots) never surfaced «Поке с
    курицей» or «Зеленый салат с брокколи и цитрусами» — a *scheduled* dish is not offered in
    its own replacement pool, so those two Б/Ж/У pairs still trace only to WARM_DATA's `meals`
    dump. Fine for this round; re-pull `meals` before activation if you want 4/4 fresh.
  - The four `/meals_uploads/` PNGs are live (200) and their intrinsic size really is
    **340×250**, so the specced `width="340" height="250"` attrs are the true aspect ratio.
- **Keep provenance dates out of `<style>` comments.** WP-W2 acceptance reads literally: «the
  string `2026-08-20` appears ONLY inside the HTML comment». My first cut documented the live
  re-verification in the CSS comment and would have failed that grep with zero copy problems.
  All date-bearing prose now lives in the `<!-- … -->` block inside `<section>`; the CSS
  comment carries mechanics + the contrast table only.
- Spine geometry (decision W4, background gradient instead of `::before`) checks out
  arithmetically: `<ol>` padding-left 26px, background-position `7px` is against the padding
  box, so the 2px rule spans x=7..9 and the 14px dot at `left:-25px` inside a full-width `li`
  spans x=1..15 — both centred on x=8. No pseudo-element, no `content:`.
- `justify-content` never appears in this fragment (WP-W3's trap): the two centred rows use
  `align-items` only, so the WP-W4 `content:` preflight grep is clean at 0.
- **No usable headless browser in the sandbox**: `firefox --headless --screenshot` hangs to
  timeout even with a fresh `-profile`, and there is no chromium/chrome. A delegated
  implementer cannot do the 390×844 visual pass; markup/CSS review + the scratch render are
  the ceiling, and the browser check belongs to the assembly WP.
- Scratch check (no generated file touched): assemble `--out` scratchpad → 18 sections,
  validate **0 errors / 10 warnings, exit 0**; 50-day contributes no warning of its own
  (no `sf-`/`of-` selectors, no `<script>`), and `landing/config.json` was never written.

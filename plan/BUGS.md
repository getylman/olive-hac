# Bug register — audit of 2026-08-16

Two independent audits: the rendered page (draft **1069**) and the repo tooling.
Severity is by revenue/user impact. "Verified" = reproduced against the live render or a
crafted fixture; "inferred" = reasoned but not observable without a browser.

---

## A. Rendered page

### A1 · P0 · Pricing matrix contradicts the offer — 5-day gift days do not exist
**Verified, and platform-wide (not ours).** `window.OLIVE_PRICING` in the render:

| plan 5 (1200 ккал) | total | gift | perDay |
|---|---|---|---|
| period 1 (1 день) | 10 000 | 0 | 10 000 |
| **period 2 (5 дней)** | **50 000** | **0** | **10 000** |
| period 3 (14 дней) | 140 000 | 14 | 5 000 |
| period 4 (30 дней) | 300 000 | 30 | 5 000 |

The identical matrix ships on `olive.kz` itself (redirects to `/l/new`), so this is Olive's
production data, not a defect in our config.

Three of Olive's own sources disagree: `pricing_periods` says `gift_days: 5`; the
`order_funnel` block's built-in copy says «5 + 5 дней в подарок»; the matrix says `gift: 0`
at double the per-day rate. `order-funnel.js` reads **only the matrix** (`pairGift`;
`refreshDurationPrices` hides the gift chip when `g<=0`), so the buyer sees no gift and
10 000 ₸/день — at the step that already leaks 43%.

**Not fixable by us.** Report to Olive. Offer copy pending a marketing decision.

### A2 · P1 · `.of-gift-accent` override is dead after the first interaction
**Verified.** `.of-dd__gift` exists in the initial HTML (8 nodes) and JS only mutates its
`textContent`/`classList`, so its inline override survives. `.of-gift-accent` has **zero**
nodes at load — it is rebuilt inside an `innerHTML` string on every `applyPeriod()`, so after
any plan/duration tap it renders in off-brand red `#e53935` at the money moment.
**Fix:** overrides are a one-shot JS pass and cannot style future nodes. Move the rule to
static CSS in a `gs-` block; drop override rules 6–7.

### A3 · P1 · Desktop floating «Заказать» button is a dead link
**Verified.** `<a href="#order" class="sf-order__btn" id="sfOrderBtn">` — the page has no
`id="order"` (the funnel is `#orderFunnel`). Shown at ≥992px after 40px scroll. Also carries
no `data-cta`, so its clicks are uncounted.
**Fix:** override `{"selector":"#sfOrderBtn","attrs":{"href":"#orderFunnel"}}` — `href` is a
legal attr and the element sits outside the protected scope.

### A4 · P2 · Sticky order bar permanently covers ~86px of the mobile footer
**Verified.** `position:fixed;bottom:0`, shown whenever `#orderFunnel` is off-screen —
including at document end — and nothing pads the body, so footer contacts/requisites are
occluded. `body{scroll-padding-bottom:90px}` is a no-op because the scroller is `html`.
**Fix:** in `80-orderbar.json`, `@media(max-width:767px){body{padding-bottom:96px}}`; move
scroll-padding to `:root`.

### A5 · P2 · First-paint flash (inferred — needs a real browser)
The bar ships without its `--hidden` class and the IntersectionObserver's first callback lands
after first paint, so it flashes over the hero then slides away. The observer also reads
`es[0]` instead of `es[es.length-1]`. Separately, all 7 overrides are cosmetic and applied only
at `DOMContentLoaded`, so the maintenance banner and the white-on-lime header flash un-fixed on
slow mobile — the audience we actually have.
**Fix:** ship `gs-orderbar--hidden` in markup and let the observer reveal; use the last entry;
move override-able cosmetics into static CSS where possible.

### A6 · P2 · Duplicate heavy assets (platform-side)
Swiper CSS loaded twice, Swiper JS twice (the second without `?v=`, so no cache reuse), and
`leaflet.min.js` loads although the page has no map. Template + funnel block both inject deps.
**Report to Olive**; not fixable from our config.

**Checked and clean:** `data-cta` values unique and every CTA instrumented;
`body[data-landing-version="1069"]` present so attribution works; the `--gs-*` token block
appears exactly once; no duplicate ids; heading order h1→h2→h3 clean; no 390px overflow found
by static analysis.

---

## B. Repo tooling

### B1 · P1 · `qa.py` `data-cta` check is a false pass
**Reproduced.** `n_cta = html.count("data-cta")` counts the substring anywhere, so a page whose
only occurrence is `[data-cta]{color:red}` in CSS — and which has **zero** real attributes —
prints `PASS … 1 found`. This green-lights precisely the CR-0 failure the whole project exists
to prevent.
**Fix:** count `re.findall(r'data-cta="[^"]+"', html)`; fail when empty.

### B2 · P1 · `qa.py` never verifies overrides were delivered
**Reproduced** (`grep -i override tools/qa.py` → nothing). The entire override layer ships
unchecked.
**Fix:** assert each override's selector appears in the render; spot-check `text`/`addClass`.

### B3 · P1 · `validate.py` misses illegal content it claims to block
**Reproduced, all passing with 0 warnings:** external `<img src="https://…">` and `<iframe>`
(the `EXTERNAL_REF` regex only covers `<script src`, `<link href=https`, `@import/@font-face`,
`url(https`), and `<div/onclick="…">` (the handler regex requires leading whitespace, but
browsers execute the `/`-separated form).
**Fix:** add `<img|<iframe|<source|srcset` external checks; handler regex `[\s/]on[a-z]+\s*=`.

### B4 · P1 · `validate.py` only scans `type:"html"` blocks
**Reproduced.** A `text` block whose `body` carries `<script src="https://…">` and
`<img src=x onerror=…>`, and a `faq` answer with `onerror=`, all pass. `text.body` is emitted
raw by the renderer.
**Fix:** run the html checks over every markup-bearing string prop (`text.body`, `faq` and
`testimonials` items).

### B5 · P2 · `olive.py` hand-rolled flag parsing is fragile
`save gosura cfg --label --status draft` silently sets the label to the literal `"--status"`.
A dangling `--label` raises a bare `IndexError`; `activate abc` raises `ValueError` (both exit
non-zero, so fail-safe). `--status` is unvalidated.
**Fix:** use `argparse`; validate `status ∈ {draft, active, archive}`.

### B6 · P2 · `assemble.py` silently drops `overrides` set in meta.json, and skips mis-numbered fragments
`config["meta"]["overrides"]` comes only from overrides.json and the later `setdefault` cannot
override it, so an `overrides` key in meta.json is silently lost. `FRAGMENT_RE = ^\d\d-` drops
`5-x.json` / `100-x.json` with only a stdout warning. Both silently produce a wrong config.
**Fix:** hard-error on `overrides` inside meta.json; make a skipped `.json` fragment a
non-zero exit.

### B7 · P2 · `preview/serve.py` serves the whole repo root
**Reproduced:** HTTP 200 on `/.git/config` and `/.claude/settings.json`. Bound to 127.0.0.1 and
path traversal is blocked, so it is localhost-only — but it exposes files the preview never
needs. Port arg unvalidated (crashes on non-int).
**Fix:** serve only `preview/` plus the `research/` CSS, or a temp dir; validate the port.

### B8 · P2 · `render.py` breaks if an override value contains `</script>`
**Reproduced.** Overrides are inlined via `json.dumps` into a `<script>`; a literal `</script>`
closes the tag early. Preview-only.
**Fix:** escape `<` as `<`.

### B9 · P2 · `olive.py` error and SSE handling
HTTP 401/403/5xx surface as raw urllib tracebacks, bypassing the clean `MCP error:` path and
discarding the JSON-RPC error body. The SSE parser takes only the first `data:` line
(suspected limitation; the live endpoint returns plain JSON).
**Fix:** catch `HTTPError` and parse its body; iterate SSE events.

**Checked and clean:** `.claude/settings.json` has no unprompted write path —
`call landing_save_version` / `call landing_activate` and the `save`/`activate` wrappers are
not allowlisted, and `call landings *` cannot prefix-match `landing_save_version`. No stale
hardcoded-token references remain anywhere.

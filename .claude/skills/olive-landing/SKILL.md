---
name: olive-landing
description: Ship a change to the Olive.kz gosura landing page safely — assemble fragments, validate, render, save a draft, and QA the real server output. Use for any edit to the landing (copy, sections, theme, overrides), for checking a draft before publishing, and when asked to activate or roll back a version.
---

# Shipping a change to the gosura landing

The page is composed **server-side from a fixed block registry** over MCP. There is no
filesystem deploy. You edit JSON fragments, assemble them, and save a version.

Read `research/BRIEF.md` first if you have not this session — it is the verified ground truth
for the block registry, config format, business data and constraints.

## The loop

```bash
# 1. edit fragments — never landing/config.json, it is generated
#    landing/sections/NN-name.json   one {"type":...,"props":{...}} per file
#    landing/meta/meta.json          title + theme tokens
#    landing/meta/overrides.json     CSS-selector patches

python3 tools/assemble.py                       # fragments -> landing/config.json
python3 tools/validate.py landing/config.json   # MUST exit 0 before any save
python3 preview/render.py landing/config.json   # local approximation
python3 preview/serve.py landing/config.json 8787   # 390x844 + desktop, auto-reload

./tools/olive.py save gosura landing/config.json --label "what changed" --status draft
python3 tools/qa.py <version_id>                # QA the REAL server render
```

`validate.py` checks the config is *legal*. `qa.py` checks the page the server actually
*built* — those differ, and only the second catches a block that renders nothing.

Expected `validate.py` warnings (not errors): four `of-`/`#orderFunnel` selectors missing from
the saved old DOM, and one `<script>` advisory for the sticky order bar.

## Safety — the part that matters

1. **Drafts only. Activation is the user's decision, never yours.** Saving never overwrites;
   each save is a new version and `--status draft` does not change what visitors see. Only
   activate when the user explicitly says so:
   `./tools/olive.py activate <version_id>`
   Rollback = activate the previous id. **Live baseline: 871.**
2. **Never fabricate** a number, dish, price, review, certification or medical claim. Pull real
   data from `./tools/olive.py call meals|overview|delivery_zones|pricing_periods`. Note that
   "orders" ≠ "fulfilled orders" — a large share historically never get paid.
3. **Never restructure the order form.** Inside `#order`, `#order-menu`, `#orderFunnel`, `.of`,
   `.sf-form` only `text`/`style`/`addClass` overrides apply; `html` is dropped there.
   Overrides must never set `id`, `name`, `data-*` or `on*`.
4. **Every CTA needs `data-cta`** — the platform counts conversions by that attribute alone.

## Facts that cost effort to learn

- The edge WAF 403s default HTTP agents. `tools/olive.py` sends a browser UA; with `curl` pass
  `-A "Mozilla/5.0 (iPhone; ...)"`.
- `order_funnel`'s `offer` prop is an **object** `{badge, title, subtitle}`.
- `home_quality` renders **nothing** on a landing; `home_result` claims «400 блюд» vs 297 in
  the API. Both are hard-failed by `tools/qa.py`.
- The server emits `html` block content **raw, with no wrapper** — each block brings its own
  `<section>` and padding.
- `meta.theme` compiles to `--l-*` variables *and* to `body .of { --of-* }`.
- Custom CSS is `gs-`-scoped. Lime `#C4F139` never carries white text (1.31:1).

## Handoffs — the project's memory between runs

`handoff/design-auditor.md`, `handoff/architect.md`, `handoff/implementer.md` carry each role's
living state: verified facts, decisions in force with their evidence, gotchas, and open
questions. Each agent reads its own file first and updates it before finishing.

When you work on the landing **without** delegating, you are standing in for those roles: read
the relevant handoff first, and record anything durable you learn back into it. A fact that
cost effort to establish and lives only in a transcript is lost. Keep them current — a stale
handoff is worse than none, so delete what you disprove.

## For a larger redesign

Use the agent pipeline instead of editing by hand — the definitions live in `.claude/agents/`:

1. `landing-design-auditor` (Fable) — audit + design system.
2. `landing-architect` (Fable) — decisions, section order, copy, and conflict-free work packages.
3. several `landing-implementer` (Opus) **in parallel**, one per work package, each owning
   disjoint files.
4. Then run the loop above yourself: assemble → validate → draft → `qa.py` → report to the user.

Ask implementers to report anything contradicting the plan; those flags have caught real
errors (an unverified `data-cta` claim, a copy regression against the block's own defaults).

# olive-hac — Gosura landing (Olive.kz conversion hackathon)

We own one page: **https://olive.kz/l/gosura**. Olive drives paid ads to it and the winner is
whoever's page produces the most sales. So this repo is a **mobile conversion-rate project**,
not a website build — the page is composed server-side from a fixed block registry over MCP.

Start with **[research/TZ.md](research/TZ.md)** — the assignment itself: what the contest asks
for, what it is *not*, how winning is measured, and what is still unconfirmed. Then
**[research/BRIEF.md](research/BRIEF.md)** — verified ground truth (block registry, config
format, business data, hard constraints). Everything else builds on those two.

## Layout

| path | what |
|---|---|
| `research/` | ground truth: BRIEF, saved live HTML/CSS, MCP dumps, recon renders |
| `design/` | `AUDIT.md` (mobile + conversion audit), `DESIGN_SYSTEM.md` (tokens, `gs-` components) |
| `plan/` | `ARCHITECTURE.md` (decisions + section table), `WORK_PACKAGES.md` (build plan) |
| `landing/meta/` | `meta.json` (title + theme), `overrides.json` (CSS-selector patches) |
| `landing/sections/` | one JSON fragment per section, merged in filename order |
| `landing/config.json` | **generated** — never hand-edit |
| `tools/` | `olive.py` (MCP client), `assemble.py`, `validate.py`, `qa.py`, `ship.sh` (one-shot ship loop) |
| `preview/` | `render.py`, `serve.py` — local mobile preview |

## Workflow

### One-shot: ship a draft by token

Everything below is plain Python; `tools/ship.sh` is the glue that runs the whole loop
(assemble → validate → save **draft** → QA the real server render) in one command:

```bash
tools/ship.sh <token>                            # token or the full https://…/landings/<token> URL
tools/ship.sh -l "v8 hero copy" <token>          # with a version label
tools/ship.sh -n <token>                         # dry-run: validate + show the save call, no write
tools/ship.sh                                    # token taken from $OLIVE_MCP_URL if exported
```

It prints the new version id and `https://olive.kz/l/gosura?v=<id>` preview URL, and exits
non-zero if validation or QA fails. It **never activates** — going live is always the manual
`./tools/olive.py activate <id>` (rollback = activate the previous id).

### Step by step (what ship.sh runs, plus the local preview)

```bash
python3 tools/assemble.py                        # fragments -> landing/config.json
python3 tools/validate.py landing/config.json    # must exit 0 before any save
python3 preview/render.py landing/config.json    # one-shot local render
python3 preview/serve.py landing/config.json 8787  # 390x844 + desktop, auto-reload

./tools/olive.py show gosura                     # versions and their status
./tools/olive.py save gosura landing/config.json --label "v2" --status draft
python3 tools/qa.py <version_id>                 # QA what the server actually built
```

`OLIVE_MCP_URL` carries the endpoint token — a credential, deliberately not in the repo.
Either pass the token to `ship.sh` as an argument, or export the URL yourself:

```bash
export OLIVE_MCP_URL='https://olive.kz/mcp/landings/<token>'
```

Never commit the token; `olive.py` masks it in error output, and `ship.sh` never echoes it.
Note: the local preview renders the funnel as a placeholder and olive.kz images as gradient
fallbacks — only `qa.py <id>` against the server render is authoritative.

The edge WAF 403s default HTTP agents — `olive.py`
sends a browser User-Agent, and `curl` needs `-A "Mozilla/5.0 ..."`.

## Safety rules

1. **Drafts only.** `landing_save_version` never overwrites — each save is a new version, and
   `--status draft` does not change what visitors see. **Activation is a user decision.**
   Rollback = activate the previous id (live baseline: **871**).
2. **No fabricated content** — every number, dish, price and claim traces to an MCP tool or the
   live page. This page takes real money.
3. **Never restructure the order form.** `#order`, `#order-menu`, `#orderFunnel`, `.of`,
   `.sf-form` accept only `text` / `style` / `addClass` overrides; `html` is dropped there.
4. Overrides must never set `id`, `name`, `data-*` or `on*` attributes — they carry order logic.

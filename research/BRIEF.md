# Olive.kz Hackathon — Ground Truth Brief

**Read this before doing anything.** It is verified fact pulled from the live MCP endpoint
and the live page, not assumption.

## 1. What the contest actually is

We own one landing page: **https://olive.kz/l/gosura** (slug `gosura`).
Olive runs **paid ads into it**. The winner is whoever's page produces **the most sales**.

So this is a **conversion-rate optimisation job on a mobile landing page**, not a
"build a website" job. Ad traffic in Kazakhstan is overwhelmingly mobile → **mobile-first
is the whole game**, which is exactly what the user asked for.

## 2. How we ship (the only deploy path)

There is no filesystem deploy. The page is composed server-side from a **block registry**
via an MCP endpoint. Drive it with the repo helper:

```bash
./tools/olive.py list-tools
./tools/olive.py show gosura
./tools/olive.py call meals '{"per_page":5}'
./tools/olive.py save gosura landing/config.json --label "v2 mobile" --status draft
./tools/olive.py activate <version_id>
```

Endpoint: `https://olive.kz/mcp/landings/<token>`, read from `$OLIVE_MCP_URL` (required — the
token is a credential and is never committed).

**Versioning is safe.** `landing_save_version` never overwrites — every save creates a new
version. `status=draft` does **not** publish; it returns a `preview_url`. Only
`landing_activate` (or `status=active`) changes what visitors see, and it demotes the
previously active version to draft, so rollback = activate the old id.

> **Rule: never publish without explicit user approval.** Iterate on drafts.

## 3. Config format (authoritative)

```json
{
  "meta": {
    "title": "...",
    "theme": { "primary": "#RRGGBB" },
    "overrides": [ { "selector": "...", "text": "..." } ]
  },
  "sections": [ { "type": "hero", "props": { } } ]
}
```

### Available blocks (`type` values) — nothing else validates

**Full-page / order machinery (real, working checkout — do not rebuild these):**

| type | what it is | props |
|---|---|---|
| `home` | entire olive.kz homepage duplicate | — |
| `order` | full order block (plans, calendar, menu, checkout) | — |
| `order_menu` | plans + dish menu + form (top of homepage) | `heading`, `subheading`, `banner` |
| `order_filters` | preference/allergen filters + modals | — |
| `order_funnel` | **step-by-step order wizard, mobile-first, per prototype** | `offer`, `hero_title`, `hero_sub` |

**Homepage sections (prebuilt, styled):** `home_map`, `home_faq`, `home_banner`,
`home_result`, `home_marquee`, `home_menu`, `home_advantages`, `home_quality`, `home_promo`

**Free-form blocks (our design surface):**

| type | props |
|---|---|
| `hero` | `heading`, `subheading`, `image`, `cta_text`, `cta_href`, `align` |
| `text` | `heading`, `body`, `align` |
| `html` | `content` — **arbitrary HTML, our main creative lever** |
| `features` | `heading`, `items` |
| `cta` | `heading`, `subheading`, `cta_text`, `cta_href` |
| `testimonials` | `heading`, `items` |
| `faq` | `heading`, `items` |
| `lead_form` | `heading`, `subheading`, `button_text` |

### Theme tokens (`meta.theme`)

| token | default | role |
|---|---|---|
| `primary` | `#C4F139` | lime accent — button fills, highlights |
| `primaryHover` | `#D5FA6B` | accent hover |
| `primaryDark` | `#194536` | deep green — headings, text on buttons, icons |
| `ink` | `#181717` | body text |
| `bgSoft` | `#F2F2F2` | soft section background |
| `bgAccent` | `#EAF3DF` | light accent wash |

### Overrides (`meta.overrides`) — CSS-selector patches over rendered markup

Keys: `selector` (required), `text`, `html`, `style` (string or object), `addClass`, `attrs`.

**Hard limits — respect or the save is rejected / silently ignored:**
- `attrs` may **never** set `id`, `name`, `data-*`, `on*` — those carry order logic.
- Inside the order form (`#order`, `#order-menu`, `#orderFunnel`, `.of`, `.sf-form`) only
  `text` / `style` / `addClass` apply. `html` is **not** applied there — payment structure is protected.
- Selectors must come from the real DOM: `research/gosura.html` (saved) or `GET /l/gosura`.

## 4. Business data — this drives the design, not taste

From `orders_summary` / `overview` (whole history, 1130 orders, ₸92,314,210 revenue):

**Average order: ₸81,694.** Customers: 717. Callback requests: 24.

**By meal plan — the weight-loss segment dominates:**

| plan | orders | share |
|---|---|---|
| **1 200 Ккал** | **474** | **42%** |
| 1 500 Ккал | 293 | 26% |
| 1 800 Ккал | 247 | 22% |
| 2 500 Ккал | 115 | 10% |

→ ~68% of buyers are on a **weight-loss** plan (1200/1500). The hero must speak to
weight loss first, not generic "healthy eating".

**By subscription length — the 5-day plan is the real entry point:**

| days | orders |
|---|---|
| 1 | 220 |
| 2 | 49 |
| **5** | **477** |
| 14 | 341 |
| 30 | 43 |

→ **5 days is the #1 seller**, 14 days is #2. The site currently pushes "14 days + 14 free"
hardest, but buyers actually start at 5 days. Lead with the **5-day trial as the low-friction
entry**, present 14-day as the value upsell.

**Gift days (`pricing_periods`): every multi-day period doubles — 5+5, 14+14, 30+30.**
"Pay for 5 days, eat for 10" is a genuinely strong, underused offer.

**The biggest leak: 482 of 1130 orders (43%) sit in `pending_payment` vs 648 `sent`.**
Nearly half of everyone who completes the order form never pays. Reducing payment-step
friction and anxiety is worth more than any extra top-of-funnel traffic.

## 5. Current state of our page — a blank slate

Active version **id 871**, label "Дубль главной": a plain duplicate of the homepage.

```
order_menu, home_map, home_faq, home_banner, home_result, home_marquee,
home_menu, home_advantages, home_quality, home_promo, order_filters
```

No `meta` at all — no title, no theme, no overrides.

**Its measured stats: 9 impressions, 0 CTA clicks, 0 conversions, avg time 31s, CR 0.**

Note the section order is essentially arbitrary — the map and FAQ appear before any
proof or value content. There is a lot of headroom.

## 6. Design system of the live site (match it or beat it deliberately)

- CSS: Bootstrap 5 + custom `client.css` (69KB) and `landing.css`, BEM-ish prefix **`sf-`**.
- Fonts: **"Loos Wide"** (display) and **"Museo Sans Cyrl"** (text).
- Brand: lime `#C4F139` on deep green `#194536`, ink `#181717`, soft grey `#F2F2F2`.
- Key real selectors: `.sf-header`, `.sf-banner__title`, `.sf-features__item`, `.sf-faq`,
  `.sf-form`, `#order`, `#order-menu`, `#orderBtn`, `#orderPrice`, `.sf-green-btn--classic`,
  `.sf-marquee__item`, `.sf-footer`.
- Live page carries Yandex.Metrika (webvisor), GTM, Meta Pixel — conversions are tracked.

Saved locally: `research/gosura.html`, `research/client.css`, `research/landing.css`.

## 7. Real content available for the page

`meals` returns 297 dishes with name, category, mass, **kcal/protein/fat/carbs**, price and
margin — e.g. "Скрембл с индейкой", 220g, 355 kcal, 28/24/6. Use real dishes and real
macros as social proof; do not invent menu items.

`delivery_zones` gives real zone polygons and prices; `delivery_check` validates an address.

## 8. Non-negotiable constraints

1. **Do not fabricate** prices, reviews, testimonials, certifications, counts or medical
   claims. Only real data from MCP tools or the live page. Invented reviews on a page that
   takes real money is fraud, and it would also lose the contest on trust.
2. **Do not break the order flow.** The checkout is real and protected — compose it, style
   it, never restructure it.
3. **Never activate a version without the user's explicit go-ahead.** Drafts + preview only.
4. Real phone/contacts: +7 700 870-26-26, +7 700 870-25-25, info@olive.kz, @o_live.kz,
   ООО ФУДВЕНДИНГ, Алматы, ул. Кожина 11.
5. Page language: **Russian** (Almaty market). Kazakh is "coming soon" on the live site.

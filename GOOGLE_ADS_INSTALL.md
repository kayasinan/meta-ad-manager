# Google Ads AI Agent System — Installation Guide

## What's In This Package

```
google-ads-system/
├── INSTALL.md                                      ← You are here
├── schema/
│   └── google-ads-supabase-schema.sql              ← Additive schema (runs AFTER meta-ads schema)
└── skills/
    ├── google-ads-setup.tar.gz                     ← INSTALL THIS FIRST
    ├── google-ads-orchestrator.tar.gz              ← Machine A — the brain
    ├── google-ads-data-placement-analyst.tar.gz    ← Machine B — Priority 1
    ├── google-ads-creative-analyst.tar.gz          ← Machine B — Priority 2
    ├── google-ads-postclick-analyst.tar.gz         ← Machine B — Priority 3
    ├── google-ads-competitive-intel.tar.gz         ← Machine B — Priority 4
    ├── google-ads-creative-producer.tar.gz         ← Machine B — Priority 5
    ├── google-ads-campaign-creator.tar.gz          ← Machine B — Priority 6
    └── google-ads-campaign-monitor.tar.gz          ← Machine B — Priority 7
```

Each `.tar.gz` contains a complete OpenClaw skill package:
```
google-ads-<name>/
├── SKILL.md              ← Skill definition with YAML frontmatter + full execution procedures
├── references/           ← Reference documentation (markdown)
└── scripts/              ← Utility scripts (Python)
```

## Architecture Overview

Same split-machine architecture as the Meta Ads system — **same machines, same database, same credentials**:
- **Machine A** — Same machine as Meta Ads. Runs both orchestrators (one at a time).
- **Machine B** — Same machine as Meta Ads. Runs all 14 sub-agents (7 Meta + 7 Google), one at a time.
- **Supabase** — Same project, same credentials. Google tables are prefixed with `g_` — no conflict with Meta tables.
- **OpenClaw** — Already installed from Meta setup.

**IMPORTANT — Do NOT run Meta and Google cycles at the same time.** The machines run agents sequentially and are not designed for concurrent execution. Always complete one platform's full cycle before starting the other.

```bash
# Correct: run one after the other
openclaw run meta-ads-orchestrator --brand <BRAND_ID>
# ... wait for Meta cycle to complete ...
openclaw run google-ads-orchestrator --brand <BRAND_ID>

# WRONG: do NOT run both simultaneously
# openclaw run meta-ads-orchestrator &
# openclaw run google-ads-orchestrator &   ← DO NOT DO THIS
```

Both systems share `brand_config` (extended with Google Ads fields), `landing_pages`, `alerts`, `recommendations`, and `human_creative_inspiration`. A brand can have both Meta Ads and Google Ads active — just run their cycles sequentially.

## Prerequisites

Before you start, make sure you have:

1. **The Meta Ads system already installed** (same Supabase, same machines) — or at minimum, the Meta Ads schema applied
2. **A Google Ads account** with:
   - Customer ID (xxx-xxx-xxxx)
   - Manager Account ID if under MCC
   - API developer token (from Google Ads API Center)
   - OAuth2 credentials (client ID, client secret, refresh token)
3. **Google Merchant Center** (for Shopping campaigns) — Merchant Center ID
4. **YouTube channel** (for Video campaigns) — Channel ID
5. **GA4 property** — same one used for Meta Ads (already set up)
6. **Gemini API key** — same one used for Meta Ads (already set up)

## Installation — 4 Steps

### Step 1: Update Existing Meta Ads Skills

The Meta Ads skills need to know about the shared infrastructure. Update the existing Meta Ads INSTALL.md and orchestrator on Machine A to include the sequential execution rule.

**On Machine A**, replace the existing Meta Ads orchestrator with the updated version that includes the "Shared Infrastructure" section:

```bash
# On Machine A — update the Meta Ads orchestrator with shared-infra awareness
tar xzf skills/meta-ads-orchestrator-updated.tar.gz -C ~/.openclaw/skills/
```

If you don't have the updated Meta package, the key rule to add to your existing Meta Ads orchestrator configuration is:

> **Sequential Execution Rule:** Before starting a Meta Ads cycle, verify no Google Ads cycle is running for the same brand. Check: `SELECT COUNT(*) FROM optimization_cycles WHERE brand_id = $BRAND_ID AND status NOT IN ('COMPLETED') AND agent_name LIKE 'g_%'`. If count > 0, wait for the Google Ads cycle to complete first.

### Step 2: Install Google Ads Setup Skill + Orchestrator on Machine A

```bash
# On Machine A
tar xzf skills/google-ads-setup.tar.gz -C ~/.openclaw/skills/
tar xzf skills/google-ads-orchestrator.tar.gz -C ~/.openclaw/skills/
```

### Step 3: Run the Setup Skill

```bash
openclaw run google-ads-setup
```

The Setup Skill walks you through 8 phases:

| Phase | What Happens | You Provide |
|-------|-------------|-------------|
| 0 | Self-check | Nothing — verifies Machine A is ready, detects existing Meta Ads installation |
| 1 | Supabase setup | Runs google-ads-supabase-schema.sql (extends existing schema, does NOT touch Meta tables) |
| 2 | Google Ads credentials | Developer token, OAuth2 client ID/secret/refresh token |
| 3 | Machine B connection | Reuses existing SSH connection from Meta setup (verifies it still works) |
| 4 | Agent deployment | Copies 7 Google Ads sub-agent `.tar.gz` to Machine B (alongside existing Meta agents) |
| 5 | Brand onboarding | Google Ads CID, Merchant Center, YouTube, conversion actions, targets |
| 6 | Agent testing | Tests each Google Ads agent one-by-one (waits if Meta cycle is running) |
| 7 | System readiness | Creates first Google Ads optimization cycle |

**Phase 5** links to existing brands in `brand_config`. If a brand already exists from Meta Ads setup, it adds Google Ads fields (`google_ads_customer_id`, `google_merchant_center_id`, etc.) to the **same row** — no duplication.

### Step 4: Start Running Cycles (Sequential — Never Concurrent)

```bash
# ALWAYS run one platform at a time, never both together.
# Recommended order: Meta first, then Google.

# 1. Run Meta Ads cycle
openclaw run meta-ads-orchestrator --brand <BRAND_ID>
# ... wait for Meta cycle to complete ...

# 2. Then run Google Ads cycle
openclaw run google-ads-orchestrator --brand <BRAND_ID>
```

**Why sequential?** Both systems share Machine B for agent execution. Machine B runs one agent at a time. Running both platforms concurrently would cause agents to queue unpredictably, potentially mixing Meta and Google tasks within the same cycle window and producing unreliable results.

## Key Differences from Meta Ads System

| Aspect | Meta Ads | Google Ads |
|--------|----------|------------|
| Campaign hierarchy | Campaign → Ad Set → Ad | Campaign → Ad Group → Ad + Keywords |
| Campaign types | Standard, ASC | Search, Shopping, Display, Video, PMax, Demand Gen |
| Competitive intel | Meta Ad Library (API) | Google Ads Transparency Center (web) |
| Creative diversity | Andromeda clusters | Ad Strength (POOR/AVG/GOOD/EXCELLENT) |
| Unique signals | Frequency, Reactions | Quality Score, Impression Share, Search Terms |
| Bid strategies | LOWEST_COST, COST_CAP, BID_CAP, MIN_ROAS | TARGET_CPA, TARGET_ROAS, MAX_CONV, MANUAL_CPC, etc. |
| UTM source | facebook / paid_social | google / cpc, display, video |
| Database tables | campaigns, ad_sets, ads | g_campaigns, g_ad_groups, g_ads, g_keywords |

## Key Settings Per Brand (set during onboarding)

| Setting | What It Controls |
|---------|-----------------|
| `target_ar_roas` | The ROAS you're optimizing toward |
| `min_acceptable_ar_roas` | Floor — campaigns below this for 7+ days get pause recommendations |
| `weekly_ad_volume` | New ad creatives per week (default: 3) |
| `scaling_config` | Auto-scaling proposals: step size, min ROAS, cooldown |
| `ar_multiplier` | GA4 correction factor (default 1.2) |
| `google_ads_customer_id` | Google Ads account CID |
| `google_merchant_center_id` | For Shopping campaigns |
| `youtube_channel_id` | For Video campaigns |

## Troubleshooting

- **Setup fails at a phase?** Re-run: `openclaw run google-ads-setup --phase <N>`
- **Agent stuck?** Check `agent_deliverables` for BLOCKED status where `agent_name LIKE 'g_%'`
- **Schema conflict?** The Google schema uses `g_` prefixed tables — no conflict with Meta tables
- **Same brand, both platforms?** One `brand_config` row can have both `meta_ad_account_id` AND `google_ads_customer_id`

## Safety Rules

- **Budget Authority:** System NEVER spends without your explicit approval
- **Draft-First:** All campaigns created PAUSED — you approve before enabling
- **Scaling:** Detected and proposed, but YOU approve every budget increase
- **No secrets in database:** API tokens stored in Supabase Vault

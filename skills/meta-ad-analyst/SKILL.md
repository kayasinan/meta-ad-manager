---
name: meta-ad-analyst
description: Analyze Meta (Facebook/Instagram) ad account performance using Meta Ads API and GA4 Data API. Two modes — (1) Historical Intelligence to inform new campaign setup, and (2) Live Campaign Check to optimize running campaigns. Extracts winning color schemes, audience segments, creative patterns, and waste. Use when asked to audit ad performance, analyze past campaigns, check a running campaign, find waste, detect cannibalization, compare creatives, or produce data-driven recommendations.
---

# Meta Ad Analyst

Two-mode analysis framework for Meta Ads accounts.

## Modes

### Mode 1: Historical Intelligence (for new campaign setup)

Analyze 60/90/365-day data across all past campaigns to answer: **"What should our next campaign look like?"**

| Phase | What | Key Output |
|---|---|---|
| 1 | Account Audit + Meta vs GA4 verification | Truth gap %, account overview |
| 2 | Segment Breakdowns (demo, placement, device, hourly, geo) | Best/worst segments per dimension |
| 3 | 21-Query Ad Deep Dive | Granular combo performance |
| 4 | Cannibalization Analysis | Overlap map, CPM inflation estimate |
| 5 | Budget Analysis | Budget-capped winners, reallocation scenarios |
| 6 | Creative Format Comparison | Format ranking (static vs video vs carousel) |
| 7 | Creative Content Deep Dive + Color Scheme Analysis | Visual/copy/color patterns, winning themes |
| 8 | Waste Quantification + Campaign Blueprint | $/month waste, recommended structure for next campaign |

**Output feeds into:**
- **meta-ad-creator** — winning color schemes, top breeds/subjects, proven copy angles
- **meta-ad-optimizer** — recommended actions (what to exclude, scale, consolidate)

### Mode 2: Live Campaign Check (for active campaigns)

Analyze a specific running campaign to answer: **"What should we change right now?"**

| Check | What | Key Output |
|---|---|---|
| Performance | Last 7/14/30d metrics vs account average | Over/underperformers flagged |
| Fatigue | Frequency, CTR trend, CPA trend | Ads needing refresh |
| Waste | Dead placements, bad hours, cold segments | $ being wasted right now |
| Cannibalization | Active ad sets competing for same audience | Overlap % + CPM inflation |
| Budget | Constrained winners, overfunded losers | Reallocation recommendations |
| Creative | Which ads are tired, which have headroom | Refresh priority list |

**Output:** Prioritized action list for meta-ad-optimizer to execute.

## Setup Requirements

- Meta Ads API credentials (user access token with `ads_read` permission minimum)
- GA4 service account JSON key + Data API enabled in Google Cloud
- Store credentials securely (e.g., `/root/clawd/.meta_ads_credentials`, `/root/clawd/.ga4_service_account.json`)

## Report Generation

Generate a full PDF report for any account, time period, and campaign selection:

```bash
# Full account report — last 60 days
python3 {baseDir}/scripts/generate_report.py \
  --account act_23987596 \
  --account-name "Pet Bucket" \
  --meta-creds /root/clawd/.meta_ads_credentials \
  --ga4-creds /root/clawd/.ga4_service_account.json \
  --ga4-property 323020098 \
  --ga4-source "facebook_ads_ppm" \
  --days 60 \
  --output /root/clawd/PETBUCKET_60D_REPORT.md \
  --pdf

# Specific campaigns only — last 30 days
python3 {baseDir}/scripts/generate_report.py \
  --account act_23987596 \
  --campaigns "23987654321,23987654322" \
  --days 30 \
  --meta-creds /root/clawd/.meta_ads_credentials \
  --ga4-creds /root/clawd/.ga4_service_account.json \
  --ga4-property 323020098 \
  --output /root/clawd/CAMPAIGN_REPORT.md --pdf

# Live campaign check — last 7 days
python3 {baseDir}/scripts/generate_report.py \
  --account act_23987596 \
  --campaigns "23987654321" \
  --days 7 --mode live \
  --meta-creds /root/clawd/.meta_ads_credentials \
  --ga4-creds /root/clawd/.ga4_service_account.json \
  --ga4-property 323020098 \
  --output /root/clawd/LIVE_CHECK.md --pdf
```

### Report Sections

| Section | Contents |
|---------|----------|
| 1. Account Snapshot | Spend, conversions, CPA, ROAS — triple-source. Period-over-period comparison. |
| 2. Tracking Health | Click-to-session rate, Meta-GA4 discrepancy per campaign, UTM integrity |
| 3. Campaign Verdicts | Every campaign with triple-source metrics, ranked by AR ROAS |
| 4. Cannibalization | Audience overlap between ad sets, CPM inflation estimate |
| 5. Audience Segments + Dayparting | Age×Gender, Device, Placement, **Hourly with stop/run schedule**, Geo |
| 6. Frequency Analysis | Frequency distribution, fatigue signals |
| 7. Waste Summary | Dead segments, bad hours, cold audiences — $ amount per category |
| 8. Action Plan | Prioritized recommendations (🔴 high / 🟡 medium / 🟢 low) |
| 9. Top 20 Converting Ads | Best ads ranked by ROAS with: images embedded in PDF, full ad copy (headline + body + description + CTA), campaign/ad set context, performance metrics, and `edit_ad.py` command to feed directly into meta-ad-creator |

### Triple-Source in ALL Tables

Every table shows:
```
| Segment | Spend | Meta P | Meta CPA | Meta ROAS | GA4 P | GA4 CPA | GA4 ROAS | AR P | AR CPA | AR ROAS |
```

- **Meta** = Facebook's reported numbers (over-counts)
- **GA4** = Google Analytics verified (under-counts ~20%)
- **AR (Assumed Real)** = GA4 × 1.2 (best estimate)

### Output Files
- `{ACCOUNT}_{DAYS}D_REPORT.md` — Markdown report
- `{ACCOUNT}_{DAYS}D_REPORT.pdf` — PDF version with embedded ad images (with --pdf)
- `{ACCOUNT}_{DAYS}D_REPORT.html` — HTML version
- **`data/manager_actions_{days}d.json`** — Structured action plan for **meta-ad-manager** (see below)
- `data/top_ads_manifest.json` — Top 20 ads with creative details, image paths, ad copy → **feed into meta-ad-creator**
- `top_ad_images/` — Downloaded ad images (full-size from Meta)
- `data/report_{days}d_meta.json` — Raw Meta API data
- `data/report_{days}d_ga4.json` — Raw GA4 data

### Manager Actions JSON (for meta-ad-manager)

The key output: `data/manager_actions_{days}d.json` — a machine-readable action plan.

```json
{
  "account": "act_23987596",
  "period_days": 60,
  "summary": {
    "total_actions": 12,
    "high_priority": 4,
    "total_estimated_savings_daily": 142.50
  },
  "actions": [
    {
      "type": "dayparting",
      "priority": "high",
      "target": "account",
      "action": "set_ad_schedule",
      "params": {
        "stop_hours": [18, 19, 20],
        "active_hours": [0,1,2,...,17,21,22,23]
      },
      "reason": "Dead hours waste $47/day with zero conversions",
      "estimated_savings_daily": 47.00
    },
    {
      "type": "pause_campaign",
      "priority": "high",
      "target_id": "23987654321",
      "target_name": "PP - Bad Campaign",
      "action": "set_status",
      "params": {"status": "PAUSED"},
      "reason": "CPA $85 is 2.5x account average ($34)",
      "metrics": {"spend": 2400, "meta_cpa": 85, "ar_cpa": 120}
    },
    {
      "type": "scale_budget",
      "priority": "medium",
      "target_id": "23987654322",
      "params": {
        "current_daily_budget": 15.00,
        "suggested_daily_budget": 22.50,
        "increase_pct": 50
      },
      "reason": "ROAS 5.2x is 1.8x account average"
    },
    {
      "type": "add_exclusions",
      "priority": "high",
      "target_id": "23987654323",
      "params": {"exclude_audiences_from": ["id1","id2"], "country": "US"},
      "reason": "5 ad sets competing for US audience"
    },
    {
      "type": "create_variants",
      "priority": "medium",
      "target_id": "6708936337630",
      "params": {
        "source_image": "/path/to/top_01.jpg",
        "variations": 6,
        "swap_dogs": true,
        "command": "python3 edit_ad.py -i /path/to/top_01.jpg --variations 6 --swap-dogs"
      },
      "reason": "#1 ad (ROAS 6.1x). Generate fresh variants."
    }
  ]
}
```

**Action types:**
| Type | What meta-ad-manager does |
|------|--------------------------|
| `dayparting` | Set ad schedule on campaigns/ad sets to exclude dead hours |
| `pause_campaign` | Pause campaign or ad set |
| `scale_budget` | Increase daily budget on winners |
| `add_exclusions` | Add audience exclusions to reduce cannibalization |
| `create_variants` | Trigger meta-ad-creator to generate new creatives |

### meta-ad-creator Integration

The report outputs `data/top_ads_manifest.json` containing for each top ad:
- `ad_id` — Meta ad ID
- `image_local` — path to downloaded image
- `body` — full ad copy text
- `title` — headline
- `description` — link description
- `cta` — call to action type
- `meta_roas`, `meta_cpa`, `spend` — performance metrics

To create variants of a winning ad:
```bash
# Pick ad from manifest and generate 6 variants with dog breed swapping
python3 {baseDir}/../meta-ad-creator/scripts/edit_ad.py \
  -i /path/from/manifest/top_01_12345.jpg \
  --variations 6 --swap-dogs \
  -o /root/clawd/data/new_variants/
```

## Scripts

### `scripts/generate_report.py`
Full report generator. Pulls Meta + GA4 data, cross-verifies, builds triple-source report with all sections.

### `scripts/meta_api.py`
Meta Ads API helper. Key functions:
- `load_token(creds_path)` — load access token from credentials file
- `get_insights(token, account_id, level, breakdowns, ...)` — pull insights with breakdowns
- `get_adsets(token, account_id)` — pull ad sets with targeting
- `get_ads_with_creative(token, account_id)` — pull ads with creative details
- `get_ad_creative_detail(token, ad_id)` — full creative detail for one ad
- `get_action(row, action_type)` / `get_action_value(row, action_type)` — parse actions from response

### `scripts/ga4_api.py`
GA4 Data API helper. Key functions:
- `get_access_token(sa_path)` — get OAuth token from service account
- `run_report(token, property_id, dimensions, metrics, ...)` — run GA4 report
- `parse_report(response)` — parse response into list of dicts
- `make_source_filter(source_value)` — create sessionSource filter

### `scripts/cannibalization_check.py`
Detect audience overlap between ad sets. Run standalone:
```bash
python3 scripts/cannibalization_check.py /path/to/creds account_id
```

## Color Scheme Analysis (Phase 7)

When analyzing ad creatives, extract the color scheme of each top-performing ad using Gemini vision. This data feeds into meta-ad-creator for generating better-converting variants.

### How to extract:
For each winning ad image, send it to Gemini with a prompt requesting a JSON analysis of:
- `background_primary` — color name, hex, coverage %
- `background_secondary` — color name, hex, coverage %
- `badge_colors` — array of {color, hex}
- `accent_colors` — array of {color, hex, usage}
- `text_colors` — array of {color, hex, usage (headlines/body/badges)}
- `overall_palette` — warm/cool/neutral/mixed
- `dominant_mood` — e.g. clean, premium, energetic, calm
- `contrast_level` — high/medium/low
- `color_harmony` — complementary/analogous/triadic/monochromatic

### Output:
Save to `data/creative_meta/color_analysis_winners.json` with each entry tagged with:
- filename, rank, ROAS, spend, product

### Include in reports:
Add a **"Winning Color Schemes"** section to the creative analysis report showing:
- Color scheme table (rank, ROAS, background, badge colors, palette, mood, contrast)
- Key color insights (which backgrounds/badge colors/contrast levels correlate with highest ROAS)
- Color rules derived from data (e.g. "white backgrounds = top 3 ROAS", "green badges appear in 4/5 winners")

## API Gotchas

Read `references/api-gotchas.md` for known limitations:
- Meta geo breakdowns don't return purchase data
- GA4 user-scoped dimensions (age, gender) incompatible with session-scoped source filters
- `frequency_value` empty for ASC campaigns
- Creative asset breakdowns deprecated in v21+
- Campaign hourly breakdown needs quarterly splits

## Triple-Source Measurement

Always report three data sources:
- **Meta** — what Facebook reports (over-counts)
- **GA4** — what Google Analytics tracks (under-counts ~20% due to cookie consent, ad blockers)
- **Assumed Real (AR)** — GA4 × 1.2 (best estimate of true performance)

All tables must show: Meta CPA/ROAS | GA4 CPA/ROAS | AR CPA/ROAS

## Critical Rules

- **This skill is 100% READ-ONLY.** Never edit, pause, create, or modify anything.
- **GA4 is source of truth** for conversion counts and ROI.
- **Meta over-reports** conversions by 25-60% typically. Always disclose this.
- **Campaign matching uses Meta campaign ID**, not name (campaigns get renamed).
- **Every report improvement must be saved to the skill scripts immediately.** When the user requests a change to report format, styling, sections, or data — update generate_report.py (or the relevant script) so ALL future reports include the fix. Never apply one-off fixes.
- Save raw API responses to `data/{account_name}/` for reproducibility.
- Save reports as `{ACCOUNT}_SEGMENT_REPORT.md` and `{ACCOUNT}_CREATIVE_ANALYSIS.md`.


## ⚠️ DOUBLE-CONFIRMATION RULE (MANDATORY)
Before executing ANY campaign change (pause, enable, create, modify budgets, targeting, creatives, bids, exclusions, or any other modification), you MUST:
1. Present the proposed changes clearly to the user
2. Ask for explicit confirmation ONE MORE TIME before executing
3. Only proceed after receiving that second confirmation
This applies to ALL changes — no exceptions. This prevents accidental modifications.

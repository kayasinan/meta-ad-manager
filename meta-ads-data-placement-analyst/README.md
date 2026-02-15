# Data & Placement Analyst (Agent 1)

**Location:** Machine B

Foundation agent — pulls all raw data from Meta Ads API and GA4, computes triple-source metrics, and identifies winners/losers across campaigns, ad sets, and ads.

## Responsibilities
- Pull 21+ Meta API queries (campaigns, ad sets, ads, age, gender, placement, device, hourly, geo, frequency)
- Pull 8+ GA4 queries (sessions, campaigns, ads, landing pages, funnel, device, geo, engagement)
- Compute triple-source metrics: Meta | GA4 | Assumed Real (GA4 × 1.2)
- Classify campaigns/ad sets as winners, losers, ghosts
- Detect cannibalization and audience overlap
- Identify dead hours and weak placements

## Outputs → Supabase
- Account summary with AR CPA and AR ROAS
- Campaign verdicts with tier classification
- Top 20 ads by ROAS for Agent 2
- Dayparting analysis
- Cannibalization map

## Key Files
- `SKILL.md` — Agent instructions
- `scripts/` — Python analysis scripts

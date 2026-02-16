# Google Ads Schema Reference

This document describes the Google Ads-specific database tables and their relationships to the Meta Ads infrastructure.

## Google Ads Tables (g_* prefix)

All Google Ads-specific tables use the `g_` prefix to distinguish them from Meta Ads tables. They follow the same structure and relationship patterns as their Meta counterparts.

### g_campaigns

Stores Google Ads campaign configurations.

```sql
CREATE TABLE g_campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  campaign_id BIGINT NOT NULL, -- Google Ads Campaign ID
  campaign_name VARCHAR NOT NULL,
  status VARCHAR (ENABLED, PAUSED, REMOVED),
  campaign_type VARCHAR (SEARCH, DISPLAY, SHOPPING, VIDEO, PMAX),
  objective VARCHAR,
  start_date DATE,
  end_date DATE,
  budget NUMERIC(15,2),
  bid_strategy VARCHAR (TARGET_CPA, TARGET_ROAS, MANUAL_CPC, etc.),
  target_cpa NUMERIC(10,2),
  target_roas NUMERIC(6,2),
  daily_budget NUMERIC(15,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(brand_id, campaign_id)
);
```

**Key Fields:**
- `campaign_id`: The actual Google Ads Campaign ID (numeric, not a string)
- `campaign_type`: Search, Display, Shopping, Video, or Performance Max
- `bid_strategy`: How Google optimizes bids (Target CPA, Target ROAS, Manual CPC, etc.)
- `target_cpa` / `target_roas`: Bid strategy parameters

### g_ad_groups

Ad groups within Google Ads campaigns. In Google Ads, ad groups are the organizational unit that contains keywords and ads.

```sql
CREATE TABLE g_ad_groups (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  campaign_id UUID NOT NULL REFERENCES g_campaigns(id),
  ad_group_id BIGINT NOT NULL, -- Google Ads Ad Group ID
  ad_group_name VARCHAR NOT NULL,
  status VARCHAR (ENABLED, PAUSED, REMOVED),
  cpc_bid NUMERIC(10,2),
  cpa_bid NUMERIC(10,2),
  quality_score INT (1-10 scale),
  estimated_ctr NUMERIC(5,2), -- Expected CTR percentage
  ad_relevance VARCHAR (EXCELLENT, GOOD, AVERAGE, POOR, UNKNOWN),
  landing_page_experience VARCHAR (EXCELLENT, GOOD, AVERAGE, POOR, UNKNOWN),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(brand_id, ad_group_id)
);
```

**Key Fields:**
- `quality_score`: 1-10 scale. Impacts CPC and ad rank. Drives efficiency.
- `estimated_ctr`: Historical click-through rate expectation
- `ad_relevance`: How well ads match the keywords
- `landing_page_experience`: Page quality relative to keywords

### g_ads

Individual ads within ad groups (similar to ad creatives).

```sql
CREATE TABLE g_ads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  ad_group_id UUID NOT NULL REFERENCES g_ad_groups(id),
  ad_id BIGINT NOT NULL, -- Google Ads Ad ID
  status VARCHAR (ENABLED, PAUSED, REMOVED),
  ad_type VARCHAR (RESPONSIVE_SEARCH_AD, EXPANDED_TEXT_AD, etc.),
  headline_1 VARCHAR,
  headline_2 VARCHAR,
  headline_3 VARCHAR,
  description_line_1 VARCHAR,
  description_line_2 VARCHAR,
  display_url VARCHAR,
  final_url VARCHAR,
  utms_json JSONB, -- Contains utm_source, utm_medium, utm_campaign, utm_content, utm_term
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(brand_id, ad_id)
);
```

**Key Fields:**
- `ad_type`: Responsive Search Ad, Expanded Text Ad, etc.
- `headline_1`, `headline_2`, `headline_3`: Ad headlines (RSA allows multiple, ETAs have 2)
- `description_line_1`, `description_line_2`: Ad copy
- `utms_json`: All UTM parameters for tracking purposes

### g_keywords

Keywords targeted in ad groups (Search campaign specific).

```sql
CREATE TABLE g_keywords (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  ad_group_id UUID NOT NULL REFERENCES g_ad_groups(id),
  keyword_id BIGINT NOT NULL, -- Google Ads Keyword ID
  keyword_text VARCHAR NOT NULL,
  match_type VARCHAR (EXACT, PHRASE, BROAD, BROAD_MODIFIED),
  status VARCHAR (ENABLED, PAUSED, REMOVED),
  max_cpc NUMERIC(10,2),
  quality_score INT (1-10 scale),
  estimated_ctr NUMERIC(5,2),
  ad_relevance VARCHAR,
  landing_page_experience VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(brand_id, keyword_id)
);
```

**Key Fields:**
- `match_type`: Exact (exact phrase), Phrase (contains phrase), Broad (related terms), Broad Modified (individual word matching)
- `quality_score`: Similar to ad group but at keyword level
- `max_cpc`: Maximum cost per click you're willing to pay

### g_daily_metrics

Daily performance metrics for Google Ads campaigns, at the ad group or campaign level.

```sql
CREATE TABLE g_daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  campaign_id UUID NOT NULL REFERENCES g_campaigns(id),
  ad_group_id UUID REFERENCES g_ad_groups(id), -- Can be NULL for campaign-level metrics
  date DATE NOT NULL,
  impressions INT,
  clicks INT,
  cost NUMERIC(15,2),
  conversions NUMERIC(10,2), -- From Google Ads (may overcount)
  conversion_value NUMERIC(15,2),
  ctr NUMERIC(6,4), -- Click-through rate
  cpc NUMERIC(10,2), -- Cost per click
  cpa NUMERIC(10,2), -- Cost per conversion (Google reported)
  roas NUMERIC(6,2), -- Return on ad spend (Google reported)
  -- Triple-source columns:
  ga4_conversions NUMERIC(10,2), -- From GA4 (conservative)
  ar_conversions NUMERIC(10,2), -- AR (Assumed Real) = GA4 × ar_multiplier
  ar_cpa NUMERIC(10,2), -- AR CPA for decision-making
  ar_roas NUMERIC(6,2), -- AR ROAS for decision-making
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(brand_id, campaign_id, ad_group_id, date)
);
```

**Key Fields:**
- `conversions`: Google Ads reported (often inflated)
- `ga4_conversions`: GA4 session-based (conservative, ~20% under-count)
- `ar_conversions`: GA4 × ar_multiplier (best estimate)
- `ar_cpa`, `ar_roas`: Decision-making metrics (always use AR, not Google reported)

## Shared Tables (Used by Both Meta and Google)

These tables are used by both Meta Ads and Google Ads systems, with brand_id scoping:

### brand_config (Google Ads Extended Fields)

The main brand configuration table has Google Ads-specific fields:

```sql
-- Google Ads-specific fields in brand_config:
google_ads_customer_id VARCHAR, -- Format: xxx-xxx-xxxx
google_ads_mcc_id VARCHAR, -- Manager Account ID (optional)
google_ads_developer_token_vault_ref UUID, -- Reference to vault secret
google_ads_oauth_client_id VARCHAR,
google_ads_oauth_secret_vault_ref UUID, -- Reference to vault secret
google_ads_refresh_token_vault_ref UUID, -- Reference to vault secret
merchant_center_id VARCHAR, -- For Shopping campaigns
youtube_channel_id VARCHAR, -- For Video campaigns
conversion_action_ids JSONB, -- Array of conversion tracking IDs
bid_strategy_preference VARCHAR, -- TARGET_CPA, TARGET_ROAS, etc.
```

### daily_metrics (Shared Structure)

The shared `daily_metrics` table can store both Meta and Google metrics with a `platform` field:

```sql
CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  platform VARCHAR (META, GOOGLE), -- Which platform this metric is from
  campaign_id VARCHAR, -- Platform-specific campaign ID
  campaign_name VARCHAR,
  date DATE NOT NULL,
  impressions INT,
  clicks INT,
  cost NUMERIC(15,2),
  conversions NUMERIC(10,2), -- Platform reported
  conversion_value NUMERIC(15,2),
  ctr NUMERIC(6,4),
  cpc NUMERIC(10,2),
  cpa NUMERIC(10,2),
  roas NUMERIC(6,2),
  ga4_conversions NUMERIC(10,2), -- GA4 True
  ar_conversions NUMERIC(10,2), -- AR (GA4 × ar_multiplier)
  ar_cpa NUMERIC(10,2),
  ar_roas NUMERIC(6,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(brand_id, platform, campaign_id, date)
);
```

### tracking_health (Multi-Platform)

Tracks data integrity for both Meta and Google:

```sql
-- Fields in tracking_health relevant to Google Ads:
gclid_passing BOOLEAN, -- Are gclid parameters being captured?
click_to_session_rate NUMERIC(6,4), -- Google clicks to GA4 sessions ratio
-- Other fields same as Meta...
```

### audiences

Audience segments created from campaign data. Both Meta and Google can use these:

```sql
CREATE TABLE audiences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  source_platform VARCHAR (META, GOOGLE, CUSTOM),
  audience_name VARCHAR NOT NULL,
  audience_config JSONB, -- Platform-specific config
  size INT, -- Number of users/sessions in audience
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### creative_registry

Stores creative assets. All platforms (Meta, Google, custom) can reference these:

```sql
CREATE TABLE creative_registry (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_id UUID NOT NULL REFERENCES brand_config(id),
  platform VARCHAR (META, GOOGLE, GENERIC), -- Which platform this is for
  asset_type VARCHAR (IMAGE, VIDEO, TEXT, COPY),
  asset_data JSONB,
  status VARCHAR (ACTIVE, ARCHIVED, REJECTED),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

## UTM Parameter Schema (Google Ads)

All Google Ads ads must include consistent UTM parameters for GA4 attribution:

```json
{
  "utm_source": "google",
  "utm_medium": "cpc",        // "cpc" for search/shopping, "display" for display, "video" for video
  "utm_campaign": "[campaign_name]",
  "utm_content": "[ad_group_name]",
  "utm_term": "[keyword]"     // Search campaigns only
}
```

Example final URL:
```
https://example.com/product?utm_source=google&utm_medium=cpc&utm_campaign=Summer_Sale&utm_content=Skincare_Ads&utm_term=best+moisturizer
```

## Query Patterns

### All Google Ads Campaigns for a Brand

```sql
SELECT * FROM g_campaigns
WHERE brand_id = $BRAND_ID
ORDER BY updated_at DESC;
```

### Campaign Performance Last 7 Days

```sql
SELECT
  campaign_id,
  campaign_name,
  SUM(impressions) as total_impressions,
  SUM(clicks) as total_clicks,
  SUM(cost) as total_cost,
  SUM(ar_conversions) as ar_conversions,
  AVG(ar_roas) as avg_ar_roas,
  AVG(ar_cpa) as avg_ar_cpa
FROM g_daily_metrics
WHERE brand_id = $BRAND_ID
  AND date >= CURRENT_DATE - 7
GROUP BY campaign_id, campaign_name
ORDER BY total_cost DESC;
```

### Keywords Below Quality Score Threshold

```sql
SELECT
  k.keyword_text,
  k.match_type,
  k.quality_score,
  ag.ad_group_name,
  SUM(m.cost) as cost_last_7d
FROM g_keywords k
JOIN g_ad_groups ag ON k.ad_group_id = ag.id
LEFT JOIN g_daily_metrics m ON ag.id = m.ad_group_id
  AND m.date >= CURRENT_DATE - 7
WHERE k.brand_id = $BRAND_ID
  AND k.status = 'ENABLED'
  AND k.quality_score < 5
GROUP BY k.id, k.keyword_text, k.match_type, k.quality_score, ag.ad_group_name
ORDER BY cost_last_7d DESC;
```

### Search Terms Not in Keyword List (High Spend, Low Conversion)

```sql
SELECT
  search_term,
  SUM(impressions) as impressions,
  SUM(clicks) as clicks,
  SUM(cost) as cost,
  COUNT(DISTINCT ga4_session_id) as ga4_sessions,
  CASE WHEN COUNT(DISTINCT ga4_session_id) > 0 THEN 'YES' ELSE 'NO' END as has_ga4
FROM search_term_report
WHERE brand_id = $BRAND_ID
  AND date >= CURRENT_DATE - 7
  AND search_term NOT IN (SELECT keyword_text FROM g_keywords WHERE brand_id = $BRAND_ID)
GROUP BY search_term
HAVING SUM(cost) > 50 AND COUNT(DISTINCT ga4_session_id) = 0
ORDER BY cost DESC;
```

## Key Differences: Google Ads vs Meta Ads

| Aspect | Google Ads | Meta Ads |
|--------|-----------|----------|
| **Targeting Unit** | Keywords (Search) or Audiences (Display) | Audience segments only |
| **Quality Metric** | Quality Score (1-10) | Ad Relevance Score (1-10) |
| **Learning Phase** | Ad group level | Ad set level |
| **Cost Model** | CPC (cost per click) + conversion tracking | CPC or CPM + conversion tracking |
| **Campaign Types** | Search, Display, Shopping, Video, PMAX | Feed, Stories, Reels, Ads, Collections |
| **Attribution Model** | Click-based (gclid), View-based | Last-click, 7-day/28-day windows |
| **Optimization Level** | Campaign → Ad Group → Keyword | Campaign → Ad Set → Ad |
| **Budget Control** | Daily budget caps | Daily budget caps |
| **Bid Strategies** | Target CPA, Target ROAS, Manual CPC | Bid caps, Cost caps, ROAS targets |

## Tracking: gclid vs fbclid

- **Google Ads:** Uses `gclid` (Google Click ID) parameter in final URLs
- **Meta Ads:** Uses `fbclid` (Facebook Click ID) parameter
- **GA4 Integration:** Both platforms map their click IDs to GA4 sessions automatically
- **Data & Placement Analyst:** Verifies gclid passing rate for Google campaigns, fbclid for Meta

## Performance Reconciliation

Always track three versions of each metric:

1. **Google Ads Reported** (highest, inflated 20-60%)
2. **GA4 True** (conservative, under-counts ~20%)
3. **AR (Assumed Real)** = GA4 True × 1.2 (best estimate)

Use AR for all strategic decisions. Use GA4 True for worst-case scenarios.

```
AR = GA4 × brand_config.ar_multiplier
```

The `ar_multiplier` is calibrated during brand setup based on historical CRM data, or defaults to 1.2 (assuming GA4 under-counts by ~20%).

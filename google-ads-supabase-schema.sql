-- ============================================================
-- GOOGLE ADS AGENT SYSTEM — SUPABASE SCHEMA EXTENSION
-- ============================================================
-- This schema EXTENDS the existing Meta Ads schema.
-- Run this AFTER meta-ads-supabase-schema.sql.
--
-- Adds Google Ads-specific tables while sharing:
--   - brand_config (extended with Google Ads fields)
--   - landing_pages (same pages serve both platforms)
--   - optimization_cycles (separate cycles, same table)
--   - agent_deliverables (separate deliverables, same table)
--   - alerts (separate alerts, same table)
--   - recommendations (separate recommendations, same table)
--   - ab_tests (separate tests, same table)
--   - campaign_changes (separate changes, same table)
--   - human_creative_inspiration (can feed both platforms)
--   - setup_log (separate setup phases for Google system)
--
-- MULTI-BRAND: Same brand_id scoping. A brand can have
-- Meta Ads + Google Ads running simultaneously.
-- ============================================================


-- ============================================================
-- 1. EXTEND BRAND CONFIG (add Google Ads fields)
-- ============================================================

ALTER TABLE brand_config
  ADD COLUMN IF NOT EXISTS google_ads_customer_id TEXT,              -- Google Ads CID (xxx-xxx-xxxx)
  ADD COLUMN IF NOT EXISTS google_ads_manager_id TEXT,               -- MCC account ID if under manager account
  ADD COLUMN IF NOT EXISTS google_ads_credentials_vault_ref TEXT,    -- Vault ref for OAuth2 refresh token
  ADD COLUMN IF NOT EXISTS google_ads_developer_token_vault_ref TEXT,-- Vault ref for API developer token
  ADD COLUMN IF NOT EXISTS google_merchant_center_id TEXT,           -- Merchant Center ID for Shopping campaigns
  ADD COLUMN IF NOT EXISTS youtube_channel_id TEXT,                  -- YouTube channel for Video campaigns
  ADD COLUMN IF NOT EXISTS google_conversion_action_ids JSONB DEFAULT '[]',  -- array of conversion action IDs to track
  ADD COLUMN IF NOT EXISTS google_ads_aspect_ratios JSONB DEFAULT '{"landscape": "1.91:1 (1200x628)", "square": "1:1 (1200x1200)", "portrait": "4:5 (960x1200)", "youtube_thumbnail": "16:9 (1280x720)"}',
  ADD COLUMN IF NOT EXISTS google_ads_enabled BOOLEAN DEFAULT false; -- whether Google Ads is active for this brand


-- ============================================================
-- 2. GOOGLE ADS CAMPAIGNS
-- ============================================================

CREATE TABLE g_campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_campaign_id TEXT NOT NULL,
  name TEXT NOT NULL,                         -- naming: [Type]_[Brand]_[Market]_[Strategy]_[Date]

  -- Campaign type
  campaign_type TEXT NOT NULL,                -- SEARCH, SHOPPING, DISPLAY, VIDEO, PERFORMANCE_MAX, DEMAND_GEN
  advertising_channel_sub_type TEXT,          -- SEARCH_MOBILE_APP, SHOPPING_SMART, VIDEO_ACTION, etc.

  -- Status
  status TEXT NOT NULL DEFAULT 'PAUSED',      -- PAUSED (draft equivalent), ENABLED, REMOVED
  serving_status TEXT,                        -- SERVING, ENDED, PENDING, SUSPENDED, etc.

  -- Budget
  daily_budget NUMERIC(12,2),
  shared_budget_id TEXT,                      -- if using shared budget
  spending_limit NUMERIC(12,2),

  -- Bidding
  bid_strategy TEXT,                          -- TARGET_CPA, TARGET_ROAS, MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, MANUAL_CPC, MANUAL_CPV, TARGET_IMPRESSION_SHARE
  bid_strategy_rationale TEXT,
  target_cpa NUMERIC(12,2),                   -- for TARGET_CPA strategy
  target_roas NUMERIC(6,2),                   -- for TARGET_ROAS strategy (e.g., 3.0 = 300%)
  target_impression_share_location TEXT,       -- ANYWHERE_ON_PAGE, TOP_OF_PAGE, ABSOLUTE_TOP_OF_PAGE
  target_impression_share_pct NUMERIC(5,2),

  -- Targets (campaign-level overrides)
  target_ar_cpa NUMERIC(12,2),
  target_ar_roas NUMERIC(6,2),

  -- Networks
  search_network BOOLEAN DEFAULT true,
  display_network BOOLEAN DEFAULT false,
  search_partners BOOLEAN DEFAULT false,

  -- Geo & schedule
  geo_targeting JSONB,                        -- { countries: [], regions: [], cities: [], radius: [] }
  ad_schedule JSONB,                          -- dayparting schedule: [{ day: "MONDAY", start: "08:00", end: "22:00", bid_modifier: 1.0 }]
  language_targeting TEXT[] DEFAULT '{en}',

  -- Special categories
  special_ad_category TEXT DEFAULT 'NONE',

  -- Lifecycle
  start_date DATE,
  end_date DATE,
  scheduled_launch_at TIMESTAMPTZ,
  launched_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,
  pause_reason TEXT,
  removed_at TIMESTAMPTZ,
  removal_reason TEXT,
  post_mortem TEXT,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  UNIQUE(brand_id, google_campaign_id)
);


-- ============================================================
-- 3. GOOGLE ADS AD GROUPS (replaces Meta's ad_sets)
-- ============================================================

CREATE TABLE g_ad_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_ad_group_id TEXT NOT NULL,
  campaign_id UUID NOT NULL REFERENCES g_campaigns(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                         -- naming: [Theme]_[MatchType]_[Segment]_[Date]
  status TEXT NOT NULL DEFAULT 'ENABLED',     -- ENABLED, PAUSED, REMOVED

  -- Ad group type
  ad_group_type TEXT DEFAULT 'SEARCH_STANDARD', -- SEARCH_STANDARD, DISPLAY_STANDARD, SHOPPING_PRODUCT_ADS, VIDEO_TRUE_VIEW_IN_STREAM, etc.

  -- Bidding
  cpc_bid NUMERIC(12,2),                      -- max CPC bid (manual)
  cpm_bid NUMERIC(12,2),                      -- max CPM bid (display/video)
  cpv_bid NUMERIC(12,2),                      -- max CPV bid (video)
  bid_modifier_device_mobile NUMERIC(5,2),
  bid_modifier_device_tablet NUMERIC(5,2),

  -- Targeting
  audience_targeting JSONB,                   -- audience segments, remarketing lists
  content_targeting JSONB,                    -- topics, placements, keywords (display)
  exclusions JSONB DEFAULT '[]',

  -- Shopping-specific
  product_group_config JSONB,                 -- product group hierarchy for Shopping

  -- Smart bidding ramp-up (Google's version of learning phase)
  ramp_up_start TIMESTAMPTZ,
  ramp_up_status TEXT DEFAULT 'NOT_STARTED',  -- NOT_STARTED, RAMPING, STABLE, LIMITED

  -- Lifecycle
  created_at TIMESTAMPTZ DEFAULT now(),
  paused_at TIMESTAMPTZ,
  pause_reason TEXT,
  ar_cpa_at_pause NUMERIC(12,2),
  total_spend_at_pause NUMERIC(12,2),

  UNIQUE(brand_id, google_ad_group_id)
);


-- ============================================================
-- 4. GOOGLE ADS ADS
-- ============================================================

CREATE TABLE g_ads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_ad_id TEXT NOT NULL,
  ad_group_id UUID NOT NULL REFERENCES g_ad_groups(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'PAUSED',       -- ENABLED, PAUSED, REMOVED

  -- Ad type
  ad_type TEXT NOT NULL,                       -- RESPONSIVE_SEARCH, RESPONSIVE_DISPLAY, VIDEO, SHOPPING_PRODUCT, PERFORMANCE_MAX_ASSET, DEMAND_GEN, CALL_AD, APP_AD

  -- Responsive Search Ad assets
  rsa_headlines JSONB DEFAULT '[]',            -- array of { text, pinned_position, performance_label }
  rsa_descriptions JSONB DEFAULT '[]',         -- array of { text, pinned_position, performance_label }
  rsa_path1 TEXT,                              -- display URL path 1
  rsa_path2 TEXT,                              -- display URL path 2

  -- Responsive Display Ad assets
  rda_headlines JSONB DEFAULT '[]',            -- short headlines (25 chars)
  rda_long_headline TEXT,                      -- long headline (90 chars)
  rda_descriptions JSONB DEFAULT '[]',
  rda_images JSONB DEFAULT '[]',               -- { url, aspect_ratio }
  rda_logos JSONB DEFAULT '[]',
  rda_business_name TEXT,

  -- Video Ad assets
  video_id TEXT,                               -- YouTube video ID
  video_duration_seconds INTEGER,
  video_format TEXT,                           -- IN_STREAM_SKIPPABLE, IN_STREAM_NON_SKIPPABLE, BUMPER, IN_FEED, SHORTS
  video_companion_banner_url TEXT,
  video_thumbnail_url TEXT,

  -- Shopping Ad (auto-generated from feed)
  product_id TEXT,                             -- Merchant Center product ID
  product_title TEXT,
  product_category TEXT,

  -- Performance Max asset group link
  asset_group_id UUID REFERENCES g_asset_groups(id),

  -- Destination
  final_url TEXT,
  final_mobile_url TEXT,
  landing_page_id UUID REFERENCES landing_pages(id),

  -- UTMs
  utm_source TEXT DEFAULT 'google',
  utm_medium TEXT,                             -- cpc, display, video, shopping
  utm_campaign TEXT,
  utm_content TEXT,
  utm_term TEXT,

  -- Creative linkage
  creative_registry_id UUID REFERENCES creative_registry(id),
  creative_mode TEXT,                          -- A, B, B-H

  -- Ad Strength (Google's creative quality signal)
  ad_strength TEXT,                            -- POOR, AVERAGE, GOOD, EXCELLENT, UNSPECIFIED
  ad_strength_reasons JSONB DEFAULT '[]',      -- why it's that rating

  -- Health
  fatigue_score NUMERIC(5,2) DEFAULT 0,
  fatigue_threshold NUMERIC(5,2),
  days_active INTEGER DEFAULT 0,
  peak_ar_roas NUMERIC(6,2),
  peak_ar_roas_date DATE,

  -- Lifecycle
  created_at TIMESTAMPTZ DEFAULT now(),
  launched_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,
  pause_reason TEXT,

  UNIQUE(brand_id, google_ad_id)
);


-- ============================================================
-- 5. KEYWORDS (Search campaigns — no Meta equivalent)
-- ============================================================

CREATE TABLE g_keywords (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_criterion_id TEXT NOT NULL,
  ad_group_id UUID NOT NULL REFERENCES g_ad_groups(id) ON DELETE CASCADE,

  -- Keyword details
  keyword_text TEXT NOT NULL,
  match_type TEXT NOT NULL,                    -- BROAD, PHRASE, EXACT, NEGATIVE
  status TEXT NOT NULL DEFAULT 'ENABLED',      -- ENABLED, PAUSED, REMOVED

  -- Bidding
  cpc_bid_override NUMERIC(12,2),             -- keyword-level CPC override

  -- Quality Score (1-10, components 1-3: BELOW_AVERAGE, AVERAGE, ABOVE_AVERAGE)
  quality_score INTEGER,
  quality_score_expected_ctr TEXT,              -- BELOW_AVERAGE, AVERAGE, ABOVE_AVERAGE
  quality_score_ad_relevance TEXT,
  quality_score_landing_page TEXT,
  quality_score_history JSONB DEFAULT '[]',     -- [{ date, score, components }]

  -- Performance signals
  search_impression_share NUMERIC(5,2),        -- % of eligible impressions received
  search_top_impression_pct NUMERIC(5,2),      -- % appearing above organic
  search_abs_top_impression_pct NUMERIC(5,2),  -- % appearing in absolute top position
  impression_share_lost_budget NUMERIC(5,2),   -- % lost due to budget
  impression_share_lost_rank NUMERIC(5,2),     -- % lost due to ad rank

  -- Classification (same framework as Meta)
  classification TEXT,                          -- WINNER, LOSER, INCONCLUSIVE, HIDDEN_GEM
  confidence_pct NUMERIC(5,2),
  total_spend NUMERIC(12,2),
  total_ar_conversions NUMERIC(12,2),
  current_ar_cpa NUMERIC(12,2),
  current_ar_roas NUMERIC(6,2),

  -- Lifecycle
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  UNIQUE(brand_id, google_criterion_id)
);


-- ============================================================
-- 6. SEARCH TERMS (actual queries triggering ads)
-- ============================================================

CREATE TABLE g_search_terms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  date DATE NOT NULL,

  -- Linkage
  campaign_id UUID REFERENCES g_campaigns(id),
  ad_group_id UUID REFERENCES g_ad_groups(id),
  keyword_id UUID REFERENCES g_keywords(id),

  -- Search term details
  search_term TEXT NOT NULL,
  match_type_triggered TEXT,                   -- which match type triggered this

  -- Metrics
  impressions INTEGER,
  clicks INTEGER,
  spend NUMERIC(12,2),
  conversions NUMERIC(12,2),
  conversion_value NUMERIC(12,2),
  ctr NUMERIC(8,4),
  avg_cpc NUMERIC(12,2),

  -- AR metrics
  ar_conversions NUMERIC(12,2),
  ar_revenue NUMERIC(12,2),
  ar_cpa NUMERIC(12,2),
  ar_roas NUMERIC(6,2),

  -- Action taken
  action TEXT,                                 -- NONE, ADDED_AS_KEYWORD, ADDED_AS_NEGATIVE, MONITORED
  action_taken_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 7. PRODUCT GROUPS (Shopping campaigns)
-- ============================================================

CREATE TABLE g_product_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_criterion_id TEXT,
  campaign_id UUID NOT NULL REFERENCES g_campaigns(id) ON DELETE CASCADE,
  ad_group_id UUID REFERENCES g_ad_groups(id),

  -- Product group hierarchy
  partition_type TEXT,                          -- SUBDIVISION, UNIT
  dimension_type TEXT,                          -- CATEGORY, BRAND, ITEM_ID, PRODUCT_TYPE, CUSTOM_ATTRIBUTE, CONDITION, CHANNEL
  dimension_value TEXT,
  parent_id UUID REFERENCES g_product_groups(id),

  -- Bidding
  cpc_bid NUMERIC(12,2),

  -- Performance
  current_ar_cpa NUMERIC(12,2),
  current_ar_roas NUMERIC(6,2),
  total_spend NUMERIC(12,2),
  total_ar_conversions NUMERIC(12,2),
  classification TEXT,                          -- WINNER, LOSER, INCONCLUSIVE

  status TEXT DEFAULT 'ENABLED',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 8. ASSET GROUPS (Performance Max campaigns)
-- ============================================================

CREATE TABLE g_asset_groups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_asset_group_id TEXT,
  campaign_id UUID NOT NULL REFERENCES g_campaigns(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  status TEXT DEFAULT 'ENABLED',

  -- Assets (Performance Max bundles all creative into asset groups)
  headlines JSONB DEFAULT '[]',                -- array of text (up to 15)
  long_headlines JSONB DEFAULT '[]',           -- array of text (up to 5)
  descriptions JSONB DEFAULT '[]',             -- array of text (up to 5)
  images JSONB DEFAULT '[]',                   -- array of { url, aspect_ratio }
  logos JSONB DEFAULT '[]',
  youtube_videos JSONB DEFAULT '[]',           -- array of YouTube video IDs
  business_name TEXT,
  final_url TEXT,
  mobile_url TEXT,

  -- Listing group (product targeting for Shopping in PMax)
  listing_group_config JSONB,

  -- Audience signals
  audience_signals JSONB,                      -- { custom_segments: [], in_market: [], affinity: [], demographics: {}, your_data: [] }

  -- Performance
  ad_strength TEXT,                            -- POOR, AVERAGE, GOOD, EXCELLENT
  current_ar_cpa NUMERIC(12,2),
  current_ar_roas NUMERIC(6,2),
  total_spend NUMERIC(12,2),

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 9. GOOGLE ADS AUDIENCES
-- ============================================================

CREATE TABLE g_audiences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_audience_id TEXT,
  name TEXT NOT NULL,

  -- Audience type
  audience_type TEXT NOT NULL,                  -- REMARKETING, CUSTOMER_MATCH, IN_MARKET, AFFINITY, CUSTOM_INTENT, CUSTOM_SEGMENT, SIMILAR, COMBINED, DETAILED_DEMOGRAPHICS

  -- Configuration
  targeting_config JSONB NOT NULL,
  exclusions JSONB DEFAULT '[]',
  membership_duration_days INTEGER,            -- how long users stay in the list
  estimated_size BIGINT,

  -- Customer Match specifics
  customer_match_source TEXT,                  -- EMAIL, PHONE, ADDRESS, CRM_ID
  customer_match_upload_date TIMESTAMPTZ,

  -- Remarketing specifics
  remarketing_source TEXT,                     -- WEBSITE, APP, YOUTUBE, CUSTOMER_LIST
  remarketing_duration_days INTEGER,

  -- Geographic
  geo_targeting JSONB,

  -- Classification
  temperature TEXT CHECK (temperature IN ('COLD', 'WARM', 'HOT')),
  segment_detail TEXT,

  -- Performance
  current_ar_cpa NUMERIC(12,2),
  current_ar_roas NUMERIC(6,2),
  classification TEXT,
  confidence_pct NUMERIC(5,2),
  total_spend NUMERIC(12,2),
  total_ar_conversions NUMERIC(12,2),

  -- Assignment
  campaign_id UUID REFERENCES g_campaigns(id),
  ad_group_id UUID REFERENCES g_ad_groups(id),

  status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ARCHIVED', 'DEPRECATED')),
  archived_at TIMESTAMPTZ,
  archive_reason TEXT,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 10. AD EXTENSIONS
-- ============================================================

CREATE TABLE g_extensions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  google_extension_id TEXT,

  -- Extension type
  extension_type TEXT NOT NULL,                -- SITELINK, CALLOUT, STRUCTURED_SNIPPET, CALL, PRICE, PROMOTION, LOCATION, APP, LEAD_FORM, IMAGE

  -- Level (account, campaign, or ad group)
  level TEXT NOT NULL DEFAULT 'CAMPAIGN',       -- ACCOUNT, CAMPAIGN, AD_GROUP
  campaign_id UUID REFERENCES g_campaigns(id),
  ad_group_id UUID REFERENCES g_ad_groups(id),

  -- Extension content (varies by type, stored as JSONB)
  extension_config JSONB NOT NULL,             -- type-specific content
  -- SITELINK: { link_text, url, description1, description2 }
  -- CALLOUT: { callout_text }
  -- STRUCTURED_SNIPPET: { header, values: [] }
  -- CALL: { phone_number, country_code }
  -- PRICE: { price_qualifier, items: [{ header, description, price, unit, url }] }
  -- PROMOTION: { promotion_target, percent_off, money_off, orders_over, promotion_code, occasion }
  -- LOCATION: { business_name, address }
  -- IMAGE: { image_url, aspect_ratio }

  -- Scheduling
  start_date DATE,
  end_date DATE,
  ad_schedule JSONB,                           -- when to show this extension

  -- Performance
  clicks INTEGER DEFAULT 0,
  impressions INTEGER DEFAULT 0,
  ctr NUMERIC(8,4),

  status TEXT DEFAULT 'ENABLED',               -- ENABLED, PAUSED, REMOVED
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 11. GOOGLE ADS DAILY METRICS (triple-source: Google Ads, GA4 True, AR)
-- ============================================================
-- Separate from Meta's daily_metrics to keep schemas clean.
-- Same triple-source pattern but with Google Ads-specific fields.

CREATE TABLE g_daily_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  timezone TEXT,

  -- Entity linkage (exactly one populated per row)
  campaign_id UUID REFERENCES g_campaigns(id),
  ad_group_id UUID REFERENCES g_ad_groups(id),
  ad_id UUID REFERENCES g_ads(id),
  keyword_id UUID REFERENCES g_keywords(id),
  level TEXT NOT NULL CHECK (level IN ('campaign', 'ad_group', 'ad', 'keyword')),

  -- Breakdown
  breakdown_dimension TEXT,                    -- NULL, 'age', 'gender', 'geo_region', 'device', 'network', 'day_of_week', 'hour', 'placement', 'product_group', 'audience_segment', 'search_term_category'
  breakdown_value TEXT,

  -- GOOGLE ADS REPORTED (self-reported, may over-count)
  google_impressions BIGINT,
  google_clicks BIGINT,
  google_spend NUMERIC(12,2),
  google_conversions NUMERIC(12,2),             -- fractional (Google reports fractional conversions)
  google_conversion_value NUMERIC(12,2),
  google_cpa NUMERIC(12,2),
  google_roas NUMERIC(6,2),
  google_cpm NUMERIC(12,2),
  google_cpc NUMERIC(12,2),
  google_ctr NUMERIC(8,4),
  google_interaction_rate NUMERIC(8,4),

  -- Google Ads unique signals
  google_impression_share NUMERIC(5,2),
  google_search_impression_share NUMERIC(5,2),
  google_top_impression_pct NUMERIC(5,2),
  google_abs_top_impression_pct NUMERIC(5,2),
  google_impression_share_lost_budget NUMERIC(5,2),
  google_impression_share_lost_rank NUMERIC(5,2),
  google_quality_score_avg NUMERIC(4,2),

  -- Video metrics (YouTube)
  google_video_views BIGINT,
  google_video_view_rate NUMERIC(8,4),
  google_video_quartile_25_pct NUMERIC(5,2),
  google_video_quartile_50_pct NUMERIC(5,2),
  google_video_quartile_75_pct NUMERIC(5,2),
  google_video_quartile_100_pct NUMERIC(5,2),

  -- GA4 TRUE (under-counts ~20%)
  ga4_sessions INTEGER,
  ga4_conversions INTEGER,
  ga4_revenue NUMERIC(12,2),
  ga4_bounce_rate NUMERIC(5,2),
  ga4_avg_session_duration NUMERIC(8,2),
  true_cpa NUMERIC(12,2),                      -- google_spend / ga4_conversions
  true_roas NUMERIC(6,2),                      -- ga4_revenue / google_spend

  -- AR — ASSUMED REAL (GA4 x ar_multiplier, THE DECISION METRIC)
  ar_multiplier NUMERIC(4,2) DEFAULT 1.20,
  ar_conversions NUMERIC(12,2),
  ar_revenue NUMERIC(12,2),
  ar_cpa NUMERIC(12,2),
  ar_roas NUMERIC(6,2),

  -- TRACKING HEALTH
  click_to_session_rate NUMERIC(6,2),
  google_ga4_discrepancy NUMERIC(6,2),

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT now(),

  UNIQUE(brand_id, date, campaign_id, ad_group_id, ad_id, keyword_id, level, breakdown_dimension, breakdown_value)
);


-- ============================================================
-- 12. GOOGLE ADS TRACKING HEALTH
-- ============================================================

CREATE TABLE g_tracking_health (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  campaign_id UUID REFERENCES g_campaigns(id),

  -- Health metrics
  click_to_session_rate NUMERIC(6,2),
  google_ga4_discrepancy NUMERIC(6,2),
  utm_integrity BOOLEAN,
  gclid_passthrough BOOLEAN,                   -- Google Click ID (replaces fbclid)
  conversion_tracking_status TEXT CHECK (conversion_tracking_status IN ('HEALTHY', 'WARNING', 'ERROR', 'DOWN')),
  conversion_tag_status TEXT,                  -- ACTIVE, UNVERIFIED, NO_RECENT_CONVERSIONS

  -- Overall verdict
  health_status TEXT NOT NULL CHECK (health_status IN ('HEALTHY', 'DEGRADED', 'BROKEN')),
  issues TEXT[],

  created_at TIMESTAMPTZ DEFAULT now(),

  UNIQUE(brand_id, date, campaign_id)
);


-- ============================================================
-- 13. GOOGLE ADS CANNIBALIZATION (keyword overlap + campaign overlap)
-- ============================================================

CREATE TABLE g_cannibalization_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),
  date DATE NOT NULL,

  -- Pair type
  pair_type TEXT NOT NULL CHECK (pair_type IN ('campaign', 'ad_group', 'keyword')),
  entity_a_id UUID NOT NULL,
  entity_b_id UUID NOT NULL,

  -- Score components (0-100 each)
  keyword_overlap_pct NUMERIC(5,2),            -- % of shared search terms
  auction_overlap_pct NUMERIC(5,2),            -- % of auctions competing against each other
  shared_converter_pct NUMERIC(5,2),
  cpc_inflation_pct NUMERIC(5,2),              -- CPC instead of CPM
  budget_ratio_imbalance NUMERIC(5,2),
  performance_delta NUMERIC(5,2),

  -- Composite
  cannibal_score NUMERIC(5,2),
  severity TEXT GENERATED ALWAYS AS (
    CASE
      WHEN cannibal_score >= 81 THEN 'CRITICAL'
      WHEN cannibal_score >= 61 THEN 'URGENT'
      WHEN cannibal_score >= 41 THEN 'ACT'
      WHEN cannibal_score >= 21 THEN 'MONITOR'
      ELSE 'MINIMAL'
    END
  ) STORED,

  -- Dollar impact
  overlap_cost_weekly NUMERIC(12,2),

  -- Resolution
  recommended_action TEXT,
  action_status TEXT DEFAULT 'PENDING',

  created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 14. GOOGLE ADS COMPETITOR DATA
-- ============================================================
-- Sourced from Google Ads Transparency Center + Auction Insights

CREATE TABLE g_competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  advertiser_name TEXT NOT NULL,
  transparency_center_url TEXT,
  domain TEXT,

  -- Auction Insights data (from Data Analyst)
  impression_share NUMERIC(5,2),
  overlap_rate NUMERIC(5,2),
  outranking_share NUMERIC(5,2),
  position_above_rate NUMERIC(5,2),
  top_of_page_rate NUMERIC(5,2),
  abs_top_of_page_rate NUMERIC(5,2),

  -- Transparency Center data (from Competitive Intel)
  active_ads_count INTEGER DEFAULT 0,
  ad_formats TEXT[] DEFAULT '{}',              -- TEXT, IMAGE, VIDEO
  regions TEXT[] DEFAULT '{}',                 -- where they advertise
  topics TEXT[] DEFAULT '{}',

  -- Scoring
  threat_level TEXT DEFAULT 'LOW',
  overall_longevity_score NUMERIC(5,2),

  status TEXT DEFAULT 'MONITORING',
  last_checked TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  notes TEXT
);

CREATE TABLE g_competitor_ads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competitor_id UUID NOT NULL REFERENCES g_competitors(id) ON DELETE CASCADE,
  transparency_center_ad_id TEXT,

  -- Ad details
  format TEXT,                                 -- TEXT, IMAGE, VIDEO, SHOPPING
  headline TEXT,
  description TEXT,
  display_url TEXT,
  visual_description TEXT,
  landing_page_url TEXT,

  -- Duration & scoring
  first_seen DATE,
  last_seen DATE,
  days_active INTEGER GENERATED ALWAYS AS (last_seen - first_seen) STORED,
  longevity_score NUMERIC(5,2),
  multi_format BOOLEAN DEFAULT false,

  -- Relevance
  relevance TEXT DEFAULT 'LOW',
  mode_b_candidate BOOLEAN DEFAULT false,
  mode_b_notes TEXT,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- INDEXES
-- ============================================================

-- Brand indexes
CREATE INDEX idx_g_campaigns_brand ON g_campaigns(brand_id);
CREATE INDEX idx_g_ad_groups_brand ON g_ad_groups(brand_id);
CREATE INDEX idx_g_ads_brand ON g_ads(brand_id);
CREATE INDEX idx_g_keywords_brand ON g_keywords(brand_id);
CREATE INDEX idx_g_search_terms_brand ON g_search_terms(brand_id);
CREATE INDEX idx_g_product_groups_brand ON g_product_groups(brand_id);
CREATE INDEX idx_g_asset_groups_brand ON g_asset_groups(brand_id);
CREATE INDEX idx_g_audiences_brand ON g_audiences(brand_id);
CREATE INDEX idx_g_extensions_brand ON g_extensions(brand_id);
CREATE INDEX idx_g_dm_brand ON g_daily_metrics(brand_id);
CREATE INDEX idx_g_th_brand ON g_tracking_health(brand_id);
CREATE INDEX idx_g_cannibal_brand ON g_cannibalization_scores(brand_id);
CREATE INDEX idx_g_competitors_brand ON g_competitors(brand_id);

-- Daily metrics (most queried)
CREATE INDEX idx_g_dm_brand_date ON g_daily_metrics(brand_id, date);
CREATE INDEX idx_g_dm_campaign_date ON g_daily_metrics(campaign_id, date) WHERE level = 'campaign';
CREATE INDEX idx_g_dm_ag_date ON g_daily_metrics(ad_group_id, date) WHERE level = 'ad_group';
CREATE INDEX idx_g_dm_ad_date ON g_daily_metrics(ad_id, date) WHERE level = 'ad';
CREATE INDEX idx_g_dm_keyword_date ON g_daily_metrics(keyword_id, date) WHERE level = 'keyword';
CREATE INDEX idx_g_dm_level_date ON g_daily_metrics(level, date);
CREATE INDEX idx_g_dm_breakdown ON g_daily_metrics(breakdown_dimension, breakdown_value, date);

-- Keywords
CREATE INDEX idx_g_keywords_ad_group ON g_keywords(ad_group_id);
CREATE INDEX idx_g_keywords_quality ON g_keywords(quality_score) WHERE quality_score IS NOT NULL;
CREATE INDEX idx_g_keywords_status ON g_keywords(status) WHERE status = 'ENABLED';
CREATE INDEX idx_g_keywords_classification ON g_keywords(classification);

-- Search terms
CREATE INDEX idx_g_search_terms_date ON g_search_terms(brand_id, date);
CREATE INDEX idx_g_search_terms_action ON g_search_terms(action) WHERE action = 'NONE';
CREATE INDEX idx_g_search_terms_keyword ON g_search_terms(keyword_id);

-- Product groups
CREATE INDEX idx_g_product_groups_campaign ON g_product_groups(campaign_id);

-- Asset groups
CREATE INDEX idx_g_asset_groups_campaign ON g_asset_groups(campaign_id);

-- Competitors
CREATE INDEX idx_g_comp_ads_competitor ON g_competitor_ads(competitor_id);
CREATE INDEX idx_g_comp_ads_mode_b ON g_competitor_ads(mode_b_candidate) WHERE mode_b_candidate = true;

-- Tracking health
CREATE INDEX idx_g_th_date_campaign ON g_tracking_health(date, campaign_id);


-- ============================================================
-- VIEWS
-- ============================================================

-- Google Ads campaign health dashboard
CREATE VIEW v_google_campaign_health AS
SELECT DISTINCT ON (c.id)
  c.id,
  c.brand_id,
  c.google_campaign_id,
  c.name,
  c.campaign_type,
  c.status,
  c.target_ar_cpa,
  c.target_ar_roas,
  c.daily_budget,
  c.bid_strategy,
  dm.date,
  dm.google_spend,
  dm.ar_cpa,
  dm.ar_roas,
  dm.ar_conversions,
  dm.google_impression_share,
  dm.google_search_impression_share,
  dm.click_to_session_rate,
  dm.google_ga4_discrepancy,
  th.health_status AS tracking_health,
  CASE
    WHEN dm.ar_cpa IS NULL THEN 'NO_DATA'
    WHEN c.target_ar_cpa IS NOT NULL AND dm.ar_cpa > c.target_ar_cpa * 3 THEN 'CRITICAL'
    WHEN c.target_ar_cpa IS NOT NULL AND dm.ar_cpa > c.target_ar_cpa * 2 THEN 'DECLINING'
    WHEN c.target_ar_cpa IS NOT NULL AND dm.ar_cpa > c.target_ar_cpa * 1.3 THEN 'WATCH'
    ELSE 'HEALTHY'
  END AS health_score
FROM g_campaigns c
LEFT JOIN g_daily_metrics dm ON dm.campaign_id = c.id
  AND dm.level = 'campaign'
  AND dm.breakdown_dimension IS NULL
LEFT JOIN g_tracking_health th ON th.campaign_id = c.id AND th.date = dm.date
WHERE c.status = 'ENABLED'
ORDER BY c.id, dm.date DESC;


-- Keyword health dashboard
CREATE VIEW v_google_keyword_health AS
SELECT
  k.id,
  k.brand_id,
  k.keyword_text,
  k.match_type,
  k.status,
  k.quality_score,
  k.quality_score_expected_ctr,
  k.quality_score_ad_relevance,
  k.quality_score_landing_page,
  k.search_impression_share,
  k.impression_share_lost_budget,
  k.impression_share_lost_rank,
  k.classification,
  k.current_ar_cpa,
  k.current_ar_roas,
  k.total_spend,
  k.total_ar_conversions,
  ag.name AS ad_group_name,
  c.name AS campaign_name,
  c.campaign_type
FROM g_keywords k
JOIN g_ad_groups ag ON k.ad_group_id = ag.id
JOIN g_campaigns c ON ag.campaign_id = c.id
WHERE k.status = 'ENABLED';


-- Search terms needing action
CREATE VIEW v_google_search_terms_review AS
SELECT
  st.*,
  k.keyword_text AS triggering_keyword,
  k.match_type AS keyword_match_type,
  ag.name AS ad_group_name,
  c.name AS campaign_name,
  CASE
    WHEN st.ar_roas > 0 AND st.conversions >= 2 THEN 'ADD_AS_KEYWORD'
    WHEN st.spend > 50 AND st.conversions = 0 THEN 'ADD_AS_NEGATIVE'
    WHEN st.clicks > 20 AND st.conversions = 0 THEN 'REVIEW'
    ELSE 'MONITOR'
  END AS suggested_action
FROM g_search_terms st
LEFT JOIN g_keywords k ON st.keyword_id = k.id
LEFT JOIN g_ad_groups ag ON st.ad_group_id = ag.id
LEFT JOIN g_campaigns c ON st.campaign_id = c.id
WHERE st.action = 'NONE'
  AND st.date >= CURRENT_DATE - INTERVAL '30 days';


-- Performance Max asset group performance
CREATE VIEW v_google_pmax_performance AS
SELECT
  asg.id,
  asg.brand_id,
  asg.name AS asset_group_name,
  asg.ad_strength,
  c.name AS campaign_name,
  c.daily_budget,
  dm.date,
  dm.google_spend,
  dm.ar_cpa,
  dm.ar_roas,
  dm.ar_conversions,
  dm.google_conversions
FROM g_asset_groups asg
JOIN g_campaigns c ON asg.campaign_id = c.id
LEFT JOIN g_daily_metrics dm ON dm.campaign_id = c.id
  AND dm.level = 'campaign'
  AND dm.breakdown_dimension IS NULL
WHERE c.campaign_type = 'PERFORMANCE_MAX'
  AND asg.status = 'ENABLED';


-- ============================================================
-- RUNNER QUERY (Machine B — Google Ads agents)
-- ============================================================
-- Same pattern as Meta. Runner picks next PENDING task for a brand.
-- Agent mapping:
--   'g_data_placement'    -> google-ads-data-placement-analyst
--   'g_creative_analyst'  -> google-ads-creative-analyst
--   'g_post_click'        -> google-ads-postclick-analyst
--   'g_competitive_intel' -> google-ads-competitive-intel
--   'g_creative_producer' -> google-ads-creative-producer
--   'g_campaign_creator'  -> google-ads-campaign-creator
--   'g_campaign_monitor'  -> google-ads-campaign-monitor
--
-- UPDATE agent_deliverables
-- SET status = 'IN_PROGRESS', runner_picked_at = now(), started_at = now(), runner_machine = 'machine_b'
-- WHERE id = (
--   SELECT id FROM agent_deliverables
--   WHERE status = 'PENDING'
--     AND brand_id = $brand_id
--     AND agent_name LIKE 'g_%'
--   ORDER BY execution_priority ASC, requested_at ASC
--   LIMIT 1
--   FOR UPDATE SKIP LOCKED
-- )
-- RETURNING *;


-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

ALTER TABLE g_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_ad_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_ads ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_search_terms ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_product_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_asset_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_audiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_extensions ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_tracking_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_cannibalization_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE g_competitor_ads ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_full_access" ON g_campaigns FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_ad_groups FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_ads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_keywords FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_search_terms FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_product_groups FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_asset_groups FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_audiences FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_extensions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_daily_metrics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_tracking_health FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_cannibalization_scores FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_competitors FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON g_competitor_ads FOR ALL USING (true) WITH CHECK (true);

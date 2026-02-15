# Supabase Schema Reference

This document contains the complete database schema that must be applied during Phase 1 (Supabase Setup) of the meta-ads-setup skill.

## How to Apply This Schema

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor
3. Create a new query
4. Copy the entire SQL code below
5. Click RUN

The schema will create 18 tables, 6 views, and all necessary indexes for the Meta Ads AI Agent System.

---

## Complete Schema SQL

```sql
-- ============================================================
-- META ADS AGENT SYSTEM — SUPABASE SCHEMA
-- ============================================================
-- This schema is the shared data layer for all 8 agents.
-- Every agent reads from and writes to specific tables.
-- The Orchestrator has read access to everything.
--
-- MULTI-BRAND: Every brand-specific table includes brand_id
-- referencing brand_config(id). Agents receive brand_id at
-- invocation and filter ALL queries by it. One Supabase database
-- serves all brands. Each brand has its own Meta ad account,
-- GA4 property, API credentials, targets, and creative assets.
--
-- SETUP: Run this SQL in Supabase SQL Editor after creating your project.
-- Then add your Supabase URL + anon key to each agent's config.
-- ============================================================


-- ============================================================
-- 1. BRAND CONFIG (one row per brand, populated during onboarding)
-- ============================================================

CREATE TABLE brand_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_name TEXT NOT NULL,
  product_description TEXT,                 -- one-sentence product description for AI prompts
  website_url TEXT,                         -- main website URL

  -- Visual identity
  locked_elements JSONB DEFAULT '[]',       -- product images, logo, compliance text that must never be altered
  hero_variants JSONB DEFAULT '[]',         -- product shots, lifestyle images with prompt descriptions
  color_palette JSONB DEFAULT '{}',         -- { primary: "#hex", secondary: "#hex", accent: "#hex", background: "#hex" }
  aspect_ratios JSONB DEFAULT '{"feed": "1:1 (1080x1080)", "stories_reels": "9:16 (1080x1920)", "link_ads": "1.91:1 (1200x628)"}',

  -- Copy
  text_angles JSONB DEFAULT '[]',           -- selling points, offers, urgency phrases
  banned_words TEXT[] DEFAULT '{}',         -- competitor names, regulated terms, brand-inappropriate language

  -- Targets
  target_ar_cpa NUMERIC(12,2),              -- goal CPA we optimize toward
  target_ar_roas NUMERIC(6,2),              -- goal ROAS we optimize toward
  min_acceptable_ar_roas NUMERIC(6,2),      -- floor ROAS: campaigns below this get paused/killed
  daily_budget NUMERIC(12,2),
  monthly_budget NUMERIC(12,2),

  -- Creative volume
  weekly_ad_volume INTEGER DEFAULT 3,        -- how many new ad creatives to produce per week per brand

  -- Scaling config (auto-scaling proposals — human still approves)
  scaling_config JSONB DEFAULT '{
    "enabled": true,
    "scale_step_pct": 20,
    "min_ar_roas_to_scale": 1.5,
    "min_days_at_budget_cap": 3,
    "cooldown_days_after_scale": 2,
    "max_daily_budget": null
  }',

  -- AR calibration
  ar_multiplier NUMERIC(4,2) DEFAULT 1.20,
  ar_multiplier_calibrated_at TIMESTAMPTZ,
  ar_multiplier_source TEXT DEFAULT 'default',  -- 'default' or 'crm_calibrated'
  ar_multiplier_history JSONB DEFAULT '[]',     -- array of { date, old_value, new_value, crm_conversions, ga4_conversions }

  -- Per-brand API credentials
  -- Store actual secrets in Supabase Vault. These fields hold Vault references.
  meta_ad_account_id TEXT,                       -- Meta ad account ID (act_XXXXXXXXX)
  meta_access_token_vault_ref TEXT,              -- Vault reference for this brand's Meta API access token
  ga4_property_id TEXT,                          -- GA4 property ID (properties/XXXXXXXXX)
  ga4_credentials_vault_ref TEXT,                -- Vault reference for this brand's GA4 service account JSON key

  -- Compliance & market
  special_ad_category TEXT DEFAULT 'NONE',  -- NONE, CREDIT, HOUSING, EMPLOYMENT, POLITICAL
  market_vertical TEXT,                     -- e.g., "organic skincare", "DTC supplements"
  pixel_status TEXT DEFAULT 'unknown',      -- installed, partial, not_installed, unknown

  -- Timezone & currency
  timezone TEXT DEFAULT 'America/New_York',         -- IANA timezone (must match Meta ad account timezone)
  currency TEXT DEFAULT 'USD',                       -- ISO 4217 currency code (must match Meta ad account currency)

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 2. CAMPAIGNS / AD SETS / ADS (core campaign structure)
-- ============================================================

CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  meta_campaign_id TEXT NOT NULL,
  name TEXT NOT NULL,                         -- follows naming convention: [Objective]_[Brand]_[Market]_[AudienceTemp]_[Date]
  objective TEXT NOT NULL,                    -- CONVERSIONS, TRAFFIC, AWARENESS, LEAD_GEN
  status TEXT NOT NULL DEFAULT 'DRAFT',        -- DRAFT, SCHEDULED, ACTIVE, PAUSED, LEARNING, ARCHIVED, SUNSET
  campaign_type TEXT DEFAULT 'STANDARD',      -- STANDARD, ASC
  cbo_enabled BOOLEAN DEFAULT false,
  daily_budget NUMERIC(12,2),
  lifetime_budget NUMERIC(12,2),
  spending_limit NUMERIC(12,2),
  target_ar_cpa NUMERIC(12,2),               -- campaign-specific override (falls back to brand_config)
  target_ar_roas NUMERIC(6,2),
  special_ad_category TEXT,                   -- CREDIT, HOUSING, EMPLOYMENT, POLITICAL, or NULL
  bid_strategy TEXT,                          -- LOWEST_COST, COST_CAP, BID_CAP, MIN_ROAS
  bid_strategy_rationale TEXT,

  -- Lifecycle
  scheduled_launch_at TIMESTAMPTZ,            -- if SCHEDULED, when to go live
  launched_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,
  pause_reason TEXT,
  sunset_at TIMESTAMPTZ,
  sunset_reason TEXT,
  post_mortem TEXT,                           -- campaign sunsetting post-mortem

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  UNIQUE(brand_id, meta_campaign_id)
);

CREATE TABLE ad_sets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  meta_adset_id TEXT NOT NULL,
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                         -- follows naming convention: [AudienceType]_[Segment]_[Geo]_[Date]
  status TEXT NOT NULL DEFAULT 'ACTIVE',      -- ACTIVE, PAUSED, LEARNING, LEARNING_LIMITED

  -- Targeting
  audience_id UUID,                           -- references audiences table
  targeting_config JSONB,                     -- full targeting parameters from Data & Placement Analyst
  exclusions JSONB,                           -- exclusion rules with reasoning

  -- Delivery
  placement_config JSONB,                     -- { inclusions: [], exclusions: [] }
  dayparting_config JSONB,                    -- { golden_hours: [], dead_zones: [] }
  frequency_cap INTEGER,

  -- Budget & bid
  daily_budget NUMERIC(12,2),
  bid_strategy TEXT,                          -- LOWEST_COST, COST_CAP, BID_CAP, MIN_ROAS
  bid_cap NUMERIC(12,2),

  -- Learning phase
  learning_phase_start TIMESTAMPTZ,
  learning_phase_exit TIMESTAMPTZ,
  learning_phase_status TEXT DEFAULT 'NOT_STARTED',  -- NOT_STARTED, IN_LEARNING, EXITED, LIMITED

  -- Lifecycle
  created_at TIMESTAMPTZ DEFAULT now(),
  paused_at TIMESTAMPTZ,
  pause_reason TEXT,
  ar_cpa_at_pause NUMERIC(12,2),
  total_spend_at_pause NUMERIC(12,2),

  UNIQUE(brand_id, meta_adset_id)
);

CREATE TABLE ads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  meta_ad_id TEXT NOT NULL,
  ad_set_id UUID NOT NULL REFERENCES ad_sets(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                         -- follows naming convention: [Mode]_[Visual]_[CopyAngle]_[Variant]_[Date]
  status TEXT NOT NULL DEFAULT 'ACTIVE',      -- ACTIVE, PAUSED, DRAFT

  -- Creative details
  creative_mode TEXT,                         -- A (own winner replication), B (competitor-inspired)
  visual_description TEXT,
  copy_angle TEXT,
  variant_number INTEGER,
  primary_text TEXT,
  headline TEXT,
  description TEXT,
  cta_type TEXT,

  -- Destination
  landing_page_url TEXT,
  landing_page_id UUID,                       -- references landing_pages table

  -- UTMs (non-negotiable)
  utm_source TEXT DEFAULT 'facebook',
  utm_medium TEXT DEFAULT 'paid_social',
  utm_campaign TEXT,                          -- {brand_id}_{campaign_id}_{campaign_name}
  utm_content TEXT,                           -- {ad_id}_{image_identifier}_{copy_identifier}
  utm_term TEXT,                              -- {adset_id}_{audience_segment}

  -- Creative linkage
  creative_registry_id UUID,                  -- references creative_registry

  -- Andromeda classification
  andromeda_cluster TEXT,                     -- visual style cluster (1 of 7)
  color_subcluster TEXT,                      -- color sub-cluster (1 of 5)

  -- Health
  fatigue_score NUMERIC(5,2) DEFAULT 0,
  fatigue_threshold NUMERIC(5,2),             -- from Creative Analyst
  days_active INTEGER DEFAULT 0,
  peak_ar_roas NUMERIC(6,2),
  peak_ar_roas_date DATE,

  -- Lifecycle
  created_at TIMESTAMPTZ DEFAULT now(),
  launched_at TIMESTAMPTZ,
  paused_at TIMESTAMPTZ,
  pause_reason TEXT,

  UNIQUE(brand_id, meta_ad_id)
);


-- ============================================================
-- 3. DAILY METRICS (triple-source: Meta, GA4 True, AR)
-- ============================================================

CREATE TABLE daily_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  date DATE NOT NULL,                               -- date in brand_config.timezone (NOT UTC, NOT GA4 property timezone)
  timezone TEXT,                                     -- IANA timezone this date was recorded in (snapshot from brand_config)

  -- Entity linkage (exactly one populated per row)
  campaign_id UUID REFERENCES campaigns(id),
  ad_set_id UUID REFERENCES ad_sets(id),
  ad_id UUID REFERENCES ads(id),
  level TEXT NOT NULL CHECK (level IN ('campaign', 'ad_set', 'ad')),

  -- Breakdown (NULL = total, otherwise specific dimension)
  breakdown_dimension TEXT,                   -- NULL, 'age', 'gender', 'geo_region', 'geo_dma', 'placement', 'device', 'hour', 'day_of_week'
  breakdown_value TEXT,                       -- NULL, or the specific value (e.g., '25-34', 'female', 'TX', 'instagram_reels')

  -- META-REPORTED (self-reported, over-counts 25-60%)
  meta_impressions BIGINT,
  meta_clicks BIGINT,
  meta_spend NUMERIC(12,2),
  meta_conversions INTEGER,
  meta_revenue NUMERIC(12,2),
  meta_cpa NUMERIC(12,2),
  meta_roas NUMERIC(6,2),
  meta_cpm NUMERIC(12,2),
  meta_cpc NUMERIC(12,2),
  meta_ctr NUMERIC(8,4),                     -- percentage
  meta_frequency NUMERIC(6,2),
  meta_reach BIGINT,

  -- GA4 TRUE (under-counts ~20%)
  ga4_sessions INTEGER,
  ga4_conversions INTEGER,
  ga4_revenue NUMERIC(12,2),
  ga4_bounce_rate NUMERIC(5,2),
  ga4_avg_session_duration NUMERIC(8,2),      -- seconds
  true_cpa NUMERIC(12,2),                     -- meta_spend / ga4_conversions (GA4 source metric, NOT for decisions)
  true_roas NUMERIC(6,2),                     -- ga4_revenue / meta_spend (GA4 source metric, NOT for decisions)

  -- AR — ASSUMED REAL (GA4 x ar_multiplier, THE DECISION METRIC)
  ar_multiplier NUMERIC(4,2) DEFAULT 1.20,    -- the multiplier used for this row (snapshot)
  ar_conversions NUMERIC(12,2),               -- ga4_conversions x ar_multiplier
  ar_revenue NUMERIC(12,2),                   -- ga4_revenue x ar_multiplier
  ar_cpa NUMERIC(12,2),                       -- meta_spend / ar_conversions
  ar_roas NUMERIC(6,2),                       -- ar_revenue / meta_spend

  -- TRACKING HEALTH (per-row)
  click_to_session_rate NUMERIC(6,2),         -- (ga4_sessions / meta_clicks) x 100
  meta_ga4_discrepancy NUMERIC(6,2),          -- ((meta_conversions - ga4_conversions) / meta_conversions) x 100

  -- ENGAGEMENT
  reactions INTEGER,
  comments INTEGER,
  shares INTEGER,
  saves INTEGER,
  negative_reactions INTEGER,                 -- angry reactions

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT now(),

  -- Prevent duplicate rows (per brand)
  UNIQUE(brand_id, date, campaign_id, ad_set_id, ad_id, level, breakdown_dimension, breakdown_value)
);


-- ============================================================
-- 4. CREATIVE REGISTRY (Creative Producer writes, Creative Analyst reads)
-- ============================================================

CREATE TABLE creative_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,

  -- Generation details
  mode TEXT NOT NULL CHECK (mode IN ('A', 'B')),  -- A = own winner replication, B = competitor-inspired
  source_ad_id UUID REFERENCES ads(id),           -- Mode A: which winner was replicated
  source_competitor TEXT,                          -- Mode B: which competitor was referenced
  source_competitor_ad_id UUID,                    -- Mode B: which competitor ad was referenced

  -- Creative specifications
  prompt_used TEXT,
  model_used TEXT,                                -- e.g., 'gemini_3_pro_image'
  background_color TEXT,                          -- hex
  hero_element TEXT,                              -- description of hero image
  text_angle TEXT,                                -- selling point / offer / urgency
  copy_primary TEXT,
  copy_headline TEXT,
  copy_description TEXT,
  cta_type TEXT,

  -- Generated assets
  image_urls JSONB DEFAULT '{}',                  -- { "1x1": "url", "9x16": "url", "16x9": "url" }
  video_brief JSONB,                              -- video script details if applicable
  carousel_layout JSONB,                          -- card sequence if applicable

  -- Andromeda classification
  visual_cluster TEXT,                            -- 1 of 7 visual style clusters
  color_subcluster TEXT,                          -- 1 of 5 color sub-clusters

  -- QC pipeline
  qc_passed BOOLEAN DEFAULT false,
  qc_scores JSONB DEFAULT '{}',                    -- { "professional_quality": 8.5, "text_readability": 9.0, "text_density_pct": 15, "text_density_pass": true, "color_consistency": 7.5, "artifacts": 9.5, "brand_integrity": 8.0, "average": 8.5 }
  banned_words_check BOOLEAN DEFAULT false,
  aspect_ratio_check BOOLEAN DEFAULT false,
  brand_compliance_check BOOLEAN DEFAULT false,
  qc_notes TEXT,

  -- Meta linkage (populated after launch by Campaign Creator)
  meta_ad_id TEXT,
  meta_ad_set_id TEXT,
  launched_at TIMESTAMPTZ,

  -- Performance tracking (populated by Creative Analyst after 2+ weeks)
  ar_cpa_7d NUMERIC(12,2),
  ar_roas_7d NUMERIC(6,2),
  ar_cpa_14d NUMERIC(12,2),
  ar_roas_14d NUMERIC(6,2),
  ar_cpa_30d NUMERIC(12,2),
  ar_roas_30d NUMERIC(6,2),
  performance_verdict TEXT,                       -- WINNER, LOSER, INCONCLUSIVE

  -- Status
  status TEXT DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'QC_PASSED', 'DELIVERED', 'LIVE', 'PAUSED', 'RETIRED')),

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 5. AUDIENCE LIBRARY (Data & Placement Analyst writes)
-- ============================================================

CREATE TABLE audiences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                             -- follows naming convention
  audience_type TEXT NOT NULL,                    -- CUSTOM, LOOKALIKE, RETARGETING, INTEREST, BROAD, EXCLUSION
  meta_audience_id TEXT,                          -- Meta's audience ID once created

  -- Configuration
  targeting_config JSONB NOT NULL,                -- full Meta targeting parameters
  exclusions JSONB DEFAULT '[]',                  -- exclusion rules with reasoning
  lookalike_source TEXT,                          -- source audience for LALs
  lookalike_percentage NUMERIC(3,1),              -- 1%, 2%, etc.
  estimated_size BIGINT,

  -- Geographic
  geo_targeting JSONB,                            -- { countries: [], regions: [], dmas: [] }

  -- Classification
  temperature TEXT CHECK (temperature IN ('COLD', 'WARM', 'HOT')),
  segment_detail TEXT,                            -- e.g., "Women 25-34 TX Purchasers 1% LAL"

  -- Performance (updated each cycle)
  current_ar_cpa NUMERIC(12,2),
  current_ar_roas NUMERIC(6,2),
  classification TEXT,                            -- WINNER, LOSER, INCONCLUSIVE, HIDDEN_GEM, STRONG_WINNER, STRONG_LOSER
  confidence_pct NUMERIC(5,2),
  total_spend NUMERIC(12,2),
  total_ar_conversions NUMERIC(12,2),

  -- Assignment
  campaign_id UUID REFERENCES campaigns(id),
  ad_set_id UUID REFERENCES ad_sets(id),

  -- Status
  status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'ARCHIVED', 'DEPRECATED')),
  archived_at TIMESTAMPTZ,
  archive_reason TEXT,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 6. LANDING PAGES (Post-Click Analyst writes)
-- ============================================================

CREATE TABLE landing_pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  page_name TEXT,

  -- Scorecard
  verdict TEXT CHECK (verdict IN ('KEEP', 'FIX', 'KILL')),
  overall_score NUMERIC(5,2),

  -- Metrics
  bounce_rate NUMERIC(5,2),
  conversion_rate NUMERIC(5,2),
  avg_session_duration NUMERIC(8,2),              -- seconds
  mobile_score NUMERIC(5,2),
  desktop_score NUMERIC(5,2),
  load_time_ms INTEGER,

  -- Funnel
  funnel_stage TEXT,                              -- LANDING, PRODUCT, CART, CHECKOUT, CONFIRMATION
  cart_abandonment_rate NUMERIC(5,2),

  -- Assignment
  audience_segments TEXT[],                       -- which segments this page targets

  -- Status
  status TEXT DEFAULT 'APPROVED' CHECK (status IN ('APPROVED', 'FIX_NEEDED', 'KILLED', 'EMERGENCY_DOWN')),
  emergency_detected_at TIMESTAMPTZ,
  emergency_resolved_at TIMESTAMPTZ,

  last_checked TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  notes TEXT,

  UNIQUE(brand_id, url)
);


-- ============================================================
-- 7. COMPETITORS (Competitive Intel writes — per brand)
-- ============================================================

CREATE TABLE competitors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  brand_name TEXT NOT NULL,                         -- competitor brand name
  ad_library_url TEXT,
  market TEXT,                                    -- market/vertical

  -- Current state
  active_ads_count INTEGER DEFAULT 0,
  estimated_spend_tier TEXT,                      -- LOW, MEDIUM, HIGH, VERY_HIGH
  dominant_formats TEXT[] DEFAULT '{}',            -- e.g., {'video', 'carousel'}
  dominant_themes TEXT[] DEFAULT '{}',             -- e.g., {'social_proof', 'urgency'}
  dominant_platforms TEXT[] DEFAULT '{}',          -- e.g., {'facebook', 'instagram'}

  -- Scoring
  overall_longevity_score NUMERIC(5,2),           -- average of their ad longevity scores
  threat_level TEXT DEFAULT 'LOW',                -- LOW, MEDIUM, HIGH

  -- Status
  status TEXT DEFAULT 'MONITORING' CHECK (status IN ('MONITORING', 'NEW', 'ARCHIVED')),
  last_checked TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  notes TEXT
);

CREATE TABLE competitor_ads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competitor_id UUID NOT NULL REFERENCES competitors(id) ON DELETE CASCADE,
  ad_library_id TEXT,

  -- Ad details
  format TEXT,                                    -- IMAGE, VIDEO, CAROUSEL, COLLECTION
  visual_description TEXT,
  copy_angle TEXT,
  cta_type TEXT,
  landing_page_url TEXT,
  platforms TEXT[] DEFAULT '{}',                   -- e.g., {'facebook', 'instagram'}

  -- Duration & scoring
  first_seen DATE,
  last_seen DATE,
  days_active INTEGER GENERATED ALWAYS AS (last_seen - first_seen) STORED,
  longevity_score NUMERIC(5,2),                   -- 1-10: >60d = 8-10, 30-60 = 5-7, <30 = 1-4
  multi_placement BOOLEAN DEFAULT false,          -- +1 bonus
  scaling_signals BOOLEAN DEFAULT false,          -- +1 bonus

  -- Relevance to us
  relevance TEXT DEFAULT 'LOW',                   -- HIGH, MEDIUM, LOW
  mode_b_candidate BOOLEAN DEFAULT false,         -- worth replicating?
  mode_b_notes TEXT,

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 8. OPTIMIZATION CYCLES (Orchestrator manages — per brand)
-- ============================================================

CREATE TABLE optimization_cycles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_number SERIAL,

  -- Status
  status TEXT DEFAULT 'PHASE_1' CHECK (status IN ('PHASE_1', 'PHASE_2', 'PHASE_3', 'PHASE_4', 'PHASE_5', 'COMPLETED')),
  action_level TEXT,                              -- MODE_1 (ad rotation), MODE_2 (ad set changes), MODE_3 (new campaign)

  -- Phase tracking
  phase_1_started_at TIMESTAMPTZ,                 -- intelligence gathering
  phase_1_completed_at TIMESTAMPTZ,
  phase_2_started_at TIMESTAMPTZ,                 -- analyze and decide
  phase_2_completed_at TIMESTAMPTZ,
  phase_3_started_at TIMESTAMPTZ,                 -- present to human
  phase_3_completed_at TIMESTAMPTZ,
  phase_4_started_at TIMESTAMPTZ,                 -- brief, produce, assemble
  phase_4_completed_at TIMESTAMPTZ,
  phase_5_started_at TIMESTAMPTZ,                 -- monitoring
  phase_5_completed_at TIMESTAMPTZ,

  -- Human approval
  human_approved BOOLEAN DEFAULT false,
  human_approved_at TIMESTAMPTZ,
  human_modifications TEXT,                       -- what did the human change from the recommendation?

  -- Summary
  cycle_summary TEXT,                             -- the Cycle Summary delivered to the human
  total_actions INTEGER DEFAULT 0,
  total_estimated_savings NUMERIC(12,2),
  total_actual_savings NUMERIC(12,2),             -- filled after next cycle

  -- Timing
  started_at TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ,
  next_cycle_due TIMESTAMPTZ,                     -- started_at + 6 days

  UNIQUE(brand_id, cycle_number)
);


-- ============================================================
-- 9. AGENT DELIVERABLES (tracks what each agent owes per cycle per brand)
-- ============================================================

CREATE TABLE agent_deliverables (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),
  agent_name TEXT NOT NULL,                       -- data_placement, creative_analyst, post_click, competitive_intel, creative_producer, campaign_creator, campaign_monitor
  deliverable_type TEXT NOT NULL,                  -- '6_day_report', '365_day_report', 'landing_page_scorecard', 'competitor_landscape', 'asset_package', 'campaign_spec', 'daily_report', 'fatigue_assessment'

  -- Status
  status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'IN_PROGRESS', 'DELIVERED', 'BLOCKED', 'NOT_NEEDED')),
  blocked_reason TEXT,
  blocked_on_agent TEXT,                          -- which agent is blocking this delivery
  blocked_on_input TEXT,                          -- what specific input is missing

  -- Execution (Machine B Runner uses these fields)
  execution_priority INTEGER DEFAULT 99,          -- 1 = highest. Runner picks lowest number first. Default 99 forces explicit assignment.
  runner_picked_at TIMESTAMPTZ,                   -- when the Runner started this task
  runner_machine TEXT,                            -- identifier of the machine that ran this task

  -- Content
  content_json JSONB,                              -- structured report data (all agents reference this field)
  summary TEXT,                                   -- human-readable summary
  file_url TEXT,                                  -- link to full report file if applicable

  -- Timing
  requested_at TIMESTAMPTZ DEFAULT now(),
  started_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  expected_delivery TIMESTAMPTZ
);


-- ============================================================
-- 10. ALERTS (Campaign Monitor + Data & Placement Analyst write)
-- ============================================================

CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),
  source_agent TEXT NOT NULL,

  -- Classification
  severity TEXT NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
  alert_type TEXT NOT NULL,                       -- TRACKING_BROKEN, SPEND_RUNAWAY, CPA_SPIKE, PIXEL_DOWN, FATIGUE, AUDIENCE_EXHAUSTION, BUDGET_PACING, LEARNING_LIMITED, OVERLAP, LANDING_PAGE_DOWN, NEGATIVE_SENTIMENT

  -- Details
  title TEXT NOT NULL,
  description TEXT NOT NULL,

  -- Affected entity
  campaign_id UUID REFERENCES campaigns(id),
  ad_set_id UUID REFERENCES ad_sets(id),
  ad_id UUID REFERENCES ads(id),

  -- Impact
  money_at_risk_hourly NUMERIC(12,2),
  money_wasted NUMERIC(12,2),
  metric_value NUMERIC(12,2),                     -- the metric that triggered the alert
  metric_threshold NUMERIC(12,2),                 -- the threshold it crossed

  -- Resolution
  status TEXT DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'ACKNOWLEDGED', 'ESCALATED', 'RESOLVED', 'FALSE_POSITIVE')),
  recommended_action TEXT,
  action_level TEXT CHECK (action_level IN ('AD', 'AD_SET', 'CAMPAIGN', 'INVESTIGATION')),
  resolution TEXT,
  resolved_at TIMESTAMPTZ,
  resolved_by TEXT,

  created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 11. RECOMMENDATIONS (all agents write, Orchestrator manages)
-- ============================================================

CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),
  source_agent TEXT NOT NULL,

  -- Classification
  action_level TEXT NOT NULL CHECK (action_level IN ('AD', 'AD_SET', 'CAMPAIGN', 'INVESTIGATION')),
  action_type TEXT NOT NULL,                      -- PAUSE, ADD, SCALE, MERGE, EXCLUDE, KILL, ROTATE, INVESTIGATE, TEST
  priority INTEGER DEFAULT 5,                     -- 1 = highest

  -- Details
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  reasoning TEXT NOT NULL,

  -- Target entity
  campaign_id UUID REFERENCES campaigns(id),
  ad_set_id UUID REFERENCES ad_sets(id),
  ad_id UUID REFERENCES ads(id),

  -- Impact estimate
  estimated_savings_weekly NUMERIC(12,2),
  estimated_improvement_pct NUMERIC(6,2),

  -- Decision
  status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXECUTED', 'SUPERSEDED')),
  human_decision_notes TEXT,
  decided_at TIMESTAMPTZ,
  executed_at TIMESTAMPTZ,

  -- Outcome (filled after execution)
  actual_savings_weekly NUMERIC(12,2),
  actual_improvement_pct NUMERIC(6,2),
  outcome_notes TEXT,

  created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 12. A/B TESTS (Orchestrator manages)
-- ============================================================

CREATE TABLE ab_tests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),

  -- Definition
  test_name TEXT NOT NULL,
  variable_tested TEXT NOT NULL,                  -- CREATIVE, AUDIENCE, LANDING_PAGE, BID_STRATEGY, COPY
  hypothesis TEXT NOT NULL,
  success_metric TEXT NOT NULL,                   -- AR_CPA, AR_ROAS, CONVERSION_RATE

  -- Structure
  control_ad_set_id UUID REFERENCES ad_sets(id),
  variant_ad_set_id UUID REFERENCES ad_sets(id),
  campaign_id UUID REFERENCES campaigns(id),
  test_budget_pct NUMERIC(5,2),                   -- % of total budget

  -- Requirements
  min_duration_days INTEGER DEFAULT 7,
  min_conversions INTEGER DEFAULT 30,
  target_confidence NUMERIC(5,2) DEFAULT 95.0,

  -- Timing
  started_at TIMESTAMPTZ,
  expected_end_at TIMESTAMPTZ,
  actual_end_at TIMESTAMPTZ,

  -- Results
  control_metric_value NUMERIC(12,2),
  variant_metric_value NUMERIC(12,2),
  control_conversions INTEGER,
  variant_conversions INTEGER,
  improvement_pct NUMERIC(6,2),
  confidence_pct NUMERIC(5,2),
  result TEXT CHECK (result IN ('VARIANT_WINS', 'CONTROL_WINS', 'INCONCLUSIVE', 'EARLY_STOP', 'RUNNING', NULL)),

  -- Action
  action_taken TEXT,                              -- SCALED_VARIANT, KILLED_VARIANT, KEPT_CONTROL, PENDING
  projected_weekly_impact NUMERIC(12,2),

  -- Status
  status TEXT DEFAULT 'PLANNED' CHECK (status IN ('PLANNED', 'RUNNING', 'COMPLETED', 'EARLY_STOPPED')),

  created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 13. CANNIBALIZATION SCORES (Data & Placement Analyst writes)
-- ============================================================

CREATE TABLE cannibalization_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),
  date DATE NOT NULL,

  -- Pair type: campaign-pair or ad_set-pair
  pair_type TEXT NOT NULL CHECK (pair_type IN ('campaign', 'ad_set')),
  entity_a_id UUID NOT NULL,                      -- campaign or ad_set UUID
  entity_b_id UUID NOT NULL,

  -- Score components (0-100 each)
  audience_overlap_pct NUMERIC(5,2),
  shared_converter_pct NUMERIC(5,2),
  cpm_inflation_pct NUMERIC(5,2),
  budget_ratio_imbalance NUMERIC(5,2),
  performance_delta NUMERIC(5,2),

  -- Composite
  cannibal_score NUMERIC(5,2),                    -- 0-100 weighted composite
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
-- 14. TRACKING HEALTH LOG (Data & Placement Analyst writes)
-- ============================================================

CREATE TABLE tracking_health (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  campaign_id UUID REFERENCES campaigns(id),

  -- Health metrics
  click_to_session_rate NUMERIC(6,2),
  meta_ga4_discrepancy NUMERIC(6,2),
  utm_integrity BOOLEAN,                          -- no "(not set)" values in GA4
  pixel_status TEXT CHECK (pixel_status IN ('HEALTHY', 'WARNING', 'ERROR', 'DOWN')),
  fbclid_passthrough BOOLEAN,

  -- Overall verdict
  health_status TEXT NOT NULL CHECK (health_status IN ('HEALTHY', 'DEGRADED', 'BROKEN')),
  issues TEXT[],                                  -- array of specific issue descriptions

  created_at TIMESTAMPTZ DEFAULT now(),

  UNIQUE(brand_id, date, campaign_id)
);


-- ============================================================
-- 15. CAMPAIGN CHANGES LOG (Campaign Creator writes — audit trail)
-- ============================================================

CREATE TABLE campaign_changes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,
  cycle_id UUID REFERENCES optimization_cycles(id),

  -- What changed
  change_type TEXT NOT NULL,                      -- AD_PAUSED, AD_ADDED, ADSET_PAUSED, ADSET_ADDED, CAMPAIGN_LAUNCHED, CAMPAIGN_PAUSED, BUDGET_CHANGED, BID_CHANGED
  action_level TEXT NOT NULL CHECK (action_level IN ('AD', 'AD_SET', 'CAMPAIGN')),

  -- Affected entity
  campaign_id UUID REFERENCES campaigns(id),
  ad_set_id UUID REFERENCES ad_sets(id),
  ad_id UUID REFERENCES ads(id),

  -- Before/after
  previous_state JSONB,                           -- snapshot before the change
  new_state JSONB,                                -- snapshot after the change

  -- Reasoning
  reason TEXT NOT NULL,
  source_recommendation_id UUID REFERENCES recommendations(id),

  -- Approval
  approved_by TEXT DEFAULT 'human',
  approved_at TIMESTAMPTZ,
  executed_at TIMESTAMPTZ DEFAULT now(),

  created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- 16. HUMAN CREATIVE INSPIRATION (human submits competitor ads as inspiration)
-- ============================================================

CREATE TABLE human_creative_inspiration (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES brand_config(id) ON DELETE CASCADE,

  -- Source
  submitted_by TEXT DEFAULT 'human',
  competitor_brand TEXT,                      -- which competitor or brand this is from
  source_url TEXT,                            -- link to the original ad, landing page, or Ad Library
  source_platform TEXT DEFAULT 'meta',        -- meta, tiktok, google, instagram, other

  -- What the human provides
  image_urls JSONB DEFAULT '[]',             -- uploaded screenshots or hosted image URLs
  ad_copy_primary TEXT,                      -- the primary ad text they liked
  ad_copy_headline TEXT,                     -- headline they liked
  ad_copy_description TEXT,                  -- description they liked
  video_url TEXT,                            -- video link if applicable
  format TEXT,                               -- IMAGE, VIDEO, CAROUSEL, COLLECTION

  -- What they liked about it
  inspiration_notes TEXT NOT NULL,            -- free-text: "I love the layout, minimal text, urgency CTA"
  elements_to_replicate TEXT[] DEFAULT '{}', -- structured: {'layout', 'color_scheme', 'copy_angle', 'visual_style', 'cta', 'urgency', 'social_proof', 'format'}
  elements_to_avoid TEXT[] DEFAULT '{}',     -- what NOT to copy

  -- Our brand adaptation
  target_product TEXT,                       -- which of our products should feature
  target_audience TEXT,                      -- who this creative should target
  target_placement TEXT,                     -- feed, stories, reels, all
  requested_variants INTEGER DEFAULT 3,      -- how many variants to produce from this inspiration
  priority TEXT DEFAULT 'NORMAL' CHECK (priority IN ('URGENT', 'HIGH', 'NORMAL', 'LOW')),

  -- Processing status
  status TEXT DEFAULT 'NEW' CHECK (status IN ('NEW', 'QUEUED', 'IN_PRODUCTION', 'COMPLETED', 'REJECTED')),
  assigned_cycle_id UUID REFERENCES optimization_cycles(id),
  creative_registry_ids JSONB DEFAULT '[]',  -- UUIDs of produced creatives linked back
  processed_at TIMESTAMPTZ,
  rejection_reason TEXT,

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================
-- INDEXES
-- ============================================================

-- Brand indexes (every brand-scoped table gets a brand_id index)
CREATE INDEX idx_campaigns_brand ON campaigns(brand_id);
CREATE INDEX idx_ad_sets_brand ON ad_sets(brand_id);
CREATE INDEX idx_ads_brand ON ads(brand_id);
CREATE INDEX idx_dm_brand ON daily_metrics(brand_id);
CREATE INDEX idx_cr_brand ON creative_registry(brand_id);
CREATE INDEX idx_audiences_brand ON audiences(brand_id);
CREATE INDEX idx_landing_pages_brand ON landing_pages(brand_id);
CREATE INDEX idx_competitors_brand ON competitors(brand_id);
CREATE INDEX idx_cycles_brand ON optimization_cycles(brand_id);
CREATE INDEX idx_deliverables_brand ON agent_deliverables(brand_id);
CREATE INDEX idx_alerts_brand ON alerts(brand_id);
CREATE INDEX idx_recs_brand ON recommendations(brand_id);
CREATE INDEX idx_ab_tests_brand ON ab_tests(brand_id);
CREATE INDEX idx_cannibal_brand ON cannibalization_scores(brand_id);
CREATE INDEX idx_th_brand ON tracking_health(brand_id);
CREATE INDEX idx_changes_brand ON campaign_changes(brand_id);
CREATE INDEX idx_inspiration_brand ON human_creative_inspiration(brand_id);
CREATE INDEX idx_inspiration_status ON human_creative_inspiration(brand_id, status) WHERE status IN ('NEW', 'QUEUED');

-- Daily metrics (most queried table)
CREATE INDEX idx_dm_brand_date ON daily_metrics(brand_id, date);
CREATE INDEX idx_dm_campaign_date ON daily_metrics(campaign_id, date) WHERE level = 'campaign';
CREATE INDEX idx_dm_adset_date ON daily_metrics(ad_set_id, date) WHERE level = 'ad_set';
CREATE INDEX idx_dm_ad_date ON daily_metrics(ad_id, date) WHERE level = 'ad';
CREATE INDEX idx_dm_level_date ON daily_metrics(level, date);
CREATE INDEX idx_dm_breakdown ON daily_metrics(breakdown_dimension, breakdown_value, date);

-- Alerts
CREATE INDEX idx_alerts_severity_status ON alerts(severity, status);
CREATE INDEX idx_alerts_campaign ON alerts(campaign_id, created_at DESC);
CREATE INDEX idx_alerts_open ON alerts(status) WHERE status = 'OPEN';

-- Recommendations
CREATE INDEX idx_recs_status ON recommendations(status);
CREATE INDEX idx_recs_cycle ON recommendations(cycle_id);

-- Creative registry
CREATE INDEX idx_cr_status ON creative_registry(status);
CREATE INDEX idx_cr_mode ON creative_registry(mode);
CREATE INDEX idx_cr_meta_ad ON creative_registry(meta_ad_id) WHERE meta_ad_id IS NOT NULL;

-- Audiences
CREATE INDEX idx_audiences_status ON audiences(status);
CREATE INDEX idx_audiences_type ON audiences(audience_type, status);

-- Tracking health
CREATE INDEX idx_th_date_campaign ON tracking_health(date, campaign_id);

-- Cycles
CREATE INDEX idx_cycles_status ON optimization_cycles(status);
CREATE INDEX idx_cycles_brand_status ON optimization_cycles(brand_id, status);

-- Campaign changes
CREATE INDEX idx_changes_cycle ON campaign_changes(cycle_id);
CREATE INDEX idx_changes_campaign ON campaign_changes(campaign_id, executed_at DESC);

-- Competitor ads
CREATE INDEX idx_comp_ads_competitor ON competitor_ads(competitor_id);
CREATE INDEX idx_comp_ads_mode_b ON competitor_ads(mode_b_candidate) WHERE mode_b_candidate = true;


-- ============================================================
-- VIEWS (pre-built queries agents use frequently)
-- ============================================================

-- Latest metrics per ad (most recent date, no breakdown)
CREATE VIEW v_latest_ad_metrics AS
SELECT DISTINCT ON (dm.ad_id)
  dm.*,
  a.name AS ad_name,
  a.brand_id,
  a.creative_mode,
  a.visual_description,
  a.fatigue_score,
  a.andromeda_cluster,
  aset.name AS ad_set_name,
  aset.learning_phase_status,
  c.name AS campaign_name,
  c.target_ar_cpa,
  c.target_ar_roas,
  c.objective
FROM daily_metrics dm
JOIN ads a ON dm.ad_id = a.id
JOIN ad_sets aset ON a.ad_set_id = aset.id
JOIN campaigns c ON aset.campaign_id = c.id
WHERE dm.level = 'ad'
  AND dm.breakdown_dimension IS NULL
ORDER BY dm.ad_id, dm.date DESC;

-- Campaign health dashboard (latest day per active campaign)
CREATE VIEW v_campaign_health AS
SELECT DISTINCT ON (c.id)
  c.id,
  c.brand_id,
  c.meta_campaign_id,
  c.name,
  c.objective,
  c.campaign_type,
  c.status,
  c.target_ar_cpa,
  c.target_ar_roas,
  c.daily_budget,
  dm.date,
  dm.meta_spend,
  dm.ar_cpa,
  dm.ar_roas,
  dm.ar_conversions,
  dm.click_to_session_rate,
  dm.meta_ga4_discrepancy,
  th.health_status AS tracking_health,
  CASE
    WHEN dm.ar_cpa IS NULL THEN 'NO_DATA'
    WHEN dm.ar_cpa > c.target_ar_cpa * 3 THEN 'CRITICAL'
    WHEN dm.ar_cpa > c.target_ar_cpa * 2 THEN 'DECLINING'
    WHEN dm.ar_cpa > c.target_ar_cpa * 1.3 THEN 'WATCH'
    ELSE 'HEALTHY'
  END AS health_score
FROM campaigns c
LEFT JOIN daily_metrics dm ON dm.campaign_id = c.id
  AND dm.level = 'campaign'
  AND dm.breakdown_dimension IS NULL
LEFT JOIN tracking_health th ON th.campaign_id = c.id AND th.date = dm.date
WHERE c.status = 'ACTIVE'
ORDER BY c.id, dm.date DESC;

-- Creative performance with registry linkage
CREATE VIEW v_creative_performance AS
SELECT
  cr.id AS registry_id,
  cr.brand_id,
  cr.mode,
  cr.background_color,
  cr.hero_element,
  cr.text_angle,
  cr.visual_cluster,
  cr.color_subcluster,
  cr.performance_verdict,
  a.id AS ad_id,
  a.meta_ad_id,
  a.name AS ad_name,
  a.status AS ad_status,
  a.fatigue_score,
  a.days_active,
  dm.date,
  dm.ar_cpa,
  dm.ar_roas,
  dm.meta_ctr,
  dm.meta_frequency,
  dm.meta_spend
FROM creative_registry cr
LEFT JOIN ads a ON a.creative_registry_id = cr.id
LEFT JOIN daily_metrics dm ON dm.ad_id = a.id
  AND dm.level = 'ad'
  AND dm.breakdown_dimension IS NULL
WHERE cr.status IN ('LIVE', 'PAUSED');

-- Active audience performance
CREATE VIEW v_audience_performance AS
SELECT
  au.id,
  au.brand_id,
  au.name,
  au.audience_type,
  au.temperature,
  au.segment_detail,
  au.classification,
  au.confidence_pct,
  au.current_ar_cpa,
  au.current_ar_roas,
  au.total_spend,
  au.total_ar_conversions,
  aset.name AS ad_set_name,
  aset.status AS ad_set_status,
  c.name AS campaign_name
FROM audiences au
LEFT JOIN ad_sets aset ON au.ad_set_id = aset.id
LEFT JOIN campaigns c ON au.campaign_id = c.id
WHERE au.status = 'ACTIVE';

-- Open alerts summary
CREATE VIEW v_open_alerts AS
SELECT
  a.*,
  c.name AS campaign_name,
  aset.name AS ad_set_name,
  ad.name AS ad_name
FROM alerts a
LEFT JOIN campaigns c ON a.campaign_id = c.id
LEFT JOIN ad_sets aset ON a.ad_set_id = aset.id
LEFT JOIN ads ad ON a.ad_id = ad.id
WHERE a.status IN ('OPEN', 'ESCALATED')
ORDER BY
  CASE a.severity
    WHEN 'CRITICAL' THEN 1
    WHEN 'HIGH' THEN 2
    WHEN 'MEDIUM' THEN 3
    WHEN 'LOW' THEN 4
  END,
  a.created_at DESC;

-- Cycle deliverables status
CREATE VIEW v_cycle_status AS
SELECT
  oc.id AS cycle_id,
  oc.brand_id,
  oc.cycle_number,
  oc.status AS cycle_status,
  oc.action_level,
  oc.started_at,
  ad.agent_name,
  ad.deliverable_type,
  ad.status AS deliverable_status,
  ad.blocked_reason,
  ad.delivered_at
FROM optimization_cycles oc
LEFT JOIN agent_deliverables ad ON ad.cycle_id = oc.id
WHERE oc.status != 'COMPLETED'
ORDER BY oc.cycle_number DESC, ad.agent_name;


-- ============================================================
-- SETUP LOG (tracks setup skill progress — system-wide, not per brand)
-- ============================================================

CREATE TABLE setup_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phase INTEGER NOT NULL,                   -- 0-7
  phase_name TEXT NOT NULL,                 -- self_check, supabase, credentials, machine_b, deployment, brand_onboarding, agent_testing, readiness
  status TEXT NOT NULL DEFAULT 'PENDING',   -- PENDING, IN_PROGRESS, COMPLETE, FAILED, SKIPPED
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  details JSONB DEFAULT '{}',              -- phase-specific results (test scores, verified items, etc.)
  error_message TEXT,                       -- if FAILED, what went wrong
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(phase)                            -- one row per phase, upsert on re-run
);

-- Quick check: is setup complete?
CREATE OR REPLACE VIEW v_setup_status AS
SELECT
  COUNT(*) FILTER (WHERE status = 'COMPLETE') AS phases_complete,
  COUNT(*) FILTER (WHERE status = 'FAILED') AS phases_failed,
  COUNT(*) FILTER (WHERE status = 'PENDING') AS phases_pending,
  CASE
    WHEN COUNT(*) FILTER (WHERE status = 'COMPLETE') = 8 THEN 'READY'
    WHEN COUNT(*) FILTER (WHERE status = 'FAILED') > 0 THEN 'FAILED'
    ELSE 'INCOMPLETE'
  END AS system_status
FROM setup_log;


-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

ALTER TABLE brand_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ads ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE creative_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE audiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE landing_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_ads ENABLE ROW LEVEL SECURITY;
ALTER TABLE optimization_cycles ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_deliverables ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ab_tests ENABLE ROW LEVEL SECURITY;
ALTER TABLE cannibalization_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE tracking_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE human_creative_inspiration ENABLE ROW LEVEL SECURITY;

-- Service role policy: full access for the agent system
CREATE POLICY "service_role_full_access" ON brand_config FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON campaigns FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON ad_sets FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON ads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON daily_metrics FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON creative_registry FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON audiences FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON landing_pages FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON competitors FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON competitor_ads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON optimization_cycles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON agent_deliverables FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON alerts FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON recommendations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON ab_tests FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON cannibalization_scores FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON tracking_health FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON campaign_changes FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON human_creative_inspiration FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_role_full_access" ON setup_log FOR ALL USING (true) WITH CHECK (true);
```

## What This Schema Creates

**18 Tables:**
- brand_config, campaigns, ad_sets, ads, daily_metrics, creative_registry, audiences, landing_pages, competitors, competitor_ads, optimization_cycles, agent_deliverables, alerts, recommendations, ab_tests, cannibalization_scores, tracking_health, campaign_changes, human_creative_inspiration, setup_log

**6 Views:**
- v_latest_ad_metrics, v_campaign_health, v_creative_performance, v_audience_performance, v_open_alerts, v_cycle_status, v_setup_status

**Row Level Security (RLS):**
- All tables have RLS enabled with service role full access policies for agent operations

## Verification After Application

After running the schema SQL, verify everything was created:

```sql
-- Check all tables exist
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
-- Should return: 20 (18 data tables + 2 system tables = setup_log)

-- Check all views exist
SELECT COUNT(*) FROM pg_views WHERE schemaname = 'public';
-- Should return: 7

-- Check RLS is enabled
SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true;
-- Should return: 18 (all brand-scoped tables)
```

If all checks pass, the schema is ready for use. Proceed to Phase 1 completion in the Setup Skill.

# Meta Ads Naming Conventions

## Overview
Every campaign, ad set, and ad follows a consistent naming scheme. This enables filtering, reporting, and cross-referencing across all agents.

---

## Campaign Naming

**Format:**
```
[Objective]_[Brand]_[Market/Product]_[AudienceTemp]_[Date]
```

**Components:**
- **Objective**: CONV (Conversions), TRAFFIC, AWARENESS, LEAD (Lead Generation)
- **Brand**: Brand identifier (e.g., BrandA, SkincareXYZ)
- **Market/Product**: Geographic market or product line (e.g., SkincareUS, FitnessUK, ProductsJP)
- **AudienceTemp**: Audience temperature (Cold, Warm, Hot, Retarget, Prospecting)
- **Date**: Launch date in YYYYMMDD format

**Examples:**
```
CONV_BrandA_SkincareUS_Cold_20260214
CONV_BrandA_SkincareUS_Retarget_20260214
LEAD_BrandB_SaaSUK_Cold_20260301
TRAFFIC_BrandC_FitnessCA_Warm_20260215
AWARENESS_BrandA_ProductsJP_Cold_20260220
```

---

## Ad Set Naming

**Format:**
```
[AudienceType]_[SegmentDetail]_[Geo]_[Date]
```

**Components:**
- **AudienceType**: LAL (Lookalike), INT (Interest), RET (Retargeting), EXC (Excluded), SAC (Similar Audience)
- **SegmentDetail**: Specific audience segment (e.g., Purchasers1pct, FitnessEnthusiasts, CartAbandoners_30d, Losers)
- **Geo**: Geographic targeting (e.g., US, TX, W2534 for region + age range)
- **Date**: Creation date in YYYYMMDD format

**Examples:**
```
LAL_Purchasers1pct_US_20260214
INT_FitnessEnthusiasts_W2534_TX_20260214
RET_CartAbandoners_30d_US_20260214
EXC_Losers_M5564_20260214
SAC_HighValue_CA_20260215
```

**Geographic Code Examples:**
- `US` = Entire United States
- `TX` = Texas
- `W2534` = West region, age 25-34
- `NE4554` = Northeast region, age 45-54
- `CA` = Canada
- `UK` = United Kingdom

---

## Ad Naming

**Format:**
```
[Mode]_[VisualDescription]_[CopyAngle]_[Variant]_[Date]
```

**Components:**
- **Mode**: A (Replicate Own Winners), B (Replicate Competitor), C (Custom)
- **VisualDescription**: Background/color + hero element (e.g., Peach-GoldenRetriever, Blue-Product, Lifestyle-Studio)
- **CopyAngle**: Copy angle category (Price, SocialProof, Benefits, Shipping, Urgency, Trust)
- **Variant**: Version number (v01, v02, v03, etc.)
- **Date**: Creation date in YYYYMMDD format

**Examples:**
```
A_Peach-GoldenRetriever_Price_v01_20260214
B_Lifestyle-Studio_SocialProof_v03_20260214
A_Blue-Product_Urgency_v02_20260214
B_Gradient-Woman_Trust_v01_20260215
A_White-Family_Benefits_v04_20260214
```

**Visual Description Shorthand:**
- Color names: Peach, Blue, White, Gradient, Warm Sand, Cool Gray, etc.
- Hero elements: GoldenRetriever, Woman, Family, Product, Lifestyle, etc.
- Studio types: Studio, Lifestyle, Outdoor, Urban, Home, etc.

---

## UTM Parameter Structure

**Format:**
```
source=facebook
medium=paid_social
campaign={brand_id}_{campaign_id}_{campaign_name}
content={ad_id}_{image_identifier}_{copy_identifier}
term={adset_id}_{audience_segment}
```

**Full Example URL:**
```
https://example.com/product?
  utm_source=facebook
  &utm_medium=paid_social
  &utm_campaign=brand_a_meta_camp_789_CONV_SkincareUS_Cold
  &utm_content=meta_ad_321_peach_retriever_price
  &utm_term=meta_adset_456_LAL_Purchasers1pct_US
```

**Component Details:**

### utm_source
- **Always:** `facebook`
- Purpose: Identifies paid social as the channel

### utm_medium
- **Always:** `paid_social`
- Purpose: Distinguishes from organic social (medium=social)

### utm_campaign
- **Structure:** `{brand_id}_{campaign_id}_{campaign_name}`
- **Example:** `brand_a_meta_camp_789_CONV_SkincareUS_Cold`
- **Purpose:** Identifies the campaign for analytics aggregation
- **Note:** brand_id prefix ensures multi-brand analytics separation

### utm_content
- **Structure:** `{ad_id}_{image_identifier}_{copy_identifier}`
- **Example:** `meta_ad_321_peach_retriever_price`
- **Purpose:** Identifies the specific ad creative for performance analysis
- **Note:** Used to attribute conversions to specific image+copy combinations

### utm_term
- **Structure:** `{adset_id}_{audience_segment}`
- **Example:** `meta_adset_456_LAL_Purchasers1pct_US`
- **Purpose:** Identifies the audience segment for targeting analysis
- **Note:** Used to track which audience segments drive conversions

---

## Naming Compliance Checklist

Before launching, verify:

- [ ] Campaign name follows `[Objective]_[Brand]_[Market]_[AudienceTemp]_[Date]`
- [ ] Ad set name follows `[AudienceType]_[Segment]_[Geo]_[Date]`
- [ ] Ad name follows `[Mode]_[Visual]_[CopyAngle]_[Variant]_[Date]`
- [ ] All names use underscores (no spaces)
- [ ] Dates are in YYYYMMDD format (e.g., 20260214 for Feb 14, 2026)
- [ ] utm_source = facebook (exact)
- [ ] utm_medium = paid_social (exact)
- [ ] utm_campaign includes brand_id prefix
- [ ] utm_content identifies the ad ID
- [ ] utm_term identifies the ad set ID and segment
- [ ] No special characters in names (only alphanumeric and underscores)
- [ ] All names are descriptive and filterable

---

## Cross-Agent Reference

These naming conventions enable:
- **Creative Analyst** to reference specific ads by mode and visual
- **Data & Placement Analyst** to filter by audience type and segment
- **Campaign Monitor** to identify which ad set and campaign each metric belongs to
- **Orchestrator** to match recommendations to specific campaign structures
- **All agents** to build analytics queries that aggregate by naming pattern

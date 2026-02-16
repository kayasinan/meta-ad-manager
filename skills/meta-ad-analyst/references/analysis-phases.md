# Analysis Phases — Detailed Reference

## Phase 1: Account Audit

### 1.1 Account Overview
Pull active campaigns, ad sets, ads. Get last 30d + last 12mo performance.
Key metrics: spend, purchases, CPA, ROAS, revenue.

### 1.2 Meta vs GA4 Cross-Verification
Compare Meta reported conversions with GA4 purchases filtered by sessionSource.
Calculate over-reporting %. This establishes the "truth gap" — typically 25-60%.
Use GA4 as source of truth for ROI; use Meta data for relative segment comparison.

---

## Phase 2: Segment Breakdowns (12-Month Account Level)

Pull from `act_{ID}/insights` with breakdowns. Always include actions: purchase, add_to_cart, view_content.

| Breakdown | API breakdowns param | Notes |
|---|---|---|
| Age × Gender | `age,gender` | Best/worst demo combos |
| Placements | `publisher_platform,platform_position` | Hidden winners like FB Search |
| Devices | `impression_device` | Tablet waste detection |
| Hourly | `hourly_stats_aggregated_by_advertiser_time_zone` | Golden hours / dead hours |
| Geographic | GA4 only (region dimension) | Meta geo lacks conversion data |

---

## Phase 3: 21-Query Ad Deep Dive

Per-ad or per-campaign granular analysis. Run all 21 queries:

**Single breakdowns:** Q1 baseline, Q2 age, Q3 gender, Q5 publisher_platform, Q6 platform_position, Q8 impression_device, Q11 hourly, Q12 frequency_value, Q17 product_id (action_breakdown)

**Combo breakdowns:** Q4 age×gender, Q7 platform×position, Q9 platform×device, Q10 position×device, Q18 age×platform, Q19 gender×platform

**Triple breakdowns:** Q20 age×gender×platform, Q21 platform×position×device

**Creative (Dynamic only):** Q13-Q16 body/image/title/description_asset

Save results as `q1.json` through `q21.json` per ad.

---

## Phase 4: Cannibalization Analysis

Use `scripts/cannibalization_check.py` or pull ad sets manually.

**Check for:**
1. Multiple broad/ASC ad sets targeting same country+age → HIGH risk
2. Interest ad sets sharing same interests → HIGH risk
3. Broad ad sets overlapping interest ad sets → MEDIUM risk
4. Missing exclusions (retargeting audiences not excluded from prospecting)
5. Missing funnel stages (no retargeting for a country)

**Estimate CPM inflation:** 15-25% when 3+ ad sets overlap heavily.
**Calculate annual waste:** (overlapping spend × CPM inflation %) × 12

---

## Phase 5: Budget Analysis

For each ad set compare daily_budget vs actual spend.
- **Utilization** = monthly_spend / (daily_budget × days_in_month)
- **Budget-capped winners:** >85% utilization + CPA below account avg → SCALE
- **Budget-wasting losers:** high utilization + CPA above 1.5× avg → CUT

**Reallocation scenarios:**
- A: Cut losers, reduce total budget
- B: Reinvest loser budget into winners (same total)
- C: Theoretical ceiling (all at winner efficiency)

---

## Phase 6: Creative Format Comparison

Group all ads by format: Catalog, Static Image, Video, Manual Carousel, GIF, UGC.
Compare CPA, ROAS, CVR per format.

---

## Phase 7: Creative Content Deep Dive

### 7.1 Separate catalog vs creative ads
Catalog = `catalog` in ad name. Everything else = creative.

### 7.2 Performance ranking
For each creative ad with >$50 spend: spend, purchases, CPA, ROAS, clicks, CVR%, ATC%, CPC, CPM.

### 7.3 Theme categorization
Group by messaging angle (broad protection, price comparison, single product, seasonal, UGC, etc.)
Calculate CPA/ROAS/CVR per theme.

### 7.4 Content extraction
Pull full creative details via `ads?fields=creative{body,title,image_url,video_id,object_story_spec,link_url}`
For top ads, also fetch via individual ad endpoint for asset_feed_spec (multi-variant ads).

### 7.5 Visual analysis
Download ad images and video thumbnails.
Compare visual elements: background, emotion (positive vs negative), product visibility, text overlays, color scheme.

### 7.6 Funnel analysis
Compare winners vs losers at each funnel stage (CPM → CPC → CTR → ATC% → CVR → ATC-to-Purchase).

### 7.7 Landing page analysis
Classify by landing type: category page, product page, brand page, homepage.
Category pages typically convert best (broader selection).

---

## Phase 8: Waste Quantification & Recommendations

Quantify all waste sources in $/month and $/year:
- Cannibalization, missing retargeting, bad placements, bad creatives, budget misallocation, bad demographics, bad devices

Priority structure:
1. P1: Structural fixes (cannibalization, funnel gaps)
2. P2: Scale winners (budget-capped performers)
3. P3: Launch missing funnels (retargeting, new geos)
4. P4: Cut waste segments
5. P5: Creative strategy

---

## Output Files Per Account

```
data/{account}/              — Raw API JSONs
{ACCOUNT}_SEGMENT_REPORT.md  — Full findings with numbers
{ACCOUNT}_CREATIVE_ANALYSIS.md — Creative deep dive
```

# Google Ads API v17 & GA4 API Known Issues & Workarounds

## Google Ads API v17 Gotchas

### Fractional Conversions
**Issue:** Google Ads reports conversions as decimals (e.g., 2.4 conversions), not integers. This reflects multi-touch attribution or cross-device conversions where fractional credit is assigned.

**Impact:** Complicates statistical analysis and direct comparison with GA4's integer conversions.

**Workaround:** Round to nearest 0.1 for calculations. When performing significance testing, use GA4 integer conversions as the canonical count. Document the fractional nature in reports: "Google Ads reports fractional conversions due to multi-touch attribution."

---

### Quality Score Availability
**Issue:** Quality Score (1-10 scale) is only available at the keyword level via `ad_group_criterion.quality_info`. Cannot pull Quality Score at campaign or ad group level.

**Impact:** Cannot see aggregate Quality Score health at higher levels. Must aggregate up manually.

**Workaround:** Pull keyword-level Quality Score data and aggregate by ad group/campaign (median or average). Flag the N lowest-scoring keywords for improvement. Include caveat: "Quality Score measured at keyword level. Ad group/campaign Quality Scores are aggregated medians."

---

### Impression Share Data Delayed
**Issue:** Impression Share data (% of impressions won, lost to budget, lost to rank) lags by 1 calendar day. Today's campaigns do not have impression share data until tomorrow.

**Impact:** Your impression share queries will not include today's data.

**Workaround:** Always pull impression share with a 1-day lag. In your scheduled 6-day analysis, pull impression share data from 7+ days ago. Include caveat in reports: "Impression Share data current as of yesterday."

---

### Search Term Report Suppression
**Issue:** Google suppresses search terms below a minimum volume threshold (typically 10+ impressions) for "privacy". You cannot see low-volume search terms that may be wasting budget or converting.

**Impact:** Your search term mining will miss some high-opportunity terms and some low-volume waste.

**Workaround:** Work with the data available. Document the limitation in reports: "Search Term Report excludes low-volume queries due to Google's privacy settings. Some conversion opportunities and waste terms may be hidden." Recommend: if low-volume terms are critical for the account, ensure Search Query Insights (conversion value) is properly set up.

---

### Performance Max Limited Reporting
**Issue:** Performance Max campaigns have severely limited breakdown data. Google controls asset serving, and reporting is minimal — you cannot see which specific assets (images, videos, headlines, descriptions) are performing best.

**Impact:** Cannot granularly analyze which creative elements drive performance in Performance Max. Only asset group level aggregation is available.

**Workaround:** Use asset group level data only. Note in reports: "Performance Max campaigns show asset group level performance only. Individual asset performance not available due to Google's optimization model." Recommend manual A/B testing via separate campaigns if granular asset analysis is required.

---

### Auction Insights Unavailable for Multiple Campaign Types
**Issue:** Auction Insights (competitive metrics like impression share overlap, outranking share, position above rate) are only available for Search campaigns. They are NOT available for Display, Shopping, Video, or Performance Max campaigns.

**Impact:** Cannot use Auction Insights analysis for non-Search campaign types.

**Workaround:** Use Auction Insights only for Search campaigns in competitive analysis. For Display, Shopping, Video, and Performance Max, note "Auction Insights unavailable for this campaign type" in reports. Use alternative competitive data (Competitive Intel agent's market research) if competitive positioning is needed.

---

### Video Metrics Different Event Model
**Issue:** Video campaigns (YouTube Ads) track engagement via a different event model: views, quartile completions (25%, 50%, 75%, 100% watched), skip rates, watch time — NOT conversions the same way as Search or Display.

**Impact:** Cannot directly compare video performance to search/display using standard conversion metrics.

**Workaround:** Analyze video performance using video-specific metrics (views, quartile completion rates, skip rates, watch time). Calculate view-through conversion rate separately. Include caveat in all reports: "Video campaign performance measured by engagement (views, completions) and view-through conversions, not direct click conversions."

---

### Campaign Hourly Breakdown "Reduce Data" Error
**Issue:** Google Ads API hits a "data reduction" error when requesting hourly breakdowns for date ranges longer than approximately 90 days.

**Impact:** Your dayparting query fails silently or returns incomplete data for large date ranges.

**Workaround:** Split the date range into quarterly windows (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec) and merge results manually. Process each quarter separately, then combine results by hour of day. Document in code: `# Split dayparting query into quarterly windows due to 90-day limit.`

---

### Conversion Tracking Fragmentation
**Issue:** Google Ads conversion tracking can be set up multiple ways: Google Conversion Tracking, Google Analytics 4 integration, third-party pixel integration. Different setup methods may report different numbers.

**Impact:** Tracking discrepancies between Google Ads reported conversions and GA4 conversions may be due to configuration mismatch, not tracking failure.

**Workaround:** Verify the conversion tracking setup with the client. Ensure Google Ads is pulling conversions from the same source as GA4 (ideally GA4 directly via the integration). Document the conversion source in brand_config. Flag any mismatches in tracking health reports.

---

### Bid Adjustments Not In Breakdown Data
**Issue:** Bid adjustments (device bid adjustment, geographic bid adjustment, audience bid adjustment) are not reflected in the metrics returned by breakdown queries. The metrics are the raw performance, not adjusted performance.

**Impact:** Cannot see how bid adjustments are affecting performance directly from the API.

**Workaround:** Calculate bid adjustment impact manually by comparing "adjusted" performance (metric × bid adjustment multiplier) against actual performance. Document in analysis: "Bid adjustments not included in API metrics; impact estimated based on adjustment multiplier."

---

## GA4 Data API Gotchas

### Session Source Name Varies Per Account
**Issue:** The exact session source value for Google Ads traffic varies by account setup. Common variants: `google`, `google_ads`, `google_cpc`, `cpc`, `paid_search`.

**Impact:** Your session source filter may fail if you hardcode the wrong value for the wrong account.

**Workaround:** Inspect the GA4 data for each account first. Run a test query with `sessionSource = "*"` and check what values appear for Google Ads traffic. Document the exact value for each account in `brand_config`. Use conditional filtering:
```
WHERE sessionSource IN ('google', 'google_ads', 'google_cpc', 'cpc')
  AND sessionMedium IN ('cpc', 'paid_search', 'display', 'video')
```

---

### Session Source / Medium Not Guaranteed
**Issue:** GA4 session source and medium can show as "(not set)" if UTM parameters are missing or improperly passed.

**Impact:** Cannot filter GA4 to Google Ads traffic if UTMs are broken. Results in undercounting conversions.

**Workaround:** Include a tracking health check in every analysis cycle. Monitor UTM integrity: `% of sessions where sessionSource is NOT "(not set)"`. If >5% of sessions have broken UTMs, flag as a tracking issue. Recommend fixing UTM configuration.

---

### Age/Gender Dimensions Incompatible with Session Source Filters
**Issue:** GA4 user-scoped dimensions like `userAgeBracket` and `userGender` are incompatible with session-scoped source/medium filters in the Data API.

**Impact:** Cannot filter GA4 data by age + gender AND traffic source simultaneously in a single query.

**Workaround:** Use Google Ads API for all demographic breakdowns (age × gender). Accept that demographic analysis relies on Google-reported conversions. Note this caveat in all reports: "Demographic analysis uses Google-reported conversions due to GA4 API limitations. GA4 age/gender dimensions are incompatible with source/medium filters."

---

### GCLID Pass-Through Requires Proper Setup
**Issue:** The GCLID (Google Click ID) must be passed from Google Ads → landing page → GA4 for proper session linking. If UTM parameters are set up but GCLID is not passed, GA4 may not properly attribute sessions to Google Ads.

**Impact:** Tracking discrepancies between Google Ads and GA4 even if UTMs are set up correctly.

**Workaround:** Verify GCLID pass-through during tracking health check. Query GA4 for sessions with user pseudo IDs linked to Google Ads sessions via GCLID. If GCLID is missing, note in tracking health report: "GCLID not detected in GA4 data. Ensure landing pages capture and forward GCLID to GA4."

---

### GA4 Data API Row Limit
**Issue:** GA4 Data API has row limits per query response (typically 100,000 rows). Large accounts with many campaigns may hit this limit when querying 365 days at once.

**Impact:** Query returns incomplete data without error notification.

**Workaround:** For large date ranges, query in smaller windows (30-day chunks) and aggregate results manually. Include logic in scripts:
```python
# If results hit row limit, split into smaller date windows
if len(results) == 100000:
    # Split date range in half and retry
```

---

### Event Parameter Filtering Inconsistent
**Issue:** GA4 event parameters (custom dimensions, user properties) are case-sensitive and must match exactly. A mismatch causes the filter to silently return zero results.

**Impact:** Your event-level analysis may fail silently if parameter names are misspelled or inconsistent.

**Workaround:** Test all custom parameter filters first. Query GA4 with `eventName = "*"` and inspect actual parameter names. Document the exact case and spelling in code. Include validation: `assert 'utm_content' in ga4_events, "UTM parameter not found"`

---

## Rate Limiting & Quota

### Google Ads API Rate Limiting
**Rate Limit:** 10,000 API calls per day per manager account (or per customer account if not using a manager account).

**Enforcement:** Google returns 429 (Too Many Requests) when limit is exceeded.

**Workaround:**
1. Batch API calls where possible (use `get_customers` to fetch multiple accounts in one call)
2. Implement retry logic: on 429 response, wait exponentially (1s, 2s, 4s, 8s)
3. Track your daily call count and alert when approaching 80% of limit
4. Cache results aggressively — don't re-query data unnecessarily

---

### GA4 Data API Quota
**Quota:** 10,000 queries per day per Google Cloud project.

**Enforcement:** Google returns a quota exceeded error when limit is reached.

**Workaround:**
1. Batch queries where possible
2. Cache results — store daily metrics locally after first query
3. Implement early-in-the-day execution — run analysis cycles in the morning before quota is exhausted
4. Monitor quota usage and alert when approaching limit

---

## Conversion Attribution Model Mismatch
**Issue:** Google Ads campaigns may use different attribution models (last-click, first-click, linear, time-decay) while GA4 uses its own unified conversion model.

**Impact:** Discrepancies between Google Ads reported conversions and GA4 conversions due to attribution model differences.

**Workaround:** Use GA4 as the canonical source for all conversion analysis. Note in all reports: "Conversion analysis based on GA4 last-click attribution. Google Ads may use different attribution models, causing discrepancies." Include AR multiplier (1.2×) to account for GA4 under-counting across all platforms.

---

# Meta & GA4 API Known Issues & Workarounds

## Meta Ads API Gotchas

### Geographic Data Limitation
**Issue:** Meta geo breakdowns (region, DMA) do NOT return purchase data. They only return impressions, clicks, and spend.

**Impact:** Cannot calculate True CPA by geography from Meta alone.

**Workaround:** Use GA4 for all geographic conversion analysis. Meta geo data is only usable for impressions/clicks/spend metrics. When you need geographic CPA, pull it from GA4's geographic breakdown (Query 7).

---

### Frequency Breakdown for ASC Campaigns
**Issue:** Meta `frequency_value` breakdown returns empty data for ASC (Advantage Shopping Campaigns).

**Impact:** Cannot analyze frequency distribution for ASC campaigns.

**Workaround:** Use account-level frequency as a proxy. Flag ASC campaigns as "frequency data unavailable" in all reports and dashboards. Document this limitation when presenting frequency analysis.

---

### Creative Asset Breakdowns Deprecated in v21+
**Issue:** Meta API v21+ deprecated the creative asset breakdowns (image_asset, video_asset, title_asset, body_asset, description_asset). These queries will return no data.

**Impact:** Cannot pull per-asset performance using the old breakdown approach.

**Workaround:** Use the ad-level `object_story_spec` field to reconstruct creative details from the ad object itself. The Creative Analyst handles the decomposition — you pass the full ad object, they extract the creative details.

---

### Catalog & Dynamic Ads Have No Static Image
**Issue:** Catalog ads (dynamic product ads) are assembled dynamically from a product feed. There is no static "image" to download or analyze.

**Impact:** Cannot analyze or download the actual creative shown to users.

**Workaround:** Flag catalog ads as "dynamic creative — no static image available" in all reports and creative analyses. Rank them by performance metrics only. Do not attempt visual or color extraction for these ads.

---

### Campaign Hourly Breakdown "Reduce Data" Error
**Issue:** Meta API hits a "reduce data" error when requesting hourly breakdowns for date ranges longer than ~90 days.

**Impact:** Your hourly/dayparting query fails silently or returns incomplete data for large date ranges.

**Workaround:** Split the date range into quarterly windows (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec) and merge results manually. Process each quarter separately, then combine results by hour.

---

### Meta Click Count Includes All Click Types
**Issue:** Meta's `clicks` field includes ALL click types: link clicks, post engagement clicks, profile clicks, etc. NOT just website clicks.

**Impact:** Using `clicks` for click-to-session calculations inflates the rate and creates false "good tracking" signals.

**Workaround:** Always use `outbound_clicks` or `website_clicks` for click-to-session rate calculations, NEVER the generic `clicks` field. Be explicit in your code: filter for `click_type='link_click'` or use the specific website-bound metrics.

---

## GA4 Data API Gotchas

### Age/Gender Dimensions Incompatible with Session Source Filters
**Issue:** GA4 user-scoped dimensions like `userAgeBracket` and `userGender` are incompatible with session-scoped source/medium filters.

**Impact:** Cannot filter GA4 data by age + gender AND traffic source simultaneously. You must choose one or the other.

**Workaround:** Use Meta for all demographic breakdowns (age × gender). Accept that demographic analysis relies on Meta-reported conversions. Note this caveat in all reports: "Demographic analysis uses Meta-reported conversions due to GA4 API limitations. GA4 age/gender dimensions are unavailable for paid social traffic due to technical incompatibility."

---

### Session Source Name Varies Per Account
**Issue:** The exact session source value for Meta Ads traffic varies by account. Common variants: `facebook_ads_ppm`, `facebook`, `fb`, `paid_social`.

**Impact:** Your session source filter may fail if you hardcode the wrong value.

**Workaround:** Inspect the GA4 data for your account first. Run a test query with sessionSource = "*" and check what values appear for Meta traffic. Document the exact value for this account and use it consistently. Query pattern:
```
WHERE sessionSource IN ('facebook', 'facebook_ads_ppm', 'fb')
  AND sessionMedium = 'paid_social'
```

---

### GA4 Scope Mismatch
**Issue:** GA4 Data API requires the correct OAuth scope. If using `analytics.readonly`, the account must have proper permissions set up.

**Impact:** Queries fail with "permission denied" errors even though the key is valid.

**Workaround:** Verify:
1. The service account has Editor access to the GA4 property in the Google Cloud project
2. Data API is enabled in the Google Cloud project (API & Services → Libraries → search "Google Analytics Data API v1" → enable it)
3. The OAuth scope is `https://www.googleapis.com/auth/analytics.readonly` (read-only) or `https://www.googleapis.com/auth/analytics` (read-write)

---

## Meta Rate Limiting

**Rate Limit:** 200 API calls per hour per ad account.

**Enforcement:** Meta will return 429 (Too Many Requests) when you exceed this.

**Workaround:**
1. Add 0.3 second sleep between each API call
2. Implement retry logic: on 429 response, wait 60 seconds, then retry
3. Track your call count and alert if approaching the limit

---

## GA4 Data Export Limits

**Limit:** GA4 Data API has row limits per query response. Large accounts may hit row limits when querying 365 days at once.

**Workaround:** For large date ranges, query in smaller windows (30-day chunks) and aggregate results manually.

---

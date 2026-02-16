# Triple-Source Metrics Framework for Google Ads

## The Three Sources

### Source 1: Google Ads Reported Metrics
What Google Ads tells you it did. This is what appears in the Google Ads UI and API.

**Characteristics:**
- Over-counts conversions by 15-40% on average
- Includes multi-touch attribution (fractional conversions)
- Fast reporting (available in real-time or next day)
- NOT a reliable decision metric

**Common over-counting reasons:**
- Attribution modeling (fractional credit to multiple touchpoints)
- Cross-device attribution (credit given for views on one device, conversion on another)
- Assisted conversions (credited for influencing a conversion without direct click)

---

### Source 2: GA4 True Metrics
What Google Analytics 4 actually tracked. This is more conservative and closer to reality.

**Characteristics:**
- Under-counts conversions by ~20% due to tracking limitations
- Uses last-click attribution by default
- Includes consent-mode limitations (some conversions excluded)
- Ad blocker / privacy tool suppression
- Cross-device tracking gaps (only counts conversions on same device/browser)
- Most trustworthy of the raw sources, but still incomplete

**Common under-counting reasons:**
- Cookie consent rejections
- Ad blockers blocking GA4 pixel
- iOS privacy limitations (ITP)
- Cross-device journeys (user clicks on mobile, converts on desktop — GA4 may miss this)
- Server-side conversion tracking gaps

---

### Source 3: AR (Assumed Real)
GA4 × 1.2 — the best estimate of actual reality.

**Formula:** `AR_metric = GA4_metric × 1.2`

**Why 1.2?** Empirically, GA4 under-counts by approximately 20%, making the 1.2× correction factor a reasonable approximation of true conversions (conversions that actually happened, as confirmed by backend/CRM data).

**Characteristics:**
- Balances between Google's over-counting and GA4's under-counting
- Best predictor of actual backend conversions in most cases
- This is the metric you use for all strategic decisions
- Can be calibrated per account by comparing GA4 to CRM data

---

## Metric Calculation Examples

### Example: Campaign CPA Analysis

**Campaign "Summer Sale" Performance:**

| Source | Spend | Conversions | CPA |
|--------|-------|-------------|-----|
| Google Ads | $10,000 | 450 | $22.22 |
| GA4 (True) | $10,000 | 280 | $35.71 |
| AR (Assumed Real) | $10,000 | 336 | $29.76 |

**Interpretation:**
- Google reports $22 CPA (over-optimistic)
- GA4 tracks $36 CPA (under-pessimistic)
- AR estimate: $30 CPA (likely closest to reality)
- For budget allocation and ROAS decisions, use AR CPA of $30

---

### Example: Multi-Campaign Performance Ranking

**Rank these 3 campaigns by AR ROAS (use only AR metrics):**

| Campaign | Google Revenue | Google Spend | Google ROAS | GA4 Revenue | GA4 ROAS | AR Revenue | AR ROAS |
|----------|---|---|---|---|---|---|---|
| Brand | $50,000 | $10,000 | 5.0× | $38,000 | 3.8× | $45,600 | 4.56× |
| Prospecting | $25,000 | $15,000 | 1.67× | $18,000 | 1.2× | $21,600 | 1.44× |
| Remarketing | $12,000 | $3,000 | 4.0× | $9,000 | 3.0× | $10,800 | 3.6× |

**Ranking by AR ROAS (best to worst):**
1. Brand: 4.56× AR ROAS
2. Remarketing: 3.6× AR ROAS
3. Prospecting: 1.44× AR ROAS

**Decision:** Scale Brand, maintain Remarketing, cut Prospecting.

---

## When to Use Each Metric

### Use AR Metrics For:
- **Budget allocation decisions** — "Should I increase this campaign's budget?"
- **Campaign verdicts** — "Is this campaign a WINNER, LOSER, or INCONCLUSIVE?"
- **Segmentation analysis** — "Is this keyword audience segment profitable?"
- **Waste calculations** — "How much am I wasting on dayparting/placements?"
- **Cannibalization scoring** — "Is this campaign hurting that campaign?"
- **ROI forecasting** — "If I double budget, what's my expected return?"

### Use GA4 True Metrics For:
- **Conservative projections** — "What's the worst-case ROAS?"
- **Tracking health baseline** — "How much did GA4 track relative to Google?"
- **Funnel analysis** — "Where do sessions drop off?"
- **Landing page performance** — "Which pages convert best?" (use GA4 native data)
- **Post-click behavior** — "How long do users stay on site?" (GA4 native)

### Use Google Ads Metrics For:
- **Discrepancy tracking** — "How much is Google over-reporting?"
- **Audit trails** — "What did Google say our performance was?"
- **Historical comparison** — "Has Google's over-reporting changed?"
- **NOT strategic decisions** — Never use Google metrics alone for budget decisions

---

## AR Multiplier Calibration

The default 1.2× multiplier is a reasonable estimate, but every account has unique tracking gaps. You can calibrate it to your actual data.

### How to Calibrate

**Step 1:** Get CRM/backend conversion data for a 30-day window.

Example: Your backend/CRM reports 500 purchases in February.

**Step 2:** Pull GA4 conversions for the same 30-day window, scoped to your Google Ads traffic.

Example: GA4 tracks 380 conversions from Google Ads in February.

**Step 3:** Calculate the actual multiplier.

```
Actual Multiplier = CRM Conversions / GA4 Conversions
                  = 500 / 380
                  = 1.32×
```

**Step 4:** Use this calibrated multiplier going forward.

```
AR_metric = GA4_metric × 1.32 (instead of 1.2×)
```

**Step 5:** Update `brand_config.ar_multiplier` and document the calibration.

---

## Why AR is Better Than Either Source Alone

### Problem with Google Ads Only
```
Campaign A AR CPA: $25 (Google reports)
Campaign B AR CPA: $30 (Google reports)

Decision: Scale Campaign A, cut Campaign B

Actual Reality (from CRM):
Campaign A actual conversions: 350 (not 400)
Campaign B actual conversions: 280 (not 250)

Corrected AR CPA:
Campaign A: $10,000 / (350 × 1.2) = $23.81 ✓ (close)
Campaign B: $10,000 / (280 × 1.2) = $29.76 ✓ (close)

Google metric alone was misleading on Campaign B.
```

### Problem with GA4 Only
```
Campaign A AR CPA: $35 (GA4 reports)
Campaign B AR CPA: $40 (GA4 reports)

Decision: Scale Campaign A, cut Campaign B

But Campaign B has lower CPM, better CTR, and better Quality Score.
The decision might be wrong if Campaign B has a tracking gap
(e.g., iOS conversion not tracked in GA4, but tracked in CRM).

AR CPA adjusts for this by lifting GA4 by 1.2×, giving you
a middle-ground estimate that's usually more accurate.
```

### The AR Sweet Spot
```
AR CPA = GA4 CPA × 1.2

This typically falls between Google's over-optimistic estimate
and GA4's over-pessimistic estimate, landing closest to reality.

Example:
Google CPA: $22
GA4 CPA: $36
AR CPA: $43 (GA4 × 1.2)
CRM actual: $42

AR is only $0.48 off actual.
Google was $20 too optimistic.
GA4 was $6 too pessimistic.
```

---

## Discrepancy Tracking

### The Discrepancy Metric

Calculate for every campaign:

```
Discrepancy % = (Google Conversions - GA4 Conversions) / Google Conversions × 100
```

**Interpretation:**
- 0-20%: Normal discrepancy (tracking working well, GA4 slightly under-tracking)
- 20-40%: Elevated discrepancy (some tracking issues or attribution model differences)
- >40%: Investigate (potential tracking failure, UTM issues, or consent blocking)

### What High Discrepancy Means

If Google reports 500 conversions but GA4 only tracks 300 (40% discrepancy), something is wrong:

1. **UTM parameters broken** — GA4 can't attribute sessions to Google Ads
2. **GCLID not passed** — GA4 can't link conversions to Google Ads
3. **Conversion tracking misconfigured** — Different conversion sources in Google Ads vs. GA4
4. **Consent/privacy blocks** — GA4 tracking rejected but Google tracking allowed
5. **Cross-device journeys** — GA4 only tracks single-device, Google attributes cross-device

### Discrepancy Investigation Flow

```
IF discrepancy > 40%:
  1. Check UTM parameters in GA4 — are sessionSource/sessionCampaignId set correctly?
  2. Check GCLID pass-through — is GCLID appearing in GA4 session data?
  3. Check conversion tracking source — is GA4 tracking same conversion as Google Ads?
  4. Check consent mode settings — are users rejecting GA4 tracking?
  5. Check iOS traffic levels — high iOS = expected higher discrepancy

  IF all checks pass:
    → Increase AR multiplier slightly (1.2 → 1.25 or higher)
    → Document in brand_config that discrepancy is expected

  IF issues found:
    → Fix tracking configuration
    → Re-run analysis after fix is deployed
```

---

## When AR Multiplier Needs Adjustment

### Reasons to Increase AR Multiplier (>1.2×)
- Heavy iOS traffic (Apple privacy features limit GA4 tracking)
- Consent-mode-only regions (EU with strict consent requirements)
- High ratio of mobile conversion to web tracking
- CRM data consistently shows higher conversions than AR predicts

### Reasons to Decrease AR Multiplier (<1.2×)
- Low discrepancy consistently (<15%)
- Perfect UTM implementation and GCLID pass-through
- CRM data consistently shows lower conversions than AR predicts
- GA4 tracking is over-counting (rare, but possible with misconfiguration)

### Recalibration Trigger Events
- Quarterly: Always recalibrate with latest 90-day CRM data
- Major tracking changes: New consent banner, new conversion pixel, new OS update affecting tracking
- Significant GA4 discrepancy shift: If discrepancy jumps from 20% to 35%, recalibrate

---

## Reporting Template: Triple-Source Presentation

When presenting metrics to stakeholders, always show all three sources:

```
Campaign Performance Summary
=============================

Campaign: Summer Sale Prospecting

Metrics:
  Google Ads Reported:
    - Conversions: 450
    - CPA: $22.22
    - ROAS: 4.5×

  GA4 Tracked (True):
    - Conversions: 280
    - CPA: $35.71
    - ROAS: 2.8×

  AR Estimated (Reality):
    - Conversions: 336 (280 × 1.2)
    - CPA: $29.76
    - ROAS: 3.36×

Recommendation: Use AR metrics for all decisions.
Discrepancy: 37.7% (Google over-reports by 37.7%)

Note: GA4 under-counts by ~20% due to tracking limitations.
AR multiplier (1.2×) is calibrated to account for typical tracking gaps.
For this account, actual conversions are expected to be close to AR estimate.
```

---

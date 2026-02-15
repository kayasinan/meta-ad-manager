# Triple-Source Metrics: Meta vs GA4 vs AR

## Overview

Every performance metric in the OpenClaw system exists in three versions, each telling a different story about your campaign performance. Understanding which to trust when is critical to making the right decisions.

## The Three Sources

### 1. Meta Metrics (Self-Reported)
**What it is:** Facebook's internal measurement of your campaigns. What you see in Ads Manager.

**Trust level:** LOW — Use for relative comparison only.

**Characteristics:**
- Over-counts conversions by 25-60% (varies by vertical and targeting)
- Includes both on-platform and off-platform conversions in its attribution model
- Uses multi-touch attribution (gives credit to multiple ads in the path)
- Includes "assisted conversions" that may not have actually led to a purchase
- Counts conversions within 1-click and 28-day windows

**Why it over-counts:**
- Browser fingerprinting (matches users without cookies)
- Cross-device attribution (assumes mobile user = desktop user based on patterns)
- Estimated conversions (uses ML to estimate conversions GA4 didn't track)
- Pixel firing on page but user never completing purchase (counts as conversion)

**When to use Meta metrics:**
- Relative performance comparison (Campaign A vs Campaign B within your account)
- Trend analysis (is performance improving week-over-week)
- Detection of major drops (if Meta metrics tank, something broke)
- Never for budget allocation or go/no-go decisions

**Example:** Meta reports 1,000 conversions at $25 CPA = $25,000 spend. But only 420 actual purchases happened.

---

### 2. GA4 True Metrics (GA4-Only)
**What it is:** Google Analytics' cookie-based tracking of user behavior on your website.

**Trust level:** MEDIUM — More accurate than Meta but inherently under-counts.

**Characteristics:**
- Under-counts conversions by ~20% (varies by device and consent settings)
- Only tracks users who accept cookies
- No cross-device attribution (Safari user on mobile ≠ Chrome user on desktop)
- No estimated conversions (only tracks events that fired)
- Attribution window: last-click only (the last ad they clicked gets all credit)
- Loses iOS users on Safari due to ITP (Intelligent Tracking Prevention)
- Loses users with ad blockers

**Why it under-counts:**
- iOS Safari blocking third-party cookies (ITP blocks Meta pixel on iOS Safari)
- Users rejecting cookie consent prompts
- Ad blockers preventing pixel firing
- Cross-device journeys (user clicks on mobile, converts on desktop — GA4 often misses this)
- First-party cookie loss due to browser updates

**When to use GA4 True metrics:**
- Conservative baseline for campaign performance
- Worst-case scenario planning
- Understanding actual site behavior (bounce rate, session duration, page paths)
- Absolute truth check when Meta metrics seem too good

**Example:** GA4 reports 420 conversions at $59.52 CPA = $25,000 spend. This is closer to reality but still under-counting iOS users.

---

### 3. AR Metrics (Assumed Real) — THE DECISION METRIC
**What it is:** GA4 conversions × 1.2 multiplier. The best estimate of actual reality.

**Trust level:** HIGH — Use this for all strategic decisions.

**Formula:**
```
AR CPA = Meta spend / (GA4 conversions × 1.2)
AR ROAS = (GA4 revenue × 1.2) / Meta spend
AR Conversion Rate = (GA4 conversions × 1.2) / GA4 sessions
```

**Interpretation:**
- Assumes GA4's 20% under-counting is the primary tracking gap
- Accounts for iOS tracking loss, consent loss, and ad blocker loss
- Default multiplier 1.2× calibrated against average client data
- Can be calibrated per account using CRM/backend conversion data

**When to use AR metrics:**
- ALL budget allocation decisions
- ALL campaign go/no-go verdicts
- Segment classification (WINNER/LOSER/INCONCLUSIVE)
- Cannibalization scoring
- Waste calculation
- ROAS target comparison

**Example:** AR CPA = $25,000 / (420 × 1.2) = $49.60. This is the number you use to say "campaign is profitable at $50 target CPA."

---

## Side-by-Side Comparison

```
Campaign X Performance:

Meta Metrics:
  - Conversions: 1,000
  - Spend: $25,000
  - Meta CPA: $25
  - Meta ROAS: 3.2×

GA4 True Metrics:
  - Conversions: 420
  - Revenue: $35,000
  - GA4 CPA: $59.52
  - GA4 ROAS: 1.4×

AR Metrics (GA4 × 1.2):
  - AR Conversions: 504 (420 × 1.2)
  - AR Revenue: $42,000 ($35,000 × 1.2)
  - AR CPA: $49.60
  - AR ROAS: 1.68×
```

**What this tells us:**
- Meta is over-reporting by 2.4× (1,000 / 420)
- GA4 is under-reporting by ~20% due to tracking gaps
- The true performance is somewhere between GA4 and AR
- Campaign is profitable at $50 CPA target (AR CPA $49.60 is just inside)
- Campaign ROAS is 1.68×, not 1.4× (GA4) or 3.2× (Meta)

---

## AR Multiplier Calibration

The default 1.2× multiplier works for most accounts, but can be calibrated to your specific tracking gaps.

### How to Calibrate

Compare GA4 conversions to backend/CRM conversions for a 30-90 day period:

```
New Multiplier = CRM Conversions / GA4 Conversions

Example:
CRM shows 500 actual purchases
GA4 shows 440 conversions
Multiplier = 500 / 440 = 1.136×

Use 1.14× going forward instead of 1.2×
```

### When Multiplier Needs Adjustment

- **iOS-heavy traffic:** Multiplier may be 1.25-1.35× (more tracking loss)
- **EU with strict consent:** Multiplier may be 1.3-1.5× (more consent rejection)
- **Gaming/VPN-heavy audience:** Multiplier may be 1.15-1.2× (less tracking loss)
- **First-party data integrated:** Multiplier may be 1.05-1.15× (less tracking loss)

### Recalibration Frequency

- **Quarterly:** Standard review cycle
- **After major tracking changes:** New consent banner, switch to consent mode, major browser update
- **After major iOS update:** Significant tracking loss changes
- **When targeting changes:** New geos, new device types, new audience sources

---

## Decision Rules by Metric

### Budget Allocation
**Use:** AR metrics
**Rule:** "Allocate budget to campaigns/segments with lowest AR CPA or highest AR ROAS."
- Campaign A: AR CPA $35 → GET BUDGET
- Campaign B: AR CPA $55 → CUT BUDGET
- Campaign C: AR CPA $50 (at target) → HOLD BUDGET

### Campaign Go/No-Go Verdict
**Use:** AR metrics
**Rule:** "Campaign verdict depends on AR ROAS vs account target."
- Target ROAS: 2.0×
- Campaign AR ROAS: 2.1× → KEEP
- Campaign AR ROAS: 1.8× → STOP
- Campaign AR ROAS: 1.95× → MONITOR (within margin)

### Segment Classification
**Use:** AR metrics
**Rule:** "WINNER = AR CPA < (average × 0.7). LOSER = AR CPA > (average × 1.5)."
- Account average AR CPA: $40
- Winner threshold: < $28
- Loser threshold: > $60

### Waste Calculation
**Use:** AR metrics
**Rule:** "Waste = (losing segment's wasted spend / total spend) × AR CPA saving opportunity"
- Losing segment AR CPA: $75
- Losing segment spend: $5,000
- Account average AR CPA: $40
- Potential waste: $5,000 / $40 = $125 opportunity cost

### Cannibalization Scoring
**Use:** AR metrics for performance comparison
**Rule:** "Campaign that survives = higher AR ROAS, lower AR CPA"
- Campaign A: AR CPA $38, AR ROAS 2.4×
- Campaign B: AR CPA $52, AR ROAS 1.8×
- Decision: Campaign A survives (better metrics), B's overlapping audience should be excluded from A

---

## Reporting All Three

Every performance report must show all three versions to provide full transparency:

### 6-Day Analysis Report
```
ACCOUNT SNAPSHOT — Performance Summary

Campaign A: Product Launch
  Meta Metrics:    1,240 conversions | $25,100 spend | $20.24 CPA | 3.95× ROAS
  GA4 True:          520 conversions | $25,100 spend | $48.27 CPA | 1.85× ROAS
  AR (Assumed Real):  624 conversions | $25,100 spend | $40.22 CPA | 2.22× ROAS

Verdict: STRONG PERFORMER (AR ROAS 2.22× vs 2.0× target)
```

### Segment Directive
```
PAUSE [ad set]: 'Men 55-64 Interest' in Campaign B

Metrics (Triple-Source):
  Meta:         847 spend | 28 conversions | $30.25 CPA
  GA4 True:     847 spend | 12 conversions | $70.58 CPA
  AR:           847 spend | 14 conversions | $58.79 CPA

Account Average AR CPA: $40
Decision Threshold: Loser > 1.5× average = > $60

Analysis: This segment's AR CPA ($58.79) is approaching loser threshold.
Combined with poor engagement metrics, recommend pause to prevent further waste.

Estimated Weekly Savings: $850
```

---

## Common Pitfalls

### Pitfall 1: Using Meta CPA for Go/No-Go Decisions
**Wrong:** "Campaign has $20 CPA, below $50 target, approve budget increase."
**Right:** "Campaign has $40 AR CPA, below $50 target, approve budget increase."

Meta's $20 is fiction. AR's $40 is reality.

---

### Pitfall 2: Dismissing GA4 as "Broken"
**Wrong:** "GA4 shows 50% lower conversions than Meta. GA4 is broken."
**Right:** "GA4 shows expected 20% under-count. That's normal tracking loss. AR adjustment accounts for it."

GA4 under-counting is expected and normal, not a sign of failure.

---

### Pitfall 3: Mixing Metrics in Reports
**Wrong:** "Campaign A has $25 CPA (Meta), Campaign B has $50 CPA (AR). Campaign A wins."
**Right:** "Campaign A AR CPA $40, Campaign B AR CPA $50. Campaign A wins."

Always use the same metric for comparison.

---

### Pitfall 4: Never Recalibrating AR Multiplier
**Wrong:** "Use 1.2× multiplier forever."
**Right:** "Recalibrate multiplier quarterly against CRM data. Adjust for tracking changes."

Your tracking gaps change. Update your multiplier to match.

---

## Summary

| Decision | Metric | Why |
|----------|--------|-----|
| Strategic direction | AR | Closest to reality |
| Conservative estimate | GA4 True | Worst-case scenario |
| Trend detection | Meta | Relative comparison |
| Waste quantification | AR | Accurate opportunity cost |
| Segment classification | AR | Reliable winner/loser identification |
| Campaign verdict | AR | Strategic decision making |

**Golden Rule:** If you're making a decision that affects budget or strategy, use AR metrics. Everything else is just context.

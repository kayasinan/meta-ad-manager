# Google Ads Landing Page Scoring Framework

## Scoring Methodology

Each landing page receives a composite score from 0-100 based on six metrics:

```
Overall Score = (35% × Conversion Rate Score) +
                (25% × Bounce Rate Score) +
                (20% × Session Duration Score) +
                (10% × Mobile Score) +
                (10% × Revenue Per Session Score)
```

---

## Metric 1: Conversion Rate (35% weight)

### Google Ads Search-Specific Thresholds

| Range | GOOD | WATCH | BAD |
|-------|------|-------|-----|
| E-commerce | >3% | 1-3% | <1% |
| Lead gen | >10% | 5-10% | <5% |
| Sign-ups | >5% | 2-5% | <2% |

**Calculation:**
```
CR Score = (Page Conv Rate / Account Avg Conv Rate) × 100

If page is 50% of account average:
  CR Score = 0.5 × 100 = 50/100 points
```

**Verdict impacts:**
- Page CR > 125% of account avg → KEEP
- Page CR 50-125% of account avg → FIX
- Page CR < 50% of account avg → KILL

---

## Metric 2: Bounce Rate (25% weight)

### Google Ads Search-Specific Thresholds

| Status | Bounce Rate | Score |
|--------|------------|-------|
| GOOD | <45% | 100 |
| WATCH | 45-65% | 50 |
| BAD | >65% | 0 |

**Bounce Rate Definition:** % of sessions with zero engagement events (no clicks, scrolls, form starts, etc.)

**Google Ads context:** Search traffic typically has 45-60% bounce rate baseline, so thresholds are slightly higher than Meta traffic.

---

## Metric 3: Session Duration (20% weight)

### Google Ads Search-Specific Thresholds

| Status | Duration | Score |
|--------|----------|-------|
| GOOD | >60 seconds | 100 |
| WATCH | 30-60 seconds | 50 |
| BAD | <30 seconds | 0 |

**Why:** Search users are typically action-oriented. >60s indicates engagement. <30s suggests page load failure or irrelevance.

---

## Metric 4: Mobile Experience (10% weight)

**Mobile-to-Desktop Gap:**
```
Gap = Desktop Conv Rate / Mobile Conv Rate

Score = max(0, min(100, 70 + (30 × Gap)))

If mobile and desktop are equal:
  Gap = 1.0
  Score = 100

If mobile is 50% of desktop:
  Gap = 2.0
  Score = 40
```

**Issues to flag:**
- Mobile bounce rate >60% (while desktop <40%) → mobile UX issue
- Mobile session duration <20s → page load issue
- Mobile CTR >2x desktop CTR but lower conversion → relevance issue

---

## Metric 5: Revenue Per Session (10% weight)

**Calculation:**
```
Rev Score = (Page RPS / Account Avg RPS) × 100

Account avg RPS = $5.20
Page RPS = $3.10

Rev Score = (3.10 / 5.20) × 100 = 59.6
```

**Why this matters:** A page with 2% CR at $50 AOV beats a page with 5% CR at $10 AOV (despite lower CR).

---

## Composite Scoring Examples

### Example 1: High-Performing Page

**Metrics:**
- Conv Rate: 4.2% (vs. 3% account avg) → 140% of avg → Score: 100
- Bounce Rate: 38% → Score: 100
- Session Duration: 95 seconds → Score: 100
- Mobile Score: 98 (mobile gap = 1.05) → Score: 98
- RPS: $5.80 (vs. $5.20 avg) → Score: 112 (capped at 100) → Score: 100

**Calculation:**
```
Score = (35% × 100) + (25% × 100) + (20% × 100) + (10% × 98) + (10% × 100)
      = 35 + 25 + 20 + 9.8 + 10
      = 99.8 → KEEP
```

### Example 2: Medium-Performing Page (Fix)

**Metrics:**
- Conv Rate: 1.8% (vs. 3% account avg) → 60% of avg → Score: 60
- Bounce Rate: 52% → Score: 50
- Session Duration: 48 seconds → Score: 50
- Mobile Score: 65 (mobile gap = 1.8) → Score: 65
- RPS: $3.50 (vs. $5.20 avg) → Score: 67

**Calculation:**
```
Score = (35% × 60) + (25% × 50) + (20% × 50) + (10% × 65) + (10% × 67)
      = 21 + 12.5 + 10 + 6.5 + 6.7
      = 56.7 → FIX
```

### Example 3: Low-Performing Page (Kill)

**Metrics:**
- Conv Rate: 0.6% (vs. 3% account avg) → 20% of avg → Score: 20
- Bounce Rate: 72% → Score: 0
- Session Duration: 18 seconds → Score: 0
- Mobile Score: 30 (mobile gap = 3.5) → Score: 30
- RPS: $1.20 (vs. $5.20 avg) → Score: 23

**Calculation:**
```
Score = (35% × 20) + (25% × 0) + (20% × 0) + (10% × 30) + (10% × 23)
      = 7 + 0 + 0 + 3 + 2.3
      = 12.3 → KILL
```

---

## Verdict Decision Tree

```
IF conversion_rate > 3% AND bounce_rate < 45% AND mobile_gap < 1.5
  → KEEP (high confidence)

ELSE IF conversion_rate < 1% OR bounce_rate > 65%
  → KILL (clear failure)

ELSE IF conversion_rate < 50% of account avg
  → KILL (underperforming)

ELSE IF mobile_gap > 2.0 (mobile is 50% of desktop CR)
  → FIX (mobile UX problem)

ELSE IF session_duration < 30 seconds AND bounce_rate > 50%
  → KILL (likely load issue)

ELSE
  → FIX (borderline, needs improvement)
```

---

## Emergency Conditions

### Ultra-Short Sessions (>20% of traffic <5 seconds)
**Indicates:** Page load failure or immediate bounce
**Action:** Emergency flag, urgent fix required
**Wasted spend:** `ultra-short % × daily spend on URL`

### Mobile Completely Broken (Mobile CR <30% of desktop)
**Indicates:** Mobile rendering bug or unresponsive design
**Action:** Fix or replace immediately
**Impact:** Mobile traffic represents ~60% of Google Ads, so major impact

### Zero Conversions Over 7 Days
**Indicates:** Page down or broken conversion tracking
**Action:** Emergency response, pause campaigns pointing to this URL
**Wasted spend:** 100% of daily spend on URL

---

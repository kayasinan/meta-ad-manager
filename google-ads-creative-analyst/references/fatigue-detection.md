# Creative Fatigue Detection for Google Ads

## Fatigue Definition

Creative fatigue occurs when an ad's performance declines due to:
- Audience wearout (users have seen it too many times)
- Message fatigue (message no longer resonates)
- CTR degradation (fewer clicks per impression)
- Conversion rate decline (users clicking but not converting)

## Fatigue Score Formula

```
Fatigue Score = (35% × CTR Decay) + (25% × Frequency Pressure) + (20% × Engagement Decline) + (10% × Age) + (10% × Conversion Decline)
```

### Component 1: CTR Decay (35% weight)

**Definition:** Percentage decline in CTR from the ad's peak to current.

**Calculation:**
```
CTR Decay % = (Peak 7d CTR - Current 7d CTR) / Peak 7d CTR × 100

Example:
  Peak 7d CTR: 2.5%
  Current 7d CTR: 1.2%
  Decay: (2.5 - 1.2) / 2.5 × 100 = 52%
```

**Fatigue Threshold:** >35% decay = strong fatigue signal

### Component 2: Frequency Pressure (25% weight)

**Definition:** Increase in ad frequency (views per user) over time.

**Calculation:**
```
Frequency Pressure % = (Current 7d Frequency - 7-14d Avg Frequency) / (7-14d Avg Frequency) × 100

Example:
  7-14d Avg Frequency: 2.1
  Current 7d Frequency: 2.8
  Pressure: (2.8 - 2.1) / 2.1 × 100 = 33%
```

**Fatigue Threshold:** >25% frequency increase = audience wearout signal

### Component 3: Engagement Decline (20% weight)

**Definition:** Decline in engagement rate (clicks or interactions) per impression.

**Calculation:**
```
Engagement Decline % = (7-14d Engagement - Current 7d Engagement) / (7-14d Engagement) × 100

Example:
  7-14d Avg Engagement: 4.2%
  Current 7d Engagement: 3.1%
  Decline: (4.2 - 3.1) / 4.2 × 100 = 26%
```

**Fatigue Threshold:** >20% decline = message wearout signal

### Component 4: Age (10% weight)

**Definition:** Days the ad has been active.

**Calculation:**
```
Age Score = min(Days Active / 30, 1.0)

Example:
  Days Active: 45
  Age Score: min(45/30, 1.0) = 1.0 (maximum)
```

**Fatigue Threshold:** 30+ days = old ad, assign full age credit

### Component 5: Conversion Decline (10% weight)

**Definition:** Decline in conversion rate compared to historical average.

**Calculation:**
```
Conversion Decline % = (Historical Avg Conv Rate - Current 7d Conv Rate) / Historical Avg Conv Rate × 100

Example:
  Historical Conv Rate: 3.2%
  Current 7d Conv Rate: 2.6%
  Decline: (3.2 - 2.6) / 3.2 × 100 = 19%
```

**Fatigue Threshold:** >10% decline = conversion message fatigue

---

## Fatigue Score Interpretation

### 0-30: FRESH
**Status:** Ad performing well, no rotation needed
**Action:** Continue running, monitor weekly
**Expected:** Maintain performance level

### 31-60: AGING
**Status:** Ad showing signs of wearout, performance declining
**Action:** Monitor closely, prepare replacement
**Expected:** Prepare rotation plan within 1 week

### 61-80: FATIGUED
**Status:** Ad clearly fatigued, performance degraded
**Action:** Rotation recommended
**Expected:** Pause and add new ad within 3-5 days

### 81-100: DEAD
**Status:** Ad heavily fatigued, performance terrible
**Action:** Pause immediately
**Expected:** Remove from rotation immediately

---

## Fatigue Score Calculation Example

**Ad #4821: "Buy Blue Shoes Today"**

**Current metrics (last 7 days):**
- Impressions: 45,000
- Clicks: 1,125 (CTR: 2.5%)
- Conversions: 28
- Frequency: 2.8 times

**Historical baseline (previous 30 days):**
- Peak 7d CTR: 3.8%
- 7-14d Avg Frequency: 2.1
- 7-14d Avg Engagement: 4.2%
- Avg Conv Rate: 3.1%
- Days Active: 42

**Calculation:**

1. **CTR Decay:** (3.8 - 2.5) / 3.8 × 100 = 34.2%
   - Score component: 34.2% × 35% = 11.97

2. **Frequency Pressure:** (2.8 - 2.1) / 2.1 × 100 = 33.3%
   - Score component: 33.3% × 25% = 8.33

3. **Engagement Decline:** (4.2 - 2.5) / 4.2 × 100 = 40.5% (using CTR as proxy)
   - Score component: 40.5% × 20% = 8.10

4. **Age:** min(42/30, 1.0) = 1.0
   - Score component: 1.0 × 10% = 10.0

5. **Conversion Decline:** (3.1 - 2.5) / 3.1 × 100 = 19.4%
   - Score component: 19.4% × 10% = 1.94

**Total Fatigue Score:** 11.97 + 8.33 + 8.10 + 10.0 + 1.94 = **40.3**

**Status:** AGING (31-60 range)
**Action:** Monitor closely, prepare replacement within 1 week
**Recommendation:** "Ad #4821 showing early fatigue. CTR down 34% from peak. Prepare rotation plan for next 5 days."

---

## Reporting Format

```
Creative Fatigue Analysis
==========================

Ad #4821 (Buy Blue Shoes Today)
  Fatigue Score: 40.3 (AGING)

  Components:
    - CTR Decay: 34.2% (moderate)
    - Frequency Pressure: 33.3% (moderate)
    - Engagement Decline: 40.5% (high)
    - Age: 42 days (high)
    - Conversion Decline: 19.4% (moderate)

  Trend: Declining over past 2 weeks
  Recommendation: Prepare rotation plan for next 5 days

Ad #4822 (Blue Shoes on Sale - Limited Time!)
  Fatigue Score: 68.5 (FATIGUED)

  Components:
    - CTR Decay: 52.1% (critical)
    - Frequency Pressure: 45.0% (high)
    - Engagement Decline: 58.3% (critical)
    - Age: 52 days (maximum)
    - Conversion Decline: 31.2% (high)

  Trend: Steep decline over past week
  Recommendation: Pause and rotate with new ad immediately

Action Items (Priority Order):
  1. Pause Ad #4822 today — rotate with new creative
  2. Prepare replacement for Ad #4821 — deploy within 5 days
  3. Monitor Ads #4820, #4823 (fatigue scores 52, 48) — may need rotation in 7 days
```

---

## Prevention Strategy

### Early Detection
- Run fatigue analysis every 2-3 days for ads in rotation
- Flag ads reaching 50+ fatigue score for immediate review
- Track fatigue trends weekly (is score increasing?)

### Proactive Rotation
- Plan creative rotation before fatigue reaches 70
- Have replacement ads ready before pausing fatigued ads
- Stagger rotation to avoid learning phase impacts

### Ad Group Diversity
- Maintain 4-8 active ads per ad group
- Test new creatives continuously (don't wait for existing ads to fatigue)
- Use top-performing ads as the baseline for new variants

---

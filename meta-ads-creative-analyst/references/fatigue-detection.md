# Creative Fatigue Detection Guide

## Overview

Creative fatigue is when an ad stops performing because the audience has seen it too many times. The algorithm deprioritizes it, costs rise, and conversions drop. Your job is to detect fatigue early and flag ads for rotation before they become expensive wastes of money.

## The 5 Fatigue Signals

Fatigue score = weighted combination of 5 signals:

### Signal 1: CTR Decline (35% weight)
**What it measures:** Are fewer people clicking compared to when the ad was fresh?

**How to calculate:**
```
CTR Decay = (Peak CTR - Current CTR) / Peak CTR × 100

Peak CTR = highest CTR the ad achieved (usually day 1-5)
Current CTR = latest CTR (last 24-48 hours)

Fatigue component = CTR Decay × 0.35
```

**Interpretation:**
- <10% decay = healthy, not fatigued
- 20-40% decay = early warning sign
- 40%+ decay = fatigued, recommend pause

**Example:**
- Ad started with 2.1% CTR (peak)
- Today: 1.3% CTR (current)
- Decay: (2.1 - 1.3) / 2.1 × 100 = 38%
- Fatigue component: 38 × 0.35 = 13.3 points

---

### Signal 2: Frequency Pressure (25% weight)
**What it measures:** How many times has the average user seen this ad?

**How to calculate:**
```
Frequency Pressure = Current Frequency / Fatigue Threshold × 100

Fatigue Threshold = 2.5 (average; varies by vertical: 2.0-3.5)
Current Frequency = current average frequency from Meta API

Fatigue component = Frequency Pressure × 0.25
```

**Interpretation:**
- Frequency <1.5 = healthy, fresh audience
- Frequency 1.5-2.5 = normal range
- Frequency >2.5 = audience saturation beginning
- Frequency >3.0 = definitely fatigued

**Example:**
- Meta reports average frequency = 2.8
- Fatigue threshold = 2.5
- Pressure: (2.8 / 2.5) × 100 = 112%
- Fatigue component: 112 × 0.25 = 28 points

---

### Signal 3: Engagement Decline (20% weight)
**What it measures:** Are people interacting less with the ad (comments, shares, saves)?

**How to calculate:**
```
Engagement Rate = (reactions + comments + shares + saves) / impressions × 100

Engagement Decline = (Peak Engagement Rate - Current Engagement Rate) / Peak Engagement Rate × 100

Fatigue component = Engagement Decline × 0.20
```

**Interpretation:**
- <10% decline = healthy
- 20-30% decline = early warning
- 30%+ decline = fatigued

**Example:**
- Peak engagement rate: 1.8%
- Current engagement rate: 1.2%
- Decline: (1.8 - 1.2) / 1.8 × 100 = 33%
- Fatigue component: 33 × 0.20 = 6.6 points

---

### Signal 4: Ad Age (10% weight)
**What it measures:** How long has the ad been running?

**How to calculate:**
```
Days Running = Current Date - Launch Date

Age Score = Days Running / Average Fatigue Lifecycle × 100

Average Fatigue Lifecycle = 28 days (varies: 14-45 days by vertical)

Fatigue component = Age Score × 0.10 (capped at 10)
```

**Interpretation:**
- <14 days = too early to fatigue
- 14-28 days = normal lifecycle window
- >28 days = approaching end of life
- >45 days = nearly always fatigued

**Example:**
- Ad launched: Jan 15
- Today: Feb 15 (31 days)
- Average lifecycle: 28 days
- Age score: 31 / 28 × 100 = 110%
- Fatigue component: min(110 × 0.10, 10) = 10 points

---

### Signal 5: Conversion Rate Decline (10% weight)
**What it measures:** Are fewer visitors converting?

**How to calculate:**
```
Conversion Rate Decline = (Peak Conversion Rate - Current Conversion Rate) / Peak Conversion Rate × 100

Peak Conversion Rate = highest conversion rate (usually first 7 days)
Current Conversion Rate = latest conversion rate

Fatigue component = Conversion Rate Decline × 0.10
```

**Interpretation:**
- <15% decline = still converting
- 20-40% decline = starting to underperform
- 40%+ decline = fatigued for sure

**Example:**
- Peak conversion rate: 4.2%
- Current conversion rate: 2.8%
- Decline: (4.2 - 2.8) / 4.2 × 100 = 33%
- Fatigue component: 33 × 0.10 = 3.3 points

---

## Fatigue Score Formula

```
Total Fatigue Score = Signal 1 + Signal 2 + Signal 3 + Signal 4 + Signal 5

Total = CTR Decline (35%) + Frequency (25%) + Engagement (20%) + Age (10%) + Conversion (10%)

Score Range: 0-100
```

### Score Interpretation

| Score | Status | Action |
|-------|--------|--------|
| 0-20 | Fresh | Keep running, monitor |
| 21-40 | Healthy | Monitor closely, prepare replacement |
| 41-60 | Early Fatigue | Start rotation planning, build replacement ads |
| 61-75 | Fatigued | PAUSE ad, add replacement immediately |
| 76-100 | Severely Fatigued | PAUSE immediately, this is wasting budget |

---

## Fatigue Thresholds by Vertical

Different verticals have different fatigue patterns. Adjust your thresholds:

### E-Commerce (Fashion, Home)
- **Fatigue threshold (days):** 18-21
- **Fatigue frequency:** 2.0-2.3
- **Typical fatigue score:** Reaches 60+ by day 20

**Why:** Visual-heavy, high saturation, fast decay

### SaaS / B2B
- **Fatigue threshold (days):** 30-40
- **Fatigue frequency:** 2.5-3.0
- **Typical fatigue score:** Reaches 60+ by day 35

**Why:** Longer decision cycle, smaller audience, slower saturation

### Health & Wellness
- **Fatigue threshold (days):** 25-28
- **Fatigue frequency:** 2.2-2.5
- **Typical fatigue score:** Reaches 60+ by day 26

**Why:** Emotional/lifestyle content; moderate saturation

### Lead Generation
- **Fatigue threshold (days):** 14-18
- **Fatigue frequency:** 1.8-2.2
- **Typical fatigue score:** Reaches 60+ by day 16

**Why:** Small qualified audience, fast saturation, high frequency burns audience quickly

---

## Early Warning Signs (Before Score Hits 60)

### Week 1-2 (Days 1-14)
- **Healthy indicators:** Frequency <1.5, CTR stable or slightly declining (<5%)
- **Warning sign:** CTR declining >10% by day 7
- **Action:** Note pattern, prepare backup creative

### Week 2-3 (Days 14-21)
- **Healthy indicators:** Frequency 1.5-2.0, CTR decline <20%
- **Warning sign:** Frequency 2.0+, CTR decline >20%
- **Action:** Start building replacement ad, plan rotation date

### Week 3-4 (Days 21-28)
- **Healthy indicators:** Frequency <2.3, CTR decline <30%
- **Warning sign:** Frequency 2.3+, CTR decline >30%
- **Action:** Replacement ad ready, schedule pause in next 3-5 days

### Week 4+ (Days 28+)
- **Healthy indicators:** Rare; most ads fatigued by now
- **Warning sign:** Frequency 2.5+, CTR decline >35%
- **Action:** PAUSE immediately

---

## What Happens When Fatigue Hits

### Performance Degradation Curve
```
Day 0-5:   Peak performance (highest CTR, CR, ROAS)
Day 5-14:  Gradual decline (10-15% loss)
Day 14-21: Accelerated decline (20-35% loss)
Day 21-28: Steep decline (35-50% loss)
Day 28+:   Cliff (50%+ loss, CPA doubles)
```

### Why It Happens
1. **Impression saturation:** Audience sees ad repeatedly
2. **Algorithm deprioritization:** Meta's algorithm detects repeated impressions to same user, lowers priority
3. **Declining engagement:** Fewer clicks from remaining unsaturated audience
4. **Higher CPMs:** Algorithm charges more for impression fatigue
5. **Conversion decline:** Remaining audience may be lower-intent

---

## Rotation Strategy

### When to Build Replacement
- **Timing:** When fatigue score reaches 40-50
- **Number of replacements:** 2-3 new ads per fatigued ad
- **Source:** Use Replication Blueprint from Creative Analyst to build variants

### When to Pause Fatigued Ad
- **Timing:** When fatigue score reaches 60+
- **Action level:** AD-level (not ad set)
- **Message to Campaign Creator:** "PAUSE [ad]: Ad #XXXX in ad set Y — fatigue score 72. Add replacement to same ad set (no learning reset)."
- **Impact:** No learning phase reset (you're not pausing the ad set, just rotating within it)

### Pause Strategy
- **Good:** Pause individual ad, keep ad set active, add 2-3 fresh ads to same ad set
- **Bad:** Pause entire ad set (triggers learning phase reset)
- **Very bad:** Let fatigued ad keep running (bleeds budget)

---

## Monitoring Checkpoints

### Daily (Automated)
- Calculate fatigue score for all active ads
- Alert if any ad crosses 60 threshold
- Monitor frequency trend

### 3x Per Week
- Review CTR trends for all top-performing ads
- Identify ads approaching 40-50 fatigue
- Ensure replacement pipeline is full

### Weekly (Manual)
- Review fatigue lifecycle trends
- Update average fatigue threshold per campaign
- Plan rotation schedule for next week

---

## Example Fatigue Progression

**Ad: "Women 25-34 Lifestyle Video"**

| Date | Days | CTR | Freq | Engagement | Signal 1 | Signal 2 | Signal 3 | Signal 4 | Signal 5 | Total Score | Status |
|------|------|-----|------|------------|----------|----------|----------|----------|----------|-------------|---------|
| Jan 15 | 0 | 2.0% | 1.1 | 1.6% | 0 | 0 | 0 | 0 | 0 | 0 | Fresh |
| Jan 19 | 4 | 1.9% | 1.3 | 1.5% | 5 | 2 | 2 | 1 | 1 | 11 | Healthy |
| Jan 22 | 7 | 1.7% | 1.6 | 1.3% | 15 | 6 | 8 | 2 | 5 | 36 | Healthy |
| Jan 25 | 10 | 1.5% | 1.9 | 1.1% | 25 | 15 | 15 | 3 | 10 | 68 | **FATIGUED** |
| Jan 28 | 13 | 1.2% | 2.3 | 0.9% | 40 | 22 | 20 | 5 | 15 | 102 | **Severely Fatigued** |

**Action taken on Jan 25:** PAUSE ad, add 2 fresh ads to same ad set

---

## Special Cases

### Seasonal Products
- Fatigue threshold = shorter (10-14 days)
- High frequency tolerance = lower (1.8)
- Strategy: Rotate constantly during season, retire after

### Evergreen Products
- Fatigue threshold = longer (35-45 days)
- Audience = larger, slower saturation
- Strategy: Fewer rotations needed, focus on winning patterns

### Video vs. Static
- Video fatigue = slower (35-40 days)
- Static image fatigue = faster (18-21 days)
- Strategy: Longer lifecycle for video, weekly rotation for static

### Broad Targeting vs. Narrow
- Broad targeting = slower fatigue (larger audience)
- Narrow targeting (LAL, lookalike) = faster fatigue (smaller audience)
- Strategy: Adjust rotation frequency by audience size

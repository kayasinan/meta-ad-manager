# Google Ads Auction Insights Analysis

## Overview

Google Ads Auction Insights are competitive positioning metrics available for Search campaigns. They show how your ads perform relative to competitors in the same auctions.

**Note:** Auction Insights are available ONLY for Search campaigns, NOT for Display, Video, Shopping, or Performance Max.

---

## Metrics Explained

### 1. Impression Share (Is)
**Definition:** Your % of total impressions in auctions where your keywords appeared

```
Your IS = Your impressions / (Your impressions + Competitor impressions)

Example:
  You got 100 impressions
  Competitor A got 150 impressions
  Competitor B got 200 impressions

  Total eligible impressions = 100 + 150 + 200 = 450
  Your IS = 100 / 450 = 22.2%
```

**Interpretation:**
- >50%: You're winning the majority of auctions
- 25-50%: Competitive market, you're holding your own
- <25%: You're significantly losing share

### 2. Overlap Rate (OR)
**Definition:** % of your impressions where a specific competitor also received an impression (in the same auction)

```
OR = Overlapping impressions / Your impressions

Example:
  You got 100 impressions total
  Competitor A appeared in 75 of those auctions

  Overlap Rate = 75 / 100 = 75%
```

**Interpretation:**
- >80%: You're competing directly with this competitor in almost all auctions
- 50-80%: Significant overlap, direct competition
- <50%: Limited overlap, targeting different keywords/users

### 3. Outranking Share (ORS)
**Definition:** % of overlapping impressions where YOUR ads ranked higher than competitor

```
ORS = (Overlapping impressions where you ranked higher) / Overlapping impressions

Example:
  You and Competitor A overlapped in 75 impressions
  You ranked higher in 60 of those

  ORS = 60 / 75 = 80%
```

**Interpretation:**
- >50%: You're winning the competitive head-to-head
- ~50%: Evenly matched
- <50%: Competitor usually outranks you

### 4. Absolute Top of Page Rate (ATP)
**Definition:** % of your impressions where your ad appeared in the absolute top position (above organic results)

```
Example:
  You got 100 impressions
  Your ad appeared at absolute top in 45 of those

  ATP = 45 / 100 = 45%
```

**Interpretation:**
- >40%: Strong position
- 20-40%: Middle position
- <20%: Usually appears below top ads

### 5. Top of Page Rate (TOP)
**Definition:** % of your impressions appearing anywhere in the top section (above organic results)

```
Example:
  You got 100 impressions
  Your ad appeared in top section in 75 of those

  TOP = 75 / 100 = 75%
```

---

## Competitive Analysis Framework

### Step 1: Identify Key Competitors in Auction Insights

For each competitor where Overlap Rate >50%:
- High overlap = direct competition
- Worth monitoring and analyzing

### Step 2: Calculate Competitive Win/Loss Rate

```
Win/Loss = Outranking Share %

If ORS = 65%:
  You're winning 65% of head-to-head matchups
  Competitor is winning 35% of head-to-head matchups
```

**Trend analysis:**
- ORS increasing over time → you're gaining position
- ORS decreasing over time → competitor gaining position

### Step 3: Impression Share Analysis

```
IS tells you the total share of market
ORS tells you the quality of competition

Example Scenario A:
  Your IS = 30% (losing 70% of market)
  ORS vs Comp A = 75% (you beat them 75% of the time)

  Interpretation: You're losing to other competitors, not to Comp A
  Action: Analyze Comp B, C (not A)

Example Scenario B:
  Your IS = 30% (losing 70% of market)
  ORS vs Comp A = 20% (they beat you 80% of the time)

  Interpretation: You're losing heavily to Comp A
  Action: Improve Quality Score, bid higher, improve ad relevance
```

---

## Competitive Positioning Scorecard

For each competitor with Overlap >50%:

| Metric | You | Competitor | Winner |
|--------|-----|-----------|--------|
| Impression Share | 32% | 28% | You |
| Overlap Rate | 60% | 60% | Tie |
| Outranking Share | 72% | 28% | You |
| Avg Position | 2.1 | 2.8 | You |

**Overall Assessment:** You're outcompeting this competitor in direct matchups (72% ORS) despite lower total market share. Focus on capturing the 28% you're losing to this competitor (bid/quality optimization) and on larger competitors.

---

## Threat Identification

### Threat Level: HIGH
**Triggers:**
- Overlap Rate >75%
- Outranking Share <40% (they beat you >60% of the time)
- Trend: ORS declining month-over-month

**Action:**
1. Analyze their ads: copy, landing pages, quality score
2. Improve your Quality Score components
3. Consider bid increase for shared keywords
4. A/B test ad copy against their approach

### Threat Level: MEDIUM
**Triggers:**
- Overlap Rate 50-75%
- Outranking Share 40-60% (evenly matched)
- Trend: ORS stable

**Action:**
1. Monitor quarterly
2. Maintain current bid/quality
3. Test new messaging to differentiate

### Threat Level: LOW
**Triggers:**
- Overlap Rate <50%
- Outranking Share >60% (you beat them)
- Trend: ORS improving

**Action:**
1. Maintain current strategy
2. Continue investing where you're winning

---

## Trend Analysis

### Quarterly Comparison

Track Outranking Share quarter-over-quarter:

```
Q4 2025: ORS vs CompA = 62%
Q1 2026: ORS vs CompA = 58%
Q2 2026: ORS vs CompA = 54% (projected)

Trend: Declining
Interpretation: Competitor A gaining position
Action: Investigate why (better ads? higher bids? better quality score?)
```

---

## Reporting Template

```
Auction Insights Competitive Analysis
=====================================

Campaign: Search - Branded Keywords
Analysis Period: Feb 8-14, 2026

Your Performance:
  - Impression Share: 42%
  - Avg Position: 1.8
  - Absolute Top Rate: 68%

Top Competitors:

  Competitor: CompetitorA
    - Your IS: 42%, Their IS: 38%
    - Overlap Rate: 72%
    - Outranking Share: 78% (YOU WIN)
    - Trend: Stable
    - Threat Level: LOW

  Competitor: CompetitorB
    - Your IS: 42%, Their IS: 51%
    - Overlap Rate: 68%
    - Outranking Share: 35% (THEY WIN)
    - Trend: Declining (you were 42% last month)
    - Threat Level: HIGH

  Competitor: CompetitorC
    - Your IS: 42%, Their IS: 25%
    - Overlap Rate: 41%
    - Outranking Share: 91% (YOU WIN)
    - Trend: Improving
    - Threat Level: NONE

Key Insights:
  1. You dominate branded search (68% absolute top rate)
  2. CompetitorB is gaining ground — investigate their strategy
  3. CompetitorA is weaker — maintain position
  4. CompetitorC is not a direct threat

Recommendations:
  1. Analyze CompetitorB's ads and quality score
  2. Increase bid on CompetitorB overlap keywords by 10%
  3. Improve Quality Score on CompetitorB matchups
```

---

# Alert Thresholds & Monitoring Criteria for Google Ads

Real-time thresholds for generating alerts and recommendations during daily monitoring. Customize based on brand_config.

---

## Performance Thresholds

### CPA (Cost Per Acquisition)

| Threshold | Severity | Condition | Action |
|-----------|----------|-----------|--------|
| AR CPA > target + 20% | WARNING | Underperforming significantly | Review targeting, landing pages, audience |
| AR CPA > target + 30% | CRITICAL | Major underperformance | Recommend pause if sustained 7+ days |
| AR CPA trending ↑ for 7 days | WARNING | Worsening performance | Investigate cause (funnel issue, auction) |
| AR CPA trending ↓ for 7 days | INFO | Improving performance | Note positive trend, monitor |

**Example:**
- Target CPA: $30
- Current AR CPA: $35 (16% over) → Monitor closely
- Current AR CPA: $40 (33% over) → WARNING alert
- Current AR CPA: $45 (50% over) → CRITICAL alert

### ROAS (Return On Ad Spend)

| Threshold | Severity | Condition | Action |
|-----------|----------|-----------|--------|
| AR ROAS < target - 20% | WARNING | Underperforming | Review conversion value tracking, landing pages |
| AR ROAS < min_acceptable_ar_roas for 7+ days | CRITICAL | Below acceptable floor | Recommend pause |
| AR ROAS < 1.0 | CRITICAL | Losing money | Immediate review recommended |
| AR ROAS trending ↑ for 7 days | INFO | Improving performance | Continue monitoring |
| AR ROAS > target + 30% | INFO | Exceeding expectations | Candidate for budget scaling |

**Example:**
- Target ROAS: 2.0x
- Min acceptable ROAS: 1.5x
- Current AR ROAS: 1.8x (10% below target) → Monitor
- Current AR ROAS: 1.5x (25% below target) → WARNING
- Current AR ROAS: 1.2x (40% below target) → CRITICAL
- Current AR ROAS: 0.8x (losing money) → CRITICAL ALERT

---

## Budget & Spend Alerts

### Daily Spend Pacing

| Threshold | Severity | Condition | Action |
|-----------|----------|-----------|--------|
| Daily spend 85-100% of budget | INFO | On pace | Continue monitoring |
| Daily spend 70-85% of budget for 1 day | INFO | Slight underspend | Monitor for pattern |
| Daily spend <70% of budget for 3+ days | WARNING | Significant underspend | Investigate: Low impression volume, targeting issue |
| Daily spend >110% of budget | CRITICAL | Budget cap exceeded | Investigate: Bid inflation, budget overflow |
| Daily spend 95-110% of budget, positive ROAS | INFO | At capacity, profitable | Candidate for budget increase |

**Example:**
- Daily budget: $250
- Today's spend: $212 (85% of budget) ✅ On pace
- Today's spend: $160 (64% of budget) for 3+ days ⚠️ WARNING (underspend pattern)
- Today's spend: $280 (112% of budget) 🔴 CRITICAL (overspend, exceeds daily budget)
- Today's spend: $237 (95% of budget), ROAS 2.5x 📈 Consider budget increase

---

## Quality Score Alerts (Google Search Only)

### Quality Score Components

| Component | Threshold | Severity | Action |
|-----------|-----------|----------|--------|
| Ad Relevance: Above Avg → Avg | WARNING | Quality decline | Review ad copy, improve relevance |
| Ad Relevance: Avg → Below Avg | CRITICAL | Significant decline | Revise ad copy immediately |
| Landing Page Exp: Above Avg → Avg | WARNING | Page experience declining | Check page load speed, mobile usability |
| Landing Page Exp: Avg → Below Avg | CRITICAL | Major decline | Review page content, technical performance |
| Expected CTR: Above Avg → Avg | WARNING | CTR declining | May indicate creative fatigue |
| Expected CTR: Avg → Below Avg | CRITICAL | Major CTR decline | Rotate creatives, refresh messaging |

### Overall Quality Score

| QS Level | Threshold | Severity | Action |
|----------|-----------|----------|--------|
| QS 8-10 | Healthy | INFO | Maintain current approach |
| QS 6-7 | Moderate | INFO | Monitor, consider improvements |
| QS 5-6 | Below avg | WARNING | Investigate components, plan improvements |
| QS 1-4 | Poor | CRITICAL | Immediate action: review all components |
| QS drop >2 points in 1 week | WARNING | Rapid decline | Investigate cause quickly |
| Multiple ads with QS <5 | CRITICAL | Campaign quality issues | Review entire campaign structure |

**Example:**
- Ad QS: 8 ✅ Healthy
- Ad QS: 6 ⚠️ Monitor, slight issues
- Ad QS: 4 🔴 CRITICAL, needs immediate fix
- Ad QS dropped from 8 → 5 in one week ⚠️ WARNING, investigate

---

## Impression Share Alerts (Google Search Only)

### Impression Share Metrics

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Imp Share 70%+ | Healthy | INFO | Good visibility |
| Imp Share 50-70% | Moderate | INFO | Acceptable, monitor |
| Imp Share <50% | WARNING | Below target | Bid up or improve quality |
| Imp Share <30% | CRITICAL | Severely limited visibility | Major action needed |
| IS Lost to Budget >15% | WARNING | Budget limiting visibility | Consider budget increase |
| IS Lost to Rank >15% | WARNING | Quality/bid issues | Increase bids or improve QS |
| IS Lost to Budget >30% | CRITICAL | Budget severely limiting | Urgent: increase budget or bid strategy issue |

### Branded Keywords (special case)

| Threshold | Severity | Action |
|-----------|----------|--------|
| IS <80% on branded terms | WARNING | Competitors bidding on brand, visibility loss |
| IS <50% on branded terms | CRITICAL | Critical visibility loss on own brand |

**Example:**
- Campaign impression share: 72% ✅ Good
- Campaign impression share: 45% ⚠️ Monitor, consider optimization
- Branded keyword impression share: 42% 🔴 CRITICAL, competitors outbidding
- IS Lost to Budget: 18% for 3 days ⚠️ WARNING, budget constraint

---

## Smart Bidding & Learning Phase Alerts

### Learning Phase Status

| Condition | Severity | Action |
|-----------|----------|--------|
| Campaign in Learning phase, <7 days old | INFO | Expected, monitor data accumulation |
| Campaign in Learning >14 days, <50 conversions | WARNING | Slow learning, may need data increase |
| Campaign in Learning >21 days | CRITICAL | Stuck, insufficient conversion data or issue |
| Campaign in Learning >30 days | CRITICAL | Major issue, recommend pause and review |
| 7+ day trend: conversions decreasing | WARNING | Learning may be regressing, investigate |
| Campaign ramped up (exited Learning), stable | INFO | Smart bidding optimized, monitor ROAS |

### Conversion Data Sufficiency

| Threshold | Severity | Action |
|-----------|----------|--------|
| >20 conversions in past 7 days | Healthy | Algorithm has good data |
| 15-20 conversions in past 7 days | Moderate | Acceptable, monitor |
| 10-15 conversions in past 7 days | WARNING | Limited data, learning slower |
| <10 conversions in past 7 days | CRITICAL | Insufficient data, consider: Expand audience, increase budget, review tracking |
| Zero conversions in 3+ days | CRITICAL | Data drought, urgent review |

**Example:**
- Campaign age: 8 days, conversions: 25, status: Learning 📊 Expected
- Campaign age: 25 days, conversions: 8, status: Still Learning 🔴 CRITICAL (stuck, too slow)
- Campaign age: 30 days, conversions: 35+, status: Learning ✅ Healthy, normal phase
- Campaign age: 35 days, status: Ramped up (Learning complete) ✅ Success

---

## Creative Fatigue Alerts

### CTR (Click-Through Rate) Decline

| Threshold | Severity | Action |
|-----------|----------|--------|
| CTR baseline established (first 2 weeks) | - | Use as reference for fatigue detection |
| CTR decline 10-20% vs. baseline | INFO | Early fatigue signal, monitor |
| CTR decline 20-30% vs. baseline | WARNING | Fatigue present, plan rotation |
| CTR decline >30% vs. baseline | WARNING | Significant fatigue, rotate ASAP |
| CTR declining for 7+ consecutive days | WARNING | Sustained decline, rotate creatives |
| CTR increasing for 7+ consecutive days | INFO | Creative performing well, maintain |

### Impression Frequency (Audience Fatigue)

| Threshold | Severity | Action |
|-----------|----------|--------|
| Avg freq <2 per user in 30 days | INFO | Low frequency, audience not exhausted |
| Avg freq 2-4 per user in 30 days | INFO | Healthy frequency |
| Avg freq 4-6 per user in 30 days | WARNING | Moderate fatigue risk, monitor |
| Avg freq >6 per user in 30 days | WARNING | High frequency, audience fatiguing, consider expand or cap |
| Avg freq >10 per user in 30 days | CRITICAL | Extreme frequency, audience exhausted, expand audience |

### Ad Age & Performance

| Threshold | Severity | Action |
|-----------|----------|--------|
| Ad running 0-30 days | INFO | Fresh, expect good performance |
| Ad running 30-60 days, CTR stable | INFO | Still performing, maintain |
| Ad running >60 days | WARNING | Consider rotation, even if performing (freshness) |
| Ad running >90 days, CTR declining | CRITICAL | Definitely rotate, fatigue evident |

**Example:**
- Ad baseline CTR: 5%, current CTR: 4.2% (16% decline) ⚠️ Early fatigue
- Ad baseline CTR: 5%, current CTR: 3.0% (40% decline) 🔴 Significant fatigue, rotate
- Ad avg frequency: 5.2 per user/30 days ⚠️ Monitor for fatigue
- Ad avg frequency: 9.8 per user/30 days 🔴 Critical fatigue, expand audience

---

## Tracking Health Alerts

### Google Conversion Tracking

| Condition | Severity | Action |
|-----------|----------|--------|
| Conversion tag firing, data flowing | INFO | Healthy |
| Conversion tag not firing | CRITICAL | NO DATA, urgent fix required |
| Conversion tag firing but counts = 0 for 24h | CRITICAL | Tag broken or no conversions, investigate |
| Conversion count suddenly drops >50% | CRITICAL | Tag issue or funnel problem |

### GA4 Integration

| Condition | Severity | Action |
|-----------|----------|--------|
| GA4 events receiving data | INFO | Healthy |
| GA4 events not receiving conversion data | CRITICAL | Data flow broken |
| Click-to-session rate >70% | INFO | Good attribution |
| Click-to-session rate 50-70% | WARNING | Tracking loss occurring |
| Click-to-session rate <50% | CRITICAL | Major tracking loss |
| Google conversions ≠ GA4 conversions (within ±5%) | INFO | Normal variance |
| Google conversions >> GA4 conversions (>15% gap) | WARNING | Attribution gap, investigate |

### Auto-tagging (gclid)

| Condition | Severity | Action |
|-----------|----------|--------|
| gclid appending to URLs | INFO | Healthy |
| gclid NOT appending | CRITICAL | Auto-tagging disabled, enable immediately |
| gclid in URL but not matching GA4 | WARNING | Passthrough issue, check GA4 config |

**Example:**
- Conversion tag: Firing ✅, GA4 events flowing ✅, gclid appending ✅ → Healthy
- Conversion tag: NOT firing 🔴 CRITICAL
- Click-to-session rate: 45% 🔴 CRITICAL (major tracking loss)
- Conversions (Google): 100, Conversions (GA4): 88 (12% gap) ⚠️ WARNING

---

## Anomaly Detection Thresholds

### CPC (Cost Per Click) Spikes

| Threshold | Severity | Action |
|-----------|----------|--------|
| CPC increase 10-20% in one day | INFO | Monitor for pattern |
| CPC increase 20-50% in one day | WARNING | Auction competition spike or bid adjustment |
| CPC increase >50% in one day | CRITICAL | Investigate: Bid settings changed, auction inflation, budget shortage |
| CPC trending ↑ for 7 days | WARNING | Sustained increase, auction heating up |
| CPC trending ↓ for 7 days | INFO | Positive trend, possibly winning auction share |

### Conversion Rate Changes

| Threshold | Severity | Action |
|-----------|----------|--------|
| Conversion rate decline 10-20% | WARNING | Landing page or funnel issue possible |
| Conversion rate decline >40% | CRITICAL | Major issue: page broken, tracking broken, or audience change |
| Conversion rate drop to 0% for 6+ hours | CRITICAL | URGENT: page down, tracking broken, or payment processing failure |
| Conversion rate increase >50% | INFO | Positive signal, verify accuracy (not tracking error) |

### Impression Volume Changes

| Threshold | Severity | Action |
|-----------|----------|--------|
| Impressions decline 20-40% in one day | WARNING | Budget cap, targeting restriction, or auction loss |
| Impressions decline >60% in one day | CRITICAL | Campaign paused, budget exhausted, or major quality issue |
| Impressions trending ↓ for 3+ days | WARNING | Sustained volume loss, investigate |
| Impressions trending ↑ for 3+ days | INFO | Positive trend, expanding reach |

**Example:**
- CPC: $0.80 baseline, now $0.95 (19% increase) ⚠️ Monitor
- CPC: $0.80 baseline, now $1.35 (69% increase) 🔴 CRITICAL investigate
- Conversion rate: 3.2% baseline, now 2.8% (12% decline) ⚠️ Watch
- Conversion rate: 3.2% baseline, now 1.0% (69% decline) 🔴 CRITICAL page issue
- Impressions: 1000/day baseline, now 400/day 🔴 CRITICAL (60% drop)

---

## Scaling Detection Thresholds

### Budget Scaling Criteria (ALL must be true)

| Criteria | Requirement |
|----------|-------------|
| Daily spend pacing | ≥95% of daily budget (budget-capped) |
| Performance | AR ROAS ≥ min_acceptable_ar_roas (profitable) |
| Consistency | 3+ consecutive days meeting criteria |
| Cooldown | No scale action in past 7 days (avoid thrashing) |
| Trend | Optional: 7-day ROAS trend stable/improving |

**Scaling Proposal Trigger:**
When all criteria met, generate proposal:
> "Campaign SEARCH_SkincareCo_US_BrandTerms: Spending 97% of $250/day budget with AR ROAS 2.8x (target 2.0x) for 4 consecutive days. Recommend increasing daily budget to $350 (+40%) to capture additional revenue. Estimated monthly uplift: +$4,500 in revenue."

**Example:**
- Spend: $237/$250 (95%) ✅
- ROAS: 2.5x (above 1.5x min) ✅
- Days consistent: 4 ✅
- Last scale: 9 days ago (cooldown cleared) ✅
- → Propose scaling

---

## Search Term Health Alerts (Search Campaigns)

### High-Spend, Zero-Conversion Terms

| Threshold | Severity | Action |
|-----------|----------|--------|
| Spend >$50, conversions = 0 in 7 days | WARNING | Add to negative keywords |
| Spend >$100, conversions = 0 in 7 days | CRITICAL | Add to negative immediately |
| Multiple high-spend zero-conversion terms | CRITICAL | Review keyword strategy, targeting too broad |

### High-Volume, High-Conversion Terms (Expansion)

| Threshold | Severity | Action |
|-----------|----------|--------|
| Search term >20 conversions, NOT in keyword list | INFO | Add as new keyword (phrase or exact) |
| Search term high conversion rate, high volume | INFO | Priority expansion candidate |

---

## Shopping Feed Health Alerts (Shopping Campaigns)

### Product Disapprovals

| Threshold | Severity | Action |
|-----------|----------|--------|
| <1% of products disapproved | INFO | Healthy |
| 1-5% of products disapproved | WARNING | Monitor, review reasons |
| >5% of products disapproved | CRITICAL | Major policy issues, urgent review |

### Feed Sync Status

| Threshold | Severity | Action |
|-----------|----------|--------|
| Feed updated <24h ago | INFO | Current |
| Feed last updated 24-48h ago | WARNING | Stale, check sync |
| Feed last updated >48h ago | CRITICAL | Severely stale, investigate sync issue |

### Price Discrepancies

| Threshold | Severity | Action |
|-----------|----------|--------|
| <5% of products price variance | INFO | Acceptable |
| 5-10% of products price variance | WARNING | Monitor pricing sync |
| >10% of products price variance | CRITICAL | Major discrepancy, investigate pricing source |

---

## Alert Consolidation & Fatigue Prevention

### Multi-Alert Deduplication
- If same issue triggers multiple alerts (e.g., CPA high AND ROAS low), consolidate into single alert with multiple signals
- Prevent alert spam by grouping related issues

### Alert Frequency
- CRITICAL alerts: Every 6 hours (or immediately if detected)
- WARNING alerts: Daily (included in daily brief)
- INFO alerts: Daily summary (included in daily brief)

### Alert Acknowledgment
- Track which alerts have been acknowledged by human
- Don't repeat same alert unless condition worsens
- Clear alert when condition resolved

---

## Custom Threshold Overrides

Brands may override default thresholds in `brand_config`:

```json
{
  "alert_thresholds": {
    "cpa_warning_multiplier": 1.20,  // 20% over target
    "cpa_critical_multiplier": 1.30, // 30% over target
    "roas_warning_multiplier": 0.80, // 20% below target
    "min_acceptable_ar_roas": 1.50,
    "budget_underspend_days": 3,     // 3+ days <70% budget
    "qs_warning_threshold": 6,
    "ctrs_fatigue_threshold": 0.30,  // 30% CTR decline = fatigue
    "impression_freq_warning": 6,    // >6 freq/user = warning
    "impression_share_minimum": 0.70,
    "conversion_tracking_lag_hours": 6 // Alert if no data for 6h
  }
}
```

Use defaults unless brand specifies custom values.

---

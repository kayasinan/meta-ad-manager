# Scaling Detection & Budget Optimization for Google Ads

Framework for identifying scaling opportunities and generating scaling proposals based on real-time performance data.

---

## Scaling Detection Logic

### The Four Criteria (ALL must be met)

#### 1. Budget Utilization (≥95%)
Campaign is spending close to its daily budget cap, indicating demand exceeds supply.

**Check:**
```sql
SELECT campaign_id, campaign_name,
  daily_budget,
  SUM(spend) as today_spend,
  SUM(spend) / daily_budget as pacing_ratio
FROM g_daily_metrics
WHERE brand_id = $BRAND_ID
  AND date = TODAY()
GROUP BY campaign_id
HAVING pacing_ratio >= 0.95;
```

**Pass Criteria:** Daily spend ≥ 95% of daily budget

**Examples:**
- Budget: $250, Spend: $237 (95%) → ✅ PASS
- Budget: $250, Spend: $250+ (100%+) → ✅ PASS
- Budget: $250, Spend: $230 (92%) → ❌ FAIL (below 95%)

#### 2. Profitable Performance (ROAS ≥ min_acceptable_ar_roas)
Campaign is profitable and meeting minimum acceptable return threshold. No point scaling a losing campaign.

**Check:**
```sql
SELECT campaign_id, campaign_name,
  ar_roas,
  (SELECT min_acceptable_ar_roas FROM brand_config WHERE id = $BRAND_ID) as threshold
FROM g_daily_metrics
WHERE brand_id = $BRAND_ID
  AND date >= NOW() - INTERVAL '7 days'
  AND ar_roas >= (SELECT min_acceptable_ar_roas FROM brand_config WHERE id = $BRAND_ID)
GROUP BY campaign_id;
```

**Pass Criteria:** 7-day average AR ROAS ≥ min_acceptable_ar_roas (e.g., 1.5x minimum)

**Examples:**
- 7-day avg ROAS: 2.5x, threshold: 1.5x → ✅ PASS (profitable)
- 7-day avg ROAS: 1.8x, threshold: 1.5x → ✅ PASS (above minimum)
- 7-day avg ROAS: 1.2x, threshold: 1.5x → ❌ FAIL (below threshold, losing money)
- 7-day avg ROAS: 0.9x, threshold: 1.5x → ❌ FAIL (clearly losing money)

#### 3. Consistency (3+ consecutive days)
Criteria #1 and #2 must hold for at least 3 consecutive days to confirm pattern, not random spike.

**Check:**
```sql
SELECT campaign_id, campaign_name,
  COUNT(DISTINCT date) as consecutive_days_qualified
FROM g_daily_metrics
WHERE brand_id = $BRAND_ID
  AND date >= NOW() - INTERVAL '7 days'
  AND (SUM(spend) / daily_budget >= 0.95)
  AND ar_roas >= (SELECT min_acceptable_ar_roas FROM brand_config WHERE id = $BRAND_ID)
GROUP BY campaign_id, date
HAVING COUNT(DISTINCT date) >= 3;
```

**Pass Criteria:** 3 or more consecutive days with criteria #1 and #2 both met

**Examples:**
- Days 1, 2, 3: Both criteria met → ✅ PASS (3 consecutive)
- Days 1, 2, 3, 4: All criteria met → ✅ PASS (4 consecutive)
- Days 1, 2, break, 4, 5: Gap breaks sequence → ❌ FAIL (not consecutive)
- Days 1, 2 only: Only 2 days → ❌ FAIL (need 3+)

#### 4. Cooldown (No scaling in past 7 days)
Avoid "thrashing" by scaling too frequently. Once scaled, allow 7 days to observe impact before proposing another scale.

**Check:**
```sql
SELECT campaign_id,
  MAX(scaled_at) as last_scale_date
FROM campaign_changes
WHERE brand_id = $BRAND_ID
  AND operation_type = 'SCALING'
  AND status = 'LAUNCHED'
GROUP BY campaign_id
HAVING MAX(scaled_at) < NOW() - INTERVAL '7 days'
  OR MAX(scaled_at) IS NULL;  -- Never scaled
```

**Pass Criteria:** No scaling action in past 7 days, OR campaign has never been scaled

**Examples:**
- Last scaled: 8 days ago → ✅ PASS (cooldown cleared)
- Last scaled: 10 days ago → ✅ PASS (well past cooldown)
- Last scaled: 5 days ago → ❌ FAIL (still in 7-day cooldown)
- Never scaled before → ✅ PASS (no cooldown applies)

---

## Scaling Proposal Generation

### When All Four Criteria Met

Generate a scaling proposal with:
- Campaign name and current metrics
- Current daily budget and spend pacing
- Current ROAS and revenue impact
- Proposed budget increase (amount and %)
- Estimated monthly revenue uplift
- Recommendation confidence level

### Scaling Calculation

#### 1. Determine Headroom
How much additional budget could campaign absorb based on historical CPM/CPC trends?

**Method A: Impression-based scaling**
```
Available Daily Impressions = (Avg daily impressions × historical max CPM variance)
Additional Budget Available = Available Daily Impressions × Avg CPM

Example:
- Current impressions: 10,000/day
- Current budget: $250
- Current CPM: $25 ($250 / 10,000 impressions)
- Historical CPM variance: ±15%
- Max CPM likely: $25 × 1.15 = $28.75
- If we increase budget to $300 (20% increase):
  - Estimated new daily impressions: 10,000 × 1.15 = 11,500
  - New spend at historical CPM: $331 (over budget)
  - More realistic new spend: $290-310
  - Headroom: ~$50-60 (conservative estimate)
```

#### 2. Propose Budget Increase
Recommend 20-50% increase depending on how close to budget cap:

| Current Utilization | Recommended Increase | Rationale |
|---|---|---|
| 95-99% | +40-50% | Tight constraint, significant headroom |
| 100%+ | +30-40% | Maxed out, moderate headroom |
| >110% | +20-30% | Overspending, cautious increase |

#### 3. Calculate Revenue Impact
Estimate monthly uplift assuming ROAS holds:

```
New Daily Budget = Current Daily Budget + Increase
New Daily Spend Estimate = New Daily Budget × (average utilization ratio)
Additional Daily Spend = New Daily Spend Estimate - Current Spend
Additional Daily Revenue = Additional Daily Spend × Current ROAS
Monthly Uplift = Additional Daily Revenue × 30 days

Example:
- Current daily budget: $250
- Current daily spend: $237 (95% utilization)
- Current ROAS: 2.5x (1x spend = 2.5x revenue)
- Proposed budget increase: +$100/day → $350/day
- Expected new utilization: 96% (slightly higher)
- New daily spend estimate: $336 (96% of $350)
- Additional daily spend: $336 - $237 = $99
- Additional daily revenue: $99 × 2.5x = $247.50
- Monthly uplift: $247.50 × 30 = $7,425
```

### Scaling Proposal Template

```markdown
## Scaling Proposal: [Campaign Name]

**Date Generated:** 2026-02-16
**Campaign:** SEARCH_SkincareCo_US_BrandTerms_20260214
**Current Status:** Budget-Capped + Profitable

### Current Performance (7-day average)
- Daily Budget: $250
- Daily Spend: $237 (95% utilization)
- Clicks: 1,240
- Conversions: 82
- AR CPA: $2.89 (target: $3.00) ✅ BEATING TARGET
- AR ROAS: 2.8x (min acceptable: 1.5x) ✅ WELL ABOVE THRESHOLD
- CTR: 3.2%
- Conversion Rate: 6.6%

### Consecutive Days Qualified
✅ Days 1, 2, 3, 4 (all criteria met for 4 days)

### Scaling Rationale
Campaign is spending 95% of daily budget while delivering strong profitability (2.8x ROAS). Historical data suggests:
- CPM has remained stable ($25-26)
- CPC has remained stable ($2.00)
- Conversion rate stable at 6.5-6.7%
- No signs of audience saturation in first 4 days

This indicates organic demand exceeds current budget allocation. Scaling is low-risk given consistent performance.

### Proposal
**Increase Daily Budget:** $250 → $350 (+$100, +40%)
- Assumes 96% utilization of new budget (conservative)
- New estimated daily spend: $336
- Additional daily spend: $99

**Expected Revenue Impact (Monthly)**
- Additional daily revenue: $99 × 2.8x ROAS = $277/day
- Monthly uplift: $277 × 30 = **$8,310**
- Confidence level: High (based on consistent 4-day pattern)

**Risk Assessment**
- ⚠️ CPM/CPC inflation possible if budget doubled dramatically, but 40% increase is conservative
- ⚠️ ROAS may decline slightly (historical: -5-10% when scaling), estimated new ROAS: 2.5-2.7x
- ✅ Even at 2.5x ROAS, ROI remains strong
- ✅ No signs of audience saturation in data

### Recommendation
**Recommend APPROVE** — Increase daily budget to $350. Monitor for 7 days before next scaling proposal.

**Timeline:**
- Day 1 (today): Generate proposal
- Day 1 (after human approval): Implement budget increase
- Days 2-7: Monitor new performance metrics
- Day 7+: Re-evaluate for further scaling

**Next Review:** 2026-02-23
```

---

## Scaling Risk Assessment

### Green Lights (Low Risk)
- ✅ Budget utilization 95-105% (tight but not maxed)
- ✅ ROAS stable/trending up over 7 days
- ✅ CPM/CPC stable over 7 days
- ✅ Conversion rate consistent
- ✅ No anomalies in spend/performance relationship
- ✅ Audience signals healthy (no CTR fatigue yet)
- ✅ First or second scaling action (not 5th consecutive scale)
- ✅ Increase 40% or less (not doubling budget)

### Yellow Lights (Medium Risk - Scale with Caution)
- ⚠️ ROAS trending slightly down but still above minimum
- ⚠️ CPM trending up 10-20% (inflation starting)
- ⚠️ CTR declining 10-15% (early fatigue signals)
- ⚠️ Campaign has been scaled 2-3 times recently
- ⚠️ Budget increase 50%+ (aggressive scaling)
- ⚠️ Data history <14 days (new campaign, less predictable)
- ⚠️ Audience size small (only few thousand users, risk of saturation)

### Red Lights (High Risk - Do NOT Scale)
- 🔴 Budget utilization >110% (already overspending)
- 🔴 ROAS declining trend over 7 days
- 🔴 CPM inflation >30% in past week
- 🔴 CTR declining >25% (major fatigue)
- 🔴 Campaign has been scaled 5+ times rapidly
- 🔴 Audience size critically small (<100 users/day)
- 🔴 Conversion data insufficient (<15 conversions in past 7 days)
- 🔴 Any quality score issues emerging
- 🔴 Impression share declining (losing ground to competitors)

---

## Scaling Monitoring (Post-Implementation)

### Track After Scaling
Monitor new budget for 7 days following scale action:

**Metrics to Watch:**
- Daily spend pacing with new budget (target 85-100%)
- ROAS stability (should remain within ±10% of pre-scale)
- CPC/CPM movement (should remain stable, <5% variance)
- CTR changes (should not drop >10%)
- Conversion rate (should remain consistent)
- Quality score (should not decline)

**Decision Tree Post-Scale:**

```
Scale Approved → Budget Increased to $350/day

Day 1-2: Monitor
├─ If spend pacing 85-100% of new budget → Good, on track
├─ If spend pacing <70% of new budget → Alert: Under-utilizing new budget
└─ If spend pacing >110% of new budget → Alert: Still budget-capped

Day 3-7: Assess Performance
├─ If ROAS within ±10% of pre-scale → Success, maintain
├─ If ROAS declined >20% → Investigate cause (CPM inflation? audience saturation?)
├─ If CTR declined >20% → Creative fatigue, may need rotation
└─ If all stable → Continue monitoring, ready for next scale if criteria met

Day 7: Full Evaluation
├─ If all metrics stable and spend >90% → Ready for next scaling proposal
├─ If any metrics degraded >15% → Pause scaling, optimize current campaign
└─ If ROAS fell below min_acceptable_ar_roas → STOP, implement pause protocol
```

---

## Scaling Budget Limits

Most brands have maximum daily budgets they're willing to spend per campaign. Respect these limits:

**Example:** Brand config specifies max daily budget per Search campaign = $1,000

| Current Budget | Max Allowable | Can Scale? | New Budget |
|---|---|---|---|
| $250 | $1,000 | Yes | Up to $1,000 |
| $750 | $1,000 | Yes (limited) | Up to $1,000 |
| $950 | $1,000 | Yes (minimal) | Up to $1,000 |
| $1,000 | $1,000 | No | Stay at $1,000 |

**Check before proposing:**
```sql
SELECT campaign_id, current_budget,
  (SELECT max_daily_budget_per_campaign FROM brand_config WHERE id = $BRAND_ID) as max_allowed,
  (current_budget * 1.40) as proposed_40pct_increase
FROM g_campaigns
WHERE brand_id = $BRAND_ID;

-- If proposed budget > max_allowed, cap at max_allowed
```

---

## Scaling Documentation

### Record All Scaling Actions
Track in `campaign_changes` table:

```sql
INSERT INTO campaign_changes (
  brand_id, campaign_id, operation_type, change_details, status, scaled_at
) VALUES (
  $BRAND_ID,
  'campaign_123',
  'SCALING',
  {
    "previous_budget": 250,
    "new_budget": 350,
    "increase_percent": 40,
    "rationale": "95% utilization, 2.8x ROAS, 4 consecutive days",
    "estimated_monthly_uplift": 8310,
    "risk_level": "low",
    "approval_date": "2026-02-16"
  },
  'APPROVED',
  NOW()
);
```

### Reporting
Include scaling actions in daily brief:
- Which campaigns were scaled
- Previous and new budgets
- Estimated revenue impact
- Next review date

---

## Scaling Frequency Caps

Prevent over-aggressive scaling:

| Scaling Cadence | Recommendation |
|---|---|
| First scaling | Typically Day 7-14 of campaign |
| Subsequent scalings | Minimum 7 days between proposals |
| Maximum frequency | No more than 1-2 scalings per month per campaign |
| Hard cap | No scaling if already in top 3 budgets in account |

**Reasoning:**
- Frequent scaling creates volatility
- 7-day cooldown allows time to observe impact
- Rapid consecutive scalings risk exhausting audience
- Account-level budgeting requires fairness across campaigns

---

## Scaling by Campaign Type

### Search Campaigns (Most Common for Scaling)
- Easiest to scale (direct keyword intent)
- Lowest risk of audience saturation
- Scale freely within budget constraints
- 95%+ budget utilization is healthy target

### Display Campaigns
- More caution required (broader audience)
- Higher risk of CTR fatigue when scaling
- Watch frequency metrics closely
- Consider expanding audience instead of just increasing budget

### Shopping Campaigns
- Scaling limited by product feed size
- Can't scale beyond available inventory
- Focus on product group optimization instead
- Budget scaling useful mainly for bids, not volume

### YouTube Video Campaigns
- Scaling works well (large YouTube audience)
- Monitor for cost inflation (auction competition)
- Watch for frequency fatigue (video ads are intrusive)
- Recommend creative rotation alongside budget scaling

### Performance Max
- Scaling works well (multi-channel distribution)
- Smart bidding learns from budget increase
- May need more diverse assets before scaling
- 7-day learning phase before scaling recommended

---

## Seasonal Scaling Considerations

### Peak Seasons (Holiday, Events)
- Scale more aggressively during peak demand
- Reduce after-peak to avoid over-investing
- Plan scaling calendar in advance for seasonality

### Off-Peak Seasons
- Scale conservatively (lower demand baseline)
- Focus on efficiency (CPA/ROAS) over volume
- May recommend pausing instead of scaling

---

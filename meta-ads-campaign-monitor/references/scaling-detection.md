# Budget-Cap Scaling Detection

## Overview

When a campaign is profitable and budget-capped (spending 95%+ of its daily budget), it represents a scaling opportunity. The Campaign Monitor detects these conditions and recommends incremental budget increases to the Orchestrator.

---

## The 4 Scaling Conditions

All four conditions must be met simultaneously to trigger a scaling proposal:

### Condition 1: Campaign Is Budget-Capped
- **Metric:** Actual daily spend ≥ 95% of planned daily budget
- **Data Point:** `actual_spend / planned_budget ≥ 0.95`
- **Meaning:** Budget is the constraint; Meta could spend more if allowed

### Condition 2: Campaign Has Strong ROAS (Meets Floor)
- **Metric:** AR ROAS ≥ min_acceptable_ar_roas from brand_config
- **Data Point:** `ar_roas ≥ brand_config.scaling_config.min_ar_roas_to_scale`
- **Meaning:** Campaign is profitable enough to justify higher spend
- **Example:** If min_ar_roas = 2.5 and campaign ROAS = 2.8, condition is MET

### Condition 3: Consistent Budget-Cap Duration
- **Metric:** Campaign has been budget-capped for N consecutive days (default: 3 days)
- **Data Point:** `days_at_budget_cap ≥ brand_config.scaling_config.min_days_at_budget_cap`
- **Meaning:** Not a one-day fluctuation; consistent constraint established
- **Default:** 3 consecutive days

### Condition 4: Cooldown Period Respected
- **Metric:** No scaling event in the last N days (default: 7 days)
- **Data Point:** `days_since_last_scaling_event ≥ brand_config.scaling_config.cooldown_days_after_scale`
- **Meaning:** Avoid scaling too frequently; allow time for optimization
- **Default:** 7 days between scaling events per campaign

---

## Scaling Decision Logic

```
IF (condition_1 AND condition_2 AND condition_3 AND condition_4)
  THEN flag as "SCALING OPPORTUNITY"
  AND propose budget increase to Orchestrator
ELSE
  continue monitoring
```

---

## Budget Scale Calculation

When all 4 conditions are met, calculate the proposed increase:

### Step 1: Calculate Increase Percentage
```
increase_pct = brand_config.scaling_config.step_pct
Default: 10-15% per scaling event
```

### Step 2: Calculate New Budget
```
new_daily_budget = current_budget × (1 + increase_pct)
Example: $500/day × 1.10 = $550/day (10% increase)
```

### Step 3: Apply Budget Cap
```
IF new_daily_budget > brand_config.scaling_config.max_budget_cap
  THEN new_daily_budget = max_budget_cap
  AND note in proposal: "Capped at maximum budget limit"
```

### Step 4: Calculate Weekly Impact
```
weekly_increase = (new_daily_budget - current_budget) × 7 days
Example: ($550 - $500) × 7 = $350 additional weekly spend
```

---

## Scaling Proposal Format

When proposing a scaling opportunity, include:

```
SCALING OPPORTUNITY DETECTED

Campaign: [Campaign Name]
Current Daily Budget: $[X]
Proposed Daily Budget: $[X + increase]
Increase Amount: $[X]
Increase Percentage: [Y]%

JUSTIFICATION:
- Campaign spending 95%+ of daily budget for [N] consecutive days
- AR ROAS: [Z] (above minimum threshold of [min_roas])
- No scaling events in past [cooldown] days

EXPECTED IMPACT:
- Weekly additional spend: $[weekly_increase]
- Estimated additional weekly conversions: [based on current CPA]
- Estimated incremental revenue: [based on current ROAS]

RISKS:
- Learning phase may reset if audience is narrow
- CPM may increase if broader audience required
- Performance may degrade if budget increase is too aggressive

RECOMMENDATION:
Increase daily budget from $[X] to $[X + increase]
Scale step: [Y]%
Monitor closely for 3-5 days after scaling

REQUIRES HUMAN APPROVAL
```

---

## Cooldown Period Rules

**Why cooldown?**
- Prevents over-scaling (too much increase, too fast)
- Allows performance data to stabilize after each change
- Reduces algorithm learning phase disruption

**Cooldown calculation:**
```
last_scaling_timestamp = [when budget was last increased]
days_since = TODAY - last_scaling_timestamp
IF days_since ≥ cooldown_days → eligible for scaling
IF days_since < cooldown_days → in cooldown, skip scaling
```

**Cooldown period per campaign:**
- Default: 7 days
- Can be customized in brand_config.scaling_config.cooldown_days_after_scale
- Prevents more than 1-2 scaling events per week per campaign

**Multiple Campaigns:**
- Each campaign has its own cooldown tracker
- Scaling campaign A doesn't affect campaign B's cooldown
- Track `last_scaling_timestamp` per campaign_id

---

## Max Budget Cap Enforcement

Prevent runaway budget growth:

```
max_daily_budget = brand_config.scaling_config.max_budget_cap
```

**Rules:**
- If calculated new budget exceeds max cap, use max cap instead
- Note in proposal that cap was applied
- Do NOT exceed human's hard budget ceiling
- Require human approval before removing or raising cap

**Example:**
```
Current budget: $500/day
Proposed increase: +15% = $575/day
Max cap: $550/day
→ New budget: $550/day (capped)
→ Note in proposal: "Reached maximum budget cap of $550/day"
```

---

## Scaling Opportunity Detection Query

```sql
-- Detect scaling opportunities (brand-scoped)
SELECT
  c.id,
  c.name,
  c.daily_budget,
  dm.actual_spend,
  dm.actual_spend / c.daily_budget AS pacing,
  dm.ar_roas,
  bc.min_ar_roas_to_scale,
  CASE
    WHEN dm.actual_spend / c.daily_budget >= 0.95 THEN true
    ELSE false
  END AS is_budget_capped,
  CASE
    WHEN dm.ar_roas >= bc.min_ar_roas_to_scale THEN true
    ELSE false
  END AS meets_roas_floor,
  DATEDIFF(current_date, c.last_scaling_date) AS days_since_scaling,
  COUNT(*) FILTER (
    WHERE dm.date >= current_date - INTERVAL '3 days'
    AND dm.actual_spend / c.daily_budget >= 0.95
  ) AS days_at_cap_recent
FROM campaigns c
JOIN daily_metrics dm ON dm.campaign_id = c.id AND dm.date = current_date
JOIN brand_config bc ON c.brand_id = bc.id
WHERE c.brand_id = $BRAND_ID
  AND c.status = 'ACTIVE'
  AND dm.actual_spend / c.daily_budget >= 0.95
  AND dm.ar_roas >= bc.min_ar_roas_to_scale
  AND DATEDIFF(current_date, c.last_scaling_date) >= bc.cooldown_days_after_scale
GROUP BY c.id, c.name, c.daily_budget, dm.actual_spend, dm.ar_roas, bc.min_ar_roas_to_scale, c.last_scaling_date
ORDER BY dm.ar_roas DESC;
```

---

## Implementation Notes

### In Campaign Monitor Daily Checks:
1. Run scaling detection query at step 3.1a of daily monitoring
2. Check all 4 conditions for each active campaign
3. If all 4 conditions met, add to "SCALING OPPORTUNITIES" section of daily report
4. Write to recommendations table with action_level = 'CAMPAIGN' and action_type = 'SCALE'
5. Include estimated additional spend and expected impact
6. Wait for Orchestrator to relay to human; do NOT make budget changes

### In Campaign Creator Execution:
1. When human approves a scaling recommendation, Campaign Creator updates campaign budget in Meta
2. Record the scaling event: timestamp, new budget, increase percentage
3. Reset cooldown counter for that campaign
4. Notify Campaign Monitor that scaling occurred (update campaign record)

### In Orchestrator:
1. Receive scaling opportunity from Monitor
2. Review proposal with reasoning
3. Present to human: "Campaign X is budget-capped with 2.8× ROAS. Recommend increasing budget from $500 to $550/day. Approve?"
4. On human approval, request Campaign Creator implement the scaling
5. Track all scaling events for account health trending

---

## Example Scenario

**Day 1:**
- Campaign "CONV_SkincareUS_Cold" spending $500/day (95% of $525 planned)
- AR ROAS: 2.8 (above min of 2.5)
- Not enough consecutive days yet (only 1 day at cap)
- Result: Monitor for scaling eligibility

**Day 2:**
- Still at 95% of budget
- ROAS stable at 2.8
- 2 consecutive days at cap (eligible if cooldown met)
- Result: Continue monitoring

**Day 3:**
- Still at 95% of budget
- ROAS increased to 3.1
- 3 consecutive days at cap (meets min_days_at_budget_cap)
- Last scaling: 15 days ago (meets cooldown of 7 days)
- Result: **ALL 4 CONDITIONS MET** → Propose scaling

**Monitor Action:**
```
Write to recommendations:
  action_level: CAMPAIGN
  action_type: SCALE
  campaign_id: CONV_SkincareUS_Cold
  proposal: "Budget-capped with 3.1× ROAS. Increase $525 → $577.50/day (+10%). Weekly impact: +$367.50"

Write to daily report:
  SCALING OPPORTUNITIES section:
  - CONV_SkincareUS_Cold: +10% from $525 to $577.50/day
```

**Orchestrator:**
Relays to human for approval.

**Human Approval:**
"Yes, scale the campaign."

**Campaign Creator:**
Updates campaign budget in Meta from $525 to $577.50, records scaling event.

**Next Cycle:**
Campaign Monitor applies 7-day cooldown; cannot scale again until Day 10.

# Budget Authority Protocol

This document defines the absolute rule that the human has ALL budget authority. The system NEVER commits spending without explicit human approval.

---

## Core Rule: ABSOLUTE

**The system NEVER decides how much to spend. The human decides ALL budget-related matters.**

This is immutable. No sub-agent, no algorithm, no "reasonable default" overrides this rule. Budget authority rests with the human operator, full stop.

---

## What Requires Human Approval

### Campaign-Level Budget Decisions

1. **Campaign creation:**
   - Daily budget amount: $XXX/day
   - Monthly projection: $X,XXX/month
   - Campaign goes into DRAFT status
   - Orchestrator presents proposal to human
   - Human approves the daily budget or adjusts it
   - Only after approval does Campaign Creator launch

2. **Budget increases:**
   - "This campaign is hitting its budget cap and has strong ROAS (X.XX)"
   - Orchestrator proposes: "Increase daily budget from $XXX to $YYY?"
   - Human approves the new amount, or declines, or suggests different amount
   - Campaign Creator adjusts the budget only after approval

3. **Budget decreases:**
   - "This campaign is underperforming and wasting budget"
   - Orchestrator proposes: "Reduce daily budget from $XXX to $YYY?"
   - Human approves or adjusts
   - Campaign Creator reduces budget only after approval

4. **Campaign pause/sunset:**
   - Orchestrator: "Campaign X below acceptable ROAS for 7 days, suggests $XXX/month savings if paused"
   - Human decides: pause now, pause gradually, or continue
   - Only human says when to stop spending

### Ad Group & Keyword-Level Budget Decisions

1. **Bid adjustments:**
   - Manual CPC campaigns: any bid change requires human approval
   - Target CPA/ROAS campaigns: bid adjustments approved by Campaign Creator after strategy approval
   - Example: "Increase keyword bid from $1.50 to $2.00?" → requires human approval for manual campaigns

2. **Budget reallocation:**
   - Moving budget from losing ad group to winning ad group
   - "Reduce ad group A budget by 20%, increase ad group B by 20%?" → human approval required
   - Never auto-rebalance

### Test & Experiment Budgets

1. **A/B tests:**
   - Test budget percentage: "Allocate 20% of budget to test variant?" → human approval
   - Test duration: "Run for 14 days?" → human approval
   - Success criteria: "If test ROAS > X.XX, scale it?" → human decides outcome

2. **New market entry:**
   - Pilot budget: "Launch in new market with $XXX/day?" → human approval
   - Duration: "Test for 30 days?" → human approval
   - Scaling rules: "If ROAS > X.XX, scale to $YYY/day?" → human decides

### Seasonal/Promotional Budgets

1. **Promotional periods:**
   - "Holiday season approaching, recommend increasing daily budget from $XXX to $YYY for 6 weeks?" → human approval
   - Estimated spend: Present all numbers to human

2. **Special campaigns:**
   - Product launch, flash sale, clearance, etc.
   - Orchestrator proposes budget: "Launch campaign with $XXX/day for X days?" → human approval

### Scaling Proposals

**Scaling is a specific category that deserves detail:**

When a campaign is:
1. Hitting its daily budget cap consistently (≥3 consecutive days)
2. Maintaining strong ROAS (> min_acceptable_ar_roas, ideally near or above target)
3. No tracking issues

Then Orchestrator proposes scaling:

```
SCALING OPPORTUNITY
Campaign: [Name]
Current Status: Hitting $XXX/day budget cap
AR ROAS: X.XX (target: X.XX, min floor: X.XX)
Days at budget cap: [X/3 required]

SCALING PROPOSAL
Scale by: [20% of current budget per brand_config.scaling_config]
From: $XXX/day → $YYY/day
Est. monthly increase: $Z,ZZZ/month
Est. conversions increase: +X% (based on historical volume)
Confidence: [High / Medium]

HUMAN DECISION REQUIRED
☐ Approve: Increase to $YYY/day
☐ Adjust: Set to $[custom]/day instead
☐ Decline: Keep at current $XXX/day
☐ Other: [specify]
```

**After human approval:**
- Campaign Creator updates daily budget
- Orchestrator monitors for next 3 days
- If ROAS maintains, scaling was successful
- If ROAS drops, may revert (with human approval)

**Escalation:** Maximum 2-3 scaling steps per month recommended. If campaign needs to scale beyond that, re-evaluate strategy.

---

## What Does NOT Require Human Approval (Agent Authority)

These actions are delegated to agents and do NOT require human approval, as long as they stay within approved budget:

### Creative & Ad Optimization
- Adding new ads to existing ad groups (within overall budget)
- Pausing low-quality-score individual ads (within existing ad group budget)
- Rotating ad copy/headlines while staying within budget
- Adjusting ad-level bids in Target CPA/ROAS campaigns (Google algorithm handles)

### Audience Segment Optimization
- Creating new audience segments from campaign data
- Applying new audiences to ad groups (if within existing budget)
- Pausing underperforming audience segments (within existing budget)

### Keyword Management (Search Campaigns)
- Adding new keywords to ad groups (if within existing budget)
- Adding negative keywords to prevent waste
- Pausing low-quality keywords (within existing budget)

### Landing Page Optimization
- Recommending landing page changes
- Testing page variations (if within existing budget)
- Flagging pages that need fixing

### Reporting & Monitoring
- Generating daily/weekly/monthly reports
- Creating alerts when thresholds are crossed
- Recommending actions (with human approval required for execution)

---

## Budget Constraints (Database-Driven)

Every brand has budget constraints in `brand_config`:

```sql
SELECT
  brand_name,
  daily_budget_constraint,
  monthly_budget_constraint,
  scaling_config
FROM brand_config
WHERE id = $BRAND_ID;
```

**These are HARD LIMITS:**
- System will NEVER propose spending above `daily_budget_constraint`
- System will NEVER propose spending above `monthly_budget_constraint`
- Scaling proposals respect `scaling_config` (step size, minimum ROAS, cooldown, max cap)

**If human wants to exceed these:**
- Human must explicitly approve budget constraint change
- Orchestrator presents confirmation: "Increase daily budget cap from $XXX to $YYY?"
- Human confirms, update `brand_config`, proceed

---

## Budget Authority in Practice: Scenario Examples

### Scenario 1: New Campaign Launch

```
Cycle Summary Phase 3 (Day 4):
Orchestrator to Human:
"I recommend launching a new Search campaign targeting [segment].
Expected volume: 20 conversions/month
Bid strategy: Target ROAS X.XX
Recommended daily budget: $XXX/day (or $X,XXX/month)

Do you approve launching with:
  ☐ $XXX/day (recommended)
  ☐ $YYY/day (different amount)
  ☐ No launch

Your decision?"

Human responds: "Approve at $XXX/day"

→ Orchestrator proceeds to Phase 4 with $XXX/day budget
→ Campaign Creator creates campaign with exactly $XXX/day
→ Campaign goes live only with this approved budget
```

### Scenario 2: Budget Scaling Request

```
Monitoring Phase (Day 6):
Campaign Monitor reports:
"Campaign 'Summer Sale' hitting $500/day budget cap for 4 consecutive days.
AR ROAS: 3.2x (target: 3.0x, floor: 1.5x)
Request: Increase to $600/day? (+20% as per brand_config)"

Orchestrator to Human:
"Campaign 'Summer Sale' is ready to scale.
Current: $500/day, hitting cap consistently
Performance: 3.2x AR ROAS (strong)
Proposal: Increase by 20% → $600/day
Est. additional monthly spend: $3,000
Est. additional monthly revenue: $9,600 (at current ROAS)

Approve scaling to $600/day?"
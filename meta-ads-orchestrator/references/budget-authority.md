# Budget Authority Rules

**CRITICAL PRINCIPLE: The human decides ALL budget-related matters. The system NEVER auto-commits spending.**

This document outlines the immutable budget authority rules for the Meta Ads AI Agent System.

---

## Core Rule

The system NEVER decides how much to spend. The human decides ALL budget-related matters.

This rule is non-negotiable and overrides any other instruction in any agent's documentation. Budget-related decisions include:

- Total daily/monthly budget amounts
- Budget splits across campaigns
- Budget splits across ad sets
- Budget increases or decreases of any size
- Learning phase budget boosts
- A/B test budget allocations
- Bid caps and ROAS floors
- Campaign spending limits
- Any commitment of money, even partially

---

## What Agents DO

Agents propose budget plans with data-backed reasoning and estimated impact. They present options with tradeoffs. They wait for approval.

**Examples:**

- Data & Placement Analyst: "This winning segment can be scaled. Recommend 20% budget increase (from $1,000/day to $1,200/day) based on 8-day consecutive ROAS above 3.5×. Estimated incremental conversions: 5/week at current CPA."

- Creative Producer: "We can produce 8 new creatives this week. I recommend: 3 human inspiration variants (priority), 4 Mode A variants (own winners), 1 Mode B variant (competitor-inspired). Total Gemini cost: ~$6."

- Campaign Creator: "Proposed campaign structure: 2 cold ad sets ($300/day), 1 warm ad set ($150/day), 1 hot ad set ($50/day). Total daily budget requested: $500/day."

---

## What Agents NEVER DO

Agents NEVER set, change, or commit any budget amount without explicit human approval. Even "standard" splits like 60/30/10 cold/warm/hot are proposals, not defaults.

**What's forbidden:**
- Automatically increasing budget when a campaign hits budget cap
- Decreasing budget without human permission
- Allocating money to tests without human approval
- Using "standard industry ratios" without human sign-off
- Pre-committing budget in campaign creation
- Assuming the human wants the "maximum safe" spend

---

## Workflow: How Budget Decisions Flow

### 1. Proposal Phase (Agent → Orchestrator)

Agent analyzes data and proposes a budget plan:

```
Data & Placement Analyst writes to agent_deliverables:
{
  "title": "Scaling proposal for winning segment",
  "estimated_savings": null,
  "estimated_improvement": "5 additional conversions/week",
  "reasoning": "Women 25-34 TX segment has AR ROAS 4.2× for 8 consecutive days, budget capped at $200/day. Scaling to $240/day (20% increase) should maintain efficiency.",
  "details": {
    "current_daily_budget": 200,
    "proposed_daily_budget": 240,
    "increase_amount": 40,
    "confidence": 0.92
  }
}
```

### 2. Consolidation Phase (Orchestrator)

Orchestrator reads all proposals and presents to human:

```
SCALING PROPOSALS FOR [BRAND_NAME]:

Campaign: [Name]
  - Winning Segment: Women 25-34, TX
  - Current Daily Budget: $200
  - 8-Day AR ROAS Average: 4.2×
  - Days at Budget Cap: 8
  - Proposed Daily Budget: $240 (increase of +$40 / +20%)
  - Estimated Impact: 5 additional conversions/week
  → Approve this scaling? (Yes/No)
```

### 3. Human Decision Phase

Human reviews and decides:
- Yes → Approve the proposed budget
- No → Reject (or modify)
- Ask Questions → Request clarification

### 4. Execution Phase (Orchestrator → Agent)

Only after explicit human approval does the Orchestrator direct Campaign Creator to execute:

```
Campaign Creator receives:
{
  "action": "UPDATE_BUDGET",
  "campaign_id": "xxx",
  "new_daily_budget": 240,
  "approved_by": "human",
  "approved_at": "2026-02-14T10:30:00Z",
  "reason": "Human approved scaling proposal"
}
```

Campaign Creator updates Meta Ads Manager and logs the change.

---

## Budget Decision Categories

### 1. Initial Campaign Budget

**Trigger:** Campaign Creator builds a new campaign

**Process:**
1. Campaign Creator proposes campaign structure with budget request
2. Orchestrator presents to human: "Proposed campaign budget: $500/day. Approve?"
3. On approval → Campaign Creator publishes with approved budget
4. Nothing goes live until human approves

### 2. Budget Increases (20% or greater)

**Trigger:** Winning campaign/segment eligible for scaling

**Process:**
1. Data & Placement Analyst identifies scaling opportunity
2. Orchestrator presents scaling proposal with estimated impact
3. Human approves or rejects
4. If approved → Campaign Creator executes in 20% increments (multiple approval steps if >20% total increase)

**Important:** Each 20% step requires human approval. No auto-stepping.

Example: Scale from $1,000/day to $1,500/day (50% increase)
- Step 1: $1,000 → $1,200 (20%) — requires approval
- Step 2: $1,200 → $1,440 (20%) — requires approval
- Step 3: $1,440 → $1,500 (4%) — requires approval
- Total: 3 decision points, not 1 auto-escalation

### 3. Budget Decreases

**Trigger:** Underperforming campaign, waste identified, or human budget reduction

**Process:**
1. Orchestrator identifies reason for decrease
2. Presents recommendation to human: "Campaign performing below floor ROAS. Recommend pause to save $X/week. Approve?"
3. Human approves or overrides
4. If approved → Campaign Creator executes

### 4. A/B Test Budget

**Trigger:** Testing a new creative, audience, or strategy

**Process:**
1. Orchestrator proposes test structure with budget allocation: "10% budget for test variant, 90% control"
2. Human approves or adjusts budget split
3. Only after approval does Campaign Creator create test ad sets with approved budget
4. Test runs for minimum duration (7 days) or until statistical significance

### 5. Learning Phase Budget Boost

**Trigger:** New ad set needs faster learning

**Process:**
1. Campaign Creator may request temporary budget increase for learning phase acceleration
2. Orchestrator presents to human: "New ad set in learning phase. Recommend temporary +$50/day boost for 7 days to accelerate learning. Total cost: ~$350. Approve?"
3. Human approves or rejects
4. Boost applies only to learning phase, reverts after

### 6. Campaign Sunsetting

**Trigger:** Campaign is losing money and needs to retire

**Process:**
1. Orchestrator recommends: "Campaign X has been below floor ROAS for 21 days. Recommend gradual wind-down: reduce 20% every 2 days, full pause in 10 days. Save $X/week."
2. Human approves or chooses alternative (immediate pause, slower reduction)
3. Campaign Creator executes approved wind-down plan

---

## Budget Authority in Practice

### Scenario 1: Scaling a Winner

**Data Analyst:** "Segment is winning with AR ROAS 3.8× for 7 days. Currently at daily budget cap of $500."

**Orchestrator to Human:** "Segment 'Women 25-34 CA' is performing strongly (AR ROAS 3.8×) and fully using its daily budget. Recommend testing a 20% budget increase ($500 → $600/day) to see if efficiency holds. Estimated additional spend: $2,100/month. Approve?"

**Human:** "Yes, approved."

**Orchestrator to Campaign Creator:** "Increase ad set budget to $600/day."

**Campaign Creator:** Updates Meta and logs change.

### Scenario 2: Rejecting a Proposal

**Creative Producer:** "Propose producing 12 new creatives this cycle (double normal volume). Estimated cost: $24 in Gemini API."

**Orchestrator to Human:** "Creative Producer proposes doubling creative volume to 12 variants. Cost: $24. Do you want to proceed?"

**Human:** "No, stick with 6 variants (normal volume). We need to test different messaging before ramping up production."

**Orchestrator to Creative Producer:** "Produce 6 variants (normal volume). Prioritize human inspiration and Mode A."

### Scenario 3: Pausing a Loser

**Data Analyst:** "Campaign X is below min_acceptable_ar_roas ($35 target, currently $52 CPA) for 9 consecutive days. Recommend pause."

**Orchestrator to Human:** "Campaign X is underperforming (AR CPA $52 vs. target $35) for 9 days. Recommend pause to save $800/week. Approve?"

**Human:** "Approved. Pause it now."

**Orchestrator to Campaign Creator:** "Pause Campaign X."

**Campaign Creator:** Pauses campaign, logs change with reason.

### Scenario 4: Budget Constraint Respected

**Campaign Monitor:** Reports total current daily spend is $2,450.

**Brand Config says:** `daily_budget_constraint = $2,500`

**Data Analyst:** Proposes scaling a segment with +$100/day increase (would reach $2,550).

**Orchestrator to Human:** "Proposed budget increase (+$100/day) would exceed daily limit ($2,500). Current spend: $2,450. Would require cutting another campaign by $100/day. Recommend?"

**Human:** "Cut Campaign Y by $100/day, then approve the scaling."

**Orchestrator:** Updates both campaigns per human decision.

---

## Pre-Commitment Rule

**Draft campaigns do NOT commit budget.**

When Campaign Creator builds a campaign, it starts in DRAFT status. No money is spent until:
1. Campaign Creator publishes to Meta (status becomes ACTIVE/LIVE)
2. Orchestrator gets human approval before publishing
3. Human explicitly approves the budget

**Violation Prevention:**
- Campaign Creator NEVER publishes without human approval
- Campaign Creator NEVER auto-publishes when a campaign reaches DRAFT status
- Orchestrator ALWAYS presents final campaign configuration to human before going live

---

## Budget Audit Trail

Every budget change is logged in `campaign_changes`:

```sql
INSERT INTO campaign_changes (
  campaign_id, change_type, action_level, previous_state, new_state,
  reason, approved_by, approved_at, executed_at
) VALUES (
  $campaign_id, 'BUDGET_CHANGED', 'CAMPAIGN',
  '{"daily_budget": 500}', '{"daily_budget": 600}',
  'Scaling proposal: segment ROAS 3.8× for 7 days',
  'human', now(), now()
);
```

This creates a complete audit trail of:
- What changed
- When it changed
- Who approved it
- Why it changed
- Before/after state

---

## Violations & Safeguards

If any agent attempts to commit budget without human approval:

1. **Orchestrator detects violation** → immediately escalates to human as CRITICAL
2. **Orchestrator rejects the action** → does not execute
3. **Human is informed** → "Agent attempted unauthorized budget commitment"
4. **Reason documented** → logged in system for debugging

**Example:** If Campaign Creator tries to publish a campaign to Meta:

```
❌ VIOLATION: Campaign Creator attempted to publish campaign without human approval.
   Campaign: "CONVERSIONS_Brand_Market_Aug_25"
   Budget: $500/day
   Status: DRAFT → would become ACTIVE

   This requires explicit human approval. Re-request approval from Orchestrator before proceeding.
```

---

## Summary

**The human is the budget authority.** The system proposes, consolidates, and presents. The human approves or rejects. The system executes only after approval.

No exceptions. No auto-escalation. No defaults. Every dollar is subject to human decision-making.

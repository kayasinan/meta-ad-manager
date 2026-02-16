# Optimization Cycle Phases

This document details the 6-day optimization cycle framework for Google Ads. Each cycle follows the same pattern: gather intelligence, make decisions, present to human, execute, and monitor.

## Cycle Overview

Each optimization cycle runs for 6 days and follows this structure:

```
Day 1: Phase 1 — Intelligence Gathering
Day 2-3: Phase 2 — Analysis & Decision Making
Day 4: Phase 3 — Present Summary to Human
Day 5: Phase 4 — Brief & Assembly (contingent on approval)
Day 6: Phase 5 — Monitoring + Setup for Next Cycle
```

**Critical Rule:** Nothing happens without human approval. All recommendations are presented, and the human decides what to execute.

---

## Phase 1: Intelligence Gathering

**Duration:** Day 1 (morning)

**Purpose:** Pull fresh data from Google Ads and GA4, verify data integrity, build foundational insights.

**Deliverables Requested:**

1. **Data & Placement Analyst** — 6-Day Report
   - Verify tracking health: gclid passing, click-to-session ratio, discrepancy <30%
   - Pull 7 days of campaign data from Google Ads API
   - Pull matching GA4 sessions and conversions
   - Calculate AR metrics (GA4 × ar_multiplier)
   - Segment analysis: Which dimensions drive conversions? Which waste money?
   - Quality Score analysis: Keyword health, CTR trends
   - Search term opportunities: High-converting terms not in keyword list
   - Audience recommendations: Build segments from high-performing dimensions
   - Deliverable: Detailed 6-Day Report with winners/losers/recommendations

2. **Creative Analyst** — Creative Assessment
   - Read latest ad performance data
   - Rank ads by AR ROAS
   - Identify fatigued ads (declining CTR, high impression volume)
   - Color analysis on top performers
   - Text density audit
   - Deliverable: Ad rankings, fatigue flags, color DNA

3. **Post-Click Analyst** — Landing Page Health
   - Pull GA4 data for all landing pages
   - Analyze bounce rates, session duration, conversion rates
   - Flag pages with issues (high bounce, low conversion)
   - Deliverable: Landing page scorecard

4. **Competitive Intel Analyst** — Market Context
   - Scan competitor websites for new ad angles
   - Monitor competitor activity (if available via Ad Library)
   - Identify market trends
   - Deliverable: Market opportunity brief

5. **Campaign Monitor** — Current Status
   - Run daily check on active campaigns
   - Flag any alerts (tracking issues, anomalies, quality drops)
   - Deliverable: Daily status report

**Output:**
- Orchestrator dashboard showing all 5 reports ready
- Any BLOCKED agents flagged for human intervention

---

## Phase 2: Analysis & Decision Making

**Duration:** Day 2-3

**Purpose:** Review all intelligence, make strategic recommendations, prepare Cycle Summary for human.

**Orchestrator Actions:**

1. **Consolidate Reports**
   - Cross-reference Data & Placement report with Creative Analyst rankings
   - Verify Creative metrics align with Performance metrics
   - Check Post-Click data — do high-traffic landing pages convert?
   - Note any conflicts or missing data

2. **Identify Action Level**

   Based on the 6-Day Report, determine scope of changes:

   **Ad-Level Rotation (Most Common)**
   - Creative Analyst flagged ads X, Y as fatigued
   - → Pause those specific ads
   - → Request Creative Producer to build 2-3 replacements based on replication blueprint
   - → Campaign Creator adds new ads to the same healthy ad groups
   - Outcome: Creative refreshed, no learning reset

   **Ad Group Changes (Segment Shift)**
   - Data & Placement Analyst: "Ad group targeting high-intent keywords is a loser"
   - → Pause that ad group
   - → Data & Placement Analyst builds new audience for high-converting segment
   - → Campaign Creator adds new ad group to existing campaign
   - Outcome: New segment targeted, only new ad group in learning phase

   **New Campaign (Strategic Pivot)**
   - Entering new market vertical
   - Objective fundamentally changes (e.g., awareness → conversions)
   - Current campaign structure cannot support new strategy
   - → Build new campaign from scratch
   - Outcome: New campaign in learning phase, existing campaigns undisturbed

   **Pause/Sunset (Waste Elimination)**
   - Ad group below min_acceptable_ar_roas for 7+ consecutive days
   - → Recommend immediate pause
   - → Present human with data: cost/day, estimated monthly savings
   - → Wait for human approval

3. **Quantify Impact**
   - For each recommendation, estimate:
     - Cost/week impact (if pause)
     - Expected revenue lift (if scale)
     - Time to expected results
     - Risk factors

4. **Identify Budget Needs**
   - If scaling winners: How much additional budget?
   - If launching new ads/ad groups: Initial budget estimate
   - Always present as proposal, never as fixed decision

5. **Prepare Cycle Summary** (ready by end of Day 3)

---

## Phase 3: Present Cycle Summary to Human

**Duration:** Day 4 (morning)

**Purpose:** Present all findings and recommendations to human for approval.

**Cycle Summary Format:**

```
═══════════════════════════════════════════════════════════════
OPTIMIZATION CYCLE #[N] SUMMARY — [BRAND NAME]
[Date Range: Day 1-6 of cycle]
═══════════════════════════════════════════════════════════════

ACCOUNT HEALTH SNAPSHOT
─────────────────────────────────────────────────────────────
Total Spend (last 7 days): $X,XXX.XX
AR CPA: $XX.XX (target: $XX.XX) [ON TARGET / ABOVE / BELOW]
AR ROAS: X.XX (target: X.XX) [ON TARGET / ABOVE / BELOW]
Trend: [↑ improved / ↓ declining / → flat] vs. previous cycle
Tracking Health: [✅ HEALTHY / ⚠️ ISSUES]

WHAT'S WORKING
─────────────────────────────────────────────────────────────
🎯 Top Performing Ad Groups:
   • [Ad Group Name] — AR ROAS X.XX, $XXX spend
   • [Ad Group Name] — AR ROAS X.XX, $XXX spend

🔍 Best Converting Keywords:
   • "[Keyword 1]" (Exact) — X conversions, AR CPA $XX.XX
   • "[Keyword 2]" (Phrase) — X conversions, AR CPA $XX.XX

🎨 Top Creative:
   • [Ad ID/Name] — CTR X.X%, AR ROAS X.XX
   • [Ad ID/Name] — CTR X.X%, AR ROAS X.XX

📊 Landing Page Winners:
   • [URL] — X% conversion rate
   • [URL] — X% conversion rate

WHAT'S FAILING
─────────────────────────────────────────────────────────────
❌ Losing Campaigns/Ad Groups:
   • [Campaign/Ad Group] — AR ROAS X.XX (below min X.XX floor)
     Status: [Below floor for X days]
     Weekly cost: $XXX
     Recommended action: PAUSE
     Estimated monthly savings: $XXX

🚨 Quality Score Issues:
   • [X] keywords with Quality Score < 5
   • [X] ad groups with declining estimated CTR
   • Focus areas: [list top 3]

⚠️ Tracking Gaps:
   • [Issue description]
   • Impact: [campaigns affected]

😴 Fatigued Ads:
   • [Ad ID] — CTR declining X% week-over-week
   • [Ad ID] — Impression share plateau

WASTE QUANTIFICATION
─────────────────────────────────────────────────────────────
Estimated Monthly Waste: $XXX-$XXX
   • Ghost campaigns (paused campaigns still spending): $XX
   • Low-Quality-Score keywords overspending: $XX
   • Below-floor ad groups: $XX
   • Other: $XX

RECOMMENDATIONS (PRIORITIZED)
─────────────────────────────────────────────────────────────
PRIORITY 1 (Execute Immediately):
  ☐ Pause [Ad Group Name] (below floor, $XXX/month savings)
  ☐ Replace fatigued ads [IDs] (creative refresh, expect CTR +X%)

PRIORITY 2 (This Week):
  ☐ Launch [X] new ads based on replication blueprint
    Budget needed: $XX/day
    Expected AR ROAS: X.XX
    Expected uplift: +X% conversions
  ☐ Adjust bids on [Ad Group Name] (Quality Score improved to X)

PRIORITY 3 (Next Week):
  ☐ Build new ad group targeting [segment]
    Audience: [size] potential conversions
    Budget needed: $XX/day
    Expected AR ROAS: X.XX
  ☐ Optimize landing pages [URLs] (high bounce rate, low conversion)

QUESTIONS FOR YOU
─────────────────────────────────────────────────────────────
□ Do you approve pausing [Ad Group Name]? (Saves $XXX/month)
□ What's your budget for new creative production this week? (Recommend $XXX/day)
□ Should we launch the new [segment] ad group? Budget available?
□ Any changes to conversion tracking or landing pages you should tell me about?

NEXT ACTIONS (Pending Approval)
─────────────────────────────────────────────────────────────
Once approved:
1. Creative Producer will build [X] new ads (3-5 business days)
2. Campaign Creator will update campaign structure (1 day after creatives ready)
3. We'll monitor new ads for 3 days before optimizing bids
4. You'll get daily performance briefs during monitoring phase

═══════════════════════════════════════════════════════════════
Ready to proceed? Please approve/adjust recommendations above.
```

**Wait for Human Response:**
- Approvals on specific recommendations
- Budget decisions on new spending
- Any clarifications or adjustments to the plan
- Do not proceed until human confirms

---

## Phase 4: Brief & Assembly

**Duration:** Day 5 (contingent on approval from Phase 3)

**Purpose:** Assemble the approved work and prepare for execution.

**Only runs if human approved recommendations in Phase 3.**

**Deliverables Assigned:**

1. **Creative Producer**
   - Brief: "Create [X] new ads based on [replication blueprint / competitor inspiration / brand refresh]"
   - Specifications:
     - Ad format (Responsive Search Ad, Expanded Text Ad, etc.)
     - Headline and description copy
     - Display URL and final URL (with UTM parameters)
     - Image assets (if applicable)
   - Deadline: End of day 5
   - Output: Ads ready for review

2. **Data & Placement Analyst**
   - Brief: "Build audience for [segment description]"
   - Specifications:
     - Segment criteria: [purchase history, search behavior, demographics, etc.]
     - Expected size: [X users/sessions]
     - Expected performance: [based on historical data]
   - Deadline: End of day 5
   - Output: Audience ready for campaign deployment

3. **Campaign Creator**
   - Brief: "Create campaign: [campaign name]"
   - Specifications:
     - Campaign type: Search / Display / Shopping / Video / PMAX
     - Bid strategy: Target CPA / Target ROAS / Manual CPC
     - Target bid values (or ROAS/CPA targets)
     - Daily budget: $XXX
     - Keywords: [list of keyword themes / keyword list]
     - Audiences: [audience names to target]
     - Placements: [specific placements for display]
     - Landing pages: [URLs]
     - Ad groups: [structure]
     - Ads: [which ads go into which ad groups]
     - Schedule: [dayparting if applicable]
   - Outcome: Campaign in DRAFT status (not live yet)
   - Deadline: End of day 5
   - Output: Complete campaign spec ready for review

**Orchestrator Review (Day 5, afternoon):**
1. Verify all 3 deliverables are ready
2. Check campaign spec matches brief:
   - All UTM parameters correct? (utm_source=google, etc.)
   - Keywords present with match types?
   - Quality Score forecasts reasonable?
   - Bid strategy setup correct?
   - Landing pages tracked with gclid parameters?
3. Check creative assets:
   - All headline/description in compliance?
   - Text density under control?
   - Brand integrity intact?
4. Prepare launch approval request for human

---

## Phase 4B: Launch Approval Request

**Duration:** Day 5 (afternoon), delivered to human

**Format:**

```
═══════════════════════════════════════════════════════════════
CAMPAIGN LAUNCH APPROVAL REQUEST
═══════════════════════════════════════════════════════════════

Campaign Name: [name]
Campaign Type: [Search / Display / Shopping / Video / PMAX]
Status: DRAFT (not yet live)

STRUCTURE
─────────────────────────────────────────────────────────────
Ad Groups: [X]
  • [Ad Group 1] — [audience/keywords], [X] ads
  • [Ad Group 2] — [audience/keywords], [X] ads

Keywords: [X] total
  • [High-intent keywords]: [X]
  • [Mid-intent keywords]: [X]
  • [Long-tail keywords]: [X]

Ads: [X] total
  • [X] Responsive Search Ads
  • [X] Display Ads (if applicable)

BUDGET
─────────────────────────────────────────────────────────────
Daily Budget: $XXX
Monthly Estimate: $X,XXX (based on $XXX/day)

PERFORMANCE TARGETS
─────────────────────────────────────────────────────────────
Bid Strategy: [Target CPA / Target ROAS / Manual CPC]
Target CPA: $XX.XX
Target ROAS: X.XX×
Quality Score Forecast: X/10 (based on competitive keywords)

EXPECTED PERFORMANCE (First 30 Days)
─────────────────────────────────────────────────────────────
Expected Volume: [X] conversions/month
Expected Cost: $X,XXX
Expected ROAS: X.XX×
Expected CPA: $XX.XX
Confidence: [High / Medium / Low]

TRACKING SETUP
─────────────────────────────────────────────────────────────
✅ Google conversion tag on landing pages
✅ UTM parameters configured:
   utm_source=google
   utm_medium=cpc
   utm_campaign=[campaign_name]
   utm_content=[ad_group_name]
   utm_term=[keyword]
✅ GA4 integration verified
✅ gclid passing to landing pages

LAUNCH CHECKLIST (19 Items)
─────────────────────────────────────────────────────────────
✅ Campaign objective matches brand goals
✅ Bid strategy appropriate for business model
✅ Daily budget within brand_config constraints
✅ All ad groups have keywords or audiences
✅ All ads have valid headlines and descriptions
✅ All final URLs are valid and tracked
✅ UTM parameters correct on all ads
✅ Landing pages tracked with conversion tag
✅ Quality Score forecasts acceptable
✅ No brand safety issues identified
✅ Ad copy complies with brand guidelines
✅ Compliance text included (if applicable)
✅ Negative keyword list applied
✅ Geographic targeting correct
✅ Language targeting correct
✅ Device targeting (mobile, desktop, tablet) configured
✅ Dayparting configured (if applicable)
✅ Frequency cap set (if applicable)
✅ Ad schedule optimized based on historical data

RISK FACTORS
─────────────────────────────────────────────────────────────
⚠️ [Risk 1 & mitigation]
⚠️ [Risk 2 & mitigation]
☐ Learning phase: First 50 conversions, ~1-2 weeks

APPROVAL NEEDED
─────────────────────────────────────────────────────────────
☐ Approve launch with budget: $XXX/day
☐ Adjust budget to: $___/day and proceed
☐ Do not launch, make changes: [describe]

═══════════════════════════════════════════════════════════════
```

**Wait for Human Response:**
- Approval to launch
- Budget adjustments
- Any changes before launch
- Only proceed with execution after explicit approval

---

## Phase 5: Monitoring

**Duration:** Day 6 + Ongoing

**Purpose:** Monitor new campaigns/changes in learning phase and setup for next cycle.

**Monitoring Protocol:**

**Days 1-3 of New Ad Groups (Learning Phase):**
- Campaign Monitor pulls daily metrics
- Monitor for:
  - Conversion rate trends
  - CPC stability
  - Learning progress (Google AI should be optimizing)
  - Any anomalies (zero impressions, tracking failures)
- Report: Daily performance brief to human
- Action: Minimal — let Google's algorithms learn

**Days 4-6 (Scaling Phase):**
- Monitor for:
  - Quality Score stabilization
  - ROAS achievement vs. target
  - CPA stability
  - Search term performance (if Search campaign)
- Report: Daily performance brief to human
- Action: If Quality Score issues, pause problem keywords/ads and add new ones

**Daily Brief Format (from Campaign Monitor):**

```
DAILY PERFORMANCE BRIEF — [Date]
Covering: [Active Campaigns]

SUMMARY
─────────────────────────────────────────────────────────────
Total Spend Yesterday: $XXX
Total Conversions: X (AR: X)
AR ROAS: X.XX (target: X.XX)
AR CPA: $XX.XX (target: $XX.XX)
Status: [✅ ON TRACK / ⚠️ WATCH / 🚨 ALERT]

CAMPAIGN-BY-CAMPAIGN
─────────────────────────────────────────────────────────────
Campaign: [Name]
  • Spend: $XX | Conversions: X | AR ROAS: X.XX
  • Quality Scores: Avg X/10, [X] keywords <5
  • Status: [Healthy / Watch / Issue]

[Repeat for each active campaign]

ALERTS
─────────────────────────────────────────────────────────────
🚨 CRITICAL:
   • [Issue requiring immediate action]

⚠️ HIGH:
   • [Issue to address this week]

📌 MEDIUM:
   • [Issue to track]

OPPORTUNITIES
─────────────────────────────────────────────────────────────
💡 High-Converting Search Terms (add as keywords):
   • "[Search term]" — X conversions, $XX cost

💡 Scaling Opportunity:
   • [Campaign/Ad Group] hitting budget cap, strong ROAS
     Recommend: Increase by 20% (would add $XX/day)

📉 Quality Issues:
   • [X] keywords below Quality Score 5
   • Recommend: Review and replace

NEXT STEPS
─────────────────────────────────────────────────────────────
□ [Human approval needed on: ...]
□ [Monitor this: ...]
□ [Come back at cycle day 6 for full Cycle Summary]
```

**Day 6 (Cycle Close):**
- Request new 6-Day Report from Data & Placement Analyst (for next cycle)
- Begin Phase 1 of next cycle
- Cycles run continuously, overlapping

---

## Critical Timing Rules

1. **Do not start Phase 4 (Brief & Assembly) until Phase 3 (Human Approval) is complete**
   - This prevents wasted work if human rejects recommendations

2. **Do not launch campaign until Launch Approval (Phase 4B) is approved**
   - Campaign stays in DRAFT status until human says go

3. **Do not make decisions during Phase 1**
   - Phase 1 is intelligence gathering only, no recommendations yet

4. **Do not pause campaigns without human approval**
   - Even if data says to pause, present to human first

5. **Do not skip Daily Briefs during monitoring**
   - Human needs daily visibility during learning phase

---

## Exception Handling

### What if agents are BLOCKED?

If Data & Placement Analyst is BLOCKED (e.g., no campaign data, API failure):
- Orchestrator immediately escalates to human
- Cannot proceed with other phases
- Use cached data if available, note freshness
- Request Data & Placement Analyst retry or human input

### What if human doesn't respond?

- Orchestrator sends reminder after 24 hours
- Hold all actions until response
- Do not proceed without explicit approval
- Alert human to urgency if time-sensitive

### What if a campaign launches but performs poorly?

- Campaign Monitor detects the issue (ROAS below floor)
- Orchestrator escalates as CRITICAL ALERT
- Present data to human immediately
- Recommend action (pause, reduce bid, etc.)
- Wait for human approval before executing

---

## Cycle Metrics & Tracking

Track these metrics across cycles to see system improvement:

```sql
SELECT
  cycle_number,
  DATE(started_at) as cycle_start,
  SUM(daily_metrics.cost) as cycle_cost,
  AVG(daily_metrics.ar_roas) as avg_ar_roas,
  AVG(daily_metrics.ar_cpa) as avg_ar_cpa,
  COUNT(DISTINCT campaigns.id) as active_campaigns,
  COUNT(DISTINCT recommendations.id) as recommendations_made,
  COUNT(CASE WHEN recommendations.approved THEN 1 END) as recommendations_approved,
  COUNT(CASE WHEN recommendations.executed THEN 1 END) as recommendations_executed
FROM optimization_cycles
LEFT JOIN daily_metrics ON optimization_cycles.brand_id = daily_metrics.brand_id
LEFT JOIN campaigns ON optimization_cycles.brand_id = campaigns.brand_id
LEFT JOIN recommendations ON optimization_cycles.id = recommendations.cycle_id
GROUP BY cycle_number, cycle_start
ORDER BY cycle_number DESC;
```

This shows:
- Cost efficiency per cycle
- ROAS/CPA trends
- How many recommendations are approved and executed
- System learning over time

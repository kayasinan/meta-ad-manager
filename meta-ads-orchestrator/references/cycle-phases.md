# 6-Day Optimization Cycle Phases

Quick reference for the 5 optimization cycle phases, what happens in each, agent execution order, and decision logic.

## Phase Overview

Each optimization cycle runs 6 days with 5 distinct phases:

| Phase | Duration | Focus | Key Agents | Output |
|-------|----------|-------|-----------|--------|
| **1: Intelligence Gathering** | Day 1 | Collect all performance data and analysis | Data & Placement, Creative, Post-Click, Competitive Intel | 6-Day Report, Creative Assessment, Landing Page Analysis, Market Context |
| **2: Analyze & Decide** | Days 1-2 | Evaluate findings and determine action level | Orchestrator | Action Plan, Decision Matrix |
| **3: Present to Human** | Day 2 | Present recommendations for approval | Orchestrator + Human | Human Approval/Modifications |
| **4: Brief, Produce & Assemble** | Days 2-4 | Execute on approved plan | Creative Producer, Campaign Creator | New Assets, Campaign Structure |
| **5: Monitor** | Days 4-6 | Surveillance and preparation for next cycle | Campaign Monitor | Daily Reports, Next Cycle Prep |

---

## Phase 1: Intelligence Gathering (Day 1)

**Purpose:** Collect comprehensive performance data and analysis from all 7 agents.

**Parallel Execution:** Request these agents simultaneously (they can work in parallel to Supabase):

1. **Data & Placement Analyst** — 6-Day Report
   - Triple-source verified metrics (Meta, GA4 True, AR)
   - Winning/losing segments by breakdown dimension
   - Waste identification (ghost campaigns, dayparting waste, budget misallocation)
   - Cannibalization analysis
   - Audience segment recommendations
   - Tracking health status

2. **Creative Analyst** — Creative Assessment
   - Ad rankings by AR ROAS
   - Fatigue scores and threshold flags
   - Andromeda diversity audit (visual clustering)
   - Color & visual DNA analysis
   - Top ads manifest
   - Replication blueprint for winning patterns

3. **Post-Click Analyst** — Landing Page Analysis
   - Bounce rates per landing page
   - Conversion rates per page
   - Session duration metrics
   - FIX/KILL/KEEP verdicts
   - Funnel stage performance

4. **Competitive Intel Analyst** — Market Context
   - Competitor activity update
   - Trending ad formats in market
   - Estimated spend tier changes
   - New competitive threats
   - Opportunity map

5. **Campaign Monitor** — Daily surveillance reports (accumulated from previous days)
   - Current spend pace
   - Real-time alert summary
   - Anomalies detected

**Sequential Execution Required:** No — all 4 primary analysis agents can work in parallel.

**Output Consolidation:** Orchestrator reads all deliverables and creates a unified dashboard:
- What changed since last cycle?
- What's the account health snapshot?
- What decisions need to be made?

**Completion Criteria:** All 4 reports delivered (or agent is BLOCKED with clear reason)

---

## Phase 2: Analyze & Decide (Days 1-2)

**Purpose:** Evaluate all gathered intelligence and determine what action level is needed.

**Orchestrator Actions:**

1. **Cross-reference findings:**
   - Data & Placement says segment is winning BUT Post-Click says landing page bounces at 80% → Post-Click wins. Don't scale broken landing pages.
   - Creative Analyst says replicate winner BUT Data Analyst says that audience is fatigued → create variants but test on fresh segments.
   - Competitive Intel suggests new approach that contradicts historical data → allocate 10-15% test budget only.

2. **Evaluate campaign health:**
   - Load `brand_config.target_ar_roas` and `brand_config.min_acceptable_ar_roas`
   - Query `daily_metrics` for all active campaigns (last 7 days)
   - Identify campaigns:
     - Below `min_acceptable_ar_roas` for 7+ consecutive days → PAUSE RECOMMENDED
     - Between floor and target → underperforming, flag for human review
     - Above target → performing well, eligible for scaling

3. **Run Campaign Scaling Proposals** (if enabled in brand config):
   - Identify campaigns spending at 95%+ budget cap
   - Check they've maintained high ROAS for N consecutive days (per scaling_config)
   - Calculate proposed budget increases (up to 20% per step)
   - Present to human with confidence scores

4. **Determine action level needed:**
   - **Mode 1 (Ad Rotation):** Only fatigued ads need replacement. Same ad sets, just swap creatives.
   - **Mode 2 (Ad Set Changes):** New segments to add or losing segments to pause. New ad sets within same campaigns.
   - **Mode 3 (New Campaign):** Objective changed, entering new market, entire structure wrong. Build from scratch (rare).

5. **Compile prioritized action list:**
   - Sort by estimated dollar impact
   - Note which actions are quick wins vs. strategic shifts
   - Identify any dependencies or blockers

6. **Identify questions for human:**
   - Budget increases needed? How much?
   - Brand config changes (targets, volume, etc.)?
   - Any overrides to recommendations?
   - Scaling approval ready?

**Completion Criteria:** Action plan compiled, decisions made, human questions identified.

---

## Phase 3: Present to Human (Day 2)

**Purpose:** Get human approval on the recommended action plan before execution.

**Orchestrator Presentation:**

Compile and present the **Cycle Summary** including:

1. **Brand & Cycle Context**
   - Brand name
   - Cycle number
   - Date range covered

2. **Account Health Snapshot**
   - Total spend (last 7 days)
   - Average AR CPA (vs. target)
   - Average AR ROAS (vs. target)
   - Trend vs. previous cycle (↑ ↓ →)

3. **ROAS Health Status**
   - Campaigns at/above target ROAS: [count] → green
   - Campaigns between floor and target: [count] → yellow
   - Campaigns below floor for 7+ days: [count] → red (PAUSE RECOMMENDED)

4. **What's Working**
   - Top 3 performing ad sets/campaigns
   - Top performer: [name], AR ROAS [X.XX]
   - Winning audience segments
   - Best-performing landing pages
   - Opportunities identified

5. **What's Failing**
   - Bottom 3 performing ad sets/campaigns
   - Worst performer: [name], AR ROAS [X.XX]
   - Lost audience segments
   - Fatigued ads needing rotation
   - Broken landing pages (if any)
   - Waste sources quantified in $/week

6. **Recommended Actions (Prioritized)**
   - Action 1: [description] — Estimated savings: $[X]/week
   - Action 2: [description] — Estimated impact: [metric]
   - Action 3: [description] — Estimated savings: $[X]/week
   - Action level: Mode [1/2/3]

7. **Scaling Proposals** (if any)
   - Campaign [name] qualifies for budget scaling
   - Current daily budget: $[X] | Proposed: $[Y] (+[%pct])
   - AR ROAS history: [X.XX] (7-day avg, [N] days at budget cap)
   - → Approve scaling? (Yes/No)

8. **Questions Needing Human Input**
   - "What's your budget for testing [new approach]?"
   - "Should we pause [campaign] (below floor for 9 days)?"
   - "Approve [action] with estimated savings $X/week?"

**Human Response:**
- Approve (proceed to Phase 4)
- Approve with modifications (adjust plan, then proceed)
- Reject (document reasoning, plan alternative)

**Completion Criteria:** Human has reviewed and approved the action plan.

---

## Phase 4: Brief, Produce & Assemble (Days 2-4)

**Purpose:** Execute the approved plan: produce new creatives and assemble campaign structures.

**Orchestrator Actions:**

1. **Load weekly ad volume targets:**
   - Query `brand_config.weekly_ad_volume` for the brand
   - Count QUEUED items in `human_creative_inspiration` (these take priority)
   - Calculate remaining volume split: 60% Mode A (own winner replication), 40% Mode B (Competitive Intel)
   - Example: weekly_volume = 15, inspiration = 3 → 3 (inspiration) + 7 (Mode A) + 5 (Mode B) = 15 total

2. **If ad rotation needed (Mode 1):**
   - Assign Creative Producer to build replacement creatives:
     - Send: Replication Blueprint, Top Ads Manifest, Color Analysis, Andromeda Audit, fatigued ad list
     - Specify: number of variants (from weekly volume split), which mode (A or B or human inspiration)
     - Deadline: end of day 3

3. **If new ad sets needed (Mode 2):**
   - Confirm Data & Placement Analyst has built audience configs
   - Specify: targeting details, exclusions, dayparting, frequency caps
   - Specify: which campaigns these ad sets belong to

4. **If new campaign needed (Mode 3):**
   - Compile complete Campaign Brief:
     - Objective (CONVERSIONS, TRAFFIC, AWARENESS, LEAD_GEN)
     - Audiences (targeting config, exclusions)
     - Placements (feed, stories, reels, etc.)
     - Dayparting (if needed)
     - Frequency caps
     - Budget and bid strategy
     - Landing pages
     - Creative specs (Mode A/B, volume, requirements)

5. **When Creative Producer delivers assets:**
   - Assign Campaign Creator with clear instructions:
     - Mode 1: "Add these [N] ads to ad sets [list]. Pause ads [list]."
     - Mode 2: "Pause ad sets [list]. Create new ad sets [specs] with these audiences. Add these ads."
     - Mode 3: "Build new campaign per brief. Status: DRAFT."
   - Deadline: end of day 4

6. **When Campaign Creator delivers:**
   - Verify it matches the approved brief
   - Verify UTMs are correct on all ads
   - Verify audience configs match Data & Placement specs
   - Verify budget allocations match human-approved amounts

7. **Present final configuration to human for launch approval:**
   - Show: campaign structure, budget commitment, audience counts, creative lineup
   - Request: approval to go live (or adjust)

8. **On human approval:**
   - Direct Campaign Creator to execute (publish to Meta)
   - Notify Campaign Monitor: new campaigns/ad sets are live
   - Log change in `campaign_changes` table
   - Update cycle status to PHASE_5

**Completion Criteria:** Campaign structure built, reviewed, human-approved, and live (or Draft status if not ready).

---

## Phase 5: Monitor (Days 4-6)

**Purpose:** Surveillance and early warning system for the live changes.

**Campaign Monitor Actions:**

1. **Daily surveillance:**
   - Monitor new ad sets in learning phase (first 72 hours): no changes, data collection only
   - Monitor new ads in existing ad sets: no learning phase, watch for performance signals
   - Check for tracking anomalies (click-to-session drop, UTM gaps)
   - Flag any CRITICAL alerts immediately

2. **Generate daily reports:**
   - Current spend pace vs. daily budget
   - AR CPA/ROAS trends (vs. campaign targets)
   - Any new alerts raised
   - Learning phase status of new ad sets

3. **Orchestrator actions:**
   - Receive daily reports from Campaign Monitor
   - Present any CRITICAL alerts to human immediately
   - Collect these reports for next cycle's Phase 1 intelligence gathering

4. **End of Phase 5 (Day 6):**
   - Orchestrator requests new 6-Day Report from Data & Placement Analyst (covers the just-completed cycle + preview of next)
   - Prep for next cycle: back to Phase 1

**Completion Criteria:** All new changes monitored, no unresolved CRITICAL alerts, ready to start next cycle.

---

## Agent Execution Order (within a phase)

When multiple agents need to work, invoke them in this priority order:

1. **Data & Placement Analyst** (priority 1) — always first, others depend on its data
2. **Creative Analyst** (priority 2) — needs Data & Placement data
3. **Post-Click Analyst** (priority 3) — needs Data & Placement data
4. **Competitive Intel Analyst** (priority 4) — independent
5. **Creative Producer** (priority 5) — needs Creative Analyst output + Data & Placement audience specs
6. **Campaign Creator** (priority 6) — needs Creative Producer assets + Data & Placement audiences
7. **Campaign Monitor** (priority 7) — runs continuously, reports in daily

**Note:** Agents 1-4 can run in parallel. Agent 5+ run sequentially after their dependencies complete.

---

## Mode Decision Logic

**Choose Mode 1 (Ad Rotation) when:**
- Creative Analyst flags 3+ ads with fatigue scores >70
- Data & Placement Analyst says all ad sets are healthy (AR ROAS within acceptable range)
- No segment targeting changes needed
- Only action: swap out tired creatives

**Choose Mode 2 (Ad Set Changes) when:**
- Data & Placement Analyst identifies new winning segment
- OR identifies losing segment that needs pausing
- New audience specs are ready
- Existing campaign structure is sound
- Action: add/pause ad sets within same campaigns

**Choose Mode 3 (New Campaign) when:**
- Campaign objective must change (conversions → lead gen)
- Optimization event must change
- Entire campaign structure is fundamentally wrong
- Entering completely new market with different strategy
- **Rare — only when status quo is broken**

---

## Key Thresholds & Flags

Load from `brand_config`:

| Config Field | Usage | Threshold |
|--------------|-------|-----------|
| `target_ar_cpa` | Goal cost per conversion | Lower is better |
| `target_ar_roas` | Goal return on ad spend | Higher is better |
| `min_acceptable_ar_roas` | FLOOR ROAS threshold | Campaigns below this for 7+ days → PAUSE RECOMMENDED |
| `daily_budget_constraint` | Max daily spend | Hard cap, never exceed without human approval |
| `weekly_ad_volume` | Desired creative production volume | Target for Creative Producer |
| `scaling_config` | Auto-scaling proposal settings | When to propose budget increases |

---

## Cycle Completion Checklist

Before marking a cycle COMPLETED:

- [ ] Phase 1: All required reports delivered
- [ ] Phase 2: Action plan compiled and decisions made
- [ ] Phase 3: Human approved recommendations
- [ ] Phase 4: All changes built and live (or in Draft for approval)
- [ ] Phase 5: All changes monitored for 3-6 days
- [ ] Next cycle prep: 6-Day Report requested from Data & Placement
- [ ] Learnings documented for next cycle
- [ ] No unresolved CRITICAL alerts
- [ ] Cycle summary recorded in `optimization_cycles.cycle_summary`

Once all complete, mark cycle as COMPLETED and create next cycle.

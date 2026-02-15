# Alert Threshold Definitions

## Alert Severity Levels

All monitoring alerts are classified by severity to enable appropriate escalation and response timing.

---

## CRITICAL Alerts
**Escalate immediately to Orchestrator — money is at risk**

### Tracking Completely Broken
- **Condition:** Campaign spending with zero GA4 sessions for 24+ hours
- **Data Point:** GA4 sessions = 0 while Meta spend > $0
- **Impact:** Cannot attribute conversions; money spent with no tracking
- **Recommended Action:** PAUSE campaign immediately until Data & Placement Analyst investigates
- **Money at Risk:** All daily spend on affected campaign(s)

### Click-to-Session Rate Collapsed
- **Condition:** Click-to-session rate drops below 70%
- **Data Point:** CTS_rate < 0.70
- **Impact:** Large percentage of clicks not reaching your site
- **Recommended Action:** Investigate landing page, SSL, redirects, or server issues
- **Money at Risk:** Percentage difference between clicks and sessions

### CPA Spike — 3× Target or Higher
- **Condition:** AR CPA exceeds 3× the target CPA
- **Data Point:** AR_CPA > (Target_CPA × 3)
- **Impact:** Conversions are 3× more expensive than acceptable
- **Recommended Action:** PAUSE campaign, investigate audience/creative quality
- **Money at Risk:** (AR_CPA - Target_CPA) × daily conversions

### Spend Exceeds Budget Cap by 50%+
- **Condition:** Daily spend exceeds 150% of planned daily budget
- **Data Point:** Actual_spend > (Planned_budget × 1.50)
- **Impact:** Budget cap not functioning; bleeding cash
- **Recommended Action:** Check Meta account settings, verify budget cap is set, reduce bid strategy cap
- **Money at Risk:** (Actual_spend - Planned_budget) × remaining days

### Pixel Not Firing
- **Condition:** Meta Ads Manager reports pixel errors or no firing status
- **Data Point:** pixel_status = "ERROR" or "NOT_FIRING"
- **Impact:** Conversions cannot be tracked at all
- **Recommended Action:** PAUSE campaign, verify pixel ID, check website implementation
- **Money at Risk:** All campaign spend

---

## HIGH Alerts
**Escalate within 2 hours — performance is degrading**

### CPA Above 2× Target for 2 Consecutive Days
- **Condition:** AR CPA > (Target_CPA × 2) for 2+ consecutive days
- **Data Points:** AR_CPA_day1 > Target × 2 AND AR_CPA_day2 > Target × 2
- **Impact:** Consistent underperformance, trend established
- **Recommended Action:** Request Data & Placement Analyst investigate. Consider pausing if trend continues.
- **Timeline:** Flag if continues for 3rd day

### Creative Fatigue — Crossing 60 Threshold
- **Condition:** Ad fatigue score reaches or exceeds 60
- **Data Point:** Fatigue_score ≥ 60 on any active ad
- **Impact:** CTR declining, frequency too high, audience tiring
- **Recommended Action:** Request Creative Producer replacement for fatigued ad
- **Timeline:** Add replacement within 24 hours

### Meta-GA4 Discrepancy Over 40%
- **Condition:** Discrepancy between Meta-reported and GA4-verified conversions >40%
- **Data Point:** |Meta_conversions - GA4_conversions| / GA4_conversions > 0.40
- **Impact:** Severe data integrity issue; cannot trust either metric
- **Recommended Action:** Request Data & Placement Analyst investigate discrepancy source
- **Timeline:** Urgent investigation needed within 2 hours

### Learning Limited Status After 7 Days
- **Condition:** Ad set in "Learning Limited" status 7+ days after launch
- **Data Point:** status = "LEARNING_LIMITED" AND days_since_launch ≥ 7
- **Impact:** Algorithm can't find enough conversions; campaign won't scale
- **Recommended Action:** Recommend restructuring (broader audience, higher budget, or new ad set)
- **Timeline:** Restructure within 24 hours to prevent continued waste

### Audience Overlap Detected >60%
- **Condition:** New ad set audience overlaps >60% with another active ad set
- **Data Point:** overlap_percentage > 0.60
- **Impact:** Audience cannibalization; higher CPM, lower efficiency
- **Recommended Action:** Adjust audience targeting or reallocate budget between overlapping sets
- **Timeline:** Resolve within 24 hours

---

## MEDIUM Alerts
**Include in daily report, flag prominently — monitor closely**

### CPA Above Target but <2× for 2+ Days
- **Condition:** (Target_CPA × 1) < AR_CPA < (Target_CPA × 2) for 2+ consecutive days
- **Data Point:** AR_CPA between 1× and 2× target for multiple days
- **Impact:** Underperforming but not yet critical; trend watchpoint
- **Recommended Action:** Monitor for escalation. Suggest optimizations.
- **Timeline:** If continues to 5+ days, escalate to HIGH

### CTR Declining on Top-Performing Ad
- **Condition:** CTR declined >20% over past 3 days on a high-performing ad
- **Data Point:** (CTR_3days_ago - CTR_today) / CTR_3days_ago > 0.20
- **Impact:** Creative beginning to fatigue; performance degradation starting
- **Recommended Action:** Monitor fatigue score. Plan replacement if continues.
- **Timeline:** Watch daily; replace if fatigue score hits 50

### Frequency Approaching Fatigue Cap
- **Condition:** Avg frequency per user approaching fatigue threshold
- **Data Point:** Frequency ≥ (Fatigue_threshold × 0.80)
- **Impact:** Audience tiring; soon approaching diminishing returns
- **Recommended Action:** Consider ad rotation; prepare fresh creatives
- **Timeline:** Rotate within 3-5 days

### Underspending by 30%+
- **Condition:** Actual spend <70% of planned daily budget
- **Data Point:** Pacing < 0.70
- **Impact:** Not utilizing budget; fewer conversions captured
- **Recommended Action:** Loosen bid strategy cap, broaden audience, or increase budget
- **Timeline:** Adjust within 24-48 hours

### Negative Sentiment Spike
- **Condition:** Angry reactions (negative emoji) >10% of total reactions
- **Data Point:** Angry_reactions / Total_reactions > 0.10
- **Impact:** Audience rejecting ad creative; brand reputation risk
- **Recommended Action:** Pause ad, investigate creative, replace with different approach
- **Timeline:** Replace within 24 hours

---

## LOW Alerts
**Include in daily report, informational — normal fluctuations**

### Minor CPM Fluctuations
- **Condition:** CPM varies <±10% day-to-day
- **Data Point:** |CPM_today - CPM_yesterday| / CPM_yesterday < 0.10
- **Impact:** Normal auction variance; no action needed
- **Recommended Action:** Monitor for trends, but expect daily variation
- **Timeline:** No immediate action

### Small Day-Over-Day Performance Variations
- **Condition:** ROAS or CPA varies within ±5% day-to-day
- **Data Point:** Normal statistical variance within expected range
- **Impact:** Expected volatility; not actionable
- **Recommended Action:** None — normal operation
- **Timeline:** No action

### New Competitor Activity Detected
- **Condition:** Competitive Intel flags new competitor in marketplace
- **Data Point:** New competitor_ad spotted in Ad Library
- **Impact:** Market awareness only; no performance impact yet
- **Recommended Action:** Alert Creative Producer for future competitive analysis
- **Timeline:** Monitor for price/creative changes

---

## Alert Priority Matrix

| Severity | Response Time | Action Authority | Escalation Required |
|----------|---|---|---|
| CRITICAL | Immediate (<30 min) | Orchestrator decides PAUSE | YES — to human |
| HIGH | Within 2 hours | Orchestrator recommends actions | YES — if multiple |
| MEDIUM | Same-day (before EOD) | Included in daily report | No — recommended in report |
| LOW | Daily aggregation | Informational only | No — FYI only |

---

## Escalation Procedure

For CRITICAL and HIGH alerts:

1. **Quantify the impact**
   - How much money is at risk? Calculate spend-per-hour.
   - How many conversions are affected?
   - What's the trend (improving, stable, worsening)?

2. **Identify the cause** (if apparent)
   - Tracking failure? Budget cap failure? Audience exhaustion?
   - Creative fatigue? Bid strategy too restrictive?
   - Learning phase not exiting?

3. **Recommend specific action** with action level
   - Ad-level: "PAUSE [ad]: Ad #XXXX — fatigue"
   - Ad set-level: "PAUSE [ad set]: 'Men 55-64' — AR CPA 3× target"
   - Campaign-level: "PAUSE [campaign]: Campaign Q — tracking broken"
   - Investigation: "Request Data & Placement Analyst run early 6-Day Report"

4. **Deliver to Orchestrator immediately**
   - Do NOT wait for full daily report
   - Mark as urgent/CRITICAL in alerts table
   - Include dollar impact and recommended action

5. **Do NOT take action yourself**
   - Never pause campaigns, change budgets, or modify targeting
   - Wait for Orchestrator/human approval before any changes
   - Only report, recommend, and escalate

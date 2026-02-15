# Landing Page Scoring & Verdict System

## Overview

Every landing page needs a clear verdict: KEEP, FIX, or KILL. This guide explains the scoring criteria and how to apply them consistently across all pages.

## The 6 Core Metrics

### 1. Bounce Rate
**What it measures:** Percentage of sessions that ended on the landing page with zero engagement (no clicks, no page views, no events).

**Calculation:** `Bounced Sessions / Total Sessions × 100`

**Thresholds:**
- **GOOD (<40%):** User is engaging, page has relevant content or clear next step
- **WATCH (40-60%):** Some users bounce, likely relevance or clarity issue
- **BAD (>60%):** High abandonment, page is not meeting user expectations

**Interpretation:**
- <20% = Exceptional; very compelling page
- 20-40% = Healthy range
- 40-60% = Concerning; investigate
- >60% = Critical; page should be fixed or removed

**By device:**
- Mobile bounce rates naturally 10-15 points higher than desktop
- If gap >15 points beyond this natural difference, mobile issue

---

### 2. Average Session Duration
**What it measures:** How long (in seconds) users spend on the page.

**Calculation:** `Total Session Duration / Session Count`

**Thresholds:**
- **GOOD (>90s):** User is reading, exploring, considering
- **WATCH (45-90s):** User is browsing but not deeply engaged
- **BAD (<45s):** User is not reading content; immediate bounce likely

**Interpretation:**
- <10s = Page load failure or severe relevance issue
- 10-30s = Skimming only; not converting
- 30-60s = Light engagement; improving but not strong
- 60-90s = Moderate engagement; acceptable
- >120s = Deep engagement; very good

**Red flag:** If >20% of sessions <5s, page likely has technical issues (slow load, broken layout).

---

### 3. Pages Per Session
**What it measures:** How many pages does the user visit before converting or leaving?

**Calculation:** `Total Page Views / Session Count`

**Thresholds:**
- **GOOD (>2.5):** User is exploring product/content deeply
- **WATCH (1.5-2.5):** User visits 2-3 pages; mixed exploration
- **BAD (<1.5):** User barely explores; goes straight from landing to bounce

**Interpretation:**
- <1.2 = User not navigating; probably bounce
- 1.2-1.5 = Landing page → bounce (no secondary page view)
- 1.5-2.5 = Landing page → product/detail → bounce or convert
- 2.5-4.0 = Landing page → browse → compare → cart → convert (healthy funnel)
- >4.0 = Heavy browsing; strong product interest

**By page type:**
- Product landing page: typically 2-3 pages
- Blog/lead gen landing: typically 1-2 pages (should be high conversion on-page)
- Category/browse landing: typically 3-5 pages

---

### 4. Conversion Rate
**What it measures:** Percentage of sessions that result in conversion (purchase, lead form, signup).

**Calculation:** `Conversions / Sessions × 100`

**Thresholds by business model:**
- **E-commerce:**
  - GOOD: >3%
  - WATCH: 1-3%
  - BAD: <1%
- **Lead Generation:**
  - GOOD: >10%
  - WATCH: 5-10%
  - BAD: <5%
- **SaaS Signup:**
  - GOOD: >2%
  - WATCH: 0.5-2%
  - BAD: <0.5%

**Context matters:**
- For cold traffic (top funnel): expect 0.5-2%
- For warm retargeting: expect 3-10%
- For hot audience (email list): expect 10-30%

**Always compare to account average:**
- Page >20% above average = KEEP
- Page 20% below to 20% above = WATCH
- Page >20% below average = potential BAD

---

### 5. Revenue Per Session
**What it measures:** Average revenue generated per session.

**Calculation:** `Total Revenue / Session Count`

**Thresholds:**
- **GOOD:** Above account average (varies widely by product)
- **WATCH:** 50-100% of account average
- **BAD:** <50% of account average

**Example:**
- Account average revenue per session: $45
- Page A: $55 per session (GOOD)
- Page B: $30 per session (WATCH)
- Page C: $15 per session (BAD)

**Important:** A page with 2% conversion rate and $80 AOV ($1.60 revenue per session) beats a page with 5% conversion rate and $20 AOV ($1.00 revenue per session).

**Calculate total page value:**
```
Page Value = Conversion Rate × Average Order Value
Example: 2% × $80 = $1.60 per session
Example: 5% × $20 = $1.00 per session
```

---

### 6. Mobile vs. Desktop Performance
**What it measures:** Is the page performing similarly on mobile vs. desktop?

**Calculation:** `Mobile Conversion Rate / Desktop Conversion Rate`

**Thresholds:**
- **GOOD (>0.7, or 70% of desktop performance):** Mobile and desktop within 30% of each other
- **WATCH (0.4-0.7):** Mobile underperforming by 30-60%
- **BAD (<0.4):** Mobile underperforming by >60%

**Example:**
- Desktop conversion rate: 5%
- Mobile conversion rate: 4.2%
- Ratio: 4.2 / 5 = 0.84 (GOOD, only 16% gap)

**Example:**
- Desktop conversion rate: 5%
- Mobile conversion rate: 1.5%
- Ratio: 1.5 / 5 = 0.30 (BAD, 70% gap)

**Special consideration:** Meta Ads traffic is typically 60-70% mobile. If mobile is underperforming severely, the overall page performance is being dragged down.

---

## The Verdict System

### KEEP Verdict
**Criteria (must meet ALL):**
- Conversion rate ≥ account average OR revenue per session ≥ account average
- Bounce rate <50%
- No critical technical issues (ultra-short sessions, browser-specific problems)
- Mobile gap <30% (or at least matches your other good pages)

**Meaning:** This page is approved for all campaigns. Use it with confidence.

**Example:**
- Conversion rate: 4.2% (account avg 4.0%) ✓
- Bounce rate: 38% (<50%) ✓
- Avg session duration: 105s (>90s) ✓
- Mobile/Desktop ratio: 0.78 (>0.7) ✓
- Verdict: KEEP

---

### FIX Verdict
**Criteria (meets one or more):**
- Conversion rate within 50-100% of account average (not bad, but not great)
- Bounce rate 50-65% (high but not critical)
- Mobile gap 30-50% (mobile underperforming significantly)
- Technical issues that can be fixed (slow load time, mobile UX)
- Avg session duration 45-90s (moderate engagement)

**Meaning:** This page can still be used, but has specific issues to improve. Flag what needs fixing. Campaign Creator should know there's risk.

**Action:** Provide specific recommendations for fixing (mobile UX, load time, copy clarity, etc.).

**Example:**
- Conversion rate: 2.8% (account avg 4.0%, which is 70% of average) ✓ FIX condition
- Bounce rate: 52% (50-65% range) ✓ FIX condition
- Mobile/Desktop ratio: 0.55 (within 30-50% gap) ✓ FIX condition
- Verdict: FIX - "Mobile conversion rate 50% of desktop. Desktop performs well, mobile needs UX improvement."

---

### KILL Verdict
**Criteria (meets one or more):**
- Conversion rate <50% of account average (significantly underperforming)
- Bounce rate >65% (very high abandonment)
- Ultra-short sessions indicating page load failure (>20% of sessions <5s)
- Critical technical issues (broken page, SSL error, 404, blank page)
- Accounts for material spend but has near-zero conversions

**Meaning:** Do NOT use this page. Stop spending money on it. Remove from all active campaigns.

**Action:** Flag for immediate removal or replacement. Calculate wasted spend.

**Example:**
- Conversion rate: 0.8% (account avg 4.0%, which is 20% of average) ✓ KILL condition
- Bounce rate: 72% (>65%) ✓ KILL condition
- Avg session duration: 18s (<45s) ✓ KILL condition
- Verdict: KILL - "Page is severely underperforming. 72% bounce rate, 18s avg session (page load issues likely). Receiving $2,100/week spend; recommend immediate pause."

---

## Scoring Rubric

### Overall Page Score (0-100)

```
Score = (bounce_rate_score × 0.20) + (conversion_score × 0.35) + (mobile_score × 0.20) + (engagement_score × 0.15) + (revenue_score × 0.10)

Bounce Rate Score: (100 - bounce_rate_pct)
  - 40% bounce = 60 points
  - 60% bounce = 40 points

Conversion Score: (page_cr / account_avg_cr) × 100
  - 5% page CR / 4% account avg = 125 points
  - 2% page CR / 4% account avg = 50 points

Mobile Score: (mobile_cr / desktop_cr) × 100
  - 4% mobile / 5% desktop = 80 points (acceptable)
  - 2% mobile / 5% desktop = 40 points (bad)

Engagement Score: (avg_session_duration / 90) × 100
  - 120s = 133 points (capped at 100)
  - 45s = 50 points

Revenue Score: (page_rps / account_avg_rps) × 100
  - Page $50 / Account avg $45 = 111 points
  - Page $20 / Account avg $45 = 44 points
```

### Verdict by Score
- 80-100: KEEP
- 50-79: FIX (if issues are fixable)
- 0-49: KILL (if issues not worth fixing) or FIX (if quick wins available)

---

## Verdict Assignment Flow

```
START
|
├─ Conversion Rate >account average AND bounce <50%?
│  YES → KEEP
│  NO → continue
|
├─ Bounce rate >65% OR Conversion rate <50% of average?
│  YES → KILL
│  NO → continue
|
├─ Ultra-short sessions >20% OR critical technical issues?
│  YES → KILL
│  NO → continue
|
├─ Mobile gap >50% OR conversion 50-100% of average OR bounce 50-65%?
│  YES → FIX
│  NO → continue
|
└─ All metrics healthy but not exceptional?
   YES → KEEP
   NO → Investigate
```

---

## Example Page Evaluations

### Example 1: Product Landing Page

**URL:** /products/sneaker-collection

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Bounce Rate | 38% | <40% | GOOD |
| Avg Session Duration | 127s | >90s | GOOD |
| Pages Per Session | 2.8 | >2.5 | GOOD |
| Conversion Rate | 4.5% | >4.0% (account avg) | GOOD |
| Revenue Per Session | $52 | >$45 (account avg) | GOOD |
| Mobile/Desktop | 0.82 | >0.7 | GOOD |

**Verdict: KEEP**

This page exceeds or meets all thresholds. Approve for all campaigns.

---

### Example 2: Category Browse Page

**URL:** /category/mens-footwear

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Bounce Rate | 54% | 40-60% | WATCH |
| Avg Session Duration | 68s | 45-90s | WATCH |
| Pages Per Session | 3.2 | >2.5 | GOOD |
| Conversion Rate | 2.8% | 1-3% of $4% avg | WATCH |
| Revenue Per Session | $35 | 50-100% of avg | WATCH |
| Mobile/Desktop | 0.64 | 0.4-0.7 | WATCH |

**Verdict: FIX**

Issues:
- Mobile conversion rate (2.8% × 0.64 = 1.8%) is low
- Bounce rate trending high (54%)
- Revenue per session below average

Recommendation: Improve mobile UX. Desktop is fine (3.5% conversion), mobile needs attention.

---

### Example 3: Newsletter Signup

**URL:** /email-signup

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Bounce Rate | 28% | <40% | GOOD |
| Avg Session Duration | 42s | >45s | BAD |
| Pages Per Session | 1.1 | >2.5 | BAD |
| Conversion Rate | 12% | >10% (lead gen threshold) | GOOD |
| Revenue Per Session | N/A | - | - |
| Mobile/Desktop | 0.91 | >0.7 | GOOD |

**Verdict: KEEP**

Context: Lead gen page (email signup) doesn't need multiple page views or long session duration. Single-page conversion is expected. Conversion rate of 12% is strong for lead gen. Mobile/desktop parity is excellent.

---

## Monthly Audit Checklist

| Task | Frequency | Owner |
|------|-----------|-------|
| Recalculate all landing page metrics | Weekly | Post-Click Analyst |
| Review pages approaching KILL threshold | Daily | Monitoring alerts |
| Identify new high-performers | Weekly | Post-Click Analyst |
| Test potential FIX pages for improvement | Bi-weekly | Landing Page Owner |
| Remove KILL pages from active campaigns | Immediately when flagged | Campaign Creator |
| Document verdict changes and reasons | Weekly | Post-Click Analyst |

# Competitive Ad Longevity Scoring Guide

## Overview

Longevity is your proxy for competitor ad performance. An ad still running after 60+ days on Meta is a strong signal that the competitor believes it's profitable. Your job is to quantify that signal, identify the highest-confidence competitive ads worth replicating, and understand why they're succeeding.

## The Core Principle

**Longer-running ads = higher performance confidence**

Why? Competitors don't waste money on bad ads. The Meta Ads system is optimized for profitability. If an ad is still running after 60 days, the competitor has either:
1. Reached profitability (ROAS > 1.0)
2. Been testing (more risky)
3. Running a seasonal campaign (context-dependent)

Our scoring system weights longevity heavily because it's the most reliable signal we have without access to competitor performance data.

## Longevity Score (0-10)

### Base Score by Duration

| Days Running | Score | Confidence Level |
|--------------|-------|------------------|
| 1-7 days | 1-2 | Very Low (likely test) |
| 7-14 days | 2-3 | Low (testing period) |
| 14-30 days | 4-5 | Moderate (passed initial test) |
| 30-60 days | 6-7 | Good (proven at scale) |
| 60+ days | 8-9 | High (clearly profitable) |
| 90+ days | 9-10 | Very High (mature winner) |

### Example Duration Calculations

**Competitor Ad Running 75 Days:**
- First detected: December 1, 2025
- Last detected: February 14, 2026
- Duration: 75 days
- Base score: 8

**Competitor Ad Running 8 Days:**
- First detected: February 6, 2026
- Last detected: February 14, 2026
- Duration: 8 days
- Base score: 2 (too early to be confident)

## Longevity Boosters (+1 each)

### Booster 1: Multi-Placement Deployment (+1)

**What it means:** The same creative is running on multiple Meta placements (Facebook Feed, Instagram Reels, Instagram Stories, Instagram Explore, Audience Network, Messenger, etc.).

**Why it matters:** If a competitor has validated an ad enough to spend the effort deploying it across platforms, they're confident in its performance. Multi-placement deployment signals scaling.

**How to detect:**
- In Ad Library, see if the same creative/copy appears multiple times with different placement indicators
- If you see "Facebook Reels", "Instagram Stories", "Facebook Feed" all for the same creative, that's +1

**Example:**
- Ad ID: competitor_123456
- Placement 1: Facebook Feed (detected Dec 1)
- Placement 2: Instagram Reels (detected Dec 5)
- Placement 3: Instagram Stories (detected Dec 10)
- → Multi-placement scaling signal detected → +1 to longevity score

### Booster 2: Scaling Signals (+1)

**What it means:** The competitor is actively launching new ad variants with the same creative DNA or expanding the campaign.

**Why it matters:** When a competitor keeps creating similar ads (same visual style, different copy or layout), they're proving the approach works and scaling it. This is confidence in a winning formula.

**How to detect:**
- Same competitor has 3+ active ads with similar visual style
- Same competitor launching new ads in sequence (not just maintaining)
- Budget signals: multiple variants of same approach across different audiences

**Indicators of scaling:**
- Same visual style running in different ad set combinations
- New copy angles but same visual approach
- Testing different target audiences with same creative

**Example:**
- Competitor has 3 versions of the same "UGC testimonial" video style
- Each running for 30-45 days (not expired)
- Each targeting different audience (Age 25-34, Age 35-44, Age 45-54)
- → Scaling signal: confidence in UGC approach → +1 to longevity score

## Non-Additive Factors (Don't Add, But Flag)

### Seasonal Campaign
- Ad running only during holiday/season (not year-round)
- **Action:** Note as seasonal; may not apply to your business
- **Example:** Competitor runs holiday gift ads Nov-Dec, disappears Jan-May → probably not core strategy

### Brand Awareness Campaign
- Long-running but visually different from typical direct-response ads
- **Action:** Note as brand campaign; performance signal is weaker
- **Example:** Competitor runs 90-day brand story video; no clear CTA

### Test Campaign
- Competitor explicitly testing new format/message (context clue in copy)
- **Action:** Monitor for expansion; if scales to multi-placement, increase score

## Threat Assessment Layer

Beyond longevity, assess threat level:

### Threat Level: LOW (Score 1-4)
- Ad running <30 days
- Single placement
- No scaling signals
- Likely test; probably won't last

### Threat Level: MEDIUM (Score 5-6)
- Ad running 30-60 days
- Single or multi-placement
- Some scaling signals
- Proven but not yet dominant

### Threat Level: HIGH (Score 7-8)
- Ad running 60+ days
- Multi-placement deployment
- Clear scaling signals
- Strong performance signal

### Threat Level: CRITICAL (Score 9-10)
- Ad running 90+ days
- Multi-placement
- Multiple variants active
- Clear category dominance

## Mode B Replication Criteria

**Candidate for Mode B (competitor-inspired) replication if:**
1. ✓ Longevity score ≥ 7 (HIGH threat level)
2. ✓ Multi-placement deployed (confidence multiplier)
3. ✓ Creative DNA is extractable (we can understand and replicate)
4. ✓ Relevant to our audience/product (not industry-specific competitor)
5. ✓ Not already tested by us (check our creative_registry)

### Example Mode B Candidate

**Competitor: SkinCareCompanyX**
- Ad: "Real testimonials from real customers" video
- Longevity: 78 days running
- Placements: Facebook Feed, Instagram Reels, Instagram Stories
- Scaling: 4 similar UGC testimonial variants also active
- Longevity Score: 8 (base) + 1 (multi-placement) + 1 (scaling) = 10

**Assessment:**
- Threat Level: CRITICAL
- Mode B Candidate: YES (score 10, multi-placement, UGC testimonial DNA is extractable)
- Recommendation: "Test Mode B variant with similar UGC testimonial format. Allocate 10-15% test budget. 78 days running across 4 variants = proven approach."

## Competitive Landscape Example

### Skincare Vertical Market Analysis

**Competitor 1: BrandA**
- Ad 1: "Minimalist product shot" - 12 days, single placement, Score: 2
- Ad 2: "Lifestyle routine" - 67 days, Reels + Feed + Stories, 3 similar variants, Score: 10
- Ad 3: "Celebrity testimonial" - 45 days, single placement, Score: 5

Dominant approach: Lifestyle + Routine messaging
Mode B candidates: Ad 2 (score 10)

**Competitor 2: BrandB**
- Ad 1: "Before/After transformation" - 91 days, Feed + Reels, 5 variants active, Score: 10
- Ad 2: "Problem/Solution" - 34 days, single placement, Score: 4
- Ad 3: "Ingredients close-up" - 8 days, single placement, Score: 2

Dominant approach: Before/After transformation
Mode B candidates: Ad 1 (score 10)

**Competitor 3: BrandC**
- Ad 1: "UGC testimonial" - 52 days, Reels + Stories, 2 variants, Score: 7
- Ad 2: "Scientific explanation" - 19 days, single placement, Score: 3

Dominant approach: UGC testimonial
Mode B candidates: Ad 1 (score 7, borderline)

**Market Trend:** High confidence in lifestyle and before/after formats. UGC testimonials gaining traction. Minimal interest in product-only shots.

**Our Mode B Strategy:**
- Test 1: Lifestyle routine (confidence 10)
- Test 2: Before/after (confidence 10)
- Test 3: UGC testimonial (confidence 7)

## Quarterly Longevity Review

Every 90 days, re-score all competitor ads:

| Task | Frequency | Owner |
|------|-----------|-------|
| Re-pull all competitor ads from Ad Library | Weekly | Competitive Intel Agent |
| Recalculate longevity scores | Weekly | Competitive Intel Agent |
| Identify new Mode B candidates | Weekly | Competitive Intel Agent |
| Alert on significant changes (new entries, scaling) | Weekly | Competitive Intel Agent |
| Review market trends and gaps | Monthly | Competitive Intel Agent |
| Recommend Mode B tests based on top candidates | Monthly | Competitive Intel Agent |

## Pitfalls to Avoid

### Pitfall 1: Confusing Duration with Performance
**Wrong:** "Ad running 90 days = it will perform well for us"
**Right:** "Ad running 90 days with multi-placement = our competitor found a formula that works. We should test a similar approach, but our execution matters too."

---

### Pitfall 2: Over-Indexing on Recent Ads
**Wrong:** "That new ad (3 days running) must be fresh insight into market trends"
**Right:** "That ad is too new to judge. Wait 30-60 days to see if it scales. If it survives past 30 days with multi-placement, then it's a signal."

---

### Pitfall 3: Ignoring Context
**Wrong:** "Competitor ran holiday gift ad 120 days, so year-round gift ads must work"
**Right:** "That ad ran Nov-Dec, was retired Jan 1. It's not year-round strategy. Note as seasonal."

---

### Pitfall 4: Treating All Longevity Equally
**Wrong:** "That ad has longevity score 8, so it's as proven as this 90-day multi-placement ad (score 10)"
**Right:** "Both score well, but the 90-day multi-placement ad has higher confidence. Test both, but allocate more budget to the higher-confidence ad first."

---

## Summary Decision Tree

```
Is competitor ad still active in Ad Library?
├─ NO → Ad retired/paused. Still valuable but not current signal.
│
└─ YES → Calculate longevity
   ├─ <14 days?
   │  └─ Too early. Monitor. Score: 1-3
   │
   ├─ 14-30 days?
   │  ├─ Multi-placement?
   │  │  ├─ YES → Scaling. Score: 5-6
   │  │  └─ NO → Single placement test. Score: 3-4
   │  └─ Action: Monitor for multi-placement
   │
   ├─ 30-60 days?
   │  ├─ Multi-placement + scaling?
   │  │  └─ YES → Score: 7-8. Consider Mode B.
   │  ├─ Single placement?
   │  │  └─ YES → Score: 5-6. Monitor.
   │  └─ Action: If multi-placement, flag for Mode B review
   │
   └─ 60+ days?
      ├─ Multi-placement + scaling signals?
      │  └─ YES → Score: 9-10. STRONG Mode B candidate.
      ├─ Single placement?
      │  └─ YES → Score: 6-8. Moderate Mode B candidate.
      └─ Action: DEFINITELY flag for Mode B testing
```

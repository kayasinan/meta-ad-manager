# Google Ads Ad Strength Scoring

## Overview

Google Ads provides Ad Strength ratings natively for Responsive Search Ads (RSAs). This is a direct replacement for Andromeda visual clustering in the Meta system.

**Ad Strength Ratings:**
- **POOR** — Ad is missing key elements (headlines, descriptions, or final URL)
- **AVERAGE** — Ad has standard elements but could be optimized further
- **GOOD** — Ad is well-optimized with strong elements
- **EXCELLENT** — Ad has all recommended elements and high-quality copy

---

## What Drives Ad Strength

### For Responsive Search Ads (RSAs)

**Headlines:** 3 headlines required for good/excellent rating
- Variety matters: headlines should cover different angles (benefit, urgency, authority)
- Length variation: mix short and long headlines
- Pinned headlines: Google recommends avoiding overly pinned setups

**Descriptions:** 2 descriptions recommended
- Should complement headlines (not just repeat them)
- Different messaging angles across descriptions
- Include CTA or benefit statement

**Final URL & Display URL:**
- Must be valid and relevant to keywords
- Display URL should be clean and branded

**Landing Page:**
- Fast loading
- Mobile-friendly
- Matches ad promise

---

## Ad Strength Analysis Process

### Step 1: Pull Ad Strength Data from Google Ads API

```python
query = """
    SELECT
        ad.id,
        ad.name,
        ad.status,
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions,
        metrics.ad_strength,
        metrics.impressions,
        metrics.clicks,
        metrics.conversions
    FROM ad_group_ad
    WHERE segments.date >= '2026-02-08' AND segments.date <= '2026-02-14'
"""
```

### Step 2: Analyze Distribution

Count ads by strength rating:
```
POOR:        12 ads (3%)
AVERAGE:     185 ads (38%)
GOOD:        178 ads (37%)
EXCELLENT:   102 ads (22%)
```

### Step 3: Identify Missing Elements

For POOR and AVERAGE ads:
- Are headlines missing variety?
- Are descriptions too generic?
- Is the ad group missing enough headlines?
- Are descriptions too short?

### Step 4: Generate Improvement Recommendations

For each weak ad, recommend specific improvements:
```
Ad #4821 (AVERAGE):
  Current: 2 headlines, 1 description
  Recommendation: Add 1 more headline with benefit angle
  Recommendation: Add 1 more description with CTA
  Expected improvement: GOOD rating
```

---

## Correlation with Performance

**Hypothesis:** EXCELLENT-rated ads should outperform POOR-rated ads.

**Analysis:** Calculate average AR ROAS by Ad Strength rating:

```
POOR:        1.2× AR ROAS (baseline)
AVERAGE:     2.8× AR ROAS (+130%)
GOOD:        3.6× AR ROAS (+200%)
EXCELLENT:   4.2× AR ROAS (+250%)
```

**Conclusion:** Ad Strength is a strong predictor of performance. Prioritize improving POOR/AVERAGE ads.

---

## Recommendation Framework

### Priority 1: POOR Ads
**Action:** Fix or pause immediately.
- Add missing elements
- Improve landing page quality
- Or pause and rotate in replacement

**Timeline:** Fix within 48 hours or pause.

### Priority 2: AVERAGE Ads
**Action:** Improve or phase out over 2 weeks.
- Add 1-2 new headlines
- Enhance descriptions
- Test new variations

**Timeline:** Improve within 1 week or start replacement rotation.

### Priority 3: GOOD Ads
**Action:** Monitor and consider upgrading to EXCELLENT.
- Add final headline to reach all 3
- Enhance description with stronger CTA
- A/B test new angles

**Timeline:** Improve over next 2 weeks.

### Priority 4: EXCELLENT Ads
**Action:** Protect from fatigue.
- Monitor fatigue score closely
- Maintain performance
- Don't over-rotate if performing well

**Timeline:** Rotate only when fatigue score >70.

---

## Reporting Template

```
Ad Strength Distribution
========================

Total ads: 477

Strength Rating | Count | % | Avg AR ROAS | Recommendation
EXCELLENT       | 102   | 22% | 4.2×    | Maintain, watch for fatigue
GOOD            | 178   | 37% | 3.6×    | Improve to EXCELLENT
AVERAGE         | 185   | 38% | 2.8×    | Upgrade or phase out
POOR            | 12    | 3%  | 1.2×    | Fix immediately or pause

Priority Actions:
1. Fix 12 POOR ads within 48 hours
2. Improve 185 AVERAGE ads within 1 week (focus on high-impression ads first)
3. Upgrade 178 GOOD ads within 2 weeks
```

---

# 22-Point Google Ads Campaign Launch Checklist

Comprehensive pre-launch verification for all new campaigns, ad groups, and ads. All 22 points must be verified and marked PASSED before campaign goes ENABLED.

---

## Checklist Overview

| # | Category | Check | Pass/Fail |
|---|----------|-------|-----------|
| 1 | Campaign Setup | Campaign type matches brief | ☐ |
| 2 | Campaign Setup | Bid strategy matches brief | ☐ |
| 3 | Campaign Setup | Budget aligns with human approval | ☐ |
| 4 | Targeting | Geo targeting correct | ☐ |
| 5 | Targeting | Language targeting correct | ☐ |
| 6 | Schedule | Ad schedule set per analysis (dayparting) | ☐ |
| 7 | Network | Network settings correct (partners, expansion) | ☐ |
| 8 | Keywords (Search) | Keywords match theme (Search) | ☐ |
| 9 | Keywords (Search) | Keyword match types correct (distribution) | ☐ |
| 10 | Keywords (Search) | Negative keywords applied | ☐ |
| 11 | Shopping | Product groups configured (Shopping) | ☐ |
| 12 | PMax | Asset group complete (PMax) | ☐ |
| 13 | PMax | Audience signals set (PMax) | ☐ |
| 14 | Creative | RSA has 8+ unique headlines, 4 descriptions | ☐ |
| 15 | Creative | Ad Strength is GOOD or EXCELLENT | ☐ |
| 16 | Tracking | UTM parameters intact | ☐ |
| 17 | Tracking | Auto-tagging enabled (gclid) | ☐ |
| 18 | Landing Pages | Landing pages approved and match intent | ☐ |
| 19 | Extensions | Extensions configured (sitelinks, callouts) | ☐ |
| 20 | Conversions | Conversion tracking verified | ☐ |
| 21 | URLs | No broken final URLs (200 status) | ☐ |
| 22 | IDs | All ads have unique identifiers | ☐ |

---

## Detailed Checks

### 1. Campaign Type Matches Brief ✅

**What to verify:**
- Campaign type in Google Ads (SEARCH, DISPLAY, VIDEO, SHOPPING, PMAX, DEMAND_GEN)
- Matches objective specified in campaign brief

**How to check:**
- Open Google Ads campaign settings
- Confirm campaign type under "Campaign Type"
- Compare to brief: "Create new SEARCH campaign for branded terms" → Verify type = SEARCH

**Pass Criteria:**
- Campaign type = brief specification (no mismatch)

**Example:**
- Brief says: "Launch Search campaign for long-tail keywords"
- Campaign type: SEARCH ✅ PASS
- Brief says: "Launch Display campaign for remarketing"
- Campaign type: DISPLAY ✅ PASS
- Brief says: "Launch Search campaign"
- Campaign type: DISPLAY ❌ FAIL

---

### 2. Bid Strategy Matches Brief ✅

**What to verify:**
- Bid strategy selected (TARGET_CPA, TARGET_ROAS, MAXIMIZE_*, MANUAL_*, TARGET_IMPRESSION_SHARE)
- Matches brief specification

**How to check:**
- Google Ads Settings → Bidding Strategy
- Confirm strategy type

**Pass Criteria:**
- Bid strategy = brief specification
- If TARGET_CPA/TARGET_ROAS: Target value entered correctly
- If MANUAL_*: Max bids set appropriately

**Example:**
- Brief says: "Use TARGET_CPA strategy, target $30 CPA"
- Campaign settings: TARGET_CPA, target $30 ✅ PASS
- Brief says: "Use MAXIMIZE_CONVERSIONS strategy, budget $1000/day"
- Campaign settings: MAXIMIZE_CONVERSIONS, budget $1000 ✅ PASS
- Brief says: "Use TARGET_ROAS strategy, target 2.0x"
- Campaign settings: MANUAL_CPC ❌ FAIL (wrong strategy)

---

### 3. Budget Aligns with Human Approval ✅

**What to verify:**
- Daily budget matches human-approved amount
- Not exceeding approved budget
- Monthly budget estimate calculated correctly

**How to check:**
- Google Ads Settings → Budget
- Verify daily budget amount
- Calculate: Daily Budget × ~30 days = Monthly estimate
- Compare to human approval email/documentation

**Pass Criteria:**
- Daily budget matches approved amount exactly
- Monthly estimate = daily × ~30 (no rounding errors that inflate budget)

**Example:**
- Human approval: $250/day budget
- Campaign setting: $250/day ✅ PASS
- Human approval: $250/day
- Campaign setting: $300/day ❌ FAIL (exceeds approved)
- Human approval: $250/day
- Campaign setting: $250/day monthly (should be daily) ❌ FAIL

---

### 4. Geo Targeting Correct ✅

**What to verify:**
- Geographic locations match brief
- Countries/regions/cities specified as intended
- Exclusions applied if needed

**How to check:**
- Google Ads Settings → Locations
- Verify country, region, or city selections
- Cross-reference with brief: "US only" or "UK + EU" or "exclude California"

**Pass Criteria:**
- Locations match brief specification
- If brief says "US only", only US locations selected
- If brief says "exclude", exclusions applied

**Example:**
- Brief says: "Target US only"
- Campaign geo: United States ✅ PASS
- Brief says: "Target UK and EU"
- Campaign geo: United Kingdom + EU countries ✅ PASS
- Brief says: "Target US, exclude Texas"
- Campaign geo: US selected, Texas excluded ✅ PASS
- Brief says: "US only"
- Campaign geo: US + Canada ❌ FAIL

---

### 5. Language Targeting Correct ✅

**What to verify:**
- Language settings match audience
- Correct languages selected in Google Ads

**How to check:**
- Google Ads Settings → Languages
- Verify language selections
- Match to brief: "English-speaking audience" or "English and Spanish"

**Pass Criteria:**
- Language = brief specification
- If audience is English, select English
- If multilingual market, select all relevant languages

**Example:**
- Brief says: "English-speaking audience in US"
- Campaign language: English ✅ PASS
- Brief says: "Bilingual audience: English and Spanish"
- Campaign languages: English + Spanish ✅ PASS
- Brief says: "Spanish audience in Mexico"
- Campaign language: English ❌ FAIL

---

### 6. Ad Schedule Set Per Analysis (Dayparting) ✅

**What to verify:**
- Ad scheduling (dayparting) configured if recommended in brief
- Specific days/hours set if performance analysis suggests peak times

**How to check:**
- Google Ads Settings → Ad Schedule (Advanced Settings)
- Verify time/day configuration
- Cross-reference with brief: "Run all hours" or "Run Mon-Fri 9am-5pm only"

**Pass Criteria:**
- If brief specifies ad schedule, campaign matches
- If no schedule recommended, can run all hours (no schedule = all hours default)
- Day/hour restrictions are reasonable (e.g., not excluding all hours)

**Example:**
- Brief says: "Run all hours, all days"
- Campaign ad schedule: No restrictions (all day/all days) ✅ PASS
- Brief says: "Run Mon-Fri 9am-5pm only"
- Campaign ad schedule: Monday-Friday, 9:00am-5:00pm ✅ PASS
- Brief says: "Run evening hours 5pm-11pm"
- Campaign ad schedule: 5:00pm-11:00pm, all days ✅ PASS
- Brief says: "All hours"
- Campaign ad schedule: 9am-5pm only ❌ FAIL (restricts hours unnecessarily)

---

### 7. Network Settings Correct ✅

**What to verify:**
- Search Network: Google Search + Partners (on/off)
- Display Network: Managed Placement + Partner Networks (on/off)
- Video Network: YouTube + Partner Networks (on/off)

**How to check:**
- Google Ads Settings → Networks
- Verify which networks are enabled/disabled
- Cross-reference with brief

**Pass Criteria:**
- Network settings match brief
- For Search: Brief specifies if partners should be on/off
- For Display: Brief specifies if partner networks should be on/off

**Example:**
- Brief says: "Search network only, no partners"
- Campaign networks: Google Search only ✅ PASS
- Brief says: "Include search partners for scale"
- Campaign networks: Google Search + Search Partners ✅ PASS
- Brief says: "Display + partner networks"
- Campaign networks: Managed Placement + Partner Networks ✅ PASS
- Brief says: "Search only, no partners"
- Campaign networks: Google Search + Search Partners ❌ FAIL

---

### 8. Keywords Match Theme (Search Only) ✅

**What to verify:**
- Keywords semantically related to ad group theme
- Not random or off-topic
- Relevant to landing page

**How to check:**
- Review all keywords in ad group
- Compare to ad group name (e.g., "OrganicSkincare_Broad_20260214")
- Verify landing page matches keyword intent

**Pass Criteria:**
- All keywords are on-topic to ad group theme
- No keywords that seem unrelated or unintended
- Example: Ad group "OrganicSkincare_Broad" should NOT include keywords like "cheap makeup" or "hair loss treatment"

**Example:**
- Ad group: "OrganicSkincare_Broad"
- Keywords: organic skincare, natural skincare products, best organic face wash ✅ PASS (all on theme)
- Ad group: "AcneSolutions_Phrase"
- Keywords: acne treatment, acne skincare, best acne products ✅ PASS
- Ad group: "OrganicSkincare_Broad"
- Keywords: organic skincare, natural skincare, cheap makeup, hair regrowth ❌ FAIL (off-topic keywords)

---

### 9. Keyword Match Types Correct (Distribution) ✅

**What to verify:**
- Correct distribution of match types (broad/phrase/exact)
- No all-broad or all-exact (generally balanced approach)
- Match types align with funnel stage

**How to check:**
- Review keywords in ad group
- Categorize by match type (broad, phrase, exact)
- Verify distribution

**Pass Criteria:**
- Balanced distribution: Not all broad, not all exact
- Example healthy distribution:
  - Awareness ad group: 50% broad, 30% phrase, 20% exact
  - Conversion ad group: 20% broad, 30% phrase, 50% exact
- Match types support strategy (broad for scale, exact for precision)

**Example:**
- Ad group: "OrganicSkincare_Broad_Awareness"
  - Keywords: 60% broad, 30% phrase, 10% exact ✅ PASS (awareness stage, broad-leaning is correct)
- Ad group: "OrganicSkincare_Exact_Conversion"
  - Keywords: 10% broad, 20% phrase, 70% exact ✅ PASS (conversion stage, exact-leaning is correct)
- Ad group: "OrganicSkincare_Balanced"
  - Keywords: 100% broad match ❌ FAIL (no phrase/exact to refine intent)
- Ad group: "OrganicSkincare_Balanced"
  - Keywords: 40% broad, 30% phrase, 30% exact ✅ PASS (balanced distribution)

---

### 10. Negative Keywords Applied ✅

**What to verify:**
- Negative keywords configured at campaign or ad group level
- Blocking irrelevant searches (competitors, unrelated products)
- Preventing wasted spend

**How to check:**
- Google Ads Settings → Negative Keywords (campaign or ad group level)
- Review negative keyword list
- Verify commonly wasteful terms are blocked

**Pass Criteria:**
- At least 5-10 negative keywords applied per campaign (minimum)
- Blocking obvious non-converting searches (e.g., free, cheap, DIY, competitor brands)
- No valid product keywords are accidentally blocked

**Example:**
- Campaign: SEARCH_SkincareCo_US_BrandTerms
- Negative keywords: -free, -cheap, -DIY, -competitor_brand_1, -competitor_brand_2 ✅ PASS (blocking common non-converters)
- Campaign: SEARCH_SkincareCo_US_BrandTerms
- Negative keywords: (none configured) ❌ FAIL (allowing waste on irrelevant searches)
- Campaign: SEARCH_SkincareCo_US_BrandTerms
- Negative keywords: -free, -skincare (accidentally blocking core term!) ❌ FAIL (overly aggressive)

---

### 11. Product Groups Configured (Shopping Only) ✅

**What to verify:**
- Shopping campaign has product groups defined
- Categories, brands, or attributes structured appropriately
- Bid adjustments set

**How to check:**
- Google Ads: Campaign → Product Groups
- Verify group structure (by category, brand, price, condition)
- Confirm bid adjustments applied

**Pass Criteria:**
- Product groups exist (not just "All Products" default)
- Structure makes logical sense for business (e.g., by category or brand)
- Bid adjustments reflect priority (higher bids for high-margin products)

**Example:**
- Shopping campaign: SHOPPING_SkincareCo_US_AllProducts
- Product groups:
  - All Products [default] → 0% bid adjustment
  - ├─ Category: Skincare → +20% bid adjustment (high priority)
  - ├─ Category: Supplements → +10% bid adjustment
  - └─ Price > $100 → -15% bid adjustment (lower priority/exclusion)
✅ PASS (structured with bid priorities)

- Shopping campaign: SHOPPING_SkincareCo_US_AllProducts
- Product groups: Only "All Products" default, no sub-groups ❌ FAIL (no segmentation)

---

### 12. Asset Group Complete (PMax Only) ✅

**What to verify:**
- Performance Max campaign has all required assets
- Headlines (15), long headlines (5), descriptions (5)
- Images (landscape, square, ideally portrait)
- Logo and video (optional but recommended)

**How to check:**
- Google Ads PMax campaign → Asset Group
- Verify each asset type count
- Check visual content included

**Pass Criteria:**
- Minimum assets: 15 headlines, 5 long headlines, 5 descriptions, 2+ image sizes
- Recommended: Add portrait image, logo, video for higher strength

**Example:**
- PMax asset group: 15 headlines ✅, 5 long headlines ✅, 5 descriptions ✅, landscape image ✅, square image ✅, logo ✅, video ✅
✅ PASS (complete and diverse)

- PMax asset group: 10 headlines ❌ (below 15), 5 long headlines ✅, 5 descriptions ✅, landscape image ✅, square image ✅
❌ FAIL (insufficient headlines)

---

### 13. Audience Signals Set (PMax Only) ✅

**What to verify:**
- Performance Max has audience signals configured
- At least one signal: remarketing list, customer match (email), or interest/demographic

**How to check:**
- Google Ads PMax campaign → Asset Group → Audience Signals
- Verify at least one audience provided

**Pass Criteria:**
- At least 1 audience signal present (remarketing, customer match, interest segment, etc.)
- Signals are relevant to product/audience

**Example:**
- PMax campaign:
- Audience signals: Remarketing list (site visitors) + In-market audience (beauty shoppers) ✅ PASS
- PMax campaign:
- Audience signals: (none provided) ❌ FAIL (no signals = less targeted learning)

---

### 14. RSA Has 8+ Unique Headlines, 4 Descriptions ✅

**What to verify:**
- Responsive Search Ads (Search/PMax) have minimum asset count
- 8+ unique headlines (min)
- 4 descriptions (min)

**How to check:**
- Google Ads RSA → Headlines & Descriptions
- Count unique headlines (exclude duplicates)
- Count descriptions

**Pass Criteria:**
- Minimum 8 unique headlines
- Minimum 4 descriptions
- All under character limits (30 chars/headline, 90 chars/description)

**Example:**
- RSA ad: 10 unique headlines ✅ (8+ requirement), 4 descriptions ✅ ✅ PASS
- RSA ad: 6 unique headlines ❌ (<8 requirement), 4 descriptions ✅ ❌ FAIL
- RSA ad: 8 unique headlines ✅, 3 descriptions ❌ (<4 requirement) ❌ FAIL

---

### 15. Ad Strength is GOOD or EXCELLENT ✅

**What to verify:**
- Google Ads Ad Strength assessment for RSA/PMax
- Minimum "GOOD", target "EXCELLENT"

**How to check:**
- Google Ads RSA/PMax → Ad Strength indicator (Google provides score)
- If showing "Low" or "Average", improve assets

**Pass Criteria:**
- Ad Strength: GOOD or EXCELLENT (minimum)
- If showing AVERAGE/LOW: Fix and recheck before launch

**Example:**
- RSA ad strength: EXCELLENT ✅ PASS (highest quality)
- RSA ad strength: GOOD ✅ PASS (acceptable)
- RSA ad strength: AVERAGE ❌ FAIL (needs improvement: add headlines/descriptions or vary messaging)
- RSA ad strength: LOW ❌ FAIL (critical issues: too few assets or poor variety)

---

### 16. UTM Parameters Intact ✅

**What to verify:**
- Final URLs include UTM parameters
- utm_source=google, utm_medium correct, utm_campaign/content/term populated
- No truncated or broken UTM strings

**How to check:**
- Google Ads campaign/ad group → Final URL
- Verify full URL includes UTM parameters
- Example: `https://example.com/product?utm_source=google&utm_medium=cpc&utm_campaign=search_skincareco_us_brandterms&utm_content=organikskincare_broad&utm_term=organic+skincare`

**Pass Criteria:**
- utm_source=google ✅
- utm_medium=cpc (Search/Shopping) or display (Display) or video (Video) ✅
- utm_campaign populated ✅
- utm_content populated ✅
- utm_term populated (Search) or utm_placement (Display/Video) ✅
- No truncation or breaking

**Example:**
- URL: `https://example.com?utm_source=google&utm_medium=cpc&utm_campaign=search_skincareco_us_brandterms_20260214&utm_content=ad_123&utm_term=organic+skincare` ✅ PASS
- URL: `https://example.com` (no UTM parameters) ❌ FAIL
- URL: `https://example.com?utm_source=google&utm_medium=cpc&utm_campaign=...&utm_content` (truncated, utm_content value missing) ❌ FAIL

---

### 17. Auto-Tagging Enabled (gclid) ✅

**What to verify:**
- Google auto-tagging enabled in account settings
- gclid parameter will append automatically to URLs
- GA4 can receive conversion data from Google Ads

**How to check:**
- Google Ads Account Settings → Tracking → Auto-tagging
- Verify toggle is ON

**Pass Criteria:**
- Auto-tagging enabled = YES
- This allows gclid to append, connecting Google Ads clicks to GA4 sessions

**Example:**
- Auto-tagging: ON ✅ PASS (gclid will append automatically)
- Auto-tagging: OFF ❌ FAIL (GA4 attribution will break)

---

### 18. Landing Pages Approved and Match Intent ✅

**What to verify:**
- All final URLs point to approved landing pages (from Post-Click Analyst)
- Landing page content matches ad messaging
- No mismatches (e.g., ad promises "free shipping", landing page doesn't mention it)

**How to check:**
- Review ad copy vs. landing page content
- Verify landing page URL is in approved list
- Spot-check: Does ad promise match landing page delivery?

**Pass Criteria:**
- Landing page is in approved list (Post-Click Analyst verified)
- Content matches ad messaging
- User doesn't see disconnect after clicking

**Example:**
- Ad headline: "Free Shipping on Orders $50+"
- Landing page shows: "Free shipping for orders over $50" ✅ PASS (messaging aligns)
- Ad headline: "Shop Premium Skincare"
- Landing page shows: Generic homepage (no skincare promo visible) ⚠️ REVIEW (could be OK if not a high-priority ad, but ideally points to specific skincare page)
- Ad headline: "Get 20% Off"
- Landing page shows: No discount visible, top-level pricing ❌ FAIL (major disconnect)

---

### 19. Extensions Configured (Search Campaigns) ✅

**What to verify:**
- Search ads have extensions configured (sitelinks, callouts, structured snippets, etc.)
- At least 2-3 extension types present
- Extensions add value and improve CTR

**How to check:**
- Google Ads Campaign/Ad Group → Extensions (or Ad Group page shows extensions)
- Verify multiple extension types present

**Pass Criteria:**
- At least 2-3 extension types configured:
  - Sitelinks (4-6 minimum)
  - Callouts (3-4 minimum)
  - Structured Snippets (optional but valuable)
  - Call extensions (if phone number important)
  - Price/Promotion extensions (if applicable)

**Example:**
- Campaign extensions:
  - Sitelinks: Shop, Quiz, About, Coupons (4 sitelinks) ✅
  - Callouts: Free Shipping, Money-Back Guarantee, Dermatologist-Approved (3 callouts) ✅
  - Structured Snippet: Types → Cleansers, Serums, Moisturizers (1 snippet) ✅
✅ PASS (multiple extension types)

- Campaign extensions:
  - Sitelinks: None ❌
  - Callouts: None ❌
  - Other: None ❌
❌ FAIL (no extensions configured, missing CTR boost)

---

### 20. Conversion Tracking Verified ✅

**What to verify:**
- Google Conversion Tracking tag installed and firing
- GA4 event mapping configured
- Conversion events showing up in reports

**How to check:**
- Google Ads Account → Conversions
- Verify conversion action exists and is enabled
- Check Google Tag Manager or GA4 for tag status
- Review conversion counts (should show events flowing in real-time)

**Pass Criteria:**
- Google Conversion Tracking tag deployed and firing ✅
- GA4 event mapping configured ✅
- Conversion counts increasing (can verify during launch)
- No data flow errors

**Example:**
- Conversion tracking: Enabled, tag firing, data flowing ✅ PASS
- Conversion tracking: Tag not installed, no data flowing ❌ FAIL (CRITICAL)
- Conversion tracking: Tag installed but firing to wrong GA4 property ❌ FAIL (CRITICAL)

---

### 21. No Broken Final URLs (200 Status) ✅

**What to verify:**
- All final URLs respond with HTTP 200 (success)
- No 404s (not found) or 500s (server error)
- No redirects that break tracking

**How to check:**
- Manually visit each final URL (or use bulk URL checker)
- Verify page loads normally
- Check HTTP status code (ideally 200)

**Pass Criteria:**
- All URLs return 200 status
- No 404s or 500s
- Minimal redirects (1 redirect OK, but check tracking doesn't break)

**Example:**
- URL 1: `https://example.com/shop` → 200 ✅
- URL 2: `https://example.com/quiz` → 200 ✅
- URL 3: `https://example.com/old-page` → 404 (page not found) ❌ FAIL
- URL 4: `https://example.com/products` → 500 (server error) ❌ FAIL

---

### 22. All Ads Have Unique Identifiers ✅

**What to verify:**
- Each ad has unique ID (assigned by Google Ads system)
- Naming convention followed (allows easy tracking)
- No duplicate ads

**How to check:**
- Google Ads Ads list → Verify each ad has:
  - Unique ad ID (auto-assigned by Google)
  - Unique ad name following convention (e.g., A_RSA_Benefits_V1_20260214)

**Pass Criteria:**
- Each ad has unique Google ID ✅
- Ad names follow naming convention ✅
- No two ads have identical names (suggests duplication)

**Example:**
- Ad 1: ID: 123456, Name: A_RSA_Benefits_V1_20260214 ✅
- Ad 2: ID: 123457, Name: A_RSA_SocialProof_V1_20260214 ✅
- Ad 3: ID: 123458, Name: B_RSA_Testimonial_V1_20260214 ✅
✅ PASS (unique IDs, naming convention followed)

- Ad 1: ID: 123456, Name: A_RSA_Benefits_V1_20260214 ✅
- Ad 2: ID: 123456, Name: A_RSA_Benefits_V1_20260214 ❌ (duplicate ID and name)
❌ FAIL (duplication issue)

---

## Checklist Completion & Sign-Off

### Before Launching
- [ ] All 22 items verified and marked PASS
- [ ] Any FAIL items resolved and re-checked
- [ ] Campaign status still PAUSED (not yet ENABLED)
- [ ] Budget proposal ready for human review
- [ ] Campaign spec documented for Orchestrator

### Launch Approval Process
1. **Creator** → Completes 22-point checklist, marks all PASS
2. **Creator** → Delivers campaign to Orchestrator with checklist status
3. **Orchestrator** → Reviews checklist, presents to human
4. **Human** → Approves budget, bid strategy, targeting
5. **Creator** → On approval, changes campaign status PAUSED → ENABLED
6. **Monitor** → Verifies launch and begins daily monitoring

### Checklist Status Values
- **PASS (✅):** Item verified, meets criteria
- **FAIL (❌):** Item not met, needs fix before launch
- **N/A (⊘):** Item not applicable to this campaign type (e.g., keyword check for Display campaign)
- **REVIEW (⚠️):** Item OK but worth double-checking

### Final Checklist Document
```markdown
## Campaign Launch Checklist
Campaign: SEARCH_SkincareCo_US_BrandTerms_20260214
Created: 2026-02-14
Verified by: [Your Agent Name]

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Campaign type | ✅ PASS | Type: SEARCH (matches brief) |
| 2 | Bid strategy | ✅ PASS | TARGET_CPA $30 (matches brief) |
| 3 | Budget | ✅ PASS | $250/day (approved) |
| 4 | Geo | ✅ PASS | US only |
| 5 | Language | ✅ PASS | English |
| 6 | Ad schedule | ✅ PASS | All hours (no restrictions) |
| 7 | Network | ✅ PASS | Google Search + Partners on |
| 8 | Keywords theme | ✅ PASS | All on-topic to organic skincare |
| 9 | Match types | ✅ PASS | 50% broad, 30% phrase, 20% exact |
| 10 | Negative keywords | ✅ PASS | Applied: free, cheap, DIY, competitor terms |
| 11 | Product groups | N/A | Not applicable (Search campaign) |
| 12 | Asset group | N/A | Not applicable (not PMax) |
| 13 | Audience signals | N/A | Not applicable (not PMax) |
| 14 | RSA assets | ✅ PASS | 10 headlines, 4 descriptions |
| 15 | Ad strength | ✅ PASS | EXCELLENT |
| 16 | UTM params | ✅ PASS | utm_source=google, utm_medium=cpc, etc. |
| 17 | Auto-tagging | ✅ PASS | Enabled |
| 18 | Landing pages | ✅ PASS | Approved, messaging matches |
| 19 | Extensions | ✅ PASS | Sitelinks, callouts configured |
| 20 | Conversion tracking | ✅ PASS | Tag firing, GA4 flowing |
| 21 | URLs | ✅ PASS | All return 200 status |
| 22 | Unique IDs | ✅ PASS | Each ad has unique ID + naming convention |

**Overall Status: APPROVED FOR LAUNCH ✅**
All 22 checks passed. Campaign ready for human budget review and ENABLED status.
```

---

# Google Ads Naming Conventions

Standardized naming across campaigns, ad groups, and ads for consistency, trackability, and ease of analysis.

---

## Campaign Naming Format

### Standard Template
```
[TYPE]_[BRAND]_[MARKET]_[STRATEGY]_[DATE]
```

### Components

| Component | Definition | Examples | Rules |
|-----------|-----------|----------|-------|
| **TYPE** | Campaign type (SEARCH/DISPLAY/VIDEO/SHOPPING/PMAX/DEMAND_GEN) | SEARCH, DISPLAY, VIDEO, SHOPPING, PMAX, DGEN | Uppercase, no spaces |
| **BRAND** | Brand or product name (short) | SkincareCo, BeautyApp, EcommerceSite | CamelCase or abbreviated (max 15 chars) |
| **MARKET** | Geographic market / segment | US, UK, EU, CA, AU, GLOBAL | Country code or region, uppercase |
| **STRATEGY** | Campaign strategy / objective | BrandTerms, GeneralTerms, Remarketing, TopProducts, Awareness, Consideration, Conversion | Clear descriptor, PascalCase |
| **DATE** | Launch date | 20260214 | YYYYMMDD format (ISO 8601) |

### Campaign Examples

**Search Campaigns:**
- `SEARCH_SkincareCo_US_BrandTerms_20260214`
- `SEARCH_SkincareCo_UK_GeneralTerms_20260214`
- `SEARCH_SkincareCo_US_LongTail_20260214`
- `SEARCH_SkincareCo_US_Remarketing_20260214`

**Display Campaigns:**
- `DISPLAY_SkincareCo_US_Remarketing_20260214`
- `DISPLAY_SkincareCo_US_InMarket_20260214`
- `DISPLAY_SkincareCo_EU_Awareness_20260214`

**Shopping Campaigns:**
- `SHOPPING_SkincareCo_US_AllProducts_20260214`
- `SHOPPING_SkincareCo_US_BudgetFriendly_20260214`
- `SHOPPING_SkincareCo_US_PremiumOnly_20260214`

**YouTube Video Campaigns:**
- `VIDEO_SkincareCo_US_BumperAds_20260214`
- `VIDEO_SkincareCo_US_InStream_20260214`
- `VIDEO_SkincareCo_US_Discovery_20260214`

**Performance Max Campaigns:**
- `PMAX_SkincareCo_US_TopProducts_20260214`
- `PMAX_SkincareCo_US_NewCustomers_20260214`
- `PMAX_SkincareCo_EU_AllProducts_20260214`

**Demand Gen Campaigns:**
- `DGEN_SkincareCo_US_Awareness_20260214`
- `DGEN_SkincareCo_US_BudgetSegment_20260214`

---

## Ad Group Naming Format

### Search Campaigns — Template
```
[THEME]_[MATCHTYPE]_[SEGMENT]_[DATE]
```

| Component | Definition | Examples | Rules |
|-----------|-----------|----------|-------|
| **THEME** | Keyword theme / topic | OrganicSkincare, AcneSolutions, AntiAging, SkinroutineApp | PascalCase, keyword-focused (max 15 chars) |
| **MATCHTYPE** | Keyword match type | Broad, Phrase, Exact | Capitalized |
| **SEGMENT** | Audience segment / funnel stage | Awareness, Consideration, Conversion, MobileUsers, Remarketing, BudgetShopper | PascalCase (optional but recommended) |
| **DATE** | Ad group creation date | 20260214 | YYYYMMDD |

### Search Ad Group Examples
- `OrganicSkincare_Broad_Awareness_20260214`
- `OrganicSkincare_Phrase_Conversion_20260214`
- `AcneSolutions_Exact_MobileUsers_20260214`
- `AntiAging_Broad_Desktop_20260214`
- `SkinroutineApp_Phrase_AppDownloads_20260214`
- `CompetitorBrand_Broad_Remarketing_20260214` (competitor capture)

### Display/Video/Shopping Campaigns — Template
```
[THEME]_[AUDIENCE/TOPIC]_[SEGMENT]_[DATE]
```

| Component | Definition | Examples | Rules |
|-----------|-----------|----------|-------|
| **THEME** | Campaign focus / product | SkinCareInterest, BeautyAwareness, TravelDestinations | PascalCase (max 15 chars) |
| **AUDIENCE/TOPIC** | Targeting audience or content topic | Remarketing, InMarket, YouTubeBeauty, NewsCategory | Specific audience/topic name |
| **SEGMENT** | Device or sub-audience | Desktop, Mobile, HighValue, BudgetAudience | Optional, clear descriptor |
| **DATE** | Ad group creation date | 20260214 | YYYYMMDD |

### Display/Video/Shopping Ad Group Examples
- `SkinCareInterest_Remarketing_Desktop_20260214`
- `BeautyAwareness_InMarketAudience_Mobile_20260214`
- `TravelDestinations_YouTubeTravel_Desktop_20260214`
- `SkinCareProducts_InterestAudience_20260214`
- `PromotionalOffer_Remarketing_HighValue_20260214`

### Performance Max — Ad Group (Asset Group) Template
```
[PRODUCT/CATEGORY]_[OBJECTIVE]_[SEGMENT]_[DATE]
```

### Performance Max Examples
- `TopProducts_NewCustomer_Desktop_20260214`
- `SkinSerums_Conversion_Remarketing_20260214`
- `BudgetFriendly_Awareness_Mobile_20260214`

---

## Ad Naming Format

### Template
```
[MODE]_[FORMAT]_[ANGLE]_[VARIANT]_[DATE]
```

| Component | Definition | Examples | Rules |
|-----------|-----------|----------|-------|
| **MODE** | Creative production mode | A (own winners), B (competitor), BH (human inspiration) | Single letter: A, B, or BH |
| **FORMAT** | Ad format | RSA, RDA, Video, Shopping, PMax | Format abbreviation, uppercase |
| **ANGLE** | Creative angle / approach | Benefits, Testimonial, Comparison, Lifestyle, ProductHighlight, SocialProof, FOMO, ROI | Specific descriptive angle |
| **VARIANT** | Variant number or specific detail | V1, V2, V3, or specific detail (Red, Blue, Headline1) | V + number OR specific descriptor |
| **DATE** | Ad creation date | 20260214 | YYYYMMDD |

### Ad Examples

**Search RSA Ads:**
- `A_RSA_Benefits_V1_20260214` (Mode A: own winner)
- `B_RSA_PainPoint_V1_20260214` (Mode B: competitor-inspired)
- `BH_RSA_Testimonial_V1_20260214` (Mode B-H: human inspiration)
- `A_RSA_Urgency_V2_20260214` (second variant with urgency angle)
- `A_RSA_SocialProof_V3_20260214` (third variant emphasizing reviews)

**Display RDA Ads:**
- `A_RDA_Lifestyle_V1_20260214`
- `B_RDA_ProductShowcase_V1_20260214`
- `BH_RDA_LifestyleEmotional_V1_20260214`

**YouTube Video Ads:**
- `A_Video_Testimonial_15s_20260214`
- `B_Video_ProblemSolution_30s_20260214`
- `BH_Video_BrandStory_Bumper_20260214`
- `A_Video_HookTest_6s_20260214`

**Shopping Ads:**
- `A_Shopping_ProductHighlight_V1_20260214`
- `B_Shopping_PriceLeader_V1_20260214`
- `BH_Shopping_LifestylePositioning_V1_20260214`

**Performance Max Ads:**
- `A_PMax_DiverseAssets_V1_20260214`
- `B_PMax_CompetitorDNA_V1_20260214`
- `BH_PMax_HumanInspirationAssets_V1_20260214`

---

## Keyword Naming (Search Campaigns Only)

### Keyword Structure (no formal naming, but follow these conventions):

**Broad Match Keywords:**
- Format: `skincare for acne` (lowercase, two or more words, natural language)
- Use: Capture broad intent, let Google match variations
- Example keywords:
  - organic skincare
  - best acne treatment
  - natural skincare products

**Phrase Match Keywords:**
- Format: `"skincare for acne"` (quoted, lowercase)
- Use: Match specific phrase intent
- Example keywords:
  - "acne solution skincare"
  - "best organic skincare"
  - "dermatologist recommended skincare"

**Exact Match Keywords:**
- Format: `[skincare for acne]` (bracketed, lowercase)
- Use: Match exact intent, highest conversion intent
- Example keywords:
  - [buy organic skincare]
  - [dermatologist recommended skincare]
  - [acne treatment products]

**Negative Keywords (ad group or campaign level):**
- Format: `-term` (minus sign, lowercase)
- Use: Exclude irrelevant searches
- Example negative keywords:
  - -free (exclude "free skincare" searches)
  - -cheap (exclude budget hunters)
  - -DIY (exclude DIY skincare blogs)
  - -for dogs (exclude pet-related searches if not relevant)

---

## Extension Naming (Search Campaigns)

### Sitelink Extensions
- Name: `[PageName]_[Destination]`
- Examples:
  - `Shop_Products`
  - `About_Company`
  - `Quiz_SkinType`
  - `Sale_SpringPromo`

### Callout Extensions
- Name: Usually just the callout text (no formal naming, but standardized across all ads)
- Examples:
  - Free Shipping on Orders $50+
  - 30-Day Money-Back Guarantee
  - Dermatologist-Recommended
  - Ships within 24 Hours

### Promotion Extensions
- Name: `[Offer]_[Expiry]`
- Examples:
  - Spring20_20260331
  - NewCustomer15_20260228
  - Bundle_Ongoing

---

## Bid Strategy Naming (Optional but Recommended)

If you create custom bid strategies or rules:

### Format
```
[METRIC]_[TARGET]_[MARKET]
```

### Examples
- `CPA_30_US` (Target $30 CPA in US market)
- `ROAS_2_UK` (Target 2.0x ROAS in UK market)
- `EarlyMorning_+25_US` (Bid up 25% for early morning hours)
- `Mobile_-10_US` (Bid down 10% for mobile users)

---

## UTM Parameter Naming

### Campaign UTM
Format: `{campaign_id}_{campaign_name_slug}`

Example:
- Campaign: `SEARCH_SkincareCo_US_BrandTerms_20260214`
- UTM Campaign: `search_skincareco_us_brandterms_20260214` (lowercase, underscores)

### Ad Group UTM
Format: `{ad_group_id}_{ad_group_name_slug}`

Example:
- Ad Group: `OrganicSkincare_Broad_Awareness_20260214`
- UTM Content: `organikskincare_broad_awareness_20260214`

### Full URL Example
```
https://example.com/shop/skincare?
  utm_source=google
  &utm_medium=cpc
  &utm_campaign=search_skincareco_us_brandterms_20260214
  &utm_content=organikskincare_broad_awareness_20260214
  &utm_term=organic+skincare+products
```

---

## Naming Consistency Rules

### DO's ✅
- Use consistent date format (YYYYMMDD) across all levels
- Use PascalCase for multi-word names in single component
- Use lowercase in slugified versions (UTM, URLs)
- Keep brand name consistent across all campaigns/ad groups
- Use underscores to separate components, never spaces or hyphens (in most places)
- Make names descriptive enough to understand purpose without opening Google Ads

### DON'Ts ❌
- Don't use special characters (@, #, $, %) in names
- Don't use spaces (use underscores instead)
- Don't use mixed date formats (stick to YYYYMMDD)
- Don't abbreviate brand name differently across campaigns (SkincareCo vs SC vs SCCO — pick one)
- Don't use numbers that could confuse (0 vs O, 1 vs I, 5 vs S)
- Don't create ambiguous names ("Campaign1", "Test", "NewAd" — be specific)

---

## Organization Structure Example

```
SEARCH_SkincareCo_US_BrandTerms_20260214
├── OrganicSkincare_Broad_Awareness_20260214
│   ├── A_RSA_Benefits_V1_20260214
│   ├── A_RSA_SocialProof_V2_20260214
│   └── A_RSA_FOMO_V3_20260214
├── OrganicSkincare_Phrase_Conversion_20260214
│   ├── B_RSA_Testimonial_V1_20260214
│   ├── B_RSA_Comparison_V1_20260214
│   └── A_RSA_ROI_V1_20260214
└── AcneSolutions_Exact_MobileUsers_20260214
    ├── A_RSA_MobileFriendly_V1_20260214
    └── BH_RSA_MobileTestimonial_V1_20260214
```

---

## Migration Notes (From Meta to Google)

If migrating campaigns from Meta Ads:
- Use similar brand names for continuity
- Map Meta campaign objectives to Google campaign types:
  - Meta "Conversions" → Google SEARCH or SHOPPING
  - Meta "Traffic" → Google DISPLAY or DEMAND_GEN
  - Meta "Awareness" → Google DISPLAY or VIDEO
  - Meta "Video Views" → Google VIDEO
- Update naming to Google convention as you create new campaigns (don't try to rename Meta-created campaigns retroactively)
- Keep ad group names specific to Google context (keywords for Search, audiences for Display)

---

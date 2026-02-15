# Creative Selection Engine — Weekly Ad Production Logic

## Overview
Instead of always cloning top 3 winners, the system maintains a **scored creative library** built from a 2-year analysis, and uses a weighted selection engine to pick diverse directions each cycle.

---

## Phase 1: Calibration (One-Time)
- Pull last 3 months (Nov 17 – Feb 15, 2026) where both Meta and GA4 data exist
- Calculate exact ratio at **ad level**: Meta ROAS vs AR ROAS
- Establish a single discount factor (Meta over-reports ~25%)
- Validate across spend tiers
- Output: `discount_factor` (e.g., 0.78)

## Phase 2: 2-Year Ad Pull (One-Time)
- Pull ALL ads from last 24 months via Meta API
- Apply discount factor → **Estimated Real ROAS** per ad
- Filter: Est. Real ROAS ≥ 3x AND spend ≥ $50
- Store in Supabase `creative_library` table

## Phase 3: Creative Cataloging (One-Time)
- Download image/thumbnail + ad copy for every qualifier
- Tag each ad:
  - `product` — NexGard, Simparica, Heartgard, etc.
  - `visual_theme` — cute dog, product-focused, lifestyle, seasonal
  - `color_scheme` — light/dark, dominant colors
  - `copy_angle` — price, trust, benefits, urgency, social proof
  - `format` — static, carousel, video, catalog
  - `season` — when it ran
  - `est_real_roas` — calibrated ROAS
  - `spend` — total lifetime spend
- Store in Supabase `creative_library` table

## Phase 4: Diversity Mapping (One-Time)
- Cluster ads by visual similarity → identify "creative families"
- Build coverage matrix: Product × Theme × Angle × Color
- Flag hidden gems (3-5x ROAS, never scaled)
- Flag gaps (combos never tried)
- Store clusters in Supabase `creative_clusters` table

## Phase 5: Variation Briefs (One-Time)
- **Cluster A** (top winners, ROAS ≥ 6x): Slight variations only — these are proven
- **Cluster B** (mid-performers, ROAS 3-5x): Bolder variations, new copy angles, color swaps
- **Cluster C** (underexplored combos): Net-new creatives inspired by working elements
- Target: **15-20 diverse creative directions**

---

## Weekly Selection Engine (Every Cycle)

### Scoring Formula

Each creative direction gets a composite score (0-100):

| Factor | Weight | Scoring Logic |
|--------|--------|---------------|
| **Historical ROAS** | 30% | Normalized: (est_real_roas - 3.0) / (max_roas - 3.0) × 100 |
| **Freshness** | 25% | Days since last used in a new ad. Never used = 100. Used this cycle = 0. Linear decay over 8 weeks. |
| **Cluster Diversity** | 20% | If this week's batch already has N ads from this cluster: score = max(0, 100 - N×50). Forces spread across clusters. |
| **Product Coverage** | 15% | If this week's batch is missing this product: 100. Already has it: 0. Ensures product mix. |
| **Fatigue Risk** | 10% | LOW fatigue = 100. MODERATE = 50. HIGH = 0. Based on Agent 2's latest fatigue scoring. |

### Composite Score
```
score = (roas_score × 0.30) + (freshness_score × 0.25) + (diversity_score × 0.20) + (coverage_score × 0.15) + (fatigue_score × 0.10)
```

### Selection Process (Each Cycle)

```
1. Agent 2 delivers: updated fatigue status for active ads
2. Load creative_library + creative_usage_log from Supabase
3. Score every direction using the 5 factors
4. Sort by composite score (highest first)
5. Pick top 5-6, enforcing hard rules:
   - Max 2 ads from same cluster
   - Min 2 different products
   - Min 2 different copy angles
   - Min 1 from Cluster B or C (mid-performers or untested)
6. Agent 5 generates variations of the selected 5-6
7. Log selections to creative_usage_log
```

### Hard Rules (Override Scores)
- **Max 2 per cluster** — even if Cluster A has the top 6 scores, only 2 get picked
- **Min 2 products** — if first 3 picks are all NexGard, force next pick to different product
- **Min 1 fresh direction** — at least 1 pick must be from Cluster B/C (not top winners)
- **Never reuse within 4 weeks** — if a direction was used in the last 4 weeks, hard block

### Supabase Tables

**`creative_library`** (populated by Phase 2-4)
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| brand_id | uuid | FK to brands |
| ad_id | text | Original Meta ad ID |
| ad_name | text | Ad name |
| image_url | text | Creative image URL |
| product | text | Product shown |
| visual_theme | text | Theme category |
| color_scheme | text | Dominant colors |
| copy_angle | text | Messaging angle |
| copy_headline | text | Original headline |
| copy_body | text | Original body text |
| format | text | static/carousel/video/catalog |
| cluster_id | text | Cluster assignment |
| cluster_tier | text | A (top) / B (mid) / C (explore) |
| est_real_roas | numeric | Calibrated ROAS |
| meta_roas | numeric | Raw Meta ROAS |
| spend | numeric | Lifetime spend |
| created_at | timestamptz | When cataloged |

**`creative_usage_log`** (populated each cycle)
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| brand_id | uuid | FK to brands |
| library_id | uuid | FK to creative_library |
| cycle_id | uuid | FK to optimization_cycles |
| used_at | timestamptz | When selected |
| variation_type | text | What was changed from source |
| result_ad_id | text | Meta ad ID of the generated ad |

**`creative_clusters`** (populated by Phase 4)
| Column | Type | Description |
|--------|------|-------------|
| id | text | Cluster identifier |
| brand_id | uuid | FK to brands |
| name | text | Human-readable cluster name |
| tier | text | A / B / C |
| description | text | What defines this cluster |
| member_count | int | Number of ads in cluster |
| avg_roas | numeric | Average est. real ROAS |

---

## Lifecycle

```
ONE-TIME SETUP:
  Phase 1 (Calibration) → Phase 2 (Pull) → Phase 3 (Catalog) → Phase 4 (Map) → Phase 5 (Briefs)
  
EVERY CYCLE:
  Agent 2 (fatigue update) → Selection Engine (score + pick 5-6) → Agent 5 (generate) → Agent 6 (create PAUSED)
  
QUARTERLY REFRESH:
  Re-run Phase 2-4 to capture new ads that performed well
```

---

*This document defines the creative selection strategy. All changes must be pushed to the GitHub repo.*

---

## Human Creative Input (Test & Learn)

### How It Works
Sinan (or team) can submit a sample creative at any time — an image, a concept sketch, a competitor screenshot, or a text brief. The system treats it as a **test candidate** alongside the scored selections.

### Input Flow
```
Human sends sample creative (image/concept/brief)
        │
        ▼
Agent 5 (Creative Producer):
  1. Generates the submitted concept as-is (faithful to input)
  2. Generates 2-3 variations (different copy, color, product combos)
  3. QC scores all variants
        │
        ▼
Agent 6 (Campaign Creator):
  Creates test ads PAUSED alongside the regular cycle ads
  Tags: source = "human_input", test_id = unique ref
        │
        ▼
Agent 7 (Campaign Monitor):
  Tracks performance after launch
  After 7 days with sufficient data (spend ≥ $50):
    - ROAS ≥ 3x → ✅ WINNER — added to creative_library as new direction
    - ROAS < 3x → ❌ LEARNED — logged but not reused
```

### Supabase Tracking

**`creative_tests`** table:
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| brand_id | uuid | FK to brands |
| submitted_by | text | Who submitted (e.g., "sinan") |
| submitted_at | timestamptz | When submitted |
| input_type | text | image / concept / brief / competitor |
| input_description | text | What was submitted |
| input_image_url | text | Image if provided |
| status | text | PENDING / TESTING / WINNER / LEARNED |
| test_ad_ids | text[] | Meta ad IDs created for testing |
| result_roas | numeric | Actual ROAS after test period |
| result_spend | numeric | Spend during test |
| added_to_library | boolean | Whether it graduated to creative_library |
| library_id | uuid | FK if added |
| notes | text | Learnings from the test |

### Selection Engine Integration
- Human inputs get **automatic slot reservation**: 1-2 of the 5-6 weekly slots are reserved for test candidates when available
- Regular scored selections fill the remaining 3-4 slots
- If no human input that week, all 5-6 slots go to scored selections
- Once a test creative becomes a WINNER, it enters the regular scoring system with its own cluster assignment

### Feedback Loop
```
WINNER path:
  Test ad ROAS ≥ 3x
  → Added to creative_library with real performance data
  → Assigned to existing cluster or creates new cluster
  → Enters regular scoring rotation
  → Variations of it will be created in future cycles

LEARNED path:
  Test ad ROAS < 3x
  → Logged in creative_tests with notes on why
  → NOT added to creative_library
  → Similar concepts get a penalty in future scoring
  → Learnings inform the "never-produce" list if pattern emerges
```

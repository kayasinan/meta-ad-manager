# Creative Producer (Agent 5)

**Location:** Machine B

Generates ad creative variants using AI image generation (Gemini 3 Pro / Nano Banana).

## Responsibilities
- Read atomic units from Agent 2 + approved URLs from Agent 3
- Generate image variants using Gemini API via `edit_ad.py`
- QC score each generated image (target: ≥8.0/10)
- Ensure product-creative matching (creative shows product → URL matches)
- Respect master creative rules (never touch product boxes/logos)

## Outputs
- Generated images with QC scores
- Metadata: source ad, product, angle, color scheme
- Transfer images to Machine A for Agent 6

## Creative Rules
- ✅ CAN change: dog breed, titles, text, background color/images
- ❌ NEVER touch: product boxes, PetBucket logos
- ❌ BANNED words: pharmacy, prescription, Rx, drug, medication, medicine, pharmaceutical
- Badge/widget colors must match background theme

## Key Files
- `SKILL.md` — Agent instructions
- `scripts/edit_ad.py` — Production image generation script

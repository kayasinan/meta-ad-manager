---
name: meta-ad-creator
description: Generate Meta (Facebook/Instagram) ad creative variants using DALL-E 3. Analyze top-performing ads, define winning creative formulas, then batch-generate professional ad variants with swappable elements (subjects, colors, headlines). Use when creating ad creatives, generating ad variants, refreshing ad fatigue, or building Meta ad campaigns.
---

# Meta Ad Creator

Generate production-ready Meta ad variants. Supports two modes:

1. **Edit mode (Gemini / Nano Banana Pro)** — Edit existing winning ads: swap background colors and badge text while keeping product boxes + logos pixel-perfect. Best for creating variations of proven ads.
2. **Generate mode (DALL-E 3)** — Generate completely new ads from scratch with swappable subjects, colors, and headlines. Best for exploring new creative directions.

## Quick Start

### Edit an existing ad (recommended)

```bash
# Single edit with custom text
uv run {baseDir}/scripts/edit_ad.py \
  --input /path/to/winning_ad.jpg \
  --color "Peach (#FFDAB9)" \
  --badges "SAVE 50% VS VET PRICES" "ONE CHEW. TOTAL PROTECTION" "FREE SHIPPING OVER \$49" \
  --output ./output/variant.png \
  --resolution 2K

# Batch: auto-generate text variations from an ad
uv run {baseDir}/scripts/edit_ad.py \
  --input /path/to/winning_ad.jpg \
  --variations 5 \
  --output ./output/ \
  --resolution 2K

# Batch from config file
uv run {baseDir}/scripts/edit_ad.py \
  --config variants.json \
  --output ./output/ \
  --resolution 2K
```

### Generate from scratch (DALL-E 3)

```bash
python3 {baseDir}/scripts/generate_ads.py \
  --config variants.json --output ./output/ --quality hd --style natural

python3 {baseDir}/scripts/create_gallery.py ./output/
```

## Edit Mode Workflow (Gemini)

### Phase 1: Identify Editable Elements

For each source ad, identify:
- **Editable:** Background color, badge/widget text, icons, dog/animal (if separate from product box)
- **Locked:** Product boxes, brand logos, dogs ON product boxes, FDA text

**MASTER RULE:** Never touch product boxes or logos. If the dog is part of the product box, it's locked too. If the dog is a separate element (standing/sitting next to the product), it CAN be swapped.

### Dog Breed Swapping

When the source ad has a separate dog (not printed on the product box), you can swap the breed. This is one of the most powerful creative levers — different breeds resonate with different audiences.

```bash
# Swap the dog breed
uv run {baseDir}/scripts/edit_ad.py \
  --input winning_ad.jpg \
  --dog "French Bulldog puppy, fawn coat, big round eyes" \
  --color "Lavender (#E8DAEF)" \
  --badges "SAVE 50% VS VET" "TRUSTED BY 500K+" "FREE SHIPPING" \
  --output variant.png

# Auto-generate variants with different breeds
uv run {baseDir}/scripts/edit_ad.py \
  --input winning_ad.jpg \
  --variations 6 \
  --swap-dogs \
  --output ./variants/
```

#### Proven dog breeds for pet product ads:
| Breed | Appeal | Best For |
|-------|--------|----------|
| Golden Retriever | Universal, family-friendly | Broad audiences, 45+ |
| French Bulldog | Trendy, urban | Younger demos 25-44 |
| Labrador | Trustworthy, active | Family audiences |
| Beagle | Curious, cute | Emotional hooks |
| Husky | Striking, eye-catching | Scroll-stopping |
| Corgi | Adorable, social media favorite | Engagement |
| Pomeranian | Fluffy, small dog owners | Small breed products |
| German Shepherd | Strong, protective | Protection messaging |

#### Dog swap prompt formula:
```
Replace the dog with a [BREED] ([coat description], [expression], 
looking at camera, photorealistic studio quality).
```
Always specify: breed, coat/color details, expression, "looking at camera", "photorealistic".

### ⚠️ BANNED WORDS — Never use in badge/banner text:
- **pharmacy** / **online pharmacy**
- **prescription** / **Rx**
- **drug** / **medication** / **medicine** / **pharmaceutical**

These trigger ad rejections and compliance issues. The script auto-validates and blocks any badge text containing banned words.

### Phase 2: Define Variations

Each variation changes:
- **Background color** — solid colors that contrast with the product
- **Badge text** — 3 badges with different marketing angles

#### Proven Text Angle Categories

| Category | Example Badges |
|----------|---------------|
| **Price/Value** | "SAVE UP TO 50% VS VET PRICES", "75% CHEAPER THAN YOUR VET" |
| **Social Proof** | "TRUSTED BY 500K+ PET PARENTS", "4.9★ FROM 12,000+ REVIEWS" |
| **Shipping/Speed** | "FREE SHIPPING OVER $49", "SHIPS SAME DAY TO YOUR DOOR" |
| **Product Benefits** | "ONE CHEW PROTECTS AGAINST 5 PARASITES", "KILLS FLEAS, TICKS & WORMS" |
| **Trust/Authority** | "#1 ONLINE PET PHARMACY", "100% GENUINE PRODUCTS GUARANTEED", "VET-RECOMMENDED" |
| **Urgency** | "LIMITED TIME: EXTRA 10% OFF", "DON'T WAIT UNTIL IT'S TOO LATE" |

### Phase 3: Generate & QC

The edit script:
1. Sends the original image + edit prompt to Gemini 3 Pro Image (Nano Banana Pro)
2. Gets back an edited 2K image (2048×2048)
3. Runs QC check: scores professional quality, text readability, color consistency, artifacts, brand integrity (1-10 each)
4. Only saves images that pass QC (average ≥ 7)

### Phase 4: Review

Build HTML gallery for side-by-side comparison with the original.

## Variant Config Format (Edit Mode)

```json
{
  "source": "/path/to/winning_ad.jpg",
  "locked_elements": "Product box, PetBucket logo, FDA text, 6 PACK label",
  "variants": [
    {
      "color_name": "Peach",
      "color_hex": "#FFDAB9",
      "badges": ["75% CHEAPER THAN YOUR VET", "LOVED BY 500K+ DOG OWNERS", "FAST FREE DELIVERY TO YOUR DOOR"],
      "filename": "variant-peach-value.png"
    },
    {
      "color_name": "Lavender",
      "color_hex": "#E8DAEF",
      "badges": ["SAVE UP TO 50% VS VET PRICES", "TRUSTED BY 500K+", "FREE SHIPPING"],
      "dog_breed": "French Bulldog",
      "dog_desc": "adorable French Bulldog puppy with fawn coat, big round eyes, looking at camera",
      "filename": "variant-lavender-frenchie.png"
    }
  ]
}
```

## Auto-Variation Mode

When using `--variations N`, the script auto-generates N different text + color combos by mixing:
- **Colors:** Navy, Peach, Mint, Coral, Powder Blue, Lavender, Light Yellow, Soft Gray
- **Text angles:** Rotates through Price, Social Proof, Shipping, Benefits, Trust, Urgency

This is the fastest way to generate multiple A/B test variants from a single winning ad.

## Cohesive Color Design

Badge/widget colors automatically adapt to match the background theme. When the background is peach, badges become warm coral/brown tones — not stuck on the original green. The prompt instructs Gemini to create a unified color palette across background, badges, text, and accents.

## Creative Metadata Registry

Every generated creative auto-saves metadata to `/data/creative_meta/registry.json`. This enables closed-loop analysis: when ads go live on Meta, match ad ID → creative metadata → performance data to find which attributes drive the best ROAS.

### Tracked attributes per creative:
| Attribute | Example |
|-----------|---------|
| `source_ad` | WINNER_Static_2.jpg |
| `source_ad_roas` | 6.1 |
| `product_box` | Simparica TRIO |
| `background_color_name` + `_hex` | Peach / #FFDAB9 |
| `badge_text` | ["75% CHEAPER", "LOVED BY 500K+", "FREE DELIVERY"] |
| `text_angle` | price / social_proof / benefits / urgency / trust |
| `creative_theme` | standard / premium / summer / emotional / urgent |
| `headline` | "YOUR DOG DESERVES BETTER THAN FLEAS" |
| `model_used` | gemini-3-pro-image |
| `qc_score` | 9.4 |
| `meta_ad_id` | (linked when uploaded to Meta) |
| `status` | draft → uploaded → live → analyzed |

### Analysis example:
```
"Peach + price angle → avg 4.2x ROAS"
"Mint + social proof → avg 2.8x ROAS"
→ Generate more peach/price variants
```

## API Keys

- **Gemini (edit mode):** `GEMINI_API_KEY` env var — get one at https://aistudio.google.com/apikey
- **OpenAI (generate mode):** `OPENAI_API_KEY` env var

## References

- **Prompt formulas** for different verticals: See `references/prompt-formulas.md`
- **Winning creative patterns** from Meta Ads analysis: See `references/winning-patterns.md`


## ⚠️ DOUBLE-CONFIRMATION RULE (MANDATORY)
Before executing ANY campaign change (pause, enable, create, modify budgets, targeting, creatives, bids, exclusions, or any other modification), you MUST:
1. Present the proposed changes clearly to the user
2. Ask for explicit confirmation ONE MORE TIME before executing
3. Only proceed after receiving that second confirmation
This applies to ALL changes — no exceptions. This prevents accidental modifications.

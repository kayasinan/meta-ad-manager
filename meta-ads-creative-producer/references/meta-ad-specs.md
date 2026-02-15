# Meta Ads Creative Specifications

## Image Placement Dimensions

| Placement | Dimensions | Aspect Ratio | Minimum Size | Notes |
|-----------|-----------|-------------|--------------|-------|
| Feed (Facebook/Instagram) | 1080×1080 | 1:1 | 600×600 | Optimal for carousel and single image ads |
| Feed (4:5) | 1080×1350 | 4:5 | 600×750 | Taller format, uses more mobile space |
| Stories/Reels | 1080×1920 | 9:16 | 600×1067 | Full-screen vertical format |
| Link Ads | 1200×628 | 1.91:1 | 600×314 | Text overlay safe zone: bottom 20% covered |
| Right Column (Desktop) | 1200×1200 | 1:1 | 254×133 | Small format, text must be large |
| Carousel (per card) | 1080×1080 | 1:1 | 600×600 | All cards must share same aspect ratio |
| Audience Network | 1080×1920 | 9:16 to 16:9 | 398×208 | Varies by publisher |

---

## File Requirements

| Requirement | Value |
|-------------|-------|
| Format | JPG or PNG |
| Max File Size | 30 MB per image |
| Aspect Ratio Tolerance | 3% (Meta auto-crops outside this) |
| Minimum Resolution | 1080px on shortest edge |
| Recommended Resolution | 2048px for high quality |

**Format Selection Guidelines:**
- **JPG**: Use for photographs, lifestyle images, product photos (smaller file size, no transparency needed)
- **PNG**: Use for graphics with transparency, logos, illustrations with transparent backgrounds

---

## Text Overlay Rules

### Hard Text Coverage Limit
**Maximum text coverage: ≤20% of image area (hard limit)**

- Meta removed the official 20% text rule in 2021, but the algorithm still penalizes text-heavy images with reduced delivery and higher CPMs
- This is not optional guidance — it directly affects ad performance
- **Images exceeding 20% text coverage FAIL QC automatically, regardless of other quality scores**

### What Counts as Text
- Badge overlays (price, discount, social proof)
- CTA text on the image (not Meta's CTA button — that's separate)
- Watermarks with text
- Logo text (brand name in the logo)

### What Does NOT Count as Text
- Product packaging text (text that's physically part of the product photo)
- Lifestyle imagery that happens to contain text (e.g., store sign in background)

### Text Consolidation Rule
If the creative brief requires heavy text (e.g., "50% OFF + FREE SHIPPING + LIMITED TIME"):
- Consolidate into ONE badge/overlay, not multiple scattered text elements
- Use Meta's ad copy fields (primary text, headline, description) for your message, not the image itself

---

## Stories/Reels Safe Zones

Stories and Reels have UI elements that cover parts of the image:

| Zone | Coverage | Content | Safe Margin |
|------|----------|---------|------------|
| Top | 14% | Status bar, account name | KEEP CLEAR |
| Bottom | 35% | CTA button, swipe-up area | KEEP CLEAR |
| Sides | 6% | Edge padding for device widths | KEEP CLEAR |
| Safe Area | Middle 50% | Place badges and key text here | USE THIS |

**Critical:** Place all badges, text overlays, and key visual elements in the middle 50% of the vertical canvas for Stories/Reels.

---

## Text Character Limits (Ad Copy Fields)

| Field | Optimal Length | Maximum Before Truncation | Notes |
|-------|---|---|---|
| Primary Text | 125 chars | 125 | Truncated with "...See More" if exceeded |
| Headline | 27 chars (Feed), 40 chars (other) | 40 | Different limits by placement |
| Description | 18-30 chars | 30 | Keep concise |
| Carousel Headline (per card) | 45 chars | 45 | Tested limit per card |

---

## Color Palette Best Practices

### Cohesive Color Design
Generate a unified color palette — not just a background swap:
- When background is peach, badges become warm coral/brown tones
- Text colors complement the background
- Accents create visual harmony
- No generic badges slapped on every variant

### Data-Driven Color Selection
Color choices must be extracted from winning ad performance:
- Exact color schemes from top-performing ads (background colors + coverage %)
- Badge colors that performed well
- Contrast levels that work (not too subtle, not too jarring)
- Mood and harmony type (warm, cool, neutral, complementary)

---

## Image Quality Standards

### Resolution & Clarity
- Minimum 1080px on shortest edge for all formats
- 2048px preferred for maximum quality
- No blurry, low-res, or amateur-looking images
- Professional polish required — looks like a real, polished ad

### Artifact-Free
- No AI generation weirdness: extra fingers, melted text, warped edges, uncanny faces
- No overlapping text or cut-off elements
- No color banding or posterization
- No visible compression artifacts

### Brand Integrity
- Product imagery untouched and pixel-perfect
- Brand logo position and style preserved
- Compliance/legal text unchanged
- No distortion of locked elements

---

## Creative Format Guidelines

### Static Images
- Clean, professional composition
- Product clearly visible and identifiable
- Single focal point or clear visual hierarchy
- Text minimal and legible at all sizes

### Video Concepts
- Hook: first 1.5 seconds must grab attention
- Pacing: mobile-first (vertical, fast cuts)
- Audio: music type, voiceover style, or text-only for sound-off
- Text overlays: visible and readable without sound
- Production style: UGC, studio, screen recording, or animation

### Carousel Ads
- Best-performing card in position 1
- Each card: image + headline (max 45 chars)
- Card flow: storytelling sequence or feature progression
- Consistent visual style across all cards
- Remove or replace underperforming card types

---

## Validation Checklist

Before submission, verify:

- [ ] File format is JPG or PNG (not WEBP, BMP, etc.)
- [ ] File size ≤ 30 MB
- [ ] Dimensions match placement requirements (within 3% tolerance)
- [ ] Minimum 1080px on shortest edge (2048px preferred)
- [ ] Text coverage ≤ 20% of image area
- [ ] Stories/Reels: no critical content in top 14%, bottom 35%, or sides 6%
- [ ] All text is readable and properly positioned
- [ ] No spelling/grammar errors in any text
- [ ] Colors are cohesive and match brand palette
- [ ] No AI artifacts or distortions
- [ ] Product imagery and logo are pixel-perfect
- [ ] Image passed QC pipeline (automated scoring)
- [ ] Copy text within character limits
- [ ] Landing page URL from approved list
- [ ] UTM parameters correctly configured

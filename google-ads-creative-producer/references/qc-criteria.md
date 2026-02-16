# QC Pipeline — 7-Point Quality Criteria for Google Ads Creatives

Quality assurance standard for all creative assets before marking DELIVERED. Every asset must pass all 7 checks.

---

## 1. Professional Quality

### Images
**Pass Criteria:**
- Professional photography or design (not amateur/stock images)
- Proper color grading and white balance
- Sharp focus on subject (no blur unless intentional motion blur)
- Appropriate resolution (minimum 1200px on largest dimension)
- No visible watermarks or attribution text
- Lighting is even and flattering (for product/lifestyle)
- Composition follows rule of thirds or clear visual hierarchy
- No visible dust, scratches, or sensor artifacts

**Fail Criteria:**
- Low-quality/pixelated image
- Obvious watermarks or branding from stock sites
- Under-lit or over-exposed
- Blurry or out-of-focus subject
- Visible compression artifacts
- Appears AI-generated with aesthetic issues (oversaturation, unnatural colors)

### Video
**Pass Criteria:**
- Steady framing (no shaky camera work unless stylistically intentional)
- Proper white balance and color grading
- Professional audio (clear narration/voiceover, minimal background noise)
- Smooth transitions and editing
- Professional titles/graphics (not amateurish)
- No visible lens artifacts or technical issues
- Proper aspect ratio for platform (16:9 for YouTube)

**Fail Criteria:**
- Shaky footage or unstable camera work
- Color grading is off (too saturated, wrong white balance)
- Audio is muffled, distorted, or unintelligible
- Abrupt transitions or poor editing
- Poorly designed text overlays
- Pixelation or compression artifacts
- Aspect ratio wrong for platform

**Scoring:**
- Professional Quality Score: 1-10 (7+ is Pass)

---

## 2. Text Readability

### Font Size & Visibility
**Pass Criteria:**
- Body text minimum 12pt (equivalent) when displayed
- Headline text minimum 18pt (equivalent)
- Text is not obscured by other elements
- Sufficient padding around text for clarity
- Text remains readable at smallest display size (mobile ad at 200px width)

**Contrast Ratio (WCAG AA Standard)**
**Pass Criteria:**
- All text has 4.5:1 contrast ratio minimum (WCAG AA)
- Black text on light background or vice versa (high contrast)
- No light gray on white or other low-contrast combinations
- If text has shadow/outline, background contrast still meets 4.5:1

**Tool:** Use WebAIM Contrast Checker to verify ratios
- Test foreground color (text) vs. background color
- If colors not pure (e.g., semi-transparent), test against actual background

**Examples:**
- ✅ Pass: Black (#000000) on white (#FFFFFF) = 21:1 contrast
- ✅ Pass: White (#FFFFFF) on dark blue (#003366) = 12.6:1 contrast
- ✅ Pass: Dark gray (#333333) on light yellow (#FFFF99) = 7.5:1 contrast
- ❌ Fail: Light gray (#CCCCCC) on white (#FFFFFF) = 1.4:1 contrast
- ❌ Fail: Dark blue (#003366) on dark green (#006600) = 1.8:1 contrast

### Text Overlay on Images
**Pass Criteria:**
- Text overlay covers maximum 20% of image area (Google Display Ads policy)
- Text is centered or positioned clearly (not cramped edges)
- Text outline/shadow provides readability against image background
- No text wrapping in awkward places

**Fail Criteria:**
- Text obscures important product elements
- >20% of image covered in text
- Text illegible due to image underneath
- Text cramped into corner or twisted

**Scoring:**
- Text Readability Score: 1-10 (7+ is Pass)

---

## 3. Character Limits Compliance

### Search RSA
**Pass Criteria:**
- All headlines ≤30 characters (including spaces)
- All descriptions ≤90 characters (including spaces)
- Display path 1 ≤15 characters
- Display path 2 ≤15 characters (if provided)
- Minimum 8 unique headlines provided
- Minimum 4 descriptions provided
- No cut-off text or partial words

**Fail Criteria:**
- Any headline >30 chars (will be truncated by Google)
- Any description >90 chars (will be truncated)
- <8 headlines provided
- <4 descriptions provided

**Character Count Tool:** Use Google Ads Character Counter or online tool
```
Headline: "Shop Premium Organic Skincare Products" = 38 characters → FAIL (exceeds 30)
Fixed: "Premium Organic Skincare" = 24 characters → PASS
```

### Display RDA
**Pass Criteria:**
- Short headlines ≤25 characters (max 5)
- Long headline ≤90 characters
- Descriptions ≤90 characters (max 5)
- Business name ≤25 characters
- Logo present (no character limit)
- All required fields filled

**Fail Criteria:**
- Short headline >25 chars
- Long headline >90 chars
- Missing long headline
- Missing business name
- Missing logo

### Shopping
**Pass Criteria:**
- Title ≤150 characters
- Description ≤5000 characters (but aim for 100-250 optimal)
- All keywords front-loaded in title
- No special characters breaking fields

**Fail Criteria:**
- Title >150 chars
- Keyword obscured by excessive description

### Video
**Pass Criteria (6s bumper):**
- Duration exactly 5.5-6 seconds
- Script word count ~50-55 words
- No over-reading (words per second reasonable)

**Pass Criteria (15s non-skip):**
- Duration exactly 15 seconds
- Script word count ~75-85 words

**Pass Criteria (15-30s skippable):**
- Duration 15-30 seconds (optimal 20-25)
- Script word count ~150-180 for 30 seconds
- Hook complete in first 3 seconds

**Fail Criteria:**
- Duration outside specified range
- Script unreadable within time (too many words, rushed)
- Hook incomplete or weak

### Performance Max
**Pass Criteria:**
- 15 headlines provided, all ≤30 chars
- 5 long headlines provided, all ≤90 chars
- 5 descriptions provided, all ≤90 chars
- All image aspect ratios included (landscape, square, portrait, tall)
- Final URL complete with UTM parameters

**Fail Criteria:**
- Missing any headline count
- Character overages in any field
- Missing image sizes
- Missing final URL

**Scoring:**
- Character Limits Compliance Score: PASS/FAIL (binary — no partial credit)

---

## 4. Ad Strength Check (RSA & PMax)

### Responsive Search Ads
**Google Ad Strength Prediction:** Use Google Ads API or UI to check predicted ad strength

**Factors Considered:**
- Number of unique headlines (8+ = better)
- Number of descriptions (4 = good, 5+ = excellent)
- Headline variety (different angles, benefits, CTAs)
- Description variety (proof, benefits, value props)
- Relevance to keywords and landing page

**Strength Levels:**
- 🔴 **Poor/Low:** <7 headlines OR <4 descriptions OR low variety
  - Action: Add headlines/descriptions and vary messaging
- 🟡 **Average:** 7-8 headlines + 4 descriptions with some variety
  - Action: Add 1-2 more headlines, vary messaging
- 🟢 **Good:** 8-10 headlines + 4 descriptions with good variety
  - Action: Pin top performers, monitor performance
- 🟢 **Excellent:** 12+ headlines + 4 descriptions with strong variety and pinning
  - Action: Maintain and monitor performance

**Scoring:**
- Ad Strength Score: GOOD or EXCELLENT = PASS, otherwise REVIEW_NEEDED

### Performance Max
**Google Ad Strength Prediction:** Similar to RSA, considers asset completeness and diversity

**Factors Considered:**
- Number of headlines (15+ = better)
- Number of long headlines (5 = good)
- Number of descriptions (5 = good, varied messaging = excellent)
- Image variety (multiple aspect ratios, diverse imagery)
- Logo presence (increases strength)
- Video presence (increases strength, optional)
- Audience signals provided (increases strength)

**Strength Levels:**
- 🔴 **Poor/Low:** Missing major asset types or too few assets
- 🟡 **Average:** Minimum assets provided with low variety
- 🟢 **Good:** Full asset count with reasonable variety
- 🟢 **Excellent:** Full asset count + diverse imagery + audience signals + video

**Scoring:**
- Ad Strength Score: GOOD or EXCELLENT = PASS, otherwise REVIEW_NEEDED

---

## 5. Color Consistency

### Brand Palette Adherence
**Pass Criteria:**
- Primary brand color used consistently (e.g., all ads use brand blue)
- Secondary colors from brand palette only (no random colors)
- No conflicting colors that clash with brand identity
- Accent colors purposeful and on-brand
- Black/white text follows brand guidelines

**Brand Config Reference:**
From `brand_config`, verify:
- `primary_color` used in at least 50% of designs
- `secondary_colors` (array) used for variation
- `text_color` used for readability
- `forbidden_colors` (array) NEVER used

**Fail Criteria:**
- Color outside brand palette
- Neon or clashing colors inconsistent with brand
- Too many colors (>5 colors per design creates visual chaos)
- Forbidden colors present

### Consistency Within Series
**Pass Criteria:**
- If creating ad set with multiple variants, color palette consistent across variants
- Variations appear intentional (different angle) not inconsistent (random color change)
- Each variant recognizable as part of same campaign

**Fail Criteria:**
- One variant red, another green (looks like different brands)
- Color so different it seems like mistake, not variation

**Scoring:**
- Color Consistency Score: 1-10 (7+ is Pass)

---

## 6. Artifacts & AI Quality Issues

### Visual Artifacts
**Pass Criteria:**
- No pixelation or compression artifacts
- No warped/distorted shapes or impossible geometry
- No broken objects or body parts (e.g., hand with 7 fingers)
- No text rendering errors (garbled characters, broken letters)
- No color bleeding or halos around objects
- Blending between elements is smooth, not jagged

### AI Generation Errors (if using AI generation tools)
**Pass Criteria:**
- No visible signs of AI synthesis (overly smooth, unnatural texture)
- Text is readable and correctly spelled (no "teh" instead of "the")
- Proportions are correct (faces symmetrical, hands reasonable)
- Objects are correctly formed (chairs with 4 legs, not 3)
- No watermarks or tool signatures visible

### Specific Red Flags
**Fail Criteria:**
- Text distorted or illegible
- Product warped or impossible shape
- Background discontinuity (e.g., shadow doesn't match light)
- Objects clipped or cut off awkwardly
- Face looks uncanny or asymmetrical
- Hands/fingers disproportionate
- Background artifacts (random lines, floating objects)
- Product appears to float or defy physics

**Scoring:**
- Artifacts & AI Quality Score: 1-10 (8+ is Pass, 0 artifacts = 10)

---

## 7. Brand Integrity

### Logo Presence & Placement
**Pass Criteria:**
- Logo present in image or ad (except video thumbnails may be optional)
- Logo size appropriate (not tiny/invisible, not overwhelming)
- Logo placement follows brand guidelines (usually corner or bottom)
- Logo is crisp and clear, not blurry or pixelated
- Logo color is brand-correct (not inverted or altered)

**Fail Criteria:**
- Logo missing
- Logo barely visible or too small to recognize
- Logo distorted or incorrect color
- Logo overlapping critical product area

### Product Visibility & Recognition
**Pass Criteria:**
- Primary product clearly visible and recognizable
- Product is hero of the image (dominant visual)
- Product benefits visible (if applicable: color, size, features)
- Product not obscured by text, models, or other elements
- Multiple products shown if product line diversity is goal

**Fail Criteria:**
- Product hidden or ambiguous
- Product appears secondary to background/model
- Product cropped or partially visible
- Wrong product shown (e.g., competitor product)

### Compliance Text (if required)
**Pass Criteria:**
- Legal disclaimers present if required (e.g., "Results not guaranteed" for health claims)
- Trademark symbols correct (™ for trademarks, ® for registered)
- Fine print legible and compliant
- Expiry dates/dates current (if promotion shown)

**Fail Criteria:**
- Missing required disclaimers
- Illegal claims without disclaimers (e.g., "Cures acne" without FDA disclaimer)
- Expired offer dates shown
- Incorrect trademark symbols

### Locked Brand Elements (from brand_config)
**Pass Criteria:**
- All locked elements present:
  - Locked elements are defined in `brand_config.locked_elements` (array)
  - Example: ["logo", "primary_color", "compliance_text"]
  - Verify each locked element is present and correct
- Swappable elements (from `brand_config.swappable_elements`) are varied appropriately
  - Example swappable: ["headline", "background", "hero_image", "offer"]

**Fail Criteria:**
- Any locked element missing or incorrect
- Locked element altered from brand standards
- Swappable element repeats too much (no variation)

### Brand Guideline Violations
**Pass Criteria:**
- No violated guidelines from brand_config
- Typography: Fonts match brand specification
- Spacing: Adequate white space, not cramped
- Tone: Copy matches brand voice (professional/playful/technical)
- Values: Brand values reflected (sustainable/luxury/accessible/etc.)

**Fail Criteria:**
- Wrong fonts (serif when brand uses sans-serif)
- Cramped or cluttered design
- Copy tone mismatched (professional brand with casual slang)
- Visual style conflicts with brand (minimalist brand with ornate design)

**Scoring:**
- Brand Integrity Score: 1-10 (7+ is Pass)

---

## QC Scorecard — Final Tally

```
QC Scorecard: [AD ID / ASSET NAME]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Professional Quality:        [9/10] ✅ PASS
2. Text Readability:            [8/10] ✅ PASS
3. Character Limits Compliance: [✅] PASS
4. Ad Strength Check:           [EXCELLENT] ✅ PASS
5. Color Consistency:           [9/10] ✅ PASS
6. Artifacts & AI Quality:      [10/10] ✅ PASS
7. Brand Integrity:             [8/10] ✅ PASS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall QC Status:              [PASSED] ✅

Issues Found: 0
Ready for Delivery: YES
```

### QC Status Options
- **PASSED:** All 7 checks passed, asset ready for production
- **REVIEW_NEEDED:** 1-2 minor issues, requires small fix (resize text, adjust color, add headline)
- **FAILED:** 3+ issues, asset needs remake (major issues with professional quality, brand integrity, or artifacts)

### QC Actions by Status
| Status | Action |
|--------|--------|
| PASSED | Write to creative_registry, mark ready for delivery |
| REVIEW_NEEDED | Flag for creator to fix, request rework, re-QC when resubmitted |
| FAILED | Request full remake, do not deliver |

---

## QC Tools & References

### Online Character Counters
- Google Ads Character Counter (in Google Ads UI)
- Online tool: [Counter.net](https://counter.net/)

### Contrast Ratio Checkers
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Contrast Ratio.com](https://contrast-ratio.com/)

### Image Quality Assessment
- Zoom to 100% and inspect for pixelation
- Use browser DevTools to check pixel dimensions
- Load on mobile device to test readability at small sizes

### Video Duration & Transcription
- Use video editing software (Adobe Premiere, Final Cut Pro) to verify exact duration
- Manual word count or transcription tool to verify word count
- Test playback at 1x speed to ensure narration pace is reasonable

---

## Common QC Failures & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| Headline over 30 chars | Overly detailed messaging | Remove non-essential adjectives; use shorter words |
| Low contrast text | Dark text on dark background | Use white text on dark; black text on light |
| Pixelated image | Low resolution source | Request high-res image (1200px+) or recreate |
| AI generation artifacts | Weak model output | Regenerate with better prompt or use different tool |
| Logo missing | Oversight in design | Add logo to corner/bottom, ensure brand-correct |
| Ad Strength "Average" | Too few headlines/descriptions | Add 2-3 more headlines and vary messaging |
| Color outside palette | Designer used wrong color | Replace with correct brand color from palette |
| Product obscured | Poor composition | Recompose image with product as hero |

---

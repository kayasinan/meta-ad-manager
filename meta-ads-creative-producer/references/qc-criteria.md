# QC Pipeline Criteria

## 6-Point Quality Control System

Every generated image is automatically scored on 6 criteria using Gemini 2.0 Flash vision model. No human review needed for basic quality.

### Standard Criteria (Both Mode A and Mode B)

| # | Criteria | What It Checks | Score Range | Fail Example | Pass Threshold |
|---|----------|---|---|---|---|
| 1 | **Professional Quality** | Does it look like a real, polished ad? Composition, lighting, clarity, polish level. | 1-10 | Blurry, amateur, low-res feel, unfinished | 7+ |
| 2 | **Text Readability** | Can you read all badge/overlay text clearly? No overlapping, cut-off, garbled, or too-small text. | 1-10 | Text overlapping, cut off corners, illegible size, poor contrast | 7+ |
| 3 | **Text Density** | Is text covering more than 20% of the image area? | PASS/FAIL | Multiple badges, large text blocks, text-heavy layout | MUST PASS (≤20%) |
| 4 | **Color Consistency** | Does the palette make sense as a unified design? Colors harmonize, no jarring contrasts. | 1-10 | Random clashing colors, disjointed look, unrelated palette | 7+ |
| 5 | **Artifacts/Distortions** | Any AI-generation weirdness? Extra fingers, melted text, warped edges, uncanny faces. | 1-10 | Morphed hands, distorted products, glitchy elements | 7+ |
| 6 | **Brand Integrity** | Product imagery and logo untouched? Compliance text preserved? | 1-10 | Logo morphed, product box distorted, compliance text altered | 7+ |

---

## Additional Criteria for Mode B (Competitor-Inspired)

| # | Criteria | What It Checks | Score Range | Notes |
|---|----------|---|---|---|
| 7 | **Brand Identity** | Does it clearly read as YOUR brand (not generic)? Logo visibility, color scheme reflects your brand. | 1-10 (min 8.0) | Generic feel, no brand presence, could be anyone's ad |
| 8 | **Zero Competitor Trace** | Any remnant of competitor branding? Their logo, product, exact color scheme. | PASS/FAIL | Competitor logo visible, their product shown, their colors too exact |

---

## Scoring & Passing Rules

### For Mode A (Replicate Own Winners)
**PASS** if:
- Text density ≤ 20% (PASS/FAIL, auto-fail if exceeds)
- Average score across criteria 1-6 ≥ 7.0
- All 5 numeric criteria (1, 2, 4, 5, 6) individually ≥ 6.0

**FAIL** if:
- Text density > 20% (automatic fail, no scoring of other criteria)
- Average score < 7.0
- Any single criterion < 6.0

**Action on FAIL:**
- Image is deleted immediately (no wasted storage)
- Failure logged with specific failing criteria
- Prompt is adjusted based on the specific failures
- Retry automatically (max 3 retries per variant)
- If max retries exceeded, log as failed variant and move to next

### For Mode B (Competitor-Inspired)
**PASS** if:
- Text density ≤ 20% (PASS/FAIL, auto-fail if exceeds)
- Average score across criteria 1-6 ≥ 7.0
- All 5 numeric criteria individually ≥ 6.0
- Brand identity (criteria 7) ≥ 8.0
- Zero competitor trace (criteria 8) = PASS

**FAIL** if:
- Text density > 20%
- Average score < 7.0
- Brand identity < 8.0
- Zero competitor trace = FAIL
- Any single criterion < 6.0

**Action on FAIL:**
- Image is deleted immediately
- Failure logged with specific criteria
- Prompt adjusted to strengthen brand identity or reduce competitor visibility
- Retry automatically (max 3 retries per variant)

---

## Typical Results

- **Pass rate: ~95%** — The 5% catch rate prevents bad images from reaching Meta
- Most failures are caught on text density (>20% coverage) or artifacts
- Brand integrity and competitor trace are rare failures when prompts are well-constructed
- Average pass on first attempt: high quality images get generated consistently

---

## QC Score Recording

Every scored image is logged with:
```json
{
  "image_id": "var-001",
  "qc_passed": true,
  "qc_scores": {
    "professional_quality": 9,
    "text_readability": 9,
    "text_density": "PASS",
    "color_consistency": 10,
    "artifacts": 9,
    "brand_integrity": 10,
    "brand_identity": 9,
    "competitor_trace": "PASS",
    "average": 9.4
  },
  "qc_notes": "Excellent quality, text minimal, colors harmonious",
  "qc_timestamp": "2026-02-14T14:30:00Z"
}
```

This metadata is stored in the Creative Registry and used for:
- Historical QC performance tracking
- Identifying which prompt styles generate highest quality
- Feeding back into the Creative Analyst's feedback loop

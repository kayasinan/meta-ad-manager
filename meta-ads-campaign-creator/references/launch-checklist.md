# Campaign Launch Checklist

## 19-Point Pre-Launch Verification

Before sending a campaign, ad set, or ad to the Orchestrator for final human approval, verify every item on this checklist.

---

## Campaign Configuration

### 1. Campaign Objective Matches the Brief
- [ ] Objective selected: Conversions / Traffic / Awareness / Lead Generation
- [ ] Objective aligns with the brief's stated goal
- [ ] Conversion event correctly configured (if Conversions objective)

### 2. Audiences Are Correctly Configured
- [ ] All audience inclusions added and verified in Meta
- [ ] All audience exclusions added (from Data & Placement Analyst)
- [ ] Audience sizes align with expected ranges
- [ ] No unintended audience overlap with other active campaigns

### 3. Placement Exclusions Are Applied
- [ ] Placement exclusions configured per Data & Placement Analyst directives
- [ ] Included placements verified (Facebook Feed, Instagram Feed, Stories, Reels, etc.)
- [ ] Excluded placements confirmed (if any unwanted placements specified)
- [ ] Audience Network configured per brief

### 4. Dayparting Schedule Is Set
- [ ] Golden hours enabled (from Data & Placement Analyst)
- [ ] Dead zones disabled (from Data & Placement Analyst)
- [ ] Schedule matches the brief timeline
- [ ] Timezone correctly set for target market

### 5. Frequency Cap Is Configured
- [ ] Frequency cap set per Data & Placement Analyst's fatigue analysis
- [ ] Cap applies to correct period (e.g., 3 per day, 5 per week)
- [ ] Cap prevents audience exhaustion without being too restrictive

---

## Budget & Bid Strategy

### 6. Budget Allocation Matches the Brief
- [ ] Total daily budget documented (DRAFT — human approval required)
- [ ] Budget split across campaigns (if multiple active)
- [ ] Budget split across ad sets documented (cold/warm/hot distribution)
- [ ] Learning phase boost specified (if applicable)
- [ ] No budget is ACTIVE until human approves via Orchestrator

### 7. Bid Strategy Is Appropriate for the Objective
- [ ] Bid strategy selected: Lowest Cost / Cost Cap / Bid Cap / Minimum ROAS
- [ ] Bid strategy rationale documented
- [ ] Cost cap or bid cap amounts proposed (human must approve exact amounts)
- [ ] Minimum ROAS floor proposed (if applicable)

---

## Creatives & Copy

### 8. All Creatives Are Uploaded and Properly Formatted
- [ ] Image files uploaded to Meta Ads Manager
- [ ] Video files uploaded (if applicable)
- [ ] Carousel cards uploaded in correct sequence (best-performing card first)
- [ ] All creative files verified as available in Meta system

### 9. Creative Format Validation
- [ ] Images meet Meta specs: correct aspect ratios per placement
  - [ ] Feed: 1:1 (1080×1080) or 4:5 (1080×1350)
  - [ ] Stories/Reels: 9:16 (1080×1920)
  - [ ] Link Ads: 1.91:1 (1200×628)
- [ ] All images ≥1080px on shortest edge
- [ ] File format: JPG or PNG only
- [ ] File size ≤30 MB per image
- [ ] Aspect ratio within 3% tolerance

### 10. Text Density Validated
- [ ] All images passed Creative Producer's QC pipeline
- [ ] Text coverage ≤20% on every image (CRITICAL)
- [ ] If any image has >20% text, REJECTED and returned to Creative Producer
- [ ] Text density check documented for every image

### 11. Copy Is Attached to the Correct Creatives
- [ ] Primary text attached to correct image variant
- [ ] Headline attached and verified
- [ ] Description attached and verified
- [ ] No copy mismatches (wrong copy paired with wrong creative)

### 12. Copy Length Within Limits
- [ ] Primary text ≤125 characters
- [ ] Headline ≤40 characters
- [ ] Description ≤30 characters
- [ ] Character counts verified in Meta's preview

### 13. CTAs Match the Winning CTA
- [ ] CTA button type matches Creative Analyst's recommended CTA
- [ ] CTA text (if custom) aligns with winning copy formula
- [ ] CTA placement verified in preview
- [ ] CTA is appropriate for the objective

### 14. Landing Page URLs Are from Approved List
- [ ] Landing page URL sourced from Post-Click Analyst's approved list
- [ ] Landing page marked as status = 'APPROVED' in system
- [ ] URL is working (not 404 or redirect)
- [ ] URL is appropriate for the audience segment
- [ ] Ad set/audience segment maps to correct landing page variant

---

## Tracking & Analytics

### 15. UTM Parameters Are Correctly Configured on EVERY Ad
- [ ] utm_source = facebook (exact)
- [ ] utm_medium = paid_social (exact)
- [ ] utm_campaign = {brand_id}_{campaign_id}_{campaign_name}
- [ ] utm_content = {ad_id}_{image_identifier}_{copy_identifier}
- [ ] utm_term = {adset_id}_{audience_segment}
- [ ] UTMs verified in Meta preview URL (no typos, no missing parameters)
- [ ] UTM values are URL-encoded (no spaces)

---

## Advanced Features

### 16. Dynamic Creative Is Properly Set Up (If Applicable)
- [ ] Advantage+ Creative enabled (if using)
- [ ] Multiple image variants uploaded for testing
- [ ] Multiple headline variants provided
- [ ] Multiple description variants provided
- [ ] Meta's auto-optimization understood and accepted

---

## Naming & Organization

### 17. Campaign Naming Convention Is Followed
- [ ] Campaign name: `[Objective]_[Brand]_[Market]_[AudienceTemp]_[Date]`
- [ ] Ad set name: `[AudienceType]_[Segment]_[Geo]_[Date]`
- [ ] Ad name: `[Mode]_[Visual]_[CopyAngle]_[Variant]_[Date]`
- [ ] No spaces in any names (underscores only)
- [ ] All names are descriptive and filterable

---

## Final Verification

### 18. No Accidental Audience Overlap with Other Active Campaigns
- [ ] Overlap check completed with existing active campaigns
- [ ] Overlap >20% flagged to Orchestrator
- [ ] If overlap exists, documented with reasoning
- [ ] No unintended audience duplication

### 19. Campaign Status Is DRAFT (Not ACTIVE)
- [ ] Campaign created in DRAFT status
- [ ] Ad sets created in DRAFT status
- [ ] All ads created in DRAFT status
- [ ] NO ads are ACTIVE until Orchestrator approves and human authorizes
- [ ] Scheduled launch time set (if human specified timing)

---

## Deliverables to Orchestrator

When all 19 items are verified:

1. **Executed Changes** — Full campaign/ad set/ad structure created in DRAFT status
2. **Campaign Spec Sheet** — Document detailing every setting (objective, audiences, placements, budget, bids, UTMs, creatives)
3. **Launch Checklist** — Completed checklist confirming all 19 items verified
4. **Budget Plan** — Proposed budget allocation with reasoning (cold/warm/hot split, learning phase adjustment)
5. **Bid Strategy Rationale** — Why the chosen strategy fits, expected CPA/ROAS range, cap settings

## Sign-Off

**Verified by:** [Agent Name & Date]

**Campaign:** [Campaign Name]
**Mode:** [Mode 1 / Mode 2 / Mode 3]
**Status:** ✓ All 19 items verified — Ready for Orchestrator review and human approval

---

## Note for ASC (Advantage+ Shopping Campaigns)

If building an ASC campaign, items **2-5** do not apply (audiences, placement exclusions, dayparting, frequency cap are managed by Meta). All other 15 items still apply.

# Campaign Creator (Agent 6)

**Location:** Machine B (executes via Machine A for API calls)

Creates campaigns, ad sets, and ads in Meta Ads Manager. Everything is created PAUSED — nothing goes live without human approval.

## Responsibilities
- Upload generated images to Meta
- Create ad creatives with product-matched URLs and UTMs
- Create campaign structure (campaign → ad set → ads)
- Verify brand identity (correct Facebook Page and Instagram account)
- Confirm target country before creation
- All ads created PAUSED/DRAFT

## Safety Rules
- ⚠️ EVERYTHING created PAUSED — no exceptions
- ⚠️ Brand identity verified before any creation
- ⚠️ Product-creative matching enforced (atomic units)
- ⚠️ UTMs configured per ad for GA4 tracking

## Key Files
- `SKILL.md` — Agent instructions
- `scripts/` — Meta API campaign creation scripts

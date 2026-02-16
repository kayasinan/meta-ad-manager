---
name: meta-ad-optimizer
description: Execute Meta (Facebook/Instagram) ad account changes — pause/enable ads, adjust budgets, add exclusions, consolidate campaigns, upload creatives. Use ONLY after meta-ad-analyst has produced recommendations AND the user has explicitly confirmed. Never execute without user approval.
---

# Meta Ad Optimizer

Execute approved changes to Meta Ads accounts. This skill only runs **after** meta-ad-analyst has produced recommendations and the user has explicitly confirmed each action.

## ⚠️ CRITICAL RULES

1. **NEVER execute without explicit user confirmation.** Every single change needs a "yes" from the account owner.
2. **NEVER auto-execute based on analyst output alone.** Always present the recommendation first, wait for approval.
3. **Log every change** with before/after state for rollback capability.
4. If Ben or any team member requests changes, **still require Sinan's confirmation**.

## Available Actions

### Campaign Level
| Action | API Endpoint | Risk |
|--------|-------------|------|
| Pause campaign | `POST /{campaign_id}?status=PAUSED` | Medium |
| Enable campaign | `POST /{campaign_id}?status=ACTIVE` | Medium |
| Update budget | `POST /{campaign_id}?daily_budget=X` | High |
| Update bid strategy | `POST /{campaign_id}?bid_strategy=X` | High |

### Ad Set Level
| Action | API Endpoint | Risk |
|--------|-------------|------|
| Pause ad set | `POST /{adset_id}?status=PAUSED` | Medium |
| Enable ad set | `POST /{adset_id}?status=ACTIVE` | Medium |
| Adjust budget | `POST /{adset_id}?daily_budget=X` | High |
| Add age exclusion | `POST /{adset_id}?targeting=...` | Medium |
| Add placement exclusion | `POST /{adset_id}?targeting=...` | Medium |
| Add audience exclusion | `POST /{adset_id}?excluded_custom_audiences=...` | Medium |
| Update schedule/dayparting | `POST /{adset_id}?pacing_type=...` | Medium |

### Ad Level
| Action | API Endpoint | Risk |
|--------|-------------|------|
| Pause ad | `POST /{ad_id}?status=PAUSED` | Low |
| Enable ad | `POST /{ad_id}?status=ACTIVE` | Low |
| Upload creative | `POST /{account_id}/adcreatives` | Low |
| Create ad with creative | `POST /{account_id}/ads` | Medium |

### Campaign Creation
| Action | Risk |
|--------|------|
| Create PAUSED campaign | Medium |
| Create ad sets in PAUSED campaign | Medium |
| Create ads in PAUSED ad sets | Medium |

**Always create in PAUSED status.** User activates manually or gives explicit go-ahead.

## Execution Workflow

```
1. meta-ad-analyst produces recommendations
2. Present recommendations to user with clear before/after
3. User confirms specific actions
4. Execute each action, log result
5. Verify change applied correctly
6. Report summary of all changes made
```

## Change Log

Every execution saves to `data/{account_name}/change_log.json`:
```json
{
  "timestamp": "2026-02-13T12:00:00Z",
  "action": "pause_adset",
  "target_id": "12345678",
  "target_name": "Scale ASC Dog All",
  "before": {"status": "ACTIVE", "daily_budget": 40000},
  "after": {"status": "PAUSED"},
  "reason": "Zero audience exclusions, cannibalizing 5 other ad sets",
  "confirmed_by": "Sinan",
  "rollback_command": "POST /12345678?status=ACTIVE"
}
```

## Scripts

Uses the same `scripts/meta_api.py` from meta-ad-analyst for API calls. Additional functions needed:
- `update_campaign(token, campaign_id, params)` — update campaign fields
- `update_adset(token, adset_id, params)` — update ad set fields
- `update_ad(token, ad_id, params)` — update ad fields
- `create_campaign(token, account_id, params)` — create new campaign
- `upload_creative(token, account_id, image_path, params)` — upload creative image

## Setup Requirements

- Meta Ads API credentials with `ads_management` permission
- Store at `/root/clawd/.meta_ads_credentials`


## ⚠️ DOUBLE-CONFIRMATION RULE (MANDATORY)
Before executing ANY campaign change (pause, enable, create, modify budgets, targeting, creatives, bids, exclusions, or any other modification), you MUST:
1. Present the proposed changes clearly to the user
2. Ask for explicit confirmation ONE MORE TIME before executing
3. Only proceed after receiving that second confirmation
This applies to ALL changes — no exceptions. This prevents accidental modifications.

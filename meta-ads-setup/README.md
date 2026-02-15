# Meta Ads Setup (Agent S)

**Location:** Machine A (primary VPS)

Infrastructure and onboarding agent. Handles Supabase schema deployment, SSH connectivity between machines, brand configuration, and credential management.

## Responsibilities
- Deploy Supabase schema (20 tables, 7 views, RLS policies)
- Configure SSH between Machine A and Machine B
- Onboard new brands (Facebook Page, Instagram, GA4, ad account)
- Manage credentials and token lifecycle
- Deploy agent skills to Machine B

## Key Files
- `SKILL.md` — Setup procedures and schema definitions

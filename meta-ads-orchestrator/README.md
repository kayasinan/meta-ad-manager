# Meta Ads Orchestrator (Agent O)

**Location:** Machine A (primary VPS)

Central brain of the 9-agent system. Creates optimization cycles, dispatches agents via SSH to Machine B, reviews intelligence outputs, and makes scaling/pausing/creative decisions.

## Responsibilities
- Create and manage 6-day optimization cycles in Supabase
- Dispatch agents 1-7 in correct order via SSH
- Review agent deliverables and synthesize recommendations
- Enforce pipeline rules (atomic units, triple-source, brand identity)
- Present human-approval gates at Phase 3

## Key Files
- `SKILL.md` — Full agent instructions and pipeline rules

## Pipeline Rules Enforced
- Atomic Creative Units (image+URL+product+copy as one object)
- Brand Identity Check on first engagement
- Confirm target country before campaign creation
- Triple-source metrics at ALL levels
- Full 9-section optimization reports
- Cannibalization analysis in every report

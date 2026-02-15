# Meta Ad Manager — 9-Agent AI System

An AI-powered Meta (Facebook/Instagram) advertising optimization system built on OpenClaw. Uses 9 specialized agents across 2 machines with a Supabase backend for multi-brand campaign management.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  MACHINE A — Orchestrator                           │
│  ┌───────────────────┐  ┌────────────────────────┐  │
│  │   Orchestrator    │  │       Setup             │  │
│  │  (Brain/Dispatch) │  │  (Infra/Onboarding)    │  │
│  └───────┬───────────┘  └────────────────────────┘  │
│          │ SSH                                       │
├──────────┼──────────────────────────────────────────┤
│  MACHINE B — Execution Engine                       │
│          ▼                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Agent 1     │  │ Agent 2     │  │ Agent 3    │  │
│  │ Data &      │→ │ Creative    │→ │ Post-Click │  │
│  │ Placement   │  │ Analyst     │  │ Analyst    │  │
│  └─────────────┘  └─────────────┘  └────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ Agent 4     │  │ Agent 5     │  │ Agent 6    │  │
│  │ Competitive │→ │ Creative    │→ │ Campaign   │  │
│  │ Intel       │  │ Producer    │  │ Creator    │  │
│  └─────────────┘  └─────────────┘  └────────────┘  │
│  ┌─────────────┐                                    │
│  │ Agent 7     │                                    │
│  │ Campaign    │                                    │
│  │ Monitor     │                                    │
│  └─────────────┘                                    │
├─────────────────────────────────────────────────────┤
│  SUPABASE — Shared Database                         │
│  20 tables · 7 views · RLS · Multi-brand            │
└─────────────────────────────────────────────────────┘
```

## Agents

| # | Agent | Location | Role |
|---|-------|----------|------|
| O | [Orchestrator](meta-ads-orchestrator/) | Machine A | Creates optimization cycles, dispatches agents, reviews intelligence, makes decisions |
| S | [Setup](meta-ads-setup/) | Machine A | Infrastructure setup, Supabase schema, brand onboarding, SSH connectivity |
| 1 | [Data & Placement Analyst](meta-ads-data-placement-analyst/) | Machine B | Pulls Meta API + GA4 data, computes triple-source metrics, identifies winners/losers |
| 2 | [Creative Analyst](meta-ads-creative-analyst/) | Machine B | Fatigue scoring, winner classification, replication blueprints, atomic creative units |
| 3 | [Post-Click Analyst](meta-ads-postclick-analyst/) | Machine B | Landing page scoring from GA4 engagement data, URL approval |
| 4 | [Competitive Intel](meta-ads-competitive-intel/) | Machine B | Ad Library competitor analysis, gap detection |
| 5 | [Creative Producer](meta-ads-creative-producer/) | Machine B | AI image generation using Gemini, QC scoring, variant production |
| 6 | [Campaign Creator](meta-ads-campaign-creator/) | Machine B | Creates campaigns, ad sets, ads via Meta API — always PAUSED |
| 7 | [Campaign Monitor](meta-ads-campaign-monitor/) | Machine B | Live campaign optimization checks with 9-section reports |

## 6-Day Optimization Cycle

```
Day 1: Phase 1 — Intelligence Gathering (Agents 1-4)
Day 2: Phase 2 — Creative Production (Agent 5)
Day 3: Phase 3 — Human Review & Approval ← YOU ARE HERE
Day 4: Phase 4 — Campaign Creation (Agent 6, all PAUSED)
Day 5: Phase 5 — Launch (human activates)
Day 6: Phase 5 — Monitor (Agent 7)
```

## Key Principles

- **Triple-Source Measurement**: Meta | GA4 | Assumed Real (GA4 × 1.2) at ALL levels
- **Human Approval Required**: No campaign goes live without explicit confirmation
- **Atomic Creative Units**: Image + URL + Product + Copy stay bundled through entire pipeline
- **GA4 is Source of Truth**: Never trust Meta's self-reported conversions alone
- **All Campaigns Created PAUSED**: Nothing auto-launches

## Data Flow

```
Meta Ads API ──→ Agent 1 ──→ Supabase ──→ Agent 2 ──→ Supabase
GA4 Data API ──→ Agent 1      │            Agent 3 ──→ Supabase
                               │            Agent 4 ──→ Supabase
                               │                          │
                               │         ┌────────────────┘
                               │         ▼
                               │    Agent 5 (Gemini) ──→ Images
                               │                          │
                               │                          ▼
                               └──→ Agent 6 ──→ Meta Ads Manager (PAUSED)
```

## Tech Stack

- **Runtime**: OpenClaw on Ubuntu 24.04
- **Language**: Python 3.12
- **APIs**: Meta Marketing API v21.0, GA4 Data API, Gemini 3 Pro (image gen)
- **Database**: Supabase (PostgreSQL + RLS)
- **Package Management**: `uv` (Machine B), `pip3` (Machine A)

## Setup

See [meta-ads-setup/SKILL.md](meta-ads-setup/SKILL.md) for full deployment instructions.

## License

Private — All rights reserved.

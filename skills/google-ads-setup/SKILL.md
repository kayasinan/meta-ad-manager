---
name: google-ads-setup
description: First-boot setup skill for the Google Ads AI Agent System. Walks through 8 phases: self-check, Supabase schema deployment, credential collection, Machine B SSH connection, agent deployment, multi-brand onboarding, agent testing, and system readiness verification. Run this ONCE to initialize the entire system. Re-run specific phases for new brands or troubleshooting.
---

# Google Ads AI System — Setup Skill

```yaml
name: google-ads-setup
description: >
  First-boot setup skill for the Google Ads AI agent system.
  Runs once to configure the Orchestrator, connect to Machine B,
  deploy all 7 sub-agents, onboard the first brand, and test
  every agent end-to-end. The Orchestrator invokes this skill
  before any optimization cycle can begin.
trigger: First run, new brand onboarding, or system migration
runs_on: Machine A (Orchestrator's machine)
```

---

## How This Skill Works

You (the Orchestrator) run this skill exactly once per fresh deployment. It walks the human through every configuration step, validates everything, and tests each agent before declaring the system operational.

**You ask. The human answers. You configure. You test. Nothing is assumed.**

If the human doesn't have something ready (e.g., Google Ads API credentials not available yet), mark that phase as INCOMPLETE and move on. Return to incomplete phases later — the system tracks what's done and what's pending.

### Progress Tracking — EVERY Phase

At the START of every phase, write to `setup_log`:
```sql
INSERT INTO setup_log (phase, phase_name, status, started_at)
VALUES ($phase_number, $phase_name, 'IN_PROGRESS', NOW())
ON CONFLICT (phase) DO UPDATE SET status = 'IN_PROGRESS', started_at = NOW(), updated_at = NOW();
```

At the END of every phase (success):
```sql
UPDATE setup_log SET status = 'COMPLETE', completed_at = NOW(),
  details = $phase_results_json, updated_at = NOW()
WHERE phase = $phase_number;
```

If a phase fails:
```sql
UPDATE setup_log SET status = 'FAILED', error_message = $error_text, updated_at = NOW()
WHERE phase = $phase_number;
```

At Phase 7 completion, verify all phases:
```sql
SELECT system_status FROM v_setup_status;
-- Must return 'READY' (8 phases complete)
```

### Credential Carry-Forward Rule
Credentials collected in Phase 1 (Supabase) and Phase 2 (API keys) are stored in memory and carried forward into Phase 5 (Brand Onboarding) when inserting brand_config. You never ask for the same credential twice — collect once, use everywhere.

---

## Setup Phases Overview

| Phase | Name | What Happens | Can Skip? |
|-------|------|-------------|-----------|
| 0 | Self-Check | Verify Orchestrator environment is ready | No |
| 1 | Supabase | Connect to Supabase, apply schema, verify tables | No |
| 2 | Credentials | Collect and store all API keys/tokens | No |
| 3 | Machine B Connection | SSH into Machine B, verify connectivity | No |
| 4 | Agent Deployment | Install and configure all 7 agents on Machine B | No |
| 5 | Brand Onboarding | Collect Brand Config, targets, competitors, landing pages | No |
| 6 | Agent Testing | Test each agent one by one in priority order | No |
| 7 | System Readiness | Final verification, create Cycle #0, hand off to Orchestrator | No |

---

## Phase 0: Self-Check (Orchestrator Environment)

**Purpose:** Verify Machine A is ready to be the Orchestrator.

### Ask the Human — Nothing

This phase is automated. Run the following checks silently:

### Checks

```
CHECK 0.1 — Python version
  Run: python3 --version
  Pass: 3.10 or higher
  Fail: Tell human to install Python 3.10+

CHECK 0.2 — OpenClaw installed
  Run: openclaw --version
  Pass: Returns version number
  Fail: Tell human to install OpenClaw. Provide install link.

CHECK 0.3 — SSH client available
  Run: ssh -V
  Pass: OpenSSH client available
  Fail: Tell human to install OpenSSH

CHECK 0.4 — Internet connectivity
  Run: curl -s -o /dev/null -w "%{http_code}" https://api.supabase.com
  Pass: Returns 200 or 301
  Fail: Network issue — tell human to check internet connection

CHECK 0.5 — Disk space
  Run: df -h . | awk 'NR==2 {print $4}'
  Pass: >1GB available
  Fail: Warn human about low disk space
```

### Output

```
Phase 0: Self-Check
✅ Python 3.x.x
✅ OpenClaw vX.X.X
✅ SSH client available
✅ Internet connectivity OK
✅ Disk space: X.XGB available
→ Phase 0 COMPLETE
```

If any check fails, stop and tell the human exactly what to fix.

---

## Phase 1: Supabase Setup

**Purpose:** Connect to the Supabase project and apply the database schema.

### Ask the Human

```
QUESTION 1.1: "What is your Supabase project URL?"
  Example: https://xyzproject.supabase.co
  Store as: SUPABASE_URL

QUESTION 1.2: "What is your Supabase service role key?"
  Note: This is the service_role key from Supabase → Settings → API → service_role (secret)
  Store as: SUPABASE_SERVICE_KEY
  ⚠️ NEVER log this key. Store in environment variable only.

QUESTION 1.3: "Have you already applied the database schema (google-ads-supabase-schema.sql), or should I guide you through it?"
  Options:
    A) Already applied — just verify
    B) Not yet — guide me through it
```

### Actions

**If 1.3 = B (guide through schema):**
1. Tell the human: "Go to your Supabase Dashboard → SQL Editor → New Query"
2. Tell the human: "Paste the contents of BOTH `meta-ads-supabase-schema.sql` AND `google-ads-supabase-schema.sql` and click RUN"
3. Wait for human to confirm they've done it

**Verify schema (always, whether A or B):**
```sql
-- Run via Supabase API:
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Expected tables (22 — all Meta tables plus 4 Google Ads specific):**
```
ab_tests, ad_sets, ads, agent_deliverables, alerts,
audiences, brand_config, campaign_changes, campaigns,
cannibalization_scores, competitor_ads, competitors,
creative_registry, daily_metrics, landing_pages,
optimization_cycles, recommendations, tracking_health,
[Google Ads specific:]
g_campaigns, g_ad_groups, g_ads, g_keywords, g_daily_metrics
```

**Expected views (8 — 6 Meta + 2 Google Ads specific):**
```sql
SELECT viewname FROM pg_views WHERE schemaname = 'public';
-- Expected: v_latest_ad_metrics, v_campaign_health, v_creative_performance,
--           v_audience_performance, v_open_alerts, v_cycle_status,
--           [Google Ads specific:]
--           v_google_campaign_health, v_google_quality_scores
```

**Verify RLS is enabled:**
```sql
SELECT tablename, rowsecurity FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
-- All tables should appear
```

### Output

```
Phase 1: Supabase Setup
✅ Connected to Supabase: https://xyzproject.supabase.co
✅ 22/22 tables found (18 Meta + 4 Google Ads)
✅ 8/8 views found
✅ RLS enabled on all tables
→ Phase 1 COMPLETE
```

### Failure Handling
- Missing tables → tell human which ones are missing, ask them to re-run the schema SQL
- RLS not enabled → provide the specific ALTER TABLE commands
- Connection error → verify URL and service role key are correct

---

## Phase 2: Credentials Collection

**Purpose:** Collect system-wide API keys and prepare for per-brand credentials in Phase 5.

**Important:** This phase collects SYSTEM-WIDE credentials only:
- Supabase URL + service role key (required for all brands)
- Gemini API key (required for Creative Producer across all brands)

Google Ads API credentials, GA4 credentials, and Gemini credentials are PER-BRAND and will be collected during Phase 5 (Brand Onboarding) for each brand you set up.

### Ask the Human — One at a Time

Present each credential request individually. Do not dump all questions at once.

```
QUESTION 2.1: "What is your Supabase project URL?"
  Example: https://xyzproject.supabase.co
  Store as: SUPABASE_URL
  Scope: System-wide (all brands use this same Supabase project)

QUESTION 2.2: "What is your Supabase service role key?"
  Note: This is the service_role key from Supabase → Settings → API → service_role (secret)
  Store as: SUPABASE_SERVICE_KEY
  Scope: System-wide (all brands use this same key)
  ⚠️ NEVER log this key. Store in environment variable only.

QUESTION 2.3: "What is your Gemini API key?"
  Where to find: Google AI Studio → API Keys
  Store as: GEMINI_API_KEY environment variable on Machine B
  Scope: System-wide (Creative Producer uses this for all brands)
  Validate: Test with a simple API call
```

### Validation Tests

After collecting each credential, test it immediately:

```
TEST 2.1 — Supabase Connection
  Call: SELECT version() via Supabase API
  Pass: Returns version string
  Fail: URL invalid or service role key doesn't have read permissions

TEST 2.2 — Supabase Write Test
  Call: INSERT INTO brand_config (brand_name) VALUES ('__SETUP_TEST__');
       DELETE FROM brand_config WHERE brand_name = '__SETUP_TEST__';
  Pass: Insert and delete succeed
  Fail: Service role key doesn't have write permissions

TEST 2.3 — Gemini API
  Call: Generate a simple test image (1024x1024 white square with "TEST")
  Pass: Returns image data
  Fail: API key invalid or quota exceeded
```

### Output

```
Phase 2: Credentials (System-Wide)
✅ Supabase: Connected to https://xyzproject.supabase.co (read/write access confirmed)
✅ Gemini: API key valid, test generation successful
→ Phase 2 COMPLETE
→ Google Ads and GA4 credentials will be collected per-brand in Phase 5
```

---

## Phase 3: Machine B Connection

**Purpose:** Establish SSH connection from Machine A (Orchestrator) to Machine B (7 sub-agents).

### Ask the Human

```
QUESTION 3.1: "What is Machine B's IP address or hostname?"
  Format: IP address (e.g., 192.168.1.100) or hostname (e.g., agent-server.example.com)
  Store as: MACHINE_B_HOST

QUESTION 3.2: "What SSH user should I connect as?"
  Default: Same as current user
  Store as: MACHINE_B_USER

QUESTION 3.3: "Have you already set up SSH key-based authentication from this machine to Machine B?"
  Options:
    A) Yes — key is configured
    B) No — help me set it up
```

### If 3.3 = B (Set up SSH keys):

Walk the human through step by step:

```
Step 1: Generate SSH key pair (if not already done)
  "Run this on Machine A (this machine):"
  ssh-keygen -t ed25519 -C "orchestrator-to-agents"
  → Accept default location (~/.ssh/id_ed25519)
  → No passphrase (for automated agent invocation)

Step 2: Copy public key to Machine B
  "Run this on Machine A:"
  ssh-copy-id {MACHINE_B_USER}@{MACHINE_B_HOST}
  → Human enters Machine B password one last time
  → After this, password-less SSH works

Step 3: Verify
  ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "echo CONNECTION_OK"
  → Should print CONNECTION_OK without asking for password
```

### Connection Verification Tests

```
TEST 3.1 — SSH connection
  Run: ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "echo CONNECTION_OK"
  Pass: Returns "CONNECTION_OK" within 5 seconds
  Fail: Connection refused, timeout, or key not accepted

TEST 3.2 — Machine B Python version
  Run: ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "python3 --version"
  Pass: 3.10 or higher
  Fail: Tell human to install Python 3.10+ on Machine B

TEST 3.3 — Machine B OpenClaw installed
  Run: ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "openclaw --version"
  Pass: Returns version number
  Fail: Tell human to install OpenClaw on Machine B

TEST 3.4 — Machine B internet connectivity (Google Ads API)
  Run: ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "curl -s -o /dev/null -w '%{http_code}' https://googleads.googleapis.com"
  Pass: Returns 200 or 403 (auth required is fine)
  Fail: Machine B can't reach Google Ads API — check firewall/DNS

TEST 3.5 — Machine B → Supabase connectivity
  Run: ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "curl -s -o /dev/null -w '%{http_code}' {SUPABASE_URL}/rest/v1/"
  Pass: Returns 200
  Fail: Machine B can't reach Supabase — check firewall/DNS

TEST 3.6 — Machine B disk space
  Run: ssh {MACHINE_B_USER}@{MACHINE_B_HOST} "df -h . | awk 'NR==2 {print \$4}'"
  Pass: >2GB available
  Fail: Warn about low disk space (creative assets need room)
```

### Output

```
Phase 3: Machine B Connection
✅ SSH: Connected to {MACHINE_B_USER}@{MACHINE_B_HOST}
✅ Python 3.x.x on Machine B
✅ OpenClaw vX.X.X on Machine B
✅ Machine B → Google Ads API: reachable
✅ Machine B → Supabase: reachable
✅ Machine B disk space: X.XGB available
→ Phase 3 COMPLETE
```

---

## Phase 4: Agent Deployment

**Purpose:** Install and configure all 7 sub-agent skills on Machine B.

### Ask the Human

```
QUESTION 4.1: "Where should agent skill files be stored on Machine B?"
  Default: ~/google-ads-agents/
  Store as: AGENT_DIR
```

### Deployment Steps

For each of the 7 agents, in priority order:

```
DEPLOY 4.1 — Data & Placement Analyst (priority 1)
  1. Copy SKILL.md to Machine B:
     scp google-ads-data-placement-analyst/SKILL.md {MACHINE_B}:{AGENT_DIR}/google-ads-data-placement-analyst/SKILL.md
  2. Set environment variables on Machine B:
     ssh {MACHINE_B} "echo 'export SUPABASE_URL={URL}' >> ~/.bashrc"
     ssh {MACHINE_B} "echo 'export SUPABASE_SERVICE_KEY={KEY}' >> ~/.bashrc"
  3. Verify the agent is recognized by OpenClaw:
     ssh {MACHINE_B} "openclaw list" → should include google-ads-data-placement-analyst

DEPLOY 4.2 — Creative Analyst (priority 2)
  Same as above for google-ads-creative-analyst

DEPLOY 4.3 — Post-Click Analyst (priority 3)
  Same as above for google-ads-postclick-analyst

DEPLOY 4.4 — Competitive Intel Analyst (priority 4)
  Same as above for google-ads-competitive-intel

DEPLOY 4.5 — Creative Producer (priority 5)
  Same as above, plus:
  - Set GEMINI_API_KEY on Machine B:
    ssh {MACHINE_B} "echo 'export GEMINI_API_KEY={KEY}' >> ~/.bashrc"
  - Install Python dependencies:
    ssh {MACHINE_B} "pip install Pillow google-generativeai"
  - Verify Gemini access from Machine B:
    ssh {MACHINE_B} "python3 -c \"import google.generativeai; print('OK')\""

DEPLOY 4.6 — Campaign Creator (priority 6)
  Same as above for google-ads-campaign-creator

DEPLOY 4.7 — Campaign Monitor (priority 7)
  Same as above for google-ads-campaign-monitor
```

### Environment Variables Summary (Machine B ~/.bashrc)

After all deployments, Machine B should have:
```bash
export SUPABASE_URL="https://xyzproject.supabase.co"
export SUPABASE_SERVICE_KEY="eyJ..."
export GEMINI_API_KEY="AI..."
# Google Ads API credentials and GA4 credentials are in Supabase Vault
# Agents read them from Vault at runtime
```

### Verification

```
ssh {MACHINE_B} "openclaw list"
→ Should show all 7 agents:
  google-ads-data-placement-analyst
  google-ads-creative-analyst
  google-ads-postclick-analyst
  google-ads-competitive-intel
  google-ads-creative-producer
  google-ads-campaign-creator
  google-ads-campaign-monitor
```

### Output

```
Phase 4: Agent Deployment
✅ Data & Placement Analyst deployed
✅ Creative Analyst deployed
✅ Post-Click Analyst deployed
✅ Competitive Intel Analyst deployed
✅ Creative Producer deployed (+ Gemini + Pillow verified)
✅ Campaign Creator deployed
✅ Campaign Monitor deployed
✅ All 7 agents recognized by OpenClaw on Machine B
→ Phase 4 COMPLETE
```

---

## Phase 5: Brand Onboarding

**Purpose:** Onboard one or more brands with brand-specific configuration and credentials.

**Multi-Brand Support:** This phase can be run once for a single brand, or multiple times to onboard additional brands. Each brand has its own Google Ads credentials, GA4 credentials, and configuration.

### How Many Brands?

```
QUESTION 5.0: "How many brands do you want to set up today?"
  Options: 1, 2, 3, or more
  Response: Integer (e.g., "1" for single brand, "3" for three brands)
  Scope: Determines loop count for questions below
```

For EACH brand, ask all questions in logical groups below.

### Group A: Brand Identity & Credentials

```
QUESTION 5A.1: "What is your brand name?"
  Store: brand_config.brand_name

QUESTION 5A.2: "Describe your product in one sentence."
  Store: brand_config.product_description
  Purpose: Helps Creative Producer write ad copy and build image prompts

QUESTION 5A.3: "What is your website URL?"
  Store: brand_config.website_url

QUESTION 5A.4: "What is your Google Ads customer ID?"
  Format: xxx-xxx-xxxx (e.g., 123-456-7890)
  Validate: Must be 10 digits with hyphens
  Store: Temporary (will store in brand_config as google_ads_customer_id)
  Scope: This brand only

QUESTION 5A.5: "Do you have a Google Ads Manager Account (MCC)?"
  Format: xxx-xxx-xxxx (manager customer ID, if applicable)
  Store: brand_config.google_ads_mcc_id (optional, NULL if none)
  Scope: This brand only

QUESTION 5A.6: "What is your Google Ads Developer Token?"
  Where to find: Google Ads → Tools & Settings → API Center → Developer Token
  ⚠️ NEVER display this token back after storing
  Process:
    1. Store token in Supabase Vault
    2. Retrieve vault_reference_id
    3. Store vault_reference_id in brand_config.google_ads_developer_token_vault_ref
  Scope: This brand only

QUESTION 5A.7: "What is your Google Ads OAuth2 Client ID?"
  Where to find: Google Cloud Console → APIs & Services → Credentials
  Store: Temporary (will store in brand_config.google_ads_oauth_client_id)
  Scope: This brand only

QUESTION 5A.8: "What is your Google Ads OAuth2 Client Secret?"
  Where to find: Google Cloud Console → APIs & Services → Credentials
  ⚠️ NEVER display this secret back after storing
  Process:
    1. Store secret in Supabase Vault
    2. Retrieve vault_reference_id
    3. Store vault_reference_id in brand_config.google_ads_oauth_secret_vault_ref
  Scope: This brand only

STEP 5A.9: "I'll now generate your OAuth2 Refresh Token automatically."
  DO NOT ask the human for a refresh token. Generate it using the Client ID (5A.7) and Client Secret (5A.8).

  Process:
    1. Tell the human: "I'll open a browser window for you to authorize access to your Google Ads account."
    2. Run the OAuth2 flow using the Client ID and Client Secret:
       ```python
       from google_auth_oauthlib.flow import InstalledAppFlow

       flow = InstalledAppFlow.from_client_config(
           {
               "installed": {
                   "client_id": "$OAUTH_CLIENT_ID",       # from 5A.7
                   "client_secret": "$OAUTH_CLIENT_SECRET", # from 5A.8
                   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                   "token_uri": "https://oauth2.googleapis.com/token"
               }
           },
           scopes=["https://www.googleapis.com/auth/adwords"]
       )
       flow.run_local_server(port=8080)
       refresh_token = flow.credentials.refresh_token
       ```
    3. A browser window opens → human logs in with the Google account that has access to the Google Ads account → clicks "Allow"
    4. The refresh token is captured automatically
    5. Tell the human: "✅ Authorization successful. Refresh token captured."
    6. Store refresh token in Supabase Vault
    7. Retrieve vault_reference_id
    8. Store vault_reference_id in brand_config.google_ads_refresh_token_vault_ref

  ⚠️ NEVER display the refresh token to the human. Store it directly in Vault.
  ⚠️ If the OAuth flow fails (e.g., browser doesn't open, human denies access), tell them exactly what went wrong and retry.
  Scope: This brand only

QUESTION 5A.10: "What is your GA4 property ID?"
  Format: Numeric (e.g., 123456789)
  Where to find: Google Analytics → Admin → Property Settings → Property ID
  Store: Temporary (will store in brand_config.ga4_property_id)
  Scope: This brand only

QUESTION 5A.11: "Do you have a GA4 service account JSON key file?"
  Options:
    A) Yes, here's the file/path
    B) Not yet — help me create one
  If B: Walk the human through:
    1. Go to Google Cloud Console → IAM → Service Accounts
    2. Create service account with "Viewer" role
    3. Generate JSON key
    4. Add the service account email to GA4 property as "Viewer"
  Process:
    1. Store credentials in Supabase Vault
    2. Retrieve vault_reference_id
    3. Store vault_reference_id in brand_config.ga4_credentials_vault_ref
  Scope: This brand only

QUESTION 5A.12: "What is your Google Merchant Center ID (for Shopping campaigns)?"
  Format: Numeric (e.g., 123456789)
  Optional: NULL if not using Shopping campaigns
  Store: brand_config.merchant_center_id
  Scope: This brand only

QUESTION 5A.13: "What is your YouTube channel ID (for Video campaigns)?"
  Format: Channel ID starting with UC (e.g., UCxxxxxxxxxxxxxxxx)
  Optional: NULL if not using Video campaigns
  Store: brand_config.youtube_channel_id
  Scope: This brand only

QUESTION 5A.14: "Are there any special ad categories that apply to this brand?"
  Options:
    A) None — standard business
    B) Credit (financial products)
    C) Housing (real estate)
    D) Employment (job ads)
    E) Social issues / politics
  Store: brand_config.special_ad_category
  Note: This affects targeting restrictions — Campaign Creator must enforce these
  Scope: This brand only

QUESTION 5A.15: "What are your brand colors? (Provide hex codes)"
  Ask for:
    - Primary color (hex)
    - Secondary color (hex)
    - Accent color (hex)
    - Background color (hex, used for ad backgrounds)
    - Badge/overlay color (hex, used for price tags, discount badges)
  Store: brand_config.color_palette (JSON)

QUESTION 5A.16: "Describe your logo so the AI can identify it in images."
  Example: "Blue shield icon with white 'X' in center, company name in Helvetica Bold below"
  Store: brand_config.locked_elements.logo_description

QUESTION 5A.17: "Describe your product imagery (what should always appear in ads)."
  Example: "White product box with blue label, shown at 45-degree angle"
  Store: brand_config.locked_elements.product_description

QUESTION 5A.18: "Any compliance text that must appear on every ad?"
  Example: "FDA disclaimer: These statements have not been evaluated by the FDA..."
  Options: A) Yes (provide text)  B) No compliance text needed
  Store: brand_config.locked_elements.compliance_text
```

### Group B: Performance Targets & Market Vertical

```
QUESTION 5B.1: "What is your target CPA (Cost Per Acquisition)?"
  Note: This is the AR (Assumed Real) CPA — the price you want to pay per conversion.
  Format: Dollar amount (e.g., $25.00)
  Store: brand_config.target_ar_cpa

QUESTION 5B.2: "What is your target ROAS (Return on Ad Spend)?"
  Note: This is the AR ROAS — the revenue you expect per dollar spent.
  Format: Multiplier (e.g., 3.0 means $3 revenue per $1 spent)
  Store: brand_config.target_ar_roas

QUESTION 5B.2a: "What is the MINIMUM acceptable AR ROAS for this brand?"
  Explain: "This is the FLOOR — campaigns performing below this threshold for 7+ days will be recommended for pause. This should be lower than your target ROAS. For example, if your target ROAS is 3.0×, your minimum might be 1.5× (at least breaking even on ad spend after margins)."
  Store: brand_config.min_acceptable_ar_roas
  Default suggestion: "If unsure, a common starting point is 1.0× (break-even on ad spend) or your profit margin (e.g., if 50% margin, then 2.0× minimum)"

QUESTION 5B.3: "What is your daily budget constraint?"
  Note: The system will NEVER spend more than this without your explicit approval.
  Format: Dollar amount (e.g., $500/day)
  Store: brand_config.daily_budget_constraint

QUESTION 5B.4: "What is your monthly budget constraint?"
  Format: Dollar amount (e.g., $15,000/month)
  Store: brand_config.monthly_budget_constraint

QUESTION 5B.5: "Do you have historical data to calibrate the AR multiplier?"
  Context: By default, AR = GA4 × 1.2 (assuming GA4 under-counts by ~20%).
  If you have CRM or backend data, we can calibrate the multiplier precisely.
  Options:
    A) Use default 1.2× multiplier
    B) I have CRM data — let's calibrate
  If B: Ask for actual conversions vs. GA4-reported conversions for last 30 days.
        Calculate: AR multiplier = actual conversions / GA4 conversions
  Store: brand_config.ar_multiplier

QUESTION 5B.6: "What market vertical or category is this brand?"
  Examples: "DTC skincare", "premium pet food", "financial services", "organic supplements"
  Purpose: Competitive Intel Analyst uses this for keyword-based Ad Library scanning
  Store: brand_config.market_vertical

QUESTION 5B.7: "What timezone is your Google Ads account set to?"
  Format: IANA timezone (e.g., America/New_York, Europe/London, Asia/Tokyo)
  Where to find: Google Ads → Tools & Settings → Account Settings → Timezone
  Default: America/New_York
  Store: brand_config.timezone
  Note: ALL metrics will be aligned to this timezone. Must match Google Ads account timezone exactly.

QUESTION 5B.8: "What currency is your Google Ads account set to?"
  Format: ISO 4217 code (e.g., USD, EUR, GBP, AUD)
  Where to find: Google Ads → Tools & Settings → Account Settings → Currency
  Default: USD
  Store: brand_config.currency
  Note: All spend, revenue, CPA, and budget values will be in this currency.

QUESTION 5B.9: "How many new ad creatives do you want to produce per week?"
  Explain: "This controls creative volume. Each cycle, the system will produce this many new creatives split between: your competitor inspiration ideas (priority), competitive intelligence finds, and variants of your own winning ads."
  Store: brand_config.weekly_ad_volume
  Default: 3
  Range: 1-10 (note: more ads = more Gemini API usage)

QUESTION 5B.10: "Do you want automatic campaign scaling proposals?"
  Explain: "When a campaign is spending its full budget AND has strong ROAS, the system can propose budget increases for your approval. You always approve — it never auto-scales."
  If yes, ask:
    - "Budget increase step size?" (default: 20%, meaning each scaling event proposes +20%)
    - "Minimum AR ROAS required to propose scaling?" (default: 1.5×)
    - "How many consecutive days at budget cap before proposing?" (default: 3)
    - "Cooldown days between scaling proposals?" (default: 2)
    - "Maximum daily budget cap?" (optional, no default)
  Store: brand_config.scaling_config as JSONB

QUESTION 5B.11: "What are your top conversion action IDs in Google Ads?"
  Explain: "These are the conversion tracking action IDs that drive your optimization. Campaign Creator will optimize campaigns to these actions."
  Format: Comma-separated conversion action IDs (e.g., 1234567890, 1234567891, 1234567892)
  Store: brand_config.conversion_action_ids (JSON array)
  Note: Can add/update these later without re-onboarding

QUESTION 5B.12: "What is your preferred bid strategy type?"
  Options:
    A) Target CPA (cost per acquisition)
    B) Target ROAS (return on ad spend)
    C) Maximize Conversions (with target CPA cap)
    D) Maximize Conversion Value (with target ROAS cap)
    E) Manual CPC
  Store: brand_config.bid_strategy_preference
  Default: Target ROAS (most common for e-commerce)
```

### Group C: Creative Configuration

```
QUESTION 5C.1: "Describe 3-5 hero image variants for your ads."
  Purpose: These are the main visual approaches for ad images.
  Per variant, provide:
    - Name (e.g., "Product Hero", "Lifestyle Shot", "Flat Lay")
    - Detailed image description for AI generation
  Example: "Product Hero: White product box centered on gradient blue background,
            soft shadow below, slight 15-degree tilt, premium feel"
  Store: brand_config.hero_variants (JSON array)

QUESTION 5C.2: "What text overlay angles do you use in ads?"
  Default categories provided. Human can customize:
    - Price: ["SAVE 50% TODAY", "LOWEST PRICE GUARANTEED"]
    - Social Proof: ["TRUSTED BY 500K+", "4.9★ RATED"]
    - Benefits: ["RESULTS IN 24 HOURS", "CLINICALLY PROVEN"]
    - Shipping: ["FREE SHIPPING", "ARRIVES TOMORROW"]
    - Urgency: ["ENDS TONIGHT", "ONLY 3 LEFT"]
    - Trust: ["MONEY-BACK GUARANTEE", "30-DAY FREE TRIAL"]
  Ask: "Would you like to customize these, or use the defaults as a starting point?"
  Store: brand_config.text_angles (JSON)

QUESTION 5C.3: "Are there any banned words for your industry?"
  Context: Words that trigger Google Ads rejections or violate your brand guidelines.
  Examples by vertical:
    - Health: "cure", "treat", "prescription", "miracle"
    - Finance: "guaranteed returns", "risk-free", "get rich"
    - Weight loss: "before/after", "overnight results"
  Ask: "List any words that should NEVER appear in your ads."
  Store: brand_config.banned_words (JSON array)

QUESTION 5C.4: "What aspect ratios do you want to produce?"
  Defaults:
    - Display: 1.91:1 (1200×628) — search result ads
    - Discovery: 1:1 (1080×1080) — feed ads
    - Video (YouTube): 16:9 (1920×1080) or 9:16 (1080×1920)
    - Shopping: 1.1:1 (1200×628) — product listing ads
  Ask: "Use these standard ratios, or customize?"
  Store: brand_config.aspect_ratios (JSON)
```

### Group D: Competitors

```
QUESTION 5D.1: "List your top 3-5 competitors to monitor for this brand."
  Per competitor:
    - Brand name
    - Domain/website URL
    - Priority: HIGH, MEDIUM, or LOW
  Store: competitors table (one row per competitor, linked to this brand_id)
```

### Group E: Landing Pages & Pixel

```
QUESTION 5E.1: "List your active landing page URLs for this brand."
  Per URL:
    - Full URL
    - Page type: product, collection, homepage, lead gen, funnel
    - Primary campaign it's used for (if known)
  Store: landing_pages table (one row per URL, linked to this brand_id)
  Note: Post-Click Analyst will validate these in the first cycle

QUESTION 5E.2: "Is the Google conversion tag installed on all landing pages for this brand?"
  Options:
    A) Yes — on all pages
    B) Some pages — need help identifying which ones
    C) Not yet — help me install it
  If B or C: Flag for Data & Placement Analyst to verify tracking health
  Store: brand_config.conversion_tracking_status
```

### Write to Database — Per Brand

**Important:** For EACH brand, follow this process:

**Step 1: Store credentials in Supabase Vault**

```sql
-- Store Google Ads Developer Token in Vault
INSERT INTO vault_secrets (secret_type, secret_value)
VALUES ('google_ads_developer_token', $developer_token)
RETURNING id AS dev_token_vault_ref_id;

-- Store Google Ads OAuth Client Secret in Vault
INSERT INTO vault_secrets (secret_type, secret_value)
VALUES ('google_ads_oauth_secret', $oauth_client_secret)
RETURNING id AS oauth_secret_vault_ref_id;

-- Store Google Ads Refresh Token in Vault
INSERT INTO vault_secrets (secret_type, secret_value)
VALUES ('google_ads_refresh_token', $refresh_token)
RETURNING id AS refresh_token_vault_ref_id;

-- Store GA4 service account credentials in Vault
INSERT INTO vault_secrets (secret_type, secret_value)
VALUES ('ga4_credentials', $ga4_credentials_json)
RETURNING id AS ga4_vault_ref_id;
```

**Step 2: Insert Brand Config with vault references**

```sql
INSERT INTO brand_config (
  brand_name, product_description, website_url,
  google_ads_customer_id, google_ads_mcc_id,
  google_ads_developer_token_vault_ref,
  google_ads_oauth_client_id,
  google_ads_oauth_secret_vault_ref,
  google_ads_refresh_token_vault_ref,
  merchant_center_id, youtube_channel_id,
  ga4_property_id, ga4_credentials_vault_ref,
  special_ad_category,
  target_ar_cpa, target_ar_roas,
  min_acceptable_ar_roas,
  daily_budget_constraint, monthly_budget_constraint,
  ar_multiplier, market_vertical, conversion_tracking_status,
  color_palette, locked_elements, hero_variants,
  text_angles, banned_words, aspect_ratios,
  timezone, currency,
  weekly_ad_volume, scaling_config,
  conversion_action_ids, bid_strategy_preference
) VALUES (
  $brand_name,                                    -- Phase 5, Q5A.1
  $product_description,                           -- Phase 5, Q5A.2
  $website_url,                                   -- Phase 5, Q5A.3
  $google_ads_customer_id,                        -- Phase 5, Q5A.4
  $google_ads_mcc_id,                             -- Phase 5, Q5A.5
  $dev_token_vault_ref_id,                        -- ← vault reference from Step 1
  $google_ads_oauth_client_id,                    -- Phase 5, Q5A.7
  $oauth_secret_vault_ref_id,                     -- ← vault reference from Step 1
  $refresh_token_vault_ref_id,                    -- ← vault reference from Step 1
  $merchant_center_id,                            -- Phase 5, Q5A.12
  $youtube_channel_id,                            -- Phase 5, Q5A.13
  $ga4_property_id,                               -- Phase 5, Q5A.10
  $ga4_vault_ref_id,                              -- ← vault reference from Step 1
  $special_ad_category,                           -- Phase 5, Q5A.14
  $target_ar_cpa,                                 -- Phase 5, Q5B.1
  $target_ar_roas,                                -- Phase 5, Q5B.2
  $min_acceptable_ar_roas,                        -- Phase 5, Q5B.2a
  $daily_budget_constraint,                       -- Phase 5, Q5B.3
  $monthly_budget_constraint,                     -- Phase 5, Q5B.4
  $ar_multiplier,                                 -- Phase 5, Q5B.5 (default 1.20)
  $market_vertical,                               -- Phase 5, Q5B.6
  $conversion_tracking_status,                    -- Phase 5, Q5E.2
  $color_palette,                                 -- Phase 5, Q5A.15
  $locked_elements,                               -- Phase 5, Q5A.16 + Q5A.17 + Q5A.18
  $hero_variants,                                 -- Phase 5, Q5C.1
  $text_angles,                                   -- Phase 5, Q5C.2
  $banned_words,                                  -- Phase 5, Q5C.3
  $aspect_ratios,                                 -- Phase 5, Q5C.4
  $timezone,                                      -- Phase 5, Q5B.7
  $currency,                                      -- Phase 5, Q5B.8
  $weekly_ad_volume,                              -- Phase 5, Q5B.9
  $scaling_config,                                -- Phase 5, Q5B.10 (JSONB with scaling params)
  $conversion_action_ids,                         -- Phase 5, Q5B.11 (JSON array)
  $bid_strategy_preference                        -- Phase 5, Q5B.12
) RETURNING id AS brand_id;
-- Store BRAND_ID for confirmation display and Cycle creation
```

**Step 3: Insert Competitors (linked to this brand)**

```sql
INSERT INTO competitors (brand_id, name, domain_url, priority) VALUES
  ($brand_id, 'Competitor A', 'https://competitorA.com', 'HIGH'),
  ($brand_id, 'Competitor B', 'https://competitorB.com', 'MEDIUM'),
  ...;
```

**Step 4: Insert Landing Pages (linked to this brand)**

```sql
INSERT INTO landing_pages (brand_id, url, page_type) VALUES
  ($brand_id, 'https://brand.com/product', 'product'),
  ($brand_id, 'https://brand.com/checkout', 'funnel'),
  ...;
```

**Step 5: Display brand confirmation**

After successful INSERT, display:
```
✅ Brand onboarded: "[Brand Name]"
   Brand ID (UUID): $brand_id
   Google Ads Customer ID: 123-456-7890
   GA4 Property: 123456789
   Market Vertical: DTC skincare

Please confirm this looks correct: [YES/NO]
```

**Step 6: Repeat for additional brands**

If NUM_BRANDS > 1, loop back to Group A for the next brand.

### Output

```
Phase 5: Brand Onboarding (Multi-Brand)
✅ Brand 1: "Brand Name A" (UUID: xxxxx...)
   - Targets: AR CPA $XX.XX / AR ROAS X.XX
   - Budget: $XXX/day, $XX,XXX/month
   - Competitors: X | Landing pages: X
✅ Brand 2: "Brand Name B" (UUID: yyyyy...)
   - Targets: AR CPA $XX.XX / AR ROAS X.XX
   - Budget: $XXX/day, $XX,XXX/month
   - Competitors: X | Landing pages: X
...
✅ Total brands onboarded: X
✅ Credentials stored securely in Supabase Vault
→ Phase 5 COMPLETE
```

---

## Phase 6: Agent Testing

**Purpose:** Test each agent one by one, in priority order. Each test verifies the agent can start, read from Supabase, execute its core function, and write results back.

**Multi-Brand Testing:** If multiple brands were onboarded, test the FIRST brand (or ask which brand to test first). All test commands include --brand $BRAND_ID.

### Pre-Test Setup

Before testing, create a test optimization cycle:

```sql
INSERT INTO optimization_cycles (
  brand_id, cycle_number, status, phase, started_at
) VALUES (
  $BRAND_ID, 0, 'TESTING', 'SETUP', NOW()
) RETURNING id;
-- Store returned ID as TEST_CYCLE_ID
```

### Test Protocol — Same for Every Agent

For each agent:

1. **Create test task** in `agent_deliverables`:
```sql
INSERT INTO agent_deliverables (
  cycle_id, agent_name, deliverable_type, status,
  execution_priority, content_json
) VALUES (
  {TEST_CYCLE_ID}, '{agent_name}', 'SETUP_TEST', 'PENDING',
  {priority}, '{"test": true, "mode": "setup_verification"}'
) RETURNING id;
-- Store as TEST_TASK_ID
```

2. **Trigger agent via SSH:**
```bash
ssh {MACHINE_B} "openclaw run {agent_skill_name} --cycle {TEST_CYCLE_ID} --task {TEST_TASK_ID} --brand {BRAND_ID}"
```

3. **Check result** in `agent_deliverables`:
```sql
SELECT status, delivered_at, content_json
FROM agent_deliverables
WHERE id = {TEST_TASK_ID};
```

4. **Pass criteria:**
   - Status = `DELIVERED` (agent completed successfully)
   - OR Status = `BLOCKED` with a specific, reasonable explanation (e.g., "no historical data for first cycle")
   - `delivered_at` is set
   - `content_json` contains meaningful output (not empty)

5. **Fail criteria:**
   - Agent didn't start (SSH error)
   - Agent crashed (no status update, or error in logs)
   - Status still `PENDING` after timeout (agent never picked up the task)
   - Status = `BLOCKED` with a vague or missing explanation

---

### Test 6.1: Data & Placement Analyst (Priority 1)

**What it should do in test mode:**
- Connect to Google Ads API → pull last 7 days of campaign data
- Connect to GA4 API → pull matching sessions/conversions
- Calculate AR metrics (GA4 × AR multiplier)
- Verify tracking health (do GA4 sessions exist for Google Ads campaigns?)
- Write results to `g_daily_metrics` and `tracking_health` tables
- Build at least one audience segment from the data (even if basic)
- Run Quality Score analysis on all active keywords

**Expected outcome:**
- `g_daily_metrics`: rows inserted for the last 7 days (or explanation if no active campaigns)
- `tracking_health`: at least one row per campaign
- `audiences`: at least one audience segment created (or explanation if insufficient data)
- `agent_deliverables`: DELIVERED with summary of data pulled

**Ask the human after test:**
```
"Data & Placement Analyst test complete. Here's what it found:
- [X] campaigns active in the last 7 days
- [X] days of data imported
- [X] tracking health issues found
- [X] audience segments built
- Quality Scores: [average score], [X] keywords with low scores
Does this match your expectations?"
```

---

### Test 6.2: Creative Analyst (Priority 2)

**What it should do in test mode:**
- Read from `g_daily_metrics` and `g_ads` (populated by Test 6.1)
- Rank ads by AR ROAS
- Detect creative fatigue on any ad
- Run text overlay density analysis on top ads (using Gemini vision)
- Extract color & visual DNA from top performers
- Write to `creative_registry` with analysis results

**Expected outcome:**
- `creative_registry`: entries for analyzed ads with visual DNA data
- `g_ads`: fatigue scores updated
- Color analysis: hex codes, palette types, mood for top performers
- `agent_deliverables`: DELIVERED with ad rankings, fatigue flags, and color profiles

---

### Test 6.3: Post-Click Analyst (Priority 3)

**What it should do in test mode:**
- Read landing pages from `landing_pages` table
- Pull GA4 session data for each landing page
- Calculate bounce rates, session duration, conversion rates
- Flag any pages with ultra-short sessions (>20% under 5 seconds)

**Expected outcome:**
- `landing_pages`: updated with performance metrics
- `agent_deliverables`: DELIVERED with landing page scorecard

---

### Test 6.4: Competitive Intel Analyst (Priority 4)

**What it should do in test mode:**
- Read competitors from `competitors` table
- Search Google Ads Ad Library for each competitor
- Pull active ad count, estimated spend tier, creative styles
- Write findings to `competitor_ads`

**Expected outcome:**
- `competitor_ads`: entries for discovered competitor ads
- `agent_deliverables`: DELIVERED with competitive landscape summary

---

### Test 6.5: Creative Producer (Priority 5)

**What it should do in test mode:**
- Read `brand_config` for hero variants, colors, text angles
- Generate ONE test image using brand DNA
- Apply ONE text overlay from brand config text_angles
- Run full QC pipeline
- Write to `creative_registry`

**Expected outcome:**
- One test image generated and QC-passed
- `creative_registry`: entry with QC scores and visual metadata
- `agent_deliverables`: DELIVERED with image reference and full QC report

---

### Test 6.6: Campaign Creator (Priority 6)

**What it should do in test mode:**
- Read `brand_config`, `audiences`, `creative_registry`
- Build a test campaign structure in DRAFT status (does NOT create in Google Ads)
- Write campaign plan to `g_campaigns`, `g_ad_groups`, `g_ads` tables
- Include budget proposal in deliverable
- Validate UTM parameters on every ad (utm_source=google, utm_medium=cpc, etc.)
- Run the full launch checklist

**Expected outcome:**
- `g_campaigns`: one row in DRAFT status
- `g_ad_groups`: structured ad groups with targeting
- `g_ads`: ads linked to creative assets with valid UTMs
- `agent_deliverables`: DELIVERED with campaign spec sheet and launch checklist

---

### Test 6.7: Campaign Monitor (Priority 7)

**What it should do in test mode:**
- Read `g_campaigns`, `g_daily_metrics`, `g_ads`, `alerts`, `tracking_health`
- Run daily monitoring checklist on any active campaigns
- Check tracking health: are GA4 sessions appearing for Google-driven traffic?
- Check Quality Scores: any keywords with low scores?
- Generate a test daily brief
- Write alerts for any issues found

**Expected outcome:**
- `alerts`: any detected issues
- `agent_deliverables`: DELIVERED with daily brief

---

### Post-Testing Cleanup

After all 7 tests pass:

```sql
-- Mark test cycle as complete
UPDATE optimization_cycles
SET status = 'COMPLETED', phase = 'SETUP_COMPLETE', ended_at = NOW()
WHERE id = {TEST_CYCLE_ID};

-- Mark all test deliverables
UPDATE agent_deliverables
SET content_json = content_json || '{"setup_test": true}'
WHERE cycle_id = {TEST_CYCLE_ID};
```

### Output

```
Phase 6: Agent Testing
✅ Data & Placement Analyst: PASS (X campaigns, X days of data)
✅ Creative Analyst: PASS (X ads ranked, X fatigued)
✅ Post-Click Analyst: PASS (X pages scored)
✅ Competitive Intel: PASS (X competitors, X ads catalogued)
✅ Creative Producer: PASS (test image QC X.X/10)
✅ Campaign Creator: PASS (DRAFT campaign structured)
✅ Campaign Monitor: PASS (daily brief generated)
→ Phase 6 COMPLETE — All 7 agents operational
```

---

## Phase 7: System Readiness

**Purpose:** Final checks, create the first real optimization cycle, and hand off to the Orchestrator.

### Final Verification Checklist

```
CHECK 7.1 — All phases complete
  Verify: Phases 0-6 all show COMPLETE
  If any incomplete: list what's still pending

CHECK 7.2 — Supabase data integrity
  Query: SELECT COUNT(*) FROM brand_config → should be ≥ 1 (number of brands onboarded)
  Query: SELECT COUNT(*) FROM competitors → should be ≥ 1 (per brand)
  Query: SELECT COUNT(*) FROM landing_pages → should be ≥ 1 (per brand)
  Query: SELECT brand_id, brand_name FROM brand_config → verify all brands present

CHECK 7.3 — All environment variables set on both machines
  Machine A: SUPABASE_URL, SUPABASE_SERVICE_KEY
  Machine B: SUPABASE_URL, SUPABASE_SERVICE_KEY, GEMINI_API_KEY

CHECK 7.4 — SSH still working
  Run: ssh {MACHINE_B} "echo READY"
  Pass: Returns "READY"

CHECK 7.5 — All agents still recognized by OpenClaw
  Run: ssh {MACHINE_B} "openclaw list"
  Pass: All 7 agents listed
```

### Create Cycle #1 (Per Brand)

**If one brand:** Create Cycle #1 for that brand.

**If multiple brands:** Create Cycle #1 for EACH brand.

```sql
-- For each brand onboarded in Phase 5:
INSERT INTO optimization_cycles (
  brand_id, cycle_number, status, phase, started_at
) VALUES (
  $BRAND_ID, 1, 'ACTIVE', 'PHASE_1', NOW()
) RETURNING id;
-- Repeat for each brand in list
```

### Write Setup Record

Store the complete setup configuration for future reference:

```sql
INSERT INTO agent_deliverables (
  cycle_id, agent_name, deliverable_type, status,
  content_json, delivered_at
) VALUES (
  {CYCLE_1_ID}, 'orchestrator', 'SETUP_RECORD', 'DELIVERED',
  '{
    "setup_completed_at": "...",
    "machine_a": "...",
    "machine_b_host": "...",
    "machine_b_user": "...",
    "agents_deployed": 7,
    "agents_tested": 7,
    "brand_name": "...",
    "supabase_project": "...",
    "phases_completed": [0,1,2,3,4,5,6,7]
  }',
  NOW()
);
```

### Present Summary to Human

```
========================================
  GOOGLE ADS AI SYSTEM — SETUP COMPLETE
========================================

Machines: A (Orchestrator) ←→ B (7 Agents)
Database: Supabase connected, schema applied
Agents: 7/7 deployed and tested

Brands Onboarded: X
  Brand 1: [Brand Name A]
    - AR CPA: $XX.XX / AR ROAS X.XX
    - Daily budget: $XXX / Monthly: $XX,XXX
    - Competitors: X | Landing pages: X
  Brand 2: [Brand Name B]
    - AR CPA: $XX.XX / AR ROAS X.XX
    - Daily budget: $XXX / Monthly: $XX,XXX
    - Competitors: X | Landing pages: X
  ...

Credentials: Stored securely in Supabase Vault
  - Supabase: System-wide
  - Gemini API: System-wide
  - Google Ads credentials: Per-brand (vault references)
  - GA4 credentials: Per-brand (vault references)

Cycles Created:
  - Cycle #1 ACTIVE for each brand

Next steps:
  1. For each brand, I'll start Cycle #1 by running Data & Placement Analyst for fresh data
  2. I'll present you with a Cycle Summary before taking any action
  3. ALL budget decisions require your approval — the system never spends on its own

Ready to begin? Say "start cycle" and I'll kick things off.
========================================
```

### Output

```
Phase 7: System Readiness
✅ All 7 phases complete
✅ Database populated: X brands, X total competitors, X total landing pages
✅ Credentials stored securely in Vault (system-wide + per-brand)
✅ Environment variables verified on both machines
✅ SSH connection stable
✅ Cycles #1 created and ACTIVE for each brand
→ SETUP COMPLETE — System is operational for X brands
```

---

## Re-Running Setup

This skill can be re-invoked for:

- **New brand onboarding** — Skip Phases 0-4, run Phase 5 (new brand) + Phase 6 (re-test) + Phase 7
- **Machine migration** — Run Phase 3 (new Machine B) + Phase 4 (redeploy) + Phase 6 (re-test)
- **Troubleshooting** — Run Phase 6 to re-test a specific agent

To run a specific phase only:
```bash
openclaw run google-ads-setup --phase 5
```

---

## Add New Brand (Phase 5 Only)

After initial setup is complete, you can onboard additional brands WITHOUT repeating Phases 0-4.

**Prerequisites:**
- System-wide credentials (Supabase, Gemini) already collected in initial Phase 2
- Machines A and B still connected and ready
- All 7 agents deployed

**How to run:**
```bash
openclaw run google-ads-setup --phase 5 --skip-phases 0-4
```

**Full new brand setup (without initial infrastructure):**
```bash
openclaw run google-ads-setup --phase 5 --skip-phases 0-4
openclaw run google-ads-setup --phase 6 --skip-phases 0-5
openclaw run google-ads-setup --phase 7 --skip-phases 0-6
```

This allows you to onboard brands on a rolling basis, one at a time, without re-configuring infrastructure.

---

## Troubleshooting Reference

### Common Setup Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| SSH connection refused | Firewall blocking port 22 | Open port 22 on Machine B for Machine A's IP |
| SSH asks for password | Key not copied correctly | Re-run ssh-copy-id |
| Google Ads API returns error | Token expired or wrong permissions | Re-generate OAuth2 refresh token with appropriate scopes |
| GA4 returns no data | Service account not added to property | Add service account email as Viewer in GA4 Admin |
| Gemini returns 403 | API key invalid or billing not enabled | Check Google AI Studio for key status |
| Agent returns PENDING forever | OpenClaw can't find the skill | Verify SKILL.md is in the correct directory |
| Agent returns BLOCKED on first run | No historical data | Expected for fresh accounts — agent should explain what's missing |
| Supabase INSERT fails | RLS blocking service role | Check service role policy allows all operations |
| QC fails every image | Brand config descriptions too vague | Improve hero_variants and locked_elements descriptions |

---

## Database (Supabase)

### Tables This Skill WRITES To
- `brand_config` — initial brand configuration (Phase 5)
- `competitors` — competitor entries (Phase 5)
- `landing_pages` — landing page URLs (Phase 5)
- `optimization_cycles` — test cycle #0 and real cycle #1 (Phase 6, 7)
- `agent_deliverables` — test tasks and setup record (Phase 6, 7)
- `setup_log` — setup phase tracking (all phases)

### Key Queries

**Verify schema completeness:**
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' ORDER BY table_name;
```

**Check setup status:**
```sql
SELECT phase, status, completed_at FROM setup_log ORDER BY phase;
```

**Verify all agents tested:**
```sql
SELECT agent_name, status FROM agent_deliverables
WHERE deliverable_type = 'SETUP_TEST' ORDER BY execution_priority;
-- All 7 should show DELIVERED
```


## ⚠️ DOUBLE-CONFIRMATION RULE (MANDATORY)
Before executing ANY campaign change (pause, enable, create, modify budgets, targeting, creatives, bids, exclusions, or any other modification), you MUST:
1. Present the proposed changes clearly to the user
2. Ask for explicit confirmation ONE MORE TIME before executing
3. Only proceed after receiving that second confirmation
This applies to ALL changes — no exceptions. This prevents accidental modifications.

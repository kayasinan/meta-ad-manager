# Frequency Strategy — Optimal Ad Frequency Analysis

## Data Source
90-day analysis (Nov 17, 2025 → Feb 15, 2026) across both accounts.
All ROAS = Estimated Real (Meta × 0.80).

---

## Findings

### Pet Bucket (Prospecting-heavy)

| Frequency Range | Ad Sets | Avg ER ROAS | Avg ER CPA | Avg CVR% |
|-----------------|---------|-------------|------------|----------|
| 1.0 - 2.0 | 36 | 1.85x | $74.46 | 0.049% |
| **2.0 - 3.0** | **9** | **4.55x** | **$34.10** | **0.134%** |
| 3.0 - 5.0 | 5 | 3.46x | $29.50 | 0.127% |
| 8.0+ | 3 | 3.54x | $29.34 | 1.246% |

**Sweet spot: 2.0 - 3.0x** — ROAS peaks, CPA drops 54% vs frequency 1-2.

Note: 8.0+ shows decent ROAS but this is ALL retargeting (VTC-inflated). Real performance is likely much lower.

### Vee Underwear (Retargeting-heavy)

| Frequency Range | Ad Sets | Avg ER ROAS | Avg ER CPA | Avg CVR% |
|-----------------|---------|-------------|------------|----------|
| 1.0 - 2.0 | 4 | 4.07x | $44.41 | 0.206% |
| 2.0 - 3.0 | 7 | 4.61x | $31.51 | 0.273% |
| **3.0 - 5.0** | **7** | **7.75x** | **$20.03** | **0.584%** |
| 5.0 - 8.0 | 2 | 5.04x | $20.39 | 0.333% |

**Sweet spot: 3.0 - 5.0x** — Peak ROAS + lowest CPA.

⚠️ However: Vee's 3-5x bucket is dominated by retargeting campaigns. Applying the retargeting VTC discount (×0.60 instead of ×0.80), the real sweet spot may be closer to **2.0 - 3.0x** — same as Pet Bucket.

---

## Optimal Frequency Caps

Based on the data, frequency performance follows this pattern:
```
Freq 1.0-1.5  →  Not enough exposure, low conversion
Freq 2.0-3.0  →  ✅ SWEET SPOT — enough exposure for decision, not annoying
Freq 3.0-5.0  →  Diminishing returns start (unless retargeting warm audience)
Freq 5.0+     →  Audience fatigue, wasted spend, negative brand perception
Freq 8.0+     →  🔴 CRITICAL — immediate creative refresh or pause
```

### Caps by Campaign Type

| Campaign Type | Frequency Cap | Reasoning |
|---------------|---------------|-----------|
| **Prospecting (TOF)** | **3x per 7 days** | Sweet spot is 2-3x. Beyond 3x, cold audiences tune out |
| **Retargeting (MOF)** | **4x per 7 days** | Warm audiences tolerate slightly more, but VTC inflates results past 4x |
| **Retargeting (BOF/DPA)** | **5x per 7 days** | Hot audiences close to buying, but cap to prevent annoyance |
| **ASC / Advantage+** | **4x per 7 days** | Mixed audience, Meta auto-optimizes but needs a ceiling |

### Alert Thresholds (Campaign Monitor)

| Frequency | Action |
|-----------|--------|
| **> 4x** (Prospecting) | ⚠️ WARNING — Monitor closely, consider creative refresh |
| **> 6x** (Retargeting) | ⚠️ WARNING — Creative refresh recommended |
| **> 8x** (Any) | 🔴 CRITICAL — Immediate creative refresh or pause |
| **> 12x** (Any) | 🔴 EMERGENCY — Recommend pause, audience is burnt |

---

## Implementation in Campaign Creator

When Agent 6 creates new campaigns:

1. **Set `frequency_control_specs`** on every ad set:
   ```json
   {
     "event": "IMPRESSIONS",
     "interval_days": 7,
     "max_frequency": <cap from table above>
   }
   ```

2. **Include in draft spec:**
   ```
   FREQUENCY CONTROL:
   - Type: [Prospecting/Retargeting]
   - Cap: [X] per 7 days
   - Current account avg frequency: [Y]
   - Rationale: Based on frequency analysis showing sweet spot at 2-3x
   ```

3. **Campaign Monitor checks:**
   - Every report includes frequency vs performance correlation
   - Auto-flag when any ad set exceeds its cap threshold
   - Track frequency trend (is it rising week over week?)

---

*Based on 90-day data from Pet Bucket + Vee Underwear. Refresh quarterly.*

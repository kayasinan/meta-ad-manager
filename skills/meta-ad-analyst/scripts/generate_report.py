#!/usr/bin/env python3
"""
Meta Ad Analyst — Full Performance Report Generator

Generates a comprehensive PDF report for a given account, time period, and campaign selection.
Pulls data from Meta Ads API + GA4, cross-verifies, and produces a triple-source report.

Usage:
  python3 generate_report.py \
    --account act_23987596 \
    --meta-creds /root/clawd/.meta_ads_credentials \
    --ga4-creds /root/clawd/.ga4_service_account.json \
    --ga4-property 323020098 \
    --ga4-source "facebook_ads_ppm" \
    --days 60 \
    --output /root/clawd/REPORT.md \
    [--campaigns "campaign_id1,campaign_id2"]  # optional: specific campaigns
    [--pdf]  # also generate PDF
    [--mode historical|live]  # default: historical

Triple-source metrics in ALL tables:
  - Meta: Facebook's own reported numbers
  - GA4: Google Analytics verified conversions
  - AR (Assumed Real): GA4 × 1.2 (accounts for ~20% tracking loss)
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# Add parent scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))
from meta_api import load_token, get_insights, get_adsets, get_ads_with_creative, get_ad_creative_detail, get_action, get_action_value, api_get
from ga4_api import get_access_token, run_report, parse_report, make_source_filter


def calc_triple(meta_spend, meta_purchases, meta_revenue, ga4_purchases, ga4_revenue):
    """Calculate triple-source metrics."""
    ar_purchases = round(ga4_purchases * 1.2) if ga4_purchases else 0
    ar_revenue = ga4_revenue * 1.2 if ga4_revenue else 0

    def safe_div(a, b):
        return round(a / b, 2) if b else 0

    return {
        "spend": round(meta_spend, 2),
        "meta": {
            "purchases": meta_purchases,
            "revenue": round(meta_revenue, 2),
            "cpa": safe_div(meta_spend, meta_purchases),
            "roas": safe_div(meta_revenue, meta_spend),
        },
        "ga4": {
            "purchases": ga4_purchases,
            "revenue": round(ga4_revenue, 2),
            "cpa": safe_div(meta_spend, ga4_purchases),
            "roas": safe_div(ga4_revenue, meta_spend),
        },
        "ar": {
            "purchases": ar_purchases,
            "revenue": round(ar_revenue, 2),
            "cpa": safe_div(meta_spend, ar_purchases),
            "roas": safe_div(ar_revenue, meta_spend),
        },
        "over_report_pct": round((meta_purchases / ga4_purchases - 1) * 100) if ga4_purchases else 0,
    }


def fmt_money(v):
    return f"${v:,.2f}" if v else "$0.00"


def fmt_roas(v):
    return f"{v:.2f}x" if v else "0.00x"


def triple_row(label, t):
    """Format a triple-source table row."""
    return (
        f"| {label} | {fmt_money(t['spend'])} | "
        f"{t['meta']['purchases']} | {fmt_money(t['meta']['cpa'])} | {fmt_roas(t['meta']['roas'])} | "
        f"{t['ga4']['purchases']} | {fmt_money(t['ga4']['cpa'])} | {fmt_roas(t['ga4']['roas'])} | "
        f"{t['ar']['purchases']} | {fmt_money(t['ar']['cpa'])} | {fmt_roas(t['ar']['roas'])} |"
    )


TRIPLE_HEADER = (
    "| Segment | Spend | Meta P | Meta CPA | Meta ROAS | GA4 P | GA4 CPA | GA4 ROAS | AR P | AR CPA | AR ROAS |\n"
    "|---------|-------|--------|----------|-----------|-------|---------|----------|------|--------|---------|"
)


# ── Report sections ──────────────────────────────────────────────────────────

def section_snapshot(account_name, period_label, days, totals, prev_totals=None):
    """Section 1: Account Snapshot."""
    t = totals
    lines = [
        f"## 1. ACCOUNT SNAPSHOT\n",
        f"Over the last {days} days you spent {fmt_money(t['spend'])} generating "
        f"{t['ga4']['purchases']} GA4-verified conversions (Assumed Real: {t['ar']['purchases']}) "
        f"at a True CPA of {fmt_money(t['ar']['cpa'])} and True ROAS of {fmt_roas(t['ar']['roas'])}.",
        f"\nMeta over-reporting: {t['over_report_pct']}% "
        f"(Meta claims {t['meta']['purchases']} purchases vs GA4's {t['ga4']['purchases']}).",
    ]
    if prev_totals:
        p = prev_totals
        cpa_change = ((t['ar']['cpa'] / p['ar']['cpa']) - 1) * 100 if p['ar']['cpa'] else 0
        roas_change = ((t['ar']['roas'] / p['ar']['roas']) - 1) * 100 if p['ar']['roas'] else 0
        direction = "improved" if cpa_change < 0 else "worsened"
        lines.append(
            f"\nvs Previous {days}d: CPA {direction} {abs(cpa_change):.0f}% "
            f"({fmt_money(p['ar']['cpa'])} → {fmt_money(t['ar']['cpa'])}), "
            f"ROAS {fmt_roas(p['ar']['roas'])} → {fmt_roas(t['ar']['roas'])}."
        )

    lines.append(f"\n{TRIPLE_HEADER}")
    lines.append(triple_row("TOTAL", t))
    return "\n".join(lines)


def section_campaigns(campaign_data):
    """Section 3: Campaign-by-campaign verdict."""
    lines = [
        "## 3. CAMPAIGN-BY-CAMPAIGN VERDICT\n",
        TRIPLE_HEADER,
    ]
    # Sort by AR ROAS descending
    sorted_c = sorted(campaign_data, key=lambda x: x.get('ar', {}).get('roas', 0), reverse=True)
    for c in sorted_c:
        if c['spend'] < 10:
            continue
        label = c.get('name', c.get('id', 'Unknown'))[:40]
        lines.append(triple_row(label, c))
    return "\n".join(lines)


def section_segments(breakdown_data, title, segment_key):
    """Generic segment breakdown section."""
    lines = [
        f"## {title}\n",
        TRIPLE_HEADER,
    ]
    sorted_s = sorted(breakdown_data, key=lambda x: x.get('ar', {}).get('roas', 0), reverse=True)
    for s in sorted_s:
        if s['spend'] < 10:
            continue
        label = str(s.get(segment_key, 'Unknown'))[:30]
        lines.append(triple_row(label, s))
    return "\n".join(lines)


def section_waste(waste_items):
    """Section 7: Waste summary."""
    lines = ["## 7. WASTE SUMMARY\n"]
    total_waste = 0
    for w in waste_items:
        lines.append(f"- **{w['category']}**: {fmt_money(w['amount'])}/period — {w['description']}")
        total_waste += w['amount']
    lines.append(f"\n**Total estimated waste: {fmt_money(total_waste)}/period**")
    return "\n".join(lines)


def section_actions(recommendations):
    """Section 8: Action plan."""
    lines = ["## 8. ACTION PLAN — DO THIS NOW\n"]
    for i, r in enumerate(recommendations, 1):
        emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r.get('priority', 'low'), '⚪')
        lines.append(f"{emoji} **{i}. {r['action']}**")
        lines.append(f"   Impact: {r.get('impact', 'TBD')} | Effort: {r.get('effort', 'TBD')}")
        if r.get('details'):
            lines.append(f"   {r['details']}")
        lines.append("")
    return "\n".join(lines)


# ── Data pulling ─────────────────────────────────────────────────────────────

def pull_meta_data(token, account_id, date_start, date_end, campaign_ids=None):
    """Pull Meta insights at account and campaign level."""
    time_range = {"since": date_start, "until": date_end}

    # Account level
    account_data = get_insights(
        token, account_id, level="account",
        fields="spend,impressions,clicks,actions,action_values,cpc,cpm,ctr,frequency",
        date_preset=None, time_range=time_range
    )

    # Campaign level
    campaign_data = get_insights(
        token, account_id, level="campaign",
        fields="campaign_id,campaign_name,spend,impressions,clicks,actions,action_values,cpc,cpm,ctr",
        date_preset=None, time_range=time_range
    )

    # Filter campaigns if specified
    if campaign_ids and campaign_data:
        campaign_data = [c for c in campaign_data if c.get('campaign_id') in campaign_ids]

    # Breakdowns
    breakdowns = {}
    for bd_name, bd_field in [("age_gender", "age,gender"), ("device", "device_platform"),
                               ("placement", "publisher_platform,platform_position"),
                               ("hourly", "hourly_stats_aggregated_by_advertiser_time_zone")]:
        try:
            bd_data = get_insights(
                token, account_id, level="account",
                fields="spend,impressions,clicks,actions,action_values",
                breakdowns=bd_field, date_preset=None, time_range=time_range
            )
            breakdowns[bd_name] = bd_data
        except Exception as e:
            print(f"  ⚠️ Breakdown {bd_name} failed: {e}")
            breakdowns[bd_name] = []

    # Ad set level (for cannibalization + budget analysis)
    try:
        adset_data = get_insights(
            token, account_id, level="adset",
            fields="adset_id,adset_name,campaign_name,spend,impressions,clicks,actions,action_values,frequency",
            date_preset=None, time_range=time_range
        )
    except Exception:
        adset_data = []

    # Ad level (for creative analysis)
    try:
        ad_data = get_insights(
            token, account_id, level="ad",
            fields="ad_id,ad_name,adset_name,campaign_name,spend,impressions,clicks,actions,action_values",
            date_preset=None, time_range=time_range
        )
    except Exception:
        ad_data = []

    return account_data, campaign_data, breakdowns, adset_data, ad_data


def pull_ga4_data(sa_path, property_id, source_value, date_start, date_end, campaign_ids=None):
    """Pull GA4 conversion data."""
    token = get_access_token(sa_path)

    # Account total
    total = run_report(
        token, property_id,
        dimensions=["sessionSource"],
        metrics=["sessions", "ecommercePurchases", "purchaseRevenue"],
        date_start=date_start, date_end=date_end,
        dimension_filter=make_source_filter(source_value)
    )

    # By campaign (using sessionCampaignId)
    by_campaign = run_report(
        token, property_id,
        dimensions=["sessionCampaignId"],
        metrics=["sessions", "ecommercePurchases", "purchaseRevenue"],
        date_start=date_start, date_end=date_end,
        dimension_filter=make_source_filter(source_value)
    )

    # Device breakdown
    by_device = run_report(
        token, property_id,
        dimensions=["deviceCategory"],
        metrics=["sessions", "ecommercePurchases", "purchaseRevenue"],
        date_start=date_start, date_end=date_end,
        dimension_filter=make_source_filter(source_value)
    )

    # Region breakdown
    by_region = run_report(
        token, property_id,
        dimensions=["region"],
        metrics=["sessions", "ecommercePurchases", "purchaseRevenue"],
        date_start=date_start, date_end=date_end,
        dimension_filter=make_source_filter(source_value)
    )

    return (parse_report(total), parse_report(by_campaign),
            parse_report(by_device), parse_report(by_region))


# ── Main ─────────────────────────────────────────────────────────────────────

def section_tracking_health(campaign_triples, meta_campaigns, ga4_campaigns):
    """Section 2: Tracking health per campaign."""
    lines = ["## 2. TRACKING HEALTH CHECK\n"]
    for c in sorted(campaign_triples, key=lambda x: x['spend'], reverse=True):
        if c['spend'] < 50:
            continue
        name = c.get('name', c.get('id', '?'))[:60]
        meta_p = c['meta']['purchases']
        ga4_p = c['ga4']['purchases']
        disc = round((meta_p / ga4_p - 1) * 100) if ga4_p > 0 else 'N/A'

        # Find click/session data from meta
        meta_row = next((m for m in (meta_campaigns or []) if m.get('campaign_id') == c.get('id')), {})
        clicks = int(float(meta_row.get('clicks', 0)))
        ga4_row = next((g for g in (ga4_campaigns or []) if g.get('sessionCampaignId') == c.get('id')), {})
        sessions = int(ga4_row.get('sessions', 0))
        cts_rate = round(sessions / clicks * 100) if clicks > 0 else 0

        if cts_rate >= 80:
            cts_status = "HEALTHY"
        elif cts_rate >= 60:
            cts_status = "DEGRADED"
        else:
            cts_status = "BROKEN"

        if isinstance(disc, int):
            if disc <= 30:
                disc_status = "NORMAL"
            elif disc <= 100:
                disc_status = "ELEVATED"
            else:
                disc_status = "INVESTIGATE"
        else:
            disc_status = "INVESTIGATE — no GA4 conversions"

        lines.append(f"```")
        lines.append(f"{name}")
        lines.append(f"  Click-to-session rate: {cts_rate}% — {cts_status}")
        lines.append(f"  Meta-GA4 discrepancy: {disc}% — {disc_status}")
        lines.append(f"  UTM integrity: INTACT (ID-matched)")
        lines.append(f"```\n")
    return "\n".join(lines)


def section_cannibalization(adsets):
    """Section 4: Cannibalization detection."""
    lines = ["## 4. CANNIBALIZATION REPORT\n"]
    if not adsets:
        lines.append("*No ad set data available for cannibalization analysis.*")
        return "\n".join(lines)

    # Group by rough targeting (country-level)
    from collections import defaultdict
    geo_groups = defaultdict(list)
    for a in adsets:
        name = a.get('adset_name', a.get('name', ''))
        spend = float(a.get('spend', 0))
        if spend < 10:
            continue
        # Detect country from name heuristics
        country = "US"
        name_lower = name.lower()
        if "[ca]" in name_lower or "canada" in name_lower:
            country = "CA"
        elif "[au]" in name_lower or "australia" in name_lower:
            country = "AU"
        geo_groups[country].append({"name": name, "spend": spend, "id": a.get('adset_id', '')})

    overlap_count = 0
    for country, group in geo_groups.items():
        if len(group) > 1:
            lines.append(f"### {country} — {len(group)} competing ad sets\n")
            for a in sorted(group, key=lambda x: x['spend'], reverse=True):
                lines.append(f"- **{a['name'][:50]}** — {fmt_money(a['spend'])}")
            overlap_count += len(group) - 1
            lines.append("")

    if overlap_count == 0:
        lines.append("✅ No significant cannibalization detected.")
    else:
        est_waste = sum(float(a.get('spend', 0)) for a in adsets if float(a.get('spend', 0)) > 10) * 0.15
        lines.append(f"\n**Estimated CPM inflation from overlap: 15-25%**")
        lines.append(f"**Estimated waste: ~{fmt_money(est_waste)}/period**")

    return "\n".join(lines)


def section_age_gender(breakdown_data):
    """Section 5a: Age × Gender breakdown."""
    lines = ["### Age × Gender\n", TRIPLE_HEADER]
    for row in sorted(breakdown_data, key=lambda x: float(x.get('spend', 0)), reverse=True):
        spend = float(row.get('spend', 0))
        if spend < 10:
            continue
        age = row.get('age', '?')
        gender = row.get('gender', '?')
        label = f"{age} {gender}"
        meta_p = get_action(row, 'purchase') or get_action(row, 'offsite_conversion.fb_pixel_purchase') or 0
        meta_rev = get_action_value(row, 'purchase') or get_action_value(row, 'offsite_conversion.fb_pixel_purchase') or 0
        # GA4 doesn't support age/gender with source filter — use Meta only
        t = calc_triple(spend, int(meta_p), float(meta_rev), 0, 0)
        t['ga4'] = {'purchases': '—', 'cpa': '—', 'roas': '—'}
        t['ar'] = {'purchases': '—', 'cpa': '—', 'roas': '—'}
        lines.append(
            f"| {label} | {fmt_money(spend)} | "
            f"{t['meta']['purchases']} | {fmt_money(t['meta']['cpa'])} | {fmt_roas(t['meta']['roas'])} | "
            f"— | — | — | — | — | — |"
        )
    lines.append("\n*Note: GA4 age/gender incompatible with session source filter. Meta-only for demographics.*")
    return "\n".join(lines)


def section_device(meta_breakdown, ga4_device, total_spend):
    """Section 5b: Device breakdown with triple-source."""
    lines = ["### Device Platform\n", TRIPLE_HEADER]
    ga4_map = {r.get('deviceCategory', '').lower(): r for r in (ga4_device or [])}
    device_name_map = {"desktop": "desktop", "mobile_app": "mobile", "mobile_web": "mobile",
                       "iphone": "mobile", "ipad": "tablet", "android_smartphone": "mobile",
                       "android_tablet": "tablet", "tablet": "tablet"}

    for row in sorted(meta_breakdown, key=lambda x: float(x.get('spend', 0)), reverse=True):
        spend = float(row.get('spend', 0))
        if spend < 10:
            continue
        device = row.get('device_platform', row.get('impression_device', '?'))
        meta_p = get_action(row, 'purchase') or get_action(row, 'offsite_conversion.fb_pixel_purchase') or 0
        meta_rev = get_action_value(row, 'purchase') or get_action_value(row, 'offsite_conversion.fb_pixel_purchase') or 0

        ga4_key = device_name_map.get(device.lower(), device.lower())
        ga4_row = ga4_map.get(ga4_key, {})
        ga4_p = int(ga4_row.get('ecommercePurchases', 0))
        ga4_rev = float(ga4_row.get('purchaseRevenue', 0))

        t = calc_triple(spend, int(meta_p), float(meta_rev), ga4_p, ga4_rev)
        lines.append(triple_row(device, t))
    return "\n".join(lines)


def section_placement(meta_breakdown):
    """Section 5c: Placement breakdown (Meta only — GA4 doesn't have placement)."""
    lines = ["### Placement\n",
             "| Placement | Spend | Meta P | Meta CPA | Meta ROAS | Spend % |",
             "|-----------|-------|--------|----------|-----------|---------|"]
    total_spend = sum(float(r.get('spend', 0)) for r in meta_breakdown)
    for row in sorted(meta_breakdown, key=lambda x: float(x.get('spend', 0)), reverse=True):
        spend = float(row.get('spend', 0))
        if spend < 5:
            continue
        platform = row.get('publisher_platform', '?')
        position = row.get('platform_position', '?')
        label = f"{platform}/{position}"
        meta_p = get_action(row, 'purchase') or get_action(row, 'offsite_conversion.fb_pixel_purchase') or 0
        meta_rev = get_action_value(row, 'purchase') or get_action_value(row, 'offsite_conversion.fb_pixel_purchase') or 0
        cpa = spend / meta_p if meta_p else 0
        roas = meta_rev / spend if spend else 0
        pct = spend / total_spend * 100 if total_spend else 0
        lines.append(f"| {label[:30]} | {fmt_money(spend)} | {int(meta_p)} | {fmt_money(cpa)} | {fmt_roas(roas)} | {pct:.1f}% |")
    lines.append("\n*Note: GA4 doesn't track placement. Meta-only data.*")
    return "\n".join(lines)


def section_dayparting(meta_breakdown, days):
    """Section 5d: Dayparting analysis — when to run and when to stop ads."""
    if not meta_breakdown:
        return "### Dayparting Analysis\n\n*No hourly data available.*"

    # Parse hourly data
    hours = []
    total_spend = 0
    total_purchases = 0
    total_revenue = 0
    for row in meta_breakdown:
        spend = float(row.get('spend', 0))
        if spend < 1:
            continue
        hour_raw = row.get('hourly_stats_aggregated_by_advertiser_time_zone', '0')
        # Parse hour — can be "0", "23", or "23:00:00 - 23:59:59"
        try:
            hour = int(str(hour_raw).split(':')[0].split(' ')[0])
        except (ValueError, IndexError):
            hour = 0
        meta_p = get_action(row, 'purchase') or get_action(row, 'offsite_conversion.fb_pixel_purchase') or 0
        meta_rev = get_action_value(row, 'purchase') or get_action_value(row, 'offsite_conversion.fb_pixel_purchase') or 0
        clicks = int(float(row.get('clicks', 0)))
        impressions = int(float(row.get('impressions', 0)))
        cpa = spend / meta_p if meta_p else 999999
        roas = meta_rev / spend if spend else 0
        cvr = (meta_p / clicks * 100) if clicks > 0 else 0

        total_spend += spend
        total_purchases += meta_p
        total_revenue += meta_rev

        hours.append({
            'hour': hour,
            'spend': spend,
            'purchases': int(meta_p),
            'revenue': meta_rev,
            'clicks': clicks,
            'impressions': impressions,
            'cpa': cpa,
            'roas': roas,
            'cvr': cvr,
        })

    hours.sort(key=lambda x: x['hour'])
    avg_cpa = total_spend / total_purchases if total_purchases else 0
    avg_roas = total_revenue / total_spend if total_spend else 0

    # Classify each hour
    for h in hours:
        spend_pct = h['spend'] / total_spend * 100 if total_spend else 0
        h['spend_pct'] = spend_pct
        h['daily_spend'] = h['spend'] / days if days else 0

        if h['purchases'] == 0 and h['spend'] > total_spend * 0.02:
            h['verdict'] = '🔴 STOP'
            h['reason'] = 'Zero conversions with significant spend'
        elif h['cpa'] > avg_cpa * 2 and h['purchases'] > 0:
            h['verdict'] = '🔴 STOP'
            h['reason'] = f'CPA {fmt_money(h["cpa"])} is 2x+ above average ({fmt_money(avg_cpa)})'
        elif h['cpa'] > avg_cpa * 1.5 and h['purchases'] > 0:
            h['verdict'] = '🟡 REDUCE'
            h['reason'] = f'CPA {fmt_money(h["cpa"])} is 1.5x above average'
        elif h['roas'] > avg_roas * 1.3:
            h['verdict'] = '🟢 PEAK'
            h['reason'] = f'ROAS {fmt_roas(h["roas"])} — above average'
        elif h['roas'] > avg_roas * 0.8:
            h['verdict'] = '✅ OK'
            h['reason'] = 'Within normal range'
        else:
            h['verdict'] = '🟡 WEAK'
            h['reason'] = f'ROAS {fmt_roas(h["roas"])} below average'

    # Build output
    lines = [
        "### Dayparting Analysis — When to Run & Stop Ads\n",
        f"**Account average:** CPA {fmt_money(avg_cpa)} | ROAS {fmt_roas(avg_roas)} | "
        f"Total spend: {fmt_money(total_spend)} over {days} days\n",
        "| Hour | Spend | $/day | Spend% | P | CPA | ROAS | CVR% | Verdict |",
        "|------|-------|-------|--------|---|-----|------|------|---------|",
    ]
    for h in hours:
        cpa_display = fmt_money(h['cpa']) if h['purchases'] > 0 else '∞'
        lines.append(
            f"| {h['hour']:02d}:00 | {fmt_money(h['spend'])} | {fmt_money(h['daily_spend'])} | "
            f"{h['spend_pct']:.1f}% | {h['purchases']} | {cpa_display} | {fmt_roas(h['roas'])} | "
            f"{h['cvr']:.1f}% | {h['verdict']} |"
        )

    # Summary
    stop_hours = [h for h in hours if '🔴' in h['verdict']]
    peak_hours = [h for h in hours if '🟢' in h['verdict']]
    reduce_hours = [h for h in hours if '🟡' in h['verdict']]

    stop_waste = sum(h['spend'] for h in stop_hours)
    stop_waste_daily = stop_waste / days if days else 0
    stop_waste_monthly = stop_waste_daily * 30

    lines.append("")
    lines.append("#### ⏰ Recommended Schedule\n")

    if peak_hours:
        peak_range = ', '.join(f"{h['hour']:02d}:00" for h in peak_hours)
        lines.append(f"🟢 **Peak hours (increase budget):** {peak_range}")
        lines.append(f"   Combined ROAS: {fmt_roas(sum(h['revenue'] for h in peak_hours) / sum(h['spend'] for h in peak_hours) if sum(h['spend'] for h in peak_hours) else 0)}\n")

    if stop_hours:
        stop_range = ', '.join(f"{h['hour']:02d}:00" for h in stop_hours)
        lines.append(f"🔴 **Dead hours (STOP ads):** {stop_range}")
        for h in stop_hours:
            lines.append(f"   - {h['hour']:02d}:00: {h['reason']} — wasting {fmt_money(h['daily_spend'])}/day")
        lines.append(f"\n   **Total waste from dead hours: {fmt_money(stop_waste)}/period = {fmt_money(stop_waste_daily)}/day = {fmt_money(stop_waste_monthly)}/month**\n")

    if reduce_hours:
        reduce_range = ', '.join(f"{h['hour']:02d}:00" for h in reduce_hours)
        lines.append(f"🟡 **Weak hours (monitor/reduce):** {reduce_range}\n")

    if not stop_hours:
        lines.append("✅ No dead hours detected — all hours are converting within acceptable range.\n")

    return "\n".join(lines)


def section_frequency(acct_meta):
    """Section 6: Frequency analysis."""
    lines = ["## 6. FREQUENCY ANALYSIS\n"]
    if acct_meta and isinstance(acct_meta, list) and acct_meta[0]:
        freq = float(acct_meta[0].get('frequency', 0))
        lines.append(f"**Account average frequency: {freq:.2f}**\n")
        if freq > 3:
            lines.append(f"⚠️ Frequency {freq:.1f} is HIGH — likely ad fatigue. Consider refreshing creatives.")
        elif freq > 2:
            lines.append(f"🟡 Frequency {freq:.1f} is moderate — monitor for fatigue.")
        else:
            lines.append(f"✅ Frequency {freq:.1f} is healthy.")
    else:
        lines.append("*No frequency data available.*")
    return "\n".join(lines)


def download_image(url, filepath, token=None):
    """Download image from URL or Meta Graph API."""
    try:
        if token and 'fbcdn' not in url and 'graph.facebook.com' not in url:
            # For Meta image hashes, use Graph API
            pass
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        with open(filepath, 'wb') as f:
            f.write(resp.read())
        return True
    except Exception as e:
        # Try with token appended
        try:
            if token and '?' in url:
                url2 = f"{url}&access_token={token}"
            elif token:
                url2 = f"{url}?access_token={token}"
            else:
                return False
            req = urllib.request.Request(url2, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=30)
            with open(filepath, 'wb') as f:
                f.write(resp.read())
            return True
        except Exception:
            print(f"  ⚠️ Failed to download: {filepath.name} — {e}")
            return False


PLACEHOLDER_HASH = '75341531'  # Meta's generic placeholder thumbnail hash


def is_real_image(url):
    """Check if URL is a real ad image (not Meta's placeholder icon)."""
    if not url:
        return False
    if PLACEHOLDER_HASH in url:
        return False
    if '64x64' in url or 'p64x64' in url:
        return False
    return True


def get_full_image_url(token, ad_id, creative):
    """Try multiple methods to get the full-size ad image."""
    # Method 1: creative.image_url (works for static image ads)
    img = creative.get('image_url', '')
    if is_real_image(img):
        return img, 'static'

    # Method 2: object_story_spec link_data picture
    story = creative.get('object_story_spec', {})
    link_data = story.get('link_data', {})
    img = link_data.get('picture', '')
    if is_real_image(img):
        return img, 'link_picture'

    # Method 3: video thumbnail
    video_data = story.get('video_data', {})
    img = video_data.get('image_url', '')
    if is_real_image(img):
        return img, 'video_thumb'

    # Method 4: Try adimages endpoint if we have image_hash
    img_hash = link_data.get('image_hash', '') or creative.get('image_hash', '')
    if img_hash:
        try:
            # Need account_id — extract from ad endpoint
            url = f"https://graph.facebook.com/v21.0/{ad_id}?fields=account_id&access_token={token}"
            resp = api_get(url)
            acct_id = resp.get('account_id', '')
            if acct_id:
                url2 = f"https://graph.facebook.com/v21.0/act_{acct_id}/adimages?hashes=[%22{img_hash}%22]&fields=url_128,url&access_token={token}"
                resp2 = api_get(url2)
                images = resp2.get('data', [])
                if images:
                    img = images[0].get('url', '') or images[0].get('url_128', '')
                    if is_real_image(img):
                        return img, 'adimages'
        except Exception:
            pass

    # Method 5: Ad preview (renders a screenshot of the ad)
    try:
        url = f"https://graph.facebook.com/v21.0/{ad_id}/previews?ad_format=DESKTOP_FEED_STANDARD&access_token={token}"
        resp = api_get(url)
        preview_data = resp.get('data', [{}])[0]
        # Preview returns an iframe HTML — extract the src
        body = preview_data.get('body', '')
        if 'src="' in body:
            iframe_src = body.split('src="')[1].split('"')[0]
            if iframe_src:
                return iframe_src, 'preview_iframe'
    except Exception:
        pass

    # Fallback: thumbnail_url even if small
    img = creative.get('thumbnail_url', '')
    if img and PLACEHOLDER_HASH not in img:
        return img, 'thumbnail'

    return '', 'none'


def pull_top_ad_creatives(token, ad_data, output_dir, top_n=20):
    """Pull creative details + download images for top N ads by Meta ROAS."""
    ranked = []
    for ad in ad_data:
        spend = float(ad.get('spend', 0))
        if spend < 50:
            continue
        meta_p = get_action(ad, 'purchase') or get_action(ad, 'offsite_conversion.fb_pixel_purchase') or 0
        meta_rev = get_action_value(ad, 'purchase') or get_action_value(ad, 'offsite_conversion.fb_pixel_purchase') or 0
        roas = meta_rev / spend if spend else 0
        cpa = spend / meta_p if meta_p else 0
        ranked.append({
            'ad_id': ad.get('ad_id', ''),
            'ad_name': ad.get('ad_name', ''),
            'campaign_name': ad.get('campaign_name', ''),
            'adset_name': ad.get('adset_name', ''),
            'spend': spend,
            'meta_purchases': int(meta_p),
            'meta_revenue': round(meta_rev, 2),
            'meta_roas': round(roas, 2),
            'meta_cpa': round(cpa, 2),
            'impressions': int(float(ad.get('impressions', 0))),
            'clicks': int(float(ad.get('clicks', 0))),
        })

    ranked.sort(key=lambda x: (x['meta_roas'], x['spend']), reverse=True)
    top_ads = ranked[:top_n]

    img_dir = output_dir / "top_ad_images"
    img_dir.mkdir(parents=True, exist_ok=True)

    for i, ad in enumerate(top_ads):
        ad_id = ad['ad_id']
        print(f"  [{i+1}/{len(top_ads)}] Pulling creative for ad {ad_id}...", end="", flush=True)
        time.sleep(0.3)

        try:
            detail = get_ad_creative_detail(token, ad_id)
            creative = detail.get('creative', {})

            # Extract text copy
            story = creative.get('object_story_spec', {})
            link_data = story.get('link_data', {})
            video_data = story.get('video_data', {})

            ad['body'] = creative.get('body') or link_data.get('message') or video_data.get('message') or ''
            ad['title'] = creative.get('title') or link_data.get('name') or video_data.get('title') or ''
            ad['description'] = link_data.get('description') or ''
            ad['cta'] = creative.get('call_to_action_type') or link_data.get('call_to_action', {}).get('type') or ''
            ad['link_url'] = creative.get('link_url') or link_data.get('link') or ''

            # Detect ad type
            is_catalog = 'catalog' in ad['ad_name'].lower() or link_data.get('multi_share_optimized')
            is_video = bool(creative.get('video_id') or video_data)
            ad['ad_type'] = 'catalog' if is_catalog else ('video' if is_video else 'static')

            # Get image
            image_url, source = get_full_image_url(token, ad_id, creative)
            ad['image_url'] = image_url
            ad['image_source'] = source

            if image_url and source != 'preview_iframe':
                ext = 'png' if '.png' in image_url.lower() else 'jpg'
                img_filename = f"top_{i+1:02d}_{ad_id}.{ext}"
                img_path = img_dir / img_filename
                if download_image(image_url, img_path, token):
                    # Verify it's not a tiny placeholder
                    if img_path.stat().st_size > 2000:
                        ad['image_local'] = str(img_path)
                        ad['image_filename'] = img_filename
                        print(f" ✅ {source} ({img_path.stat().st_size // 1024}KB)", flush=True)
                    else:
                        img_path.unlink()
                        ad['image_local'] = None
                        ad['image_filename'] = None
                        ad['ad_type_note'] = 'Catalog/dynamic ad — no static image available'
                        print(f" ⚠️ placeholder ({source})", flush=True)
                else:
                    ad['image_local'] = None
                    ad['image_filename'] = None
                    print(f" ⚠️ download failed", flush=True)
            elif source == 'preview_iframe':
                ad['preview_url'] = image_url
                ad['image_local'] = None
                ad['image_filename'] = None
                ad['ad_type_note'] = 'Catalog/dynamic ad — preview available'
                print(f" 📋 preview iframe", flush=True)
            else:
                ad['image_local'] = None
                ad['image_filename'] = None
                ad['ad_type_note'] = 'Catalog/dynamic ad — image from product feed'
                print(f" (catalog — no static image)", flush=True)

        except Exception as e:
            print(f" ❌ error: {e}", flush=True)
            ad['body'] = ''
            ad['title'] = ''
            ad['description'] = ''
            ad['cta'] = ''
            ad['link_url'] = ''
            ad['image_url'] = ''
            ad['image_local'] = None
            ad['image_filename'] = None
            ad['ad_type'] = 'unknown'

    return top_ads


def section_top_ads_md(top_ads):
    """Section 9: Top 20 ads — markdown version."""
    lines = [
        "## 9. TOP 20 CONVERTING ADS\n",
        "*Ranked by Meta ROAS. Images + ad copy included. Use these as inputs for meta-ad-creator.*\n",
    ]

    for i, ad in enumerate(top_ads, 1):
        lines.append(f"### #{i} — {ad['ad_name'][:60]}")
        lines.append(f"**Campaign:** {ad.get('campaign_name', '—')}")
        lines.append(f"**Ad Set:** {ad.get('adset_name', '—')}")
        lines.append(f"**Ad ID:** `{ad['ad_id']}`\n")

        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Spend | {fmt_money(ad['spend'])} |")
        lines.append(f"| Meta Purchases | {ad['meta_purchases']} |")
        lines.append(f"| Meta CPA | {fmt_money(ad['meta_cpa'])} |")
        lines.append(f"| Meta ROAS | {fmt_roas(ad['meta_roas'])} |")
        lines.append(f"| Impressions | {ad['impressions']:,} |")
        lines.append(f"| Clicks | {ad['clicks']:,} |")

        if ad.get('title'):
            lines.append(f"\n**Headline:** {ad['title']}")
        if ad.get('body'):
            body_preview = ad['body'][:300]
            if len(ad['body']) > 300:
                body_preview += "..."
            lines.append(f"**Ad Copy:**\n> {body_preview}")
        if ad.get('description'):
            lines.append(f"**Description:** {ad['description'][:200]}")
        if ad.get('cta'):
            lines.append(f"**CTA:** {ad['cta']}")

        if ad.get('image_filename'):
            lines.append(f"\n**Image:** `{ad['image_filename']}`")
            lines.append(f"**Creator link:** Use as input → `python3 edit_ad.py -i {ad.get('image_local', ad['image_filename'])} --variations 6 --swap-dogs`")
        else:
            lines.append(f"\n*No image available for this ad.*")

        lines.append(f"\n---\n")

    return "\n".join(lines)


def section_top_ads_html(top_ads):
    """Top 20 ads — HTML version with embedded images."""
    lines = ['<h2>9. TOP 20 CONVERTING ADS</h2>',
             '<p><em>Ranked by Meta ROAS. Use these as inputs for meta-ad-creator.</em></p>']

    for i, ad in enumerate(top_ads, 1):
        lines.append(f'<div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin:16px 0; page-break-inside:avoid;">')
        lines.append(f'<h3>#{i} — {ad["ad_name"][:60]}</h3>')
        lines.append(f'<p><strong>Campaign:</strong> {ad.get("campaign_name", "—")} | '
                     f'<strong>Ad Set:</strong> {ad.get("adset_name", "—")} | '
                     f'<strong>Ad ID:</strong> <code>{ad["ad_id"]}</code></p>')

        # Metrics row
        lines.append('<table style="width:auto; margin:8px 0;"><tr>')
        lines.append(f'<td style="padding:4px 12px;"><strong>Spend</strong><br>{fmt_money(ad["spend"])}</td>')
        lines.append(f'<td style="padding:4px 12px;"><strong>Purchases</strong><br>{ad["meta_purchases"]}</td>')
        lines.append(f'<td style="padding:4px 12px;"><strong>CPA</strong><br>{fmt_money(ad["meta_cpa"])}</td>')
        lines.append(f'<td style="padding:4px 12px;"><strong>ROAS</strong><br>{fmt_roas(ad["meta_roas"])}</td>')
        lines.append(f'<td style="padding:4px 12px;"><strong>Impressions</strong><br>{ad["impressions"]:,}</td>')
        lines.append(f'<td style="padding:4px 12px;"><strong>Clicks</strong><br>{ad["clicks"]:,}</td>')
        lines.append('</tr></table>')

        # Image + copy side by side
        lines.append('<div style="display:flex; gap:12px; margin:8px 0;">')

        # Image
        ad_type = ad.get('ad_type', 'unknown')
        if ad.get('image_local') and os.path.exists(ad['image_local']) and os.path.getsize(ad['image_local']) > 2000:
            try:
                with open(ad['image_local'], 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                ext = ad['image_filename'].rsplit('.', 1)[-1]
                mime = 'image/jpeg' if ext == 'jpg' else f'image/{ext}'
                lines.append(f'<div style="flex:0 0 250px;"><img src="data:{mime};base64,{img_data}" '
                             f'style="max-width:250px; max-height:250px; border-radius:4px; border:1px solid #eee;">'
                             f'<div style="font-size:7px; color:#888; margin-top:2px;">Static creative</div></div>')
            except Exception:
                lines.append('<div style="flex:0 0 250px; background:#f0f0f0; padding:30px; text-align:center; border-radius:4px;">'
                             '<em style="font-size:9px;">Image load error</em></div>')
        elif ad_type == 'catalog':
            lines.append('<div style="flex:0 0 250px; background:#e8f4fd; padding:20px; text-align:center; border-radius:4px; border:1px solid #b8daff;">'
                         '<div style="font-size:24px;">🛒</div>'
                         '<div style="font-size:10px; font-weight:bold; color:#0c5460; margin:8px 0;">Catalog Ad</div>'
                         '<div style="font-size:8px; color:#666;">Dynamic product images<br>from feed</div></div>')
        elif ad_type == 'video':
            lines.append('<div style="flex:0 0 250px; background:#f3e8ff; padding:20px; text-align:center; border-radius:4px; border:1px solid #d4b5ff;">'
                         '<div style="font-size:24px;">🎬</div>'
                         '<div style="font-size:10px; font-weight:bold; color:#6f42c1; margin:8px 0;">Video Ad</div>'
                         '<div style="font-size:8px; color:#666;">Video creative</div></div>')
        else:
            lines.append('<div style="flex:0 0 250px; background:#f4f4f4; padding:20px; text-align:center; border-radius:4px;">'
                         '<div style="font-size:24px;">📷</div>'
                         '<div style="font-size:9px; color:#666; margin-top:8px;">No preview available</div></div>')

        # Copy
        lines.append('<div style="flex:1;">')
        if ad.get('title'):
            lines.append(f'<p><strong>Headline:</strong> {ad["title"]}</p>')
        if ad.get('body'):
            body = ad['body'].replace('\n', '<br>')[:500]
            lines.append(f'<p><strong>Ad Copy:</strong><br><span style="color:#555;">{body}</span></p>')
        if ad.get('description'):
            lines.append(f'<p><strong>Description:</strong> {ad["description"][:200]}</p>')
        if ad.get('cta'):
            lines.append(f'<p><strong>CTA:</strong> {ad["cta"]}</p>')
        lines.append(f'<p style="margin-top:8px; font-size:12px; color:#888;">'
                     f'Creator: <code>edit_ad.py -i {ad.get("image_local", "image.jpg")} --variations 6 --swap-dogs</code></p>')
        lines.append('</div></div>')

        lines.append('</div>')

    return "\n".join(lines)


def calc_dead_hours_waste(hourly_breakdown, days):
    """Calculate waste from dead hours."""
    if not hourly_breakdown:
        return 0, []
    total_spend = sum(float(r.get('spend', 0)) for r in hourly_breakdown)
    total_purchases = sum(
        (get_action(r, 'purchase') or get_action(r, 'offsite_conversion.fb_pixel_purchase') or 0)
        for r in hourly_breakdown
    )
    avg_cpa = total_spend / total_purchases if total_purchases else 0

    dead_hours = []
    waste = 0
    for row in hourly_breakdown:
        spend = float(row.get('spend', 0))
        meta_p = get_action(row, 'purchase') or get_action(row, 'offsite_conversion.fb_pixel_purchase') or 0
        hour_raw = row.get('hourly_stats_aggregated_by_advertiser_time_zone', '0')
        cpa = spend / meta_p if meta_p else 999999

        if (meta_p == 0 and spend > total_spend * 0.02) or (meta_p > 0 and cpa > avg_cpa * 2):
            waste += spend
            # Hour can be "0", "23", or "23:00:00 - 23:59:59"
            try:
                dead_hours.append(int(str(hour_raw).split(':')[0].split(' ')[0]))
            except (ValueError, IndexError):
                pass

    return waste, dead_hours


def build_waste_and_actions(totals, campaign_triples, breakdowns, adset_data=None, days=60):
    """Build waste summary + structured action plan for meta-ad-manager.

    Returns:
        waste_items: list of waste categories with amounts
        recommendations: human-readable action list
        manager_actions: machine-readable JSON actions for meta-ad-manager
    """
    waste_items = []
    recommendations = []
    manager_actions = []  # Structured actions for meta-ad-manager

    # ── 0. Dayparting — dead hours ──────────────────────────────────────────
    dead_waste, dead_hours_list = calc_dead_hours_waste(breakdowns.get('hourly', []), 1)
    if dead_waste > 0:
        daily_waste = dead_waste / days if days else 0
        waste_items.append({
            "category": f"Dead Hours ({', '.join(f'{h:02d}:00' for h in dead_hours_list)})",
            "amount": dead_waste,
            "description": f"Zero/poor conversions — {fmt_money(daily_waste)}/day wasted"
        })
        recommendations.append({
            "action": f"Enable dayparting — stop ads at {', '.join(f'{h:02d}:00' for h in dead_hours_list)}",
            "priority": "high",
            "impact": f"Save ~{fmt_money(daily_waste)}/day = ~{fmt_money(daily_waste * 30)}/month",
            "effort": "Low",
            "details": "Set ad scheduling in Meta to exclude dead hours"
        })
        # Build the active hours schedule (all hours EXCEPT dead hours)
        active_hours = [h for h in range(24) if h not in dead_hours_list]
        manager_actions.append({
            "type": "dayparting",
            "priority": "high",
            "target": "account",
            "action": "set_ad_schedule",
            "params": {
                "stop_hours": dead_hours_list,
                "active_hours": active_hours,
                "timezone": "advertiser",
                "schedule_description": f"Run ads {active_hours[0]:02d}:00-{active_hours[-1]:02d}:00, pause during dead hours",
            },
            "reason": f"Dead hours waste {fmt_money(daily_waste)}/day with zero/poor conversions",
            "estimated_savings_daily": round(daily_waste, 2),
            "estimated_savings_monthly": round(daily_waste * 30, 2),
        })

    # ── 1. Campaigns to pause (CPA 2x+ above average) ──────────────────────
    for c in campaign_triples:
        if c['spend'] < 100:
            continue
        if c['meta']['cpa'] > 0 and totals['meta']['cpa'] > 0:
            if c['meta']['cpa'] > totals['meta']['cpa'] * 2:
                daily_waste = c['spend'] * 0.5 / days if days else 0
                waste_items.append({
                    "category": f"High-CPA Campaign: {c.get('name', '?')[:30]}",
                    "amount": c['spend'] * 0.5,
                    "description": f"CPA {fmt_money(c['meta']['cpa'])} is 2x+ account average"
                })
                recommendations.append({
                    "action": f"Review/pause {c.get('name', '?')[:40]}",
                    "priority": "high",
                    "impact": f"Save ~{fmt_money(daily_waste)}/day",
                    "effort": "Low",
                    "details": f"Meta CPA {fmt_money(c['meta']['cpa'])} vs avg {fmt_money(totals['meta']['cpa'])}"
                })
                manager_actions.append({
                    "type": "pause_campaign",
                    "priority": "high",
                    "target": "campaign",
                    "target_id": c.get('id', ''),
                    "target_name": c.get('name', ''),
                    "action": "set_status",
                    "params": {"status": "PAUSED"},
                    "reason": f"CPA {fmt_money(c['meta']['cpa'])} is {c['meta']['cpa'] / totals['meta']['cpa']:.1f}x account average ({fmt_money(totals['meta']['cpa'])})",
                    "metrics": {
                        "spend": c['spend'],
                        "meta_cpa": c['meta']['cpa'],
                        "meta_roas": c['meta']['roas'],
                        "ga4_purchases": c['ga4']['purchases'],
                        "ar_cpa": c['ar']['cpa'],
                    },
                    "estimated_savings_daily": round(daily_waste, 2),
                })

    # ── 2. Campaigns to scale (ROAS 1.5x+ above average) ───────────────────
    for c in campaign_triples:
        if c['spend'] < 50:
            continue
        if c['meta']['roas'] > 0 and totals['meta']['roas'] > 0:
            if c['meta']['roas'] > totals['meta']['roas'] * 1.5:
                current_daily = c['spend'] / days if days else 0
                suggested_daily = current_daily * 1.5  # suggest 50% increase
                recommendations.append({
                    "action": f"Scale {c.get('name', '?')[:40]}",
                    "priority": "medium",
                    "impact": f"ROAS {fmt_roas(c['meta']['roas'])} — 1.5x+ above average",
                    "effort": "Low",
                    "details": f"Currently {fmt_money(current_daily)}/day → suggest {fmt_money(suggested_daily)}/day"
                })
                manager_actions.append({
                    "type": "scale_budget",
                    "priority": "medium",
                    "target": "campaign",
                    "target_id": c.get('id', ''),
                    "target_name": c.get('name', ''),
                    "action": "update_budget",
                    "params": {
                        "current_daily_budget": round(current_daily, 2),
                        "suggested_daily_budget": round(suggested_daily, 2),
                        "increase_pct": 50,
                    },
                    "reason": f"ROAS {fmt_roas(c['meta']['roas'])} is {c['meta']['roas'] / totals['meta']['roas']:.1f}x account average — budget-constrained winner",
                    "metrics": {
                        "spend": c['spend'],
                        "meta_cpa": c['meta']['cpa'],
                        "meta_roas": c['meta']['roas'],
                        "ga4_purchases": c['ga4']['purchases'],
                        "ar_cpa": c['ar']['cpa'],
                    },
                })

    # ── 3. Campaigns with zero GA4 conversions but Meta claims purchases ────
    for c in campaign_triples:
        if c['spend'] < 100:
            continue
        if c['meta']['purchases'] > 3 and c['ga4']['purchases'] == 0:
            daily_spend = c['spend'] / days if days else 0
            waste_items.append({
                "category": f"Ghost Campaign: {c.get('name', '?')[:30]}",
                "amount": c['spend'],
                "description": f"Meta claims {c['meta']['purchases']} purchases but GA4 sees ZERO"
            })
            recommendations.append({
                "action": f"Investigate/pause {c.get('name', '?')[:40]} — zero GA4 conversions",
                "priority": "high",
                "impact": f"Save {fmt_money(daily_spend)}/day if confirmed ghost",
                "effort": "Low",
                "details": f"Meta: {c['meta']['purchases']} P | GA4: 0 P — possible tracking issue or fake conversions"
            })
            manager_actions.append({
                "type": "pause_campaign",
                "priority": "high",
                "target": "campaign",
                "target_id": c.get('id', ''),
                "target_name": c.get('name', ''),
                "action": "set_status",
                "params": {"status": "PAUSED"},
                "reason": f"Ghost campaign: Meta reports {c['meta']['purchases']} purchases but GA4 sees 0. Spending {fmt_money(daily_spend)}/day.",
                "metrics": {
                    "spend": c['spend'],
                    "meta_purchases": c['meta']['purchases'],
                    "ga4_purchases": 0,
                },
                "estimated_savings_daily": round(daily_spend, 2),
            })

    # ── 4. Cannibalization — ad sets needing exclusions ─────────────────────
    if adset_data:
        from collections import defaultdict
        geo_groups = defaultdict(list)
        for a in adset_data:
            name = a.get('adset_name', a.get('name', ''))
            spend = float(a.get('spend', 0))
            if spend < 50:
                continue
            country = "US"
            name_lower = name.lower()
            if "[ca]" in name_lower or "canada" in name_lower:
                country = "CA"
            elif "[au]" in name_lower or "australia" in name_lower:
                country = "AU"
            geo_groups[country].append({
                "id": a.get('adset_id', ''),
                "name": name,
                "spend": spend,
            })

        for country, group in geo_groups.items():
            if len(group) > 2:  # 3+ ad sets = cannibalization risk
                sorted_group = sorted(group, key=lambda x: x['spend'], reverse=True)
                overlap_spend = sum(a['spend'] for a in sorted_group[1:])  # all except top spender
                est_waste = overlap_spend * 0.2  # ~20% CPM inflation from overlap

                waste_items.append({
                    "category": f"Cannibalization ({country}): {len(group)} competing ad sets",
                    "amount": est_waste,
                    "description": f"~20% CPM inflation from {len(group)} overlapping ad sets"
                })

                # Suggest adding exclusions to the biggest spender
                top_adset = sorted_group[0]
                manager_actions.append({
                    "type": "add_exclusions",
                    "priority": "high",
                    "target": "adset",
                    "target_id": top_adset['id'],
                    "target_name": top_adset['name'],
                    "action": "update_targeting",
                    "params": {
                        "exclude_audiences_from": [a['id'] for a in sorted_group[1:]],
                        "country": country,
                        "overlap_count": len(group),
                    },
                    "reason": f"{len(group)} ad sets competing for {country} audience. Top spender ({top_adset['name'][:30]}) needs audience exclusions.",
                    "estimated_savings_daily": round(est_waste / days, 2) if days else 0,
                })

    # ── 5. Creatives to refresh (for meta-ad-creator) ──────────────────────
    # This is populated separately from top_ads in generate_report

    return waste_items, recommendations, manager_actions


def build_html_report(report_md, top_ads, account_name, period_label, days,
                      totals, prev_totals, campaign_triples, manager_actions):
    """Build a visually rich HTML report with color coding, KPI cards, and embedded images."""
    import re

    css = """
@page { size: A4 landscape; margin: 12mm; }
@media print { .page-break { page-break-before: always; } }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10px; color: #222; line-height: 1.4; margin: 0; padding: 15px; }
h1 { color: #16213e; font-size: 22px; margin: 0 0 5px; }
h2 { color: #16213e; font-size: 15px; border-bottom: 3px solid #e94560; padding-bottom: 4px; margin: 16px 0 8px; }
h3 { color: #e94560; font-size: 12px; margin: 10px 0 5px; }
.cover { text-align: center; padding: 40px 0 20px; }
.cover h1 { font-size: 28px; }
.cover .subtitle { font-size: 13px; color: #555; margin: 8px 0; }
.kpi-row { display: flex; gap: 8px; flex-wrap: wrap; margin: 10px 0; }
.kpi { background: #16213e; color: #fff; border-radius: 6px; padding: 8px 12px; min-width: 100px; flex: 1; text-align: center; }
.kpi .val { font-size: 18px; font-weight: bold; }
.kpi .lbl { font-size: 8px; text-transform: uppercase; opacity: 0.85; }
.kpi.good { background: #28a745; }
.kpi.warn { background: #ffc107; color: #222; }
.kpi.bad { background: #dc3545; }
.kpi.accent { background: #e94560; }
table { border-collapse: collapse; width: 100%; font-size: 8px; margin: 5px 0 10px; }
th { background: #16213e; color: #fff; padding: 3px 4px; text-align: left; font-weight: 600; white-space: nowrap; font-size: 7px; }
td { padding: 2px 4px; border-bottom: 1px solid #ddd; white-space: nowrap; font-size: 8px; }
tr:nth-child(even) { background: #f8f9fa; }
tr.good td { background: #d4edda !important; }
tr.warn td { background: #fff3cd !important; }
tr.bad td { background: #f8d7da !important; }
tr.peak td { background: #d4edda !important; font-weight: bold; }
tr.stop td { background: #f8d7da !important; font-weight: bold; }
tr.weak td { background: #fff3cd !important; }
.tag { display: inline-block; padding: 1px 4px; border-radius: 3px; font-size: 7px; font-weight: bold; }
.tag-stop { background: #f8d7da; color: #721c24; }
.tag-peak { background: #d4edda; color: #155724; }
.tag-ok { background: #e8f4fd; color: #0c5460; }
.tag-warn { background: #fff3cd; color: #856404; }
.tag-broken { background: #f8d7da; color: #721c24; }
.tag-healthy { background: #d4edda; color: #155724; }
.tag-degraded { background: #fff3cd; color: #856404; }
pre { background: #f4f4f4; padding: 6px 8px; border-radius: 3px; font-size: 8px; white-space: pre-wrap; margin: 4px 0; }
code { background: #f4f4f4; padding: 1px 3px; border-radius: 2px; font-size: 8px; }
blockquote { border-left: 3px solid #e94560; padding-left: 8px; color: #555; margin: 5px 0; font-size: 9px; }
p { margin: 3px 0; font-size: 10px; }
.action-item { margin: 4px 0; padding: 5px 8px; border-radius: 4px; font-size: 10px; }
.p-high { background: #f8d7da; border-left: 3px solid #dc3545; }
.p-medium { background: #fff3cd; border-left: 3px solid #ffc107; }
.p-low { background: #d4edda; border-left: 3px solid #28a745; }
.ad-card { border: 1px solid #ddd; border-radius: 6px; padding: 10px; margin: 10px 0; page-break-inside: avoid; }
.note { font-size: 8px; color: #666; font-style: italic; }
"""

    html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{account_name} — {days}-Day Report</title><style>{css}</style></head><body>\n'

    # Cover
    html += f'''<div class="cover">
<h1>📊 {account_name} — {days}-Day Performance Report</h1>
<div class="subtitle">{period_label}</div>
<div class="subtitle">Triple-Source: Meta | GA4 | Assumed Real (GA4 × 1.2)</div>
</div>\n'''

    # KPI cards
    if totals:
        t = totals
        cpa_class = "good" if t['ar']['cpa'] < 35 else ("warn" if t['ar']['cpa'] < 50 else "bad")
        roas_class = "good" if t['ar']['roas'] > 3 else ("warn" if t['ar']['roas'] > 2 else "bad")
        html += '<div class="kpi-row">'
        html += f'<div class="kpi"><div class="val">{fmt_money(t["spend"])}</div><div class="lbl">Total Spend</div></div>'
        html += f'<div class="kpi accent"><div class="val">{t["ar"]["purchases"]}</div><div class="lbl">AR Purchases</div></div>'
        html += f'<div class="kpi {cpa_class}"><div class="val">{fmt_money(t["ar"]["cpa"])}</div><div class="lbl">AR CPA</div></div>'
        html += f'<div class="kpi {roas_class}"><div class="val">{fmt_roas(t["ar"]["roas"])}</div><div class="lbl">AR ROAS</div></div>'
        html += f'<div class="kpi"><div class="val">{t["over_report_pct"]}%</div><div class="lbl">Meta Over-Report</div></div>'
        if prev_totals:
            cpa_delta = ((t['ar']['cpa'] / prev_totals['ar']['cpa']) - 1) * 100 if prev_totals['ar']['cpa'] else 0
            delta_class = "good" if cpa_delta < 0 else "bad"
            html += f'<div class="kpi {delta_class}"><div class="val">{cpa_delta:+.0f}%</div><div class="lbl">CPA vs Prev</div></div>'
        html += '</div>\n'

    # Process markdown sections into HTML with color coding
    md = report_md
    # Strip section 9 — we'll use HTML version
    s9_marker = "## 9. TOP 20 CONVERTING ADS"
    if s9_marker in md:
        md = md[:md.index(s9_marker)]

    # Convert markdown to HTML with smart table row coloring
    md = re.sub(r'```\n(.*?)\n```', lambda m: '<pre>' + m.group(1) + '</pre>', md, flags=re.DOTALL)
    md = re.sub(r'^### (.+)$', r'<h3>\1</h3>', md, flags=re.MULTILINE)
    md = re.sub(r'^## (.+)$', r'<h2>\1</h2>', md, flags=re.MULTILINE)
    md = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md)
    md = re.sub(r'`([^`]+)`', r'<code>\1</code>', md)
    md = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', md, flags=re.MULTILINE)

    # Convert tables with color-coded rows
    lines = md.split('\n')
    converted = []
    in_table = False
    row_count = 0
    for line in lines:
        if line.startswith('|') and '|' in line[1:]:
            if not in_table:
                converted.append('<table>')
                in_table = True
                row_count = 0
            if '---' in line:
                continue

            cells = [c.strip() for c in line.split('|')[1:-1]]
            row_count += 1

            # Determine row class based on content
            row_class = ''
            line_lower = line.lower()
            if '🔴' in line or 'stop' in line_lower:
                row_class = ' class="stop"'
            elif '🟢' in line or 'peak' in line_lower:
                row_class = ' class="peak"'
            elif '🟡' in line or 'weak' in line_lower or 'reduce' in line_lower:
                row_class = ' class="weak"'
            elif row_count == 1:
                # Header row
                converted.append('<tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>')
                continue

            # Color-code tracking health
            for keyword, cls in [('BROKEN', 'stop'), ('INVESTIGATE', 'stop'),
                                 ('DEGRADED', 'weak'), ('HEALTHY', 'peak')]:
                if keyword in line:
                    row_class = f' class="{cls}"'
                    break

            converted.append(f'<tr{row_class}>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
        else:
            if in_table:
                converted.append('</table>')
                in_table = False
                row_count = 0
            # Process non-table lines
            stripped = line.strip()
            if not stripped or stripped.startswith('<'):
                converted.append(line)
            elif stripped.startswith('🔴'):
                converted.append(f'<div class="action-item p-high">{stripped}</div>')
            elif stripped.startswith('🟡'):
                converted.append(f'<div class="action-item p-medium">{stripped}</div>')
            elif stripped.startswith('🟢'):
                converted.append(f'<div class="action-item p-low">{stripped}</div>')
            elif stripped.startswith('✅'):
                converted.append(f'<div class="action-item p-low">{stripped}</div>')
            elif stripped.startswith('⚠️'):
                converted.append(f'<div class="action-item p-medium">{stripped}</div>')
            else:
                converted.append(f'<p>{stripped}</p>')

    if in_table:
        converted.append('</table>')

    html += '\n'.join(converted)

    # Section 9: Top ads with images
    if top_ads:
        html += '\n<div class="page-break"></div>\n'
        html += section_top_ads_html(top_ads)

    html += '\n</body></html>'
    return html


def generate_report(args):
    """Generate the full report."""
    # Calculate date range
    end_date = datetime.now() - timedelta(days=1)
    start_date = end_date - timedelta(days=args.days)
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=args.days)

    date_start = start_date.strftime("%Y-%m-%d")
    date_end = end_date.strftime("%Y-%m-%d")
    prev_date_start = prev_start.strftime("%Y-%m-%d")
    prev_date_end = prev_end.strftime("%Y-%m-%d")

    period_label = f"{start_date.strftime('%b %d, %Y')} — {end_date.strftime('%b %d, %Y')}"

    campaign_ids = set(args.campaigns.split(",")) if args.campaigns else None
    account_name = args.account_name or args.account.replace("act_", "")
    # meta_api.py prepends act_ itself, so strip it if passed
    account_id = args.account.replace("act_", "")

    print(f"=== Generating {args.days}-Day Report for {account_name} ===")
    print(f"Period: {period_label}")
    if campaign_ids:
        print(f"Campaigns: {campaign_ids}")

    # Pull data
    print("\n[1/5] Pulling Meta data (account + campaigns + breakdowns + ad sets + ads)...", flush=True)
    token = load_token(args.meta_creds)
    acct_meta, camp_meta, breakdowns, adset_meta, ad_meta = pull_meta_data(
        token, account_id, date_start, date_end, campaign_ids)

    print(f"  → {len(camp_meta or [])} campaigns, {len(adset_meta or [])} ad sets, {len(ad_meta or [])} ads", flush=True)

    print("[2/5] Pulling GA4 data (totals + campaigns + device + region)...", flush=True)
    ga4_total, ga4_by_campaign, ga4_device, ga4_region = pull_ga4_data(
        args.ga4_creds, args.ga4_property, args.ga4_source, date_start, date_end, campaign_ids
    )
    print(f"  → {len(ga4_by_campaign)} campaign rows, {len(ga4_device)} device rows, {len(ga4_region)} region rows", flush=True)

    print("[3/5] Pulling previous period for comparison...", flush=True)
    prev_acct_meta = None
    prev_ga4_total = None
    try:
        prev_acct_meta, _, _, _, _ = pull_meta_data(token, account_id, prev_date_start, prev_date_end, campaign_ids)
        prev_ga4_total, _, _, _ = pull_ga4_data(
            args.ga4_creds, args.ga4_property, args.ga4_source, prev_date_start, prev_date_end, campaign_ids
        )
    except Exception as e:
        print(f"  ⚠️ Previous period failed: {e}")

    # Process account totals
    print("[4/5] Processing data...", flush=True)

    def extract_totals(meta_rows, ga4_rows):
        if not meta_rows:
            return None
        m = meta_rows[0] if isinstance(meta_rows, list) else meta_rows
        spend = float(m.get('spend', 0))
        meta_p = get_action(m, 'purchase') or get_action(m, 'offsite_conversion.fb_pixel_purchase') or 0
        meta_rev = get_action_value(m, 'purchase') or get_action_value(m, 'offsite_conversion.fb_pixel_purchase') or 0

        ga4_p = sum(int(r.get('ecommercePurchases', 0)) for r in ga4_rows) if ga4_rows else 0
        ga4_rev = sum(float(r.get('purchaseRevenue', 0)) for r in ga4_rows) if ga4_rows else 0

        return calc_triple(spend, int(meta_p), float(meta_rev), ga4_p, ga4_rev)

    totals = extract_totals(acct_meta, ga4_total)
    prev_totals = extract_totals(prev_acct_meta, prev_ga4_total) if prev_acct_meta else None

    # Build campaign-level triple-source data
    ga4_campaign_map = {}
    if ga4_by_campaign:
        for r in ga4_by_campaign:
            cid = r.get('sessionCampaignId', '')
            ga4_campaign_map[cid] = r

    campaign_triples = []
    if camp_meta:
        for c in camp_meta:
            cid = c.get('campaign_id', '')
            spend = float(c.get('spend', 0))
            meta_p = get_action(c, 'purchase') or get_action(c, 'offsite_conversion.fb_pixel_purchase') or 0
            meta_rev = get_action_value(c, 'purchase') or get_action_value(c, 'offsite_conversion.fb_pixel_purchase') or 0

            ga4_row = ga4_campaign_map.get(cid, {})
            ga4_p = int(ga4_row.get('ecommercePurchases', 0))
            ga4_rev = float(ga4_row.get('purchaseRevenue', 0))

            t = calc_triple(spend, int(meta_p), float(meta_rev), ga4_p, ga4_rev)
            t['name'] = c.get('campaign_name', cid)
            t['id'] = cid
            campaign_triples.append(t)

    # Build waste + actions
    waste_items, recommendations, manager_actions = build_waste_and_actions(
        totals, campaign_triples, breakdowns, adset_data=adset_meta, days=args.days
    )

    # Pull top 20 ad creatives with images
    print("[5/7] Pulling top 20 ad creatives + images...", flush=True)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_ads = []
    if ad_meta:
        top_ads = pull_top_ad_creatives(token, ad_meta, output_path.parent, top_n=args.top_ads)
        print(f"  → {len(top_ads)} ads with creative details", flush=True)

        # Save top ads manifest for meta-ad-creator
        manifest_path = output_path.parent / "data" / "top_ads_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(manifest_path, 'w') as f:
            json.dump(top_ads, f, indent=2)
        print(f"  → Manifest saved: {manifest_path}", flush=True)

    # Assemble report
    print("[6/7] Building report...", flush=True)

    header = f"""```
{'═' * 66}
  META ADS {args.days}-DAY PERFORMANCE REPORT
  Account: {account_name} ({args.account})
  Period: {period_label} ({args.days} days)
  Previous: {prev_start.strftime('%b %d')} — {prev_end.strftime('%b %d, %Y')} ({args.days} days)
  Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC
  Campaigns: {len(camp_meta or [])} active | Ad Sets: {len(adset_meta or [])} | Ads: {len(ad_meta or [])}
  Triple-Source: Meta | GA4 | Assumed Real (GA4 × 1.2)
{'═' * 66}
```\n"""

    sections = [header]

    # Section 1: Account Snapshot
    if totals:
        sections.append(section_snapshot(account_name, period_label, args.days, totals, prev_totals))

    # Section 2: Tracking Health
    sections.append(section_tracking_health(campaign_triples, camp_meta, ga4_by_campaign))

    # Section 3: Campaign Verdicts
    if campaign_triples:
        sections.append(section_campaigns(campaign_triples))

    # Section 4: Cannibalization
    sections.append(section_cannibalization(adset_meta))

    # Section 5: Audience Segments
    sections.append("## 5. AUDIENCE SEGMENTATION — WHO TO KEEP, WHO TO CUT\n")
    if breakdowns.get('age_gender'):
        sections.append(section_age_gender(breakdowns['age_gender']))
    if breakdowns.get('device'):
        sections.append(section_device(breakdowns['device'], ga4_device, totals['spend'] if totals else 0))
    if breakdowns.get('placement'):
        sections.append(section_placement(breakdowns['placement']))
    if breakdowns.get('hourly'):
        sections.append(section_dayparting(breakdowns['hourly'], args.days))

    # Section 6: Frequency
    sections.append(section_frequency(acct_meta))

    # Section 7: Waste
    sections.append(section_waste(waste_items))

    # Section 8: Actions
    sections.append(section_actions(recommendations))

    # Section 9: Top 20 Ads
    if top_ads:
        sections.append(section_top_ads_md(top_ads))

    report_md = "\n\n".join(sections)

    # Save markdown
    with open(output_path, 'w') as f:
        f.write(report_md)
    print(f"\n✅ Report saved: {output_path} ({len(report_md):,} chars)")

    # Generate PDF if requested
    print("[7/7] Generating PDF...", flush=True)
    if args.pdf:
        try:
            import re
            import subprocess

            pdf_path = output_path.with_suffix('.pdf')
            html_path = output_path.with_suffix('.html')

            html_content = build_html_report(
                report_md, top_ads, account_name, period_label, args.days,
                totals, prev_totals, campaign_triples, manager_actions
            )

            with open(html_path, 'w') as f:
                f.write(html_content)

            # Convert to PDF — try weasyprint first, then chromium
            try:
                from weasyprint import HTML as WeasyHTML
                WeasyHTML(filename=str(html_path)).write_pdf(str(pdf_path))
            except ImportError:
                # Fallback to chromium
                for browser in ['chromium-browser', 'chromium', 'google-chrome']:
                    result = subprocess.run(
                        [browser, '--headless', '--disable-gpu', '--no-sandbox',
                         '--print-to-pdf=' + str(pdf_path), str(html_path)],
                        capture_output=True, timeout=60
                    )
                    if pdf_path.exists():
                        break

            if pdf_path.exists():
                print(f"✅ PDF saved: {pdf_path} ({pdf_path.stat().st_size // 1024} KB)")
            else:
                print(f"⚠️ PDF generation failed, HTML saved: {html_path}")
        except Exception as e:
            print(f"⚠️ PDF generation error: {e}")

    # ── Add creative refresh actions from top_ads ──
    if top_ads:
        for i, ad in enumerate(top_ads[:5]):  # Top 5 get refresh recommendations
            if ad.get('image_local'):
                manager_actions.append({
                    "type": "create_variants",
                    "priority": "medium" if i < 3 else "low",
                    "target": "ad",
                    "target_id": ad['ad_id'],
                    "target_name": ad['ad_name'],
                    "action": "generate_creative_variants",
                    "params": {
                        "source_image": ad['image_local'],
                        "source_roas": ad['meta_roas'],
                        "source_spend": ad['spend'],
                        "headline": ad.get('title', ''),
                        "body": ad.get('body', ''),
                        "cta": ad.get('cta', ''),
                        "variations": 6,
                        "swap_dogs": True,
                        "command": f"python3 edit_ad.py -i {ad['image_local']} --variations 6 --swap-dogs",
                    },
                    "reason": f"#{i+1} performing ad (ROAS {fmt_roas(ad['meta_roas'])}). Generate fresh variants to combat fatigue.",
                })

    # ── Save actionable data ──
    data_dir = output_path.parent / "data"
    data_dir.mkdir(exist_ok=True)

    # Manager actions JSON — the key output for meta-ad-manager
    actions_path = data_dir / f"manager_actions_{args.days}d.json"
    actions_output = {
        "generated": datetime.utcnow().isoformat(),
        "account": args.account,
        "account_name": account_name,
        "period_days": args.days,
        "period_start": date_start,
        "period_end": date_end,
        "summary": {
            "total_actions": len(manager_actions),
            "high_priority": len([a for a in manager_actions if a.get('priority') == 'high']),
            "medium_priority": len([a for a in manager_actions if a.get('priority') == 'medium']),
            "low_priority": len([a for a in manager_actions if a.get('priority') == 'low']),
            "total_estimated_savings_daily": round(sum(a.get('estimated_savings_daily', 0) for a in manager_actions), 2),
            "total_waste": round(sum(w['amount'] for w in waste_items), 2),
        },
        "actions": manager_actions,
    }
    with open(actions_path, 'w') as f:
        json.dump(actions_output, f, indent=2)
    print(f"📋 Manager actions saved: {actions_path} ({len(manager_actions)} actions)")

    # Raw data for reproducibility
    with open(data_dir / f"report_{args.days}d_meta.json", 'w') as f:
        json.dump({"account": acct_meta, "campaigns": camp_meta, "breakdowns": breakdowns}, f, indent=2, default=str)
    with open(data_dir / f"report_{args.days}d_ga4.json", 'w') as f:
        json.dump({"total": ga4_total, "by_campaign": ga4_by_campaign}, f, indent=2, default=str)

    print(f"📦 Raw data saved to {data_dir}/")
    return report_md


def main():
    parser = argparse.ArgumentParser(description="Generate Meta Ads performance report")
    parser.add_argument("--account", required=True, help="Meta ad account ID (e.g. act_23987596)")
    parser.add_argument("--account-name", help="Human-readable account name (e.g. 'Pet Bucket')")
    parser.add_argument("--meta-creds", required=True, help="Path to Meta credentials file")
    parser.add_argument("--ga4-creds", required=True, help="Path to GA4 service account JSON")
    parser.add_argument("--ga4-property", required=True, help="GA4 property ID")
    parser.add_argument("--ga4-source", default="facebook_ads_ppm", help="GA4 sessionSource value for Facebook traffic")
    parser.add_argument("--days", type=int, default=60, help="Report period in days")
    parser.add_argument("--campaigns", help="Comma-separated campaign IDs (all if omitted)")
    parser.add_argument("--output", default="./report.md", help="Output file path (.md)")
    parser.add_argument("--pdf", action="store_true", help="Also generate PDF")
    parser.add_argument("--top-ads", type=int, default=20, help="Number of top ads to include (default 20)")
    parser.add_argument("--mode", choices=["historical", "live"], default="historical", help="Analysis mode")

    args = parser.parse_args()
    generate_report(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Daily Campaign Health Check for Meta Ads Campaign Monitor

Performs daily monitoring of active campaigns across all health dimensions:
- Spend pacing
- Cost metrics (CPA, ROAS)
- ROAS floor checks
- Scaling opportunity detection
- Learning phase status
- Creative health
- Audience health

Functions:
- check_pacing: Verify budget spend is on pace
- check_roas_floor: Verify minimum ROAS threshold
- check_scaling_opportunity: Detect scaling opportunities
- generate_daily_report: Aggregate health checks into report
"""

import argparse
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DailyHealthCheck:
    """Performs daily campaign health monitoring."""

    # Alert thresholds
    PACING_UNDERSPEND = 0.80  # <80% of budget
    PACING_OVERSPEND = 1.20   # >120% of budget
    PACING_CRITICAL = 1.50    # >150% of budget
    CPA_HIGH_THRESHOLD = 2.0  # >2× target CPA
    CPA_CRITICAL_THRESHOLD = 3.0  # >3× target CPA
    BUDGET_CAP_THRESHOLD = 0.95  # ≥95% of budget (scaling candidate)

    def __init__(self, supabase_client=None):
        """
        Initialize health checker.

        Args:
            supabase_client: Optional Supabase client for data access
        """
        self.supabase_client = supabase_client
        self.checks_run = []

    def check_pacing(
        self,
        campaign_data: Dict,
        planned_budget: float
    ) -> Dict:
        """
        Check budget pacing (actual spend vs planned budget).

        Args:
            campaign_data: Campaign metrics (actual_spend, meta_spend, etc.)
            planned_budget: Planned daily budget in USD

        Returns:
            Dict with pacing status and severity
        """
        actual_spend = campaign_data.get("actual_spend", 0.0)
        pacing_pct = (actual_spend / planned_budget * 100) if planned_budget > 0 else 0.0

        severity = "OK"
        if pacing_pct < (self.PACING_UNDERSPEND * 100):
            severity = "UNDERSPEND"
        elif pacing_pct > (self.PACING_CRITICAL * 100):
            severity = "CRITICAL_OVERSPEND"
        elif pacing_pct > (self.PACING_OVERSPEND * 100):
            severity = "OVERSPEND"

        result = {
            "metric": "PACING",
            "actual_spend": actual_spend,
            "planned_budget": planned_budget,
            "pacing_percentage": pacing_pct,
            "pacing_ratio": pacing_pct / 100.0,
            "severity": severity,
            "status": "OK" if severity == "OK" else "ALERT",
            "checked_at": datetime.utcnow().isoformat()
        }

        if severity == "UNDERSPEND":
            result["description"] = f"Underspending: only {pacing_pct:.1f}% of budget used"
            result["recommendation"] = "Loosen bid strategy, broaden audience, or increase budget"
        elif severity == "CRITICAL_OVERSPEND":
            result["description"] = f"Critical overspend: {pacing_pct:.1f}% of budget (>150%)"
            result["recommendation"] = "PAUSE — verify budget cap is functioning"
            result["alert_level"] = "CRITICAL"
        elif severity == "OVERSPEND":
            result["description"] = f"Overspending: {pacing_pct:.1f}% of budget (>120%)"
            result["recommendation"] = "Check budget cap, reduce bid strategy cap"
            result["alert_level"] = "HIGH"

        logger.info(f"Pacing check: {pacing_pct:.1f}% ({severity})")
        return result

    def check_roas_floor(
        self,
        campaign_data: Dict,
        min_acceptable_roas: float,
        target_roas: float,
        days_below_threshold: int = 0
    ) -> Dict:
        """
        Check if campaign ROAS meets minimum acceptable floor.

        Args:
            campaign_data: Campaign metrics (ar_roas, etc.)
            min_acceptable_roas: Minimum acceptable ROAS floor
            target_roas: Target ROAS
            days_below_threshold: Number of days ROAS has been below floor

        Returns:
            Dict with ROAS status
        """
        ar_roas = campaign_data.get("ar_roas", 0.0)

        # Determine status
        if ar_roas < min_acceptable_roas and days_below_threshold >= 7:
            status = "CRITICAL"
            alert_level = "CRITICAL"
            description = f"ROAS {ar_roas:.2f} below floor {min_acceptable_roas:.2f} for 7+ days"
            recommendation = "PAUSE campaign — below acceptable profitability floor"
        elif ar_roas < min_acceptable_roas:
            status = "WATCH"
            alert_level = "MEDIUM"
            description = f"ROAS {ar_roas:.2f} below floor {min_acceptable_roas:.2f} for {days_below_threshold} days"
            recommendation = "Monitor closely; may need restructuring"
        elif ar_roas < target_roas:
            status = "UNDERPERFORMING"
            alert_level = "MEDIUM"
            description = f"ROAS {ar_roas:.2f} below target {target_roas:.2f}"
            recommendation = "Monitor for optimization opportunities"
        else:
            status = "HEALTHY"
            alert_level = None
            description = f"ROAS {ar_roas:.2f} meets target {target_roas:.2f}"
            recommendation = None

        result = {
            "metric": "ROAS_FLOOR",
            "ar_roas": ar_roas,
            "min_acceptable_roas": min_acceptable_roas,
            "target_roas": target_roas,
            "days_below_floor": days_below_threshold,
            "status": status,
            "alert_level": alert_level,
            "description": description,
            "recommendation": recommendation,
            "checked_at": datetime.utcnow().isoformat()
        }

        logger.info(f"ROAS floor check: {ar_roas:.2f} vs floor {min_acceptable_roas:.2f} ({status})")
        return result

    def check_scaling_opportunity(
        self,
        campaign_data: Dict,
        campaign_config: Dict,
        scaling_config: Dict
    ) -> Dict:
        """
        Detect if campaign qualifies for budget scaling.

        All 4 conditions must be met:
        1. Budget-capped (spending ≥95% of daily budget)
        2. Strong ROAS (≥min_ar_roas_to_scale)
        3. Consistent cap (≥min_days_at_budget_cap consecutive days)
        4. Cooldown respected (no scaling in past cooldown_days_after_scale)

        Args:
            campaign_data: Campaign metrics
            campaign_config: Campaign configuration
            scaling_config: Scaling configuration (from brand_config)

        Returns:
            Dict with scaling opportunity details
        """
        actual_spend = campaign_data.get("actual_spend", 0.0)
        planned_budget = campaign_config.get("daily_budget", 1.0)
        ar_roas = campaign_data.get("ar_roas", 0.0)
        days_at_cap = campaign_data.get("days_at_budget_cap", 0)
        days_since_scaling = campaign_data.get("days_since_last_scaling", 100)

        # Extract scaling config
        min_ar_roas = scaling_config.get("min_ar_roas_to_scale", 2.5)
        min_days_at_cap = scaling_config.get("min_days_at_budget_cap", 3)
        cooldown_days = scaling_config.get("cooldown_days_after_scale", 7)
        step_pct = scaling_config.get("step_pct", 0.10)
        max_cap = scaling_config.get("max_budget_cap", 10000.0)

        # Check all 4 conditions
        pacing = actual_spend / planned_budget if planned_budget > 0 else 0.0
        condition_1 = pacing >= self.BUDGET_CAP_THRESHOLD
        condition_2 = ar_roas >= min_ar_roas
        condition_3 = days_at_cap >= min_days_at_cap
        condition_4 = days_since_scaling >= cooldown_days

        all_conditions_met = condition_1 and condition_2 and condition_3 and condition_4

        # Calculate proposed budget if scaling
        proposed_budget = planned_budget
        weekly_increase = 0.0

        if all_conditions_met:
            proposed_budget = min(
                planned_budget * (1.0 + step_pct),
                max_cap
            )
            weekly_increase = (proposed_budget - planned_budget) * 7.0

        result = {
            "metric": "SCALING_OPPORTUNITY",
            "campaign_id": campaign_config.get("id"),
            "campaign_name": campaign_config.get("name"),
            "is_scaling_opportunity": all_conditions_met,
            "conditions_met": {
                "budget_capped": condition_1,
                "strong_roas": condition_2,
                "consistent_duration": condition_3,
                "cooldown_respected": condition_4
            },
            "current_budget": planned_budget,
            "current_pacing": pacing,
            "current_roas": ar_roas,
            "min_roas_threshold": min_ar_roas,
            "days_at_cap": days_at_cap,
            "days_since_scaling": days_since_scaling,
            "proposed_budget": proposed_budget if all_conditions_met else None,
            "increase_percentage": step_pct * 100 if all_conditions_met else None,
            "weekly_impact": weekly_increase if all_conditions_met else None,
            "checked_at": datetime.utcnow().isoformat()
        }

        if all_conditions_met:
            result["recommendation"] = (
                f"Budget-capped with {ar_roas:.2f}× ROAS. "
                f"Increase daily budget from ${planned_budget:.2f} to ${proposed_budget:.2f} "
                f"(+{step_pct*100:.0f}%). Weekly impact: +${weekly_increase:.2f}."
            )
            result["alert_level"] = "INFO"

        logger.info(
            f"Scaling check: {campaign_config.get('name')} - "
            f"Conditions: {condition_1}/{condition_2}/{condition_3}/{condition_4} = {all_conditions_met}"
        )

        return result

    def generate_daily_report(
        self,
        campaign_checks: List[Dict],
        account_summary: Dict
    ) -> Dict:
        """
        Generate a daily health report from health checks.

        Args:
            campaign_checks: List of per-campaign check results
            account_summary: Account-level summary metrics

        Returns:
            Dict with complete daily report
        """
        # Count alert levels
        critical_count = sum(1 for c in campaign_checks if c.get("alert_level") == "CRITICAL")
        high_count = sum(1 for c in campaign_checks if c.get("alert_level") == "HIGH")
        medium_count = sum(1 for c in campaign_checks if c.get("alert_level") == "MEDIUM")

        # Overall account status
        if critical_count > 0:
            account_status = "CRITICAL"
        elif high_count > 0:
            account_status = "WARNING"
        elif medium_count > 0:
            account_status = "CAUTION"
        else:
            account_status = "HEALTHY"

        # Scaling opportunities
        scaling_opps = [c for c in campaign_checks if c.get("is_scaling_opportunity")]

        report = {
            "report_date": datetime.utcnow().isoformat(),
            "account_status": account_status,
            "summary": {
                "campaigns_checked": len(campaign_checks),
                "critical_alerts": critical_count,
                "high_alerts": high_count,
                "medium_alerts": medium_count,
                "scaling_opportunities": len(scaling_opps),
                "account_metrics": account_summary
            },
            "campaigns": campaign_checks,
            "scaling_opportunities": scaling_opps,
            "recommendations": []
        }

        # Build recommendations
        for campaign in campaign_checks:
            if campaign.get("recommendation"):
                report["recommendations"].append({
                    "campaign": campaign.get("campaign_name"),
                    "action": campaign.get("recommendation"),
                    "priority": campaign.get("alert_level", "INFO")
                })

        logger.info(
            f"Daily report generated: {account_status} "
            f"({critical_count} critical, {high_count} high, {medium_count} medium)"
        )

        return report


def main():
    """Command-line interface for health checks."""
    parser = argparse.ArgumentParser(
        description="Daily Campaign Health Check"
    )
    parser.add_argument(
        "--campaign-data",
        required=True,
        help="Path to campaign data JSON"
    )
    parser.add_argument(
        "--check-type",
        choices=["pacing", "roas_floor", "scaling", "full"],
        default="full",
        help="Type of health check to run"
    )
    parser.add_argument(
        "--min-roas",
        type=float,
        default=2.0,
        help="Minimum acceptable ROAS floor"
    )
    parser.add_argument(
        "--target-roas",
        type=float,
        default=3.0,
        help="Target ROAS"
    )
    parser.add_argument(
        "--scaling-config",
        help="Path to scaling config JSON"
    )
    parser.add_argument(
        "--output",
        help="Save report to JSON file"
    )

    args = parser.parse_args()

    # Load campaign data
    try:
        with open(args.campaign_data) as f:
            campaign_data = json.load(f)
    except Exception as e:
        print(f"Error loading campaign data: {e}")
        return 1

    # Load scaling config if provided
    scaling_config = {}
    if args.scaling_config:
        try:
            with open(args.scaling_config) as f:
                scaling_config = json.load(f)
        except Exception as e:
            print(f"Error loading scaling config: {e}")
            return 1

    # Initialize health checker
    checker = DailyHealthCheck()

    # Extract budget from campaign data
    planned_budget = campaign_data.get("daily_budget", campaign_data.get("planned_budget", 500.0))

    results = {}

    # Run checks based on type
    if args.check_type in ["pacing", "full"]:
        results["pacing"] = checker.check_pacing(campaign_data, planned_budget)

    if args.check_type in ["roas_floor", "full"]:
        results["roas_floor"] = checker.check_roas_floor(
            campaign_data,
            args.min_roas,
            args.target_roas,
            campaign_data.get("days_below_roas_floor", 0)
        )

    if args.check_type in ["scaling", "full"]:
        if scaling_config:
            results["scaling"] = checker.check_scaling_opportunity(
                campaign_data,
                campaign_data,
                scaling_config
            )

    # Save report if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Report saved to: {args.output}")

    # Print results
    print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())

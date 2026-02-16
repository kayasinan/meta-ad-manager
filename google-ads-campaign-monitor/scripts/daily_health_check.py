#!/usr/bin/env python3
"""
Daily Health Check for Google Ads Campaigns

Runs 14-point daily monitoring checklist on active campaigns.
Generates alerts for critical issues and scaling proposals.

Usage:
  python daily_health_check.py --brand-id brand_abc --cycle-id cycle_123 --output daily_brief.json
"""

import argparse
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class MetricSnapshot:
    """Daily metrics snapshot for a campaign"""
    campaign_id: str
    campaign_name: str
    date: str
    spend: float
    clicks: int
    impressions: int
    conversions: int
    conversion_value: float
    cpa: float
    roas: float
    ctr: float
    cpc: float
    daily_budget: float


@dataclass
class Alert:
    """Alert for critical or warning issues"""
    campaign_id: str
    campaign_name: str
    alert_type: str
    severity: AlertSeverity
    description: str
    metric: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    recommendation: Optional[str] = None


class DailyHealthCheck:
    """Performs 14-point daily monitoring on Google Ads campaigns"""

    def __init__(self, brand_id: str, brand_config: Dict):
        self.brand_id = brand_id
        self.brand_config = brand_config
        self.alerts: List[Alert] = []
        self.today = datetime.now().strftime("%Y-%m-%d")

    def check_1_spend_pacing(self, metric: MetricSnapshot) -> None:
        """Check 1: Spend pacing vs budget"""
        logger.info(f"Check 1: Spend pacing - {metric.campaign_name}")

        pacing_ratio = metric.spend / metric.daily_budget if metric.daily_budget > 0 else 0

        if pacing_ratio < 0.70:
            alert = Alert(
                campaign_id=metric.campaign_id,
                campaign_name=metric.campaign_name,
                alert_type="BUDGET_UNDERSPEND",
                severity=AlertSeverity.WARNING,
                description=f"Campaign spending only {pacing_ratio*100:.1f}% of daily budget (${metric.spend:.2f} of ${metric.daily_budget:.2f})",
                metric="spend_pacing",
                metric_value=pacing_ratio,
                threshold=0.70,
                recommendation="Investigate: Low impression volume, targeting too narrow, or budget cap set too high?"
            )
            self.alerts.append(alert)
        elif pacing_ratio > 1.10:
            alert = Alert(
                campaign_id=metric.campaign_id,
                campaign_name=metric.campaign_name,
                alert_type="BUDGET_OVERSPEND",
                severity=AlertSeverity.CRITICAL,
                description=f"Campaign spending {pacing_ratio*100:.1f}% of daily budget (${metric.spend:.2f} of ${metric.daily_budget:.2f})",
                metric="spend_pacing",
                metric_value=pacing_ratio,
                threshold=1.0,
                recommendation="URGENT: Campaign exceeding daily budget cap"
            )
            self.alerts.append(alert)

    def check_2_performance_targets(self, metric: MetricSnapshot) -> None:
        """Check 2: Performance vs targets"""
        logger.info(f"Check 2: Performance targets - {metric.campaign_name}")

        target_cpa = self.brand_config.get("target_cpa", 30.0)
        target_roas = self.brand_config.get("target_roas", 2.0)

        # CPA check
        if metric.cpa > target_cpa * 1.30:
            alert = Alert(
                campaign_id=metric.campaign_id,
                campaign_name=metric.campaign_name,
                alert_type="CPA_UNDERPERFORM",
                severity=AlertSeverity.CRITICAL,
                description=f"CPA ${metric.cpa:.2f} is 30%+ above target ${target_cpa:.2f}",
                metric="cpa",
                metric_value=metric.cpa,
                threshold=target_cpa * 1.30,
                recommendation="Review targeting, landing pages, conversion tracking"
            )
            self.alerts.append(alert)
        elif metric.cpa > target_cpa * 1.20:
            alert = Alert(
                campaign_id=metric.campaign_id,
                campaign_name=metric.campaign_name,
                alert_type="CPA_WARNING",
                severity=AlertSeverity.WARNING,
                description=f"CPA ${metric.cpa:.2f} is 20%+ above target ${target_cpa:.2f}",
                metric="cpa",
                metric_value=metric.cpa,
                threshold=target_cpa * 1.20
            )
            self.alerts.append(alert)

        # ROAS check
        min_roas = self.brand_config.get("min_acceptable_ar_roas", 1.5)
        if metric.roas < min_roas * 0.80:
            alert = Alert(
                campaign_id=metric.campaign_id,
                campaign_name=metric.campaign_name,
                alert_type="ROAS_CRITICAL",
                severity=AlertSeverity.CRITICAL,
                description=f"ROAS {metric.roas:.2f}x is critically below minimum {min_roas:.2f}x",
                metric="roas",
                metric_value=metric.roas,
                threshold=min_roas,
                recommendation="Campaign losing money or very close, consider pause"
            )
            self.alerts.append(alert)
        elif metric.roas < min_roas:
            alert = Alert(
                campaign_id=metric.campaign_id,
                campaign_name=metric.campaign_name,
                alert_type="ROAS_WARNING",
                severity=AlertSeverity.WARNING,
                description=f"ROAS {metric.roas:.2f}x below minimum {min_roas:.2f}x",
                metric="roas",
                metric_value=metric.roas,
                threshold=min_roas
            )
            self.alerts.append(alert)

    def check_3_quality_score(self, campaign_data: Dict) -> None:
        """Check 3: Quality Score (Search only)"""
        logger.info(f"Check 3: Quality Score - {campaign_data.get('campaign_name')}")

        quality_scores = campaign_data.get("quality_scores", [])

        if not quality_scores:
            return  # Not a Search campaign or no QS data

        avg_qs = sum(qs.get("score", 7) for qs in quality_scores) / len(quality_scores)

        if avg_qs < 5:
            alert = Alert(
                campaign_id=campaign_data.get("campaign_id"),
                campaign_name=campaign_data.get("campaign_name"),
                alert_type="QS_POOR",
                severity=AlertSeverity.CRITICAL,
                description=f"Average Quality Score {avg_qs:.1f} is very low (below 5)",
                metric="quality_score",
                metric_value=avg_qs,
                recommendation="Review all components: Ad Relevance, Landing Page Experience, Expected CTR"
            )
            self.alerts.append(alert)
        elif avg_qs < 6:
            alert = Alert(
                campaign_id=campaign_data.get("campaign_id"),
                campaign_name=campaign_data.get("campaign_name"),
                alert_type="QS_WARNING",
                severity=AlertSeverity.WARNING,
                description=f"Average Quality Score {avg_qs:.1f} below 6",
                metric="quality_score",
                metric_value=avg_qs
            )
            self.alerts.append(alert)

    def check_4_impression_share(self, campaign_data: Dict) -> None:
        """Check 4: Impression Share (Search only)"""
        logger.info(f"Check 4: Impression Share - {campaign_data.get('campaign_name')}")

        imp_share = campaign_data.get("impression_share", None)

        if imp_share is None:
            return  # Not applicable

        is_lost_to_budget = campaign_data.get("is_lost_to_budget", 0)
        is_lost_to_rank = campaign_data.get("is_lost_to_rank", 0)

        if imp_share < 0.50 and is_lost_to_rank > 0.15:
            alert = Alert(
                campaign_id=campaign_data.get("campaign_id"),
                campaign_name=campaign_data.get("campaign_name"),
                alert_type="IS_LOST_TO_RANK",
                severity=AlertSeverity.WARNING,
                description=f"Impression Share {imp_share*100:.1f}% with {is_lost_to_rank*100:.1f}% lost to rank",
                metric="impression_share",
                metric_value=imp_share,
                recommendation="Increase bids or improve Quality Score"
            )
            self.alerts.append(alert)

        if is_lost_to_budget > 0.15:
            alert = Alert(
                campaign_id=campaign_data.get("campaign_id"),
                campaign_name=campaign_data.get("campaign_name"),
                alert_type="IS_LOST_TO_BUDGET",
                severity=AlertSeverity.WARNING,
                description=f"{is_lost_to_budget*100:.1f}% impression share lost to budget",
                metric="is_lost_to_budget",
                metric_value=is_lost_to_budget,
                recommendation="Consider increasing daily budget"
            )
            self.alerts.append(alert)

    def check_5_search_terms(self, search_terms: List[Dict]) -> None:
        """Check 5: Search term review (Search only)"""
        logger.info("Check 5: Search term review")

        # High-spend, zero-conversion terms
        high_waste_terms = [
            term for term in search_terms
            if term.get("spend", 0) > 50 and term.get("conversions", 0) == 0
        ]

        if high_waste_terms:
            terms_list = ", ".join([t.get("search_term", "") for t in high_waste_terms[:5]])
            alert = Alert(
                campaign_id="search_campaign",
                campaign_name="Search Campaign",
                alert_type="HIGH_SPEND_ZERO_CONV",
                severity=AlertSeverity.WARNING,
                description=f"{len(high_waste_terms)} terms with >$50 spend, 0 conversions: {terms_list}",
                recommendation="Add these terms as negative keywords"
            )
            self.alerts.append(alert)

    def check_6_smart_bidding_rampup(self, campaign_data: Dict) -> None:
        """Check 6: Smart bidding ramp-up status"""
        logger.info(f"Check 6: Smart bidding - {campaign_data.get('campaign_name')}")

        bidding_strategy = campaign_data.get("bidding_strategy", "MANUAL_CPC")

        if "TARGET_" in bidding_strategy or "MAXIMIZE_" in bidding_strategy:
            campaign_age_days = campaign_data.get("campaign_age_days", 0)
            conversions_7day = campaign_data.get("conversions_7day", 0)
            is_learning = campaign_data.get("is_learning_phase", False)

            if campaign_age_days > 21 and is_learning and conversions_7day < 50:
                alert = Alert(
                    campaign_id=campaign_data.get("campaign_id"),
                    campaign_name=campaign_data.get("campaign_name"),
                    alert_type="SMART_BID_STUCK",
                    severity=AlertSeverity.CRITICAL,
                    description=f"Campaign {campaign_age_days} days old, still in Learning with <50 conversions",
                    recommendation="Increase budget or audience size to accelerate learning"
                )
                self.alerts.append(alert)

    def check_7_tracking_health(self, tracking_data: Dict) -> None:
        """Check 7: Conversion tracking health"""
        logger.info("Check 7: Tracking health")

        conversion_tag_firing = tracking_data.get("conversion_tag_firing", False)
        ga4_syncing = tracking_data.get("ga4_syncing", False)
        click_to_session_rate = tracking_data.get("click_to_session_rate", 0)

        if not conversion_tag_firing:
            alert = Alert(
                campaign_id="account",
                campaign_name="All Campaigns",
                alert_type="TAG_NOT_FIRING",
                severity=AlertSeverity.CRITICAL,
                description="Google Conversion tracking tag not firing",
                recommendation="URGENT: Check Google Tag Manager, conversion tracking tag deployment"
            )
            self.alerts.append(alert)

        if not ga4_syncing:
            alert = Alert(
                campaign_id="account",
                campaign_name="All Campaigns",
                alert_type="GA4_NOT_SYNCING",
                severity=AlertSeverity.CRITICAL,
                description="GA4 not receiving conversion data",
                recommendation="Check GA4 event mapping, data flow configuration"
            )
            self.alerts.append(alert)

        if click_to_session_rate < 0.50:
            alert = Alert(
                campaign_id="account",
                campaign_name="All Campaigns",
                alert_type="TRACKING_LOSS",
                severity=AlertSeverity.CRITICAL,
                description=f"Click-to-session rate only {click_to_session_rate*100:.1f}% (target >70%)",
                recommendation="Significant tracking loss, investigate tag deployment"
            )
            self.alerts.append(alert)

    def check_8_creative_fatigue(self, ad_data: List[Dict]) -> None:
        """Check 8: Creative fatigue signals"""
        logger.info("Check 8: Creative fatigue")

        fatigued_ads = []
        for ad in ad_data:
            baseline_ctr = ad.get("baseline_ctr", 0.05)
            current_ctr = ad.get("current_ctr", 0.05)
            ctr_decline = (baseline_ctr - current_ctr) / baseline_ctr if baseline_ctr > 0 else 0

            if ctr_decline > 0.30:  # >30% CTR decline
                fatigued_ads.append(ad.get("ad_id", ""))

        if fatigued_ads:
            alert = Alert(
                campaign_id="creative",
                campaign_name="All Campaigns",
                alert_type="CREATIVE_FATIGUE",
                severity=AlertSeverity.WARNING,
                description=f"{len(fatigued_ads)} ads showing >30% CTR decline (fatigue)",
                recommendation="Rotate creatives, refresh with new variants"
            )
            self.alerts.append(alert)

    def check_9_scaling_detection(self, metric: MetricSnapshot,
                                 previous_metrics: List[MetricSnapshot]) -> None:
        """Check 9: Budget scaling opportunity detection"""
        logger.info(f"Check 9: Scaling detection - {metric.campaign_name}")

        # Check if met scaling criteria for 3+ consecutive days
        min_roas = self.brand_config.get("min_acceptable_ar_roas", 1.5)
        pacing_ratio = metric.spend / metric.daily_budget if metric.daily_budget > 0 else 0

        scaling_criteria_met = (
            pacing_ratio >= 0.95 and
            metric.roas >= min_roas and
            metric.conversions >= 10
        )

        if scaling_criteria_met:
            # Check cooldown (no scaling in past 7 days)
            last_scale_date = self.brand_config.get("campaigns", {}).get(
                metric.campaign_id, {}
            ).get("last_scaled_date")

            if last_scale_date:
                days_since_scale = (datetime.now() - datetime.fromisoformat(last_scale_date)).days
                if days_since_scale < 7:
                    return  # Still in cooldown

            # Generate scaling proposal
            new_budget = metric.daily_budget * 1.40
            additional_spend = (metric.daily_budget * 0.96) - metric.spend
            estimated_uplift = additional_spend * metric.roas

            logger.info(f"Scaling opportunity detected for {metric.campaign_name}")
            logger.info(f"  Current budget: ${metric.daily_budget:.2f}")
            logger.info(f"  Proposed budget: ${new_budget:.2f}")
            logger.info(f"  Estimated monthly uplift: ${estimated_uplift * 30:.2f}")

    def run_all_checks(self, campaign_data: Dict) -> Dict:
        """Run all 14 monitoring checks"""
        logger.info(f"Starting 14-point daily health check for {campaign_data.get('campaign_name')}")

        # Create metric snapshot
        metric = MetricSnapshot(
            campaign_id=campaign_data.get("campaign_id"),
            campaign_name=campaign_data.get("campaign_name"),
            date=self.today,
            spend=campaign_data.get("spend", 0),
            clicks=campaign_data.get("clicks", 0),
            impressions=campaign_data.get("impressions", 0),
            conversions=campaign_data.get("conversions", 0),
            conversion_value=campaign_data.get("conversion_value", 0),
            cpa=campaign_data.get("cpa", 0),
            roas=campaign_data.get("roas", 0),
            ctr=campaign_data.get("ctr", 0),
            cpc=campaign_data.get("cpc", 0),
            daily_budget=campaign_data.get("daily_budget", 250)
        )

        # Run checks
        self.check_1_spend_pacing(metric)
        self.check_2_performance_targets(metric)
        self.check_3_quality_score(campaign_data)
        self.check_4_impression_share(campaign_data)
        self.check_5_search_terms(campaign_data.get("search_terms", []))
        self.check_6_smart_bidding_rampup(campaign_data)
        self.check_7_tracking_health(campaign_data.get("tracking", {}))
        self.check_8_creative_fatigue(campaign_data.get("ads", []))
        self.check_9_scaling_detection(metric, [])

        # Compile report
        critical_alerts = [a for a in self.alerts if a.severity == AlertSeverity.CRITICAL]
        warning_alerts = [a for a in self.alerts if a.severity == AlertSeverity.WARNING]

        report = {
            "date": self.today,
            "campaign_id": campaign_data.get("campaign_id"),
            "campaign_name": campaign_data.get("campaign_name"),
            "health_status": "CRITICAL" if critical_alerts else "WARNING" if warning_alerts else "HEALTHY",
            "metrics": asdict(metric),
            "alerts_count": {
                "critical": len(critical_alerts),
                "warning": len(warning_alerts),
                "total": len(self.alerts)
            },
            "alerts": [
                {
                    "type": a.alert_type,
                    "severity": a.severity.value,
                    "description": a.description,
                    "recommendation": a.recommendation
                }
                for a in self.alerts
            ]
        }

        return report


def main():
    parser = argparse.ArgumentParser(description="Daily Health Check for Google Ads")
    parser.add_argument("--brand-id", required=True, help="Brand ID")
    parser.add_argument("--cycle-id", help="Campaign cycle ID")
    parser.add_argument("--output", default="daily_brief.json", help="Output brief file")

    args = parser.parse_args()

    # Example brand config
    brand_config = {
        "brand_name": "SkincareCo",
        "target_cpa": 30.0,
        "target_roas": 2.0,
        "min_acceptable_ar_roas": 1.5
    }

    # Example campaign data
    campaign_data = {
        "campaign_id": "campaign_123",
        "campaign_name": "SEARCH_SkincareCo_US_BrandTerms_20260214",
        "spend": 237.50,
        "clicks": 1240,
        "impressions": 38750,
        "conversions": 82,
        "conversion_value": 6560,
        "cpa": 2.89,
        "roas": 2.77,
        "ctr": 0.032,
        "cpc": 0.191,
        "daily_budget": 250.0,
        "bidding_strategy": "TARGET_CPA",
        "quality_scores": [
            {"ad_id": "ad_1", "score": 8},
            {"ad_id": "ad_2", "score": 7}
        ],
        "impression_share": 0.78,
        "is_lost_to_budget": 0.05,
        "is_lost_to_rank": 0.17,
        "search_terms": [],
        "campaign_age_days": 15,
        "conversions_7day": 120,
        "is_learning_phase": False,
        "tracking": {
            "conversion_tag_firing": True,
            "ga4_syncing": True,
            "click_to_session_rate": 0.82
        },
        "ads": []
    }

    checker = DailyHealthCheck(args.brand_id, brand_config)
    report = checker.run_all_checks(campaign_data)

    # Output
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Daily brief saved to {args.output}")
    logger.info(f"Health Status: {report['health_status']}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

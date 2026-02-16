"""
Creative Fatigue Calculator for Google Ads

Calculates fatigue scores based on:
- CTR decay (35%)
- Frequency pressure (25%)
- Engagement decline (20%)
- Age (10%)
- Conversion rate decline (10%)

Fatigue ranges:
- 0-30: FRESH
- 31-60: AGING
- 61-80: FATIGUED
- 81-100: DEAD
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta


class FatigueCalculator:
    """Calculate creative fatigue scores for Google Ads."""

    def calculate_fatigue_score(self, ad_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate fatigue score for a single ad.

        Args:
            ad_metrics: Dict with current and historical metrics

        Returns:
            Dict with fatigue score (0-100) and component breakdown
        """
        # Extract metrics
        peak_ctr = ad_metrics.get("peak_ctr", 0.025)
        current_ctr = ad_metrics.get("current_ctr", 0.015)
        current_frequency = ad_metrics.get("current_frequency", 2.5)
        avg_frequency_7_14d = ad_metrics.get("avg_frequency_7_14d", 2.1)
        current_engagement = ad_metrics.get("current_engagement_rate", 0.042)
        avg_engagement_7_14d = ad_metrics.get("avg_engagement_7_14d", 0.052)
        days_active = ad_metrics.get("days_active", 30)
        historical_cr = ad_metrics.get("historical_conversion_rate", 0.032)
        current_cr = ad_metrics.get("current_conversion_rate", 0.028)

        # Component 1: CTR Decay (35% weight)
        ctr_decay_pct = self._calculate_ctr_decay(peak_ctr, current_ctr)
        ctr_score = min(100, ctr_decay_pct)  # Capped at 100

        # Component 2: Frequency Pressure (25% weight)
        frequency_pressure_pct = self._calculate_frequency_pressure(
            current_frequency, avg_frequency_7_14d
        )
        frequency_score = min(100, frequency_pressure_pct)

        # Component 3: Engagement Decline (20% weight)
        engagement_decline_pct = self._calculate_engagement_decline(
            avg_engagement_7_14d, current_engagement
        )
        engagement_score = min(100, engagement_decline_pct)

        # Component 4: Age (10% weight)
        age_score = min(100, (days_active / 30) * 100)

        # Component 5: Conversion Decline (10% weight)
        cr_decline_pct = self._calculate_cr_decline(historical_cr, current_cr)
        cr_score = min(100, cr_decline_pct)

        # Calculate composite fatigue score
        fatigue_score = (
            (ctr_score * 0.35) +
            (frequency_score * 0.25) +
            (engagement_score * 0.20) +
            (age_score * 0.10) +
            (cr_score * 0.10)
        )

        # Determine status
        status = self._get_fatigue_status(fatigue_score)

        return {
            "fatigue_score": round(fatigue_score, 1),
            "status": status,
            "components": {
                "ctr_decay": {
                    "value": ctr_decay_pct,
                    "score": round(ctr_score, 1),
                    "weight": 0.35,
                },
                "frequency_pressure": {
                    "value": frequency_pressure_pct,
                    "score": round(frequency_score, 1),
                    "weight": 0.25,
                },
                "engagement_decline": {
                    "value": engagement_decline_pct,
                    "score": round(engagement_score, 1),
                    "weight": 0.20,
                },
                "age": {
                    "value": days_active,
                    "score": round(age_score, 1),
                    "weight": 0.10,
                },
                "conversion_decline": {
                    "value": cr_decline_pct,
                    "score": round(cr_score, 1),
                    "weight": 0.10,
                },
            },
            "metrics": {
                "peak_ctr": peak_ctr,
                "current_ctr": current_ctr,
                "current_frequency": current_frequency,
                "days_active": days_active,
            }
        }

    def _calculate_ctr_decay(self, peak_ctr: float, current_ctr: float) -> float:
        """Calculate CTR decay percentage."""
        if peak_ctr == 0:
            return 0
        decay = ((peak_ctr - current_ctr) / peak_ctr) * 100
        return max(0, decay)

    def _calculate_frequency_pressure(self, current_freq: float, avg_freq: float) -> float:
        """Calculate frequency pressure percentage."""
        if avg_freq == 0:
            return 0
        pressure = ((current_freq - avg_freq) / avg_freq) * 100
        return max(0, pressure)

    def _calculate_engagement_decline(self, avg_engagement: float, current_engagement: float) -> float:
        """Calculate engagement decline percentage."""
        if avg_engagement == 0:
            return 0
        decline = ((avg_engagement - current_engagement) / avg_engagement) * 100
        return max(0, decline)

    def _calculate_cr_decline(self, historical_cr: float, current_cr: float) -> float:
        """Calculate conversion rate decline percentage."""
        if historical_cr == 0:
            return 0
        decline = ((historical_cr - current_cr) / historical_cr) * 100
        return max(0, decline)

    def _get_fatigue_status(self, score: float) -> str:
        """Map fatigue score to status."""
        if score <= 30:
            return "FRESH"
        elif score <= 60:
            return "AGING"
        elif score <= 80:
            return "FATIGUED"
        else:
            return "DEAD"

    def batch_calculate(self, ads_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate fatigue scores for multiple ads.

        Returns:
            List of ads sorted by fatigue score (highest first)
        """
        results = []

        for ad_metrics in ads_metrics:
            score_result = self.calculate_fatigue_score(ad_metrics)
            score_result["ad_id"] = ad_metrics.get("ad_id")
            score_result["ad_name"] = ad_metrics.get("ad_name")
            results.append(score_result)

        # Sort by fatigue score (highest/most fatigued first)
        return sorted(results, key=lambda x: x["fatigue_score"], reverse=True)

    def get_action_recommendation(self, fatigue_score: float) -> Dict[str, Any]:
        """
        Get action recommendation based on fatigue score.

        Returns:
            Dict with recommended action and timeline
        """
        if fatigue_score <= 30:
            return {
                "action": "MONITOR",
                "priority": "LOW",
                "timeline": "Monitor weekly",
                "description": "Ad performing well, no rotation needed"
            }
        elif fatigue_score <= 60:
            return {
                "action": "PREPARE_REPLACEMENT",
                "priority": "MEDIUM",
                "timeline": "Prepare rotation within 1 week",
                "description": "Ad showing early signs of wearout"
            }
        elif fatigue_score <= 80:
            return {
                "action": "ROTATE",
                "priority": "HIGH",
                "timeline": "Pause and rotate within 3-5 days",
                "description": "Ad is fatigued, rotation recommended"
            }
        else:
            return {
                "action": "PAUSE_IMMEDIATELY",
                "priority": "CRITICAL",
                "timeline": "Pause today",
                "description": "Ad is dead, remove from rotation"
            }

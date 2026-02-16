"""
Landing Page Scoring for Google Ads post-click analysis.

Scores landing pages based on:
- Conversion rate (35%)
- Bounce rate (25%)
- Session duration (20%)
- Mobile experience (10%)
- Revenue per session (10%)
"""

from typing import Dict, List, Any
import statistics


class LandingPageScorer:
    """Score landing pages for Google Ads traffic."""

    def __init__(self, account_metrics: Dict[str, float]):
        """
        Initialize scorer with account baseline metrics.

        Args:
            account_metrics: Dict with account avg CR, bounce rate, session duration, RPS
        """
        self.account_cr = account_metrics.get("avg_conversion_rate", 0.03)
        self.account_bounce = account_metrics.get("avg_bounce_rate", 0.45)
        self.account_duration = account_metrics.get("avg_session_duration", 60)
        self.account_rps = account_metrics.get("avg_revenue_per_session", 5.20)

    def score_page(self, page_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Score a single landing page.

        Args:
            page_metrics: Dict with page metrics (conv_rate, bounce_rate, duration, mobile_conv_rate, rps)

        Returns:
            Dict with score, components, verdict
        """
        # Extract metrics
        conv_rate = page_metrics.get("conversion_rate", 0)
        bounce_rate = page_metrics.get("bounce_rate", 0)
        duration = page_metrics.get("avg_session_duration", 0)
        mobile_cr = page_metrics.get("mobile_conversion_rate", conv_rate)
        rps = page_metrics.get("revenue_per_session", 0)

        # Component 1: Conversion Rate (35%)
        cr_score = min(100, (conv_rate / self.account_cr) * 100) if self.account_cr > 0 else 0

        # Component 2: Bounce Rate (25%)
        if bounce_rate < 0.45:
            bounce_score = 100
        elif bounce_rate < 0.65:
            bounce_score = 50
        else:
            bounce_score = 0

        # Component 3: Session Duration (20%)
        if duration > 60:
            duration_score = 100
        elif duration > 30:
            duration_score = 50
        else:
            duration_score = 0

        # Component 4: Mobile Experience (10%)
        mobile_gap = self.account_cr / mobile_cr if mobile_cr > 0 else 999
        mobile_score = max(0, min(100, 70 + (30 * (1 - min(1, 1 / mobile_gap)))))

        # Component 5: Revenue Per Session (10%)
        rps_score = min(100, (rps / self.account_rps) * 100) if self.account_rps > 0 else 0

        # Composite Score
        composite = (
            (cr_score * 0.35) +
            (bounce_score * 0.25) +
            (duration_score * 0.20) +
            (mobile_score * 0.10) +
            (rps_score * 0.10)
        )

        # Verdict
        verdict = self._get_verdict(conv_rate, bounce_rate, duration, mobile_gap)

        return {
            "composite_score": round(composite, 1),
            "conversion_rate_score": round(cr_score, 1),
            "bounce_rate_score": round(bounce_score, 1),
            "duration_score": round(duration_score, 1),
            "mobile_score": round(mobile_score, 1),
            "rps_score": round(rps_score, 1),
            "verdict": verdict,
            "metrics": {
                "conversion_rate": conv_rate,
                "bounce_rate": bounce_rate,
                "avg_session_duration": duration,
                "mobile_gap": mobile_gap,
                "revenue_per_session": rps,
            }
        }

    def _get_verdict(self, conv_rate: float, bounce_rate: float, duration: float, mobile_gap: float) -> str:
        """Determine KEEP/FIX/KILL verdict."""

        # KILL conditions
        if conv_rate < (self.account_cr * 0.5):
            return "KILL"
        if bounce_rate > 0.65:
            return "KILL"
        if duration < 30 and bounce_rate > 0.50:
            return "KILL"

        # KEEP conditions
        if conv_rate > (self.account_cr * 1.25) and bounce_rate < 0.45 and mobile_gap < 1.5:
            return "KEEP"

        # FIX conditions
        if mobile_gap > 2.0:
            return "FIX"
        if conv_rate < (self.account_cr * 0.75):
            return "FIX"
        if bounce_rate > 0.55:
            return "FIX"

        # Default
        return "FIX" if conv_rate < (self.account_cr * 1.0) else "KEEP"

    def score_pages_batch(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score multiple pages and return sorted by score."""
        results = []

        for page in pages:
            score_result = self.score_page(page)
            score_result["url"] = page.get("url")
            score_result["page_name"] = page.get("page_name")
            results.append(score_result)

        # Sort by composite score (descending)
        return sorted(results, key=lambda x: x["composite_score"], reverse=True)


def calculate_funnel_dropoff(funnel_events: List[Dict[str, int]]) -> Dict[str, Any]:
    """
    Calculate conversion funnel drop-off rates and dollar impact.

    Args:
        funnel_events: List of dicts with event_name and event_count

    Returns:
        Funnel analysis with drop-off rates and impact
    """
    funnel_order = ["page_view", "add_to_cart", "begin_checkout", "purchase"]
    events_by_name = {e["event_name"]: e["event_count"] for e in funnel_events}

    # Build funnel with drop-off rates
    funnel = []
    previous_count = None

    for event_name in funnel_order:
        count = events_by_name.get(event_name, 0)

        if previous_count is not None and previous_count > 0:
            dropoff_rate = (previous_count - count) / previous_count
        else:
            dropoff_rate = None

        funnel.append({
            "event": event_name,
            "count": count,
            "dropoff_rate": round(dropoff_rate, 3) if dropoff_rate is not None else None,
            "dropoff_pct": round(dropoff_rate * 100, 1) if dropoff_rate is not None else None,
        })

        previous_count = count

    return {"funnel": funnel}

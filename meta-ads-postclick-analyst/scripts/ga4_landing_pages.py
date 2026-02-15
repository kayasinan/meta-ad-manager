"""
GA4 landing page metrics extraction helper.
Pulls GA4 data filtered to Meta Ads traffic and calculates performance metrics.
"""

import json
from typing import List, Dict, Any

class LandingPageAnalyzer:
    """Analyzer for landing page performance using GA4 data."""

    def __init__(self, ga4_client):
        """
        Initialize landing page analyzer.

        Args:
            ga4_client: Initialized GA4APIClient instance
        """
        self.ga4_client = ga4_client

    def get_landing_page_metrics(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> List[Dict[str, Any]]:
        """
        Get landing page performance metrics filtered to paid social traffic.

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): {'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}
            source_filter (str): Session source to filter on (default 'facebook')

        Returns:
            List[Dict]: Landing page metrics with calculated scores
        """
        # Query GA4 for landing page data
        landing_pages_data = self.ga4_client.get_landing_page_metrics(
            property_id=property_id,
            date_range=date_range,
            source_filter=source_filter
        )

        # Enrich with additional calculations
        return self._enrich_landing_page_data(landing_pages_data)

    def _enrich_landing_page_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich raw GA4 data with calculated metrics and verdicts.

        Args:
            raw_data: Raw landing page metrics from GA4

        Returns:
            List: Enriched data with scores and verdicts
        """
        enriched = []

        # Calculate account-level averages
        account_avg_cr = self._calculate_average_conversion_rate(raw_data)
        account_avg_rps = self._calculate_average_revenue_per_session(raw_data)

        for page in raw_data:
            enriched_page = page.copy()

            # Calculate additional metrics
            enriched_page['conversion_rate_pct'] = (
                (page.get('conversions', 0) / page.get('sessions', 1)) * 100
                if page.get('sessions', 0) > 0 else 0
            )

            enriched_page['bounce_rate_pct'] = page.get('bounceRate', 0)

            enriched_page['avg_session_duration_sec'] = page.get('avgSessionDuration', 0)

            enriched_page['revenue_per_session'] = (
                page.get('totalRevenue', 0) / page.get('sessions', 1)
                if page.get('sessions', 0) > 0 else 0
            )

            # Calculate mobile vs. desktop split (if available)
            if 'deviceCategory' in page:
                enriched_page['device_type'] = page['deviceCategory']

            # Compare to account averages
            enriched_page['conversion_rate_vs_avg'] = (
                enriched_page['conversion_rate_pct'] / account_avg_cr * 100
                if account_avg_cr > 0 else 0
            )

            enriched_page['revenue_per_session_vs_avg'] = (
                enriched_page['revenue_per_session'] / account_avg_rps * 100
                if account_avg_rps > 0 else 0
            )

            # Assign verdict
            enriched_page['verdict'] = self._calculate_verdict(enriched_page, account_avg_cr, account_avg_rps)

            # Calculate overall score
            enriched_page['overall_score'] = self._calculate_overall_score(enriched_page)

            enriched.append(enriched_page)

        # Sort by revenue per session (most valuable first)
        enriched.sort(key=lambda x: x.get('revenue_per_session', 0), reverse=True)

        return enriched

    def _calculate_average_conversion_rate(self, pages: List[Dict[str, Any]]) -> float:
        """Calculate account-level average conversion rate."""
        total_conversions = sum(p.get('conversions', 0) for p in pages)
        total_sessions = sum(p.get('sessions', 0) for p in pages)
        return (total_conversions / total_sessions * 100) if total_sessions > 0 else 0

    def _calculate_average_revenue_per_session(self, pages: List[Dict[str, Any]]) -> float:
        """Calculate account-level average revenue per session."""
        total_revenue = sum(p.get('totalRevenue', 0) for p in pages)
        total_sessions = sum(p.get('sessions', 0) for p in pages)
        return (total_revenue / total_sessions) if total_sessions > 0 else 0

    def _calculate_verdict(
        self,
        page: Dict[str, Any],
        account_avg_cr: float,
        account_avg_rps: float
    ) -> str:
        """
        Calculate KEEP/FIX/KILL verdict for a landing page.

        Args:
            page: Page metrics
            account_avg_cr: Account average conversion rate
            account_avg_rps: Account average revenue per session

        Returns:
            str: Verdict (KEEP, FIX, or KILL)
        """
        cr = page.get('conversion_rate_pct', 0)
        br = page.get('bounce_rate_pct', 0)
        sessions = page.get('sessions', 0)
        rps = page.get('revenue_per_session', 0)

        # Minimum sessions threshold (need enough data)
        if sessions < 10:
            return 'INSUFFICIENT_DATA'

        # KILL criteria
        if br > 65 or cr < (account_avg_cr * 0.5) or (sessions > 100 and cr < 1.0):
            return 'KILL'

        # Ultra-short sessions indicator (potential technical issue)
        if page.get('avgSessionDuration', 0) < 10:
            return 'KILL'

        # FIX criteria
        if (50 <= br <= 65) or (account_avg_cr * 0.5 <= cr < account_avg_cr) or (rps < account_avg_rps * 0.5):
            return 'FIX'

        # KEEP criteria
        if cr >= account_avg_cr or rps >= account_avg_rps:
            if br < 50:
                return 'KEEP'

        # Default to WATCH if none of above
        return 'WATCH'

    def _calculate_overall_score(self, page: Dict[str, Any]) -> float:
        """
        Calculate overall landing page score (0-100).

        Args:
            page: Page metrics

        Returns:
            float: Score from 0 to 100
        """
        # Bounce rate score (lower bounce = higher score)
        bounce_score = max(0, 100 - page.get('bounce_rate_pct', 100))

        # Conversion rate score (higher CR = higher score)
        # Normalize to account average (assume 4% typical account avg)
        typical_cr = 4.0
        conversion_score = min(100, (page.get('conversion_rate_pct', 0) / typical_cr) * 100)

        # Session duration score (higher duration = higher engagement)
        typical_duration = 90
        duration_score = min(100, (page.get('avg_session_duration_sec', 0) / typical_duration) * 100)

        # Revenue score
        typical_rps = 45
        revenue_score = min(100, (page.get('revenue_per_session', 0) / typical_rps) * 100)

        # Weighted average
        score = (
            (bounce_score * 0.25) +
            (conversion_score * 0.35) +
            (duration_score * 0.15) +
            (revenue_score * 0.25)
        )

        return round(score, 1)

    def get_device_split(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> List[Dict[str, Any]]:
        """
        Get landing page metrics split by device (mobile vs. desktop).

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on

        Returns:
            List[Dict]: Metrics by landing page and device
        """
        # Build filter for session source
        dimension_filter = {
            "filter": {
                "fieldName": "sessionSource",
                "stringFilter": {
                    "matchType": "EXACT",
                    "value": source_filter
                }
            }
        }

        response = self.ga4_client.run_report(
            property_id=property_id,
            dimensions=['landingPage', 'deviceCategory'],
            metrics=['sessions', 'conversions', 'bounceRate', 'avgSessionDuration', 'totalRevenue'],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        return self.ga4_client.parse_report(response)

    def get_funnel_analysis(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> Dict[str, Any]:
        """
        Get conversion funnel analysis for Meta Ads traffic.

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on

        Returns:
            Dict: Funnel metrics at each stage
        """
        # Build filter for session source
        dimension_filter = {
            "filter": {
                "fieldName": "sessionSource",
                "stringFilter": {
                    "matchType": "EXACT",
                    "value": source_filter
                }
            }
        }

        response = self.ga4_client.run_report(
            property_id=property_id,
            dimensions=['eventName'],
            metrics=['eventCount', 'eventValue'],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        funnel_data = self.ga4_client.parse_report(response)

        # Organize by funnel stage
        funnel_stages = {
            'page_view': 0,
            'add_to_cart': 0,
            'begin_checkout': 0,
            'purchase': 0
        }

        for event in funnel_data:
            event_name = event.get('eventName', '').lower()
            if 'page_view' in event_name:
                funnel_stages['page_view'] += event.get('eventCount', 0)
            elif 'add_to_cart' in event_name:
                funnel_stages['add_to_cart'] += event.get('eventCount', 0)
            elif 'begin_checkout' in event_name:
                funnel_stages['begin_checkout'] += event.get('eventCount', 0)
            elif 'purchase' in event_name:
                funnel_stages['purchase'] += event.get('eventCount', 0)

        # Calculate drop-off rates
        base_count = max(funnel_stages['page_view'], 1)

        return {
            'funnel_stages': funnel_stages,
            'dropoff_rates': {
                'page_view_to_cart': (
                    (base_count - funnel_stages['add_to_cart']) / base_count * 100
                ) if base_count > 0 else 0,
                'cart_to_checkout': (
                    (funnel_stages['add_to_cart'] - funnel_stages['begin_checkout']) / max(funnel_stages['add_to_cart'], 1) * 100
                ),
                'checkout_to_purchase': (
                    (funnel_stages['begin_checkout'] - funnel_stages['purchase']) / max(funnel_stages['begin_checkout'], 1) * 100
                )
            }
        }


if __name__ == "__main__":
    import argparse
    from ga4_api import GA4APIClient

    parser = argparse.ArgumentParser(description='GA4 Landing Page Analysis Tool')
    parser.add_argument('--service-account', required=True, help='Path to service account JSON')
    parser.add_argument('--property-id', required=True, help='GA4 property ID')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--analysis', default='landing_pages',
                       choices=['landing_pages', 'device_split', 'funnel'],
                       help='Analysis type')

    args = parser.parse_args()

    ga4_client = GA4APIClient(args.service_account)
    analyzer = LandingPageAnalyzer(ga4_client)
    date_range = {'start_date': args.start_date, 'end_date': args.end_date}

    if args.analysis == 'landing_pages':
        result = analyzer.get_landing_page_metrics(args.property_id, date_range)
    elif args.analysis == 'device_split':
        result = analyzer.get_device_split(args.property_id, date_range)
    elif args.analysis == 'funnel':
        result = analyzer.get_funnel_analysis(args.property_id, date_range)

    print(json.dumps(result, indent=2))

"""
GA4 Data API Client for Google Ads data pull

Handles 8 GA4 queries per cycle, filtering to utm_source=google traffic:
1. Session overview (Google traffic)
2. Campaign-level sessions
3. Ad-level sessions
4. Landing page performance
5. Conversion funnel events
6. Device breakdown
7. Geographic breakdown
8. Session paths & engagement
"""

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    Dimension,
    Metric,
    DateRange,
    FilterExpression,
    StringFilter,
    Filter,
)
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class GA4DataClient:
    """
    GA4 Data API client for Google Ads traffic analysis.

    Usage:
        client = GA4DataClient(
            credentials_json="/path/to/service_account.json",
            ga4_property_id="123456789"
        )

        sessions = client.get_session_overview(
            start_date="2026-02-08",
            end_date="2026-02-14"
        )
    """

    def __init__(self, credentials_json: str, ga4_property_id: str):
        """
        Initialize GA4 Data API client.

        Args:
            credentials_json: Path to service account JSON key
            ga4_property_id: GA4 property ID (numeric)
        """
        self.client = BetaAnalyticsDataClient.from_service_account_file(credentials_json)
        self.property_id = ga4_property_id

    def _build_request(
        self,
        start_date: str,
        end_date: str,
        dimensions: List[str],
        metrics: List[str],
        filter_expression=None,
    ) -> RunReportRequest:
        """
        Build a GA4 Data API request.

        Args:
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            dimensions: List of dimension names
            metrics: List of metric names
            filter_expression: Optional filter

        Returns:
            RunReportRequest object
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
            limit=100000,
        )

        if filter_expression:
            request.dimension_filter = filter_expression

        return request

    def _execute_request(self, request: RunReportRequest) -> List[Dict[str, Any]]:
        """Execute a GA4 Data API request and return results."""
        response = self.client.run_report(request)

        results = []
        for row in response.rows:
            row_dict = {}

            # Dimensions
            for i, dimension in enumerate(response.dimension_headers):
                row_dict[dimension.name] = row.dimension_values[i].value

            # Metrics
            for i, metric in enumerate(response.metric_headers):
                try:
                    row_dict[metric.name] = float(row.metric_values[i].value)
                except ValueError:
                    row_dict[metric.name] = row.metric_values[i].value

            results.append(row_dict)

        logger.info(f"GA4 query executed. Rows returned: {len(results)}")
        return results

    # Query 1: Session Overview (Google traffic)
    def get_session_overview(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 1: Session overview for Google Ads traffic only.

        Returns: Total sessions, conversions, revenue
        """
        # Filter to utm_source=google
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=[],
            metrics=["sessions", "conversions", "conversionValue"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

    # Query 2: Campaign-Level Sessions
    def get_campaign_sessions(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 2: Campaign-level GA4 data joined via UTM campaign.

        Returns: Sessions, conversions, revenue per campaign
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["sessionCampaignId"],
            metrics=["sessions", "conversions", "conversionValue", "bounceRate", "avgSessionDuration"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

    # Query 3: Ad-Level Sessions
    def get_ad_sessions(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 3: Ad-level GA4 data joined via utm_content (sessionManualAdContent).

        Returns: Sessions, conversions, revenue per ad
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["sessionManualAdContent"],
            metrics=["sessions", "conversions", "conversionValue"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

    # Query 4: Landing Page Performance
    def get_landing_page_performance(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 4: Landing page performance for Google Ads traffic.

        Returns: Per-URL metrics including bounce rate, duration, conversions
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["landingPage"],
            metrics=["sessions", "bounceRate", "avgSessionDuration", "conversions", "conversionValue"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

    # Query 5: Conversion Funnel Events
    def get_conversion_funnel(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 5: Conversion funnel event breakdown.

        Returns: Event counts for page_view, add_to_cart, begin_checkout, purchase
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["eventName"],
            metrics=["eventCount", "eventValue"],
            filter_expression=source_filter,
        )

        results = self._execute_request(request)

        # Filter to funnel events only
        funnel_events = ["page_view", "add_to_cart", "begin_checkout", "purchase"]
        return [r for r in results if r.get("eventName") in funnel_events]

    # Query 6: Device Breakdown
    def get_device_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 6: Device category breakdown for Google Ads traffic.

        Returns: Desktop, mobile, tablet performance
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["deviceCategory"],
            metrics=["sessions", "conversions", "conversionValue"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

    # Query 7: Geographic Breakdown
    def get_geographic_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 7: Country and region/state breakdown for Google Ads traffic.

        Returns: Geographic performance with sessions, conversions, revenue
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["country", "region"],
            metrics=["sessions", "conversions", "conversionValue"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

    # Query 8: Session Paths & Engagement
    def get_session_paths(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 8: Session paths and engagement metrics.

        Returns: Page paths with session engagement metrics
        """
        source_filter = FilterExpression(
            filter=Filter(
                field_name="sessionSource",
                string_filter=StringFilter(match_type="EXACT", value="google"),
            )
        )

        request = self._build_request(
            start_date=start_date,
            end_date=end_date,
            dimensions=["pagePath", "sessionManualAdContent"],
            metrics=["engagedSessions", "avgSessionDuration", "screenPageViews"],
            filter_expression=source_filter,
        )

        return self._execute_request(request)

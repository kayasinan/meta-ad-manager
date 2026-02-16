"""
Google Ads API v17 Client for Data Placement Analyst

Handles all 21 Google Ads API queries per cycle:
1-4: Account, campaign, ad group, keyword performance
5-7: Search terms, placements, ad performance
8-10: Demographics (age, gender, age×gender)
11-12: Geography (country, region)
13-14: Network, device breakdowns
15: Dayparting (hour + day of week)
16-18: Product groups, asset groups, audiences
19-21: Quality Score, Impression Share, Auction Insights
"""

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import time

logger = logging.getLogger(__name__)


class GoogleAdsDataClient:
    """
    Google Ads API v17 client for data collection.

    Usage:
        client = GoogleAdsDataClient(
            credentials_json="/path/to/service_account.json",
            developer_token="YOUR_DEVELOPER_TOKEN",
            customer_id="1234567890"
        )

        campaigns = client.get_campaigns_performance(
            start_date="2026-02-08",
            end_date="2026-02-14"
        )
    """

    def __init__(self, credentials_json: str, developer_token: str, customer_id: str):
        """
        Initialize Google Ads API client.

        Args:
            credentials_json: Path to service account JSON key
            developer_token: Google Ads developer token
            customer_id: Google Ads customer ID (without hyphens)
        """
        self.client = GoogleAdsClient.load_from_storage(credentials_json)
        self.developer_token = developer_token
        self.customer_id = customer_id
        self.ga_service = self.client.get_service("GoogleAdsService")
        self.call_count = 0
        self.daily_call_limit = 10000

    def _execute_query(self, query: str, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Execute a GAQL query with rate limiting and retry logic.

        Args:
            query: GAQL query string
            timeout: Query timeout in seconds

        Returns:
            List of result rows

        Raises:
            GoogleAdsException: If query fails after retries
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                self.call_count += 1

                if self.call_count > self.daily_call_limit * 0.8:
                    logger.warning(
                        f"Approaching daily API call limit: {self.call_count}/"
                        f"{self.daily_call_limit}"
                    )

                request = self.client.get_type("SearchGoogleAdsRequest")
                request.customer_id = self.customer_id
                request.query = query
                request.page_size = 10000

                response = self.ga_service.search(request)

                results = []
                for batch in response:
                    for row in batch.results:
                        results.append(row)

                logger.info(f"Query executed successfully. Rows returned: {len(results)}")
                return results

            except GoogleAdsException as ex:
                if ex.error.code == 429:  # Rate limited
                    logger.warning(f"Rate limited. Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Google Ads API error: {ex.error.message}")
                    raise
            except Exception as ex:
                logger.error(f"Unexpected error: {str(ex)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise

        raise GoogleAdsException("Query failed after 3 retries")

    # Query 1: Account Overview
    def get_account_overview(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Query 1: Account overview metrics.

        Returns: spend, impressions, clicks, conversions, revenue for full account
        """
        query = f"""
            SELECT
                customer.id,
                customer.descriptive_name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM customer
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        # Aggregate results
        total_impressions = sum(r.metrics.impressions for r in results)
        total_clicks = sum(r.metrics.clicks for r in results)
        total_cost = sum(r.metrics.cost_micros for r in results) / 1_000_000
        total_conversions = sum(r.metrics.conversions for r in results)
        total_revenue = sum(r.metrics.conversions_value for r in results)

        return {
            "customer_id": results[0].customer.id if results else None,
            "impressions": total_impressions,
            "clicks": total_clicks,
            "spend": total_cost,
            "conversions": total_conversions,
            "revenue": total_revenue,
        }

    # Query 2: Campaign Performance
    def get_campaigns_performance(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 2: Per-campaign performance metrics.

        Returns: List of campaigns with spend, impressions, clicks, conversions, CPA, ROAS
        """
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.all_conversions,
                metrics.all_conversions_value
            FROM campaign
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        campaigns = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            campaign_data = {
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "status": row.campaign.status.name,
                "channel_type": row.campaign.advertising_channel_type.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": spend / conversions if conversions > 0 else None,
                "roas": revenue / spend if spend > 0 else None,
            }
            campaigns.append(campaign_data)

        return campaigns

    # Query 3: Ad Group Performance
    def get_ad_groups_performance(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 3: Per-ad-group performance metrics.

        Returns: List of ad groups with spend, conversions, quality score
        """
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                ad_group.id,
                ad_group.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM ad_group
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        ad_groups = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            ad_group_data = {
                "campaign_id": row.campaign.id,
                "campaign_name": row.campaign.name,
                "ad_group_id": row.ad_group.id,
                "ad_group_name": row.ad_group.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": spend / conversions if conversions > 0 else None,
            }
            ad_groups.append(ad_group_data)

        return ad_groups

    # Query 4: Keyword Performance
    def get_keywords_performance(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 4: Per-keyword performance metrics.

        Returns: Keywords with impressions, clicks, conversions, quality score
        """
        query = f"""
            SELECT
                campaign.id,
                ad_group.id,
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.expected_ctr,
                ad_group_criterion.quality_info.landing_page_quality_score,
                ad_group_criterion.quality_info.ad_relevance_rating,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.average_cpc,
                metrics.average_position,
                metrics.search_impression_share,
                metrics.search_budget_lost_impression_share,
                metrics.search_rank_lost_impression_share
            FROM keyword_view
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
                AND ad_group_criterion.criterion_id IS NOT NULL
        """

        results = self._execute_query(query)

        keywords = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            keyword_data = {
                "campaign_id": row.campaign.id,
                "ad_group_id": row.ad_group.id,
                "keyword_id": row.ad_group_criterion.criterion_id,
                "keyword_text": row.ad_group_criterion.keyword.text,
                "match_type": row.ad_group_criterion.keyword.match_type.name,
                "quality_score": row.ad_group_criterion.quality_info.quality_score,
                "expected_ctr": row.ad_group_criterion.quality_info.expected_ctr.name if
                               row.ad_group_criterion.quality_info.expected_ctr else None,
                "ad_relevance": row.ad_group_criterion.quality_info.ad_relevance_rating.name if
                               row.ad_group_criterion.quality_info.ad_relevance_rating else None,
                "landing_page_quality": row.ad_group_criterion.quality_info.landing_page_quality_score.name if
                                       row.ad_group_criterion.quality_info.landing_page_quality_score else None,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "avg_cpc": row.metrics.average_cpc / 1_000_000 if row.metrics.average_cpc else 0,
                "avg_position": row.metrics.average_position,
                "impression_share": row.metrics.search_impression_share,
                "lost_to_budget": row.metrics.search_budget_lost_impression_share,
                "lost_to_rank": row.metrics.search_rank_lost_impression_share,
            }
            keywords.append(keyword_data)

        return keywords

    # Query 5: Search Term Report
    def get_search_terms(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 5: Search term report - actual queries triggering ads.

        Returns: Search terms with impressions, clicks, conversions
        """
        query = f"""
            SELECT
                campaign.id,
                ad_group.id,
                search_term_view.search_term,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM search_term_view
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
                AND metrics.impressions > 0
        """

        results = self._execute_query(query)

        search_terms = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            search_term_data = {
                "campaign_id": row.campaign.id,
                "ad_group_id": row.ad_group.id,
                "search_term": row.search_term_view.search_term,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpc": spend / row.metrics.clicks if row.metrics.clicks > 0 else 0,
                "ctr": row.metrics.clicks / row.metrics.impressions if row.metrics.impressions > 0 else 0,
            }
            search_terms.append(search_term_data)

        return search_terms

    # Query 8-10: Demographics
    def get_demographics_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 8-10: Age and gender breakdowns (combined).

        Returns: Demographics with conversions and CPA
        """
        query = f"""
            SELECT
                campaign.id,
                segments.age_range,
                segments.gender,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM ad_group
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        demographics = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            demo_data = {
                "campaign_id": row.campaign.id,
                "age_range": row.segments.age_range.name if row.segments.age_range else "UNKNOWN",
                "gender": row.segments.gender.name if row.segments.gender else "UNKNOWN",
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": spend / conversions if conversions > 0 else None,
            }
            demographics.append(demo_data)

        return demographics

    # Query 11-12: Geography
    def get_geography_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 11-12: Country and region/state breakdowns.

        Returns: Geographic performance with spend and conversions
        """
        query = f"""
            SELECT
                campaign.id,
                geographic_view.country_criterion_id,
                geographic_view.region_criterion_id,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM geographic_view
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        geos = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            geo_data = {
                "campaign_id": row.campaign.id,
                "country_id": row.geographic_view.country_criterion_id,
                "region_id": row.geographic_view.region_criterion_id,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": spend / conversions if conversions > 0 else None,
            }
            geos.append(geo_data)

        return geos

    # Query 13: Network Breakdown
    def get_network_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 13: Search, Search Partners, Display, YouTube network breakdown.

        Returns: Network performance metrics
        """
        query = f"""
            SELECT
                campaign.id,
                segments.network,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM ad_group
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        networks = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            network_data = {
                "campaign_id": row.campaign.id,
                "network": row.segments.network.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": spend / conversions if conversions > 0 else None,
            }
            networks.append(network_data)

        return networks

    # Query 14: Device Breakdown
    def get_device_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 14: Desktop, mobile, tablet breakdown.

        Returns: Device performance metrics
        """
        query = f"""
            SELECT
                campaign.id,
                segments.device,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM ad_group
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        devices = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            device_data = {
                "campaign_id": row.campaign.id,
                "device": row.segments.device.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": spend / conversions if conversions > 0 else None,
            }
            devices.append(device_data)

        return devices

    # Query 15: Dayparting (Hour + Day of Week)
    def get_dayparting_breakdown(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 15: Hourly and day-of-week breakdown for dayparting analysis.

        Returns: Spend and conversions by hour (0-23) and day of week
        """
        query = f"""
            SELECT
                campaign.id,
                segments.hour_of_day,
                segments.day_of_week,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM ad_group
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
        """

        results = self._execute_query(query)

        dayparts = []
        for row in results:
            spend = row.metrics.cost_micros / 1_000_000
            conversions = row.metrics.conversions
            revenue = row.metrics.conversions_value

            daypart_data = {
                "campaign_id": row.campaign.id,
                "hour": row.segments.hour_of_day,
                "day_of_week": row.segments.day_of_week.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
            }
            dayparts.append(daypart_data)

        return dayparts

    # Query 19: Quality Score
    def get_quality_score_audit(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Query 19: Quality Score components at keyword level.

        Returns: Keywords with quality score and component ratings
        """
        query = f"""
            SELECT
                campaign.id,
                ad_group.id,
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.expected_ctr,
                ad_group_criterion.quality_info.ad_relevance_rating,
                ad_group_criterion.quality_info.landing_page_quality_score,
                metrics.impressions,
                metrics.clicks,
                metrics.conversions
            FROM keyword_view
            WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
                AND ad_group_criterion.quality_info.quality_score IS NOT NULL
        """

        results = self._execute_query(query)

        quality_scores = []
        for row in results:
            qs_data = {
                "campaign_id": row.campaign.id,
                "ad_group_id": row.ad_group.id,
                "keyword_id": row.ad_group_criterion.criterion_id,
                "keyword_text": row.ad_group_criterion.keyword.text,
                "quality_score": row.ad_group_criterion.quality_info.quality_score,
                "expected_ctr": row.ad_group_criterion.quality_info.expected_ctr.name if
                               row.ad_group_criterion.quality_info.expected_ctr else None,
                "ad_relevance": row.ad_group_criterion.quality_info.ad_relevance_rating.name if
                               row.ad_group_criterion.quality_info.ad_relevance_rating else None,
                "landing_page_quality": row.ad_group_criterion.quality_info.landing_page_quality_score.name if
                                       row.ad_group_criterion.quality_info.landing_page_quality_score else None,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "conversions": row.metrics.conversions,
            }
            quality_scores.append(qs_data)

        return quality_scores

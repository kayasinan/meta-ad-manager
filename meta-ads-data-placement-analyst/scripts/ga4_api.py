"""
GA4 Data API helper library for accessing Google Analytics 4 data.
Uses service account authentication for server-side API access.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

class GA4APIClient:
    """Client for GA4 Data API v1 operations."""

    API_URL = "https://analyticsdata.googleapis.com/v1beta"
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

    def __init__(self, service_account_path: str):
        """
        Initialize GA4 API client with service account credentials.

        Args:
            service_account_path (str): Path to service account JSON file

        Raises:
            FileNotFoundError: If service account file not found
            ValueError: If credentials are invalid
        """
        try:
            self.credentials = Credentials.from_service_account_file(
                service_account_path,
                scopes=self.SCOPES
            )
            self.access_token = None
            self._refresh_token()
        except FileNotFoundError:
            raise FileNotFoundError(f"Service account file not found: {service_account_path}")
        except Exception as e:
            raise ValueError(f"Failed to load service account credentials: {e}")

    def _refresh_token(self):
        """Refresh the access token."""
        request = Request()
        self.credentials.refresh(request)
        self.access_token = self.credentials.token

    def get_access_token(self, service_account_path: str) -> str:
        """
        Get access token from service account.

        Args:
            service_account_path (str): Path to service account JSON file

        Returns:
            str: Access token
        """
        self.__init__(service_account_path)
        return self.access_token

    def _ensure_token_valid(self):
        """Ensure access token is fresh."""
        if not self.credentials.valid:
            self._refresh_token()

    def run_report(
        self,
        property_id: str,
        dimensions: List[str],
        metrics: List[str],
        date_range: Dict[str, str],
        dimension_filter: Optional[Dict[str, Any]] = None,
        limit: int = 100000
    ) -> Dict[str, Any]:
        """
        Run a GA4 Data API report.

        Args:
            property_id (str): GA4 property ID (numeric)
            dimensions (List[str]): Dimension names (e.g., 'date', 'sessionCampaignId')
            metrics (List[str]): Metric names (e.g., 'sessions', 'conversions')
            date_range (Dict): {'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}
            dimension_filter (Dict): Filter criteria (optional)
            limit (int): Max rows per request (default 100000)

        Returns:
            Dict: Raw API response

        Raises:
            requests.RequestException: If API call fails
        """
        self._ensure_token_valid()

        url = f"{self.API_URL}/properties/{property_id}:runReport"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        request_body = {
            "dateRanges": [
                {
                    "startDate": date_range.get('start_date'),
                    "endDate": date_range.get('end_date')
                }
            ],
            "dimensions": [{"name": dim} for dim in dimensions],
            "metrics": [{"name": metric} for metric in metrics],
            "limit": str(limit)
        }

        # Add filter if provided
        if dimension_filter:
            request_body["dimensionFilter"] = dimension_filter

        try:
            response = requests.post(url, json=request_body, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"GA4 API report request failed: {e}")

    def parse_report(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse GA4 Data API response into flat records.

        Args:
            response (Dict): Raw API response from run_report

        Returns:
            List[Dict]: Parsed records with dimension and metric values

        Raises:
            KeyError: If response structure is unexpected
        """
        records = []

        if 'rows' not in response:
            return records

        dimension_headers = response.get('dimensionHeaders', [])
        metric_headers = response.get('metricHeaders', [])

        for row in response['rows']:
            record = {}

            # Parse dimensions
            if 'dimensions' in row:
                for i, value in enumerate(row['dimensions']):
                    if i < len(dimension_headers):
                        dim_name = dimension_headers[i].get('name')
                        record[dim_name] = value

            # Parse metrics
            if 'metricValues' in row:
                for i, value in enumerate(row['metricValues']):
                    if i < len(metric_headers):
                        metric_name = metric_headers[i].get('name')
                        # Try to convert to numeric
                        try:
                            record[metric_name] = float(value.get('value', 0))
                        except (ValueError, AttributeError):
                            record[metric_name] = value.get('value', 0)

            if record:
                records.append(record)

        return records

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
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on (default 'facebook')

        Returns:
            List[Dict]: Landing page metrics
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

        response = self.run_report(
            property_id=property_id,
            dimensions=[
                'landingPage',
                'deviceCategory'
            ],
            metrics=[
                'sessions',
                'conversions',
                'bounceRate',
                'avgSessionDuration',
                'totalRevenue'
            ],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        return self.parse_report(response)

    def get_campaign_metrics(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> List[Dict[str, Any]]:
        """
        Get campaign-level metrics filtered to paid social traffic.

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on

        Returns:
            List[Dict]: Campaign metrics
        """
        dimension_filter = {
            "filter": {
                "fieldName": "sessionSource",
                "stringFilter": {
                    "matchType": "EXACT",
                    "value": source_filter
                }
            }
        }

        response = self.run_report(
            property_id=property_id,
            dimensions=[
                'sessionCampaignId'
            ],
            metrics=[
                'sessions',
                'conversions',
                'bounceRate',
                'totalRevenue'
            ],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        return self.parse_report(response)

    def get_ad_metrics(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> List[Dict[str, Any]]:
        """
        Get ad-level metrics (via utm_content) filtered to paid social traffic.

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on

        Returns:
            List[Dict]: Ad metrics
        """
        dimension_filter = {
            "filter": {
                "fieldName": "sessionSource",
                "stringFilter": {
                    "matchType": "EXACT",
                    "value": source_filter
                }
            }
        }

        response = self.run_report(
            property_id=property_id,
            dimensions=[
                'sessionManualAdContent'  # This is utm_content
            ],
            metrics=[
                'sessions',
                'conversions',
                'totalRevenue'
            ],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        return self.parse_report(response)

    def get_device_metrics(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> List[Dict[str, Any]]:
        """
        Get device breakdown metrics.

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on

        Returns:
            List[Dict]: Device metrics
        """
        dimension_filter = {
            "filter": {
                "fieldName": "sessionSource",
                "stringFilter": {
                    "matchType": "EXACT",
                    "value": source_filter
                }
            }
        }

        response = self.run_report(
            property_id=property_id,
            dimensions=[
                'deviceCategory'
            ],
            metrics=[
                'sessions',
                'conversions',
                'totalRevenue'
            ],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        return self.parse_report(response)

    def get_geographic_metrics(
        self,
        property_id: str,
        date_range: Dict[str, str],
        source_filter: str = "facebook"
    ) -> List[Dict[str, Any]]:
        """
        Get geographic breakdown metrics (country, region).

        Args:
            property_id (str): GA4 property ID
            date_range (Dict): Date range for query
            source_filter (str): Session source to filter on

        Returns:
            List[Dict]: Geographic metrics
        """
        dimension_filter = {
            "filter": {
                "fieldName": "sessionSource",
                "stringFilter": {
                    "matchType": "EXACT",
                    "value": source_filter
                }
            }
        }

        response = self.run_report(
            property_id=property_id,
            dimensions=[
                'country',
                'region'
            ],
            metrics=[
                'sessions',
                'conversions',
                'totalRevenue'
            ],
            date_range=date_range,
            dimension_filter=dimension_filter
        )

        return self.parse_report(response)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='GA4 Data API Helper')
    parser.add_argument('--service-account', required=True, help='Path to service account JSON')
    parser.add_argument('--property-id', required=True, help='GA4 property ID')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--report', default='campaigns', choices=['campaigns', 'ads', 'landing_pages', 'device', 'geographic'],
                       help='Report type')

    args = parser.parse_args()

    client = GA4APIClient(args.service_account)
    date_range = {'start_date': args.start_date, 'end_date': args.end_date}

    if args.report == 'campaigns':
        result = client.get_campaign_metrics(args.property_id, date_range)
    elif args.report == 'ads':
        result = client.get_ad_metrics(args.property_id, date_range)
    elif args.report == 'landing_pages':
        result = client.get_landing_page_metrics(args.property_id, date_range)
    elif args.report == 'device':
        result = client.get_device_metrics(args.property_id, date_range)
    elif args.report == 'geographic':
        result = client.get_geographic_metrics(args.property_id, date_range)

    print(json.dumps(result, indent=2))

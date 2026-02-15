"""
Meta Ads API helper library for accessing campaign, ad set, and ad performance data.
Handles rate limiting, pagination, and error handling.
"""

import requests
import time
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

class MetaAPIClient:
    """Client for Meta Ads API v21.0 operations."""

    BASE_URL = "https://graph.facebook.com/v21.0"
    RATE_LIMIT_CALLS_PER_HOUR = 200
    RATE_LIMIT_SLEEP = 0.3  # seconds between calls

    def __init__(self, access_token: str):
        """
        Initialize Meta API client.

        Args:
            access_token (str): Valid Meta API access token

        Raises:
            ValueError: If access token is empty
        """
        if not access_token:
            raise ValueError("Access token cannot be empty")
        self.access_token = access_token
        self.call_count = 0
        self.last_call_time = None

    def load_token(self, creds_path: str) -> str:
        """
        Load access token from credentials file.

        Args:
            creds_path (str): Path to credentials JSON file
                Expected format: {"access_token": "..."}

        Returns:
            str: Access token

        Raises:
            FileNotFoundError: If credentials file not found
            KeyError: If 'access_token' key missing
        """
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            token = creds.get('access_token')
            if not token:
                raise KeyError("'access_token' key not found in credentials file")
            self.access_token = token
            return token
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in credentials file: {e}")

    def _apply_rate_limit(self):
        """Apply rate limiting between API calls."""
        time.sleep(self.RATE_LIMIT_SLEEP)
        self.call_count += 1
        self.last_call_time = time.time()

    def _handle_retry(self, response: requests.Response, max_retries: int = 3) -> Optional[requests.Response]:
        """
        Handle rate limit retries with exponential backoff.

        Args:
            response: Response object
            max_retries (int): Maximum number of retries

        Returns:
            requests.Response: The response after retry or original if not retriable
        """
        if response.status_code == 429:  # Too Many Requests
            for attempt in range(max_retries):
                wait_time = 60 * (attempt + 1)  # 60s, 120s, 180s
                print(f"Rate limited (429). Waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                # Re-attempt the request
                return response  # Caller should retry the request
        return response

    def get_insights(
        self,
        account_id: str,
        level: str = "account",
        fields: List[str] = None,
        breakdowns: List[str] = None,
        date_range: Dict[str, str] = None,
        filtering: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get insights data from Meta Ads API.

        Args:
            account_id (str): Meta ad account ID (with or without 'act_' prefix)
            level (str): 'account', 'campaign', 'adset', or 'ad'
            fields (List[str]): Fields to retrieve
            breakdowns (List[str]): Breakdown dimensions
            date_range (Dict): {'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}
            filtering (List[Dict]): Filter criteria

        Returns:
            List[Dict]: Insights data, paginated

        Raises:
            requests.RequestException: If API call fails
        """
        if fields is None:
            fields = [
                'impressions', 'clicks', 'spend', 'actions',
                'action_values', 'cpa', 'roas', 'cpm', 'cpc', 'ctr', 'frequency'
            ]

        if breakdowns is None:
            breakdowns = []

        # Format account ID
        if not account_id.startswith('act_'):
            account_id = f"act_{account_id}"

        # Build endpoint
        endpoint = f"{self.BASE_URL}/{account_id}/insights"

        params = {
            'access_token': self.access_token,
            'fields': ','.join(fields),
            'level': level,
        }

        if breakdowns:
            params['breakdowns'] = ','.join(breakdowns)

        if date_range:
            params['time_range'] = json.dumps({
                'since': date_range.get('start_date'),
                'until': date_range.get('end_date')
            })

        if filtering:
            params['filtering'] = json.dumps(filtering)

        params['limit'] = 500  # Max results per page

        all_data = []
        page_cursor = None

        try:
            while True:
                if page_cursor:
                    params['after'] = page_cursor

                self._apply_rate_limit()
                response = requests.get(endpoint, params=params, timeout=30)

                # Handle rate limiting
                if response.status_code == 429:
                    self._handle_retry(response)
                    continue  # Retry

                response.raise_for_status()
                data = response.json()

                if 'data' in data:
                    all_data.extend(data['data'])

                # Check for pagination
                if 'paging' in data and 'cursors' in data['paging']:
                    page_cursor = data['paging']['cursors'].get('after')
                    if not page_cursor:
                        break  # No more pages
                else:
                    break  # No paging info

            return all_data

        except requests.RequestException as e:
            raise requests.RequestException(f"Meta API insights request failed: {e}")

    def get_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all campaigns for the account.

        Args:
            account_id (str): Meta ad account ID

        Returns:
            List[Dict]: Campaign objects
        """
        if not account_id.startswith('act_'):
            account_id = f"act_{account_id}"

        endpoint = f"{self.BASE_URL}/{account_id}/campaigns"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,status,objective,created_time,updated_time',
            'limit': 500
        }

        all_campaigns = []
        page_cursor = None

        try:
            while True:
                if page_cursor:
                    params['after'] = page_cursor

                self._apply_rate_limit()
                response = requests.get(endpoint, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if 'data' in data:
                    all_campaigns.extend(data['data'])

                if 'paging' in data and 'cursors' in data['paging']:
                    page_cursor = data['paging']['cursors'].get('after')
                    if not page_cursor:
                        break
                else:
                    break

            return all_campaigns

        except requests.RequestException as e:
            raise requests.RequestException(f"Meta API campaigns request failed: {e}")

    def get_adsets(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all ad sets for the account.

        Args:
            account_id (str): Meta ad account ID

        Returns:
            List[Dict]: Ad set objects
        """
        if not account_id.startswith('act_'):
            account_id = f"act_{account_id}"

        endpoint = f"{self.BASE_URL}/{account_id}/adsets"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,campaign_id,status,targeting,daily_budget,lifetime_budget,created_time',
            'limit': 500
        }

        all_adsets = []
        page_cursor = None

        try:
            while True:
                if page_cursor:
                    params['after'] = page_cursor

                self._apply_rate_limit()
                response = requests.get(endpoint, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if 'data' in data:
                    all_adsets.extend(data['data'])

                if 'paging' in data and 'cursors' in data['paging']:
                    page_cursor = data['paging']['cursors'].get('after')
                    if not page_cursor:
                        break
                else:
                    break

            return all_adsets

        except requests.RequestException as e:
            raise requests.RequestException(f"Meta API ad sets request failed: {e}")

    def get_ads_with_creative(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all ads with creative details for the account.

        Args:
            account_id (str): Meta ad account ID

        Returns:
            List[Dict]: Ad objects with creative information
        """
        if not account_id.startswith('act_'):
            account_id = f"act_{account_id}"

        endpoint = f"{self.BASE_URL}/{account_id}/ads"
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,adset_id,status,created_time,updated_time,creative,object_story_spec',
            'limit': 500
        }

        all_ads = []
        page_cursor = None

        try:
            while True:
                if page_cursor:
                    params['after'] = page_cursor

                self._apply_rate_limit()
                response = requests.get(endpoint, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if 'data' in data:
                    all_ads.extend(data['data'])

                if 'paging' in data and 'cursors' in data['paging']:
                    page_cursor = data['paging']['cursors'].get('after')
                    if not page_cursor:
                        break
                else:
                    break

            return all_ads

        except requests.RequestException as e:
            raise requests.RequestException(f"Meta API ads request failed: {e}")


def load_token(creds_path: str) -> str:
    """
    Load access token from credentials file.

    Args:
        creds_path (str): Path to credentials JSON file

    Returns:
        str: Access token
    """
    client = MetaAPIClient("temp")
    return client.load_token(creds_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Meta Ads API Helper')
    parser.add_argument('--token', required=True, help='Meta API access token')
    parser.add_argument('--account-id', required=True, help='Meta ad account ID')
    parser.add_argument('--operation', required=True, choices=['campaigns', 'adsets', 'ads', 'insights'],
                       help='Operation to perform')
    parser.add_argument('--level', default='account', help='Insights level (account, campaign, adset, ad)')
    parser.add_argument('--breakdown', help='Breakdown dimension (comma-separated)')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')

    args = parser.parse_args()

    client = MetaAPIClient(args.token)

    if args.operation == 'campaigns':
        result = client.get_campaigns(args.account_id)
    elif args.operation == 'adsets':
        result = client.get_adsets(args.account_id)
    elif args.operation == 'ads':
        result = client.get_ads_with_creative(args.account_id)
    elif args.operation == 'insights':
        date_range = None
        if args.start_date and args.end_date:
            date_range = {'start_date': args.start_date, 'end_date': args.end_date}
        breakdowns = args.breakdown.split(',') if args.breakdown else []
        result = client.get_insights(args.account_id, level=args.level, breakdowns=breakdowns, date_range=date_range)

    print(json.dumps(result, indent=2))

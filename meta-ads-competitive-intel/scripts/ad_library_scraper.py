"""
Meta Ad Library API helper for accessing competitor ads.
Searches and retrieves ads from the Meta Ads Archive.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode

class AdLibraryScraper:
    """Scraper for Meta Ad Library data."""

    API_BASE = "https://graph.facebook.com/v21.0"
    AD_ARCHIVE_ENDPOINT = "/ads_archive"

    def __init__(self, access_token: str):
        """
        Initialize Ad Library scraper.

        Args:
            access_token (str): Valid Meta API access token with ads_archive access

        Raises:
            ValueError: If access token is empty
        """
        if not access_token:
            raise ValueError("Access token cannot be empty")
        self.access_token = access_token

    def search_ads(
        self,
        search_terms: List[str],
        ad_type: str = "ALL",
        country: str = "US",
        media_type: str = "all",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for ads in Meta Ad Library.

        Args:
            search_terms (List[str]): Advertiser names or keywords to search
            ad_type (str): Type of ad to search ('POLITICAL_AND_ISSUE_ADS', 'HOUSING_ADS', 'CREDIT_ADS', 'EMPLOYMENT_ADS', 'ALL')
            country (str): Country code (US, GB, CA, etc.)
            media_type (str): 'all', 'image', 'video', 'carousel'
            limit (int): Max results per search

        Returns:
            List[Dict]: Ad objects with metadata

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.API_BASE}{self.AD_ARCHIVE_ENDPOINT}"

        all_ads = []

        try:
            for search_term in search_terms:
                params = {
                    'access_token': self.access_token,
                    'search_terms': search_term,
                    'ad_type': ad_type,
                    'country': country,
                    'media_type': media_type,
                    'limit': limit,
                    'fields': 'id,name,ad_creation_time,ad_status,ad_snapshot_url,images,videos,media_type,plaintext_preview,target_locations,target_genders,target_ages,adset_id,ad_set_id,platform'
                }

                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if 'data' in data:
                    for ad in data['data']:
                        # Add metadata
                        ad['search_term'] = search_term
                        ad['country'] = country
                        all_ads.append(ad)

                # Handle pagination
                while 'paging' in data and 'cursors' in data['paging']:
                    if 'after' not in data['paging']['cursors']:
                        break

                    params['after'] = data['paging']['cursors']['after']
                    response = requests.get(url, params=params, timeout=30)
                    response.raise_for_status()
                    data = response.json()

                    if 'data' in data:
                        for ad in data['data']:
                            ad['search_term'] = search_term
                            ad['country'] = country
                            all_ads.append(ad)

            return all_ads

        except requests.RequestException as e:
            raise requests.RequestException(f"Ad Library search failed: {e}")

    def get_ad_details(self, ad_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific ad.

        Args:
            ad_id (str): Facebook ad ID

        Returns:
            Dict: Detailed ad information
        """
        url = f"{self.API_BASE}/{ad_id}"

        params = {
            'access_token': self.access_token,
            'fields': 'id,name,ad_creation_time,ad_status,ad_snapshot_url,images,videos,media_type,plaintext_preview,target_locations,target_genders,target_ages,adset_id,platform,reach_estimate,impressions'
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to get ad details: {e}")

    def calculate_longevity(self, ad_creation_time: str, ad_end_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate ad longevity (how long it's been running).

        Args:
            ad_creation_time (str): ISO format datetime when ad was created
            ad_end_time (str): ISO format datetime when ad ended (None if still active)

        Returns:
            Dict: Longevity data with days running and status
        """
        try:
            creation_dt = datetime.fromisoformat(ad_creation_time.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Try parsing as timestamp
            try:
                creation_dt = datetime.fromtimestamp(int(ad_creation_time))
            except (ValueError, TypeError):
                return {'days_running': None, 'status': 'unknown_creation_time'}

        if ad_end_time:
            try:
                end_dt = datetime.fromisoformat(ad_end_time.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                end_dt = datetime.now()
        else:
            end_dt = datetime.now()

        days_running = (end_dt - creation_dt).days

        return {
            'days_running': days_running,
            'status': 'active' if not ad_end_time else 'ended',
            'created_date': creation_dt.isoformat(),
            'ended_date': end_dt.isoformat() if ad_end_time else None
        }

    def score_longevity(self, days_running: int) -> int:
        """
        Score ad longevity (0-10 scale).

        Args:
            days_running (int): Number of days ad has been running

        Returns:
            int: Longevity score 0-10
        """
        if days_running < 7:
            return 1
        elif days_running < 14:
            return 3
        elif days_running < 30:
            return 5
        elif days_running < 60:
            return 7
        elif days_running < 90:
            return 8
        else:
            return 9

    def analyze_competitor(
        self,
        competitor_name: str,
        country: str = "US"
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of a competitor's active ads.

        Args:
            competitor_name (str): Name of competitor advertiser
            country (str): Country code

        Returns:
            Dict: Competitor analysis with ads grouped by format and scored
        """
        # Search for competitor ads
        ads = self.search_ads([competitor_name], country=country)

        # Group by format
        by_format = {'image': [], 'video': [], 'carousel': [], 'other': []}
        by_status = {'active': [], 'ended': []}

        for ad in ads:
            media_type = ad.get('media_type', 'other').lower()
            if media_type in by_format:
                by_format[media_type].append(ad)
            else:
                by_format['other'].append(ad)

            # Calculate longevity
            longevity_data = self.calculate_longevity(
                ad.get('ad_creation_time'),
                ad.get('ad_end_time')
            )
            ad['longevity'] = longevity_data
            ad['longevity_score'] = self.score_longevity(longevity_data.get('days_running', 0))

            if longevity_data['status'] == 'active':
                by_status['active'].append(ad)
            else:
                by_status['ended'].append(ad)

        # Calculate statistics
        active_ads = by_status['active']
        avg_longevity = sum(a.get('longevity_score', 0) for a in active_ads) / len(active_ads) if active_ads else 0

        return {
            'competitor_name': competitor_name,
            'country': country,
            'total_ads': len(ads),
            'active_ads_count': len(by_status['active']),
            'format_distribution': {
                'image': len(by_format['image']),
                'video': len(by_format['video']),
                'carousel': len(by_format['carousel']),
                'other': len(by_format['other'])
            },
            'average_longevity_score': round(avg_longevity, 1),
            'top_ads_by_longevity': sorted(
                active_ads,
                key=lambda x: x.get('longevity_score', 0),
                reverse=True
            )[:10],
            'all_ads': ads
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Meta Ad Library Scraper')
    parser.add_argument('--token', required=True, help='Meta API access token')
    parser.add_argument('--competitor', required=True, help='Competitor name to search')
    parser.add_argument('--country', default='US', help='Country code (default: US)')
    parser.add_argument('--media-type', default='all', choices=['all', 'image', 'video', 'carousel'],
                       help='Media type filter')

    args = parser.parse_args()

    scraper = AdLibraryScraper(args.token)

    # Analyze competitor
    analysis = scraper.analyze_competitor(args.competitor, country=args.country)

    print(json.dumps({
        'competitor': analysis['competitor_name'],
        'country': analysis['country'],
        'total_ads': analysis['total_ads'],
        'active_ads': analysis['active_ads_count'],
        'format_distribution': analysis['format_distribution'],
        'avg_longevity_score': analysis['average_longevity_score'],
        'top_10_ads': [
            {
                'id': ad.get('id'),
                'name': ad.get('name'),
                'longevity_days': ad.get('longevity', {}).get('days_running'),
                'longevity_score': ad.get('longevity_score'),
                'media_type': ad.get('media_type'),
                'creation_date': ad.get('ad_creation_time')
            }
            for ad in analysis['top_ads_by_longevity']
        ]
    }, indent=2))

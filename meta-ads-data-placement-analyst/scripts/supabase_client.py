"""
Supabase REST API client for reading and writing data.
Handles authentication and common CRUD operations.
"""

import requests
import json
from typing import List, Dict, Any, Optional

class SupabaseClient:
    """Client for Supabase REST API operations."""

    def __init__(self, url: str, key: str):
        """
        Initialize Supabase client.

        Args:
            url (str): Supabase project URL (https://xxxxx.supabase.co)
            key (str): Supabase service role API key

        Raises:
            ValueError: If URL or key is empty
        """
        if not url or not key:
            raise ValueError("URL and key cannot be empty")

        self.url = url.rstrip('/')
        self.key = key
        self.base_url = f"{self.url}/rest/v1"

        self.headers = {
            'Authorization': f'Bearer {key}',
            'apikey': key,
            'Content-Type': 'application/json'
        }

    def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        SELECT query - retrieve rows from a table.

        Args:
            table (str): Table name
            filters (Dict): Filter criteria as key-value pairs
            columns (List): Specific columns to return

        Returns:
            List[Dict]: Query results

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"
        params = {}

        # Add column selection
        if columns:
            params['select'] = ','.join(columns)
        else:
            params['select'] = '*'

        # Add filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    params[f"{key}=eq.{value}"] = None
                elif isinstance(value, (int, float)):
                    params[f"{key}=eq.{value}"] = None
                elif isinstance(value, bool):
                    params[f"{key}=eq.{str(value).lower()}"] = None
                elif isinstance(value, list):
                    # For IN filters
                    val_str = ','.join(str(v) for v in value)
                    params[f"{key}=in.({val_str})"] = None

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json() if response.text else []
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase SELECT failed: {e}")

    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        INSERT a single row into a table.

        Args:
            table (str): Table name
            data (Dict): Row data

        Returns:
            Dict: Inserted row (if select='*' in response)

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"

        try:
            response = requests.post(
                url,
                json=data,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase INSERT failed: {e}")

    def insert_batch(
        self,
        table: str,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        INSERT multiple rows into a table.

        Args:
            table (str): Table name
            data (List[Dict]): List of rows to insert

        Returns:
            List[Dict]: Inserted rows

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"

        try:
            response = requests.post(
                url,
                json=data,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            return response.json() if response.text else []
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase INSERT BATCH failed: {e}")

    def update(
        self,
        table: str,
        filters: Dict[str, Any],
        data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        UPDATE rows matching filters.

        Args:
            table (str): Table name
            filters (Dict): Filter criteria
            data (Dict): Data to update

        Returns:
            List[Dict]: Updated rows

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"
        params = {}

        # Add filters to query string
        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    params[f"{key}=eq.{value}"] = None
                elif isinstance(value, (int, float)):
                    params[f"{key}=eq.{value}"] = None
                elif isinstance(value, bool):
                    params[f"{key}=eq.{str(value).lower()}"] = None

        try:
            response = requests.patch(
                url,
                json=data,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else []
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase UPDATE failed: {e}")

    def upsert(
        self,
        table: str,
        data: Dict[str, Any],
        on_conflict: str = "id"
    ) -> Dict[str, Any]:
        """
        UPSERT a row (insert if new, update if exists).

        Args:
            table (str): Table name
            data (Dict): Row data
            on_conflict (str): Column to use for conflict detection (default 'id')

        Returns:
            Dict: Inserted/updated row

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"

        headers = self.headers.copy()
        headers['Prefer'] = f'resolution=merge-duplicates,on_conflict={on_conflict}'

        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase UPSERT failed: {e}")

    def upsert_batch(
        self,
        table: str,
        data: List[Dict[str, Any]],
        on_conflict: str = "id"
    ) -> List[Dict[str, Any]]:
        """
        UPSERT multiple rows.

        Args:
            table (str): Table name
            data (List[Dict]): List of rows
            on_conflict (str): Column to use for conflict detection

        Returns:
            List[Dict]: Upserted rows

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"

        headers = self.headers.copy()
        headers['Prefer'] = f'resolution=merge-duplicates,on_conflict={on_conflict}'

        try:
            response = requests.post(
                url,
                json=data,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()
            return response.json() if response.text else []
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase UPSERT BATCH failed: {e}")

    def delete(
        self,
        table: str,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        DELETE rows matching filters.

        Args:
            table (str): Table name
            filters (Dict): Filter criteria

        Returns:
            List[Dict]: Deleted rows

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"
        params = {}

        # Add filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    params[f"{key}=eq.{value}"] = None
                elif isinstance(value, (int, float)):
                    params[f"{key}=eq.{value}"] = None

        try:
            response = requests.delete(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json() if response.text else []
        except requests.RequestException as e:
            raise requests.RequestException(f"Supabase DELETE failed: {e}")

    def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        COUNT rows in a table, optionally with filters.

        Args:
            table (str): Table name
            filters (Dict): Filter criteria

        Returns:
            int: Row count

        Raises:
            requests.RequestException: If API call fails
        """
        url = f"{self.base_url}/{table}"

        headers = self.headers.copy()
        headers['Prefer'] = 'count=exact'

        params = {'select': 'count', 'limit': '1'}

        # Add filters
        if filters:
            for key, value in filters.items():
                if isinstance(value, str):
                    params[f"{key}=eq.{value}"] = None
                elif isinstance(value, (int, float)):
                    params[f"{key}=eq.{value}"] = None

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            # Extract count from header
            return int(response.headers.get('content-range', '0-0/0').split('/')[-1])
        except (requests.RequestException, ValueError) as e:
            raise requests.RequestException(f"Supabase COUNT failed: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Supabase REST API Client')
    parser.add_argument('--url', required=True, help='Supabase project URL')
    parser.add_argument('--key', required=True, help='Supabase service role key')
    parser.add_argument('--table', required=True, help='Table name')
    parser.add_argument('--operation', required=True, choices=['select', 'insert', 'update', 'delete', 'count'],
                       help='Operation')
    parser.add_argument('--data', help='JSON data (for insert/update)')
    parser.add_argument('--filters', help='JSON filters')

    args = parser.parse_args()

    client = SupabaseClient(args.url, args.key)

    filters = json.loads(args.filters) if args.filters else None
    data = json.loads(args.data) if args.data else None

    if args.operation == 'select':
        result = client.select(args.table, filters=filters)
    elif args.operation == 'insert':
        result = client.insert(args.table, data)
    elif args.operation == 'update':
        result = client.update(args.table, filters, data)
    elif args.operation == 'delete':
        result = client.delete(args.table, filters)
    elif args.operation == 'count':
        result = client.count(args.table, filters=filters)

    print(json.dumps(result, indent=2))

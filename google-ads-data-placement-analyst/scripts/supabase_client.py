"""
Supabase Client for data storage and retrieval.

Handles all database operations for the Data Placement Analyst:
- Reading brand config, campaigns, ad groups, ads, keywords
- Writing daily metrics, tracking health, audiences, recommendations
- Writing cannibalization scores, search terms, alerts
"""

import supabase
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client for Google Ads analyst data operations.

    Usage:
        client = SupabaseClient(
            supabase_url="https://xxxxx.supabase.co",
            supabase_key="service_role_key"
        )

        brand = client.get_brand_config("brand_id_123")
        campaigns = client.get_campaigns("brand_id_123")
    """

    def __init__(self, supabase_url: str, supabase_key: str):
        """
        Initialize Supabase client.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Service role key (not anon key)
        """
        self.client = supabase.create_client(supabase_url, supabase_key)
        self.db = self.client

    # READ Operations

    def get_brand_config(self, brand_id: str) -> Dict[str, Any]:
        """Get brand configuration including API creds, targets, AR multiplier."""
        response = self.db.table("brand_config").select("*").eq("id", brand_id).single().execute()
        return response.data

    def get_campaigns(self, brand_id: str) -> List[Dict[str, Any]]:
        """Get all active campaigns for a brand."""
        response = (
            self.db.table("campaigns")
            .select("*")
            .eq("brand_id", brand_id)
            .eq("status", "ACTIVE")
            .execute()
        )
        return response.data

    def get_ad_groups(self, brand_id: str) -> List[Dict[str, Any]]:
        """Get all ad groups for a brand."""
        response = self.db.table("ad_groups").select("*").eq("brand_id", brand_id).execute()
        return response.data

    def get_ads(self, brand_id: str) -> List[Dict[str, Any]]:
        """Get all ads for a brand."""
        response = self.db.table("ads").select("*").eq("brand_id", brand_id).execute()
        return response.data

    def get_keywords(self, brand_id: str) -> List[Dict[str, Any]]:
        """Get all keywords for a brand."""
        response = self.db.table("g_keywords").select("*").eq("brand_id", brand_id).execute()
        return response.data

    def get_agent_deliverable(self, brand_id: str, cycle_id: str, agent_name: str) -> Dict[str, Any]:
        """Get task assignment for this agent from agent_deliverables table."""
        response = (
            self.db.table("agent_deliverables")
            .select("*")
            .eq("brand_id", brand_id)
            .eq("cycle_id", cycle_id)
            .eq("agent_name", agent_name)
            .single()
            .execute()
        )
        return response.data

    # WRITE Operations

    def insert_daily_metrics(self, metrics: List[Dict[str, Any]]) -> None:
        """Insert daily metrics for campaigns, ad groups, ads, keywords."""
        self.db.table("g_daily_metrics").insert(metrics).execute()
        logger.info(f"Inserted {len(metrics)} daily metric rows")

    def insert_tracking_health(self, health_records: List[Dict[str, Any]]) -> None:
        """Insert tracking health status per campaign."""
        self.db.table("g_tracking_health").insert(health_records).execute()
        logger.info(f"Inserted {len(health_records)} tracking health records")

    def insert_audiences(self, audiences: List[Dict[str, Any]]) -> None:
        """Insert/upsert built audiences."""
        self.db.table("g_audiences").upsert(audiences).execute()
        logger.info(f"Inserted/updated {len(audiences)} audiences")

    def update_keywords(self, keyword_updates: List[Dict[str, Any]]) -> None:
        """Update keyword performance and classification."""
        for update in keyword_updates:
            self.db.table("g_keywords").update(update).eq("id", update["id"]).execute()
        logger.info(f"Updated {len(keyword_updates)} keywords")

    def insert_search_terms(self, search_terms: List[Dict[str, Any]]) -> None:
        """Insert search term report data."""
        self.db.table("g_search_terms").insert(search_terms).execute()
        logger.info(f"Inserted {len(search_terms)} search term records")

    def insert_cannibalization_scores(self, cannibal_scores: List[Dict[str, Any]]) -> None:
        """Insert cannibalization analysis results."""
        self.db.table("g_cannibalization_scores").insert(cannibal_scores).execute()
        logger.info(f"Inserted {len(cannibal_scores)} cannibalization score records")

    def insert_alerts(self, alerts: List[Dict[str, Any]]) -> None:
        """Insert critical tracking or performance alerts."""
        self.db.table("alerts").insert(alerts).execute()
        logger.info(f"Inserted {len(alerts)} alerts")

    def insert_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """Insert action recommendations from analysis."""
        self.db.table("recommendations").insert(recommendations).execute()
        logger.info(f"Inserted {len(recommendations)} recommendations")

    def update_agent_deliverable(
        self,
        brand_id: str,
        cycle_id: str,
        agent_name: str,
        status: str,
        summary: str = None,
        content: Dict[str, Any] = None,
    ) -> None:
        """Mark agent deliverable as complete or blocked."""
        update_data = {
            "status": status,
            "delivered_at": datetime.utcnow().isoformat() if status == "DELIVERED" else None,
        }

        if summary:
            update_data["summary"] = summary

        if content:
            update_data["content"] = content

        self.db.table("agent_deliverables").update(update_data).eq(
            "brand_id", brand_id
        ).eq("cycle_id", cycle_id).eq("agent_name", agent_name).execute()

        logger.info(f"Updated deliverable status to {status}")

    def update_ar_multiplier(self, brand_id: str, new_multiplier: float, source: str) -> None:
        """Update AR multiplier calibration."""
        self.db.table("brand_config").update({
            "ar_multiplier": new_multiplier,
            "ar_multiplier_source": source,
            "ar_multiplier_calibrated_at": datetime.utcnow().isoformat(),
        }).eq("id", brand_id).execute()

        logger.info(f"Updated AR multiplier to {new_multiplier}× (source: {source})")

    # Utility Methods

    def get_verified_data_for_agents(self, brand_id: str, date_range: tuple) -> Dict[str, Any]:
        """
        Pull verified daily metrics data for other agents (Creative, Post-Click, etc).

        Args:
            brand_id: Brand ID
            date_range: Tuple of (start_date, end_date) in YYYY-MM-DD format

        Returns:
            Dictionary with metrics by level (campaign, ad_group, ad, keyword)
        """
        start_date, end_date = date_range

        response = (
            self.db.table("g_daily_metrics")
            .select("*")
            .eq("brand_id", brand_id)
            .gte("date", start_date)
            .lte("date", end_date)
            .execute()
        )

        # Organize by level
        data_by_level = {
            "campaign": [],
            "ad_group": [],
            "ad": [],
            "keyword": [],
        }

        for row in response.data:
            level = row.get("level")
            if level in data_by_level:
                data_by_level[level].append(row)

        return data_by_level

    def get_ghost_campaigns(self, brand_id: str, date_range: tuple) -> List[Dict[str, Any]]:
        """
        Identify ghost campaigns - where Google reports conversions but GA4 shows zero.

        Returns: List of campaigns with Google conversions but no GA4 conversions
        """
        start_date, end_date = date_range

        response = (
            self.db.table("g_daily_metrics")
            .select("*")
            .eq("brand_id", brand_id)
            .eq("level", "campaign")
            .gte("date", start_date)
            .lte("date", end_date)
            .gt("google_conversions", 0)
            .eq("ga4_conversions", 0)
            .execute()
        )

        return response.data

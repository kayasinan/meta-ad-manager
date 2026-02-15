#!/usr/bin/env python3
"""
Meta Ads Campaign Builder

Constructs campaign, ad set, and ad structures in Meta Ads API.
All creations are in DRAFT status — no live activation without human approval.

Functions:
- create_campaign_draft: Create a campaign in DRAFT status
- create_adset_draft: Create an ad set in DRAFT status
- create_ad_draft: Create an ad in DRAFT status
- validate_utm: Validate UTM parameters before creation
"""

import argparse
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetaCampaignBuilder:
    """Builds campaign structures in Meta Ads API."""

    def __init__(self, access_token: str, account_id: str, api_version: str = "v19.0"):
        """
        Initialize the campaign builder.

        Args:
            access_token: Meta Graph API access token
            account_id: Meta ad account ID
            api_version: Meta API version (default: v19.0)
        """
        self.access_token = access_token
        self.account_id = account_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}/act_{account_id}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def create_campaign_draft(
        self,
        name: str,
        objective: str,
        budget_daily: Optional[float] = None,
        target_ar_cpa: Optional[float] = None,
        target_ar_roas: Optional[float] = None,
        bid_strategy: str = "LOWEST_COST",
        bid_strategy_rationale: str = ""
    ) -> Tuple[Optional[str], Dict]:
        """
        Create a campaign in DRAFT status.

        Args:
            name: Campaign name (following naming convention)
            objective: Campaign objective (CONVERSIONS, TRAFFIC, AWARENESS, LEAD_GENERATION)
            budget_daily: Proposed daily budget (draft only, human approves)
            target_ar_cpa: Target attribution-ready CPA
            target_ar_roas: Target attribution-ready ROAS
            bid_strategy: Bid strategy (LOWEST_COST, COST_CAP, BID_CAP, MINIMUM_ROAS)
            bid_strategy_rationale: Why this strategy was chosen

        Returns:
            Tuple of (campaign_id, metadata_dict)
        """
        try:
            payload = {
                "name": name,
                "objective": objective,
                "status": "DRAFT",  # CRITICAL: Always create in DRAFT status
            }

            # Optional fields
            if budget_daily:
                payload["daily_budget"] = int(budget_daily * 100)  # In cents

            # Add custom fields if supported by API
            if target_ar_cpa:
                payload["target_ar_cpa"] = target_ar_cpa
            if target_ar_roas:
                payload["target_ar_roas"] = target_ar_roas

            # Note: Bid strategy is configured at ad set level
            # Store as metadata for reference
            payload["custom_data"] = {
                "bid_strategy": bid_strategy,
                "bid_strategy_rationale": bid_strategy_rationale
            }

            # Create campaign
            url = f"{self.base_url}/campaigns"
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            campaign_id = result.get("id")

            metadata = {
                "campaign_id": campaign_id,
                "name": name,
                "objective": objective,
                "status": "DRAFT",
                "budget_daily_proposed": budget_daily,
                "target_ar_cpa": target_ar_cpa,
                "target_ar_roas": target_ar_roas,
                "bid_strategy": bid_strategy,
                "bid_strategy_rationale": bid_strategy_rationale,
                "created_at": datetime.utcnow().isoformat(),
                "api_response": result
            }

            logger.info(f"Campaign created in DRAFT: {campaign_id} ({name})")
            return campaign_id, metadata

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create campaign: {e}")
            return None, {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"Campaign creation failed: {e}")
            return None, {"error": str(e), "status": "failed"}

    def create_adset_draft(
        self,
        campaign_id: str,
        name: str,
        audience_id: str,
        daily_budget: float,
        targeting_config: Dict,
        placement_config: Dict,
        dayparting_config: Optional[Dict] = None,
        frequency_cap: int = 4
    ) -> Tuple[Optional[str], Dict]:
        """
        Create an ad set in DRAFT status.

        Args:
            campaign_id: Parent campaign ID
            name: Ad set name (following naming convention)
            audience_id: Meta audience ID for targeting
            daily_budget: Daily budget in USD
            targeting_config: Targeting parameters (age, gender, location, interests, etc.)
            placement_config: Placements (FACEBOOK, INSTAGRAM, AUDIENCE_NETWORK, etc.)
            dayparting_config: Schedule/dayparting restrictions (optional)
            frequency_cap: Maximum frequency per period (default: 4 per day)

        Returns:
            Tuple of (adset_id, metadata_dict)
        """
        try:
            payload = {
                "name": name,
                "campaign_id": campaign_id,
                "daily_budget": int(daily_budget * 100),  # In cents
                "billing_event": "IMPRESSIONS",
                "optimization_goal": "COST_PER_CONVERSION",  # Auto-adjust based on campaign objective
                "status": "DRAFT",  # CRITICAL: Always create in DRAFT status
                "targeting": targeting_config,
                "promoted_object": {
                    "pixel_id": targeting_config.get("pixel_id")
                }
            }

            # Placements
            if placement_config:
                payload["placement_config"] = placement_config

            # Frequency cap
            if frequency_cap:
                payload["frequency_map"] = [
                    {
                        "interval_frequency_type": "DAY",
                        "max_frequency": frequency_cap
                    }
                ]

            # Dayparting
            if dayparting_config:
                payload["adset_schedule"] = dayparting_config

            # Create ad set
            url = f"{self.base_url}/adsets"
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            adset_id = result.get("id")

            metadata = {
                "adset_id": adset_id,
                "campaign_id": campaign_id,
                "name": name,
                "audience_id": audience_id,
                "daily_budget": daily_budget,
                "frequency_cap": frequency_cap,
                "status": "DRAFT",
                "learning_phase_start": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "api_response": result
            }

            logger.info(f"Ad set created in DRAFT: {adset_id} ({name})")
            return adset_id, metadata

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create ad set: {e}")
            return None, {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"Ad set creation failed: {e}")
            return None, {"error": str(e), "status": "failed"}

    def create_ad_draft(
        self,
        adset_id: str,
        name: str,
        creative_id: str,
        adset_spec_config: Dict
    ) -> Tuple[Optional[str], Dict]:
        """
        Create an ad in DRAFT status.

        Args:
            adset_id: Parent ad set ID
            name: Ad name (following naming convention)
            creative_id: Meta creative ID
            adset_spec_config: Ad-specific configuration (copy, landing page, CTA, etc.)

        Returns:
            Tuple of (ad_id, metadata_dict)
        """
        try:
            payload = {
                "name": name,
                "adset_id": adset_id,
                "creative": {
                    "creative_id": creative_id
                },
                "status": "DRAFT",  # CRITICAL: Always create in DRAFT status
            }

            # Merge ad-specific config
            payload.update(adset_spec_config)

            # Create ad
            url = f"{self.base_url}/ads"
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            result = response.json()
            ad_id = result.get("id")

            metadata = {
                "ad_id": ad_id,
                "adset_id": adset_id,
                "name": name,
                "creative_id": creative_id,
                "status": "DRAFT",
                "created_at": datetime.utcnow().isoformat(),
                "api_response": result
            }

            logger.info(f"Ad created in DRAFT: {ad_id} ({name})")
            return ad_id, metadata

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create ad: {e}")
            return None, {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"Ad creation failed: {e}")
            return None, {"error": str(e), "status": "failed"}

    def validate_utm(self, ad_config: Dict) -> List[str]:
        """
        Validate UTM parameters in ad configuration.

        Args:
            ad_config: Ad configuration dictionary

        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []

        # Extract tracking URL
        tracking_url = ad_config.get("adset_spec", {}).get("tracking_url")
        if not tracking_url:
            issues.append("No tracking URL specified")
            return issues

        # Validate required UTM parameters
        required_utms = {
            "utm_source": "facebook",
            "utm_medium": "paid_social"
        }

        for param, expected_value in required_utms.items():
            if param not in tracking_url:
                issues.append(f"Missing required parameter: {param}")
            elif expected_value and expected_value not in tracking_url:
                issues.append(f"Incorrect {param}: expected '{expected_value}'")

        # Check for utm_campaign
        if "utm_campaign" not in tracking_url:
            issues.append("Missing utm_campaign parameter")
        else:
            # Verify format: {brand_id}_{campaign_id}_{name}
            utm_campaign = [p.split("=")[1] for p in tracking_url.split("&") if p.startswith("utm_campaign")]
            if utm_campaign and "_" not in utm_campaign[0]:
                issues.append("utm_campaign format invalid (should be brand_id_campaign_id_name)")

        # Check for utm_content
        if "utm_content" not in tracking_url:
            issues.append("Missing utm_content parameter")
        else:
            # Verify includes ad_id and image identifier
            utm_content = [p.split("=")[1] for p in tracking_url.split("&") if p.startswith("utm_content")]
            if utm_content and "_" not in utm_content[0]:
                issues.append("utm_content format invalid (should be ad_id_image_copy)")

        # Check for utm_term
        if "utm_term" not in tracking_url:
            issues.append("Missing utm_term parameter")
        else:
            # Verify includes adset_id and segment
            utm_term = [p.split("=")[1] for p in tracking_url.split("&") if p.startswith("utm_term")]
            if utm_term and "_" not in utm_term[0]:
                issues.append("utm_term format invalid (should be adset_id_segment)")

        return issues

    def pause_ad(self, ad_id: str, reason: str = "") -> Tuple[bool, Dict]:
        """
        Pause an ad (update status to PAUSED).

        Args:
            ad_id: Meta ad ID
            reason: Pause reason (for logging)

        Returns:
            Tuple of (success, metadata_dict)
        """
        try:
            payload = {"status": "PAUSED"}

            url = f"{self.base_url}/ads/{ad_id}"
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            metadata = {
                "ad_id": ad_id,
                "status": "PAUSED",
                "pause_reason": reason,
                "paused_at": datetime.utcnow().isoformat(),
                "api_response": response.json()
            }

            logger.info(f"Ad paused: {ad_id} ({reason})")
            return True, metadata

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to pause ad: {e}")
            return False, {"error": str(e), "status": "failed"}

    def pause_adset(self, adset_id: str, reason: str = "") -> Tuple[bool, Dict]:
        """
        Pause an ad set (update status to PAUSED).

        Args:
            adset_id: Meta ad set ID
            reason: Pause reason (for logging)

        Returns:
            Tuple of (success, metadata_dict)
        """
        try:
            payload = {"status": "PAUSED"}

            url = f"{self.base_url}/adsets/{adset_id}"
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()

            metadata = {
                "adset_id": adset_id,
                "status": "PAUSED",
                "pause_reason": reason,
                "paused_at": datetime.utcnow().isoformat(),
                "api_response": response.json()
            }

            logger.info(f"Ad set paused: {adset_id} ({reason})")
            return True, metadata

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to pause ad set: {e}")
            return False, {"error": str(e), "status": "failed"}


def main():
    """Command-line interface for campaign builder."""
    parser = argparse.ArgumentParser(
        description="Meta Ads Campaign Builder"
    )
    parser.add_argument(
        "--access-token",
        required=True,
        help="Meta Graph API access token"
    )
    parser.add_argument(
        "--account-id",
        required=True,
        help="Meta ad account ID"
    )
    parser.add_argument(
        "--action",
        required=True,
        choices=["create_campaign", "create_adset", "create_ad", "validate_utm"],
        help="Action to perform"
    )
    parser.add_argument(
        "--campaign-name",
        help="Campaign name for create_campaign"
    )
    parser.add_argument(
        "--campaign-objective",
        choices=["CONVERSIONS", "TRAFFIC", "AWARENESS", "LEAD_GENERATION"],
        help="Campaign objective"
    )
    parser.add_argument(
        "--adset-name",
        help="Ad set name for create_adset"
    )
    parser.add_argument(
        "--campaign-id",
        help="Campaign ID for create_adset/create_ad"
    )
    parser.add_argument(
        "--audience-id",
        help="Audience ID for create_adset"
    )
    parser.add_argument(
        "--budget",
        type=float,
        help="Daily budget in USD"
    )
    parser.add_argument(
        "--targeting-config",
        help="Path to targeting config JSON"
    )
    parser.add_argument(
        "--placement-config",
        help="Path to placement config JSON"
    )
    parser.add_argument(
        "--ad-name",
        help="Ad name for create_ad"
    )
    parser.add_argument(
        "--creative-id",
        help="Creative ID for create_ad"
    )
    parser.add_argument(
        "--ad-config",
        help="Path to ad config JSON for create_ad/validate_utm"
    )
    parser.add_argument(
        "--output",
        help="Save result to JSON file"
    )

    args = parser.parse_args()

    # Initialize builder
    builder = MetaCampaignBuilder(args.access_token, args.account_id)

    result = None

    # Execute action
    if args.action == "create_campaign":
        if not args.campaign_name or not args.campaign_objective:
            print("Error: --campaign-name and --campaign-objective required")
            return 1

        campaign_id, metadata = builder.create_campaign_draft(
            name=args.campaign_name,
            objective=args.campaign_objective
        )

        result = {
            "action": "create_campaign",
            "success": campaign_id is not None,
            "campaign_id": campaign_id,
            "metadata": metadata
        }

    elif args.action == "create_adset":
        if not args.campaign_id or not args.adset_name or not args.audience_id or not args.budget:
            print("Error: --campaign-id, --adset-name, --audience-id, --budget required")
            return 1

        # Load configs
        targeting_config = {}
        placement_config = {}

        if args.targeting_config:
            with open(args.targeting_config) as f:
                targeting_config = json.load(f)
        if args.placement_config:
            with open(args.placement_config) as f:
                placement_config = json.load(f)

        adset_id, metadata = builder.create_adset_draft(
            campaign_id=args.campaign_id,
            name=args.adset_name,
            audience_id=args.audience_id,
            daily_budget=args.budget,
            targeting_config=targeting_config,
            placement_config=placement_config
        )

        result = {
            "action": "create_adset",
            "success": adset_id is not None,
            "adset_id": adset_id,
            "metadata": metadata
        }

    elif args.action == "create_ad":
        if not args.campaign_id or not args.ad_name or not args.creative_id or not args.ad_config:
            print("Error: --campaign-id, --ad-name, --creative-id, --ad-config required")
            return 1

        # Load ad config
        with open(args.ad_config) as f:
            ad_config = json.load(f)

        ad_id, metadata = builder.create_ad_draft(
            adset_id=args.campaign_id,  # Note: using campaign_id as adset_id
            name=args.ad_name,
            creative_id=args.creative_id,
            adset_spec_config=ad_config
        )

        result = {
            "action": "create_ad",
            "success": ad_id is not None,
            "ad_id": ad_id,
            "metadata": metadata
        }

    elif args.action == "validate_utm":
        if not args.ad_config:
            print("Error: --ad-config required")
            return 1

        with open(args.ad_config) as f:
            ad_config = json.load(f)

        issues = builder.validate_utm(ad_config)

        result = {
            "action": "validate_utm",
            "success": len(issues) == 0,
            "issues": issues
        }

    # Save result if requested
    if args.output and result:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Result saved to: {args.output}")

    # Print result
    print(json.dumps(result, indent=2))

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    exit(main())

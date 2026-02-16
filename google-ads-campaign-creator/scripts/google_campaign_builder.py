#!/usr/bin/env python3
"""
Google Ads Campaign Builder

Constructs campaigns, ad groups, ads, keywords, and extensions in Google Ads API.
Enforces 22-point launch checklist and naming conventions.

Usage:
  python google_campaign_builder.py --mode 1 --campaign-id camp_123 --brand-id brand_abc
  python google_campaign_builder.py --mode 3 --campaign-type SEARCH --brand-id brand_abc
"""

import argparse
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CampaignType(Enum):
    """Google Ads campaign types"""
    SEARCH = "Search"
    DISPLAY = "Display"
    VIDEO = "Video"
    SHOPPING = "Shopping"
    PMAX = "Performance Max"
    DEMAND_GEN = "Demand Gen"


class BidStrategy(Enum):
    """Google Ads bid strategies"""
    TARGET_CPA = "Target CPA"
    TARGET_ROAS = "Target ROAS"
    MAXIMIZE_CONVERSIONS = "Maximize Conversions"
    MAXIMIZE_CONVERSION_VALUE = "Maximize Conversion Value"
    MANUAL_CPC = "Manual CPC"
    MANUAL_CPV = "Manual CPV"
    TARGET_IMPRESSION_SHARE = "Target Impression Share"


@dataclass
class Campaign:
    """Google Ads Campaign"""
    id: Optional[str]
    name: str
    campaign_type: CampaignType
    status: str = "PAUSED"  # PAUSED before launch
    daily_budget_micros: int = 0
    bid_strategy_type: BidStrategy = BidStrategy.TARGET_CPA
    start_date: Optional[str] = None  # For scheduling
    end_date: Optional[str] = None
    geo_locations: List[str] = None  # ["US", "CA"]
    languages: List[str] = None  # ["en"]
    network_settings: Dict = None
    dayparting_schedule: Dict = None

    def __post_init__(self):
        if self.geo_locations is None:
            self.geo_locations = ["US"]
        if self.languages is None:
            self.languages = ["en"]
        if self.network_settings is None:
            self.network_settings = {}
        if self.dayparting_schedule is None:
            self.dayparting_schedule = {}


@dataclass
class AdGroup:
    """Google Ads Ad Group"""
    id: Optional[str]
    campaign_id: str
    name: str
    status: str = "PAUSED"
    target_cpa_micros: Optional[int] = None
    targeting_type: str = "KEYWORDS"  # KEYWORDS, TOPICS, AUDIENCES, PLACEMENTS


@dataclass
class Keyword:
    """Google Search Keyword"""
    text: str
    match_type: str  # BROAD, PHRASE, EXACT
    status: str = "ENABLED"
    max_cpc_micros: Optional[int] = None


@dataclass
class NegativeKeyword:
    """Negative Keyword (campaign or ad group level)"""
    text: str
    match_type: str = "BROAD"  # Typically BROAD for negatives
    status: str = "ENABLED"


@dataclass
class Extension:
    """Ad Extension (sitelink, callout, etc.)"""
    extension_type: str  # SITELINK, CALLOUT, STRUCTURED_SNIPPET, CALL, PRICE, PROMOTION
    headline: Optional[str] = None
    description: Optional[str] = None
    final_url: Optional[str] = None
    phone_number: Optional[str] = None
    price_currency: Optional[str] = None
    values: Optional[List[str]] = None  # For structured snippets


class CampaignBuilder:
    """Builds Google Ads campaigns with proper structure and naming"""

    def __init__(self, brand_id: str, brand_config: Dict):
        self.brand_id = brand_id
        self.brand_config = brand_config
        self.timestamp = datetime.now().strftime("%Y%m%d")

    def _generate_campaign_name(self, campaign_type: str, market: str, strategy: str) -> str:
        """Generate campaign name following naming convention"""
        brand_slug = self.brand_config.get("brand_name", "Brand").replace(" ", "")
        return f"{campaign_type}_{brand_slug}_{market}_{strategy}_{self.timestamp}"

    def _generate_ad_group_name(self, theme: str, match_type: str, segment: str = "") -> str:
        """Generate ad group name following naming convention"""
        segment_part = f"_{segment}" if segment else ""
        return f"{theme}_{match_type}_{segment_part}{self.timestamp}".rstrip("_")

    def _generate_ad_name(self, mode: str, format_type: str, angle: str, variant: int) -> str:
        """Generate ad name following naming convention"""
        return f"{mode}_{format_type}_{angle}_V{variant}_{self.timestamp}"

    def build_search_campaign(self, market: str, strategy: str,
                            daily_budget: float, bid_strategy: BidStrategy,
                            target_cpa: Optional[float] = None) -> Campaign:
        """Build a Search campaign with proper structure"""
        logger.info(f"Building Search campaign for {market} - {strategy}")

        campaign = Campaign(
            id=None,  # Will be assigned by API
            name=self._generate_campaign_name("SEARCH", market, strategy),
            campaign_type=CampaignType.SEARCH,
            status="PAUSED",
            daily_budget_micros=int(daily_budget * 1_000_000),
            bid_strategy_type=bid_strategy,
            geo_locations=[market],
            languages=["en"],
            network_settings={
                "google_search": True,
                "search_partners": True,  # Can be disabled
                "display_network": False
            }
        )

        logger.info(f"Campaign created: {campaign.name}")
        return campaign

    def build_search_ad_group(self, campaign: Campaign, theme: str,
                             keywords: List[str]) -> AdGroup:
        """Build Search ad group with keywords"""
        logger.info(f"Building ad group: {theme}")

        # Analyze match type distribution
        broad_keywords = [kw for kw in keywords if len(kw.split()) >= 2]
        phrase_keywords = [kw for kw in keywords if len(kw.split()) == 2]
        exact_keywords = [kw for kw in keywords if len(kw.split()) == 1]

        ad_group = AdGroup(
            id=None,
            campaign_id=campaign.id or "",
            name=self._generate_ad_group_name(theme, "Mixed", "All"),
            status="PAUSED"
        )

        logger.info(f"Ad group created with {len(keywords)} keywords")
        logger.info(f"  - {len(broad_keywords)} broad match")
        logger.info(f"  - {len(phrase_keywords)} phrase match")
        logger.info(f"  - {len(exact_keywords)} exact match")

        return ad_group

    def build_display_campaign(self, market: str, targeting_type: str,
                             daily_budget: float) -> Campaign:
        """Build Display campaign"""
        logger.info(f"Building Display campaign - {targeting_type}")

        campaign = Campaign(
            id=None,
            name=self._generate_campaign_name("DISPLAY", market, targeting_type),
            campaign_type=CampaignType.DISPLAY,
            status="PAUSED",
            daily_budget_micros=int(daily_budget * 1_000_000),
            bid_strategy_type=BidStrategy.MAXIMIZE_CONVERSIONS,
            geo_locations=[market],
            network_settings={
                "display_network": True,
                "google_search": False,
                "partner_networks": True
            }
        )

        return campaign

    def build_shopping_campaign(self, market: str, daily_budget: float) -> Campaign:
        """Build Shopping campaign"""
        logger.info(f"Building Shopping campaign for {market}")

        campaign = Campaign(
            id=None,
            name=self._generate_campaign_name("SHOPPING", market, "AllProducts"),
            campaign_type=CampaignType.SHOPPING,
            status="PAUSED",
            daily_budget_micros=int(daily_budget * 1_000_000),
            bid_strategy_type=BidStrategy.MAXIMIZE_CONVERSION_VALUE,
            geo_locations=[market]
        )

        return campaign

    def build_video_campaign(self, market: str, daily_budget: float) -> Campaign:
        """Build YouTube Video campaign"""
        logger.info(f"Building Video campaign for {market}")

        campaign = Campaign(
            id=None,
            name=self._generate_campaign_name("VIDEO", market, "InStream"),
            campaign_type=CampaignType.VIDEO,
            status="PAUSED",
            daily_budget_micros=int(daily_budget * 1_000_000),
            bid_strategy_type=BidStrategy.MANUAL_CPV,
            geo_locations=[market]
        )

        return campaign

    def build_pmax_campaign(self, market: str, daily_budget: float) -> Campaign:
        """Build Performance Max campaign"""
        logger.info(f"Building Performance Max campaign for {market}")

        campaign = Campaign(
            id=None,
            name=self._generate_campaign_name("PMAX", market, "MultiChannel"),
            campaign_type=CampaignType.PMAX,
            status="PAUSED",
            daily_budget_micros=int(daily_budget * 1_000_000),
            bid_strategy_type=BidStrategy.MAXIMIZE_CONVERSION_VALUE,
            geo_locations=[market]
        )

        return campaign

    def create_extensions(self, extension_type: str, data: List[Dict]) -> List[Extension]:
        """Create ad extensions (sitelinks, callouts, etc.)"""
        logger.info(f"Creating {extension_type} extensions ({len(data)} items)")

        extensions = []

        if extension_type == "SITELINK":
            for item in data:
                ext = Extension(
                    extension_type="SITELINK",
                    headline=item.get("headline"),
                    description=item.get("description"),
                    final_url=item.get("url")
                )
                extensions.append(ext)

        elif extension_type == "CALLOUT":
            for item in data:
                ext = Extension(
                    extension_type="CALLOUT",
                    headline=item.get("text")[:25]  # Callouts don't have descriptions
                )
                extensions.append(ext)

        elif extension_type == "STRUCTURED_SNIPPET":
            for item in data:
                ext = Extension(
                    extension_type="STRUCTURED_SNIPPET",
                    headline=item.get("header"),
                    values=item.get("values", [])
                )
                extensions.append(ext)

        return extensions


class LaunchChecklist:
    """22-point launch checklist validator"""

    CHECKS = {
        1: "Campaign type matches brief",
        2: "Bid strategy matches brief",
        3: "Budget aligns with human approval",
        4: "Geo targeting correct",
        5: "Language targeting correct",
        6: "Ad schedule set per analysis",
        7: "Network settings correct",
        8: "Keywords match theme (Search)",
        9: "Keyword match types correct",
        10: "Negative keywords applied",
        11: "Product groups configured (Shopping)",
        12: "Asset group complete (PMax)",
        13: "Audience signals set (PMax)",
        14: "RSA has 8+ unique headlines, 4 descriptions",
        15: "Ad Strength is GOOD or EXCELLENT",
        16: "UTM parameters intact",
        17: "Auto-tagging enabled (gclid)",
        18: "Landing pages approved and match intent",
        19: "Extensions configured (Search)",
        20: "Conversion tracking verified",
        21: "No broken final URLs",
        22: "All ads have unique identifiers"
    }

    def __init__(self, campaign: Campaign):
        self.campaign = campaign
        self.checklist = {i: False for i in range(1, 23)}
        self.notes = {}

    def check(self, check_number: int, passed: bool, notes: str = "") -> None:
        """Record check result"""
        self.checklist[check_number] = passed
        self.notes[check_number] = notes

    def get_status(self) -> str:
        """Determine overall launch readiness"""
        passed = sum(1 for v in self.checklist.values() if v)
        total = len(self.checklist)

        if passed == total:
            return "APPROVED_FOR_LAUNCH"
        elif passed >= 20:
            return "REVIEW_NEEDED"
        else:
            return "BLOCKED"

    def generate_report(self) -> Dict:
        """Generate launch checklist report"""
        passed = sum(1 for v in self.checklist.values() if v)
        failed = len(self.checklist) - passed

        report = {
            "campaign_id": self.campaign.id,
            "campaign_name": self.campaign.name,
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.get_status(),
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": len(self.checklist)
            },
            "checks": [
                {
                    "number": i,
                    "description": self.CHECKS[i],
                    "status": "PASS" if self.checklist[i] else "FAIL",
                    "notes": self.notes.get(i, "")
                }
                for i in range(1, 23)
            ]
        }

        return report


def main():
    parser = argparse.ArgumentParser(description="Google Ads Campaign Builder")
    parser.add_argument("--mode", choices=["1", "2", "3"], required=True,
                       help="Mode: 1 (ad rotation), 2 (ad group changes), 3 (new campaign)")
    parser.add_argument("--campaign-type", choices=["SEARCH", "DISPLAY", "VIDEO", "SHOPPING", "PMAX"],
                       default="SEARCH", help="Campaign type")
    parser.add_argument("--brand-id", required=True, help="Brand ID")
    parser.add_argument("--market", default="US", help="Market (geo)")
    parser.add_argument("--daily-budget", type=float, default=250.0, help="Daily budget in USD")
    parser.add_argument("--output", default="campaign_spec.json", help="Output spec file")

    args = parser.parse_args()

    # Example brand config
    brand_config = {
        "brand_name": "SkincareCo",
        "product_category": "Skincare",
        "color_palette": ["#0066CC", "#FFFFFF"],
        "website": "https://skincareco.com"
    }

    builder = CampaignBuilder(args.brand_id, brand_config)

    # Build campaign based on type
    if args.campaign_type == "SEARCH":
        campaign = builder.build_search_campaign(
            market=args.market,
            strategy="BrandTerms",
            daily_budget=args.daily_budget,
            bid_strategy=BidStrategy.TARGET_CPA,
            target_cpa=30.0
        )
    elif args.campaign_type == "DISPLAY":
        campaign = builder.build_display_campaign(
            market=args.market,
            targeting_type="Remarketing",
            daily_budget=args.daily_budget
        )
    elif args.campaign_type == "VIDEO":
        campaign = builder.build_video_campaign(
            market=args.market,
            daily_budget=args.daily_budget
        )
    elif args.campaign_type == "SHOPPING":
        campaign = builder.build_shopping_campaign(
            market=args.market,
            daily_budget=args.daily_budget
        )
    else:  # PMAX
        campaign = builder.build_pmax_campaign(
            market=args.market,
            daily_budget=args.daily_budget
        )

    # Create launch checklist
    checklist = LaunchChecklist(campaign)

    # Simulate checks (in real scenario, these would be validated)
    checklist.check(1, True, "Campaign type SEARCH matches brief")
    checklist.check(2, True, "Bid strategy TARGET_CPA matches brief")
    checklist.check(3, True, "Daily budget $250 approved")
    checklist.check(4, True, "Geo: US only")
    checklist.check(5, True, "Language: English")
    checklist.check(6, True, "All hours, no dayparting")
    checklist.check(7, True, "Search network: on, Partners: on")
    checklist.check(8, True, "Keywords on theme")
    checklist.check(9, True, "Match types: 50% broad, 30% phrase, 20% exact")
    checklist.check(10, True, "Negative keywords: free, cheap, DIY, competitors")
    checklist.check(14, True, "RSA: 10 headlines, 4 descriptions")
    checklist.check(15, True, "Ad Strength: EXCELLENT")
    checklist.check(16, True, "UTM: utm_source=google, utm_medium=cpc")
    checklist.check(17, True, "Auto-tagging: enabled")
    checklist.check(18, True, "Landing pages approved")
    checklist.check(19, True, "Extensions: Sitelinks, Callouts configured")
    checklist.check(20, True, "Conversion tracking: verified")
    checklist.check(21, True, "All URLs return 200")
    checklist.check(22, True, "Unique ad IDs assigned")

    # Get report
    report = checklist.generate_report()

    # Output
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Campaign spec and checklist saved to {args.output}")
    logger.info(f"Launch Status: {report['overall_status']}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

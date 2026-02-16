#!/usr/bin/env python3
"""
QC Pipeline Checker for Google Ads Creatives

Validates all creative assets against 7-point QC pipeline before marking DELIVERED.
Checks: Professional Quality, Text Readability, Character Limits, Ad Strength,
Color Consistency, Artifacts, and Brand Integrity.

Usage:
  python qc_check.py --creative-id creative_123 --brand-id brand_abc --output report.json
"""

import argparse
import json
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QCCheck:
    """Single QC check result"""
    check_name: str
    check_number: int
    status: str  # PASS, FAIL, REVIEW_NEEDED
    score: int   # 0-10
    notes: str


class QCPipeline:
    """7-point QC validation pipeline for Google Ads creatives"""

    def __init__(self, creative_data: Dict):
        self.creative = creative_data
        self.checks: List[QCCheck] = []
        self.timestamp = datetime.now().isoformat()

    def check_1_professional_quality(self) -> QCCheck:
        """Check 1: Professional Quality - Image/video aesthetics"""
        logger.info("Check 1: Professional Quality...")

        score = 0
        notes = []

        # Check for professional imagery indicators
        if self.creative.get("image_source") == "professional_photographer":
            score += 8
            notes.append("Professional photography")
        elif self.creative.get("image_source") == "stock":
            score += 6
            notes.append("Stock imagery (acceptable)")
        elif self.creative.get("image_source") == "ai_generated":
            score += 4
            notes.append("AI-generated (verify quality)")
        else:
            score += 2
            notes.append("Unknown image source")

        # Color grading assessment
        if self.creative.get("color_graded", False):
            score += 2
            notes.append("Color graded")

        # Resolution check
        image_width = self.creative.get("image_width", 0)
        if image_width >= 1200:
            score += 0  # Already counted in setup
            notes.append(f"Resolution OK ({image_width}px)")
        else:
            score -= 2
            notes.append(f"Low resolution ({image_width}px)")

        status = "PASS" if score >= 7 else "REVIEW_NEEDED" if score >= 5 else "FAIL"

        return QCCheck(
            check_name="Professional Quality",
            check_number=1,
            status=status,
            score=score,
            notes="; ".join(notes)
        )

    def check_2_text_readability(self) -> QCCheck:
        """Check 2: Text Readability - Font size and contrast"""
        logger.info("Check 2: Text Readability...")

        score = 0
        notes = []

        # Font size check
        text_elements = self.creative.get("text_elements", [])
        small_text_count = sum(1 for t in text_elements if t.get("font_size", 12) < 12)
        if small_text_count == 0:
            score += 4
            notes.append("All text minimum 12pt")
        elif small_text_count <= 1:
            score += 2
            notes.append(f"One small text element")
        else:
            score -= 2
            notes.append(f"{small_text_count} small text elements")

        # Contrast ratio check
        contrast_ratios = [t.get("contrast_ratio", 0) for t in text_elements]
        if all(cr >= 4.5 for cr in contrast_ratios):
            score += 3
            notes.append("All text meets WCAG AA (4.5:1)")
        elif all(cr >= 3.0 for cr in contrast_ratios):
            score += 1
            notes.append("Most text meets WCAG A (3:1)")
        else:
            score -= 3
            notes.append("Low contrast text detected")

        # Text overlay coverage (max 20% of image for Display ads)
        overlay_percent = self.creative.get("text_overlay_percent", 0)
        if overlay_percent <= 20:
            score += 3
            notes.append(f"Text overlay {overlay_percent}% of image")
        else:
            score -= 2
            notes.append(f"Text overlay exceeds 20% ({overlay_percent}%)")

        status = "PASS" if score >= 7 else "REVIEW_NEEDED" if score >= 4 else "FAIL"

        return QCCheck(
            check_name="Text Readability",
            check_number=2,
            status=status,
            score=min(score, 10),
            notes="; ".join(notes)
        )

    def check_3_character_limits(self) -> QCCheck:
        """Check 3: Character Limits Compliance"""
        logger.info("Check 3: Character Limits Compliance...")

        ad_type = self.creative.get("ad_type", "RSA")
        violations = []

        if ad_type == "RSA":
            headlines = self.creative.get("headlines", [])
            descriptions = self.creative.get("descriptions", [])

            for i, h in enumerate(headlines):
                if len(h) > 30:
                    violations.append(f"Headline {i+1}: {len(h)} chars (max 30)")

            for i, d in enumerate(descriptions):
                if len(d) > 90:
                    violations.append(f"Description {i+1}: {len(d)} chars (max 90)")

            if len(headlines) < 8:
                violations.append(f"{len(headlines)} headlines (need 8+)")

            if len(descriptions) < 4:
                violations.append(f"{len(descriptions)} descriptions (need 4)")

        elif ad_type == "RDA":
            short_headlines = self.creative.get("short_headlines", [])
            long_headline = self.creative.get("long_headline", "")

            for i, sh in enumerate(short_headlines):
                if len(sh) > 25:
                    violations.append(f"Short headline {i+1}: {len(sh)} chars (max 25)")

            if len(long_headline) > 90:
                violations.append(f"Long headline: {len(long_headline)} chars (max 90)")

        elif ad_type == "Shopping":
            title = self.creative.get("product_title", "")
            if len(title) > 150:
                violations.append(f"Product title: {len(title)} chars (max 150)")

        elif ad_type == "PMax":
            headlines = self.creative.get("headlines", [])
            long_headlines = self.creative.get("long_headlines", [])
            descriptions = self.creative.get("descriptions", [])

            if len(headlines) < 15:
                violations.append(f"{len(headlines)} headlines (need 15)")

            if len(long_headlines) < 5:
                violations.append(f"{len(long_headlines)} long headlines (need 5)")

            if len(descriptions) < 5:
                violations.append(f"{len(descriptions)} descriptions (need 5)")

        status = "PASS" if len(violations) == 0 else "FAIL"
        notes = "; ".join(violations) if violations else "All limits met"

        return QCCheck(
            check_name="Character Limits Compliance",
            check_number=3,
            status=status,
            score=10 if status == "PASS" else 0,
            notes=notes
        )

    def check_4_ad_strength(self) -> QCCheck:
        """Check 4: Ad Strength Check (RSA/PMax only)"""
        logger.info("Check 4: Ad Strength Check...")

        ad_type = self.creative.get("ad_type", "RSA")

        if ad_type not in ["RSA", "PMax"]:
            return QCCheck(
                check_name="Ad Strength Check",
                check_number=4,
                status="PASS",
                score=10,
                notes="Not applicable for this ad type"
            )

        score = 0
        notes = []

        if ad_type == "RSA":
            headlines = self.creative.get("headlines", [])
            descriptions = self.creative.get("descriptions", [])

            # Headline count
            if len(headlines) >= 12:
                score += 3
                notes.append(f"{len(headlines)} headlines (excellent)")
            elif len(headlines) >= 8:
                score += 2
                notes.append(f"{len(headlines)} headlines (good)")
            else:
                score += 1
                notes.append(f"{len(headlines)} headlines (below optimal)")

            # Description count
            if len(descriptions) >= 4:
                score += 2
                notes.append(f"{len(descriptions)} descriptions")

            # Variety assessment (simplified)
            unique_headlines = len(set(headlines))
            if unique_headlines >= 8:
                score += 3
                notes.append("High headline variety")
            else:
                score += 1
                notes.append("Low headline variety")

            # Pinning assessment
            pinned = sum(1 for h in self.creative.get("pinned_headlines", []))
            if 1 <= pinned <= 3:
                score += 2
                notes.append(f"{pinned} headlines pinned (recommended)")

        elif ad_type == "PMax":
            headlines = self.creative.get("headlines", [])
            long_headlines = self.creative.get("long_headlines", [])
            descriptions = self.creative.get("descriptions", [])
            images = self.creative.get("images", [])

            if len(headlines) == 15:
                score += 2
            if len(long_headlines) == 5:
                score += 2
            if len(descriptions) == 5:
                score += 2

            # Image diversity
            unique_sizes = len(set(img.get("aspect_ratio") for img in images))
            if unique_sizes >= 3:
                score += 3
                notes.append("Diverse image sizes")

        # Convert to Google's ad strength assessment
        if score >= 8:
            strength = "EXCELLENT"
            status = "PASS"
        elif score >= 6:
            strength = "GOOD"
            status = "PASS"
        elif score >= 4:
            strength = "AVERAGE"
            status = "REVIEW_NEEDED"
        else:
            strength = "LOW"
            status = "FAIL"

        notes.append(f"Ad Strength: {strength}")

        return QCCheck(
            check_name="Ad Strength Check",
            check_number=4,
            status=status,
            score=min(score, 10),
            notes="; ".join(notes)
        )

    def check_5_color_consistency(self) -> QCCheck:
        """Check 5: Color Consistency - Brand palette adherence"""
        logger.info("Check 5: Color Consistency...")

        brand_colors = self.creative.get("brand_config", {}).get("color_palette", [])
        creative_colors = self.creative.get("colors_used", [])
        forbidden_colors = self.creative.get("brand_config", {}).get("forbidden_colors", [])

        violations = []

        # Check for forbidden colors
        for color in creative_colors:
            if color in forbidden_colors:
                violations.append(f"Forbidden color used: {color}")

        # Check brand palette adherence
        on_brand = sum(1 for c in creative_colors if c in brand_colors)
        brand_adherence = on_brand / len(creative_colors) if creative_colors else 0

        if brand_adherence >= 0.8:
            score = 9
            notes = [f"{int(brand_adherence*100)}% colors on-brand"]
        elif brand_adherence >= 0.6:
            score = 6
            notes = [f"{int(brand_adherence*100)}% colors on-brand"]
        else:
            score = 3
            notes = [f"Only {int(brand_adherence*100)}% colors on-brand"]

        if len(violations) > 0:
            score -= 3
            notes.extend(violations)
            status = "FAIL"
        else:
            status = "PASS" if score >= 7 else "REVIEW_NEEDED"

        return QCCheck(
            check_name="Color Consistency",
            check_number=5,
            status=status,
            score=max(score, 0),
            notes="; ".join(notes)
        )

    def check_6_artifacts_quality(self) -> QCCheck:
        """Check 6: Artifacts & AI Quality Issues"""
        logger.info("Check 6: Artifacts & AI Quality Issues...")

        score = 10
        notes = []

        # AI generation quality indicators
        is_ai_generated = self.creative.get("ai_generated", False)
        ai_artifacts = self.creative.get("ai_artifacts", [])

        if is_ai_generated:
            if len(ai_artifacts) == 0:
                score -= 1
                notes.append("AI-generated, no visible artifacts")
            elif len(ai_artifacts) <= 2:
                score -= 3
                notes.append(f"{len(ai_artifacts)} minor artifacts")
            else:
                score -= 5
                notes.append(f"{len(ai_artifacts)} noticeable artifacts")

        # Compression/pixelation
        if self.creative.get("compression_artifacts", False):
            score -= 2
            notes.append("Compression artifacts detected")

        # Text rendering
        if self.creative.get("text_distortion", False):
            score -= 3
            notes.append("Text distortion detected")

        status = "PASS" if score >= 8 else "REVIEW_NEEDED" if score >= 5 else "FAIL"

        return QCCheck(
            check_name="Artifacts & AI Quality Issues",
            check_number=6,
            status=status,
            score=max(score, 0),
            notes="; ".join(notes) if notes else "Clean, no artifacts"
        )

    def check_7_brand_integrity(self) -> QCCheck:
        """Check 7: Brand Integrity - Logo, product, locked elements"""
        logger.info("Check 7: Brand Integrity...")

        score = 0
        notes = []
        locked_elements = self.creative.get("brand_config", {}).get("locked_elements", [])

        # Logo presence
        logo_present = self.creative.get("logo_present", False)
        if logo_present:
            score += 2
            notes.append("Logo present")
        else:
            score -= 3
            notes.append("Logo missing")

        # Product visibility
        product_visible = self.creative.get("product_visible", False)
        if product_visible:
            score += 2
            notes.append("Product visible")
        else:
            score -= 2
            notes.append("Product not prominent")

        # Locked elements compliance
        missing_locked = [elem for elem in locked_elements
                         if not self.creative.get(f"has_{elem}", False)]

        if len(missing_locked) == 0:
            score += 2
            notes.append("All locked elements present")
        else:
            score -= 3
            notes.append(f"Missing locked elements: {', '.join(missing_locked)}")

        # Compliance text (if required)
        requires_compliance = self.creative.get("brand_config", {}).get("requires_compliance_text", False)
        has_compliance = self.creative.get("has_compliance_text", False)

        if requires_compliance and has_compliance:
            score += 2
            notes.append("Compliance text present")
        elif requires_compliance and not has_compliance:
            score -= 3
            notes.append("Missing required compliance text")

        status = "PASS" if score >= 6 else "REVIEW_NEEDED" if score >= 3 else "FAIL"

        return QCCheck(
            check_name="Brand Integrity",
            check_number=7,
            status=status,
            score=max(score, 0),
            notes="; ".join(notes)
        )

    def run_all_checks(self) -> Dict:
        """Run all 7 QC checks"""
        logger.info("Running 7-point QC pipeline...")

        self.checks = [
            self.check_1_professional_quality(),
            self.check_2_text_readability(),
            self.check_3_character_limits(),
            self.check_4_ad_strength(),
            self.check_5_color_consistency(),
            self.check_6_artifacts_quality(),
            self.check_7_brand_integrity(),
        ]

        # Determine overall status
        passed = sum(1 for c in self.checks if c.status == "PASS")
        reviewed = sum(1 for c in self.checks if c.status == "REVIEW_NEEDED")
        failed = sum(1 for c in self.checks if c.status == "FAIL")

        if failed > 0:
            overall_status = "FAILED"
        elif reviewed > 0:
            overall_status = "REVIEW_NEEDED"
        else:
            overall_status = "PASSED"

        logger.info(f"QC Complete: {passed} PASS, {reviewed} REVIEW, {failed} FAIL")

        return {
            "timestamp": self.timestamp,
            "creative_id": self.creative.get("id"),
            "ad_type": self.creative.get("ad_type"),
            "overall_status": overall_status,
            "passed": passed,
            "reviewed": reviewed,
            "failed": failed,
            "checks": [
                {
                    "number": c.check_number,
                    "name": c.check_name,
                    "status": c.status,
                    "score": c.score,
                    "notes": c.notes
                }
                for c in self.checks
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="QC Pipeline Checker")
    parser.add_argument("--creative-id", required=True, help="Creative ID")
    parser.add_argument("--creative-data", help="JSON file with creative data")
    parser.add_argument("--brand-id", required=True, help="Brand ID")
    parser.add_argument("--output", default="qc_report.json", help="Output report file")

    args = parser.parse_args()

    # Load creative data (simplified example)
    creative_data = {
        "id": args.creative_id,
        "brand_id": args.brand_id,
        "ad_type": "RSA",
        "headlines": [
            "Premium Organic Skincare",
            "Natural Ingredients, Real Results",
            "Shop High-Quality Products",
            "30-Day Money-Back Guarantee",
            "Free Shipping on Orders $50+",
            "Dermatologist-Approved",
            "Join 50,000+ Happy Customers",
            "Cruelty-Free and Eco-Friendly",
            "Expert-Formulated Skincare",
            "Transform Your Skin Today",
            "Affordable Luxury Beauty",
            "Science-Backed Formulations",
            "Your Skin's New Best Friend",
            "Visible Results in 2 Weeks",
            "Premium Quality, Low Price"
        ],
        "descriptions": [
            "Natural ingredients dermatologist tested cruelty-free eco-friendly.",
            "Free shipping all orders 30-day guarantee no questions asked.",
            "Trusted by thousands of customers average rating 4.8 stars.",
            "Clinically proven reduce acne wrinkles dark spots results guaranteed."
        ],
        "image_width": 1200,
        "image_source": "professional_photographer",
        "color_graded": True,
        "text_elements": [
            {"font_size": 18, "contrast_ratio": 8.5},
            {"font_size": 14, "contrast_ratio": 6.2},
        ],
        "text_overlay_percent": 15,
        "colors_used": ["#0066CC", "#FFFFFF", "#333333"],
        "ai_generated": False,
        "logo_present": True,
        "product_visible": True,
        "brand_config": {
            "color_palette": ["#0066CC", "#FFFFFF", "#333333"],
            "forbidden_colors": ["#FF00FF", "#00FF00"],
            "locked_elements": ["logo", "product"]
        }
    }

    pipeline = QCPipeline(creative_data)
    report = pipeline.run_all_checks()

    # Output report
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"QC report saved to {args.output}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
QC Pipeline for Meta Ads Creative Producer

Automated quality control for generated ad creatives using Gemini Vision AI.
Scores images on 6 criteria and determines pass/fail status.

Functions:
- run_qc: Run full QC pipeline on an image
- check_text_density: Detect and measure text coverage
- overall_verdict: Determine pass/fail and generate report
"""

import argparse
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import base64

import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QCPipeline:
    """Automated quality control for generated ad creatives."""

    # QC criteria definitions
    CRITERIA = {
        1: {
            "name": "Professional Quality",
            "description": "Does it look like a real, polished ad?"
        },
        2: {
            "name": "Text Readability",
            "description": "Can you read all badge/overlay text clearly?"
        },
        3: {
            "name": "Text Density",
            "description": "Is text covering more than 20% of image area?",
            "type": "pass_fail"
        },
        4: {
            "name": "Color Consistency",
            "description": "Does the palette make sense as a unified design?"
        },
        5: {
            "name": "Artifacts/Distortions",
            "description": "Any AI-generation weirdness?"
        },
        6: {
            "name": "Brand Integrity",
            "description": "Product imagery and logo untouched?"
        },
    }

    MODE_B_CRITERIA = {
        7: {
            "name": "Brand Identity",
            "description": "Does it clearly read as YOUR brand (not generic)?"
        },
        8: {
            "name": "Zero Competitor Trace",
            "description": "Any remnant of competitor branding?",
            "type": "pass_fail"
        },
    }

    def __init__(self, gemini_api_key: str):
        """
        Initialize QC pipeline.

        Args:
            gemini_api_key: API key for Gemini Vision
        """
        self.gemini_api_key = gemini_api_key
        self.gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models"

    def _call_gemini_vision(self, image_path: str, prompt: str) -> str:
        """
        Call Gemini Vision to analyze an image.

        Args:
            image_path: Path to the image file
            prompt: Analysis prompt

        Returns:
            Model response text
        """
        try:
            with open(image_path, "rb") as img_file:
                image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")

            # Determine MIME type
            mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

            request_payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": image_data
                                }
                            },
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,  # Lower temperature for consistent analysis
                    "topK": 40,
                    "topP": 0.95,
                },
            }

            headers = {"Content-Type": "application/json"}
            url = f"{self.gemini_endpoint}/gemini-pro-vision:generateContent?key={self.gemini_api_key}"

            response = requests.post(url, json=request_payload, headers=headers, timeout=60)
            response.raise_for_status()

            response_data = response.json()

            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            return part["text"]

            return ""

        except Exception as e:
            logger.error(f"Gemini Vision call failed: {e}")
            return ""

    def check_text_density(self, image_path: str) -> Dict:
        """
        Check text coverage (density) in image.

        Args:
            image_path: Path to the image

        Returns:
            Dict with percentage and pass/fail status
        """
        prompt = """Analyze this image and estimate the percentage of the image area covered by text overlays, badges, and logos with text.

Text includes:
- Badge overlays (price, discount, social proof)
- CTA text on image
- Logo text (brand name in logo)
- Any watermarks with text

Text does NOT include:
- Product packaging text (part of physical product)
- Incidental text in background (store signs, etc.)

Provide your analysis in this format:
TEXT_COVERAGE_PERCENTAGE: [0-100]%
TEXT_ELEMENTS: [list each text element found]
ASSESSMENT: [brief assessment of coverage level]
PASSES_20PCT_LIMIT: [YES or NO]"""

        analysis = self._call_gemini_vision(image_path, prompt)

        # Parse response
        result = {
            "raw_analysis": analysis,
            "passes_20pct": False,
            "estimated_percentage": None,
        }

        try:
            lines = analysis.split("\n")
            for line in lines:
                if "TEXT_COVERAGE_PERCENTAGE:" in line:
                    pct_str = line.split(":")[-1].strip().replace("%", "").strip()
                    result["estimated_percentage"] = float(pct_str)
                if "PASSES_20PCT_LIMIT:" in line:
                    result["passes_20pct"] = "YES" in line.upper()
        except Exception as e:
            logger.warning(f"Error parsing text density response: {e}")

        return result

    def run_qc(self, image_path: str, brand_config: Dict, mode: str = "A") -> Dict:
        """
        Run full QC pipeline on an image.

        Args:
            image_path: Path to the image
            brand_config: Brand configuration
            mode: 'A' for Mode A, 'B' for Mode B

        Returns:
            Dict with QC scores and verdict
        """
        if not os.path.exists(image_path):
            return {
                "passed": False,
                "error": f"Image file not found: {image_path}",
                "scores": {}
            }

        logger.info(f"Running QC pipeline on: {image_path}")

        # Prompt for scoring
        scoring_prompt = f"""Analyze this ad creative on the following criteria. Score each 1-10 (unless otherwise noted).

SCORING CRITERIA:

1. Professional Quality (1-10): Does it look like a real, polished ad? Evaluate composition, lighting, clarity, polish level.

2. Text Readability (1-10): Can you read all badge/overlay text clearly? Check for overlapping, cut-off, garbled, or too-small text.

3. Text Density (1-10, BUT PASS/FAIL): Estimate percentage of image covered by text. ≤20% = PASS, >20% = FAIL (automatic fail regardless of other scores).

4. Color Consistency (1-10): Does the palette make sense as a unified design? Colors harmonize, no jarring contrasts.

5. Artifacts/Distortions (1-10): Any AI-generation weirdness? Extra fingers, melted text, warped edges, uncanny faces?

6. Brand Integrity (1-10): Are product imagery and logo untouched? Is compliance text preserved?

Provide scores in this format:
CRITERION_1: [score] [brief reasoning]
CRITERION_2: [score] [brief reasoning]
CRITERION_3: [PASS/FAIL] [percentage]% coverage [brief reasoning]
CRITERION_4: [score] [brief reasoning]
CRITERION_5: [score] [brief reasoning]
CRITERION_6: [score] [brief reasoning]

OVERALL_FEEDBACK: [brief overall assessment]"""

        # Add Mode B criteria if applicable
        if mode == "B":
            scoring_prompt += """\n\n7. Brand Identity (1-10): Does it clearly read as YOUR brand (not generic)? Evaluate logo visibility, color scheme, overall brand presence.

8. Zero Competitor Trace (PASS/FAIL): Is there ANY remnant of competitor branding? Logo, product, exact color scheme, or branded elements?

CRITERION_7: [score] [brief reasoning]
CRITERION_8: [PASS/FAIL] [brief reasoning]"""

        analysis = self._call_gemini_vision(image_path, scoring_prompt)

        # Parse scores
        scores = {}
        criteria_count = 8 if mode == "B" else 6
        text_density_pass = None

        try:
            lines = analysis.split("\n")
            for i in range(1, criteria_count + 1):
                for line in lines:
                    if f"CRITERION_{i}:" in line:
                        content = line.split(":", 1)[-1].strip()

                        if i == 3:  # Text density (pass/fail)
                            scores[f"criterion_{i}"] = {
                                "name": self.CRITERIA[i]["name"],
                                "value": "PASS" if "PASS" in content.upper() else "FAIL",
                                "reasoning": content
                            }
                            text_density_pass = "PASS" in content.upper()
                        elif i == 8 and mode == "B":  # Competitor trace
                            scores[f"criterion_{i}"] = {
                                "name": self.MODE_B_CRITERIA[i]["name"],
                                "value": "PASS" if "PASS" in content.upper() else "FAIL",
                                "reasoning": content
                            }
                        else:
                            try:
                                score_val = float(content.split()[0])
                                scores[f"criterion_{i}"] = {
                                    "name": self.CRITERIA.get(i, {}).get("name", f"Criterion {i}"),
                                    "value": score_val,
                                    "reasoning": content
                                }
                            except (ValueError, IndexError):
                                logger.warning(f"Could not parse score for criterion {i}: {content}")
        except Exception as e:
            logger.error(f"Error parsing QC scores: {e}")

        # Determine verdict
        verdict = self.overall_verdict(scores, mode, text_density_pass)

        result = {
            "image_path": image_path,
            "mode": mode,
            "scores": scores,
            "text_density_pass": text_density_pass,
            "passed": verdict["passed"],
            "average_score": verdict["average"],
            "details": verdict,
            "raw_analysis": analysis,
            "qc_timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"QC Complete: {'PASS' if result['passed'] else 'FAIL'} (avg score: {result['average_score']})")

        return result

    def overall_verdict(
        self,
        scores: Dict,
        mode: str = "A",
        text_density_pass: bool = True
    ) -> Tuple[bool, float, Dict]:
        """
        Determine pass/fail verdict based on scores.

        Args:
            scores: Dictionary of criterion scores
            mode: 'A' or 'B'
            text_density_pass: Whether text density check passed

        Returns:
            Tuple of (passed, average_score, details_dict)
        """
        # Text density is automatic fail
        if not text_density_pass:
            return {
                "passed": False,
                "average": 0.0,
                "reason": "AUTOMATIC FAIL: Text density exceeds 20% limit",
                "text_density_exceeded": True
            }

        # Calculate average of numeric scores (exclude pass/fail)
        numeric_scores = []
        for key, score_data in scores.items():
            if isinstance(score_data.get("value"), (int, float)):
                numeric_scores.append(score_data["value"])

        average = sum(numeric_scores) / len(numeric_scores) if numeric_scores else 0.0

        # Check pass criteria
        details = {
            "average": average,
            "numeric_scores_count": len(numeric_scores),
            "text_density_exceeded": False
        }

        # Mode A: average >= 7.0, all individual >= 6.0
        if mode == "A":
            all_above_6 = all(s >= 6.0 for s in numeric_scores)
            passed = average >= 7.0 and all_above_6
            details["reason"] = (
                "PASS: Average >= 7.0 and all criteria >= 6.0"
                if passed
                else f"FAIL: Average {average:.1f} or individual criterion < 6.0"
            )
            details["passed"] = passed
            return details

        # Mode B: average >= 7.0, all individual >= 6.0, brand identity >= 8.0, competitor trace = PASS
        elif mode == "B":
            all_above_6 = all(s >= 6.0 for s in numeric_scores)

            # Check brand identity (criterion 7)
            brand_identity_score = scores.get("criterion_7", {}).get("value", 0)
            brand_identity_ok = isinstance(brand_identity_score, (int, float)) and brand_identity_score >= 8.0

            # Check competitor trace (criterion 8)
            competitor_trace = scores.get("criterion_8", {}).get("value", "FAIL")
            competitor_trace_ok = competitor_trace == "PASS"

            passed = (
                average >= 7.0 and
                all_above_6 and
                brand_identity_ok and
                competitor_trace_ok
            )

            if not passed:
                reasons = []
                if average < 7.0:
                    reasons.append(f"average {average:.1f} < 7.0")
                if not all_above_6:
                    reasons.append("some criteria < 6.0")
                if not brand_identity_ok:
                    reasons.append(f"brand identity {brand_identity_score} < 8.0")
                if not competitor_trace_ok:
                    reasons.append("competitor trace FAIL")

                details["reason"] = f"FAIL: {', '.join(reasons)}"
            else:
                details["reason"] = "PASS: All criteria met for Mode B"

            details["passed"] = passed
            details["brand_identity_score"] = brand_identity_score
            details["competitor_trace"] = competitor_trace
            return details

        return {
            "passed": False,
            "average": average,
            "reason": "Unknown mode"
        }


def main():
    """Command-line interface for QC pipeline."""
    parser = argparse.ArgumentParser(
        description="QC Pipeline for Meta Ads Creative Producer"
    )
    parser.add_argument(
        "--gemini-key",
        required=True,
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to image to check"
    )
    parser.add_argument(
        "--mode",
        choices=["A", "B"],
        default="A",
        help="Mode A or Mode B (default: A)"
    )
    parser.add_argument(
        "--brand-config",
        help="Path to brand config JSON (optional)"
    )
    parser.add_argument(
        "--output",
        help="Save QC report to JSON file"
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.gemini_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not provided or set in environment")
        return 1

    # Load brand config if provided
    brand_config = {}
    if args.brand_config:
        try:
            with open(args.brand_config, "r") as f:
                brand_config = json.load(f)
        except Exception as e:
            print(f"Error loading brand config: {e}")
            return 1

    # Initialize QC pipeline
    qc = QCPipeline(api_key)

    # Run QC
    result = qc.run_qc(args.image, brand_config, mode=args.mode)

    # Save report if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"QC report saved to: {args.output}")

    # Print result
    print(f"\nQC Result: {'PASS' if result['passed'] else 'FAIL'}")
    print(f"Average Score: {result['average_score']:.1f}/10")
    print(f"Details: {json.dumps(result['details'], indent=2)}")

    return 0 if result['passed'] else 1


if __name__ == "__main__":
    exit(main())

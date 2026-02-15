#!/usr/bin/env python3
"""
Creative Generation Helper for Meta Ads Creative Producer

Handles the generation of ad creative assets using Gemini Vision AI.
Supports Mode A (edit existing images) and Mode B (generate from scratch).

Functions:
- build_prompt: Construct detailed Gemini prompts with brand constraints
- generate_image: Call Gemini API to generate/edit images
- save_with_metadata: Save images with metadata to output directory
"""

import argparse
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple
import base64

import requests


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CreativeGenerator:
    """Handles creative asset generation using Gemini Vision API."""

    def __init__(self, gemini_api_key: str, output_dir: str = "./output"):
        """
        Initialize the creative generator.

        Args:
            gemini_api_key: API key for Gemini Vision
            output_dir: Directory to save generated images
        """
        self.gemini_api_key = gemini_api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models"

    def build_prompt(
        self,
        brand_config: Dict,
        mode: str,
        source_data: Dict,
        variant_params: Optional[Dict] = None
    ) -> str:
        """
        Build a detailed Gemini prompt for creative generation.

        Args:
            brand_config: Brand configuration (locked elements, color palette, banned words)
            mode: 'A' for edit existing, 'B' for generate from scratch
            source_data: Source image info (Mode A) or competitor DNA (Mode B)
            variant_params: Specific variant parameters (background color, text angle, hero element)

        Returns:
            Formatted prompt string for Gemini API
        """
        if variant_params is None:
            variant_params = {}

        prompt_parts = []

        if mode == 'A':
            # Mode A: Edit existing image
            prompt_parts.append(
                f"""You are editing an ad image for the brand '{brand_config.get('brand_name', 'Unknown')}'.

LOCKED ELEMENTS (DO NOT MODIFY):
{json.dumps(brand_config.get('locked_elements', {}), indent=2)}

ELEMENTS TO CHANGE:
- Background: Change to {variant_params.get('background_color', 'a new cohesive background')}
- Badge/Overlay Text: {', '.join(variant_params.get('badge_text', ['New messaging']))}
- Hero Element: {variant_params.get('hero_element', 'Keep existing if not specified')}

REQUIREMENTS:
1. Keep all locked elements pixel-perfect and unchanged
2. Create a cohesive color palette that harmonizes with {variant_params.get('background_color', 'the new background')}
3. Text must be clear and readable, covering ≤20% of image area
4. Maintain professional ad quality
5. No text outside of specified badges/overlays

SPECIFIC INSTRUCTIONS:
- Aspect ratio: {variant_params.get('aspect_ratio', '1080x1080')}
- Generate at 2048x2048 resolution for maximum quality
- Ensure brand logo remains in original position with no distortion
"""
            )

        elif mode == 'B':
            # Mode B: Generate from scratch
            prompt_parts.append(
                f"""You are creating a new ad image for the brand '{brand_config.get('brand_name', 'Unknown')}'.
This ad is inspired by competitor creative DNA but will be entirely your brand's content.

CREATIVE DNA FROM COMPETITOR ANALYSIS:
{json.dumps(source_data.get('creative_dna', {}), indent=2)}

YOUR BRAND ELEMENTS:
- Brand Name: {brand_config.get('brand_name')}
- Product Description: {brand_config.get('locked_elements', {}).get('product_images', ['Product image'])[0] if brand_config.get('locked_elements', {}).get('product_images') else 'Product'}
- Logo Style: {brand_config.get('locked_elements', {}).get('logo', 'Professional brand logo')}
- Brand Colors: {json.dumps(brand_config.get('color_palette', {}).get('backgrounds', []), indent=2)}

CREATE AN AD WITH:
1. Layout composition: {source_data.get('creative_dna', {}).get('layout', 'Product-centered with supporting elements')}
2. Visual style: {source_data.get('creative_dna', {}).get('visual_style', 'Professional studio')}
3. Color approach: {source_data.get('creative_dna', {}).get('color_mood', 'Professional and trustworthy')}
4. Text overlay approach: {source_data.get('creative_dna', {}).get('text_overlay', 'Minimal text, clear readability')}
5. Hero element: {variant_params.get('hero_element', source_data.get('creative_dna', {}).get('hero_type', 'Professional subject matter'))}

CRITICAL REQUIREMENTS:
1. 100% YOUR BRAND - zero trace of competitor branding
2. Use your product, your logo, your colors
3. Professional quality that looks like a real ad
4. Text ≤20% of image area
5. Safe zones respected for Stories/Reels (if applicable)
6. Text must be readable and strategically placed

FORBIDDEN:
- No competitor logo, product, or brand name
- No exact color matching to competitor
- No reuse of competitor's copy or messaging

Generate at 2048x2048 resolution."""
            )

        # Add banned words warning
        banned_words = brand_config.get('banned_words', [])
        if banned_words:
            prompt_parts.append(
                f"\nBAN THESE WORDS (Meta will reject): {', '.join(banned_words)}\n"
                "Do not include any of these terms in badge text or overlays."
            )

        # Add specific variant instructions
        if variant_params.get('text_angle'):
            prompt_parts.append(
                f"\nText angle/messaging focus: {variant_params.get('text_angle')}"
            )

        return "\n".join(prompt_parts)

    def generate_image(
        self,
        prompt: str,
        source_image_path: Optional[str] = None,
        aspect_ratio: str = "1080x1080",
        resolution: str = "2K"
    ) -> Tuple[Optional[bytes], Dict]:
        """
        Generate or edit an image using Gemini Vision API.

        Args:
            prompt: Detailed prompt for image generation
            source_image_path: Path to source image (Mode A only, optional for Mode B)
            aspect_ratio: Target aspect ratio (e.g., "1080x1080", "1080x1920")
            resolution: Output resolution ('1K' for 1024x1024, '2K' for 2048x2048)

        Returns:
            Tuple of (image_bytes, metadata_dict)
        """
        try:
            # Prepare API request
            headers = {
                "Content-Type": "application/json",
            }

            # Build the request payload
            request_payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                },
            }

            # Add source image if Mode A (edit)
            if source_image_path:
                if not os.path.exists(source_image_path):
                    logger.error(f"Source image not found: {source_image_path}")
                    return None, {"error": "Source image not found"}

                with open(source_image_path, "rb") as img_file:
                    image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
                    request_payload["contents"][0]["parts"].insert(0, {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_data
                        }
                    })

            # Call Gemini API
            model = "gemini-pro-vision" if source_image_path else "gemini-pro"
            url = f"{self.gemini_endpoint}/{model}:generateContent?key={self.gemini_api_key}"

            logger.info(f"Calling Gemini API: {model}")
            response = requests.post(url, json=request_payload, headers=headers, timeout=60)
            response.raise_for_status()

            response_data = response.json()

            # Extract image from response
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]

                # Handle image response
                if "content" in candidate and "parts" in candidate["content"]:
                    for part in candidate["content"]["parts"]:
                        if "inlineData" in part:
                            image_bytes = base64.standard_b64decode(
                                part["inlineData"]["data"]
                            )
                            metadata = {
                                "model": model,
                                "aspect_ratio": aspect_ratio,
                                "resolution": resolution,
                                "size_bytes": len(image_bytes),
                                "generated_at": datetime.utcnow().isoformat(),
                                "status": "success"
                            }
                            return image_bytes, metadata

            logger.warning("No image data in Gemini response")
            return None, {"error": "No image data in response", "status": "failed"}

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None, {"error": str(e), "status": "failed"}
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None, {"error": str(e), "status": "failed"}

    def save_with_metadata(
        self,
        image_bytes: bytes,
        metadata: Dict,
        output_dir: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """
        Save image with metadata to output directory.

        Args:
            image_bytes: Raw image data
            metadata: Image metadata (QC scores, source info, etc.)
            output_dir: Override default output directory
            filename: Custom filename (default: auto-generated)

        Returns:
            Tuple of (image_path, metadata_dict)
        """
        try:
            save_dir = Path(output_dir) if output_dir else self.output_dir
            save_dir.mkdir(parents=True, exist_ok=True)

            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"creative_{timestamp}.png"

            image_path = save_dir / filename

            # Write image file
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Image saved: {image_path}")

            # Write metadata file
            metadata_filename = image_path.stem + "_metadata.json"
            metadata_path = save_dir / metadata_filename

            full_metadata = {
                "filename": filename,
                "filepath": str(image_path),
                "generation_metadata": metadata,
                "saved_at": datetime.utcnow().isoformat()
            }

            with open(metadata_path, "w") as f:
                json.dump(full_metadata, f, indent=2)
            logger.info(f"Metadata saved: {metadata_path}")

            return str(image_path), full_metadata

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return "", {"error": str(e), "status": "save_failed"}


def main():
    """Command-line interface for creative generation."""
    parser = argparse.ArgumentParser(
        description="Generate Meta ad creatives using Gemini Vision AI"
    )
    parser.add_argument(
        "--gemini-key",
        required=True,
        help="Gemini API key (or set GEMINI_API_KEY env var)"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["A", "B"],
        help="Generation mode: A (edit existing) or B (generate from scratch)"
    )
    parser.add_argument(
        "--brand-config",
        required=True,
        help="Path to brand config JSON file"
    )
    parser.add_argument(
        "--source-image",
        help="Path to source image (required for Mode A)"
    )
    parser.add_argument(
        "--competitor-dna",
        help="Path to competitor creative DNA JSON (Mode B)"
    )
    parser.add_argument(
        "--background-color",
        help="Target background color (Mode A variant parameter)"
    )
    parser.add_argument(
        "--badge-text",
        nargs="+",
        help="Badge/overlay text (space-separated, quoted)"
    )
    parser.add_argument(
        "--hero-element",
        help="Hero element description for swap"
    )
    parser.add_argument(
        "--text-angle",
        help="Text angle/messaging focus (e.g., 'Price', 'Social Proof')"
    )
    parser.add_argument(
        "--aspect-ratio",
        default="1080x1080",
        help="Target aspect ratio (default: 1080x1080)"
    )
    parser.add_argument(
        "--resolution",
        choices=["1K", "2K", "4K"],
        default="2K",
        help="Output resolution (default: 2K)"
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Output directory for generated images (default: ./output)"
    )

    args = parser.parse_args()

    # Get API key from argument or environment
    api_key = args.gemini_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not provided or set in environment")
        return 1

    # Load brand config
    try:
        with open(args.brand_config, "r") as f:
            brand_config = json.load(f)
    except Exception as e:
        print(f"Error loading brand config: {e}")
        return 1

    # Load variant parameters
    variant_params = {
        "background_color": args.background_color,
        "badge_text": args.badge_text or [],
        "hero_element": args.hero_element,
        "text_angle": args.text_angle,
        "aspect_ratio": args.aspect_ratio,
    }

    # Load source data
    source_data = {}
    if args.mode == "B" and args.competitor_dna:
        try:
            with open(args.competitor_dna, "r") as f:
                source_data = json.load(f)
        except Exception as e:
            print(f"Error loading competitor DNA: {e}")
            return 1

    # Initialize generator
    generator = CreativeGenerator(api_key, args.output_dir)

    # Build prompt
    prompt = generator.build_prompt(brand_config, args.mode, source_data, variant_params)
    logger.info(f"Prompt built for Mode {args.mode}")

    # Generate image
    image_bytes, metadata = generator.generate_image(
        prompt,
        source_image_path=args.source_image,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution
    )

    if not image_bytes:
        print(f"Generation failed: {metadata}")
        return 1

    # Save with metadata
    filepath, full_metadata = generator.save_with_metadata(
        image_bytes,
        metadata,
        output_dir=args.output_dir
    )

    if not filepath:
        print(f"Save failed: {full_metadata}")
        return 1

    print(f"Success: {filepath}")
    print(f"Metadata: {json.dumps(full_metadata, indent=2)}")
    return 0


if __name__ == "__main__":
    exit(main())

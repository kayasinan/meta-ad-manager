"""
Gemini Vision API helper for analyzing ad creative images.
Extracts color analysis, text density, and creative DNA.
"""

import requests
import os
import json
import base64
from typing import Dict, Any, Optional
from pathlib import Path

class GeminiVisionAnalyzer:
    """Analyzer for ad creative using Gemini Vision API."""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def __init__(self, api_key: str):
        """
        Initialize Gemini Vision analyzer.

        Args:
            api_key (str): Google Gemini API key

        Raises:
            ValueError: If API key is empty
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_key = api_key

    def load_image_as_base64(self, image_path: str) -> str:
        """
        Load image file and encode as base64.

        Args:
            image_path (str): Path to image file

        Returns:
            str: Base64-encoded image data

        Raises:
            FileNotFoundError: If image file not found
            ValueError: If file is not a valid image format
        """
        valid_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        file_ext = Path(image_path).suffix.lower()

        if file_ext not in valid_formats:
            raise ValueError(f"Unsupported image format: {file_ext}. Supported: {valid_formats}")

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return base64.standard_b64encode(image_data).decode('utf-8')
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image_path}")

    def _call_gemini(self, prompt: str, image_base64: str, media_type: str = "image/jpeg") -> str:
        """
        Call Gemini Vision API with image and prompt.

        Args:
            prompt (str): Analysis prompt
            image_base64 (str): Base64-encoded image
            media_type (str): MIME type of image

        Returns:
            str: API response text

        Raises:
            requests.RequestException: If API call fails
        """
        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': prompt
                        },
                        {
                            'inline_data': {
                                'mime_type': media_type,
                                'data': image_base64
                            }
                        }
                    ]
                }
            ]
        }

        params = {'key': self.api_key}

        try:
            response = requests.post(
                self.API_URL,
                json=payload,
                headers=headers,
                params=params,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0].get('text', '')

            raise ValueError("Unexpected API response structure")

        except requests.RequestException as e:
            raise requests.RequestException(f"Gemini API call failed: {e}")

    def analyze_creative(
        self,
        image_path_or_url: str,
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Analyze ad creative image.

        Args:
            image_path_or_url (str): Local file path or URL to image
            analysis_type (str): Type of analysis ('comprehensive', 'color', 'text_density', 'andromeda')

        Returns:
            Dict: Analysis results

        Raises:
            ValueError: If analysis type is invalid
        """
        if analysis_type == "comprehensive":
            return self._comprehensive_analysis(image_path_or_url)
        elif analysis_type == "color":
            return self._color_analysis(image_path_or_url)
        elif analysis_type == "text_density":
            return self._text_density_analysis(image_path_or_url)
        elif analysis_type == "andromeda":
            return self._andromeda_classification(image_path_or_url)
        else:
            raise ValueError(f"Unknown analysis_type: {analysis_type}")

    def _comprehensive_analysis(self, image_path_or_url: str) -> Dict[str, Any]:
        """Run comprehensive creative analysis."""
        # Load image
        if image_path_or_url.startswith('http'):
            # For URLs, we'd need different handling
            image_base64 = self._load_image_from_url(image_path_or_url)
        else:
            image_base64 = self.load_image_as_base64(image_path_or_url)

        prompt = """Analyze this ad creative and provide a detailed assessment. Return a JSON object with:
{
  "format": "image|video|carousel|collection",
  "subject_matter": "description of what's shown",
  "people_present": true/false,
  "text_count": number,
  "text_coverage_estimate": percentage,
  "primary_colors": ["hex codes"],
  "mood": "professional|playful|urgent|luxurious|minimal|other",
  "production_quality": "professional|amateur|ugc|studio|polished",
  "target_audience_inferred": "description",
  "brand_elements_visible": true/false,
  "likely_cta": "call to action inferred",
  "design_notes": "key observations"
}"""

        response_text = self._call_gemini(prompt, image_base64)
        return json.loads(response_text)

    def _color_analysis(self, image_path_or_url: str) -> Dict[str, Any]:
        """Analyze colors in creative."""
        if image_path_or_url.startswith('http'):
            image_base64 = self._load_image_from_url(image_path_or_url)
        else:
            image_base64 = self.load_image_as_base64(image_path_or_url)

        prompt = """Analyze the colors in this ad creative. Return a JSON object with:
{
  "background_colors": ["hex codes of dominant background colors"],
  "badge_overlay_colors": ["hex codes of badges, price tags, discount labels"],
  "accent_colors": ["hex codes of secondary accent colors"],
  "palette_type": "warm|cool|neutral|high_contrast|monochrome",
  "mood": "professional|playful|urgent|luxurious|minimal",
  "contrast_level": "high|medium|low",
  "text_color": "hex code",
  "text_treatment": {
    "font_style": "serif|sans_serif|script|custom",
    "relative_size": "large|medium|small",
    "color_contrast": "high|medium|low"
  },
  "color_psychology": "description of emotional impact"
}"""

        response_text = self._call_gemini(prompt, image_base64)
        return json.loads(response_text)

    def _text_density_analysis(self, image_path_or_url: str) -> Dict[str, Any]:
        """Analyze text density and coverage."""
        if image_path_or_url.startswith('http'):
            image_base64 = self._load_image_from_url(image_path_or_url)
        else:
            image_base64 = self.load_image_as_base64(image_path_or_url)

        prompt = """Analyze the text coverage in this ad creative. Return a JSON object with:
{
  "text_coverage_percentage": number (0-100),
  "text_element_count": number,
  "text_elements": [
    {
      "type": "headline|badge|price|cta|other",
      "content": "text content",
      "placement": "center|top_left|top_right|bottom_left|bottom_right|full_width",
      "size": "large|medium|small"
    }
  ],
  "text_placement_description": "description of where text is positioned",
  "meta_compliance": {
    "passes_20_percent_rule": true/false,
    "recommendation": "description"
  },
  "density_assessment": "text_light|text_medium|text_heavy",
  "performance_outlook": "description of likely performance"
}"""

        response_text = self._call_gemini(prompt, image_base64)
        return json.loads(response_text)

    def _andromeda_classification(self, image_path_or_url: str) -> Dict[str, Any]:
        """Classify ad using Andromeda visual clustering."""
        if image_path_or_url.startswith('http'):
            image_base64 = self._load_image_from_url(image_path_or_url)
        else:
            image_base64 = self.load_image_as_base64(image_path_or_url)

        prompt = """Classify this ad using Meta's Andromeda visual clustering model. Return a JSON object with:
{
  "visual_style_cluster": "product_only|lifestyle|ugc|studio|text_heavy|illustration|video_native",
  "color_sub_cluster": "warm|cool|neutral|high_contrast|monochrome",
  "cluster_explanation": "why this classification",
  "style_confidence": 0.0-1.0,
  "color_confidence": 0.0-1.0,
  "similar_high_performers": "description of what similar ads typically do well",
  "diversification_opportunity": "where you could test different approaches"
}"""

        response_text = self._call_gemini(prompt, image_base64)
        return json.loads(response_text)

    def classify_andromeda(self, image_path_or_url: str) -> Dict[str, Any]:
        """
        Classify ad into Andromeda cluster.

        Args:
            image_path_or_url (str): Path or URL to image

        Returns:
            Dict: Cluster classification
        """
        return self._andromeda_classification(image_path_or_url)

    def check_text_density(self, image_path_or_url: str) -> Dict[str, Any]:
        """
        Check text density and compliance with Meta's 20% rule.

        Args:
            image_path_or_url (str): Path or URL to image

        Returns:
            Dict: Text density analysis
        """
        analysis = self._text_density_analysis(image_path_or_url)
        return {
            'percentage': analysis.get('text_coverage_percentage'),
            'passes_meta_rule': analysis.get('meta_compliance', {}).get('passes_20_percent_rule'),
            'elements': analysis.get('text_elements'),
            'recommendation': analysis.get('meta_compliance', {}).get('recommendation')
        }

    def _load_image_from_url(self, url: str) -> str:
        """
        Load image from URL and encode as base64.

        Args:
            url (str): Image URL

        Returns:
            str: Base64-encoded image

        Raises:
            requests.RequestException: If URL fetch fails
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_data = response.content
            return base64.standard_b64encode(image_data).decode('utf-8')
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to load image from URL: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Gemini Vision Analysis Tool')
    parser.add_argument('--api-key', required=True, help='Google Gemini API key')
    parser.add_argument('--image', required=True, help='Path to image file or URL')
    parser.add_argument('--analysis', default='comprehensive',
                       choices=['comprehensive', 'color', 'text_density', 'andromeda'],
                       help='Type of analysis')

    args = parser.parse_args()

    analyzer = GeminiVisionAnalyzer(args.api_key)
    result = analyzer.analyze_creative(args.image, args.analysis)

    print(json.dumps(result, indent=2))

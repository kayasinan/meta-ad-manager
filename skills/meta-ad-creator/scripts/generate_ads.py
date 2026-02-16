#!/usr/bin/env python3
"""
Meta Ad Creative Generator - DALL-E 3
Generate production-ready ad variants with swappable elements.

Usage:
  # Single ad
  python3 generate_ads.py --brand "PetBucket" --product "NexGard" \
    --subject "Golden Retriever" --color "Navy Blue" \
    --headline "Wag More, Worry Less" --output ./output/

  # Batch from config
  python3 generate_ads.py --config variants.json --output ./output/

  # With custom benefits and badge
  python3 generate_ads.py --brand "PetBucket" --subject "Corgi" \
    --color "Orange" --headline "Protect Your Furry Friend" \
    --benefits "Vet Recommended,Trusted Brands,75% Off Vet Prices" \
    --badge "FREE SHIPPING" --output ./output/

Requires: OPENAI_API_KEY environment variable
"""

import argparse
import json
import os
import sys
import time
import base64
from pathlib import Path

try:
    import openai
except ImportError:
    print("Installing openai...")
    os.system(f"{sys.executable} -m pip install openai -q")
    import openai


def build_prompt(config, variant):
    """Build DALL-E 3 prompt from config and variant."""
    
    brand = config.get("brand", "Brand")
    product_type = config.get("product_type", "product")
    product_items = config.get("product_items", "")
    cta = config.get("cta", "SHOP NOW")
    cta_color = config.get("cta_color", "green")
    badge = config.get("badge", "")
    benefits = config.get("benefits", [])
    
    subject = variant.get("subject", "product")
    color = variant.get("color", "white")
    headline = variant.get("headline", brand)
    style_note = variant.get("style", "photorealistic")
    
    # Build benefits string
    benefits_str = ""
    if benefits:
        benefits_list = ", ".join(benefits[:3])
        benefits_str = f"benefits listed with checkmark icons: {benefits_list},"
    
    # Build product items string
    products_str = ""
    if product_items:
        products_str = f"{product_items} displayed prominently,"
    
    # Build badge string
    badge_str = ""
    if badge:
        badge_str = f'"{badge}" promotional badge in top-left corner,'
    
    prompt = (
        f'Professional {product_type} advertisement for {brand}, '
        f'{color} solid color background, '
        f'{subject} prominently featured, {style_note}, '
        f'{products_str} '
        f'{brand} logo in top-right corner, '
        f'headline text "{headline}" in bold modern sans-serif font, '
        f'{cta} button in {cta_color} at bottom, '
        f'{badge_str} '
        f'{benefits_str} '
        f'clean professional Meta ad format, square 1:1 aspect ratio, '
        f'high production value, studio quality'
    )
    
    # Clean up double spaces
    prompt = " ".join(prompt.split())
    return prompt


def generate_image(client, prompt, size="1024x1024", quality="hd", style="natural"):
    """Generate a single image via DALL-E 3."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            style=style,
            n=1,
            response_format="b64_json"
        )
        return base64.b64decode(response.data[0].b64_json), response.data[0].revised_prompt
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None, None


def save_image(image_data, filepath):
    """Save image bytes to file."""
    with open(filepath, "wb") as f:
        f.write(image_data)


def main():
    parser = argparse.ArgumentParser(description="Generate Meta ad variants with DALL-E 3")
    parser.add_argument("--config", help="JSON config file with brand + variants")
    parser.add_argument("--brand", help="Brand name")
    parser.add_argument("--product", help="Product name/description")
    parser.add_argument("--product-type", default="product", help="Product category (e.g., 'pet product')")
    parser.add_argument("--subject", help="Main visual subject (e.g., 'Golden Retriever')")
    parser.add_argument("--color", help="Background color")
    parser.add_argument("--headline", help="Ad headline text")
    parser.add_argument("--benefits", help="Comma-separated benefits")
    parser.add_argument("--badge", help="Promotional badge text")
    parser.add_argument("--cta", default="SHOP NOW", help="CTA button text")
    parser.add_argument("--filename", help="Output filename")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--quality", default="hd", choices=["hd", "standard"])
    parser.add_argument("--style", default="natural", choices=["natural", "vivid"])
    parser.add_argument("--size", default="1024x1024", choices=["1024x1024", "1792x1024", "1024x1792"])
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between API calls (seconds)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without generating")
    
    args = parser.parse_args()
    
    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build config from file or CLI args
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        variants = config.get("variants", [])
    elif args.brand and args.subject:
        config = {
            "brand": args.brand,
            "product_type": args.product_type,
            "product_items": args.product or "",
            "cta": args.cta,
            "cta_color": "green",
            "badge": args.badge or "",
            "benefits": args.benefits.split(",") if args.benefits else []
        }
        filename = args.filename or f"ad-{args.subject.lower().replace(' ', '-')}-{args.color.lower().replace(' ', '-')}.png"
        variants = [{
            "subject": args.subject,
            "color": args.color or "white",
            "headline": args.headline or args.brand,
            "filename": filename
        }]
    else:
        parser.error("Provide --config OR (--brand and --subject)")
        return
    
    # Initialize OpenAI client
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print("❌ OPENAI_API_KEY not set")
        sys.exit(1)
    
    client = openai.OpenAI(api_key=api_key) if not args.dry_run else None
    
    # Generate
    total = len(variants)
    success = 0
    prompts_log = {}
    
    print(f"\n=== Generating {total} Ad Variants for {config.get('brand', 'Brand')} ===\n")
    
    for i, variant in enumerate(variants, 1):
        filename = variant.get("filename", f"ad-variant-{i}.png")
        filepath = output_dir / filename
        
        prompt = build_prompt(config, variant)
        
        print(f"[{i}/{total}] {filename}")
        print(f"  Subject: {variant.get('subject')} | Color: {variant.get('color')} | Headline: {variant.get('headline')}")
        
        if args.dry_run:
            print(f"  Prompt: {prompt[:120]}...")
            prompts_log[filename] = prompt
            continue
        
        image_data, revised_prompt = generate_image(
            client, prompt, 
            size=args.size, 
            quality=args.quality, 
            style=args.style
        )
        
        if image_data:
            save_image(image_data, filepath)
            print(f"  ✅ Saved ({len(image_data) / 1024:.0f} KB)")
            prompts_log[filename] = {
                "prompt": prompt,
                "revised_prompt": revised_prompt
            }
            success += 1
        
        if i < total:
            time.sleep(args.delay)
    
    # Save prompts log
    log_path = output_dir / "prompts.json"
    with open(log_path, "w") as f:
        json.dump(prompts_log, f, indent=2)
    
    print(f"\n{'=' * 50}")
    print(f"✅ Generated: {success}/{total}")
    print(f"📁 Output: {output_dir}")
    print(f"📋 Prompts log: {log_path}")
    
    if success > 0 and not args.dry_run:
        print(f"\nRun gallery builder:")
        print(f"  python3 create_gallery.py {output_dir}")


if __name__ == "__main__":
    main()

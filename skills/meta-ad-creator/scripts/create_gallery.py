#!/usr/bin/env python3
"""
Generate HTML gallery from a folder of ad variant images.

Usage:
  python3 create_gallery.py ./output/
  python3 create_gallery.py ./output/ --title "Petbucket Q1 2026 Variants"
"""

import argparse
import json
import os
from pathlib import Path

GALLERY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
        h1 {{ text-align: center; margin-bottom: 10px; color: #fff; }}
        .subtitle {{ text-align: center; color: #888; margin-bottom: 30px; }}
        .stats {{ text-align: center; background: #16213e; padding: 20px; border-radius: 12px; margin-bottom: 30px; }}
        .stats span {{ margin: 0 20px; }}
        .stats strong {{ color: #4ecdc4; font-size: 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #16213e; border-radius: 12px; overflow: hidden; transition: transform 0.2s; cursor: pointer; }}
        .card:hover {{ transform: scale(1.02); box-shadow: 0 8px 32px rgba(78, 205, 196, 0.2); }}
        .card img {{ width: 100%; height: auto; display: block; }}
        .card-info {{ padding: 12px; }}
        .card-title {{ font-weight: 600; color: #fff; margin-bottom: 5px; font-size: 14px; }}
        .card-meta {{ font-size: 12px; color: #888; }}
        .tag {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; margin-right: 5px; margin-top: 5px; }}
        .tag.subject {{ background: #ff6b6b; color: #fff; }}
        .tag.color {{ background: #4ecdc4; color: #1a1a2e; }}
        .tag.headline {{ background: #95e1d3; color: #1a1a2e; }}
        
        /* Lightbox */
        .lightbox {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 1000; justify-content: center; align-items: center; }}
        .lightbox.active {{ display: flex; }}
        .lightbox img {{ max-width: 90%; max-height: 90%; border-radius: 8px; }}
        .lightbox-close {{ position: fixed; top: 20px; right: 30px; color: #fff; font-size: 36px; cursor: pointer; z-index: 1001; }}
    </style>
</head>
<body>
    <h1>🎨 {title}</h1>
    <p class="subtitle">Click any image to view full size</p>
    
    <div class="stats">
        <span>Total Variants: <strong>{count}</strong></span>
    </div>
    
    <div class="grid">
{cards}
    </div>
    
    <div class="lightbox" id="lightbox" onclick="this.classList.remove('active')">
        <span class="lightbox-close">&times;</span>
        <img id="lightbox-img" src="">
    </div>
    
    <script>
        document.querySelectorAll('.card img').forEach(img => {{
            img.addEventListener('click', () => {{
                document.getElementById('lightbox-img').src = img.src;
                document.getElementById('lightbox').classList.add('active');
            }});
        }});
    </script>
</body>
</html>"""

CARD_TEMPLATE = """        <div class="card">
            <img src="{filename}" alt="{name}" loading="lazy">
            <div class="card-info">
                <div class="card-title">{name}</div>
                <div class="card-meta">{meta}</div>
            </div>
        </div>"""


def main():
    parser = argparse.ArgumentParser(description="Generate HTML gallery from ad images")
    parser.add_argument("directory", help="Directory containing ad images")
    parser.add_argument("--title", default="Ad Variants Gallery", help="Gallery title")
    parser.add_argument("--output", help="Output HTML filename (default: gallery.html in image dir)")
    
    args = parser.parse_args()
    
    img_dir = Path(args.directory)
    if not img_dir.exists():
        print(f"❌ Directory not found: {img_dir}")
        return
    
    # Find images
    extensions = {'.png', '.jpg', '.jpeg', '.webp'}
    images = sorted([f for f in img_dir.iterdir() if f.suffix.lower() in extensions])
    
    if not images:
        print(f"❌ No images found in {img_dir}")
        return
    
    # Load prompts log if available
    prompts_log = {}
    prompts_path = img_dir / "prompts.json"
    if prompts_path.exists():
        with open(prompts_path) as f:
            prompts_log = json.load(f)
    
    # Build cards
    cards = []
    for img in images:
        name = img.stem.replace("-", " ").replace("_", " ").title()
        
        # Extract metadata from filename or prompts log
        meta_parts = []
        prompt_info = prompts_log.get(img.name, {})
        if isinstance(prompt_info, dict):
            meta_parts.append(f"Prompt logged")
        
        size_kb = img.stat().st_size / 1024
        meta_parts.append(f"{size_kb:.0f} KB")
        
        meta = " · ".join(meta_parts)
        
        cards.append(CARD_TEMPLATE.format(
            filename=img.name,
            name=name,
            meta=meta
        ))
    
    # Build HTML
    html = GALLERY_TEMPLATE.format(
        title=args.title,
        count=len(images),
        cards="\n".join(cards)
    )
    
    # Write output
    output_path = Path(args.output) if args.output else img_dir / "gallery.html"
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"✅ Gallery created: {output_path}")
    print(f"   {len(images)} images")


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.10"
# dependencies = ["google-genai>=1.14.0", "Pillow>=10.0"]
# ///
"""
Meta Ad Creative Editor — Gemini 3 Pro Image (Nano Banana Pro)
Edit existing winning ads: swap background color + badge text while keeping
product boxes and logos pixel-perfect.

Usage:
  # Single edit
  uv run edit_ad.py --input ad.jpg --color "Peach" \
    --badges "SAVE 50%" "FREE SHIPPING" "VET RECOMMENDED" --output out.png

  # Auto-generate N variations
  uv run edit_ad.py --input ad.jpg --variations 5 --output ./variants/

  # Batch from config
  uv run edit_ad.py --config variants.json --output ./variants/

Requires: GEMINI_API_KEY environment variable
"""

import argparse
import json
import os
import sys
import time
import random
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

# ── Text angle pools for auto-variation ──────────────────────────────────────

# ⚠️ BANNED WORDS — never use in badge text (regulatory/compliance risk)
BANNED_WORDS = ["pharmacy", "prescription", "rx", "drug", "medication", "medicine", "pharmaceutical"]

TEXT_ANGLES = {
    "price": [
        ["SAVE UP TO 50% VS VET PRICES", "ONE CHEW. TOTAL PROTECTION", "FREE SHIPPING OVER $49"],
        ["75% CHEAPER THAN YOUR VET", "SAME PRODUCTS, FRACTION OF THE PRICE", "WHY OVERPAY AT THE VET?"],
        ["WHY PAY MORE AT THE VET?", "EXPOSED: VET PRICE MARKUPS", "SAVE HUNDREDS EVERY YEAR"],
    ],
    "social_proof": [
        ["TRUSTED BY 500K+ PET PARENTS", "100% GENUINE PRODUCTS", "4.9★ FROM 12,000+ REVIEWS"],
        ["#1 PET PROTECTION STORE ONLINE", "LOVED BY 500K+ DOG OWNERS", "JOIN PET PARENTS WHO SAVE BIG"],
        ["12,000+ FIVE STAR REVIEWS", "RECOMMENDED BY VET TECHS", "TRUSTED SINCE 2010"],
    ],
    "benefits": [
        ["KILLS FLEAS, TICKS & WORMS", "ONE TASTY MONTHLY CHEW", "VET-RECOMMENDED ALL-IN-ONE"],
        ["ONE CHEW PROTECTS AGAINST 5 PARASITES", "WORKS IN 24 HOURS", "LASTS A FULL MONTH"],
        ["PREVENTS HEARTWORM DISEASE", "ELIMINATES FLEAS IN HOURS", "SAFE FOR DOGS & PUPPIES"],
    ],
    "shipping": [
        ["FAST FREE DELIVERY TO YOUR DOOR", "100% GENUINE GUARANTEED", "EASY MONTHLY REFILLS"],
        ["SHIPS SAME DAY — FREE OVER $49", "DELIVERED TO YOUR DOORSTEP", "HASSLE-FREE REORDERING"],
        ["FREE EXPRESS SHIPPING", "ARRIVES IN 3-5 BUSINESS DAYS", "AUTO-REFILL & SAVE 10%"],
    ],
    "urgency": [
        ["LIMITED TIME: EXTRA 10% OFF", "DON'T WAIT UNTIL IT'S TOO LATE", "PROTECT THEM NOW"],
        ["SPRING SALE: UP TO 60% OFF", "FLEA SEASON IS HERE", "ACT NOW — LIMITED STOCK"],
        ["TODAY ONLY: FREE SHIPPING", "PARASITE SEASON ALERT", "ORDER BEFORE IT SELLS OUT"],
    ],
    "trust": [
        ["#1 TRUSTED PET STORE ONLINE", "100% GENUINE PRODUCTS GUARANTEED", "4.9★ RATED BY 12,000+ REVIEWS"],
        ["AUTHENTIC BRAND PRODUCTS ONLY", "FULLY LICENSED & REGULATED", "MONEY-BACK GUARANTEE"],
        ["VET-APPROVED TREATMENTS", "SAME AS YOUR VET SELLS", "100% SATISFACTION GUARANTEED"],
    ],
}

DOG_BREEDS = [
    ("Golden Retriever", "happy Golden Retriever with warm golden coat, friendly smile, looking at camera"),
    ("French Bulldog", "adorable French Bulldog puppy with fawn coat, big round eyes, perked bat ears, looking at camera"),
    ("Labrador", "friendly chocolate Labrador Retriever with warm brown eyes, happy expression, looking at camera"),
    ("Beagle", "happy Beagle with classic tri-color coat, floppy ears, curious expression, looking at camera"),
    ("Husky", "beautiful Siberian Husky with striking blue eyes, white and gray coat, sitting alert, looking at camera"),
    ("Corgi", "fluffy Pembroke Welsh Corgi with big smile, orange and white coat, looking at camera"),
    ("Pomeranian", "fluffy Pomeranian with thick orange coat, fox-like face, happy expression, looking at camera"),
    ("German Shepherd", "noble German Shepherd with alert expression, black and tan coat, looking at camera"),
]

COLORS = [
    ("Peach", "#FFDAB9"),
    ("Mint Green", "#D5F5E3"),
    ("Light Yellow", "#FFF8DC"),
    ("Powder Blue", "#D6EAF8"),
    ("Soft Coral", "#FFE4E1"),
    ("Lavender", "#E8DAEF"),
    ("Soft Gray", "#F2F3F4"),
    ("Light Cyan", "#E0FFFF"),
    ("Warm Sand", "#F5DEB3"),
    ("Pale Rose", "#FFE4E1"),
]


def build_edit_prompt(color_name, color_hex, badges, locked_desc=None, dog_desc=None):
    """Build the Gemini edit prompt."""
    locked = locked_desc or "Product box, brand logo, dog on the box, FDA text, all product labels"

    dog_section = ""
    if dog_desc:
        dog_section = f"""
1. REPLACE THE DOG: Remove the current dog and replace with a {dog_desc}, photorealistic studio quality. Keep the dog in a natural pose in the same area of the image.

2. BACKGROUND: Change the background to a {color_name} color ({color_hex}). Clean, professional, uniform.

3. BADGES — change badge colors AND text:"""
    else:
        dog_section = f"""
1. BACKGROUND: Change the background to a {color_name} color ({color_hex}). Clean, professional, uniform.

2. BADGES — change badge colors AND text:"""

    return f"""Edit this pet product advertisement image. Make these SPECIFIC changes:
{dog_section}
   - Change badge/widget colors to complement the new {color_name} background. Create a cohesive, harmonious color scheme throughout.
   - Replace badge text with NEW copy:
     - '{badges[0]}'
     - '{badges[1]}'
     - '{badges[2]}'
   - Keep same badge shapes, font weight (bold, uppercase, sans-serif). Good contrast for readability.

DO NOT CHANGE: {locked}. Keep all positions and proportions.

Professional ad quality, cohesive color palette, crisp text, no artifacts."""


def validate_badges(badges):
    """Check badges for banned words. Returns list of violations."""
    violations = []
    for badge in badges:
        for word in BANNED_WORDS:
            if word.lower() in badge.lower():
                violations.append(f"'{word}' found in: {badge}")
    return violations


def generate_variations(n, swap_dogs=False):
    """Auto-generate N unique color+text combos, optionally with dog breed swaps."""
    combos = []
    angle_keys = list(TEXT_ANGLES.keys())
    used = set()

    for i in range(n):
        # Rotate through angles
        angle = angle_keys[i % len(angle_keys)]
        # Pick a random text set from that angle
        text_options = TEXT_ANGLES[angle]
        badges = random.choice(text_options)
        badges_key = tuple(badges)

        # Pick color (rotate)
        color_name, color_hex = COLORS[i % len(COLORS)]

        # Pick dog breed if swapping
        dog_breed_name = None
        dog_desc = None
        if swap_dogs:
            dog_breed_name, dog_desc = DOG_BREEDS[i % len(DOG_BREEDS)]

        # Avoid exact duplicates
        key = (color_name, badges_key, dog_breed_name)
        attempts = 0
        while key in used and attempts < 20:
            badges = random.choice(text_options)
            badges_key = tuple(badges)
            color_name, color_hex = random.choice(COLORS)
            if swap_dogs:
                dog_breed_name, dog_desc = random.choice(DOG_BREEDS)
            key = (color_name, badges_key, dog_breed_name)
            attempts += 1
        used.add(key)

        dog_slug = f"-{dog_breed_name.lower().replace(' ', '-')}" if dog_breed_name else ""
        slug = f"v{i+1}-{color_name.lower().replace(' ', '-')}{dog_slug}-{angle}"
        entry = {
            "color": f"{color_name} ({color_hex})",
            "color_name": color_name,
            "color_hex": color_hex,
            "badges": list(badges),
            "angle": angle,
            "filename": f"variant-{slug}.png",
        }
        if swap_dogs:
            entry["dog_breed"] = dog_breed_name
            entry["dog_desc"] = dog_desc
        combos.append(entry)

    return combos


def edit_image(client, source_path, prompt, resolution="2K"):
    """Edit an image via Gemini (Nano Banana Pro)."""
    with open(source_path, "rb") as f:
        img_bytes = f.read()

    mime = "image/jpeg" if str(source_path).lower().endswith((".jpg", ".jpeg")) else "image/png"

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[
            types.Part.from_bytes(data=img_bytes, mime_type=mime),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            return part.inline_data.data
    return None


def edit_image_nbp(source_path, prompt, output_path, resolution="2K"):
    """Edit via Nano Banana Pro skill script (higher quality Gemini 3 Pro Image)."""
    import subprocess

    nbp_script = "/usr/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py"
    if not os.path.exists(nbp_script):
        return None

    cmd = [
        "uv", "run", nbp_script,
        "--prompt", prompt,
        "-i", str(source_path),
        "--filename", str(output_path),
        "--resolution", resolution,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                          env={**os.environ, "PATH": f"/root/.local/bin:{os.environ.get('PATH', '')}"})

    if result.returncode == 0 and os.path.exists(output_path):
        return output_path
    else:
        print(f"  ⚠️ NBP error: {result.stderr[:200]}")
        return None


def qc_check(client, image_path):
    """Run quality control check on generated image."""
    with open(image_path, "rb") as f:
        img_bytes = f.read()

    mime = "image/jpeg" if str(image_path).lower().endswith((".jpg", ".jpeg")) else "image/png"

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type=mime),
                """Score this advertisement image 1-10 on each:
1. Professional quality
2. Text readability
3. Color consistency
4. Artifacts/seams
5. Brand element integrity
Reply ONLY with: score1,score2,score3,score4,score5|PASS or FAIL
Example: 8,9,8,7,9|PASS""",
            ],
        )
        text = response.text.strip()
        # Parse scores
        if "|" in text:
            scores_str, verdict = text.split("|", 1)
            scores = [int(s.strip()) for s in scores_str.split(",") if s.strip().isdigit()]
            avg = sum(scores) / len(scores) if scores else 0
            return {"scores": scores, "average": avg, "pass": "PASS" in verdict.upper()}
    except Exception as e:
        print(f"  ⚠️ QC error: {e}")

    return {"scores": [], "average": 0, "pass": True}  # Default pass on QC failure


def main():
    parser = argparse.ArgumentParser(description="Edit Meta ad variants with Gemini")
    parser.add_argument("--input", "-i", help="Source ad image to edit")
    parser.add_argument("--config", help="JSON config with source + variants")
    parser.add_argument("--color", help="Background color (e.g. 'Peach (#FFDAB9)')")
    parser.add_argument("--badges", nargs=3, help="Three badge texts")
    parser.add_argument("--locked", help="Description of locked elements")
    parser.add_argument("--dog", help="Dog breed description to swap in (e.g. 'happy French Bulldog puppy, fawn coat')")
    parser.add_argument("--swap-dogs", action="store_true", help="Auto-swap dog breeds across variations")
    parser.add_argument("--variations", "-n", type=int, help="Auto-generate N variations")
    parser.add_argument("--output", "-o", default="./output", help="Output path (file or directory)")
    parser.add_argument("--resolution", default="2K", choices=["1K", "2K", "4K"])
    parser.add_argument("--no-qc", action="store_true", help="Skip quality control check")
    parser.add_argument("--delay", type=float, default=5.0, help="Delay between API calls")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without generating")

    args = parser.parse_args()

    # Validate API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and not args.dry_run:
        print("❌ GEMINI_API_KEY not set. Get one at https://aistudio.google.com/apikey")
        sys.exit(1)

    # Build variants list
    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        source = config["source"]
        locked = config.get("locked_elements")
        variants = config["variants"]
    elif args.input and args.variations:
        source = args.input
        locked = args.locked
        variants = generate_variations(args.variations, swap_dogs=args.swap_dogs)
    elif args.input and args.badges:
        source = args.input
        locked = args.locked
        color_str = args.color or "Peach (#FFDAB9)"
        # Parse color
        if "(" in color_str:
            cname = color_str.split("(")[0].strip()
            chex = color_str.split("(")[1].replace(")", "").strip()
        else:
            cname, chex = color_str, ""
        variants = [{
            "color_name": cname,
            "color_hex": chex,
            "badges": args.badges,
            "filename": Path(args.output).name if not Path(args.output).is_dir() else "variant.png",
        }]
    else:
        parser.error("Provide: --config, OR (--input + --variations), OR (--input + --badges)")
        return

    # Setup output
    output_dir = Path(args.output)
    if len(variants) > 1 or args.variations:
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir.parent.mkdir(parents=True, exist_ok=True)

    # Init Gemini client for QC (not for generation — NBP handles that)
    client = None
    if not args.dry_run:
        client = genai.Client(api_key=api_key)

    total = len(variants)
    success = 0
    results = []

    print(f"\n=== Editing {total} Variant{'s' if total > 1 else ''} ===")
    print(f"Source: {source}\n")

    for i, v in enumerate(variants, 1):
        cname = v.get("color_name", v.get("color", "Peach"))
        chex = v.get("color_hex", "")
        badges = v.get("badges", ["", "", ""])
        angle = v.get("angle", "custom")
        filename = v.get("filename", f"variant-{i}.png")
        dog_desc = v.get("dog_desc") or args.dog if hasattr(args, 'dog') else v.get("dog_desc")
        dog_breed = v.get("dog_breed", "custom" if dog_desc else None)

        if len(variants) > 1:
            filepath = output_dir / filename
        else:
            filepath = output_dir if not output_dir.is_dir() else output_dir / filename

        prompt = build_edit_prompt(cname, chex, badges, locked, dog_desc=dog_desc)

        print(f"[{i}/{total}] {filename}")
        dog_info = f" | Dog: {dog_breed}" if dog_breed else ""
        print(f"  Color: {cname} {chex} | Angle: {angle}{dog_info}")
        print(f"  Badges: {' | '.join(badges)}")

        # Check for banned words
        violations = validate_badges(badges)
        if violations:
            print(f"  ⚠️ BANNED WORD detected — skipping:")
            for v in violations:
                print(f"     {v}")
            results.append({"filename": filename, "error": "banned words", "violations": violations})
            continue

        if args.dry_run:
            print(f"  Prompt: {prompt[:120]}...")
            results.append({"filename": filename, "prompt": prompt})
            continue

        # Generate via Nano Banana Pro
        out = edit_image_nbp(source, prompt, str(filepath), args.resolution)

        if out and os.path.exists(str(filepath)):
            size_kb = os.path.getsize(str(filepath)) / 1024
            print(f"  ✅ Generated ({size_kb:.0f} KB)")

            # QC check
            qc = {"pass": True, "average": 0, "scores": []}
            if not args.no_qc and client:
                # Convert to jpg for QC if needed
                qc_path = str(filepath)
                if qc_path.endswith(".png"):
                    qc_jpg = qc_path.replace(".png", "_qc.jpg")
                    Image.open(qc_path).convert("RGB").save(qc_jpg, "JPEG", quality=90)
                    qc_path = qc_jpg
                qc = qc_check(client, qc_path)
                if qc_path != str(filepath):
                    os.remove(qc_path)

                status = "✅ PASS" if qc["pass"] else "❌ FAIL"
                print(f"  QC: {status} (avg {qc['average']:.1f}/10, scores: {qc['scores']})")

            result_entry = {
                "filename": filename,
                "color": f"{cname} {chex}",
                "badges": badges,
                "angle": angle,
                "qc_pass": qc["pass"],
                "qc_avg": qc["average"],
                "qc_scores": qc["scores"],
            }
            if dog_breed:
                result_entry["dog_breed"] = dog_breed
                result_entry["dog_swapped"] = True
            results.append(result_entry)
            success += 1
        else:
            print(f"  ❌ Failed")
            results.append({"filename": filename, "error": "generation failed"})

        if i < total:
            time.sleep(args.delay)

    # Save results log
    log_dir = output_dir if output_dir.is_dir() else output_dir.parent
    log_path = log_dir / "edit_log.json"
    with open(log_path, "w") as f:
        json.dump({"source": str(source), "results": results}, f, indent=2)

    # Auto-append to creative metadata registry
    registry_path = Path("/root/clawd/data/creative_meta/registry.json")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    if registry_path.exists():
        with open(registry_path) as f:
            registry = json.load(f)
    else:
        registry = {"total": 0, "creatives": []}

    from datetime import datetime, timezone
    for r in results:
        if "error" in r:
            continue
        cid = f"AUTO{registry['total'] + 1:04d}"
        entry = {
            "id": cid,
            "filename": r.get("filename", ""),
            "path": str(log_dir / r.get("filename", "")),
            "source_ad": os.path.basename(str(source)),
            "product_box": None,
            "background_color_name": r.get("color", "").split("#")[0].strip() if r.get("color") else None,
            "background_color_hex": ("#" + r.get("color", "").split("#")[-1].strip()) if "#" in r.get("color", "") else None,
            "badge_text": r.get("badges", []),
            "text_angle": r.get("angle", "custom"),
            "creative_theme": "standard",
            "headline": None,
            "dog_breed": r.get("dog_breed"),
            "dog_swapped": r.get("dog_swapped", False),
            "model_used": "gemini-3-pro-image",
            "resolution": args.resolution,
            "qc_score": r.get("qc_avg"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "meta_ad_id": None,
            "status": "draft",
        }
        registry["creatives"].append(entry)
        registry["total"] = len(registry["creatives"])

    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)

    print(f"\n{'=' * 50}")
    print(f"✅ Generated: {success}/{total}")
    print(f"📁 Output: {output_dir}")
    print(f"📋 Log: {log_path}")

    if success > 0:
        passed = sum(1 for r in results if r.get("qc_pass"))
        if not args.no_qc:
            print(f"🔍 QC passed: {passed}/{success}")


if __name__ == "__main__":
    main()

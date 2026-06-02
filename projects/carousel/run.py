#!/usr/bin/env python3
"""
run.py — main entry point for the branded carousel generator.

Usage:
    python3 run.py --brand olipop --product raspberry-sherbet
    python3 run.py --brand olipop --product raspberry-sherbet --open

Brand context is read from a LOCAL folder (brands/<brand>/), never scraped.
Models are provider-agnostic (set FOUNDRY_LLM / FOUNDRY_IMAGE in .env). With no
API keys, it runs free in stub mode and produces placeholder SVG slides.
"""

import argparse
import os
import sys

import config
import research
import generate
import gallery


def main() -> int:
    ap = argparse.ArgumentParser(description="Branded Instagram carousel generator")
    ap.add_argument("--brand", required=True, help="brand folder slug under brands/")
    ap.add_argument("--product", required=True, help="product file slug under brands/<brand>/products/")
    ap.add_argument("--open", action="store_true", help="open the gallery in a browser when done")
    args = ap.parse_args()

    print(f"\n=== Foundry Carousel Generator ===")
    print(f"Brand:   {args.brand}")
    print(f"Product: {args.product}")
    print(f"LLM:     {config.LLM_PROVIDER}")
    print(f"Image:   {config.IMAGE_PROVIDER}\n")

    try:
        brand_data = research.load_brand(args.brand)
        product_data = research.load_product(args.brand, args.product)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    out_dir = os.path.join(config.OUTPUT_DIR, args.brand, args.product)

    print(f"Brand identified: {brand_data['brand_name']}")
    print(f"Colors: {brand_data['colors']}")
    photos = product_data.get("ref_photos", [])
    print(f"Reference photos: {len(photos)} found"
          f"{' (' + ', '.join(os.path.basename(p) for p in photos) + ')' if photos else ''}\n")

    print(f"Phase 1/2 — generating {config.NUM_SLIDES} slide concepts...")
    concepts, llm_stub = research.generate_concepts(brand_data, product_data, out_dir)
    print(f"  {len(concepts)} concepts generated{'  [STUB LLM — no key]' if llm_stub else ''}\n")

    print(f"Phase 2/2 — rendering slides...")
    slides, img_stub = generate.generate_slides(
        concepts, args.brand, args.product, photos, out_dir)
    ok = len([s for s in slides if s.get("ok")])
    print(f"  {ok}/{len(slides)} slides rendered{'  [STUB IMAGES — placeholders]' if img_stub else ''}\n")

    path = gallery.build_gallery(slides, brand_data, out_dir, open_browser=args.open)
    print(f"Done. Gallery: {path}")
    print(f"Files in: {out_dir}")
    if llm_stub or img_stub:
        print("\nNote: ran in STUB mode (no API keys). Add ANTHROPIC_API_KEY and an")
        print("image key (e.g. FAL_KEY) to .env to generate real copy and images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

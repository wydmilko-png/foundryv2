"""
research.py — load brand identity from a LOCAL folder (not web scraping) and turn
it into slide concepts.

Folder shape:
    brands/<brand>/
        brand.md                 brand identity
        products/<product>.md    one file per product
        assets/<product>/*.{jpg,png,webp}   optional real product photos
"""

import json
import os
import re

import config
import providers

_IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")


def _parse_md_sections(path: str) -> dict:
    """Parse a markdown file into {lowercased-heading: text-block}."""
    sections, current, buf = {}, None, []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## "):
                if current is not None:
                    sections[current] = "\n".join(buf).strip()
                current = line[3:].strip().lower()
                buf = []
            elif line.startswith("# "):
                sections["_title"] = line[2:].strip()
            else:
                buf.append(line.rstrip())
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def _lines(block: str) -> list:
    return [l.strip(" -•\t") for l in block.splitlines() if l.strip()]


def load_brand(brand_slug: str) -> dict:
    folder = os.path.join(config.BRANDS_DIR, brand_slug)
    brand_md = os.path.join(folder, "brand.md")
    if not os.path.exists(brand_md):
        raise FileNotFoundError(f"No brand.md found at {brand_md}")
    s = _parse_md_sections(brand_md)

    # Colors: accept "primary: #hex" lines, else grab hex codes in order.
    colors = {}
    color_block = s.get("colors", "")
    for line in _lines(color_block):
        if ":" in line:
            k, _, v = line.partition(":")
            m = config.HEX_RE.search(v)
            if m:
                colors[k.strip().lower()] = m.group(0)
    if not colors:
        found = config.HEX_RE.findall(color_block)
        for name, hx in zip(("primary", "secondary", "accent"), found):
            colors[name] = hx

    return {
        "brand_name": s.get("_title", brand_slug),
        "slug": brand_slug,
        "colors": colors,
        "typography": s.get("typography", ""),
        "voice": s.get("voice", ""),
        "visual_style": s.get("visual style", s.get("visual_style", "")),
        "taglines": _lines(s.get("taglines", "")),
        "folder": folder,
    }


def load_product(brand_slug: str, product_slug: str) -> dict:
    folder = os.path.join(config.BRANDS_DIR, brand_slug)
    product_md = os.path.join(folder, "products", f"{product_slug}.md")
    if not os.path.exists(product_md):
        raise FileNotFoundError(f"No product file at {product_md}")
    s = _parse_md_sections(product_md)

    # Optional reference photos in assets/<product>/
    refs = []
    assets = os.path.join(folder, "assets", product_slug)
    if os.path.isdir(assets):
        refs = [os.path.join(assets, f) for f in sorted(os.listdir(assets))
                if f.lower().endswith(_IMG_EXT)]

    return {
        "name": s.get("_title", product_slug),
        "slug": product_slug,
        "one_liner": s.get("one-liner", s.get("one_liner", "")),
        "benefits": _lines(s.get("benefits", "")),
        "ingredients": s.get("ingredients", ""),
        "proof": s.get("proof", ""),
        "offer": s.get("offer", s.get("offer/cta", "")),
        "ref_photos": refs,
    }


def generate_concepts(brand_data: dict, product_data: dict, out_dir: str) -> list:
    llm = providers.get_llm()
    concepts = llm.generate_concepts(brand_data, product_data)

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "brand_dna.json"), "w", encoding="utf-8") as fh:
        json.dump(brand_data, fh, indent=2)
    with open(os.path.join(out_dir, "concepts.json"), "w", encoding="utf-8") as fh:
        json.dump(concepts, fh, indent=2)
    return concepts, getattr(llm, "is_stub", False)

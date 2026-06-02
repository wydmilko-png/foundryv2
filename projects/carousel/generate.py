"""
generate.py — render each concept into a slide file via the configured image
provider (real model if a key is set, otherwise the free SVG stub).
"""

import os
import time

import config
import providers


def generate_slides(concepts: list, brand_slug: str, product_slug: str,
                    ref_photos: list, out_dir: str) -> tuple:
    gen = providers.get_image_generator()
    is_stub = getattr(gen, "is_stub", False)
    ext = getattr(gen, "ext", "png")

    # Real image models take photo references by URL; local file paths only make
    # sense to the stub. (Uploading local files to a host is a future adapter.)
    refs_for_model = [] if is_stub else [p for p in ref_photos if p.startswith("http")]

    slides_dir = os.path.join(out_dir, "slides")
    os.makedirs(slides_dir, exist_ok=True)

    results = []
    for c in concepts:
        n, stype = c["slide"], c["type"]
        fname = f"slide_{n}_{stype}.{ext}"
        out_path = os.path.join(slides_dir, fname)
        print(f"  Generating slide {n}/{len(concepts)}: {stype} — {c['headline']}")
        try:
            gen.generate(c, refs_for_model if not is_stub else ref_photos, out_path)
            results.append({**c, "file": os.path.join("slides", fname), "ok": True})
        except Exception as e:                 # one failure shouldn't kill the deck
            print(f"    ! slide {n} failed: {e}")
            results.append({**c, "file": None, "ok": False, "error": str(e)})
        if not is_stub:
            time.sleep(2)                      # be gentle with rate limits

    return results, is_stub

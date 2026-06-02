"""
llm_stub — free, offline concept generator.

Produces 6 deterministic, on-brand slide concepts straight from the brand.md /
product.md content, with NO API call. Good enough to run and review the whole
pipeline for $0; swap in a real LLM (set ANTHROPIC_API_KEY) for production copy.
"""

import config


class StubLLM:
    is_stub = True

    def __init__(self, reason: str = ""):
        self.reason = reason

    def generate_concepts(self, brand_data: dict, product_data: dict) -> list:
        palette = brand_data.get("colors", {})
        primary = palette.get("primary", "#222222")
        secondary = palette.get("secondary", "#EEEEEE")
        accent = palette.get("accent", "#888888")
        text_color = "#FFFFFF"

        product = product_data.get("name", "the product")
        benefits = product_data.get("benefits", []) or ["Better every day"]
        ingredients = product_data.get("ingredients", "Clean, simple ingredients.")
        proof = product_data.get("proof", "Loved by thousands.")
        offer = product_data.get("offer", "Shop now.")
        one_liner = product_data.get("one_liner", product)

        # Rotate the two background colors so each slide feels like its own world.
        bgs = [(primary, secondary), (secondary, primary), (accent, secondary),
               (primary, accent), (secondary, accent), (accent, primary)]

        copy = {
            "hook":        (product.upper(), one_liner),
            "problem":     ("TIRED OF THE SAME?", "There's a better-for-you option."),
            "benefit":     (benefits[0].upper(), ", ".join(benefits[:3])),
            "ingredients": ("WHAT'S INSIDE", ingredients),
            "proof":       ("THE PROOF", proof),
            "cta":         ("GRAB YOURS", offer),
        }

        concepts = []
        for i, stype in enumerate(config.SLIDE_TYPES[:config.NUM_SLIDES]):
            headline, subtext = copy.get(stype, (product.upper(), one_liner))
            bg1, bg2 = bgs[i % len(bgs)]
            concepts.append({
                "slide": i + 1,
                "type": stype,
                "headline": headline,
                "subtext": subtext,
                "bg_color_1": bg1,
                "bg_color_2": bg2,
                "text_color": text_color,
                "image_prompt": (
                    f"A finished 1080x1350 Instagram carousel slide for {product}. "
                    f"Wavy organic color blocks separating {bg1} and {bg2}. "
                    f"Bold rounded ALL-CAPS headline '{headline}' overlaid on the image. "
                    f"Subtext '{subtext}'. Photorealistic product hero, centered. "
                    f"Hand-drawn doodles and sticker badges matching the brand. "
                    f"Slide type: {stype}."
                ),
            })
        return concepts

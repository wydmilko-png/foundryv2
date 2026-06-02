"""
llm_anthropic — concept generation via the Anthropic Messages API (REST, stdlib).

No SDK install: we POST to the REST endpoint with urllib. Set ANTHROPIC_API_KEY in
.env to activate (otherwise the factory uses llm_stub instead).
"""

import json
import re
import urllib.request
import urllib.error

import config

SYSTEM_PROMPT = """You are a world-class DTC creative director specializing in Gen Z CPG brands like Olipop, Liquid Death, and Athletic Greens. You design Instagram carousel content that looks like it came from a professional creative team.

Given brand research data and a product focus, generate exactly {n} Instagram carousel slide concepts. Each slide is a self-contained visual with designed layout baked into the image itself.

Return ONLY valid JSON — no markdown fences, no preamble. An array of {n} objects:
[
  {{
    "slide": 1,
    "type": "hook",
    "headline": "ALL CAPS, max 6 words, punchy scroll-stopper",
    "subtext": "Supporting line, max 12 words, direct benefit",
    "bg_color_1": "#hex from the brand palette",
    "bg_color_2": "#hex secondary/accent from the brand palette",
    "text_color": "#hex headline color that pops on bg_color_1",
    "image_prompt": "Detailed 150+ word prompt for a finished 1080x1350 IG slide: wavy color blocks between bg_color_1 and bg_color_2, centered photorealistic product, bold rounded ALL-CAPS headline overlaid, decorative doodles/stickers, bottom tagline, mood and lighting. Reference the specific product."
  }}
]

Slide types to include (one each, in order): {types}.
Rules: bg colors must come from the scraped/provided palette; each slide a different color world; every image_prompt must reference the specific product and include the exact copy to render; the cta slide must bake in a shop/offer callout."""


class AnthropicLLM:
    is_stub = False

    def __init__(self, model: str):
        self.model = model or "claude-sonnet-4-6"

    def generate_concepts(self, brand_data: dict, product_data: dict) -> list:
        system = SYSTEM_PROMPT.format(
            n=config.NUM_SLIDES,
            types=", ".join(config.SLIDE_TYPES[:config.NUM_SLIDES]),
        )
        user = (
            f"Brand data: {json.dumps(brand_data)}\n\n"
            f"Product focus: {json.dumps(product_data)}\n\n"
            f"Generate {config.NUM_SLIDES} carousel slide concepts."
        )
        body = json.dumps({
            "model": self.model,
            "max_tokens": 4000,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": config.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Anthropic API HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}") from e

        text = "".join(block.get("text", "") for block in payload.get("content", []))
        clean = re.sub(r"```json|```", "", text).strip()
        return json.loads(clean)

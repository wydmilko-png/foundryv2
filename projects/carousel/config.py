"""
config.py — settings + .env loader for the carousel generator.

Design goals (per founder):
- Provider-agnostic: the LLM and the image model are chosen by strings in .env,
  never hard-coded. Swapping models is a one-line change, not a rewrite.
- Runs with NO keys: if a provider's key is missing, the pipeline auto-falls back
  to a free local "stub" so the whole thing runs end-to-end for $0.
- No third-party dependencies: everything here is Python standard library.
"""

import os
import re

CAROUSEL_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_dotenv(path: str) -> None:
    """Minimal .env loader (stdlib only). Does not override existing env vars."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


_load_dotenv(os.path.join(CAROUSEL_DIR, ".env"))


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


# --- Output format ---------------------------------------------------------
IMAGE_SIZE = {"width": 1080, "height": 1350}   # Instagram 4:5
IMAGE_QUALITY = "high"
NUM_SLIDES = int(env("FOUNDRY_NUM_SLIDES", "6"))

# Slide types, in order. One concept per type.
SLIDE_TYPES = ["hook", "problem", "benefit", "ingredients", "proof", "cta"]

# --- Provider selection (provider:model) -----------------------------------
# Examples you can drop in .env without touching code:
#   FOUNDRY_LLM=anthropic:claude-sonnet-4-6
#   FOUNDRY_IMAGE=fal:openai/gpt-image-2
#   FOUNDRY_IMAGE=fal:fal-ai/nano-banana
#   FOUNDRY_IMAGE=fal:fal-ai/flux/dev
LLM_PROVIDER = env("FOUNDRY_LLM", "anthropic:claude-sonnet-4-6")
IMAGE_PROVIDER = env("FOUNDRY_IMAGE", "fal:openai/gpt-image-2")

# Force stub mode for a fully offline run even if keys exist.
FORCE_STUB = env("FOUNDRY_STUB", "") in ("1", "true", "yes")

# --- API keys --------------------------------------------------------------
ANTHROPIC_API_KEY = env("ANTHROPIC_API_KEY")
FAL_KEY = env("FAL_KEY")

# --- Paths -----------------------------------------------------------------
BRANDS_DIR = os.path.join(CAROUSEL_DIR, "brands")
OUTPUT_DIR = os.path.join(CAROUSEL_DIR, "output")


def split_provider(spec: str):
    """'fal:openai/gpt-image-2' -> ('fal', 'openai/gpt-image-2')."""
    provider, _, model = spec.partition(":")
    return provider.strip().lower(), model.strip()


HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}")

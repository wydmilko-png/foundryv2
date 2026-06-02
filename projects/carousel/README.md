# Branded Carousel Generator

Turns **local brand context** (a folder, not a scraped URL) into 6 Instagram
carousel slides + an HTML gallery. Built by the Foundry.

Three design principles:
1. **Local context, not scraping** — reads `brands/<brand>/brand.md` + a product
   file. Exact colors/voice/copy you control → reliable, on-brand output.
2. **Provider-agnostic** — the LLM and image model are chosen by strings in `.env`.
   Swap GPT Image 2 ↔ Nano Banana ↔ Flux, or Claude ↔ anything, with no code change.
3. **Runs with no keys** — with no API keys it produces placeholder SVG slides for
   free, so you can see the whole flow before paying for anything. No installs
   either (pure Python standard library).

## Try it now (free, no keys)
```bash
python3 run.py --brand olipop --product raspberry-sherbet
open output/olipop/raspberry-sherbet/index.html      # view the gallery
```

## Add a brand
```
brands/<brand>/
  brand.md                    # ## Colors / ## Typography / ## Voice / ## Visual Style / ## Taglines
  products/<product>.md       # ## One-liner / ## Benefits / ## Ingredients / ## Proof / ## Offer
  assets/<product>/*.jpg      # optional product photos used as image references
```
Then: `python3 run.py --brand <brand> --product <product>`

## Go live (real images)
```bash
cp .env.example .env
# put ANTHROPIC_API_KEY and an image key (e.g. FAL_KEY) in .env
python3 run.py --brand olipop --product raspberry-sherbet --open
```
Switch models any time by editing `FOUNDRY_IMAGE` / `FOUNDRY_LLM` in `.env`.

## Files
- `run.py` — entry point
- `research.py` — load brand/product folder + generate concepts
- `generate.py` — render slides via the chosen image provider
- `gallery.py` — build the HTML gallery
- `config.py` — settings + .env loader
- `providers/` — swappable LLM + image adapters (stub, anthropic, fal)

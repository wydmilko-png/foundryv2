"""
image_fal — real image generation via FAL (REST, stdlib).

FAL is used as a gateway: one key, many models. Swap the model by changing the
FOUNDRY_IMAGE string in .env (e.g. fal:openai/gpt-image-2, fal:fal-ai/nano-banana,
fal:fal-ai/flux/dev) — no code change. No SDK install; we POST with urllib.

If a slide has reference photos (refs), they are passed through as image_urls when
the chosen model supports image-to-image; otherwise it's plain text-to-image.
"""

import json
import os
import urllib.request
import urllib.error

import config


class FalImage:
    is_stub = False
    ext = "png"

    def __init__(self, model: str):
        self.model = model or "openai/gpt-image-2"

    def generate(self, concept: dict, refs: list, out_path: str) -> str:
        body = {
            "prompt": concept["image_prompt"],
            "image_size": config.IMAGE_SIZE,   # if a model rejects the dict, set a preset enum in .env
            "quality": config.IMAGE_QUALITY,
            "num_images": 1,
            "output_format": "png",
        }
        # Pass product photos as references when present (model-permitting).
        if refs:
            body["image_urls"] = refs

        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"https://fal.run/{self.model}",
            data=data,
            headers={
                "Authorization": f"Key {config.FAL_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"FAL HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}") from e

        images = payload.get("images") or []
        if not images:
            raise RuntimeError(f"FAL returned no images: {json.dumps(payload)[:300]}")
        url = images[0]["url"]

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as img_resp:
            with open(out_path, "wb") as fh:
                fh.write(img_resp.read())
        return out_path

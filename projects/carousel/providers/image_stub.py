"""
image_stub — free, offline slide renderer.

Writes a real 1080x1350 SVG per slide using the concept's brand colors, headline,
subtext, type badge and a wavy color-block background — so the gallery looks like
the real layout without any API call or install. Swap in a real image model
(set FAL_KEY) to replace these placeholders with generated PNGs.

SVG is used (not PNG) so there is zero third-party dependency; it renders natively
in the browser gallery.
"""

import html
import os

import config


def _wrap(text: str, width: int) -> list:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class StubImage:
    is_stub = True
    ext = "svg"

    def __init__(self, reason: str = ""):
        self.reason = reason

    def generate(self, concept: dict, refs: list, out_path: str) -> str:
        W, H = config.IMAGE_SIZE["width"], config.IMAGE_SIZE["height"]
        bg1 = concept.get("bg_color_1", "#222222")
        bg2 = concept.get("bg_color_2", "#EEEEEE")
        text_color = concept.get("text_color", "#FFFFFF")
        headline = html.escape(concept.get("headline", ""))
        subtext = html.escape(concept.get("subtext", ""))
        stype = html.escape(concept.get("type", "").upper())

        head_lines = _wrap(headline, 16)
        head_svg = "".join(
            f'<tspan x="{W//2}" dy="{0 if i == 0 else 96}">{ln}</tspan>'
            for i, ln in enumerate(head_lines)
        )
        sub_lines = _wrap(subtext, 34)
        sub_svg = "".join(
            f'<tspan x="{W//2}" dy="{0 if i == 0 else 44}">{ln}</tspan>'
            for i, ln in enumerate(sub_lines)
        )

        ref_note = ""
        if refs:
            ref_note = (f'<text x="{W//2}" y="{H-60}" text-anchor="middle" '
                        f'font-family="sans-serif" font-size="26" fill="{text_color}" '
                        f'opacity="0.7">[uses {len(refs)} product photo(s) as reference]</text>')

        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{bg1}"/>
  <path d="M0,{int(H*0.62)} C {int(W*0.3)},{int(H*0.52)} {int(W*0.7)},{int(H*0.72)} {W},{int(H*0.60)} L {W},{H} L 0,{H} Z" fill="{bg2}"/>
  <rect x="48" y="48" rx="28" ry="28" width="{60 + len(stype)*26}" height="64" fill="{text_color}" opacity="0.9"/>
  <text x="{78}" y="{90}" font-family="sans-serif" font-weight="700" font-size="30" fill="{bg1}">{stype}</text>
  <text x="{W//2}" y="{int(H*0.40)}" text-anchor="middle" font-family="sans-serif" font-weight="800" font-size="84" fill="{text_color}">{head_svg}</text>
  <text x="{W//2}" y="{int(H*0.78)}" text-anchor="middle" font-family="sans-serif" font-size="38" fill="{text_color}" opacity="0.95">{sub_svg}</text>
  <circle cx="{W-80}" cy="80" r="26" fill="{bg2}" stroke="{text_color}" stroke-width="3"/>
  <text x="{W//2}" y="{H-120}" text-anchor="middle" font-family="sans-serif" font-size="22" fill="{text_color}" opacity="0.55">PLACEHOLDER — add an image API key to generate the real slide</text>
  {ref_note}
</svg>'''

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        return out_path

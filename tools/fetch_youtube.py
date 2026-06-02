#!/usr/bin/env python3
"""
fetch_youtube.py — pull a YouTube video's full transcript as plain text.

What it does:
  Takes a YouTube URL (any common form) or a bare 11-character video ID,
  fetches the transcript with the `youtube-transcript-api` library, and prints
  it as one clean block of plain text.

Notes for the non-technical reader:
  - No API key. Read-only. It only reads the public, auto- or human-made
    captions that the video already publishes.
  - If a video has captions turned off, there is simply nothing to read and the
    script will say so plainly.

Usage:
    python3 fetch_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"
    python3 fetch_youtube.py VIDEO_ID

It also exposes get_transcript_text(url_or_id) so other tools (like fetch_x.py)
can pull a transcript directly and read a whole item as one.
"""

import re
import sys


def extract_video_id(url_or_id: str) -> str | None:
    """Pull the 11-character video ID out of any common YouTube link form,
    or accept a bare ID. Returns None if nothing usable is found."""
    s = (url_or_id or "").strip()

    # Already a bare ID (11 chars of the YouTube alphabet, nothing else).
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", s):
        return s

    # Patterns covering watch?v=, youtu.be/, /embed/, /shorts/, /live/, /v/
    patterns = [
        r"(?:v=|/v/)([0-9A-Za-z_-]{11})",
        r"youtu\.be/([0-9A-Za-z_-]{11})",
        r"/embed/([0-9A-Za-z_-]{11})",
        r"/shorts/([0-9A-Za-z_-]{11})",
        r"/live/([0-9A-Za-z_-]{11})",
    ]
    for pat in patterns:
        m = re.search(pat, s)
        if m:
            return m.group(1)
    return None


def get_transcript_text(url_or_id: str) -> str:
    """Return the full transcript as one plain-text string.

    Raises ValueError if the link can't be parsed, or RuntimeError with a
    plain-language reason if no transcript is available.
    """
    video_id = extract_video_id(url_or_id)
    if not video_id:
        raise ValueError(f"Could not find a YouTube video ID in: {url_or_id!r}")

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError as e:  # pragma: no cover - environment guard
        raise RuntimeError(
            "The 'youtube-transcript-api' library is not installed.\n"
            "Install it with:  python3 -m pip install youtube-transcript-api"
        ) from e

    # The library's API changed across versions. Try the current instance-based
    # API first (v1.x: YouTubeTranscriptApi().fetch(...)), then fall back to the
    # older static API (get_transcript(...)) so this keeps working either way.
    snippets_text = []
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        for snippet in fetched:
            # FetchedTranscriptSnippet has a .text attribute.
            snippets_text.append(getattr(snippet, "text", "") or "")
    except AttributeError:
        # Older versions: classmethod returning a list of dicts.
        raw = YouTubeTranscriptApi.get_transcript(video_id)
        snippets_text = [item.get("text", "") for item in raw]
    except Exception as e:
        # Turn library-specific errors (disabled, unavailable, no transcript)
        # into one plain message.
        raise RuntimeError(
            f"Couldn't get a transcript for video {video_id}: {e}"
        ) from e

    text = "\n".join(line for line in snippets_text if line.strip())
    if not text.strip():
        raise RuntimeError(
            f"Video {video_id} returned an empty transcript "
            "(captions may be disabled)."
        )
    return text


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if (len(argv) == 2 and argv[1] in ("-h", "--help")) else 2

    target = argv[1]
    try:
        video_id = extract_video_id(target)
        text = get_transcript_text(target)
    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"=== YouTube transcript: {video_id} ===\n")
    print(text)
    print(f"\n=== end transcript ({len(text)} characters) ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

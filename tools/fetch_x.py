#!/usr/bin/env python3
"""
fetch_x.py — read any public tweet (X/Twitter) without an API key.

How it works (the trick):
  X's own site is locked down, but the free, read-only service "fxtwitter"
  mirrors any public tweet as clean JSON. So we take your tweet link, swap the
  domain to api.fxtwitter.com, fetch the JSON, and print the text plus every
  link found inside the tweet.

What you get:
  - The author, the tweet text, and basic stats (replies / reposts / likes).
  - A list of every link found inside the tweet (articles, repos, other tools).
  - If one of those links is a YouTube video, it chains to fetch_youtube.py and
    appends the transcript, so the whole item reads as one.

Limitations (be honest about these):
  - No API key, read-only.
  - It reads the MAIN tweet plus the reply COUNT only — it cannot read full
    reply threads.

Usage:
    python3 fetch_x.py https://x.com/jack/status/20
    python3 fetch_x.py https://twitter.com/user/status/123  --no-chain
"""

import json
import re
import sys
import urllib.error
import urllib.request

API_HOST = "api.fxtwitter.com"
USER_AGENT = "FoundryBot/1.0 (+https://github.com/wydmilko-png/foundryv2)"

URL_RE = re.compile(r"https?://[^\s\)\]\}'\"<>]+")
YOUTUBE_RE = re.compile(r"(?:youtube\.com/|youtu\.be/)", re.IGNORECASE)


def to_api_url(tweet_url: str) -> str:
    """Turn a tweet URL (or 'user/status/id') into the fxtwitter API URL."""
    s = (tweet_url or "").strip()

    # Bare "user/status/id" with no scheme/host.
    if re.fullmatch(r"[^/]+/status/\d+", s):
        return f"https://{API_HOST}/{s}"

    # Strip scheme, then strip any twitter/x host, keep the path.
    no_scheme = re.sub(r"^https?://", "", s)
    path = re.sub(r"^(www\.)?(x|twitter|fxtwitter|vxtwitter)\.com/", "", no_scheme,
                  flags=re.IGNORECASE)
    path = path.split("?")[0].rstrip("/")
    if not path:
        raise ValueError(f"Doesn't look like a tweet URL: {tweet_url!r}")
    return f"https://{API_HOST}/{path}"


def fetch_json(api_url: str) -> dict:
    req = urllib.request.Request(api_url, headers={"User-Agent": USER_AGENT,
                                                   "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"fxtwitter returned HTTP {e.code} for {api_url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error reaching fxtwitter: {e.reason}") from e
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise RuntimeError("fxtwitter did not return valid JSON.") from e


def collect_links(tweet: dict) -> list[str]:
    """Gather every link found inside the tweet, de-duplicated, in order."""
    links: list[str] = []

    def add(u: str | None):
        if u and u not in links:
            links.append(u)

    # 1) URLs written in the tweet text (fxtwitter expands t.co to real URLs).
    for m in URL_RE.findall(tweet.get("text", "") or ""):
        add(m.rstrip(".,);"))

    # 2) Quoted tweet.
    quote = tweet.get("quote") or {}
    add(quote.get("url"))

    # 3) Link card (preview of an external article/site).
    card = tweet.get("twitter_card") or {}
    if isinstance(card, dict):
        add(card.get("url"))

    # 4) Media (photos / videos hosted on the tweet).
    media = tweet.get("media") or {}
    if isinstance(media, dict):
        for group in ("photos", "videos", "all"):
            for item in (media.get(group) or []):
                if isinstance(item, dict):
                    add(item.get("url"))

    return links


def read_tweet(tweet_url: str, chain: bool = True) -> str:
    """Build the full plain-text report for a tweet (and chained YouTube)."""
    api_url = to_api_url(tweet_url)
    payload = fetch_json(api_url)

    if payload.get("code") != 200 or "tweet" not in payload:
        msg = payload.get("message", "unknown error")
        raise RuntimeError(f"fxtwitter could not read that tweet: {msg}")

    tweet = payload["tweet"]
    author = tweet.get("author", {}) or {}
    out: list[str] = []

    out.append("=== Tweet ===")
    out.append(f"Author : {author.get('name', '?')} (@{author.get('screen_name', '?')})")
    out.append(f"Date   : {tweet.get('created_at', '?')}")
    out.append(f"URL    : {tweet.get('url', api_url)}")
    out.append("")
    out.append(tweet.get("text", "") or "(no text)")
    out.append("")
    out.append(
        f"Stats  : {tweet.get('replies', 0)} replies | "
        f"{tweet.get('retweets', 0)} reposts | {tweet.get('likes', 0)} likes"
    )
    out.append("Note   : main tweet + reply COUNT only — full reply threads "
               "are not readable here.")

    links = collect_links(tweet)
    out.append("")
    if links:
        out.append(f"=== Links found inside the tweet ({len(links)}) ===")
        for i, link in enumerate(links, 1):
            out.append(f"  {i}. {link}")
    else:
        out.append("=== No links found inside the tweet ===")

    # Chain: if a YouTube link is present, append its transcript.
    if chain:
        yt_links = [l for l in links if YOUTUBE_RE.search(l)]
        for yt in yt_links:
            out.append("")
            out.append(f"=== Chained YouTube transcript for: {yt} ===")
            try:
                from fetch_youtube import get_transcript_text
            except ImportError:
                import os
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from fetch_youtube import get_transcript_text
            try:
                out.append(get_transcript_text(yt))
            except Exception as e:
                out.append(f"(could not fetch transcript: {e})")

    return "\n".join(out)


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("-")]
    flags = [a for a in argv[1:] if a.startswith("-")]

    if "-h" in flags or "--help" in flags or len(args) != 1:
        print(__doc__)
        return 0 if ("-h" in flags or "--help" in flags) else 2

    chain = "--no-chain" not in flags
    try:
        print(read_tweet(args[0], chain=chain))
    except (ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

# The Foundry

A personal pipeline that turns a **link** into either an **installed tool** or a
**clear build plan**.

You paste a link (X/Twitter, YouTube, GitHub, a blog, docs). The Foundry fetches
it, reads it, classifies what it is, tags which lane it serves, and ends with a
**park / build-now / build-later** recommendation. Then it either builds the thing
or writes a self-contained handoff. Every finished item is logged in one master
doc in Google Drive ("The Foundry"), so there's a single source of truth.

It's written for a non-technical founder: plain language, facts over opinions, and
the founder makes the call.

---

## What's in here

```
Foundry/
├── tools/
│   ├── fetch_x.py         # read any public tweet (no API key)
│   └── fetch_youtube.py   # pull a video's full transcript (no API key)
├── handoffs/              # self-contained build briefs for big jobs
├── SKILL.md               # the procedure that runs on every pasted link
├── requirements.txt
└── README.md
```

## Setup (one time)

This Mac's system Python is locked down (Homebrew/PEP 668), so the Foundry uses
its own private virtual environment. Setup is two lines:

```bash
python3 -m venv ~/Foundry/.venv
~/Foundry/.venv/bin/pip install -r ~/Foundry/requirements.txt
```

(`fetch_x.py` uses only Python's built-in libraries. Only `fetch_youtube.py`
needs the one dependency above. Running both through the venv keeps the chaining
feature working.)

## The two test commands

```bash
# 1) Read a tweet — prints author, text, stats, and every link inside it
~/Foundry/.venv/bin/python ~/Foundry/tools/fetch_x.py https://x.com/jack/status/20

# 2) Read a video's transcript — prints the full captions as plain text
~/Foundry/.venv/bin/python ~/Foundry/tools/fetch_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### How the two tools work
- **fetch_x.py** swaps the tweet's domain to `api.fxtwitter.com`, reads the public
  JSON, and prints clean text + every link found inside. It reads the main tweet
  and the reply *count* only — not full reply threads. If it finds a YouTube link
  inside the tweet, it automatically chains `fetch_youtube.py` so the whole item
  reads as one.
- **fetch_youtube.py** takes a YouTube URL or video ID and prints the full
  transcript as plain text, using the `youtube-transcript-api` library.

## The master log (Google Drive)

Finished items are recorded in the Google Drive doc **"The Foundry"** (inside the
top-level **"The Foundry"** folder). One row per finished link:

| Date | Link | What it is | Lane(s) | Verdict | Where it landed | Dependencies |

Both Claude and the founder update this doc — it's the single source of truth.

## The lanes
- **Gray Matter** — business / agency / client-facing work
- **Mater.ia** — product / build line
- **Personal** — personal tools, learning, life ops

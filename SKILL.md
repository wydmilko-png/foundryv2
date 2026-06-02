---
name: foundry
description: The procedure that runs whenever a link is pasted into the Foundry — fetch it, list its sub-links, classify it, write a scout's report (never a verdict), tag the lane(s), and end with a park / build-now / build-later recommendation. Build it or write a handoff.
---

# The Foundry — link triage procedure

**Who this is for:** a non-technical founder. Explain in plain language. Give facts,
not opinions dressed as facts. The founder decides what is worth building; your job
is to scout honestly and make the decision easy.

When a link is pasted, run these steps **in order** and produce the report.

---

## Step 1 — Fetch the link
Pick the right tool (run them through the Foundry's private venv):
- **X / Twitter** (`x.com`, `twitter.com`) → `~/Foundry/.venv/bin/python ~/Foundry/tools/fetch_x.py <url>`
- **YouTube** (`youtube.com`, `youtu.be`) → `~/Foundry/.venv/bin/python ~/Foundry/tools/fetch_youtube.py <url>`
- **GitHub / blog / docs / anything else** → fetch and read the page directly.

If `fetch_x.py` finds a YouTube link inside a tweet, it already chains the
transcript automatically — read the whole item as one.

## Step 2 — List every sub-link found
Surface **every** link the item points to: GitHub repos, documentation, a second
tool, a demo, a paper. Number them. These are the real leads — the headline link
is often just the doorway.

## Step 3 — Classify what it is
Put it in exactly one bucket (or say it spans two and why):
- **MCP** — a server that plugs tools into Claude/an agent.
- **Skill** — a reusable procedure/instruction set (like this file).
- **Script-or-repo** — runnable code you install and call.
- **Workflow-or-prompt** — a way of working / a prompt pattern, no code to install.
- **Just-hype** — interesting to know, nothing to build or install.

## Step 4 — Write a scout's report, NOT a verdict
Describe what it is, what it does, what it needs to run, and what's unproven.
State facts and trade-offs. **Do not** say "this is worth it" or "skip it" — that
is the founder's call. Make the call easy by being concrete.

## Step 5 — Tag the lane(s)
Which lane(s) does it serve? Say if it fits more than one and why:
- **Gray Matter** — <business / agency / client-facing work>
- **Mater.ia** — <product / build line>
- **Personal** — <personal tools, learning, life ops>

(If a lane's exact meaning is unclear for a given item, say which lane it *looks*
like it serves and what would confirm it.)

## Step 6 — If the link is too thin to plan, don't dead-end
Never stop at "not enough info." Say exactly:
- what specific piece is missing (the repo? the docs? a demo? pricing?), and
- what the founder should go grab to make it plannable (e.g. "send the GitHub
  link from the thread" or "the README install section").

## Step 7 — End with a recommendation: park / build-now / build-later
Frame it as **impact**, not effort:
- **Park** — log it, no action now. Say what would change that.
- **Build-now** — high enough impact to do this session.
- **Build-later** — worth building, but after X / when Y is true.
Tie the framing to business (Gray Matter / Mater.ia) or personal value.

---

## Execution rule (after the recommendation)
- If the founder says **build now** and it fits one session → build it, then give
  a single **test command** they can run themselves.
- If it's **too big for one session** → write a **self-contained handoff** to
  `~/Foundry/handoffs/<short-name>.md`, addressed to a fresh Claude Code session
  that **cannot see this chat**. It must include: the goal, the source link(s),
  every sub-link, what to build, the exact steps, the test command, and any
  credentials/installs needed. Assume zero prior context.

## After anything is finished
Add one row to the master log — the Google Drive doc **"The Foundry"** inside the
top-level **"The Foundry"** folder (update it, never duplicate it). One entry per
finished link:

| Date | Link | What it is | Lane(s) | Verdict | Where it landed | Dependencies |

Both you and the founder write to this doc — it is the single source of truth.

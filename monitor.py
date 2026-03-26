#!/usr/bin/env python3
"""
Open Science Policy Monitor
Checks 19 IS venue author guideline pages monthly for open science policy changes.
Uses Claude's web search tool to access venue pages (avoids publisher 403 blocks).
Proposes updates as GitHub Pull Requests with evidence.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

# ---------- Config ----------
REPO_ROOT = Path(__file__).resolve().parent
VENUES_FILE = REPO_ROOT / "venues.json"
PROMPT_FILE = REPO_ROOT / "prompt.txt"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096


def load_venues() -> dict:
    with open(VENUES_FILE) as f:
        return json.load(f)


def load_prompt() -> str:
    with open(PROMPT_FILE) as f:
        return f.read()


# ---------- Call Claude API with web search ----------

def analyse_venue(venue: dict, system_prompt: str) -> dict | None:
    """Ask Claude to search for and code a venue's open science policies."""

    # Build a hint about known URLs so Claude knows where to look
    url_hints = ""
    if venue.get("guide_urls"):
        url_hints = "\nKnown author guideline URLs (may have changed):\n"
        for u in venue["guide_urls"]:
            url_hints += f"  - {u}\n"

    user_msg = (
        f"Venue: {venue['name']} ({venue['abbr']})\n"
        f"Venue ID: {venue['id']}\n"
        f"Main URL: {venue['url']}\n"
        f"{url_hints}\n"
        f"Please search the web for this venue's current author guidelines "
        f"and open science policies, then code them according to your instructions."
    )

    try:
        # Initial request with web search tool
        messages = [{"role": "user", "content": user_msg}]
        result = _call_api(messages, system_prompt, venue)
        return result

    except Exception as e:
        print(f"  ⚠ Error for {venue['abbr']}: {e}")
        return None


def _call_api(messages: list, system_prompt: str, venue: dict,
              depth: int = 0) -> dict | None:
    """Call Claude API, handling multi-turn tool use automatically."""
    if depth > 10:
        print(f"  ⚠ Too many tool use rounds for {venue['abbr']}, giving up")
        return None

    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "system": system_prompt,
            "tools": [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                }
            ],
            "messages": messages,
        },
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()

    stop_reason = data.get("stop_reason", "")

    if stop_reason == "tool_use":
        # Claude wants to search — continue the conversation
        # Add assistant's response to messages
        messages.append({"role": "assistant", "content": data["content"]})

        # Build tool results for each tool use block
        tool_results = []
        for block in data.get("content", []):
            if block.get("type") == "tool_use":
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": "Search results provided.",
                })

        messages.append({"role": "user", "content": tool_results})
        return _call_api(messages, system_prompt, venue, depth + 1)

    # Final response — extract JSON
    text_parts = []
    for block in data.get("content", []):
        if block.get("type") == "text":
            text_parts.append(block["text"])

    text = "\n".join(text_parts).strip()

    # Find the JSON object in the response
    json_start = text.find("{")
    json_end = text.rfind("}") + 1
    if json_start == -1 or json_end == 0:
        print(f"  ⚠ No JSON found in response for {venue['abbr']}")
        print(f"    Response: {text[:300]}...")
        return None

    json_str = text[json_start:json_end]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error for {venue['abbr']}: {e}")
        print(f"    Raw: {json_str[:300]}...")
        return None


# ---------- Compare codings ----------

PRACTICE_KEYS = [
    "open_access", "preprint", "open_data", "open_materials",
    "open_artefact", "registered_reports", "open_peer_review", "replication"
]

COLUMN_NAMES = [
    "Open Access", "Preprint", "Open Data", "Open Materials",
    "Open Artefact", "Registered Reports", "Open Peer Review", "Replication"
]

CODING_LABELS = {0: "Not addressed", 1: "Permitted or available", 2: "Required or actively offered"}


def compare(venue: dict, result: dict) -> list[dict]:
    """Compare current codings with new codings. Returns list of changes."""
    if result.get("status") != "ok":
        return []

    changes = []
    new_codings = result.get("codings", {})
    current_vals = venue["vals"]

    for i, key in enumerate(PRACTICE_KEYS):
        new_val = new_codings.get(key)
        if new_val is None:
            continue
        old_val = current_vals[i]
        if new_val != old_val:
            changes.append({
                "venue_id": venue["id"],
                "venue_name": f"{venue['name']} ({venue['abbr']})",
                "practice": COLUMN_NAMES[i],
                "practice_index": i,
                "old_value": old_val,
                "old_label": CODING_LABELS[old_val],
                "new_value": new_val,
                "new_label": CODING_LABELS[new_val],
                "evidence": result.get("evidence", {}).get(key, "No evidence provided"),
            })
    return changes


# ---------- Apply changes to venues.json ----------

def apply_changes(venues_data: dict, changes: list[dict]) -> dict:
    """Return a copy of venues_data with changes applied."""
    import copy
    updated = copy.deepcopy(venues_data)
    for change in changes:
        for section in updated["sections"]:
            for venue in section["venues"]:
                if venue["id"] == change["venue_id"]:
                    venue["vals"][change["practice_index"]] = change["new_value"]
    updated["last_reviewed"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return updated


# ---------- Generate venues-data.js ----------

def generate_venues_data_js(venues_data: dict) -> str:
    """Generate the venues-data.js file content from venues.json."""
    lines = [
        "// venues-data.js — Auto-updated by Open Science Policy Monitor",
        f"// Last updated: {venues_data.get('last_reviewed', 'unknown')}",
        "// Manual edits will be overwritten on next monitor run.",
        "",
        "const COLS = ['Open Access','Preprint','Open Data','Open Materials','Open Artefact','Registered Reports','Open Peer Review','Replication'];",
        "",
        "// 0 = absent, 1 = partial (~), 2 = present (✓)",
        "const rows = [",
    ]
    for section in venues_data["sections"]:
        lines.append(f"  // SECTION: {section['label'].upper()}")
        lines.append(f"  {{ section: \"{section['label']}\" }},")
        for v in section["venues"]:
            display_name = v.get("html_name", v["name"])
            vals_str = "[" + ",".join(str(x) for x in v["vals"]) + "]"
            safe_name = display_name.replace("'", "\\'")
            safe_abbr = v["abbr"].replace("'", "\\'")
            safe_url = v["url"].replace("'", "\\'")
            lines.append(
                f"  {{ name: '{safe_name}', "
                f"abbr: '{safe_abbr}', "
                f"url: '{safe_url}', "
                f"vals: {vals_str} }},"
            )
    lines.append("];")
    lines.append("")
    return "\n".join(lines)


# ---------- Git operations ----------

def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"  git {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()


def create_pull_request(changes: list[dict], updated_data: dict):
    """Create a branch, commit changes, and create a PR via GitHub CLI."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    branch_name = f"monitor/update-{date_str}"

    # Write updated venues.json
    with open(VENUES_FILE, "w") as f:
        json.dump(updated_data, f, indent=2)
        f.write("\n")

    # Write updated venues-data.js (this is what index.html loads)
    js_path = REPO_ROOT / "venues-data.js"
    with open(js_path, "w") as f:
        f.write(generate_venues_data_js(updated_data))

    # Build PR body
    body_lines = [f"## Open Science Policy Monitor — {date_str}", ""]
    body_lines.append(f"**{len(changes)} change(s) detected:**\n")
    for c in changes:
        body_lines.append(
            f"### {c['venue_name']} — {c['practice']}\n"
            f"- **Was:** {c['old_label']} ({c['old_value']})\n"
            f"- **Now:** {c['new_label']} ({c['new_value']})\n"
            f"- **Evidence:** {c['evidence']}\n"
        )

    body = "\n".join(body_lines)

    # Git operations
    git("checkout", "-b", branch_name)
    git("add", "venues.json", "venues-data.js")
    git("commit", "-m", f"monitor: {len(changes)} policy change(s) detected — {date_str}")
    git("push", "origin", branch_name)

    # Create PR via GitHub CLI
    subprocess.run([
        "gh", "pr", "create",
        "--title", f"Policy update: {len(changes)} change(s) — {date_str}",
        "--body", body,
        "--base", "main",
        "--head", branch_name,
    ], cwd=REPO_ROOT)

    print(f"\n✅ Pull request created on branch {branch_name}")


# ---------- Main ----------

def main():
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not set. Exiting.")
        sys.exit(1)

    print("=" * 60)
    print("Open Science Policy Monitor")
    print(f"Run date: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    venues_data = load_venues()
    system_prompt = load_prompt()
    all_changes: list[dict] = []

    # Flatten all venues
    all_venues = []
    for section in venues_data["sections"]:
        all_venues.extend(section["venues"])

    print(f"\nChecking {len(all_venues)} venues...\n")

    for venue in all_venues:
        print(f"▶ {venue['name']} ({venue['abbr']})")
        result = analyse_venue(venue, system_prompt)
        if not result:
            print(f"  ⚠ No result from API, skipping")
            continue

        if result.get("status") == "error":
            print(f"  ⚠ Error: {result.get('error_message', 'unknown')}")
            continue

        changes = compare(venue, result)
        if changes:
            for c in changes:
                print(f"  🔄 {c['practice']}: {c['old_label']} → {c['new_label']}")
            all_changes.extend(changes)
        else:
            print(f"  ✓ No changes")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Scan complete. {len(all_changes)} change(s) found.")
    print("=" * 60)

    if all_changes:
        updated_data = apply_changes(venues_data, all_changes)

        if os.environ.get("GITHUB_ACTIONS"):
            create_pull_request(all_changes, updated_data)
        else:
            # Local run — update files directly (no PR created)
            with open(VENUES_FILE, "w") as f:
                json.dump(updated_data, f, indent=2)
                f.write("\n")
            js_path = REPO_ROOT / "venues-data.js"
            with open(js_path, "w") as f:
                f.write(generate_venues_data_js(updated_data))
            print(f"\nLocal run — venues.json and venues-data.js updated directly (no PR).")
            print("Changes summary:")
            for c in all_changes:
                print(f"  {c['venue_name']} | {c['practice']}: "
                      f"{c['old_label']} → {c['new_label']}")
                print(f"    Evidence: {c['evidence']}")
    else:
        print("\nNo changes to commit.")


if __name__ == "__main__":
    main()

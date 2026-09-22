#!/usr/bin/env python3
"""
Fetch GitHub repositories tagged with the `awesome-list` topic, sorted by
star count, and write them to data/repos.json for the static site to render.

Usage:
    python3 scripts/fetch_data.py

Environment:
    GITHUB_TOKEN   Optional. A GitHub token raises the API rate limit from
                   60 req/hr (unauthenticated) to 5000 req/hr. In GitHub
                   Actions, the built-in GITHUB_TOKEN is used automatically.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = "https://api.github.com/search/repositories"
QUERY = "topic:awesome-list"
PER_PAGE = 100
MAX_PAGES = 3          # 100 * 3 = up to 300 repos
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "repos.json")


def fetch_page(page: int, token: str | None) -> dict:
    url = f"{API_URL}?q={QUERY}&sort=stars&order=desc&per_page={PER_PAGE}&page={page}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "awesome-index-site",
    })
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"GitHub API error {e.code} on page {page}: {body}", file=sys.stderr)
        raise


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    all_items = []

    for page in range(1, MAX_PAGES + 1):
        data = fetch_page(page, token)
        items = data.get("items", [])
        if not items:
            break
        all_items.extend(items)
        if len(items) < PER_PAGE:
            break
        time.sleep(1)  # be polite between pages

    records = []
    for it in all_items:
        records.append({
            "name": it["full_name"],
            "desc": (it.get("description") or "").strip(),
            "stars": it["stargazers_count"],
            "lang": it.get("language") or "",
            "url": it["html_url"],
            "updated": it["updated_at"][:10],
            "avatar": it["owner"]["avatar_url"],
        })

    records.sort(key=lambda r: r["stars"], reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "query": QUERY,
        "count": len(records),
        "items": records,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(records)} repos to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

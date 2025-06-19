import sys
import os
import requests
import json
import time

# Ensure access to reviewer_config.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'clang', 'tools', 'reviewer-suggester'))

try:
    from reviewer_config import GITHUB_TOKEN
except ImportError:
    raise ImportError("❌ reviewer_config.py not found or GITHUB_TOKEN not defined. Please check the file path and token setup.")

# GitHub API headers
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPO = "llvm/llvm-project"
OUTPUT_FILE = "data/openmp_prs.json"


def get_reviewers(pr_number):
    """Fetch reviewers for a given PR based on review comments."""
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/reviews"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[WARN] Could not fetch reviewers for PR #{pr_number}, status: {response.status_code}")
        return []
    reviews = response.json()
    reviewers = list({review["user"]["login"] for review in reviews if "user" in review and review["user"]})
    return reviewers


def get_openmp_prs(max_pages=10):
    """Fetch OpenMP-related PRs and their reviewers."""
    prs = []
    seen_prs = set()
    for page in range(1, max_pages + 1):
        print(f"[INFO] Fetching PRs from page {page}...")
        url = f"https://api.github.com/repos/{REPO}/pulls?state=closed&per_page=100&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[ERROR] GitHub API error: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        for pr in data:
            pr_text = (pr.get("title", "") + " " + (pr.get("body") or "")).lower()
            if "openmp" in pr_text and pr["number"] not in seen_prs:
                reviewers = get_reviewers(pr["number"])
                prs.append({
                    "number": pr["number"],
                    "title": pr["title"],
                    "body": pr.get("body") or "",
                    "reviewers": reviewers
                })
                seen_prs.add(pr["number"])

        time.sleep(1)  # Respect API rate limits

    return prs


if __name__ == "__main__":
    print("[INFO] Starting OpenMP PR download...")
    os.makedirs("data", exist_ok=True)  # Create data/ if it doesn't exist
    openmp_prs = get_openmp_prs()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(openmp_prs, f, indent=2)
    print(f"[INFO] ✅ Saved {len(openmp_prs)} PRs to {OUTPUT_FILE}")

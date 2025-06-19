import requests
import json
import time

headers = {
    "Authorization": "token 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",  # <-- replace this
    "Accept": "application/vnd.github+json"
}

prs = []

# Fetch first 5 pages of OpenMP PRs (adjust as needed)
for page in range(1, 6):
    print(f"Fetching page {page}...")
    url = f"https://api.github.com/repos/llvm/llvm-project/pulls"
    params = {
        "state": "closed",
        "labels": "openmp",
        "per_page": 100,
        "page": page
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"❌ GitHub API failed: {response.status_code} {response.text}")
        break

    pr_list = response.json()

    if not isinstance(pr_list, list):
        print("❌ Unexpected response format:", pr_list)
        break

    for pr in pr_list:
        prs.append({
            "title": pr.get("title", ""),
            "body": pr.get("body", ""),
            "reviewers": [r["login"] for r in pr.get("requested_reviewers", [])]
        })

    time.sleep(1)  # to respect rate limits

# Save to JSON file
with open("historical_openmp_prs.json", "w") as f:
    json.dump(prs, f, indent=2)

print(f"\n✅ Collected {len(prs)} PRs and saved to historical_openmp_prs.json")

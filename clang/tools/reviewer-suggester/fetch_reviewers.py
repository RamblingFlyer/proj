import requests
import json
from datetime import datetime
import os
from reviewer_config import GITHUB_TOKEN
from collections import defaultdict
import argparse

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPO = "llvm/llvm-project"
PER_PAGE = 100

def test_api_connection():
    test_url = "https://api.github.com/user"
    response = requests.get(test_url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        print(f"Successfully authenticated as: {user_data.get('login')}")
    else:
        print(f"Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")

def fetch_pull_requests(page=1):
    url = f"https://api.github.com/repos/{REPO}/pulls"
    params = {
        "state": "all",
        "per_page": PER_PAGE,
        "page": page,
        "sort": "created",
        "direction": "desc"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error fetching pull requests: {response.status_code}")
        return []
    
    return response.json()

def fetch_pr_events(pr_number):
    url = f"https://api.github.com/repos/{REPO}/issues/{pr_number}/events"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    events = response.json()
    request_times = {}
    for event in events:
        if event.get("event") == "review_requested" and "requested_reviewer" in event:
            reviewer = event["requested_reviewer"]["login"]
            request_times[reviewer] = event["created_at"]
    return request_times

def fetch_reviews_for_pr(pr_number):
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}/reviews"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    return response.json()

def fetch_reviewer_data(max_prs):
    reviewer_data = defaultdict(lambda: {
        "num_reviews": 0,
        "last_active": "1900-01-01",
        "review_times": [],
        "avg_response_time_hours": 0
    })

    test_api_connection()

    page = 1
    processed_prs = 0

    while True:
        pull_requests = fetch_pull_requests(page)
        if not pull_requests:
            break

        for pr in pull_requests:
            if processed_prs >= max_prs:
                break
            pr_number = pr["number"]
            request_times = fetch_pr_events(pr_number)
            reviews = fetch_reviews_for_pr(pr_number)

            for review in reviews:
                try:
                    reviewer = review["user"]["login"]
                    submitted_at = review["submitted_at"]
                    reviewer_data[reviewer]["num_reviews"] += 1
                    review_date = submitted_at.split("T")[0]
                    if review_date > reviewer_data[reviewer]["last_active"]:
                        reviewer_data[reviewer]["last_active"] = review_date
                    request_time = request_times.get(reviewer)
                    if request_time:
                        requested = datetime.strptime(request_time, "%Y-%m-%dT%H:%M:%SZ")
                        submitted = datetime.strptime(submitted_at, "%Y-%m-%dT%H:%M:%SZ")
                        response_time = (submitted - requested).total_seconds() / 3600
                        if response_time > 0:
                            reviewer_data[reviewer]["review_times"].append(response_time)
                except:
                    continue

            processed_prs += 1

        if processed_prs >= max_prs or len(pull_requests) < PER_PAGE:
            break

        page += 1

    for reviewer in reviewer_data:
        times = reviewer_data[reviewer]["review_times"]
        if times:
            reviewer_data[reviewer]["avg_response_time_hours"] = sum(times) / len(times)
        del reviewer_data[reviewer]["review_times"]

    return dict(reviewer_data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prs", type=int, default=10, help="Max number of PRs to process")
    args = parser.parse_args()

    print(f"\n[INFO] Fetching data from latest {args.max_prs} PRs...")
    reviewer_data = fetch_reviewer_data(args.max_prs)

    os.makedirs("data", exist_ok=True)
    output_file = os.path.join("data", "reviewers.json")
    with open(output_file, "w") as f:
        json.dump(reviewer_data, f, indent=2)

    print(f"\n✅ Saved reviewer data to {output_file}")
    print(f"🧠 Total reviewers found: {len(reviewer_data)}")

if __name__ == "__main__":
    main()

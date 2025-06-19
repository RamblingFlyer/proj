import sys
import requests
from reviewer_config import GITHUB_TOKEN
from similarity_engine import find_similar_prs
from reviewer_ranker import rank_reviewers

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPO = "llvm/llvm-project"

def fetch_pr(pr_number):
    url = f"https://api.github.com/repos/{REPO}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"[ERROR] Could not fetch PR #{pr_number}")
    
    pr = response.json()
    return pr["title"], pr["body"]

def main(pr_number):
    print(f"[INFO] Running reviewer suggester for PR #{pr_number}")
    
    title, body = fetch_pr(pr_number)
    similar_prs = find_similar_prs(title, body)
    
    ranked_reviewers = rank_reviewers(similar_prs)

    print("\n[📋 Suggested Reviewers]")
    for reviewer, scores in ranked_reviewers:
        print(f"  - {reviewer} (score: {scores['total']}) "
              f"[expertise: {scores['expertise']}, activity: {scores['activity']}, "
              f"response: {scores['response']}, relevance: {scores['relevance']}]")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 run.py <PR_NUMBER>")
        sys.exit(1)

    main(int(sys.argv[1]))

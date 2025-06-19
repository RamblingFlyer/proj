import os
import json
import requests
from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def fetch_pr_metadata(pr_number):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing GitHub token. Set GITHUB_TOKEN environment variable.")

    headers = {"Authorization": f"token " + token}
    pr_url = f"https://api.github.com/repos/llvm/llvm-project/pulls/{pr_number}"
    files_url = f"{pr_url}/files"

    pr_resp = requests.get(pr_url, headers=headers)
    files_resp = requests.get(files_url, headers=headers)

    try:
        pr_resp.raise_for_status()
        files_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("GitHub API error:", pr_resp.text)
        raise RuntimeError(f"Failed to fetch PR #{pr_number} metadata.") from e

    pr = pr_resp.json()
    files = files_resp.json()

    return {
        "title": pr.get("title", ""),
        "body": pr.get("body", ""),
        "files": [f["filename"] for f in files if "filename" in f]
    }

def compute_similarity(pr_title, pr_body, historical_prs):
    if not pr_title:
        raise ValueError("PR title is missing")
    if pr_body is None:
        pr_body = ""

    query_text = pr_title + " " + pr_body
    new_vec = model.encode(query_text, convert_to_tensor=True, normalize_embeddings=True)

    scores = []
    for pr in historical_prs:
        hist_title = pr.get("title", "")
        hist_body = pr.get("body") or ""   # ✅ Safely handles None
        reviewers = pr.get("reviewers", [])

        if not hist_title:
            continue

        hist_text = hist_title + " " + hist_body
        hist_vec = model.encode(hist_text, convert_to_tensor=True, normalize_embeddings=True)

        sim_tensor = util.cos_sim(new_vec, hist_vec)
        sim = sim_tensor[0][0].item()

        if not (0.0 <= sim <= 1.0):
            print(f"⚠️ Warning: Similarity score {sim} is out of range for PR titled: {hist_title}")

        scores.append((sim, reviewers))
    return scores


def suggest_reviewers(pr_number):
    try:
        new_pr = fetch_pr_metadata(pr_number)
        pr_title, pr_body = new_pr["title"], new_pr["body"]

        with open("historical_openmp_prs.json") as f:
            historical_prs = json.load(f)

        scores = compute_similarity(pr_title, pr_body, historical_prs)
    except Exception as e:
        print(f"Error while suggesting reviewers: {e}")
        raise

    reviewer_score = {}
    for sim, reviewers in scores:
        for r in reviewers:
            reviewer_score[r] = reviewer_score.get(r, 0.0) + sim

    return sorted(reviewer_score.items(), key=lambda x: -x[1])[:5]

import json
from collections import Counter
from datetime import datetime
import math
import os

def days_since(date_str):
    try:
        last_active = datetime.strptime(date_str, "%Y-%m-%d")
        return (datetime.now() - last_active).days
    except Exception:
        return 9999

def normalize(score_dict):
    if not score_dict:
        return {}
    max_score = max(score_dict.values())
    if max_score == 0:
        return {k: 0 for k in score_dict}
    return {k: v / max_score for k, v in score_dict.items()}

def rank_reviewers(similar_prs):
    reviewer_counter = Counter()
    for pr in similar_prs:
        for reviewer in pr.get("reviewers", []):
            reviewer_counter[reviewer] += 1

    metadata_path = os.path.join("data", "reviewers.json")
    if not os.path.exists(metadata_path):
        print("[WARN] reviewers.json not found. Using frequency only.")
        return [(reviewer, {"total": count}) for reviewer, count in reviewer_counter.most_common()]

    with open(metadata_path) as f:
        reviewer_profiles = json.load(f)

    raw_scores = {}
    detailed_scores = {}

    for reviewer, freq in reviewer_counter.items():
        meta = reviewer_profiles.get(reviewer, {})
        last_active_days = days_since(meta.get("last_active", "1900-01-01"))
        response_time = meta.get("avg_response_time_hours", 48)
        expertise = meta.get("num_reviews", 0)

        activity_score = max(0, 1 - last_active_days / 30)
        responsiveness_score = max(0, 1 - response_time / 24)
        expertise_score = min(expertise / 50, 1)
        relevance_score = freq / len(similar_prs)

        total_score = (
            0.4 * expertise_score +
            0.2 * activity_score +
            0.2 * responsiveness_score +
            0.2 * relevance_score
        )

        raw_scores[reviewer] = total_score
        detailed_scores[reviewer] = {
            "total": round(total_score, 3),
            "expertise": round(expertise_score, 3),
            "activity": round(activity_score, 3),
            "response": round(responsiveness_score, 3),
            "relevance": round(relevance_score, 3)
        }

    normalized = normalize({k: v["total"] for k, v in detailed_scores.items()})

    # Attach normalized total back
    for reviewer in detailed_scores:
        detailed_scores[reviewer]["total"] = round(normalized[reviewer], 3)

    sorted_reviewers = sorted(detailed_scores.items(), key=lambda x: x[1]["total"], reverse=True)
    return sorted_reviewers

import requests
from reviewer_config import GITHUB_TOKEN

headers = {
    "Authorization": f"token {GITHUB_TOKEN}"
}

def fetch_pr_metadata(pr_number):
    url = f"https://api.github.com/repos/llvm/llvm-project/pulls/{pr_number}"
    response = requests.get(url, headers=headers)
    data = response.json()
    return {
        "number": pr_number,
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "files": fetch_changed_files(pr_number)
    }

def fetch_changed_files(pr_number):
    url = f"https://api.github.com/repos/llvm/llvm-project/pulls/{pr_number}/files"
    response = requests.get(url, headers=headers)
    return [file['filename'] for file in response.json()]

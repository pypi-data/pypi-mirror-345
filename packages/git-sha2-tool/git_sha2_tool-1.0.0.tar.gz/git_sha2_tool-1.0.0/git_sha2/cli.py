import argparse
import hashlib
import requests
import sys

def to_raw_url(git_url):
    if "github.com" in git_url and "/blob/" in git_url:
        return git_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    raise ValueError("Unsupported or invalid Git URL.")

def download_file_content(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def compute_sha256(content):
    return hashlib.sha256(content).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Compute SHA-256 hash of file at a Git URL.")
    parser.add_argument("git_url", help="Git file URL (e.g., GitHub raw/blob link)")
    args = parser.parse_args()

    try:
        raw_url = to_raw_url(args.git_url)
        content = download_file_content(raw_url)
        sha256 = compute_sha256(content)
        print(f"SHA-256: {sha256}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

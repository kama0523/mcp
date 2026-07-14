#　FastMCPで作るGitHub用MCP　Server

import os
import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("GitHub Progress Server")

GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_PERSONAL_ACCESS_TOKEN}",
    "Accept": "application/vnd.github+json",
}


@mcp.tool
def get_repository_info(owner: str, repo: str) -> dict:
    """
    GitHubリポジトリの基本情報を取得する。
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    return {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "open_issues": data.get("open_issues_count"),
        "updated_at": data.get("updated_at"),
        "default_branch": data.get("default_branch"),
    }


@mcp.tool
def get_latest_commits(owner: str, repo: str, limit: int = 5) -> list[dict]:
    """
    最新コミットを取得する。
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=HEADERS, params={"per_page": limit})
    response.raise_for_status()
    commits = response.json()

    return [
        {
            "sha": commit.get("sha"),
            "message": commit.get("commit", {}).get("message"),
            "author": commit.get("commit", {}).get("author", {}).get("name"),
            "date": commit.get("commit", {}).get("author", {}).get("date"),
        }
        for commit in commits
    ]


@mcp.tool
def get_readme(owner: str, repo: str) -> str:
    """
    READMEの内容を取得する。
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    download_url = data.get("download_url")
    if not download_url:
        return ""

    readme_response = requests.get(download_url)
    readme_response.raise_for_status()
    return readme_response.text


@mcp.tool
def list_repository_files(owner: str, repo: str, path: str = "") -> list[dict]:
    """
    指定したパス配下のファイル一覧を取得する。
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    items = response.json()

    if isinstance(items, dict):
        items = [items]

    return [
        {
            "name": item.get("name"),
            "path": item.get("path"),
            "type": item.get("type"),
        }
        for item in items
    ]


if __name__ == "__main__":
    mcp.run()
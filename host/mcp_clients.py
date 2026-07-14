"""MCP Serverとの接続処理。

Hostから見た「MCP Client」の責務だけをこのファイルにまとめます。
"""

from pathlib import Path

from fastmcp import Client


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GITHUB_SERVER = PROJECT_ROOT / "servers" / "github_server.py"


def create_github_client() -> Client:
    """GitHub MCP Serverを子プロセスとして起動するClientを作る。"""
    return Client(GITHUB_SERVER)

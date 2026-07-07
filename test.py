#!/usr/bin/env python3
"""
GitHub Remote MCP Serverに接続する最小クライアント。

事前にプロジェクトルートの .env にGitHub Personal Access Tokenを設定してください。

    GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_...

必要なら接続先URLも変更できます。

    GITHUB_MCP_URL=https://api.githubcopilot.com/mcp/
"""

import asyncio
import json
import os
from pathlib import Path

from fastmcp import Client
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local", override=True)

GITHUB_MCP_URL = os.getenv("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")


def create_github_client() -> Client:
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_PAT")

    if not token:
        raise RuntimeError(
            "GITHUB_PERSONAL_ACCESS_TOKEN か GITHUB_PAT が設定されていません。"
        )

    return Client(GITHUB_MCP_URL, auth=token)


def print_tool(tool, index: int) -> None:
    description = getattr(tool, "description", None) or "No description"
    first_line = description.strip().splitlines()[0]
    print(f"{index:2}. {tool.name} - {first_line}")


def print_tool_schema(tool) -> None:
    schema = getattr(tool, "inputSchema", None) or getattr(tool, "input_schema", None)
    print(f"\n[TOOL] {tool.name}")

    if getattr(tool, "description", None):
        print(f"\n{tool.description}")

    if schema:
        print("\n[INPUT SCHEMA]")
        print(json.dumps(schema, ensure_ascii=False, indent=2))
    else:
        print("\n[INPUT SCHEMA] なし")


def choose_tool(tools):
    while True:
        raw = input("\n実行するツール番号を入力してください。終了は q: ").strip()

        if raw.lower() in {"q", "quit", "exit"}:
            return None

        if not raw.isdigit():
            print("[ERROR] 番号を入力してください。")
            continue

        index = int(raw)
        if 1 <= index <= len(tools):
            return tools[index - 1]

        print(f"[ERROR] 1 から {len(tools)} の番号を入力してください。")


def read_tool_arguments() -> dict:
    raw = input("\n引数をJSONで入力してください。空なら {}: ").strip()

    if not raw:
        return {}

    try:
        arguments = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSONの形式が正しくありません: {exc}") from exc

    if not isinstance(arguments, dict):
        raise ValueError("引数は JSON object で入力してください。例: {\"owner\":\"octocat\"}")

    return arguments


async def main():
    client = create_github_client()

    async with client:
        await client.ping()
        print("[OK] GitHub Remote MCP Serverに接続しました")

        tools = await client.list_tools()
        print(f"\n[LIST] 利用可能なツール数: {len(tools)}")

        for index, tool in enumerate(tools, start=1):
            print_tool(tool, index)

        while True:
            tool = choose_tool(tools)
            if tool is None:
                print("[END] 終了します")
                return

            print_tool_schema(tool)

            try:
                arguments = read_tool_arguments()
            except ValueError as exc:
                print(f"[ERROR] {exc}")
                continue

            result = await client.call_tool(tool.name, arguments)
            print("\n[RESULT]")
            print(result)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as exc:
        print(f"[ERROR] {exc}")

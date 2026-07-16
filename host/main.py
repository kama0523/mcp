"""学習用MCP Hostのエントリーポイント。

MCP Serverから取得したGitHub情報をLLMへ渡して文章化します。
"""

import asyncio
import json

from host.llm import ask_llm
from host.mcp_clients import create_github_client


async def main() -> None:
    client = create_github_client()

    async with client:
        owner = input("GitHubのユーザー名または組織名: ")
        repo = input("リポジトリ名: ")

        result = await client.call_tool(
            "get_repository_info",
            {
                "owner": owner,
                "repo": repo,
            },
        )

        repository = result.data

    print("\nリポジトリ情報")
    print(f"名前: {repository['full_name']}")
    print(f"説明: {repository['description']}")
    print(f"言語: {repository['language']}")
    print(f"スター数: {repository['stars']}")
    print(f"未解決Issue数: {repository['open_issues']}")
    print(f"最終更新: {repository['updated_at']}")
    print(f"デフォルトブランチ: {repository['default_branch']}")

    repository_text = json.dumps(
        repository,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
以下はGitHubリポジトリから取得した情報です。

{repository_text}

この情報だけを使用して、リポジトリの概要を日本語で簡潔に説明してください。
情報に含まれていないことは推測しないでください。
"""

    answer = ask_llm(prompt)

    print("\nLLMによるリポジトリの説明")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())

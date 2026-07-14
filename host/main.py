"""学習用MCP Hostの最初のエントリーポイント。

第1段階ではLLMをまだ使わず、HostがMCP Serverを発見できることを確認します。
"""

import asyncio
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



if __name__ == "__main__":
    asyncio.run(main())






if __name__ == "__main__":
    asyncio.run(main())

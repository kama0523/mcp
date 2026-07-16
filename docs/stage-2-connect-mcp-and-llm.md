# 第2段階: MCPの取得結果をLLMへ渡す

## この段階の目的

MCP Serverから取得したGitHubリポジトリ情報をLLMへ渡し、自然な日本語の説明を生成します。

```text
owner・repoを入力
  ↓
MCP Client
  ↓
MCP Server
  ↓
GitHub APIからデータを取得
  ↓
取得データをLLMへ渡す
  ↓
LLMが日本語で説明
```

この段階では、使用するMCPツールをHost側で `get_repository_info` に固定します。質問に応じてLLM自身にツールを選ばせる処理は、次の段階で実装します。

## ファイルの役割

```text
host/main.py
    MCPとLLMを順番に呼び出し、全体の処理を進めるHost

host/mcp_clients.py
    MCP Serverへ接続するClientを作る

servers/github_server.py
    GitHub APIをMCPツールとして公開する

host/llm.py
    OpenAI APIへ入力を送り、回答文を受け取る
```

## 1. 必要なimport

```python
import asyncio
import json

from host.llm import ask_llm
from host.mcp_clients import create_github_client
```

`json` は、MCP Serverから受け取ったPythonの辞書を、LLMへ渡しやすいJSON文字列へ変換するために使用します。

`ask_llm` は `host/llm.py` に定義したLLM呼び出し関数です。importしただけでは `host/llm.py` のテスト用 `main()` は実行されません。

## 2. MCP Serverからリポジトリ情報を取得

```python
client = create_github_client()

async with client:
    result = await client.call_tool(
        "get_repository_info",
        {
            "owner": owner,
            "repo": repo,
        },
    )

    repository = result.data
```

`client.call_tool()` は、MCP Serverに登録されているツールを名前と引数を指定して実行します。

```text
ツール名: get_repository_info
引数: owner, repo
```

`result.data` には、MCP Serverが返したPythonの辞書が入ります。

## 3. MCP接続を終了する

`async with client:` の外に出ると、MCP ClientとMCP Serverの接続が終了します。

GitHubデータ取得後の表示処理とLLM呼び出しは `async with` の外に置いています。必要なデータを取得した後までMCP Serverを起動し続ける必要がないためです。

## 4. 元データを表示する

```python
print("\nリポジトリ情報")
print(f"名前: {repository['full_name']}")
print(f"説明: {repository['description']}")
```

MCP Serverから返された元データを表示します。LLMの回答と比較することで、LLMが情報を正しく文章化できているか確認できます。

## 5. 辞書をJSON文字列へ変換する

```python
repository_text = json.dumps(
    repository,
    ensure_ascii=False,
    indent=2,
)
```

`repository` はPythonの辞書です。`json.dumps()` によって、次のようなJSON形式の文字列へ変換します。

```json
{
  "full_name": "owner/repository",
  "description": "リポジトリの説明",
  "language": "Python"
}
```

- `ensure_ascii=False`: 日本語を `\uXXXX` 形式へ変換せず、そのまま残す
- `indent=2`: 2文字分の字下げを使い、読みやすく整形する

## 6. LLMへ渡すプロンプトを作る

```python
prompt = f"""
以下はGitHubリポジトリから取得した情報です。

{repository_text}

この情報だけを使用して、リポジトリの概要を日本語で簡潔に説明してください。
情報に含まれていないことは推測しないでください。
"""
```

`f"""..."""` は、複数行の文字列へ変数を埋め込むf-stringです。`{repository_text}` の位置に、MCPで取得した実際のデータが入ります。

LLMへ単に「リポジトリを説明してください」と依頼するのではなく、取得済みの事実と回答条件を一緒に渡します。

```text
LLMがGitHubへ直接アクセスする       ×
Hostが取得したGitHubデータを渡す    ○
```

「情報に含まれていないことは推測しない」と指定するのは、渡していない情報をLLMが補ってしまうことを減らすためです。

## 7. LLMを呼び出す

```python
answer = ask_llm(prompt)
```

`host/llm.py` の `ask_llm()` にプロンプトを渡します。内部ではOpenAI Responses APIへリクエストを送り、回答文だけを返します。

```python
response = client.responses.create(
    model="gpt-5-nano",
    input=question,
)

return response.output_text
```

今回は最低限の動作とコストを優先し、OpenAI側は同期処理のまま使用します。

## 8. LLMの回答を表示する

```python
print("\nLLMによるリポジトリの説明")
print(answer)
```

これにより、MCPから取得した構造化データとは別に、LLMが生成した説明文を確認できます。

## 非同期処理について

OpenAI APIの呼び出しは同期処理です。

```python
answer = ask_llm(prompt)
```

一方、現在使用しているFastMCP Clientの接続とツール呼び出しは非同期処理です。

```python
async with client:
    result = await client.call_tool(...)
```

現在の構成は次のとおりです。

```text
FastMCP Client: 非同期
OpenAI API:     同期
```

APIを1回ずつ順番に呼ぶ現在の学習段階では、OpenAI APIを非同期化する必要はありません。複数リクエストの同時実行や待ち時間が問題になった時点で再検討します。

## 実行方法

プロジェクトルートで実行します。

```bash
uv run python -m host.main
```

入力例です。

```text
GitHubのユーザー名または組織名: kama0523
リポジトリ名: mcp
```

実行時には、最初にMCP Serverから取得した元データが表示され、その後にLLMが生成した説明が表示されます。

## この段階で理解すること

- MCP ServerはGitHubの実データを取得する
- MCP HostはMCP ClientとLLMを順番に呼び出す
- LLMは渡されたデータを読みやすい文章へ変換する
- 現時点では、使用するMCPツールをHostが固定している
- LLMによるツール選択はまだ実装していない

## 次の段階

現在は、Hostがツール名を固定しています。

```python
"get_repository_info"
```

次の段階ではMCP Serverからツール一覧と引数仕様を取得してLLMへ渡し、ユーザーの質問に応じてLLM自身が使用するツールと引数を選ぶ処理を作ります。

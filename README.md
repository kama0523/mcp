# MCP Study

GitHubリポジトリの情報をMCP Serverから取得し、LLMで進捗を分析するための学習用プロジェクトです。

## 構成

```text
ユーザー
  ↓ 質問
MCP Host（host/main.py）
  ├─ LLMとの会話（host/llm.py）
  └─ MCP Client（host/mcp_clients.py）
          ↓ MCPで接続
     MCP Server（servers/github_server.py）
          ↓ HTTP API
        GitHub
```

- **MCP Host**: ユーザー、LLM、MCP Clientをまとめて動かすアプリ本体
- **MCP Client**: MCP Serverへ接続し、ツールの取得・実行を行う部分
- **MCP Server**: GitHub操作をMCPツールとして公開する部分

## 第1段階: MCP Serverへの接続確認

プロジェクトルートで実行します。

```bash
uv run python -m host.main
```

GitHub APIはまだ呼び出さず、Serverが公開しているツール一覧だけを表示します。

## 今後の学習順序

1. MCP Serverへの接続とツール一覧の取得
2. Hostから指定したMCPツールを実行
3. LLM APIを接続
4. LLMに利用するツールを選ばせる
5. ツールの結果をLLMに戻し、進捗レポートを生成

## 学習ノート

- [第2段階: MCPの取得結果をLLMへ渡す](docs/stage-2-connect-mcp-and-llm.md)

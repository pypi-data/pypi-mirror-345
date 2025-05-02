# Google Calendar MCP Python プロジェクト運用・開発ルール

- src layout 厳守（src/配下に実装コードを配置）
- 依存管理は uv ＋ pyproject.toml ＋ requirements.txt ＋ uv.lock で行う
- 認証は Service Account のみ、環境変数 GOOGLE_APPLICATION_CREDENTIALS でパス指定
- MCP Python SDK（modelcontextprotocol/python-sdk）を利用する
- CI/CD は Astral 公式推奨の GitHub Actions ワークフロー（publish.yaml）を利用する
- TypeScript 資産や不要な CI, Dockerfile 等は追加しない
- ドキュメントや設計ファイルは docs/配下に配置

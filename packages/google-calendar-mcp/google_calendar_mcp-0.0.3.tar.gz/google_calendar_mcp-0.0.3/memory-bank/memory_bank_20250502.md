# 2025-05-02 時点 Google Calendar MCP Python プロジェクト修正履歴

## 主な修正内容

- TypeScript 資産・旧 CI・Dockerfile 等、Python プロジェクトに不要なファイルを全削除
- src layout（src/配下に main.py, tools/）へ完全移行
- Python 3.13 対応
- MCP Python SDK（modelcontextprotocol/python-sdk）を利用
- Google Calendar API は Service Account 認証（環境変数 GOOGLE_APPLICATION_CREDENTIALS で JSON パス指定）
- 依存管理は uv ＋ pyproject.toml ＋ requirements.txt ＋ uv.lock
- Astral 公式ベストプラクティスに従った GitHub Actions（publish.yaml）で PyPI 自動公開
- README, 設計ドキュメント, .gitignore 等も整理

## 現在のディレクトリ構成（抜粋）

```
.
├── .github/workflows/publish.yaml
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.txt
├── uv.lock
├── docs/
│   ├── python-mcp-design.md
│   └── memory_bank_20250502.md
└── src/
    ├── __init__.py
    ├── main.py
    └── tools/
        ├── __init__.py
        └── calendar_tools.py
```

## 運用・開発ルール（@/.clinerules/3-python-mcp.md 等に保存推奨）

- src layout 厳守
- 依存管理は uv ＋ pyproject.toml ＋ requirements.txt ＋ uv.lock
- 認証は Service Account のみ、環境変数でパス指定
- MCP Python SDK を利用
- CI/CD は Astral 公式推奨の GitHub Actions ワークフローを利用
- TypeScript 資産や不要な CI, Dockerfile 等は追加しない

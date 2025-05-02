# CLI エントリポイント対応リファクタリング設計案

## 目的

- `uvx google-calendar-mcp` で Google Calendar MCP サーバーを起動できるようにする
- Python コミュニティ標準のエントリポイント設計に準拠

## 主な修正内容

### 1. ディレクトリ・ファイル構成

- `src/google_calendar_mcp/` ディレクトリを新規作成
- `src/main.py` → `src/google_calendar_mcp/cli.py` にロジック移植
- `src/tools/calendar_tools.py` → `src/google_calendar_mcp/calendar_tools.py` に移動
- `src/__init__.py`, `src/tools/__init__.py` → `src/google_calendar_mcp/__init__.py` に統合
- 旧 `src/main.py`, `src/tools/` ディレクトリは削除

### 2. pyproject.toml 修正

```toml
[project.scripts]
google-calendar-mcp = "google_calendar_mcp.cli:main"
```

### 3. README 修正

- 利用方法を `uvx google-calendar-mcp` での実行例に変更
- 直接 `python -m ...` での起動説明は削除

### 4. その他

- 必要に応じて import パス等も修正

---

この設計案に基づき、ファイル移動・統合・pyproject.toml/README 修正を順次実施する。

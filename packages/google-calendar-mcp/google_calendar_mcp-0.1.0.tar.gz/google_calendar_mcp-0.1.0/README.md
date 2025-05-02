# Google Calendar MCP

Google Calendar MCP (Model Context Protocol) server implementation in Python with Service Account authentication.

## 概要

このプロジェクトは、Google Calendar API を MCP (Model Context Protocol) サーバーとして実装したものです。TypeScript 版から Python への移植版で、認証方式を OAuth 2.0 から Service Account に変更しています。

## 特徴

- Python 3.13 対応
- MCP (Model Context Protocol) サーバー実装
- Google Calendar API 連携
- Service Account 認証
- uv による依存管理

## 必要条件

- Python 3.13 以上
- Google Cloud Platform のプロジェクトと有効な Service Account
- Service Account に Google Calendar API へのアクセス権限が付与されていること

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/youyo/google-calendar-mcp.git
cd google-calendar-mcp

# 依存関係のインストール
uv pip install -r requirements.txt
```

## 設定

1. Google Cloud Platform でプロジェクトを作成し、Google Calendar API を有効化します。
2. Service Account を作成し、JSON キーファイルをダウンロードします。
3. 環境変数`GOOGLE_APPLICATION_CREDENTIALS`に JSON キーファイルのパスを設定します。

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## 使い方

```bash
# サーバーを起動
python -m src.main
```

## 利用可能なツール

- `list-calendars`: 利用可能なカレンダーの一覧を表示
- `list-events`: カレンダーからイベントを一覧表示
- `search-events`: カレンダー内のイベントをテキストで検索
- `list-colors`: カレンダーイベントで利用可能な色 ID とその意味を一覧表示
- `create-event`: 新しいカレンダーイベントを作成
- `update-event`: 既存のカレンダーイベントを更新
- `delete-event`: カレンダーイベントを削除

## ライセンス

MIT

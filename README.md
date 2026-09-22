# RSS_alter

IFTTT代替RSS to Webhookスクリプト
main.pyを定期実行することで指定したフォーラムの新着と、新規投稿ページ、新規批評開始ページの通知を出します
記事系についてはsqlite3で管理します

## develop

```bash
uv sync
```

依存はuv.lock/pyproject.tomlで管理しており、requirements.txtは使用しません。
Dockerイメージもビルド時に`uv sync --locked`で依存を解決します。

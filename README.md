# RSS_alter

IFTTT代替RSS to Webhookスクリプト
main.pyを定期実行することで指定したフォーラムの新着と、新規投稿ページ、新規批評開始ページの通知を出します
記事系についてはsqlite3で管理します

## gen requirements

```bash
uv export --no-hashes --format requirements-txt > requirements.txt
```

# Git ルール

## ブランチ作成前

新しい実装を始める前に必ず main を最新化してからブランチを切ること。

```bash
git checkout main && git pull
git checkout -b feature/<name>
```

## コミット前チェック

コミット対象のファイルに絶対パス（`/home/`, `/Users/`, `/root/` など）が含まれている場合は、コミット前にユーザーへアラートを上げること。

# Git ルール

## ブランチ作成前

新しい実装を始める前に必ず main を最新化してからブランチを切ること。

```bash
git checkout main && git pull
git checkout -b feature/<name>
```

## コミット前チェック

コミット対象のファイルに絶対パス（`/home/`, `/Users/`, `/root/` など）が含まれている場合は、コミット前にユーザーへアラートを上げること。

パスワード・API キーなどの秘匿情報が含まれていないか確認すること。`.git/hooks/pre-commit` にチェックスクリプトを設置済み。リポジトリをクローンした場合は以下で再セットアップする。

```bash
cp .claude/scripts/pre-commit-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

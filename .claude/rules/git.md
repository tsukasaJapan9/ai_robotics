# Git ルール

## 初回セットアップ

リポジトリをクローンした後に以下を実行する。

```bash
# GitHub CLI の認証
gh auth login

# pre-commit フックのセットアップ
cp .claude/scripts/pre-commit-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## PR 作成

PR の作成・更新には `gh` コマンドを使う。タイトルはコンベンショナルコミット形式にする。

```bash
gh pr create --title "feat: ..." --body "..."
gh pr edit <number> --title "..." --body "..."
```

## ブランチ作成前

新しい実装を始める前に必ず main を最新化してからブランチを切ること。

```bash
git checkout main && git pull
git checkout -b feature/<name>
```

## コミット前チェック

コミット対象のファイルに絶対パス（`/home/`, `/Users/`, `/root/` など）が含まれている場合は、コミット前にユーザーへアラートを上げること。

パスワード・API キーなどの秘匿情報が含まれていないか確認すること。`.git/hooks/pre-commit` にチェックスクリプトを設置済み（初回セットアップ参照）。

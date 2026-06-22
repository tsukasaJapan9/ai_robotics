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

## PR 作成・更新

push 後は必ず PR のタイトルと概要を適切に設定すること。

- タイトルはコンベンショナルコミット形式（`feat:` / `fix:` / `docs:` など）
- 概要にはブランチ全体の変更内容・設計決定のサマリを記載する

## ブランチ作成前

新しい実装を始める前に必ず main を最新化してからブランチを切ること。

```bash
git checkout main && git pull
git checkout -b feature/<name>
```

## コミット前チェック

コミット対象のファイルに絶対パス（`/home/`, `/Users/`, `/root/` など）が含まれている場合は、コミット前にユーザーへアラートを上げること。

パスワード・API キーなどの秘匿情報が含まれていないか確認すること。`.git/hooks/pre-commit` にチェックスクリプトを設置済み（初回セットアップ参照）。

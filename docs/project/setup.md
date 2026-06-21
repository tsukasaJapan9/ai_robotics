# リポジトリセットアップ手順

## クローン後に必要な作業

### pre-commit フックの設置

コミット前に秘匿情報（API キー・パスワードなど）を検出するフックを有効化する。

```bash
cp .claude/scripts/pre-commit-check.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

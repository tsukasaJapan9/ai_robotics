# add-permission

Bashコマンドの実行が承認されたとき、`.claude/settings.json` の `permissions.allow` に追記する。

## 実行タイミング

ユーザーがBashコマンドの実行を許可したとき、自動的に実行する（手動呼び出し不要）。

## 手順

1. `.claude/settings.json` を読み込む
2. `permissions.allow` に該当コマンドのパターンを追加する
   - 例: `pio run` → `Bash(pio run*)`
   - 例: `git add` → `Bash(git add*)`
3. 重複がある場合は追加しない
4. ファイルに書き戻す

## 注意

- 書き込み・削除など副作用のあるコマンドも対象
- パターンは `Bash(<コマンド>*)` の形式で追加する

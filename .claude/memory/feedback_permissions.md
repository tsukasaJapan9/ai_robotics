---
name: feedback-permissions-allowlist
description: ユーザーがコマンドを許可したら.claude/settings.jsonのpermissions.allowに追記する
metadata:
  type: feedback
---

ユーザーがBashコマンドの実行を許可したら、都度 `.claude/settings.json` の `permissions.allow` に追記する。

**Why:** 毎回同じコマンドで許可を求めないようにするため。ユーザーが明示的に指示。

**How to apply:** コマンド実行が許可されたら、そのセッション内で `.claude/settings.json` を更新する。書き込み・削除など副作用のあるコマンドも対象。既存エントリの重複追加はしない。

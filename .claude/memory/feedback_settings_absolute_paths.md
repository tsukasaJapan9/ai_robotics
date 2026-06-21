---
name: feedback-settings-absolute-paths
description: 絶対パスを含む設定はプロジェクト settings.json ではなくユーザ設定に入れる
metadata:
  type: feedback
---

`.claude/settings.json`（プロジェクト）には絶対パスを含むエントリを入れない。

絶対パス（`/home/tsukasa/...` など）を含む Bash パーミッションルールは `~/.claude/settings.json`（ユーザ設定）に入れること。

**Why:** プロジェクト settings.json は git で共有されるため、他の環境では動かないローカルパスを含むべきでない。

**How to apply:** Claude Code が自動追加したパーミッションルールをコミット前に確認し、絶対パスを含むものはユーザ設定へ移動する。

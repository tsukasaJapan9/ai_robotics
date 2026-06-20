---
name: feedback-memory-location
description: メモリの md ファイルは ai_robotics ディレクトリ内の .claude/memory/ に保存する
metadata:
  type: feedback
---

メモリ用 md ファイルはすべて `.claude/memory/` に保存する（リポジトリ直下からの相対パス）。

**Why:** プロジェクト内にまとめて管理したい（git で追跡できる・見つけやすい）。

**How to apply:** 新しいメモリファイルを作成するときは必ずこのディレクトリに保存する。ファイルパスはリポジトリルートからの相対パスで記載する。

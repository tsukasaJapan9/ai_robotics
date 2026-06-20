---
name: feedback-project-structure
description: プロジェクト内のファイル保存先ルール（knowledge/rules/skills/agents）
metadata:
  type: feedback
---

プロジェクト内のファイルは種類ごとに以下のディレクトリに保存する。

- 開発ナレッジ → `.claude/knowledge/`
- ルール → `.claude/rules/`
- スキル → `.claude/skills/`
- サブエージェント → `.claude/agents/`
- メモリ → `.claude/memory/`（[[feedback-memory-location]] 参照）
- ドキュメント → `docs/<適切なサブディレクトリ>/`（プロジェクトルート直下の docs/）

**Why:** プロジェクト内で役割ごとにディレクトリが分かれており、それに従って管理する。

**How to apply:** 各種ファイルを作成・保存するとき、上記の対応ディレクトリに置く。ファイルパスを記載する場合はリポジトリルートからの相対パスで書く（例: `firmware/m5stack_core2/src/main.cpp`）。

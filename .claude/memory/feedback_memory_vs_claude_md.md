---
name: feedback-memory-vs-claude-md
description: memory と CLAUDE.md の使い分けを意識する
metadata:
  type: feedback
---

memory と CLAUDE.md の役割を明確に使い分ける。

- `CLAUDE.md` — ユーザーが Claude に守らせる指示・ルール
- `.claude/memory/` — Claude が会話から学んで自分で書き留める観察メモ

**Why:** ユーザーから明示的に意識するよう指示された。

**How to apply:** 絶対守るべきルールは CLAUDE.md へ、会話で気づいたユーザーの好み・プロジェクト背景・フィードバックは memory へ保存する。memory にルールを書かない。

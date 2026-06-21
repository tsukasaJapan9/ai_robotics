---
name: feedback-git-branch
description: 新しい実装を始める前に必ず main を checkout/pull してからブランチを切ること
metadata:
  type: feedback
---

新しい実装を始める前に必ず以下の手順を守ること：

```bash
git checkout main && git pull
git checkout -b feature/<name>
```

**Why:** 過去に feature ブランチのままで新しい実装を始めてしまい、ユーザーに指摘された。

**How to apply:** 新しいタスクの実装を始める際、現在のブランチが main かどうか確認する。main でなければ必ず切り替えてから pull し、新しいブランチを作成する。「マージしました」などのユーザー発言がブランチ切り替えのトリガー。

[[feedback-memory-vs-claude-md]]

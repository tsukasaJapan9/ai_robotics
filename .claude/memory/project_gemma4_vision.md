---
name: project-gemma4-vision
description: gemma4 は画像を無視することがある（間欠的なビジョン失敗）
metadata:
  type: project
---

gemma4 はビジョン対応モデルだが、**画像を無視して「画像が提供されていません」と返すことが間欠的に発生する**。

保存した画像は正常な JPEG であり、リクエストの形式も正しい。モデル側の非決定的な挙動によるもの。

**Why:** LM Studio + gemma4 の組み合わせで camera_client を開発中に確認。prompt_tokens が低くなることはなく（画像は渡っている）、モデルが画像を処理しないケースがある。

**How to apply:** gemma4 を使った画像解析では「画像なし」レスポンスに対するリトライ処理や、interval を設けて LM Studio への負荷を下げることを検討する。

# ドキュメントスタイル

## 冗長な記載を避ける

- JSON 例は1つにまとめる。差分はフィールドにコメントか箇条書きで補足する
- 同じ情報を言い換えて繰り返さない
- 「〜します」「〜を行います」などの説明的な前置きは省く

**NG**
```
通常レスポンス:
{"status": "ok"}

Perception モジュールはさらに media_type を返す:
{"status": "ok", "media_type": "image/jpeg"}
```

**OK**
```
{"status": "ok", "media_type": "<mime-type>|null"}

- `media_type`: Perception モジュールのみ設定。それ以外は null。
```

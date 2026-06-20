# LM Studio セットアップ

## インストール

公式サイトからダウンロード：https://lmstudio.ai

## モデルのダウンロード

LM Studio の「Discover」タブでモデルを検索してダウンロード。

## API サーバーの起動

「Local Server」タブでモデルをロードして「Start Server」。

デフォルト: `http://localhost:1234`

## curl でチャット

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:e4b",
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "stream": false
  }'
```

画像を渡す場合（base64 エンコード）：

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"gemma4:e4b\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {\"type\": \"text\", \"text\": \"Describe this image.\"},
          {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/jpeg;base64,$(base64 -w0 image.jpg)\"}}
        ]
      }
    ],
    \"stream\": false
  }"
```

Thinking を有効にする場合：

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma4:e4b",
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "thinking": {
      "type": "enabled",
      "budget_tokens": 1024
    },
    "stream": false
  }'
```

※ モデルが thinking に対応している場合のみ有効。GUI の「Extended Thinking」設定も確認すること。

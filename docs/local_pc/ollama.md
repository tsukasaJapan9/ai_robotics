# ollama セットアップ

## インストール

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

自動起動は不要なので無効化：

```bash
sudo systemctl disable --now ollama
```

## モデルの保存先

デフォルトは `~/.ollama/models`。外部ストレージに変えたい場合は、**サーバー起動時に明示的に渡す**（`~/.bashrc` への export だけでは引き継がれないことがある）。

## サーバー起動

```bash
# デフォルト（~/.ollama/models）
ollama serve &

# 保存先を指定する場合
OLLAMA_MODELS=/media/tsukasa/DATA/ollama/models ollama serve &
```

起動確認：

```bash
curl http://localhost:11434/api/tags
```

終了：

```bash
kill $(pgrep ollama)
```

## モデルのダウンロード

サーバー起動後に pull する：

```bash
ollama pull gemma4:e4b
```

削除：

```bash
ollama rm gemma4:e4b
```

## 動作確認

```bash
# テキスト
ollama run gemma4:e4b "Hello"

# API
curl http://localhost:11434/api/tags
```

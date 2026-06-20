# ollama セットアップ

## インストール

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

自動起動は不要なので無効化：

```bash
sudo systemctl disable --now ollama
```

## モデルの保存先を外部ストレージに変更

`~/.bashrc` に追記：

```bash
export OLLAMA_MODELS=/mnt/外部ストレージのパス/ollama/models
```

## サーバー起動

```bash
ollama serve &
```

終了：

```bash
kill $(pgrep ollama)
```

## モデルのダウンロード

```bash
ollama pull gemma4:e4b
```

## 動作確認

```bash
# テキスト
ollama run gemma4:e4b "Hello"

# API
curl http://localhost:11434/api/tags
```

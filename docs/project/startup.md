# サービス起動手順

## 事前準備

1. **Stack-chan** の電源を入れ、画面に IP アドレスが表示されるまで待つ
2. **LM Studio** を起動し、モデル（`gemma4:e4b`）をロードしてローカルサーバーを開始する

## 起動（それぞれ別ターミナルで順番に実行）

```bash
# ① センサー（カメラ）
cd local_pc/platform/sensors/camera_m5stack
uv run src/main.py --url <Stack-chanのIP>

# ② 推論
cd local_pc/platform/inference/lm_studio
uv run src/main.py

# ③ アクション（サーボ）
cd local_pc/platform/actions/stackchan_servo
uv run src/main.py --url <Stack-chanのIP>

# ④ パイロット（①②③ 起動後に実行）
cd local_pc/platform/pilots/wonder_pilot
uv run src/main.py
```

④ を起動するとパイプライン（カメラ → 推論 → サーボ）が動き始める。

## ポート一覧

| モジュール | ポート |
|---|---|
| camera_m5stack | 8101 |
| lm_studio | 8201 |
| stackchan_servo | 8301 |
| wonder_pilot | 8000 |

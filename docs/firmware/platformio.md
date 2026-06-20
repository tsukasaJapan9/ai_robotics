# PlatformIO ビルド＆転送

## 基本コマンド

プロジェクトディレクトリ（`platformio.ini` があるディレクトリ）で実行する。

```bash
# ビルド
pio run

# ビルド＆転送
pio run --target upload

# シリアルモニタ
pio device monitor

# 転送＆シリアルモニタ
pio run --target upload && pio device monitor

# クリーン
pio run --target clean
```

## 例: CoreS3 camera_sample

```bash
cd firmware/m5stack_core_s3/examples/camera_sample
pio run --target upload
```

## 環境を指定する場合

`platformio.ini` に複数の `[env:xxx]` がある場合は `-e` で指定する。

```bash
pio run -e m5stack-cores3 --target upload
```

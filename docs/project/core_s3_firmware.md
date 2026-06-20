# CoreS3 ファームウェア開発方針

## 概要

M5Stack CoreS3 向けのロボットファームウェア開発。
既存の Core2 プロジェクト（`firmware/m5stack_core2/`）を CoreS3 向けに展開する。

## 方針

- 新しい CoreS3 プロジェクトは `firmware/m5stack_core_s3/` 以下に作成する（Core2 と並列）
- PlatformIO の `board = m5stack-cores3`、ライブラリは M5Unified（既存と同じ）
- 通信は USB シリアル

## Core2 との主な差異（実装上の注意）

| 項目 | Core2 | CoreS3 |
|---|---|---|
| SoC | ESP32 | ESP32-S3 |
| IMU | MPU6886 | BMI270 + BMM150 |
| 物理ボタン | 3個 | なし（タッチのみ） |
| 内部 I2C | G21/G22 | G11/G12 |
| PORT.C TX/RX | G14/G13 | G18/G17 |

- M5Unified API は共通で使える
- 物理ボタン（BtnA/B/C）が使えないためタッチで代替
- esp_camera と M5Unified の I2C バス競合に注意（`sccb_i2c_port` で既存バスを再利用する）

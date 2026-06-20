# M5Stack CoreS3 ハードウェア仕様

出典: https://docs.m5stack.com/en/core/CoreS3

## SoC・メモリ
- SoC: ESP32-S3 Dual-core Xtensa LX7 @ 240MHz
- Flash: 16MB
- PSRAM: 8MB Quad
- Wi-Fi: 2.4GHz

## ディスプレイ・タッチ
- IPS LCD: 2.0インチ 320×240 (ILI9342C)
- タッチ: FT6336U（静電容量式）
- 物理ボタンなし（タッチのみ）

## センサー
- IMU: BMI270（6軸: 加速度 + ジャイロ）
- 磁気センサー: BMM150（3軸）
- 近接センサー: LTR-553ALS-WA
- RTC: BM8563
- カメラ: GC0308（0.3MP）

## オーディオ
- アンプ: AW88298（16-bit I2S、1W）
- マイク: ES7210（デュアルマイク）

## 電源
- PMU: AXP2101
- バッテリ: 500mAh
- 外部電源: DC 9〜24V（DinBase 経由）

## 通信・ストレージ
- USB: Type-C（OTG / CDC）
- microSD: 最大 16GB

## ピン配置

### 内部バス
| 機能 | GPIO |
|---|---|
| LCD MOSI | G37 |
| LCD SCK | G36 |
| LCD CS | G3 |
| LCD DC | G35 |
| SD CS | G4 |
| I2C SDA（内部） | G12 |
| I2C SCL（内部） | G11 |
| UART RXD0 | G44 |
| UART TXD0 | G43 |
| マイク / I2S | G34, G33, G13, G14, G0 |

### 外部ポート
| ポート | ピン |
|---|---|
| PORT.A (Grove/I2C) | G2(SDA), G1(SCL) |
| PORT.B (GPIO/ADC) | G9, G8 |
| PORT.C (UART) | G17(RX), G18(TX) |

### M5-Bus 拡張
- ADC: G10
- GPIO: G5, G6, G7

## PlatformIO 設定

```ini
[env:m5stack-cores3]
platform = espressif32
board = m5stack-cores3
framework = arduino
lib_deps = m5stack/M5Unified@^0.2.5
```

## Core2 との主な差異
| 項目 | Core2 | CoreS3 |
|---|---|---|
| SoC | ESP32 | ESP32-S3 |
| IMU | MPU6886 | BMI270 + BMM150 |
| 物理ボタン | 3個 | なし（タッチのみ） |
| カメラ | なし | GC0308 |
| マイク | なし | デュアルマイク |
| PORT.C TX/RX | G14/G13 | G18/G17 |
| 内部 I2C | G21/G22 | G11/G12 |

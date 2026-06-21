# Stack-chan ハードウェア仕様

出典: https://docs.m5stack.com/en/arduino/stackchan/servo

## ベースハードウェア

M5Stack CoreS3 ベース（Kickstarter クラウドファンディング品）

## サーボ

- 型番: SCS0009（Feetech シリアルバスサーボ）
- 通信: UART Serial2（RX=GPIO7, TX=GPIO6, 1Mbps）
- 電源制御: M5IOE1 I/O エキスパンダ（I2C アドレス 0x6F / PY32IOExpander）経由

### 軸と角度

| 軸 | 方向 | 範囲 | 中央 | 備考 |
|---|---|---|---|---|
| X（水平） | 小→右回転、大→左回転 | 0〜360° | 160° | 角度制限不要 |
| Y（垂直） | 小→上、大→下 | 5〜85° | 45° | 限界角度でロックし故障する恐れがあるため制限する |

### camera_client での制御範囲

PC 側（servo_control.py）では Y 軸を 50〜85° に絞って使用。

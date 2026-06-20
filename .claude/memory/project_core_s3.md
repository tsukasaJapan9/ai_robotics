---
name: project-core-s3
description: M5Stack Core S3 向けロボットファームウェア開発の方針と状況
metadata:
  type: project
---

M5Stack Core S3 向けのロボットファームウェア開発を開始予定（2026-06-20時点では意思表示のみ、実装未着手）。

**Why:** 既存の Core2 プロジェクト（`firmware/m5stack_core2/`）を Core S3 向けに展開するための第一歩。

**How to apply:**
- 新しい Core S3 プロジェクトは `firmware/m5stack_core_s3/` 以下に作成する（Core2 と並列）
- PlatformIO の `board = m5stack-cores3`、ライブラリは M5Unified（既存と同じ）
- 通信は USB シリアル（既存と同じ方式）
- Core S3 の IMU は BMI270（Core2 の MPU6886 とは異なるが M5Unified API は共通）
- 物理ボタンがなく、タッチ画面のみ（BtnA/B/C の扱いに注意）

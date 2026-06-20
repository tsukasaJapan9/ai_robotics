# ai_robotics

## ディレクトリ構成

```
ai_robotics/
├── firmware/           # マイコン向けファームウェア
│   ├── arduino/        # Arduino スケッチ（Dynamixel モーター制御など）
│   └── m5stack_core2/  # M5Stack Core2 向け PlatformIO プロジェクト
├── local_pc/           # PC 側で動かす Python スクリプト
├── docs/               # プロジェクトドキュメント
│   ├── architecture/   # アーキテクチャ設計
│   ├── project/        # プロジェクト関連ドキュメント
│   └── spec/           # 仕様書
├── service/            # サービス・バックエンド関連
└── .claude/            # Claude Code 設定
    ├── memory/         # Claude の観察メモ（会話をまたいで保持）
    ├── knowledge/      # 開発ナレッジ・参考情報
    ├── rules/          # ルールファイル（このファイルから @import して使う）
    ├── skills/         # カスタムスキル
    └── agents/         # サブエージェント定義
```

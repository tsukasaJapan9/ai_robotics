# ai_robotics

@.claude/rules/firmware.md
@.claude/rules/coding_style.md
@.claude/rules/git.md
@.claude/rules/docs_style.md


## ファイル保存先

| 種類 | 保存先 |
|---|---|
| 開発ナレッジ | `.claude/knowledge/` |
| ルール | `.claude/rules/` |
| スキル | `.claude/skills/` |
| サブエージェント | `.claude/agents/` |
| メモリ | `.claude/memory/` |
| ドキュメント | `docs/<適切なサブディレクトリ>/` |

ファイルパスはリポジトリルートからの相対パスで記載する。

## ディレクトリ構成

```
ai_robotics/
├── firmware/           # マイコン向けファームウェア
│   ├── arduino/        # Arduino スケッチ（Dynamixel モーター制御など）
│   ├── m5stack_core2/  # M5Stack Core2 向け PlatformIO プロジェクト
│   └── m5stack_core_s3/ # M5Stack CoreS3 向け PlatformIO プロジェクト
│       └── examples/    # サンプルコード
├── local_pc/           # PC 側で動かす Python スクリプト・モジュール群
│   └── platform/       # プラットフォーム本体
│       ├── schemas/    # 共有スキーマパッケージ（全モジュールの path dependency）
│       ├── orchestrator/ # Orchestrator（サービスディスカバリ・ワイヤリング）
│       ├── sensors/    # SensorModule 実装群（例: camera/）
│       ├── inference/  # InferenceModule 実装群（例: openai_compat/, claude/）
│       └── actions/    # ActionModule 実装群（例: servo/）
├── docs/               # プロジェクトドキュメント
│   ├── architecture/   # アーキテクチャ設計
│   ├── firmware/       # ファームウェア開発ドキュメント
│   ├── local_pc/       # PC 側ツール・環境構築ドキュメント
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

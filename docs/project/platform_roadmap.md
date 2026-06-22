# Embodied AI Platform ロードマップ

## コンセプト

> **あらゆるロボット・センサ・LLMを接続できる「神経系ミドルウェア」**

身体性を持ったロボットのためのソフトウェア基盤。各モジュールは疎結合で、デバイス・LLM・センサを柔軟に組み合わせられる。

## アーキテクチャ

```
SensorModule ──→ Pilot ──→ InferenceModule
                    │
                    └──────────→ ActionModule
```

すべてのモジュール間通信は Pilot を介する。Viewer など読み取り専用クライアントのみ SensorModule の `/stream` に直接接続してよい。

**モジュール間インターフェース**: HTTP REST（汎用・言語非依存）

## 設計原則

| 原則 | 内容 |
|---|---|
| **疎結合** | 各モジュールは HTTP API を持ち、独立起動・交換可能 |
| **LLM非依存** | InferenceModule がバックエンドを抽象化（OpenAI互換 / Claude） |
| **HW非依存** | 具体クラスがデバイス差異を吸収（例: M5StackCameraSensorModule） |
| **段階的拡張** | 最小構成から始めてモジュールを足していく |

## モジュール構成

詳細は [docs/spec/module_interface.md](../spec/module_interface.md) を参照。

| モジュール | 基底クラス | 具体クラス例 |
|---|---|---|
| センサ | `SensorModule` | `M5StackCameraSensorModule` |
| 推論 | `InferenceModule` | `OpenAIInferenceModule`, `ClaudeInferenceModule` |
| アクション | `ActionModule` | `FeetechServoActionModule` |
| 制御 | `Pilot` | `wonder_eye`, `voice_chat` |

## 現プロジェクトとの対応

```
現在                      →  プラットフォーム化後
─────────────────────────────────────────────────
camera_client/stream.py   →  M5StackCameraSensorModule
camera_client/analyzer.py →  OpenAIInferenceModule
servo_control.py          →  FeetechServoActionModule
main.py                   →  pilots/wonder_eye
api.py (FastAPI)          →  各モジュールの共通 IF パターン
```

## ロードマップ

### Phase 1: プラットフォーム基盤の整備
- [ ] `local_pc/platform/` ディレクトリ構成を作成
- [ ] 共有スキーマ（`platform/schemas/`）を Pydantic で定義
- [ ] 既存 camera_client を `M5StackCameraSensorModule` / `OpenAIInferenceModule` / `FeetechServoActionModule` に分割
- [ ] `pilots/wonder_eye` として Pilot を実装（サービスディスカバリ含む）
- [ ] LLM バックエンドの切り替えを起動引数で可能に

### Phase 2: SensorModule の拡張
- [ ] `MicSensorModule` の追加（マイク → ASR → LLM）
- [ ] `IMUSensorModule` の追加
- [ ] 複数センサのフュージョン

### Phase 3: ActionModule の拡張
- [ ] ロボットアームモジュール（`ArmActionModule`）
- [ ] 表情・LED 表現モジュール

### Phase 4: Pilot の高度化
- [ ] コンテキスト・記憶の永続化
- [ ] マルチエージェント構成（思考 LLM + 行動 LLM を分離）
- [ ] 複数マシン構成への対応（mDNS によるサービスディスカバリ）

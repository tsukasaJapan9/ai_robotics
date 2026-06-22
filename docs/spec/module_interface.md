# モジュールインターフェース仕様

Embodied AI Platform の各モジュールが実装すべき HTTP API の仕様。

## 設計方針

### クラス階層と命名規則

`SensorModule` / `InferenceModule` / `ActionModule` を基底クラスとして定義し、具体的な実装はそれを継承した `{具体名}{基底クラス名}` の形で作る。

```
SensorModule          # 基底: /stream, /snapshot の契約を定義
├── CameraSensorModule
│   └── M5StackCameraSensorModule   # ハードウェア固有実装
├── MicSensorModule
└── IMUSensorModule
    └── M5StackIMUSensorModule

InferenceModule       # 基底: /infer の契約を定義
├── OpenAIInferenceModule    # LM Studio / Ollama / OpenAI（OpenAI互換）
└── ClaudeInferenceModule    # Anthropic API

ActionModule          # 基底: /action, /action/reset の契約を定義
├── ServoActionModule
│   └── FeetechServoActionModule    # Feetech SCS0009 固有実装
└── ArmActionModule
```

命名規則: `{ハードウェア名}{センサ種別}SensorModule` / `{ハードウェア名}{アクチュエータ種別}ActionModule`

基底クラスは HTTP インターフェースの契約（エンドポイント・スキーマ）を定義する。
具体クラスはデバイスやバックエンド固有の実装を持つ。

### ディレクトリ構成

```
local_pc/
└── platform/
    ├── schemas/                # 共有スキーマパッケージ（全モジュールの path dependency）
    │   ├── pyproject.toml
    │   └── src/schemas/
    │       └── schemas.py
    ├── pilots/                     # Pilot 実装群（ユースケースごとに1つ）
    │   ├── wonder_eye/             # 視線制御 Pilot
    │   │   ├── pyproject.toml
    │   │   └── src/
    │   │       ├── main.py
    │   │       ├── discovery.py    # サービスディスカバリ（ポートスキャン）
    │   │       └── pipeline.py     # ワイヤリング・推論ループ制御
    │   └── voice_chat/             # 音声対話 Pilot（将来）
    │       ├── pyproject.toml
    │       └── src/main.py
    ├── sensors/                    # SensorModule 実装群
    │   ├── camera_m5stack/         # M5StackCameraSensorModule
    │   │   ├── pyproject.toml
    │   │   └── src/main.py
    │   ├── camera_usb/             # USBCameraSensorModule（将来）
    │   └── mic_usb/                # MicSensorModule（将来）
    ├── inference/                  # InferenceModule 実装群
    │   ├── openai_compat/          # OpenAIInferenceModule（LM Studio / Ollama / OpenAI）
    │   │   ├── pyproject.toml
    │   │   └── src/main.py
    │   └── claude/                 # ClaudeInferenceModule
    │       ├── pyproject.toml
    │       └── src/main.py
    └── actions/                    # ActionModule 実装群
        ├── servo_feetech/          # FeetechServoActionModule
        │   ├── pyproject.toml
        │   └── src/main.py
        ├── servo_dynamixel/        # DynamixelServoActionModule（将来）
        └── arm/                    # ArmActionModule（将来）
```

各モジュールは独立した uv プロジェクトとし、`platform/schemas/` を path dependency として参照する。

---

## 共通規則

### スキーマ定義方針

リクエスト・レスポンスのスキーマは Pydantic モデルを正規定義とする。

- 共有スキーマは `local_pc/platform/` パッケージに集約する
- 各モジュールは path dependency として参照する（`uv add --editable ../platform`）
- このドキュメントは設計の意図と概要を記述する。詳細な型定義はコードが正式仕様

**想定するモデル構成**

```
local_pc/platform/src/platform/
└── schemas.py
    ├── HealthResponse       # 共通
    ├── ErrorResponse        # 共通
    ├── InferRequest         # InferenceModule
    ├── InferResponse        # InferenceModule
    ├── ActionRequest        # ActionModule 共通
    ├── ActionResponse       # ActionModule 共通
    └── MoveParams           # ServoActionModule 固有
```

### ベースURL

各モジュールは独立したプロセスとして起動し、固有のポートを持つ。

### ポート番号ルール

| 番台 | 用途 | 例 |
|---|---|---|
| 8000 | Pilot | 8000 |
| 8100〜 | SensorModule | CameraSensorModule: 8101、MicSensorModule: 8102 |
| 8200〜 | InferenceModule | OpenAIInferenceModule: 8201 |
| 8300〜 | ActionModule | ServoActionModule: 8301 |

### 共通エンドポイント

すべてのモジュールが実装する。

#### `GET /health`

**Response 200**
```json
{
  "status": "ok",
  "module": "<module-name>",
  "media_type": "<mime-type>|null"
}
```

- `media_type`: SensorModule は MIME タイプを返す（例: `"image/jpeg"`）。それ以外は `null`

### エラーレスポンス

```json
{
  "error": "<message>"
}
```

---

## SensorModule

センサからデータを取得し、下流へ提供するモジュール。

すべての SensorModule が共通で実装するエンドポイント:

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/health` | GET | 死活確認（`media_type` を含む） |
| `/stream` | GET | センサデータの連続配信 |
| `/snapshot` | GET | 最新データを1件取得 |

Content-Type はモジュールごとに異なる:

| モジュール | `/stream` Content-Type | `/snapshot` Content-Type |
|---|---|---|
| CameraSensorModule | `multipart/x-mixed-replace; boundary=frame` | `image/jpeg` |
| MicSensorModule | `audio/wav` (チャンク) | `audio/wav` |
| IMUSensorModule | `text/event-stream` (SSE) | `application/json` |

### CameraSensorModule

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/health` | GET | 死活確認（`media_type: "image/jpeg"`） |
| `/stream` | GET | MJPEG ストリーム |
| `/snapshot` | GET | 最新フレーム1枚 |

#### `GET /stream`

**Response 200**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- 継続的に JPEG フレームを配信する

#### `GET /snapshot`

**Response 200**
- Content-Type: `image/jpeg`

**Response 503**
- フレームが未取得の場合

---

## InferenceModule

プロンプトとスキーマを受け取り、LLM を呼び出して構造化データを返すモジュール。
ステートレス。履歴・コンテキスト管理は Pilot が担う。
Pilot は LLM バックエンドの種類を意識しない。

### バックエンド抽象化

LLM バックエンドはアダプタパターンで差し替え可能にする。起動引数で選択する。

| バックエンド | 実装方式 |
|---|---|
| LM Studio | OpenAI 互換 API（`/v1/chat/completions`） |
| Ollama | OpenAI 互換 API（`/v1/chat/completions`） |
| OpenAI | OpenAI API |
| Claude | Anthropic API（tool_use で構造化出力） |

LM Studio / Ollama / OpenAI は同一アダプタで対応できる（OpenAI 互換）。
Claude のみ別アダプタが必要。

### エンドポイント

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/health` | GET | 死活確認 |
| `/infer` | POST | 推論を実行し構造化データを返す |

#### `POST /infer`

**Request Body**
```json
{
  "prompt": "<システムプロンプト>",
  "schema": { "<JSON Schema>" },
  "data": {
    "type": "image",
    "content": "<base64>",
    "media_type": "image/jpeg"
  }
}
```

- `schema`: 出力に期待する JSON Schema。LLM の structured output 機能に渡す
- `data`: 任意。Pilot が SensorModule からデータを取得し base64 エンコードして渡す
  - `type`: `image` / `audio` / `text`
  - `content`: base64 エンコードされたバイナリ、またはテキスト
  - `media_type`: MIME タイプ（例: `image/jpeg`, `audio/wav`）

**Response 200**
```json
{
  "result": { "<schema に沿った構造化データ>" },
  "model": "gemma4:e4b",
  "timestamp": "14:23:01"
}
```

**Response 503**
```json
{
  "error": "backend unavailable"
}
```

---

## ActionModule

指令を受けてアクチュエータを動かすモジュール。

すべての ActionModule が共通で実装するエンドポイント:

| エンドポイント | メソッド | 説明 |
|---|---|---|
| `/health` | GET | 死活確認 |
| `/action` | POST | アクションを実行 |
| `/action/reset` | POST | 初期状態に戻す |

#### `POST /action`

**Request Body**
```json
{
  "type": "<action-type>",
  "params": {}
}
```

**Response 200**
```json
{ "ok": true }
```

**Response 400**
```json
{ "error": "unknown action type: <type>" }
```

#### `POST /action/reset`

**Response 200**
```json
{ "ok": true }
```

### ServoActionModule

Stack-chan のサーボ制御モジュール。

| type | 説明 | params |
|---|---|---|
| `move` | 指定角度に移動 | `x`, `y` |

#### `move` の params

| フィールド | 型 | 範囲 | 省略時 |
|---|---|---|---|
| `x` | int | 0〜360（中央: 160） | 現在値を維持 |
| `y` | int | 50〜85（中央: 60） | 現在値を維持 |

**例**
```json
{
  "type": "move",
  "params": {"x": 160, "y": 60}
}
```

---

## Pilot

### サービスディスカバリ

Pilot 起動時にポート番号ルールに基づいてスキャンし、応答したモジュールを自動登録する。追加インフラ不要。

```
起動
 ↓
8101〜8199 をスキャン → GET /health 応答あり → SensorModule として登録
8201〜8299 をスキャン → GET /health 応答あり → InferenceModule として登録
8301〜8399 をスキャン → GET /health 応答あり → ActionModule として登録
 ↓
media_type で互換性を確認してワイヤリングを決定
```

- スキャン対象ホストは設定で指定（デフォルト: `localhost`）
- `/health` の `media_type` フィールドでモジュールの種別・対応データ型を判別する
- 将来複数マシン構成になった場合は mDNS (zeroconf) への移行を検討する

---

## モジュール間ワイヤリング

すべてのモジュール間通信は Pilot を介して行う。モジュール同士が直接通信することはない。

```
SensorModule ──→ Pilot ──→ InferenceModule
                     │
                     └──────────→ ActionModule
```

Pilot の責務:
- 各モジュールの `/health` を確認し、`media_type` で互換性を検証する
- SensorModule から `/snapshot` でデータを取得し、base64 エンコードして InferenceModule に渡す
- InferenceModule の推論結果を受け取り、ActionModule に `/action` を発行する
- 履歴・コンテキストを管理する

**ファンアウト（複数コンシューマ）**

Viewer など読み取り専用クライアントは、SensorModule の `/stream` に直接接続してよい（Pilot を介さない唯一の例外）。

```
CameraSensorModule :8101
  ├── /stream ← Viewer が直接接続（読み取り専用）
  └── /snapshot ← Pilot が取得
```

**視線制御構成（現在）**
```
CameraSensorModule :8101
    ↓ /snapshot
Pilot       :8000
    ↓ POST /infer (base64)
InferenceModule    :8201
    ↓ result
Pilot       :8000
    ↓ POST /action
ServoActionModule  :8301
```

**音声対話構成（将来）**
```
MicSensorModule    :8102
    ↓ /snapshot
Pilot       :8000
    ↓ POST /infer (base64)
InferenceModule    :8201
    ↓ result
Pilot       :8000
    ↓ POST /action
ActionModule       :8301
```

各モジュールの接続先は起動引数または設定ファイルで指定する（ハードコードしない）。

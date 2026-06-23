"""
Wonder Pilot - カメラ画像を取得し LLM で解析、Stack-chan サーボを動かすパイロット。

Port: 8000

Pipeline: SensorModule(/snapshot) → InferenceModule(/infer) → ActionModule(/action)
"""
import argparse
import base64
import logging
import threading
import time
from datetime import datetime

import requests
import uvicorn
from fastapi import FastAPI
from schemas import ActionRequest, HealthResponse, InferData, InferRequest
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MODULE_NAME = "wonder_pilot"

# X: 0-360 (160=正面中央), Y: 50-85 (60=正面中央)
INFER_SCHEMA = {
    "type": "object",
    "properties": {
        "x": {"type": "integer"},
        "y": {"type": "integer"},
        "reason": {"type": "string"},
    },
    "required": ["x", "y", "reason"],
    "additionalProperties": False,
}

PROMPT = """\
あなたは好奇心旺盛なロボットであり、人間の世界を探索しています。
同じ場所が5回続いた場合は、xやyの値を大きく変更して新しいものを見るようにすること。

画像の中で最も目を引くものに注目し、JSONスキーマに従って答えてください。

X軸（水平）: 0〜360（160が正面中央、小さいほど右、大きいほど左）
Y軸（垂直）: 50〜85（60が正面中央、小さいほど上、大きいほど下）\
"""

_sensor_url = ""
_infer_url = ""
_action_url = ""
_interval = 0.0

latest_result: dict | None = None
history: list[dict] = []  # {"time": str, "x": int, "y": int, "reason": str}

app = FastAPI()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", module=MODULE_NAME)


@app.get("/status")
async def status():
    return {"latest": latest_result, "history": history}


def _build_prompt() -> str:
    if not history:
        return PROMPT
    lines = "\n".join(
        f"- [{e['time']}] x={e['x']} y={e['y']} reason={e['reason']}"
        for e in history
    )
    return PROMPT + f"\n\nこれまでの注目履歴:\n{lines}"


def _pilot_loop():
    global latest_result
    last_run = 0.0

    while True:
        now = time.time()
        if now - last_run < _interval:
            time.sleep(0.1)
            continue
        last_run = now

        # スナップショット取得
        try:
            resp = requests.get(f"{_sensor_url}/snapshot", timeout=(10, 30))
            resp.raise_for_status()
            frame = resp.content
        except Exception as e:
            logger.warning(f"Snapshot failed: {e}")
            time.sleep(2)
            continue

        # 推論
        req = InferRequest(
            prompt=_build_prompt(),
            schema=INFER_SCHEMA,
            data=InferData(
                type="image",
                content=base64.b64encode(frame).decode(),
                media_type="image/jpeg",
            ),
        )
        try:
            resp = requests.post(
                f"{_infer_url}/infer", json=req.model_dump(), timeout=60
            )
            resp.raise_for_status()
            result = resp.json()["result"]
        except Exception as e:
            logger.warning(f"Inference failed: {e}")
            continue

        x = max(0, min(360, int(result["x"])))
        y = max(50, min(85, int(result["y"])))
        reason = result.get("reason", "")
        ts = datetime.now().strftime("%H:%M:%S")
        logger.info(f"[{ts}] x={x} y={y} reason={reason}")

        latest_result = {"time": ts, "x": x, "y": y, "reason": reason}
        history.append(latest_result)
        if len(history) > 10:
            history.pop(0)

        # サーボ移動
        try:
            requests.post(
                f"{_action_url}/action",
                json=ActionRequest(type="move", params={"x": x, "y": y}).model_dump(),
                timeout=2,
            )
        except Exception as e:
            logger.warning(f"Action failed: {e}")


def main():
    global _sensor_url, _infer_url, _action_url, _interval
    parser = argparse.ArgumentParser(description="Wonder Pilot")
    parser.add_argument("--sensor-url", default="http://localhost:8101")
    parser.add_argument("--infer-url", default="http://localhost:8201")
    parser.add_argument("--action-url", default="http://localhost:8301")
    parser.add_argument("--interval", type=float, default=0.0, help="推論間隔（秒）")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    _sensor_url = args.sensor_url.rstrip("/")
    _infer_url = args.infer_url.rstrip("/")
    _action_url = args.action_url.rstrip("/")
    _interval = args.interval

    logger.info(f"Sensor:   {_sensor_url}")
    logger.info(f"Infer:    {_infer_url}")
    logger.info(f"Action:   {_action_url}")
    logger.info(f"Interval: {_interval}s")
    logger.info(f"Port:     {args.port}")

    threading.Thread(target=_pilot_loop, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_graceful_shutdown=0)


if __name__ == "__main__":
    main()

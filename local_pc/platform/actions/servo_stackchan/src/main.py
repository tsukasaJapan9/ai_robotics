"""
Stack-chan サーボ制御 ActionModule。
Stack-chan ファームウェアの HTTP API (/servo, /center) にリクエストを転送する。

Port: 8301
"""
import argparse
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schemas import ActionRequest, ActionResponse, HealthResponse

MODULE_NAME = "servo_stackchan"

_servo_url = ""

app = FastAPI()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", module=MODULE_NAME)


@app.post("/action", response_model=ActionResponse)
async def action(body: ActionRequest):
    if body.type == "move":
        params: dict[str, int] = {}
        if body.params.get("x") is not None:
            params["x"] = body.params["x"]
        if body.params.get("y") is not None:
            params["y"] = body.params["y"]
        if not params:
            return ActionResponse(ok=True)
        try:
            resp = requests.get(f"{_servo_url}/servo", params=params, timeout=2.0)
            resp.raise_for_status()
            return ActionResponse(ok=True)
        except Exception as e:
            return JSONResponse(status_code=502, content={"error": str(e)})
    else:
        return JSONResponse(status_code=400, content={"error": f"unknown action type: {body.type}"})


@app.post("/action/reset", response_model=ActionResponse)
async def action_reset():
    try:
        resp = requests.get(f"{_servo_url}/center", timeout=2.0)
        resp.raise_for_status()
        return ActionResponse(ok=True)
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": str(e)})


def main():
    global _servo_url
    parser = argparse.ArgumentParser()
    parser.add_argument("--servo-url", default="http://192.168.0.10")
    parser.add_argument("--port", type=int, default=8301)
    args = parser.parse_args()

    _servo_url = args.servo_url.rstrip("/")
    print(f"Servo URL: {_servo_url}")
    print(f"Port:      {args.port}")

    uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_graceful_shutdown=0)


if __name__ == "__main__":
    main()

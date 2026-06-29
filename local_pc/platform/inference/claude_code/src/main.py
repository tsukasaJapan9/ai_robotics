"""
Claude Code CLI を使った InferenceModule。
claude -p をサブプロセスで呼び出し、サブスクリプション枠内で動作する。

Port: 8202
"""
import argparse
import asyncio
import base64
import json
import logging
import os
import tempfile
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schemas import HealthResponse, InferRequest, InferResponse
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MODULE_NAME = "claude_code"

app = FastAPI()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", module=MODULE_NAME)


@app.post("/infer", response_model=InferResponse)
async def infer(body: InferRequest):
    tmp_path = None
    tmp_dir = None

    try:
        cmd = [
            "claude", "-p", body.prompt,
            "--json-schema", json.dumps(body.json_schema),
            "--output-format", "json",
        ]

        # 画像がある場合は temp ファイルに保存し --add-dir で渡す
        if body.data and body.data.type == "image":
            suffix = "." + body.data.media_type.split("/")[-1]
            tmp_dir = tempfile.mkdtemp()
            tmp_path = os.path.join(tmp_dir, f"image{suffix}")
            with open(tmp_path, "wb") as f:
                f.write(base64.b64decode(body.data.content))
            # プロンプトにファイルパスを付加してClaudeに読み込ませる
            cmd[2] = f"{body.prompt}\n\n画像ファイル: {tmp_path}"
            cmd.extend(["--add-dir", tmp_dir])

        logger.info(f"Calling: {cmd[:4]}...")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        except asyncio.TimeoutError:
            proc.kill()
            logger.error("claude -p timed out")
            return JSONResponse(status_code=504, content={"error": "timeout"})

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        if tmp_dir and os.path.exists(tmp_dir):
            os.rmdir(tmp_dir)

    if proc.returncode != 0:
        err = stderr.decode().strip()
        logger.error(f"claude exit {proc.returncode}: {err}")
        return JSONResponse(status_code=502, content={"error": "claude error", "detail": err})

    raw = stdout.decode().strip()
    logger.debug(f"claude output: {raw}")

    # --output-format json は {"type":"result","result":"..."} 形式
    try:
        outer = json.loads(raw)
        text = outer.get("result", raw)
    except json.JSONDecodeError:
        text = raw

    # コードブロックがあれば除去してパース
    try:
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}\ntext={text}")
        return JSONResponse(status_code=502, content={"error": "invalid JSON from claude"})

    return InferResponse(
        result=result,
        model=MODULE_NAME,
        timestamp=datetime.now().strftime("%H:%M:%S"),
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8202)
    args = parser.parse_args()

    logger.info(f"Port: {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_graceful_shutdown=0)


if __name__ == "__main__":
    main()

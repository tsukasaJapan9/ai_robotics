"""
LM Studio InferenceModule。
LM Studio の OpenAI 互換 API を使い、ローカルモデルで構造化出力を返す。

Port: 8201
"""
import argparse
import json
import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from openai import OpenAI
from schemas import HealthResponse, InferRequest, InferResponse
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MODULE_NAME = "lm_studio"

_client: OpenAI | None = None
_model: str = ""

app = FastAPI()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", module=MODULE_NAME)


@app.post("/infer", response_model=InferResponse)
async def infer(body: InferRequest):
    # メッセージ組み立て: 画像があればビジョン形式
    if body.data and body.data.type == "image":
        content = [
            {"type": "text", "text": body.prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{body.data.media_type};base64,{body.data.content}"
                },
            },
        ]
    else:
        content = body.prompt

    messages = [{"role": "user", "content": content}]

    try:
        resp = _client.chat.completions.create(
            model=_model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "result",
                    "schema": body.schema,
                    "strict": True,
                },
            },
        )
    except Exception as e:
        logger.error(f"LM Studio request failed: {e}")
        return JSONResponse(status_code=503, content={"error": "backend unavailable"})

    raw = resp.choices[0].message.content
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse response JSON: {e}\nraw={raw}")
        return JSONResponse(status_code=502, content={"error": "invalid JSON from model"})

    return InferResponse(
        result=result,
        model=resp.model,
        timestamp=datetime.now().strftime("%H:%M:%S"),
    )


def main():
    global _client, _model
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:1234/v1")
    parser.add_argument("--model", default="gemma4:e4b")
    parser.add_argument("--port", type=int, default=8201)
    args = parser.parse_args()

    _client = OpenAI(base_url=args.base_url, api_key="lm-studio")
    _model = args.model

    logger.info(f"Base URL: {args.base_url}")
    logger.info(f"Model:    {_model}")
    logger.info(f"Port:     {args.port}")

    uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_graceful_shutdown=0)


if __name__ == "__main__":
    main()

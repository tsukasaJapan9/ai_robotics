"""
M5Stack カメラ MJPEG ストリームを取得し、HTTP API として公開する SensorModule。

Port: 8101
"""
import argparse
import asyncio
import logging
import threading
import time
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from schemas import HealthResponse
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

MODULE_NAME = "camera_m5stack"
BOUNDARY = b"--frame"
latest_frame: bytes | None = None


def _read_stream(stream_url: str):
    global latest_frame
    while True:
        try:
            with requests.get(stream_url, stream=True, timeout=(10, None)) as resp:
                resp.raise_for_status()
                buf = b""
                for chunk in resp.iter_content(chunk_size=4096):
                    buf += chunk
                    while True:
                        boundary_pos = buf.find(BOUNDARY)
                        if boundary_pos == -1:
                            break
                        buf = buf[boundary_pos:]
                        header_end = buf.find(b"\r\n\r\n")
                        if header_end == -1:
                            break
                        header = buf[:header_end].decode(errors="ignore")
                        content_length = None
                        for line in header.split("\r\n"):
                            if line.lower().startswith("content-length:"):
                                content_length = int(line.split(":", 1)[1].strip())
                                break
                        if content_length is None:
                            buf = buf[len(BOUNDARY):]
                            break
                        frame_start = header_end + 4
                        if len(buf) < frame_start + content_length:
                            break
                        frame = buf[frame_start:frame_start + content_length]
                        buf = buf[frame_start + content_length:]
                        latest_frame = frame
        except Exception as e:
            logger.warning(f"Stream error: {e}, reconnecting in 2s...")
            time.sleep(2)


app = FastAPI()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", module=MODULE_NAME, media_type="image/jpeg")


@app.get("/stream")
async def stream():
    async def generate():
        while True:
            frame = latest_frame
            if frame:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    frame +
                    b"\r\n"
                )
            await asyncio.sleep(0.033)

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/snapshot")
async def snapshot():
    if latest_frame is None:
        raise HTTPException(status_code=503, detail="No frame available")
    return Response(content=latest_frame, media_type="image/jpeg")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://192.168.0.9:8101/stream")
    parser.add_argument("--port", type=int, default=8101)
    args = parser.parse_args()

    logger.info(f"Stream: {args.url}")
    logger.info(f"Port:   {args.port}")

    threading.Thread(target=_read_stream, args=(args.url,), daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=args.port, timeout_graceful_shutdown=0)


if __name__ == "__main__":
    main()

import base64
import io
import os
import queue
import threading
import time
import requests
from PIL import Image
import servo_control

# 最新の解析結果と解析に使った画像
latest_analysis: str = ""
analyzed_image: bytes | None = None
is_analyzing: bool = False

_NO_IMAGE_HINTS = ["画像が提供", "画像がない", "no image", "no picture", "cannot see"]

_save_frames = False
_debug_dir = "debug_frames"


def _save_frame(frame: bytes, label: str):
    os.makedirs(_debug_dir, exist_ok=True)
    path = os.path.join(_debug_dir, f"{label}_{time.strftime('%H%M%S')}.jpg")
    with open(path, "wb") as f:
        f.write(frame)


def _analyze_loop(frame_queue: "queue.Queue[bytes]", api_url: str, model: str, prompt: str, interval: float, servo_enabled: bool = False):
    global latest_analysis, analyzed_image, is_analyzing
    last_analyzed = 0.0

    while True:
        try:
            frame = frame_queue.get(timeout=30)
        except queue.Empty:
            continue

        now = time.time()
        if now - last_analyzed < interval:
            continue
        last_analyzed = now

        try:
            Image.open(io.BytesIO(frame)).verify()
        except Exception:
            if _save_frames:
                _save_frame(frame, "invalid")
            continue

        image_b64 = base64.b64encode(frame).decode()
        if _save_frames:
            _save_frame(frame, "input")

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}},
                    ],
                }
            ],
            "stream": False,
        }

        try:
            is_analyzing = True
            print(f"[{time.strftime('%H:%M:%S')}] Analyzing...")
            resp = requests.post(f"{api_url}/v1/chat/completions", json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]

            if _save_frames and any(hint in result for hint in _NO_IMAGE_HINTS):
                _save_frame(frame, "no_image_response")

            latest_analysis = result
            analyzed_image = frame
            print(f"[{time.strftime('%H:%M:%S')}] {result}\n")
            if servo_enabled:
                servo_control.apply(result)
        except Exception as e:
            print(f"Analysis error: {e}")
        finally:
            is_analyzing = False


def start(frame_queue: "queue.Queue[bytes]", api_url: str, model: str, prompt: str, interval: float, save_frames: bool = False, servo_enabled: bool = False):
    global _save_frames
    _save_frames = save_frames
    t = threading.Thread(
        target=_analyze_loop,
        args=(frame_queue, api_url, model, prompt, interval, servo_enabled),
        daemon=True,
    )
    t.start()
    return t

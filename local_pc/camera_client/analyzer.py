import base64
import io
import queue
import threading
import time
import requests
from PIL import Image

# 最新の解析結果と解析に使った画像
latest_analysis: str = ""
analyzed_image: bytes | None = None
is_analyzing: bool = False

# LLM が「画像がない」と判断したときに示すキーワード
_NO_IMAGE_HINTS = ["画像が提供", "画像がない", "no image", "no picture", "cannot see"]


def _save_debug_frame(frame: bytes, label: str):
    path = f"debug_{label}_{time.strftime('%H%M%S')}.jpg"
    with open(path, "wb") as f:
        f.write(frame)
    return path


def _analyze_loop(frame_queue: "queue.Queue[bytes]", api_url: str, model: str, prompt: str, interval: float):
    global latest_analysis, analyzed_image
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

        # [1] Pillow でデコードして JPEG の妥当性を確認
        try:
            Image.open(io.BytesIO(frame)).verify()
        except Exception as e:
            path = _save_debug_frame(frame, "invalid")
            print(f"[{time.strftime('%H:%M:%S')}] [1] Invalid frame (size={len(frame)}): {e} → {path}")
            continue

        # [2] 推論に渡すフレームを保存
        image_b64 = base64.b64encode(frame).decode()
        path = _save_debug_frame(frame, "input")
        print(f"[{time.strftime('%H:%M:%S')}] [2] Frame ok (size={len(frame)}, b64={len(image_b64)}) → {path}")

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

        # [3] LM Studio に送信
        try:
            is_analyzing = True
            print(f"[{time.strftime('%H:%M:%S')}] [3] Analyzing...")
            resp = requests.post(f"{api_url}/v1/chat/completions", json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]

            # [4] LLM が画像なしと判断したか検出
            if any(hint in result for hint in _NO_IMAGE_HINTS):
                path = _save_debug_frame(frame, "no_image_response")
                print(f"[{time.strftime('%H:%M:%S')}] [4] LLM reported no image → saved {path}")

            latest_analysis = result
            analyzed_image = frame
            print(f"[{time.strftime('%H:%M:%S')}] {result}\n")
        except Exception as e:
            print(f"Analysis error: {e}")
        finally:
            is_analyzing = False


def start(frame_queue: "queue.Queue[bytes]", api_url: str, model: str, prompt: str, interval: float):
    t = threading.Thread(
        target=_analyze_loop,
        args=(frame_queue, api_url, model, prompt, interval),
        daemon=True,
    )
    t.start()
    return t

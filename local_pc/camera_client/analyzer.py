import base64
import queue
import threading
import time
import requests

# 最新の解析結果と解析に使った画像
latest_analysis: str = ""
analyzed_image: bytes | None = None
is_analyzing: bool = False


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

        image_b64 = base64.b64encode(frame).decode()
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
            resp = requests.post(f"{api_url}/v1/chat/completions", json=payload, timeout=60)
            resp.raise_for_status()
            latest_analysis = resp.json()["choices"][0]["message"]["content"]
            analyzed_image = frame
            print(f"[{time.strftime('%H:%M:%S')}] {latest_analysis}\n")
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

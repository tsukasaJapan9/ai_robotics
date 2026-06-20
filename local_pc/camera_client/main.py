import argparse
import base64
import queue
import threading
import time
import requests


def stream_frames(stream_url: str, frame_queue: "queue.Queue[bytes]"):
    """MJPEG ストリームを常時読み続け、最新フレームをキューに入れるスレッド"""
    # 接続タイムアウト 10 秒、read タイムアウトなし（ストリーム接続のため）
    with requests.get(stream_url, stream=True, timeout=(10, None)) as resp:
        resp.raise_for_status()
        buf = b""
        for chunk in resp.iter_content(chunk_size=4096):
            buf += chunk
            while True:
                # JPEG の開始・終了マーカーでフレームを切り出す
                start = buf.find(b"\xff\xd8")  # SOI
                end = buf.find(b"\xff\xd9")    # EOI
                if start == -1 or end == -1 or end < start:
                    break
                frame = buf[start:end + 2]
                buf = buf[end + 2:]
                # 古いフレームは捨て、常に最新フレームだけ保持する
                while not frame_queue.empty():
                    frame_queue.get_nowait()
                frame_queue.put(frame)


def analyze_frame(frame_bytes: bytes, api_url: str, model: str, prompt: str) -> str:
    image_b64 = base64.b64encode(frame_bytes).decode()
    # LM Studio は OpenAI 互換 API
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
    resp = requests.post(f"{api_url}/v1/chat/completions", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="M5Stack カメラ映像を LM Studio で解析する")
    parser.add_argument("--stream-url", default="http://192.168.0.9/stream")
    parser.add_argument("--api-url",    default="http://localhost:1234")
    parser.add_argument("--model",      default="gemma4:e4b")
    parser.add_argument("--prompt",     default="この画像に何が映っているか説明してください。")
    parser.add_argument("--interval",   type=float, default=0.0, help="分析間隔（秒）")
    args = parser.parse_args()

    print(f"Stream: {args.stream_url}")
    print(f"Model:  {args.model}")
    print(f"Interval: {args.interval}s\n")

    frame_queue: queue.Queue[bytes] = queue.Queue()
    t = threading.Thread(target=stream_frames, args=(args.stream_url, frame_queue), daemon=True)
    t.start()

    last_analyzed = 0.0
    while True:
        try:
            frame = frame_queue.get(timeout=30)
        except queue.Empty:
            print("Stream timeout")
            break

        now = time.time()
        if now - last_analyzed < args.interval:
            continue
        last_analyzed = now

        print(f"[{time.strftime('%H:%M:%S')}] Analyzing...")
        result = analyze_frame(frame, args.api_url, args.model, args.prompt)
        print(f">>> {result}\n")


if __name__ == "__main__":
    main()

import argparse
import base64
import time
import requests


def iter_mjpeg_frames(stream_url: str):
    """MJPEG ストリームから JPEG フレームを順に yield する"""
    with requests.get(stream_url, stream=True, timeout=10) as resp:
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
                yield buf[start:end + 2]
                buf = buf[end + 2:]


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
    parser.add_argument("--prompt",     default="Describe what you see in this image.")
    parser.add_argument("--interval",   type=float, default=3.0, help="分析間隔（秒）")
    args = parser.parse_args()

    print(f"Stream: {args.stream_url}")
    print(f"Model:  {args.model}")
    print(f"Interval: {args.interval}s\n")

    last_analyzed = 0.0
    for frame in iter_mjpeg_frames(args.stream_url):
        now = time.time()
        if now - last_analyzed < args.interval:
            continue
        last_analyzed = now

        print(f"[{time.strftime('%H:%M:%S')}] Analyzing...")
        result = analyze_frame(frame, args.api_url, args.model, args.prompt)
        print(f">>> {result}\n")


if __name__ == "__main__":
    main()

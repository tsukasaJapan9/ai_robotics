import argparse
import queue
import stream
import analyzer
import uvicorn
from api import app


def main():
    parser = argparse.ArgumentParser(description="M5Stack カメラ映像を LM Studio で解析する")
    parser.add_argument("--stream-url", default="http://192.168.0.9/stream")
    parser.add_argument("--api-url",    default="http://localhost:1234")
    parser.add_argument("--model",      default="gemma4:e4b")
    parser.add_argument("--prompt",     default="この画像に何が映っているか説明してください。")
    parser.add_argument("--interval",   type=float, default=0.0, help="分析間隔（秒）")
    parser.add_argument("--port",       type=int,   default=8000, help="API サーバポート")
    args = parser.parse_args()

    print(f"Stream:   {args.stream_url}")
    print(f"Model:    {args.model}")
    print(f"Interval: {args.interval}s")
    print(f"API:      http://localhost:{args.port}\n")

    frame_queue: queue.Queue[bytes] = queue.Queue()
    stream.start(args.stream_url, frame_queue)
    analyzer.start(frame_queue, args.api_url, args.model, args.prompt, args.interval)

    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

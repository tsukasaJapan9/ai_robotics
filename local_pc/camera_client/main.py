import argparse
import queue

import analyzer
import servo_client
import stream
import uvicorn
from api import app

SYSTEM_PROMPT = """
あなたは好奇心旺盛なロボットであり、人間の世界を探索しています。
これまでの推論履歴が会話の流れとして与えられています。同じ場所ばかりを見続けず、まだ見ていない方向や新しいものに積極的に目を向けてください。

画像の中で最も目を引くものに注目し、以下のJSON形式のみで答えてください。それ以外のテキストは出力しないでください。

{"x": <角度>, "y": <角度>, "reason": "<注目した対象とその理由>"}

X軸（水平）: 0〜360（160が正面中央、小さいほど右、大きいほど左）
Y軸（垂直）: 50〜85（60が正面中央、小さいほど上、大きいほど下）

出力例:
- 右上に猫がいる場合: {"x": 130, "y": 52, "reason": "右上に猫がいて動きが気になるため"}
- 左側に人物がいる場合: {"x": 195, "y": 60, "reason": "左側に人物がいて表情が気になるため"}
- 中央に本がある場合: {"x": 160, "y": 65, "reason": "中央に本があり、タイトルが読めそうなため"}
"""


def main():
    parser = argparse.ArgumentParser(
        description="M5Stack カメラ映像を LM Studio で解析する"
    )
    parser.add_argument("--stream-url", default="http://192.168.0.9/stream")
    parser.add_argument("--api-url", default="http://localhost:1234")
    parser.add_argument("--model", default="gemma4:e4b")
    parser.add_argument("--prompt", default=SYSTEM_PROMPT)
    parser.add_argument("--interval", type=float, default=0.0, help="分析間隔（秒）")
    parser.add_argument("--port", type=int, default=8000, help="API サーバポート")
    parser.add_argument(
        "--save-frames",
        action="store_true",
        help="推論フレームを debug_frames/ に保存する",
    )
    parser.add_argument(
        "--servo-url",
        default="",
        help="wonder_eye サーボ API の URL（例: http://192.168.0.10）",
    )
    args = parser.parse_args()

    print(f"Stream:   {args.stream_url}")
    print(f"Model:    {args.model}")
    print(f"Interval: {args.interval}s")
    if args.servo_url:
        print(f"Servo:    {args.servo_url}")
    print(f"API:      http://localhost:{args.port}\n")

    if args.servo_url:
        servo_client.setup(args.servo_url)
        servo_client.center()

    frame_queue: queue.Queue[bytes] = queue.Queue()
    stream.start(args.stream_url, frame_queue)
    analyzer.start(
        frame_queue,
        args.api_url,
        args.model,
        args.prompt,
        args.interval,
        args.save_frames,
        servo_enabled=bool(args.servo_url),
    )

    config = uvicorn.Config(
        app, host="0.0.0.0", port=args.port, timeout_graceful_shutdown=0
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    main()

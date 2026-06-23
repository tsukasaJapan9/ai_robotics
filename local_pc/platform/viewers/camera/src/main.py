"""
CameraSensorModule の /stream を表示するブラウザビューア。

Port: 8080
"""
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
_stream_url = ""


@app.get("/", response_class=HTMLResponse)
async def index():
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Camera Viewer</title>
  <style>
    body {{ margin: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }}
    img {{ max-width: 100%; max-height: 100vh; }}
  </style>
</head>
<body>
  <img src="{_stream_url}" />
</body>
</html>"""


def main():
    global _stream_url

    parser = argparse.ArgumentParser()
    parser.add_argument("--stream-url", default="http://localhost:8101/stream")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    _stream_url = args.stream_url
    print(f"Stream: {_stream_url}")
    print(f"Port:   {args.port}")
    print(f"Open:   http://localhost:{args.port}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

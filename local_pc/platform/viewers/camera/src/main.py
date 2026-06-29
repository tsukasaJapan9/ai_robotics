"""
Wonder Pilot のステータス（推論画像・結果・履歴）を表示するブラウザビューア。

Port: 8080
"""
import argparse
import logging
import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
_pilot_url = ""


@app.get("/api/status")
async def api_status():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{_pilot_url}/status", timeout=5.0)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": str(e)})


@app.get("/", response_class=HTMLResponse)
async def index():
    return """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Wonder Pilot Viewer</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #111; color: #eee; font-family: monospace; display: flex; flex-direction: column; height: 100vh; }
    #main { display: flex; flex: 1; overflow: hidden; }
    #left { display: flex; flex-direction: column; flex: 1; overflow: hidden; }
    #image-wrap { flex: 1; display: flex; align-items: center; justify-content: center; background: #000; overflow: hidden; }
    #image-wrap img { max-width: 100%; max-height: 100%; display: block; }
    #info { padding: 10px 14px; background: #1a1a1a; border-top: 1px solid #333; }
    #info .coords { font-size: 18px; font-weight: bold; color: #4cf; }
    #info .reason { margin-top: 4px; color: #ddd; font-size: 13px; }
    #history { width: 260px; overflow-y: auto; background: #1a1a1a; padding: 8px; }
    #history h2 { font-size: 12px; color: #888; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
    .hist-item { background: #222; border-radius: 4px; padding: 8px; margin-bottom: 6px; }
    .hist-item img { width: 100%; border-radius: 2px; margin-bottom: 4px; }
    .hist-item .meta { font-size: 11px; color: #aaa; }
    .hist-item .meta .coords { color: #4cf; font-weight: bold; }
    .hist-item .reason { font-size: 11px; color: #ccc; margin-top: 2px; word-break: break-all; }
    #status-bar { padding: 4px 12px; font-size: 11px; color: #555; background: #0a0a0a; }
  </style>
</head>
<body>
  <div id="main">
    <div id="left">
      <div id="image-wrap">
        <img id="latest-img" src="" alt="No image" />
      </div>
      <div id="info">
        <div class="coords" id="coords">--</div>
        <div class="reason" id="reason">--</div>
      </div>
    </div>
    <div id="history">
      <h2>History</h2>
      <div id="hist-list"></div>
    </div>
  </div>
  <div id="status-bar" id="status-bar">Connecting...</div>
  <script>
    async function poll() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const bar = document.getElementById('status-bar');

        if (data.error) {
          bar.textContent = 'Error: ' + data.error;
          return;
        }

        const latest = data.latest;
        if (latest) {
          if (latest.image) {
            document.getElementById('latest-img').src = 'data:image/jpeg;base64,' + latest.image;
          }
          document.getElementById('coords').textContent = `x=${latest.x}  y=${latest.y}`;
          document.getElementById('reason').textContent = latest.reason || '';
          bar.textContent = latest.time || '';
        }

        const hist = (data.history || []).slice().reverse();
        const list = document.getElementById('hist-list');
        list.innerHTML = '';
        for (const e of hist) {
          const div = document.createElement('div');
          div.className = 'hist-item';
          div.innerHTML = (e.image ? `<img src="data:image/jpeg;base64,${e.image}" />` : '') +
            `<div class="meta"><span class="coords">x=${e.x} y=${e.y}</span>  ${e.time}</div>` +
            `<div class="reason">${e.reason || ''}</div>`;
          list.appendChild(div);
        }
      } catch (e) {
        document.getElementById('status-bar').textContent = 'Fetch error: ' + e;
      }
    }

    poll();
    setInterval(poll, 1000);
  </script>
</body>
</html>"""


def main():
    global _pilot_url

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    _pilot_url = args.url.rstrip("/")
    logger.info(f"Pilot: {_pilot_url}")
    logger.info(f"Port:  {args.port}")
    logger.info(f"Open:  http://localhost:{args.port}")

    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()

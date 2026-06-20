import queue
import threading
import requests

# 最新フレームを保持する共有変数（読み書きは GIL で保護される）
latest_frame: bytes | None = None


def _read_stream(stream_url: str, frame_queue: "queue.Queue[bytes]"):
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

                global latest_frame
                latest_frame = frame


def start(stream_url: str, frame_queue: "queue.Queue[bytes]"):
    t = threading.Thread(target=_read_stream, args=(stream_url, frame_queue), daemon=True)
    t.start()
    return t

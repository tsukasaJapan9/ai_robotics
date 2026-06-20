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
                # Content-Length ヘッダでフレームサイズを取得して正確に切り出す
                # SOI/EOI マーカーは JPEG データ内に偽陽性が出るため信頼性が低い
                header_end = buf.find(b"\r\n\r\n")
                if header_end == -1:
                    break
                header = buf[:header_end].decode(errors="ignore")
                content_length = None
                for line in header.split("\r\n"):
                    if line.lower().startswith("content-length:"):
                        content_length = int(line.split(":", 1)[1].strip())
                        break
                if content_length is None:
                    # Content-Length がない場合は SOI/EOI フォールバック
                    start = buf.find(b"\xff\xd8")
                    end = buf.find(b"\xff\xd9")
                    if start == -1 or end == -1 or end < start:
                        break
                    frame = buf[start:end + 2]
                    buf = buf[end + 2:]
                else:
                    frame_start = header_end + 4
                    if len(buf) < frame_start + content_length:
                        break  # フレームがまだ揃っていない
                    frame = buf[frame_start:frame_start + content_length]
                    buf = buf[frame_start + content_length:]

                # 古いフレームは捨て、常に最新フレームだけ保持する
                # empty() + get_nowait() は非アトミックなので try/except で処理する
                while True:
                    try:
                        frame_queue.get_nowait()
                    except queue.Empty:
                        break
                frame_queue.put(frame)

                global latest_frame
                latest_frame = frame


def start(stream_url: str, frame_queue: "queue.Queue[bytes]"):
    t = threading.Thread(target=_read_stream, args=(stream_url, frame_queue), daemon=True)
    t.start()
    return t

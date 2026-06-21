import requests

_servo_url = ""


def setup(servo_url: str):
    global _servo_url
    _servo_url = servo_url.rstrip("/")


def move(x: int | None = None, y: int | None = None, timeout: float = 2.0) -> bool:
    """サーボを指定角度に移動。失敗しても例外を上げない。"""
    if not _servo_url:
        return False
    params: dict[str, int] = {}
    if x is not None:
        params["x"] = x
    if y is not None:
        params["y"] = y
    if not params:
        return False
    try:
        resp = requests.get(f"{_servo_url}/servo", params=params, timeout=timeout)
        return resp.ok
    except Exception:
        return False


def center(timeout: float = 2.0) -> bool:
    if not _servo_url:
        return False
    try:
        resp = requests.get(f"{_servo_url}/center", timeout=timeout)
        return resp.ok
    except Exception:
        return False

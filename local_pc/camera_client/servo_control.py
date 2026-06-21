import servo_client

# キーワード → (X角度, Y角度) のマッピング
# 複合語を先に評価することで部分一致の誤検知を防ぐ
_KEYWORD_MAP: list[tuple[str, int, int]] = [
    ("upper-left",  200, 25),
    ("upper-right", 120, 25),
    ("lower-left",  200, 65),
    ("lower-right", 120, 65),
    ("center",      160, 45),
    ("left",        200, 45),
    ("right",       120, 45),
    ("up",          160, 25),
    ("down",        160, 65),
]


def apply(analysis_text: str) -> bool:
    """AI解析テキストからキーワードを抽出してサーボを動かす。
    有効なキーワードがなければ False（サーボは前回位置を維持）。
    """
    text = analysis_text.lower()
    for keyword, x, y in _KEYWORD_MAP:
        if keyword in text:
            return servo_client.move(x=x, y=y)
    return False

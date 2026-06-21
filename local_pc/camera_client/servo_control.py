import servo_client

# キーワード → (X角度, Y角度) のマッピング
# X: 小→右回転、大→左回転（制限なし、中央160）
# Y: 小→上、大→下（範囲50〜85、中央67）
# 複合語を先に評価することで部分一致の誤検知を防ぐ
_KEYWORD_MAP: list[tuple[str, int, int]] = [
    ("upper-left",  200, 50),
    ("upper-right", 120, 50),
    ("lower-left",  200, 85),
    ("lower-right", 120, 85),
    ("center",      160, 60),
    ("left",        200, 60),
    ("right",       120, 60),
    ("up",          160, 50),
    ("down",        160, 85),
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

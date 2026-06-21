import re
import servo_client

# X: 小→右回転、大→左回転（範囲0〜360、中央160）
# Y: 小→上、大→下（範囲50〜85、中央60）
X_MIN, X_MAX = 0, 360
Y_MIN, Y_MAX = 50, 85


def apply(analysis_text: str) -> bool:
    """AI応答から {"x": N, "y": N} を抽出してサーボを動かす。
    パースできなければ False（サーボは前回位置を維持）。
    """
    x_match = re.search(r'"x"\s*:\s*(\d+)', analysis_text)
    y_match = re.search(r'"y"\s*:\s*(\d+)', analysis_text)
    if not x_match or not y_match:
        return False
    x = max(X_MIN, min(X_MAX, int(x_match.group(1))))
    y = max(Y_MIN, min(Y_MAX, int(y_match.group(1))))
    return servo_client.move(x=x, y=y)

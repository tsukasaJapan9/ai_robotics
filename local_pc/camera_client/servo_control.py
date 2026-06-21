import json
import re
import servo_client

# X: 小→右回転、大→左回転（範囲0〜360、中央160）
# Y: 小→上、大→下（範囲50〜85、中央60）
X_MIN, X_MAX = 0, 360
Y_MIN, Y_MAX = 50, 85


def apply(analysis_text: str) -> bool:
    """AI応答から {"x": N, "y": N, "reason": "..."} をパースしてサーボを動かす。
    パースできなければ False（サーボは前回位置を維持）。
    """
    # レスポンス中の JSON（配列またはオブジェクト）を抽出
    match = re.search(r'(\[.*\]|\{.*\})', analysis_text, re.DOTALL)
    if not match:
        return False
    try:
        parsed = json.loads(match.group())
    except json.JSONDecodeError:
        return False

    # リストで返ってきた場合は最後の要素を使う
    data = parsed[-1] if isinstance(parsed, list) else parsed

    if "x" not in data or "y" not in data:
        return False

    x = max(X_MIN, min(X_MAX, int(data["x"])))
    y = max(Y_MIN, min(Y_MAX, int(data["y"])))
    if reason := data.get("reason"):
        print(f"reason: {reason}")
    return servo_client.move(x=x, y=y)

#!/bin/bash
# コミット前に秘匿情報が含まれないかチェック
#
# 誤検知対策:
# - コメント行（// # * <!--）は除外
# - 開始・終了クォートで囲まれた値のみ検出

PATTERNS=(
    'password\s*[:=]\s*["'"'"'][^"'"'"']{4,}["'"'"']'
    'passwd\s*[:=]\s*["'"'"'][^"'"'"']{4,}["'"'"']'
    'api[_-]?key\s*[:=]\s*["'"'"'][^"'"'"']{4,}["'"'"']'
    'secret\s*[:=]\s*["'"'"'][^"'"'"']{4,}["'"'"']'
    'auth[_-]?token\s*[:=]\s*["'"'"'][^"'"'"']{4,}["'"'"']'
    'AKIA[0-9A-Z]{16}'
    '-----BEGIN.+PRIVATE KEY-----'
)

# このスクリプト自身はチェック対象から除外
EXCLUDE_FILES=(".claude/scripts/pre-commit-check.sh")

# ダミー値として許可するパターン（誤検知除外）
DUMMY_PATTERNS=(
    'api[_-]?key\s*[:=]\s*["'"'"']dummy["'"'"']'
)

found=0

while IFS= read -r file; do
    # 除外ファイルはスキップ
    skip=false
    for excl in "${EXCLUDE_FILES[@]}"; do
        [[ "$file" == "$excl" ]] && skip=true && break
    done
    $skip && continue

    # バイナリファイルはスキップ
    if git show ":$file" | grep -qP '\x00' 2>/dev/null; then
        continue
    fi

    for pat in "${PATTERNS[@]}"; do
        # コメント行（// # * <!--）は除外
        result=$(git show ":$file" | grep -iP -e "$pat" | grep -vP '^\s*(//|#|\*|<!--)' 2>/dev/null || true)
        for dummy_pat in "${DUMMY_PATTERNS[@]}"; do
            result=$(echo "$result" | grep -viP "$dummy_pat" || true)
        done
        if [ -n "$result" ]; then
            echo "[secrets] $file:"
            echo "$result" | head -3
            echo ""
            found=1
        fi
    done
done < <(git diff --cached --name-only --diff-filter=ACM)

if [ "$found" -ne 0 ]; then
    echo "秘匿情報が検出されました。コミットをブロックします。"
    echo "誤検知の場合は --no-verify で回避してください。"
    exit 1
fi

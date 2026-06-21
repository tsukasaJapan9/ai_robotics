#!/bin/bash
# コミット前に秘匿情報が含まれないかチェック

PATTERNS=(
    'password\s*[:=]\s*["'"'"'][^"'"'"']{4,}'
    'passwd\s*[:=]\s*["'"'"'][^"'"'"']{4,}'
    'api[_-]?key\s*[:=]\s*["'"'"'][^"'"'"']{4,}'
    'secret\s*[:=]\s*["'"'"'][^"'"'"']{4,}'
    'auth[_-]?token\s*[:=]\s*["'"'"'][^"'"'"']{4,}'
    'AKIA[0-9A-Z]{16}'
    '-----BEGIN.+PRIVATE KEY-----'
)

found=0

while IFS= read -r file; do
    # バイナリファイルはスキップ
    if git show ":$file" | grep -qP '\x00' 2>/dev/null; then
        continue
    fi
    for pat in "${PATTERNS[@]}"; do
        result=$(git show ":$file" | grep -inP "$pat" 2>/dev/null || true)
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

#!/usr/bin/env bash
# Stop hook cho Claude Code: không cho agent kết thúc lượt khi scripts/check còn lỗi.
# Chỉ chạy khi có thay đổi chưa commit. Thoát 2 = chặn và đưa lỗi cho Claude sửa.
set -u
input="$(cat)"

# Đã bị hook chặn một lần trong lượt này: cho dừng, tránh vòng lặp vô hạn.
if printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || exit 0

# Không có thay đổi thì không cần kiểm tra.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  [ -z "$(git status --porcelain)" ] && exit 0
fi

[ -f scripts/check ] || exit 0

if out="$(bash scripts/check 2>&1)"; then
  exit 0
fi

{
  echo "scripts/check đang lỗi. Sửa trước khi báo xong:"
  printf '%s\n' "$out" | tail -n 80
} >&2
exit 2

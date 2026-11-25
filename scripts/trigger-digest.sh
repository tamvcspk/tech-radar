#!/usr/bin/env bash
# Kích hoạt workflow "Daily digest" qua workflow_dispatch. Chạy từ homeserver (cron ~06:30 ICT).
# Cần biến môi trường GH_DISPATCH_TOKEN: PAT fine-grained, chỉ quyền Actions: write trên repo này.
# Không ghi token vào repo. Gửi thật (dry_run=false); muốn thử thì đặt DRY_RUN=true.
# Dùng: GH_DISPATCH_TOKEN=... bash scripts/trigger-digest.sh
set -euo pipefail

REPO="${GH_REPO:-tamvcspk/tech-radar}"
REF="${GH_REF:-main}"
DRY_RUN="${DRY_RUN:-false}"

if [ -z "${GH_DISPATCH_TOKEN:-}" ]; then
  echo "Thiếu GH_DISPATCH_TOKEN" >&2
  exit 2
fi

code=$(curl -sS -o /dev/null -w '%{http_code}' -X POST \
  -H "Authorization: Bearer ${GH_DISPATCH_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/repos/${REPO}/actions/workflows/daily-digest.yml/dispatches" \
  -d "{\"ref\":\"${REF}\",\"inputs\":{\"dry_run\":\"${DRY_RUN}\"}}")

if [ "$code" != "204" ]; then
  echo "Trigger thất bại: HTTP ${code}" >&2
  exit 1
fi
echo "Đã trigger daily-digest (ref=${REF}, dry_run=${DRY_RUN})"

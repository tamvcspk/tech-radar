# Handoff

Ghi đè toàn bộ file mỗi lần chuyển tool. Tối đa 30 dòng.

- Thời điểm: 2026-11-26
- Từ: Claude Code → Sang: (chưa chuyển)
- Nhánh / worktree: main
- Commit cuối: 8632156 (các thay đổi bên dưới chưa commit)
- `scripts/check`: OK (exit 0) lúc 2026-11-26 (test ok, docs ok; 61 test)

## Mục tiêu đang làm

PLAN.md mục 8.2, P0: bản tin hằng ngày đến đúng giờ. Checklist ở docs/SPEC.md.

## Đã xong

- Khung site, worker, workflow hằng ngày; áp project-kit (Mode 1).
- `assets/last_sent_date` (job `telegram` ghi sau khi gửi thật; `run` và `send` bỏ qua nếu ngày đã gửi) và `since` = `last_success_at`, trần 72h (D-10).
- D-11: bỏ homeserver/PAT. Cron chạy sớm 02:17 ICT (`17 19 * * *` UTC) + dự phòng 04:47 ICT (`47 21 * * *` UTC).

## Đang dở

- Chưa commit: workflow, worker/*, tests/*, docs/*, scripts/trigger-digest.sh.
- Chưa chạy thật trên Actions: bước commit `last_sent_date` trong job `telegram` chưa có run nào.

## Việc tiếp theo (theo thứ tự)

1. Commit và push; chạy tay `workflow_dispatch` với dry_run=false một lần để xác nhận `assets/last_sent_date` được commit.
2. Quyết định có gửi Telegram im lặng (`disable_notification`) để 02:17 không rung máy; chưa làm.
3. Theo dõi 7 ngày, ghi kết quả vào mục "Ghi chú" của docs/SPEC.md. Nếu có ngày cả hai lần cron bị rớt thì mở lại phương án homeserver (D-11).

## Lưu ý cho người nhận

- Repo public; không đưa `.env` hay secret vào commit.
- Gửi thật trong ngày sẽ chặn mọi lần chạy khác cùng ngày ICT (cố ý). Dry-run không ghi `last_sent_date`.
- `scripts/trigger-digest.sh` không còn dùng; xóa được nếu muốn gọn.

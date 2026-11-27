# Handoff

Ghi đè toàn bộ file mỗi lần chuyển tool. Tối đa 30 dòng.

- Thời điểm: 2026-11-27 (khoảng 11:15 ICT)
- Từ: Claude Code → Sang: (chưa chuyển)
- Nhánh / worktree: main
- Commit cuối: xem `git log -1` (commit "P0: cron mỗi giờ 02:17–07:17 ICT (D-13)" cùng bản handoff này)
- `scripts/check`: OK (exit 0) lúc 2026-11-27 (test ok, docs ok)

## Mục tiêu đang làm

PLAN.md mục 8.2, P0: bản tin hằng ngày đến đúng giờ (trước 08:00 ICT). Checklist ở docs/SPEC.md.

## Đã xong

- `last_sent_date` và `since` (D-10); không gửi im lặng (D-12). Commit 172d53e.
- Chặn gửi trùng đã kiểm chứng trên Actions (2026-11-27: lần dự phòng chạy, deploy/telegram skipped).
- D-13: lịch cron `17 19-23,0 * * *` (02:17–07:17 ICT, 6 lần). Vẫn serverless; sáng không có tin thì chạy tay workflow trên GitHub (bỏ chọn dry_run).

## Đang dở / vấn đề

- Cron GitHub trễ 6–7h: 2026-11-27 bản tin gửi 09:18 ICT; 11-26 cũng không có cron nào trước 09:00 ICT. Lịch mới (D-13) chỉ có hiệu lực sau khi push; chưa biết có cải thiện không.

## Việc tiếp theo (theo thứ tự)

1. Mỗi sáng `gh run list --workflow daily-digest.yml`: lần nào gửi, lúc mấy giờ; ghi vào "Ghi chú" của docs/SPEC.md. Đủ 7 ngày liên tiếp trước 08:00 thì đóng P0.
2. Sau 3–4 ngày vẫn trễ: báo người dùng; phương án cuối là dịch vụ ngoài gọi `workflow_dispatch` (cần PAT).
3. Sau P0 thì P1 (nguồn mới). Ý tưởng "radar tuỳ chọn" (nhiều chủ đề, cấu hình bằng Issue/PR) đã ghi ở mục "Ý tưởng để sau" của docs/SPEC.md cùng ghi chú thiết kế; CHƯA làm vì ngoài P0 và đụng Non-goals. Khi mở milestone: cập nhật docs/BRIEF.md và thêm entry D-xx.

## Lưu ý cho người nhận

- Repo public; không đưa `.env` hay secret vào commit. Workflow nhận cấu hình từ issue/PR phải giới hạn chủ repo.
- Gửi thật trong ngày sẽ chặn mọi lần chạy khác cùng ngày ICT (cố ý). Dry-run không ghi `last_sent_date`.
- Bot commit `digest:`/`sent:` lên main: luôn `git pull --rebase` trước khi push.

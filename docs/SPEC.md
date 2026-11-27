# Spec: tech-radar

## Milestone hiện tại: P0 — kích hoạt đáng tin

Nguồn: PLAN.md ở gốc repo, mục 8.2, hàng P0.

Mục tiêu: bản tin hằng ngày không còn phụ thuộc vào cron GitHub (lỗi ghi nhận ở PLAN mục 8.1: 06:30 đến 12:41).

Xong khi: 7 ngày liên tiếp có bản tin trước 08:00 ICT và không gửi trùng trong một ngày. (Đã đổi theo D-11: không dùng homeserver; chạy sớm bằng cron GitHub để có đệm cho độ trễ.)

### Checklist

- [x] ~~PAT + trigger `workflow_dispatch` từ homeserver~~: bỏ, thay bằng chạy sớm (D-11). `scripts/trigger-digest.sh` giữ lại như đường dự phòng thủ công, không dùng.
- [x] Dời `schedule` sang 02:17 ICT (`17 19 * * *` UTC) và thêm lần dự phòng 04:47 ICT (`47 21 * * *` UTC).
- [x] Thêm `assets/last_sent_date` để chặn gửi trùng trong một ngày.
- [x] Đổi `LOOKBACK` 24h cố định thành `since` = lần chạy thành công gần nhất, trần 72h.
- [x] Đổi lịch sang mỗi giờ 02:17–07:17 ICT (`17 19-23,0 * * *`), không sáng thì chạy tay `workflow_dispatch` (D-13).
- [ ] Ghi kết quả 7 ngày đầu vào mục "Ghi chú" bên dưới.

## Contract

Không có contract máy đọc được (Mode 1). Các bước nội bộ dùng Pydantic models trong `worker/models.py`.

## Cấu trúc thư mục

```
tech-radar/
├── AGENTS.md / CLAUDE.md    # luật agent
├── PLAN.md                  # ý tưởng, kiến trúc, roadmap (nguồn gốc)
├── mkdocs.yml
├── assets/                  # state dedup (processed_urls.json + .json.gz xoay vòng)
├── docs/                    # Markdown build thành site + BRIEF/SPEC/DECISIONS/HANDOFF
│   └── digests/YYYY-MM-DD/
├── worker/                  # ingest → lọc → enrich → xuất bản
├── tests/
├── scripts/                 # check, stop-check.sh
└── .github/workflows/       # daily-digest.yml, pages.yml
```

## Milestone tiếp theo

- P1: nguồn mới (Lobste.rs, Show HN ≥ 100, HF Daily Papers, Simon Willison, 2–3 blog kỹ thuật có RSS); giới hạn 15 mục mỗi nguồn; chủ đề thành enum cố định. Chi tiết: PLAN mục 8.2.

## Ý tưởng để sau

- Các hàng P2–P5 trong PLAN mục 8.2 (lọc tầng 1, điều hướng năm/tháng, Telegram theo mục và poller reaction, backfill 2026).
- Xem thêm PLAN mục 5.
- **Radar tuỳ chọn (đề xuất 2026-11-27)**: nâng tech-radar thành nền tảng nhiều radar theo chủ đề (security, economy, ...), mỗi radar có nguồn, tiêu chí lọc, lịch chạy và kênh Telegram riêng; cấu hình bằng Issue form hoặc PR. Chưa làm: ngoài P0, và đụng Non-goals ("tag và trang index theo chủ đề", BRIEF) nên phải cập nhật BRIEF và thêm entry D-xx khi mở milestone. Ghi chú thiết kế sơ bộ, chưa quyết:
  - Cấu hình mỗi radar là một file `radars/<tên>.yml` (nguồn, chủ đề, ngưỡng điểm, lịch, chat Telegram). Tin công nghệ hiện tại trở thành radar mặc định. PR vào file này là đường cấu hình chính (có review, có lịch sử); Issue form chỉ là giao diện nhập, workflow đọc issue rồi mở PR.
  - Lịch: cron GitHub là tĩnh, nên giữ một cron mỗi giờ (D-13) rồi để worker đọc `radars/*.yml` và chỉ chạy radar đến hạn. `last_sent_date` cần tách theo radar.
  - Bảo mật (repo public): workflow chỉ nhận issue/PR từ chủ repo (`author_association == OWNER`), không chạy code từ PR của người ngoài, không đưa secret vào ngữ cảnh PR từ fork. Token và chat ID mỗi radar để trong GitHub Secrets, file yml chỉ ghi tên secret.
  - Rủi ro cần đo trước: quota Gemini theo số radar, nguồn mới mỗi chủ đề (P1 chưa xong), site MkDocs cần cấu trúc theo radar (đụng P3).
  - Thứ tự gợi ý: xong P0 và P1, sau đó tách `radars/*.yml` với đúng một radar, rồi mới thêm Issue form.

## Ghi chú

- 2026-11-26: sau khi push lịch mới (lúc 18:20 UTC 11-25), cả hai lần cron (19:17 và 21:47 UTC) không chạy, kiểm tra lúc 01:11 UTC. Run gần nhất trước đó cũng là cron trễ khoảng 6 giờ (11-25 05:37 UTC). Chạy tay `workflow_dispatch` dry_run=false thành công (run 45734116997): có commit `digest: 2026-11-26` và `sent: 2026-11-26`, `assets/last_sent_date` = `2026-11-26`. Chưa biết việc không chạy là do vừa đổi lịch hay cron GitHub vốn rớt; cần thêm dữ liệu các ngày sau.
- 2026-11-27: cả hai lần cron chạy nhưng trễ rất nhiều: lần 02:17 ICT khởi động lúc 02:16 UTC (09:16 ICT, trễ ~7h), lần 04:47 ICT khởi động 03:49 UTC (10:49 ICT, trễ ~6h). Bản tin gửi 09:18 ICT, không đạt mục tiêu trước 08:00. Lần dự phòng tự bỏ qua đúng (job deploy/telegram skipped nhờ `last_sent_date`), nên chặn gửi trùng đã được kiểm chứng trên Actions. Kết luận tạm: chạy sớm không đủ vì cron GitHub trễ 6–7h kể cả khi đặt 02:17 ICT; cần cân nhắc lại phương án trigger ngoài (D-11).

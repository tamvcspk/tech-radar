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

## Ghi chú

- (chưa có)

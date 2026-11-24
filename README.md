# Tech Radar

Hệ thống tự động tổng hợp tin công nghệ mỗi sáng, chạy $0/tháng trên GitHub Actions.

- **Telegram** (lớp 1): 1 tin tổng hợp 5–7 mục, đọc trong ~1 phút.
- **GitHub Pages** (lớp 2): bài phân tích sâu cho từng mục, tự động lưu thành kho tra cứu có tìm kiếm.

Chi tiết ý tưởng, kiến trúc và kế hoạch: xem [PLAN.md](PLAN.md).

## Trạng thái

Bước 1 (khung site), Bước 2 (worker) và Bước 3 (workflow hằng ngày `daily-digest.yml`) đã xong.

Xem site cục bộ:

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m mkdocs serve
```

## Cấu trúc dự kiến

```
tech-radar/
├── README.md
├── PLAN.md                  # ý tưởng, kiến trúc, quyết định, roadmap
├── mkdocs.yml               # (Bước 1)
├── docs/                    # Markdown được SSG build thành site
│   ├── index.md
│   └── digests/YYYY-MM-DD/
├── worker/                  # Python: ingest → lọc → enrich → xuất bản
├── tests/
└── .github/workflows/
    ├── daily-digest.yml     # cron + workflow_dispatch
    └── pages.yml            # (có thể gộp vào daily-digest)
```

## Worker (chạy local)

```
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest                # test không gọi API thật
.venv/Scripts/python -m worker run            # lấy tin, chấm điểm, sinh docs/digests/ và out/telegram.json
.venv/Scripts/python -m worker send --dry-run # in tin Telegram ra console
```

Đổi nguồn theo dõi trong [worker/sources.py](worker/sources.py). Mặc định `DRY_RUN=1`, nên không gửi Telegram khi chưa tắt.

## Secrets cần cấu hình (GitHub Actions)

- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Không bao giờ commit `.env` hay API key vào repo. Repo là public.

# Tech Radar — Ý tưởng & Kế hoạch

Trạng thái: **Bản nháp, chưa bắt đầu code.**
Ngày tạo: 2026-11-24

## 1. Mục tiêu

Tổng hợp tin công nghệ tự động, hằng ngày, với 2 lớp đọc:

- **Lớp 1 — Telegram (đọc nhanh):** 1 tin/ngày, 5–7 mục, mỗi mục 2–3 dòng: tiêu đề + 1 câu giá trị cốt lõi + 2 link [Đào sâu] và [Nguồn gốc].
- **Lớp 2 — GitHub Pages (đọc sâu & lưu trữ):** bài phân tích kỹ thuật cho từng mục (vấn đề, cách hoạt động, trade-off, điểm đáng chú ý). Tích lũy thành kho "Tech Radar Archive" có tìm kiếm toàn văn.

Ràng buộc: $0/tháng, không cần máy chủ chạy 24/7.

## 2. Kiến trúc

```
[Ingestion]                 [AI]                        [Publishing]
hnrss.org (HN, points≥300)  Chặng 1: Gatekeeper         A. Repo (Markdown)
GitHub Search API      ──▶  chấm điểm, chọn Top 5–7 ──▶   └─ Actions: SSG build → Pages
GitHub Releases .atom       Chặng 2: Enrichment          B. Telegram: 1 tin tổng hợp
SQLite/JSON (state)         fulltext → Markdown + tóm tắt   (gửi SAU khi Pages deploy xong)
```

### Chặng 1 — Gatekeeper
- Đầu vào: tiêu đề + mô tả ngắn của item mới trong 24h, đã lọc trùng.
- 1 lần gọi Gemini với structured output (Pydantic): mỗi item có `score` (1–10), `reason`, `topic`.
- Chọn Top 5–7 có điểm ≥ 7, ưu tiên đa dạng chủ đề.

### Chặng 2 — Enrichment & Publish
- Chỉ với 5–7 mục đã chọn: lấy fulltext (trafilatura cho bài báo, GitHub API cho README).
- Sinh cùng lúc: tóm tắt 2 dòng (Telegram) và bài Markdown (Pages).
- Ghi file vào `docs/digests/YYYY-MM-DD/`, build, deploy, rồi mới gửi Telegram.

## 3. Quyết định kiến trúc

| Quyết định | Chọn | Lý do |
|---|---|---|
| Sinh bài deep dive | Pre-generate mỗi sáng | Đọc tức thì; kho lưu trữ đầy đủ; không cần bot chạy 24/7 |
| Nơi chạy | GitHub Actions (MVP) | $0, không phụ thuộc điện/mạng nhà; homelab để sau |
| SSG | MkDocs Material 9.7.0 (pin phiên bản) | Build nhanh, dark mode, tìm kiếm client-side. Đã kiểm tra 2026-11-24: Material ở maintenance mode, chỉ sửa lỗi nghiêm trọng/bảo mật đến 2027-05-05. Chấp nhận được vì pipeline chỉ sinh Markdown. Đường lui: Zensical (cùng đội, đọc được `mkdocs.yml`) |
| Ngôn ngữ | Tiếng Việt (Telegram và Pages) | Một ngôn ngữ duy nhất, không song ngữ |
| Repo | `tech-radar`, public | Điều kiện để Pages miễn phí |
| Số mục/ngày | Linh hoạt 0–7, chỉ lấy điểm ≥ 7 | Không gửi tin rỗng |
| State | `processed_urls.json` trong repo | Diff gọn, dễ đọc. Không dùng `state.db` (binary) |
| LLM | Gemini (free tier), sau lớp provider mỏng | Dễ đổi model khi quota/giá thay đổi |
| Thứ tự job | Python → commit → deploy Pages → Telegram | Link Telegram không bao giờ 404 |

## 4. Rủi ro & cách xử lý

**Nội dung (quan trọng nhất, vì bài là công khai):**
- LLM bịa số liệu (ví dụ "giảm 40% độ trễ"). → Prompt chỉ dùng thông tin có trong fulltext; không rõ thì ghi "chưa rõ"; số liệu phải trích nguồn.
- Tóm tắt dễ giống quảng cáo. → Yêu cầu nêu trade-off và hạn chế, không chỉ điểm mạnh.
- Bản quyền. → Chỉ dùng fulltext để phân tích, không chép đoạn dài; luôn có link nguồn; kiểm tra license của repo trước khi tóm tắt README.

**Chọn lọc:**
- Điểm 1–10 dễ dồn về 7–8. → Bắt model giải thích `reason`; theo dõi phân phối điểm qua các ngày.
- Không đủ 5 mục đạt ngưỡng. → Gửi ít hơn, hoặc bỏ qua ngày đó. Không gửi tin rỗng.
- Trùng tin giữa các nguồn. → Dedup theo canonical URL + tên repo + độ tương đồng tiêu đề.

**Vận hành:**
- Cron GitHub Actions dùng **UTC**: 06:30 ICT = `30 23 * * *` (UTC hôm trước).
- Cron có thể trễ hoặc bị bỏ qua vài chục phút. Chấp nhận, và luôn có `workflow_dispatch`.
- Repo public: scheduled workflow có thể bị tắt sau 60 ngày không hoạt động. Cần kiểm tra commit của bot có được tính không.
- Lần chạy thủ công và lần chạy lịch có thể đè nhau. → `concurrency: group: daily-digest`.
- Telegram `parse_mode=HTML`: phải escape output của LLM (`&`, `<`, `>`) trước khi bọc thẻ. Giới hạn 4096 ký tự/tin.
- Telegram preview: dùng `link_preview_options={"is_disabled": true}`.
- Cào web từ IP GitHub Actions có thể bị Cloudflare chặn. → Fallback về description trong feed và ghi log rõ.
- Gemini free tier: quota và model thay đổi thường xuyên, có thể khác theo vùng. Kiểm tra AI Studio trước khi chốt.
- Free tier có thể cho Google dùng dữ liệu để cải thiện sản phẩm. Nguồn đều công khai nên không đáng lo, nhưng không đưa gì nhạy cảm vào prompt.
- GitHub Pages soft limit: 1 GB, 100 GB băng thông/tháng, 10 build/giờ. Mức dùng dự kiến (~365 file/năm) không chạm trần.

## 5. Ý tưởng để sau (không làm trong MVP)

- Nguồn bổ sung: Reddit, blog RSS, Hacker News đầy đủ, arXiv (lọc theo từ khóa).
- Nguồn khó (X/Twitter, web động) qua RSSHub self-hosted trên homelab. Chỉ thêm khi thật sự cần.
- Lệnh Telegram `/deep <số>` để phân tích sâu theo yêu cầu. Cần bot chạy long polling 24/7, nên để sau.
- Tag theo chủ đề (AI, Infra, Database...) và trang index theo chủ đề.
- Đánh giá chất lượng bài: giữ lại mục người đọc bấm vào để học dần sở thích.
- Hỏi đáp trên kho lưu trữ (RAG nhỏ trên Markdown).

## 6. Roadmap

Ước lượng thực tế: khoảng 1 cuối tuần cho cả 3 bước, không phải 1 buổi tối.

**Bước 0 — Chốt quyết định (xong ở mục 3).**
- [ ] Xác nhận Gemini API khả dụng và quota đủ tại vùng của bạn.
- [x] Chọn SSG: MkDocs Material 9.7.0 (xem mục 3).
- [ ] Tạo bot Telegram, lấy `TELEGRAM_CHAT_ID`.

**Bước 1 — Khung repo & Pages (~30 phút).**
- [x] Cấu hình `mkdocs.yml` với theme, dark mode, tìm kiếm (build `--strict` đã qua ở máy local).
- [x] Tạo `docs/index.md` và một bản tin mẫu thủ công (`docs/digests/2026-11-24/`).
- [x] Workflow `pages.yml`: build và deploy bằng `actions/deploy-pages`.
- [ ] Thay `<user>` trong `mkdocs.yml`, push lên GitHub, bật Pages (source: GitHub Actions).
- [ ] Xác nhận site live.

**Bước 2 — Worker Python (cuối tuần).**
- [ ] Ingestion: hnrss.org (points ≥ 300), GitHub Search API, GitHub Releases `.atom`.
- [ ] Dedup và `processed_urls.json`.
- [ ] Chặng 1: Gatekeeper với Pydantic, chọn Top 5–7.
- [ ] Chặng 2: fulltext + sinh Markdown và tóm tắt Telegram. Escape HTML, kiểm tra độ dài.
- [ ] Gửi Telegram (có `dry_run` để in ra console thay vì gửi).
- [ ] Test với fixture; không gọi API thật trong unit test.

**Bước 3 — Tự động hóa (~1–2 giờ).**
- [ ] `daily-digest.yml`: cron `30 23 * * *` UTC + `workflow_dispatch`, `concurrency`.
- [ ] Chuỗi job: worker → commit → deploy Pages → Telegram (chỉ khi deploy thành công).
- [ ] Thông báo khi job fail.
- [ ] Chạy thử thủ công 2–3 lần, kiểm tra chất lượng bài từng ngày.

**Bước 4 — Theo dõi (1–2 tuần).**
- [ ] Xem phân phối điểm, số mục mỗi ngày, lỗi fetch.
- [ ] Chỉnh prompt dựa trên bài thực tế.

## 7. Câu hỏi đã chốt (2026-11-24)

- Ngôn ngữ: tiếng Việt.
- Tên repo/site: `tech-radar`.
- Repo public.
- Số mục mỗi ngày: linh hoạt 0–7.

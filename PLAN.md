# Tech Radar — Ý tưởng & Kế hoạch

Trạng thái: **Đã triển khai Bước 1–3** (khung site, worker, workflow hằng ngày). Xem README để biết cách chạy.
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
| State | `assets/processed_urls.json` (JSON nén gọn) + xoay vòng `assets/processed_urls-YYYY-MM.json.gz` (tối đa 12 tháng) | Giữ state tách khỏi root, có trần số mục & file nén nên không phình vô hạn |
| LLM | `gemini-3.8-flash` (đã xác minh qua `models.list`), sau lớp provider mỏng | Tổng ~8 req/ngày nên ưu tiên chất lượng phân tích tiếng Việt & chống bịa đặt thay vì `flash-lite`; dự phòng `gemini-3.5-flash-lite` nếu bị siết quota |
| Thứ tự job | Python → `mkdocs build --strict` → commit → deploy Pages → Telegram | Bài hỏng không lọt vào `main`; link Telegram không bao giờ 404 |

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
- [x] Xác nhận Gemini API khả dụng và kiểm tra `models.list()` (`gemini-3.8-flash`).
- [x] Chọn SSG: MkDocs Material 9.7.0 (xem mục 3).
- [x] Tạo bot Telegram, lấy `TELEGRAM_CHAT_ID` (và đặt vào GitHub Secrets).

**Bước 1 — Khung repo & Pages (~30 phút).**
- [x] Cấu hình `mkdocs.yml` với theme, dark mode, tìm kiếm (build `--strict` đã qua ở máy local).
- [x] Tạo `docs/index.md`, `docs/digests/index.md` (xếp mới nhất lên đầu) và bản tin đầu tiên (`docs/digests/2026-11-24/`).
- [x] Workflow `pages.yml`: build và deploy bằng `actions/deploy-pages`.
- [x] Thay `<user>` thành `tamvcspk` trong `mkdocs.yml`.
- [x] Push lên GitHub, bật Pages (source: GitHub Actions) và xác nhận site live.

**Bước 2 — Worker Python (cuối tuần).**
- [x] Ingestion: hnrss.org (points ≥ 300), GitHub Search API (lọc fork/archived/NOASSERTION/từ khóa đáng ngờ), GitHub Releases `.atom` (đọc `<content>`, bỏ pre-release).
- [x] Dedup (giữ query định danh, bỏ tracking param) và `assets/processed_urls.json` (JSON gọn + xoay vòng `.json.gz`).
- [x] Chặng 1: Gatekeeper với Pydantic, chọn tối đa 7 mục điểm ≥ 7 (có thể ít hơn hoặc rỗng).
- [x] Chặng 2: fulltext/README (kiểm tra license kể cả link GitHub từ HN) + sinh Markdown (gộp bài khi chạy lại trong ngày qua `.articles.json`) và tóm tắt Telegram. Escape HTML, kiểm tra độ dài.
- [x] Retry/backoff cho lỗi Gemini tạm thời (429/5xx) và gửi Telegram (`python -m worker send --dry-run`).
- [x] Test với fixture; không gọi API thật trong unit test.

**Bước 3 — Tự động hóa (~1–2 giờ).**
- [x] `daily-digest.yml`: cron `30 23 * * *` UTC + `workflow_dispatch` (mặc định dry run), `concurrency`, quyền tối thiểu theo từng job.
- [x] Chuỗi job: worker → `mkdocs build --strict` → commit (`git pull --rebase`) → deploy Pages (chỉ khi có bản tin) → Telegram.
- [x] Thông báo khi job fail (gửi qua Telegram, tự bỏ qua nếu chưa cấu hình secret).
- [x] Cấu hình GitHub Secrets (`GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) và Variable `GEMINI_MODEL=gemini-3.8-flash`.
- [ ] Chạy thử thủ công (`workflow_dispatch`) 2–3 lần, kiểm tra chất lượng bài từng ngày.

**Bước 4 — Theo dõi & tinh chỉnh (1–2 tuần).**
- [ ] Xem phân phối điểm, số mục mỗi ngày, lỗi fetch.
- [ ] Tinh chỉnh heuristic chống repo spam sao ảo ở GitHub Search dựa trên log (`stars`, `forks`, `lang`, `desc_len`) đã gắn sẵn.
- [ ] Chỉnh prompt dựa trên bài thực tế.
- [ ] Đồng bộ Python local về 3.12 (khớp CI) khi tiện; cân nhắc `mkdocs-awesome-nav` nếu muốn đổi cả thứ tự sidebar (hiện đã có trang `docs/digests/index.md` xếp mới nhất lên đầu).

## 7. Câu hỏi đã chốt (2026-11-24)

- Ngôn ngữ: tiếng Việt.
- Tên repo/site: `tech-radar`.
- Repo public.
- Số mục mỗi ngày: linh hoạt 0–7.

## 8. Kế hoạch cải thiện (đề xuất 2026-11-25)

Trạng thái: **đề xuất, chưa triển khai.** Thứ tự ưu tiên theo ROI và phụ thuộc.

### 8.1 Lỗi đã ghi nhận: bản tin 06:30 đến lúc 12:41

- Cron `30 23 * * *` UTC (06:30 ICT) đúng. Lần chạy theo lịch ngày 2026-11-25 được GitHub tạo lúc 05:37:59 UTC (12:37 ICT), trễ khoảng 6 giờ. Job chạy 4 phút.
- GitHub chỉ cam kết "best effort" cho `schedule`. Có thể trễ nhiều giờ hoặc bị bỏ qua. Mục 4 ghi "trễ vài chục phút" là đánh giá quá lạc quan.
- Lịch `schedule` của repo public có thể bị tắt sau 60 ngày không hoạt động (xem mục 4).

**Why:** cron trên GitHub không đáng tin về giờ. Cần kích hoạt từ bên ngoài.
**How to apply:** P0 bên dưới.

### 8.2 Bảng kế hoạch

| # | Việc | Công sức | Phụ thuộc |
|---|---|---|---|
| P0 | Kích hoạt `workflow_dispatch` từ homeserver (PAT fine-grained, chỉ `actions:write` trên repo này). Giữ `schedule` làm dự phòng, dời sang ~08:00 ICT. Thêm `assets/last_sent_date` để không gửi trùng. Đổi `LOOKBACK` 24h cố định thành `since = lần chạy thành công gần nhất`, trần 72h. | ~2h | — |
| P1 | Nguồn mới: Lobste.rs JSON (`/hottest.json` hoặc `/t/<tag>.json`, có `score`); Show HN ≥100; HF Daily Papers qua `huggingface.co/api/daily_papers` (có `upvotes`); Simon Willison `/atom/entries/`; 2–3 blog kỹ thuật có RSS. Giới hạn tối đa 15 mục mỗi nguồn. Chủ đề chuyển sang enum cố định. | ~½ ngày | — |
| P2 | Lọc tầng 1 không dùng LLM: repo tạo 7–30 ngày trước, còn push gần đây; kiểm tra `/languages` (tỷ lệ code), số commit sau ngày tạo, CI/tests (chỉ là điểm cộng nhẹ). Đưa số liệu và ~1.500 ký tự đầu README vào prompt Gatekeeper. Thêm red flags (thin wrapper, hype, số liệu không kiểm chứng) và green flags theo thuộc tính đo được (benchmark, ít dependency, nêu hạn chế). Không cộng điểm theo ngôn ngữ lập trình. | ~1 ngày | — |
| P3 | Điều hướng năm/tháng/ngày trên site; trang tổng kết tháng (một lần LLM mỗi tháng). Giữ nguyên URL trang ngày vì link Telegram đã gửi. | ~½ ngày | — |
| P4 | Telegram: một tin tiêu đề + mỗi mục một tin (`disable_notification` cho tin mục). Poller reaction (`allowed_updates=["message_reaction"]`) chạy trên homeserver, long polling 24/7. Hồ sơ sở thích theo chủ đề đưa vào prompt, giữ 1 trong 7 mục cho chủ đề ngoài sở thích. | ~1–2 ngày | P1 |
| P5 | Backfill 2026: HN Algolia API + GitHub REST (releases, Search theo tháng). Sinh trang tổng kết tháng 1–10 bằng chung code với P3, không sinh bản tin ngày giả. Chạy theo từng tháng bằng `workflow_dispatch` có tham số `month`, chạy lại được, không gửi Telegram. Kiểm tra quota Gemini RPD trước khi chạy. | ~1 ngày | P3, P2 |

**Không làm hoặc để sau:** ArXiv thô (cs.AI có hàng trăm bài mỗi ngày, LLM không đánh giá được qua tiêu đề); ByteByteGo (chủ yếu là sơ đồ đăng lại); `papers.takara.ai` (trung gian không chính thức); phân tích tài khoản stargazer; tầng "nửa năm" (chồng lên năm và tháng).

### 8.3 Quyết định còn mở

- Ngưỡng HN: giữ 300 hay hạ xuống 200 sau khi xem số lượng tin.
- Poller reaction: chạy trên homeserver hay chấp nhận đọc `getUpdates` mỗi ngày (mất dữ liệu nếu lịch trễ quá 24h).
- Anthropic engineering blog: kiểm tra xem có RSS chính thức không trước khi thêm.

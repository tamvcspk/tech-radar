# Brief: tech-radar

Ngày chốt: 2026-11-26 · Mode: 1
Nguồn: PLAN.md ở gốc repo (ý tưởng ngày 2026-11-24, đề xuất cải thiện ngày 2026-11-25).

## Vấn đề

Tin công nghệ nhiều và rải rác. Muốn nắm nhanh mỗi ngày mà không đọc hết các nguồn, và muốn bài phân tích sâu được lưu lại để tra cứu sau này. Hệ thống tự động tổng hợp, chạy $0/tháng trên GitHub Actions, không cần máy chủ 24/7.

## Người dùng

Người đọc tiếng Việt quan tâm tin công nghệ hằng ngày. PLAN không định nghĩa thêm về nhóm người đọc.

## Phạm vi (làm)

- Ingestion: hnrss.org (points ≥ 300), GitHub Search API, GitHub Releases `.atom`.
- Chặng 1: Gatekeeper bằng Gemini, chọn tối đa 7 mục điểm ≥ 7.
- Chặng 2: lấy fulltext/README, sinh bài Markdown và tóm tắt Telegram.
- Lớp 1: 1 tin Telegram tổng hợp. Lớp 2: site MkDocs trên GitHub Pages có tìm kiếm.
- Chạy tự động hằng ngày qua GitHub Actions, kèm `workflow_dispatch`.

## Non-goals (không làm)

Lấy từ PLAN.md mục 5 và cột "Không làm hoặc để sau" ở mục 8.2:

- Nguồn: ArXiv thô (cs.AI có hàng trăm bài mỗi ngày, LLM không đánh giá được qua tiêu đề); ByteByteGo (chủ yếu đăng lại sơ đồ); `papers.takara.ai` (trung gian không chính thức); phân tích tài khoản stargazer.
- Tầng "nửa năm" (chồng lên năm và tháng).
- Nguồn khó (X/Twitter, web động) qua RSSHub: chỉ thêm khi thật sự cần.
- Lệnh Telegram `/deep <số>` và bot long polling 24/7 trên GitHub Actions (để sau).
- Tag và trang index theo chủ đề; hỏi đáp trên kho lưu trữ (RAG); đánh giá chất lượng bài theo người đọc (để sau).

## Tiêu chí thành công

- Bản tin đến Telegram mỗi sáng, trong khung 06:30–08:00 ICT (PLAN mục 8.2 P0).
- Không gửi tin rỗng; ngày không đủ mục đạt ngưỡng thì gửi ít hơn hoặc bỏ qua.
- Mỗi bài có link nguồn; mọi số liệu trong bài truy được về fulltext.

## Rủi ro đã phản biện

| Rủi ro | Kịch bản lỗi cụ thể | Cách xử lý |
|---|---|---|
| LLM bịa số liệu | Bài ghi "giảm 40% độ trễ" không có trong nguồn | Prompt chỉ dùng thông tin trong fulltext; không rõ thì ghi "chưa rõ"; số liệu phải trích nguồn (PLAN §4) |
| Cron GitHub trễ hoặc bỏ qua | Bản tin 06:30 đến lúc 12:41 (ngày 2026-11-25) | Kích hoạt `workflow_dispatch` từ bên ngoài, `schedule` làm dự phòng (PLAN §8.1, P0) |
| Cào web bị chặn | Cloudflare chặn IP GitHub Actions | Fallback về description trong feed và ghi log rõ (PLAN §4) |
| Quota Gemini | Free tier đổi model và quota | Model và dự phòng ghi trong PLAN §3; kiểm tra AI Studio trước khi đổi |
| Bản quyền | Chép đoạn dài từ bài gốc hoặc README | Chỉ dùng fulltext để phân tích; luôn có link nguồn; kiểm tra license (PLAN §4) |
| Pages bị trễ so với Telegram | Link Telegram 404 | Deploy Pages xong mới gửi Telegram (PLAN §3) |

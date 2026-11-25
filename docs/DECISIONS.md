# Quyết định kỹ thuật

Chỉ thêm, không sửa entry cũ. Đổi quyết định thì thêm entry mới và ghi "Thay thế D-xx".

Nguồn gốc: bảng quyết định ở PLAN.md (gốc repo) mục 3 (2026-11-24). Entry dưới đây chép lại từ đó; mục "Đã loại" chỉ ghi phương án PLAN đã nêu, không bổ sung.

## D-01 · 2026-11-24 · Sinh bài deep dive trước mỗi sáng

- Bối cảnh: cần đọc tức thì, lưu trữ đầy đủ, không có bot chạy 24/7.
- Chọn: pre-generate mỗi sáng.
- Vì: đọc tức thì; kho lưu trữ đầy đủ; không cần bot 24/7.
- Đã loại: chưa ghi trong PLAN.

## D-02 · 2026-11-24 · Nơi chạy: GitHub Actions (MVP)

- Bối cảnh: cần chạy hằng ngày mà không tốn tiền.
- Chọn: GitHub Actions.
- Vì: $0; không phụ thuộc điện/mạng nhà.
- Đã loại: homelab, để sau (PLAN ghi "homelab để sau").

## D-03 · 2026-11-24 · SSG: MkDocs Material 9.7.0 (pin)

- Bối cảnh: site tĩnh, dark mode, tìm kiếm.
- Chọn: MkDocs Material 9.7.0, pin phiên bản.
- Vì: build nhanh, dark mode, tìm kiếm client-side. Đã kiểm tra 2026-11-24: Material ở maintenance mode, chỉ sửa lỗi nghiêm trọng/bảo mật đến 2027-05-05. Chấp nhận vì pipeline chỉ sinh Markdown.
- Đường lui: Zensical (cùng đội, đọc được `mkdocs.yml`).

## D-04 · 2026-11-24 · Ngôn ngữ: tiếng Việt

- Chọn: tiếng Việt cho cả Telegram và Pages.
- Vì: một ngôn ngữ duy nhất, không song ngữ.
- Đã loại: song ngữ (PLAN ghi "không song ngữ").

## D-05 · 2026-11-24 · Repo public

- Chọn: `tech-radar` public.
- Vì: điều kiện để GitHub Pages miễn phí.
- Hệ quả: scheduled workflow có thể bị tắt sau 60 ngày không hoạt động (PLAN mục 4); không đưa secret vào repo.

## D-06 · 2026-11-24 · Số mục mỗi ngày linh hoạt 0–7

- Chọn: chỉ lấy điểm ≥ 7, tối đa 7 mục, có thể 0.
- Vì: không gửi tin rỗng.

## D-07 · 2026-11-24 · State: JSON nén gọn và xoay vòng `.json.gz`

- Chọn: `assets/processed_urls.json` + `assets/processed_urls-YYYY-MM.json.gz` (tối đa 12 tháng).
- Vì: state tách khỏi root; có trần số mục và file nén nên không phình vô hạn.

## D-08 · 2026-11-24 · LLM: `gemini-3.8-flash`, sau lớp provider mỏng

- Chọn: `gemini-3.8-flash` (đã xác minh qua `models.list`); dự phòng `gemini-3.5-flash-lite` nếu bị siết quota.
- Vì: khoảng 8 request mỗi ngày nên ưu tiên chất lượng phân tích tiếng Việt và chống bịa đặt.
- Đã loại: `flash-lite` làm mặc định (PLAN ghi là dự phòng).

## D-09 · 2026-11-24 · Thứ tự job: build trước, Telegram sau cùng

- Chọn: Python → `mkdocs build --strict` → commit → deploy Pages → Telegram.
- Vì: bài hỏng không lọt vào `main`; link Telegram không bao giờ 404.

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

## D-10 · 2026-11-26 · Chống gửi trùng và mốc `since` (P0)

- Chọn: `assets/last_sent_date` (ICT) do job `telegram` ghi và commit sau khi gửi thật; `run` bỏ qua nếu ngày đó đã gửi, `send` cũng không gửi lại. Mốc lấy tin `since` = `last_success_at` trong `processed_urls.json`, kẹp trong [now − 72h, now], mặc định 24h khi chưa có.
- Vì: có hai đường kích hoạt (homeserver + cron dự phòng) nên phải chặn trùng; ghi sau khi gửi (không phải sau khi sinh) để lần chạy lại vẫn gửi được khi Telegram lỗi.
- Đánh đổi: `last_success_at` không tiến khi có mục bị bỏ vì lỗi LLM tạm thời, nên lần sau có thể xét lại một số mục đã thấy (dedup chặn phần đã đánh dấu). Job `telegram` cần `contents: write`.

## D-11 · 2026-11-26 · Chạy sớm bằng cron GitHub thay cho trigger homeserver (P0)

- Thay thế một phần D-10 (phần "hai đường kích hoạt: homeserver + cron dự phòng").
- Chọn: bỏ trigger từ homeserver và PAT. Cron `schedule` chạy 02:17 ICT, thêm lần dự phòng 04:47 ICT. Lần dự phòng tự bỏ qua nhờ `assets/last_sent_date` nếu bản tin đã gửi.
- Vì: người dùng ngủ lúc 02:00 nên đọc tin lúc 06:30 hay 02:00 như nhau. Độ trễ cron GitHub đã ghi nhận là 06:30 → 12:41 (PLAN mục 8.1); chạy sớm 4–5 giờ cho đệm đó mà không cần máy nào khác, token nào khác.
- Đánh đổi: tin chỉ gồm mục đến 02:17 ICT; mục xuất hiện sau đó sang bản tin hôm sau (không mất nhờ `since`). Không còn đường kích hoạt độc lập với GitHub: nếu cả hai lần cron bị rớt thì ngày đó không có tin. Khi gặp lần đầu, cân nhắc lại trigger homeserver (`scripts/trigger-digest.sh` còn dùng được). Tin Telegram đến lúc 02:17, có thể gây thông báo ban đêm.

## D-12 · 2026-11-26 · Tin Telegram gửi bình thường, không im lặng

- Chọn: giữ `sendMessage` mặc định, không dùng `disable_notification`.
- Vì: người dùng quyết định không cần gửi im lặng.

## D-13 · 2026-11-27 · Cron mỗi giờ 02:17–07:17 ICT, chạy tay khi cần (P0)

- Thay thế D-11 (phần lịch cron; vẫn không dùng homeserver).
- Chọn: một lịch `17 19-23,0 * * *` (6 lần mỗi đêm) thay cho hai lần 02:17 và 04:47. Vẫn serverless, không PAT, không dịch vụ ngoài. Nếu sáng không có tin thì vào GitHub chạy tay `workflow_dispatch` (bỏ chọn dry_run).
- Vì: ngày 2026-11-27 cả hai lần cron đều trễ 6–7 giờ (chạy lúc 09:16 và 10:49 ICT), bản tin gửi 09:18 ICT. Nhiều lần chạy tăng cơ hội có một lần đến sớm; `last_sent_date` đã kiểm chứng chặn gửi trùng.
- Đánh đổi: nếu GitHub hoãn cả repo cùng một lúc thì nhiều lần cũng không giúp. Mỗi lần bị bỏ qua tốn khoảng 20–25 giây Actions (repo public, miễn phí). Quyết định phụ thuộc dữ liệu 3–4 ngày tới; nếu vẫn trễ thì mới xét dịch vụ ngoài gọi `workflow_dispatch`.

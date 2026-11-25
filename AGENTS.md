# tech-radar

Tự động tổng hợp tin công nghệ mỗi sáng: 1 tin Telegram 5–7 mục (lớp 1) và bài phân tích sâu trên GitHub Pages (lớp 2). Chi tiết ý tưởng và kế hoạch: [PLAN.md](PLAN.md).

File này là luật chung cho mọi agent (Claude Code, Antigravity). Luật riêng của từng tool chỉ được thêm, không được mâu thuẫn với file này.

## Stack

- Python 3.12: worker (ingest → lọc → enrich → xuất bản). Dependency trong `requirements*.txt` (google-genai, pydantic, trafilatura, requests).
- MkDocs Material 9.7.0 (pin): site tĩnh, build bằng `mkdocs build --strict`.
- GitHub Actions: cron `30 23 * * *` UTC (06:30 ICT) + `workflow_dispatch`; deploy GitHub Pages.
- Telegram Bot API: gửi tin tổng hợp, `parse_mode=HTML`.

## Lệnh

| Việc | Lệnh |
|---|---|
| Kiểm tra toàn bộ (test + build docs) | `bash scripts/check` |
| Chạy worker (sinh bản tin, cần `GEMINI_API_KEY` trong `.env`) | `.venv/Scripts/python -m worker run` |
| Xem site cục bộ | `.venv/Scripts/python -m mkdocs serve` |
| Cài dependency | `.venv/Scripts/python -m pip install -r requirements-dev.txt` |

## Luật cứng

- Chỉ báo "xong" khi `bash scripts/check` thoát mã 0. Dán dòng kết quả cuối khi báo cáo.
- Chỉ làm việc nằm trong checklist của `docs/SPEC.md` (milestone hiện tại: P0). Việc ngoài phạm vi: ghi vào mục "Ý tưởng để sau" trong `docs/SPEC.md`, không tự làm.
- Không làm những thứ trong mục Non-goals của `docs/BRIEF.md`.
- Không thêm dependency mới nếu chưa ghi lý do vào `docs/DECISIONS.md`.
- Quyết định có đánh đổi ghi vào `docs/DECISIONS.md`: chỉ thêm entry mới; muốn đổi thì thêm entry ghi "Thay thế D-xx".
- Trước khi chuyển sang tool khác: cập nhật `docs/HANDOFF.md` (ghi đè) và commit.
- Không ghi secret vào file nào được commit. Repo là public. Biến môi trường mô tả trong `.env.example`; giá trị thật chỉ nằm trong `.env` (đã gitignore) hoặc GitHub Secrets.

## Quy ước code

- Tài liệu viết tiếng Việt. Thuật ngữ, lệnh và code giữ tiếng Anh.
- Test không gọi API thật (Gemini, Telegram, GitHub): dùng fixture.

## Tài liệu

- `docs/BRIEF.md`: bài toán, người dùng, phạm vi, non-goals, rủi ro đã phản biện.
- `docs/SPEC.md`: milestone hiện tại và checklist.
- `docs/DECISIONS.md`: các quyết định kỹ thuật (ADR rút gọn).
- `PLAN.md`: ý tưởng, kiến trúc và roadmap gốc. Nguồn của các file trên; không sửa để đồng bộ tự động.
- `README.md`: cách chạy local và secret cần cấu hình.
- `docs/HANDOFF.md`: trạng thái khi chuyển tool.

## Phân vai tool

- **Claude Code**: viết và sửa code, chạy lệnh, refactor.
- **Antigravity**: việc cần browser (E2E, kiểm tra UI, chụp màn hình, console error), đọc rộng toàn repo.
- **Review**: dùng phiên có ngữ cảnh mới, không phải phiên đã viết code. Thay đổi rủi ro cao (auth, migration, dữ liệu người dùng, tiền) thì review bằng tool khác họ model.
- Người duyệt diff cuối cùng.

## Kiến thức liên quan

Ghi chú trong knowledge base cá nhân. Đọc trước khi đụng tới phần liên quan.

- [[workflow/work-modes]] (C:\Src\knowledge-base\workflow\work-modes.md): quy trình Mode 1 và luật "check xanh mới báo xong".

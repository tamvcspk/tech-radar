@AGENTS.md

## Riêng cho Claude Code

- Việc đọc rộng, tìm kiếm nhiều file: dùng subagent để giữ ngữ cảnh phiên chính gọn.
- Không dùng model lớn cho boilerplate; dùng subagent model nhỏ cho việc tra cứu.
- Stop hook chạy `scripts/check` khi có thay đổi chưa commit. Nếu hook chặn, sửa lỗi nó báo, không tắt hook.

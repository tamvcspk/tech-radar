# Handoff

Ghi đè toàn bộ file mỗi lần chuyển tool. Tối đa 30 dòng.

- Thời điểm: 2026-11-26
- Từ: Claude Code → Sang: (chưa chuyển; file khởi tạo khi adopt project-kit)
- Nhánh / worktree: main
- Commit cuối: 9eeab5d
- `scripts/check`: OK (exit 0) lúc 2026-11-26

## Mục tiêu đang làm

PLAN.md mục 8.2, P0: kích hoạt workflow hằng ngày đáng tin (chưa bắt đầu).

## Đã xong

- Khung site, worker và workflow hằng ngày (PLAN mục 6, Bước 1–3).
- Áp project-kit (Mode 1): AGENTS.md, CLAUDE.md, `.agent/rules/project.md`, `scripts/check`, `scripts/stop-check.sh`, `.claude/settings.json`.

## Đang dở

- PLAN.md có thay đổi chưa commit (không do adopt tạo). Chưa quyết định giữ hay commit.

## File đã đụng

- Mới: AGENTS.md, CLAUDE.md, `.agent/rules/project.md`, `docs/HANDOFF.md`, `docs/BRIEF.md`, `docs/SPEC.md`, `docs/DECISIONS.md`, `scripts/check`, `scripts/stop-check.sh`, `.claude/settings.json`
- Sửa: `mkdocs.yml` (thêm `exclude_docs` cho 4 file nội bộ), AGENTS.md (trỏ tới docs/)

## Việc tiếp theo (theo thứ tự)

1. Quyết định về PLAN.md đang sửa dở.
2. P0: trigger `workflow_dispatch` từ homeserver, thêm `assets/last_sent_date`, đổi LOOKBACK sang `since` (PLAN mục 8.2).

## Lưu ý cho người nhận

- Luật ở AGENTS.md trỏ tới PLAN.md, không có docs/SPEC.md hay BRIEF.md riêng.
- Repo public; không đưa `.env` hay secret vào commit.

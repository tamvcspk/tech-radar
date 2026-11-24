"""Danh sách nguồn có thể chỉnh tay. Thêm/bớt repo ở đây, không cần đổi code."""

# Repo GitHub mà worker theo dõi release qua feed .atom.
WATCHED_REPOS: list[str] = [
    "python/cpython",
    "golang/go",
    "rust-lang/rust",
    "kubernetes/kubernetes",
    "nodejs/node",
    "denoland/deno",
    "astral-sh/uv",
    "pydantic/pydantic",
    "vercel/next.js",
    "microsoft/TypeScript",
]

MIN_HN_POINTS = 300
MIN_GH_STARS = 100

# astral-sh/uv 0.13.10

!!! info "Nguồn"
    Nguồn gốc: <https://github.com/astral-sh/uv/releases/tag/0.13.10>

    Chất lượng phân tích: fulltext

Bản phát hành uv 0.13.10 xử lý lỗ hổng bảo mật GHSA-vjvj-3m3f-fgmm và siết chặt quy trình kiểm tra tính hợp lệ của uv.lock.
Phiên bản này cũng sửa lỗi định dạng tệp wheel, thử nghiệm tính năng proxy index chuyển tiếp và cập nhật các bản dựng Python.

## Vấn đề
- Dự án cần khắc phục lỗ hổng an ninh được định danh là GHSA-vjvj-3m3f-fgmm (chi tiết cụ thể của lỗ hổng chưa rõ trong tài liệu nguồn).
- Tệp `uv.lock` trước đây có thể gặp tình trạng thiếu đồng bộ giữa yêu cầu phụ thuộc và phiên bản gói thực tế, thiếu thông tin giải thích khi cờ `--locked` từ chối tệp khóa, hoặc bỏ sót cảnh báo khi phụ thuộc không có mục nhập trong lockfile.
- Nguy cơ từ các tệp wheel hỏng hoặc bất thường cấu trúc khi trường kích thước nén giữa ZIP data descriptor và central directory không trùng khớp.
- Thông tin bộ nhớ đệm (cache) của trình thông dịch Python không tự cập nhật khi môi trường thay đổi như cập nhật libc, phiên bản macOS hoặc tệp `pyvenv.cfg`.
- Các trục trặc khác trong phân giải: lỗi khi `uv sync --no-install-package` gặp gói thiếu bản phân phối tương thích, việc đòi hỏi hash cho các wheel không thể truy cập, và việc tái sử dụng các phiên bản bị yank chứa marker không thỏa mãn trong chế độ `uv pip compile --universal`.

## Cách hoạt động
- Tăng cường xác thực `uv.lock`: Kiểm tra đối chiếu yêu cầu phụ thuộc với các phiên bản gói đã khóa, xuất thông báo giải thích nguyên nhân khi `--locked` yêu cầu cập nhật, và báo cáo các phụ thuộc bị thiếu mục nhập gói.
- Từ chối tệp wheel không chuẩn: Hệ thống chủ động loại bỏ các tệp wheel có kích thước nén trong ZIP data descriptor không khớp với central directory.
- Tự động làm mới cache: Trình thông dịch sẽ làm mới lại thông tin lưu tạm ngay khi phát hiện có sự thay đổi ở libc, phiên bản hệ điều hành macOS hoặc tệp cấu hình `pyvenv.cfg`.
- Điều chỉnh quy trình phân giải gói: Cho phép `uv sync --no-install-package` bỏ qua các gói không có bản phân phối tương thích; bỏ qua các wheel không tiếp cận được trước khi áp dụng kiểm tra hash trong `uv.lock`; ngăn chặn việc tái sử dụng phiên bản bị yank không phù hợp khi biên dịch đa nền tảng.
- Hỗ trợ proxy index (tính năng xem trước): Cho phép sử dụng các proxy index nhưng vẫn duy trì tính tương thích và khả chuyển của lockfile đối với index gốc (upstream) nhờ cơ chế URL gói có thể đảo ngược (reversible artifact URLs).
- Nâng cấp môi trường phụ trợ: Cập nhật các bản dựng CPython (3.11.18, 3.12.16, 3.13.18, 3.14.10, 3.15.2, 3.16.0a2), GraalPy 3.13.0 lên build 25.6.5 và cập nhật chứng chỉ gốc Mozilla thông qua `webpki-root-certs` bản 1.0.12.

## Trade-off và hạn chế
- Tính năng dùng proxy index đi kèm URL có thể đảo ngược hiện chỉ ở dạng bản xem trước (preview feature), chưa phải là cấu hình mặc định hoặc hoàn toàn ổn định.
- Việc siết chặt kiểm tra cấu trúc nén ZIP khiến các tệp wheel không chuẩn (vốn có thể được bỏ qua trước đây) bị từ chối trực tiếp, đòi hỏi kho lưu trữ hoặc nguồn đóng gói phải chuẩn hóa lại tệp.
- Cơ chế xác thực lockfile chặt chẽ hơn sẽ làm gián đoạn quy trình CI/CD dùng cờ `--locked` nếu tệp khóa trước đó tồn tại sai lệch về yêu cầu phụ thuộc chưa được cập nhật.
- Mức độ ảnh hưởng chi tiết của lỗ hổng GHSA-vjvj-3m3f-fgmm chưa rõ do tài liệu phát hành không mô tả sâu về vector tấn công.

## Điểm đáng chú ý
- Bản phát hành tập trung vào an toàn chuỗi cung ứng thông qua vá lỗi GHSA-vjvj-3m3f-fgmm và tích hợp chứng thực GitHub Artifact Attestations, cho phép người dùng kiểm tra chữ ký số của các tệp nhị phân tải về qua lệnh `gh attestation verify`.
- Cải thiện trải nghiệm gỡ lỗi của nhà phát triển khi cung cấp lý do cụ thể tại sao `uv.lock` bị từ chối bởi cờ `--locked`.
- Bổ sung trích dẫn học thuật cho mô tả gốc của Minato về thuật toán ISOP trong tài liệu của dự án.

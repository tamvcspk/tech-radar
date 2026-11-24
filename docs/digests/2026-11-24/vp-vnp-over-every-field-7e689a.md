# VP ≠ VNP over Every Field

!!! info "Nguồn"
    Nguồn gốc: <https://github.com/anthropics/formal-math/tree/main/vp-vnp>
    Chất lượng phân tích: fulltext

Kho lưu trữ công bố kết quả chứng minh VP khác VNP trên mọi trường do mô hình Claude của Anthropic tự động tìm ra và hình thức hóa bằng Lean 4.
Toàn bộ bài báo và mã nguồn kiểm chứng do AI tạo ra nhưng chưa có sự rà soát từ các nhà toán học con người.

## Vấn đề

Nghiên cứu tập trung vào bài toán độ phức tạp đại số VP và VNP. Kết quả đưa ra chứng minh rằng mạch tính đa thức chu trình Hamiltonian trên mọi trường, cũng như đa thức permanent trên các trường có đặc số khác 2, đòi hỏi hơn m^(c (log m)^(1/3)) cổng với mọi m đủ lớn (theo nguồn). Điều tương tự cũng áp dụng cho các mạch tính xấp xỉ. Từ đó dẫn đến kết luận VP là tập con thực sự của VNP và VNP không nằm trong bao đóng của VP. Tuy nhiên, theo nguồn công bố, kết quả này không giải quyết bài toán P đối với NP.

## Cách hoạt động

Toàn bộ kết quả và chứng minh được phát hiện bởi một mô hình Claude phục vụ nghiên cứu nội bộ của Anthropic. Hệ thống cung cấp bài báo đầy đủ (paper.pdf) cùng mã nguồn hình thức hóa bằng ngôn ngữ Lean 4:
- Tệp `Statement.lean` định nghĩa các phát biểu và chỉ nhập khẩu thư viện Mathlib.
- Quy trình kiểm thử sử dụng công cụ quản lý Lean (`lake`) để biên dịch và kiểm tra tính hợp lệ của chứng minh với lệnh `lake build`.
- Script `PrintAxioms.lean` kiểm tra để đảm bảo chứng minh chỉ sử dụng các tiên đề chuẩn gồm `propext`, `Classical.choice` và `Quot.sound`.
- Quy trình CI thực hiện kiểm tra sâu hơn thông qua `comparator-check.sh`, đối chiếu các phát biểu với `Challenge.lean` và xác thực lại chứng minh bằng một kernel độc lập thứ hai có tên là `nanoda`.

## Trade-off và hạn chế

- Chưa có sự kiểm chứng của con người: Toàn bộ bài báo và mã kiểm chứng đều do mô hình AI viết, và theo nguồn xác nhận thì chưa từng có nhà toán học con người nào rà soát lại chứng minh này.
- Giới hạn máy móc: Dù Lean kiểm tra tính hợp lệ của các bước suy luận toán học, không có công cụ tự động nào đảm bảo tệp phát biểu mô tả đúng và đủ hoàn toàn ý đồ thực tế.
- Trạng thái dự án: Đây chỉ là một sản phẩm nghiên cứu lưu trữ (research artifact), không được duy trì, bảo trì hay tiếp nhận các đóng góp từ bên ngoài.

## Điểm đáng chú ý

- Chứng minh toán học hoàn toàn do AI đề xuất và chuyển đổi sang dạng toán học hình thức (Lean 4) đi kèm tài liệu PDF chi tiết (trong đó phần chứng minh đầy đủ nằm ở phụ lục).
- Mức độ tin cậy của mã nguồn hình thức được tăng cường thông qua việc chạy kiểm chứng chéo bằng một kernel độc lập (nanoda) thay vì chỉ phụ thuộc vào kernel mặc định của Lean 4.
- Bảng đối chiếu chi tiết giữa các phát biểu đánh số trong bài báo và định lý trong mã Lean 4 được cung cấp ở Phụ lục Q của tài liệu.

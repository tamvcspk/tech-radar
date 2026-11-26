# Holy shit holy shit holy shit holy shit: The magnitude of what’s now happening

!!! info "Nguồn"
    Nguồn gốc: <https://scottaaronson.blog/?p=10379>

    Chất lượng phân tích: fulltext

Các phòng thí nghiệm AI liên tiếp công bố lời giải kèm mã kiểm chứng Lean cho hàng loạt bài toán lý thuyết độ phức tạp và toán học kinh điển.
Sự phát triển này mang lại các bước nhảy vọt về thuật toán nhưng kéo theo thách thức tiếp thu lời giải và rủi ro đe dọa các hệ thống mật mã.

## Vấn đề
Trong nhiều thập kỷ kể từ cuối những năm 1960, các bài toán trung tâm của khoa học máy tính lý thuyết và thuật toán như số mũ nhân ma trận (omega), số cổng tuyến tính cho biến đổi Fourier (FFT), VP ≠ VNP hay Giả thuyết Riemann vẫn là những bí ẩn lớn chưa có lời giải dứt khoát. Cộng đồng nghiên cứu thường chỉ tiến triển rất chậm qua từng manh mối nhỏ giọt, thậm chí nhiều phỏng đoán lâu năm thiếu bằng chứng vững chắc (ví dụ nhận định omega bằng 2).

## Cách hoạt động
Theo nội dung bài viết, các tổ chức như OpenAI và Anthropic ứng dụng AI để tìm ra lời giải cho các bài toán mở lớn. Thay vì phát hành thông cáo báo chí, họ trực tiếp đưa các bài báo và kết quả lên kho lưu trữ GitHub. Tính chính xác của các kết quả này được hỗ trợ và kiểm chứng thông qua các chứng chỉ hình thức hóa bằng ngôn ngữ Lean (Lean certificates). Việc ứng dụng AI hỗ trợ chứng minh cũng dần trở thành tiêu chuẩn trong nghiên cứu, như trường hợp nghiên cứu QIP(2) = PSPACE của Yupan Liu.

## Trade-off và hạn chế
- Khả năng tiếp thu của con người: Các giải pháp do AI tạo ra có thể cần đến nhiều năm để các nhà nghiên cứu con người thực sự hiểu thấu đáo.
- Nghi ngờ và tranh cãi: Vẫn có những phản bác xoay quanh các chi tiết nhỏ, như sự sai khác giữa chứng minh hình thức Lean và chứng minh không hình thức, hoặc các phần mã Lean không được sử dụng.
- Đe dọa hệ thống mật mã: Việc tìm ra các thuật toán chặn trên mới đồng nghĩa với nguy cơ phá vỡ các hệ thống mật mã đang được triển khai thực tế. Dù vậy, theo nguồn, chi tiết kỹ thuật cụ thể về các tác động mật mã này hiện vẫn chưa rõ và chưa được công bố chính thức.
- Tác động rộng hơn: Đặt ra lo ngại về sự khởi đầu của một điểm kỳ dị AI (singularity) vượt ra ngoài khuôn khổ các bài toán thuần túy.

## Điểm đáng chú ý
- Xác định chính xác số mũ nhân ma trận omega là 9/4 (theo nguồn), chứng minh được chặn dưới omega > 2 vốn là thách thức kéo dài từ thời Volker Strassen (cuối thập niên 1960).
- Số lượng cổng tuyến tính cho biến đổi Fourier được giải quyết với cả chặn trên và chặn dưới trùng khớp là N (log N)^(1/2+o(1)) (theo nguồn), vượt qua mốc O(N log N) tồn tại từ thập niên 1960.
- Ghi nhận hàng loạt kết quả lớn được công bố liên tiếp: VP ≠ VNP, kết quả Alpöge/Anthropic cho Giả thuyết Riemann, và tác giả tin rằng chứng minh P ≠ NP đang tới gần.
- Nghiên cứu của Yupan Liu chứng minh QIP(2) = PSPACE với sự trợ giúp của AI được xem là một quy trình ngày càng bình thường hóa trong nghiên cứu độ phức tạp tính toán.

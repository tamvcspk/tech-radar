# Ternary Bonsai 2.5 27B

!!! info "Nguồn"
    Nguồn gốc: <https://prismml.com/news/bonsai-2-5-27b>

    Chất lượng phân tích: fulltext

Ternary Bonsai 2.5 27B là mô hình nén dựa trên Qwen3.8 27B với kích thước 5,9 GB phục vụ các tác vụ lập trình và chạy agent trên thiết bị cá nhân.
Phiên bản này tập trung xử lý lỗi suy nghĩ lan man và vòng lặp lặp lại, đồng thời tối ưu tốc độ gọi công cụ đa bước qua llama.cpp và MLX.

## Vấn đề
Trong các quy trình làm việc dạng agent (agentic workflows), mô hình AI rất nhạy cảm với sự suy giảm chất lượng vì những sai lệch nhỏ có thể tích tụ qua từng lượt gọi công cụ và phá hỏng kết quả cuối cùng. Ở phiên bản trước (Ternary Bonsai 2), mô hình vẫn gặp tình trạng suy nghĩ thừa thãi (excessive thinking) và rơi vào các vòng lặp lặp đi lặp lại. Đồng thời, việc vận hành các trợ lý lập trình hoặc xử lý tài liệu nhạy cảm trên máy cục bộ đòi hỏi mô hình phải có dung lượng bộ nhớ nhỏ mà không làm mất đi năng lực suy luận phức tạp.

## Cách hoạt động
Ternary Bonsai 2.5 27B được xây dựng dựa trên mô hình nền tảng Qwen3.8 27B nhưng nén lại chỉ còn dung lượng 5,9 GB (theo nguồn). Bản nâng cấp này được huấn luyện để duy trì mục tiêu xuyên suốt tương tác dài, thông dịch kết quả trả về từ công cụ và tự điều chỉnh khi một bước thao tác gặp lỗi. Mô hình hoàn thành nhiệm vụ với ít lượt hội thoại hơn và tiêu tốn ít token hơn bản tiền nhiệm. Về môi trường chạy, hệ thống tương thích với GPU NVIDIA và Intel thông qua llama.cpp, cũng như các thiết bị Apple (Mac, iPhone, iPad) thông qua MLX.

## Trade-off và hạn chế
Theo nguồn công bố, mô hình vẫn tồn tại khoảng cách hiệu năng nhất định so với phiên bản gốc full-precision Qwen 3.8 27B, dù khoảng cách này đã được thu hẹp. Bài viết chưa nêu chi tiết cụ thể về mặt toán học hay phương pháp nén tam phân (ternary compression) mà dẫn chiếu sang whitepaper riêng. Ngoài ra, nguồn chưa làm rõ mức tiêu thụ điện năng thực tế cũng như tỷ lệ suy giảm ngữ cảnh khi thực hiện các tác vụ kéo dài vượt ngưỡng tài liệu công bố.

## Điểm đáng chú ý
Theo nguồn, hiệu năng xử lý của mô hình đạt tốc độ rất cao: trên một GPU NVIDIA H100 đơn lẻ, tốc độ sinh đạt 291 tokens/s (khi dùng MTP) và tốc độ xử lý prompt 2.000 token đạt 3.200 tokens/s; trên GPU phổ thông RTX 4090, tốc độ sinh đạt 204 tokens/s (với MTP) và xử lý prompt đạt khoảng 3.060 tokens/s. Mô hình có kích thước nhỏ gọn 5,9 GB giúp chạy trọn vẹn trên phần cứng tiêu dùng và thiết bị di động của Apple. Trọng số mô hình được phát hành công khai theo giấy phép Apache 2.0.

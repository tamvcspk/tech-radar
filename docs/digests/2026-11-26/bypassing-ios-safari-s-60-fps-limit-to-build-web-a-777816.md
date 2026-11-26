# Bypassing iOS Safari's 60 FPS Limit to Build Web Applications That Feel Native

!!! info "Nguồn"
    Nguồn gốc: <https://rida.dev/blog/bypassing-ios-safari-60-fps-limit>

    Chất lượng phân tích: fulltext

Kỹ thuật vượt qua rào cản 60 FPS trên iOS Safari thông qua việc tận dụng luồng compositor của vùng cuộn và cơ chế OffscreenCanvas.
Giải pháp cho phép các ứng dụng web tiếp nhận thao tác và kết xuất đồ họa ở tốc độ 120 Hz tương đương native mà không cần can thiệp cờ nhà phát triển.

## Vấn đề

Trên iOS Safari, WebKit mặc định khóa `requestAnimationFrame` cùng các sự kiện cảm ứng (touch, pointer events) ở mức 60 Hz ngay cả trên màn hình ProMotion 120 Hz, trừ khi người dùng bật cờ phát triển ẩn. Thêm vào đó, theo nguồn, các sự kiện cuộn thông thường chỉ cập nhật từ 5 đến 26 lần mỗi giây trong lúc cuộn theo quán tính (tối đa khoảng 60 lần/giây khi cuộn rất chậm), khiến trải nghiệm web di động trở nên giật và kém mượt mà. Mặt khác, việc kết xuất qua thẻ canvas cũng bị giới hạn trong chu kỳ render 60 Hz của luồng chính, điều vốn được cộng đồng xem là không thể vượt qua nếu không dùng private API hoặc cờ hệ thống.

## Cách hoạt động

Giải pháp gồm hai phần chính: thu nhận tương tác đầu vào tần số cao và kết xuất đầu ra ở 120 FPS.

- **Xử lý tương tác 120 Hz bằng "Controller":** Cơ chế cuộn trình duyệt được xử lý trực tiếp bởi compositor thread độc lập với JavaScript. Bằng cách dùng một vùng cuộn vô hình làm bộ điều khiển và đọc đồng bộ `scrollTop`/`scrollLeft`, tác giả có thể trích xuất quán tính, độ nảy và vị trí chạm tự nhiên. Sau các thử nghiệm thất bại gây hao pin hoặc lỗi chia sẻ tài nguyên, giải pháp hoạt động là dùng `MessageChannel` điều tiết qua `setTimeout` dựa theo tần số quét và khóa pha vsync bằng timestamp của `requestAnimationFrame`. Để giải quyết việc Safari chờ xác nhận IPC (làm rớt mẫu), một vòng lặp `requestAnimationFrame` rỗng được bổ sung để ép xả dữ liệu liên tục. Tiếp đó, một phần tử cuộn vô hình kích hoạt hiệu ứng CSS tăng tốc phần cứng chạy ngầm để kích hoạt ProMotion từ 90 Hz lên đủ 120 Hz. Để khắc phục việc làm tròn số nguyên của tọa độ cuộn, bề mặt cuộn được phóng to theo tỷ lệ điểm ảnh thiết bị (DPR) rồi thu nhỏ khung chứa tương ứng.
- **Kết xuất 120 FPS bằng OffscreenCanvas:** Thay vì vẽ trực tiếp trên luồng DOM chính, tác giả gọi `transferControlToOffscreen` trên phần tử `<canvas>`. WebKit xử lý khung hình đẩy từ `OffscreenCanvas` mà không phải chờ lượt vẽ của luồng chính, mở đường cho việc kết xuất đồ họa (như WebGL shader) đạt 120 FPS từ Web Worker mà không gây quá tải CPU.

## Trade-off và hạn chế

- **Nguy cơ bị vô hiệu hóa:** Tác giả nhấn mạnh không khuyến khích xây dựng lại toàn bộ ứng dụng theo cách này, vì Apple hoàn toàn có quyền thay đổi hành vi của `OffscreenCanvas` trong các bản cập nhật WebKit tương lai mà không vi phạm đặc tả HTML.
- **Độ phức tạp khi dùng toàn màn hình:** Nếu dùng toàn bộ viewport làm controller để đo tọa độ sub-point, lập trình viên buộc phải can thiệp thuộc tính `initial-scale`, điều chỉnh kích thước theo DPR, tắt tính năng tự chỉnh cỡ chữ và tự tính toán safe areas, đồng thời thanh chọn văn bản sẽ bị thu nhỏ lại.
- **Các mẹo lách kỹ thuật:** Cần phối hợp nhiều kỹ thuật phức tạp như duy trì vòng lặp rAF rỗng, chạy vùng cuộn ẩn ngầm để kích hoạt ProMotion, hoặc chuyển đổi màu trong suốt qua CSS scroll-driven animation để tránh bị Safari bóp tốc độ ghi nhận xuống 10 Hz khi thanh địa chỉ co giãn.

## Điểm đáng chú ý

- Theo nguồn công bố qua thử nghiệm quay video 240 FPS (trên thiết bị iPhone 18 Pro được nêu trong bài viết), việc điều khiển bằng cơ chế controller đạt trung bình 118 FPS trong 3 giây kéo, vượt trội hoàn toàn so với mức 60 FPS cố định của các sự kiện pointer thông thường.
- Trong chế độ Tiết kiệm pin (Low Power Mode) – vốn thường hạ trần hiển thị xuống 30 FPS theo nguồn, kỹ thuật này vẫn duy trì được mức 60 FPS.
- Phá vỡ nhận định lâu nay của cộng đồng công nghệ cho rằng canvas trên iOS Safari bắt buộc phải chạy dưới cờ hệ thống mới vượt được 60 FPS, chứng minh khả năng dựng các hiệu ứng phức tạp (như thanh điều hướng Liquid Glass dùng shader) mượt mà như ứng dụng native.

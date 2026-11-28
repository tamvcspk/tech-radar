# Credit card skimming scripts using WebRTC found on popular shopping sites

!!! info "Nguồn"
    Nguồn gốc: <https://www.infohawk.com/news/2026-11-27-black-friday-webrtc-skimmer>

    Chất lượng phân tích: fulltext

Mã độc skimming thẻ thanh toán được phát hiện lạm dụng WebRTC và hạ tầng TURN relay của Cloudflare để che giấu lưu lượng trên các website thương mại điện tử lớn.
Khai thác lỗ hổng chuỗi cung ứng từ script bên thứ ba, cuộc tấn công chỉ kích hoạt trên trang thanh toán của thiết bị di động nhằm tránh các công cụ giám sát thông thường.

## Vấn đề

Trước dịp Black Friday, một đoạn mã skimming thẻ thanh toán đã được chèn vào các cửa hàng trực tuyến của Lascana, Samsonite, American Tourister, Revolve và FWRD. Mục tiêu của mã độc là đánh cắp các trường dữ liệu nhạy cảm gồm số thẻ, ngày hết hạn, mã bảo mật (CVV), cùng thông tin cá nhân như họ tên, địa chỉ, số điện thoại và email ngay khi người dùng nhập liệu, trước cả khi hệ thống cửa hàng xử lý giao dịch. 

Nguyên nhân bắt nguồn từ điểm yếu trong chuỗi cung ứng mã nguồn: các trang web tải script bên thứ ba (pixel tiếp thị Quorum, cấu hình banner đồng thuận cookie Seers qua thẻ ảnh ẩn kích hoạt sự kiện onerror, hoặc tệp trên chính CDN của doanh nghiệp). Các đoạn mã này chạy với toàn quyền như mã nguồn chính, có khả năng đọc/ghi trang và theo dõi bàn phím. Theo nguồn, chưa rõ có bao nhiêu dữ liệu người dùng hay thẻ thanh toán thực tế đã bị thu thập trên tất cả các trang, ngoại trừ trường hợp thẻ thử nghiệm được ghi nhận bị gửi ra ngoài tại Lascana.

## Cách hoạt động

Kỹ thuật tấn công được thiết kế theo 7 bước tuần tự nhằm kết hợp yêu cầu web thông thường với kênh truyền WebRTC:

1. **Khởi tạo:** Mã loader thâm nhập trang web thông qua cấu hình banner cookie, file CDN của nhà bán lẻ, pixel tiếp thị chia sẻ hoặc trực tiếp từ mã HTML của cửa hàng.
2. **Tải script:** Loader kéo tệp `Insds.js` hoặc `gtage.js` từ bucket Amazon S3 (`<brand>-static.s3.amazonaws[.]com`).
3. **Lọc mục tiêu:** Mã độc kiểm tra thiết bị và chỉ kích hoạt trên màn hình cảm ứng hoặc kích thước nhỏ (mobile), đồng thời chỉ chạy trên đường dẫn thanh toán (ví dụ `/checkout` trên Samsonite).
4. **Thiết lập kết nối WebRTC:** Sử dụng các web request thông thường gồm `GET /_cf/ice` để lấy thông tin relay và `POST /_cf/rel` để gửi WebRTC offer tới máy chủ `*.northbridgeads[.]com`.
5. **Trao đổi dữ liệu qua TURN relay:** Toàn bộ quá trình định tuyến sử dụng hạ tầng `turn.cloudflare.com` nhằm che giấu máy chủ đích thực tế của kẻ tấn công.
6. **Nạp và thực thi mã độc:** Mã skimming được truyền thành nhiều phần (chunks) qua WebRTC data channel, sau đó được kiểm tra tính toàn vẹn bằng hàm băm SHA-256 và thực thi qua `eval`.
7. **Tuồn dữ liệu ra ngoài:** Dữ liệu thẻ và thông tin khách hàng bị đánh cắp được đóng gói và gửi ngược lại ra máy chủ ngoại vi thông qua chính WebRTC data channel này.

## Trade-off và hạn chế

- **Phụ thuộc vào tín hiệu HTTP ban đầu:** Dù các bước từ 5 đến 7 truyền qua kênh dữ liệu WebRTC nằm ngoài phạm vi kiểm soát của CSP `connect-src`, bước số 4 vẫn phải dùng request HTTP thông thường để lấy cấu hình ICE và gửi WebRTC offer. Do đó, hạn chế lớn của mã độc là nếu website cấu hình `connect-src` nghiêm ngặt và chỉ cho phép các domain tin cậy, toàn bộ quy trình thiết lập WebRTC sẽ bị chặn đứng.
- **Đánh đổi giữa lẩn trốn và phạm vi tấn công:** Kẻ tấn công chủ đích chỉ nhắm vào thiết bị di động/màn hình cảm ứng trên trang checkout nhằm vượt qua các công cụ quét tự động và đội ngũ kiểm tra trên máy tính để bàn (desktop). Tuy nhiên, chiến lược này đồng nghĩa với việc bỏ qua các luồng thanh toán từ máy tính thông thường, thu hẹp tệp nạn nhân tiềm năng.
- **Độ phức tạp trong vận hành:** Mã độc phải chia nhỏ payload, xác minh mã băm SHA-256 rồi dùng `eval` để thực thi, đòi hỏi hạ tầng TURN trung gian và xử lý nhiều tầng kết nối thay vì gửi dữ liệu qua một endpoint API đơn giản.

## Điểm đáng chú ý

- **Vũ khí hóa WebRTC:** WebRTC vốn phục vụ truyền thông âm thanh/hình ảnh thời gian thực, nay bị lợi dụng làm kênh C2 và đánh cắp dữ liệu vì các công cụ giám sát và luật an ninh mạng thường ít theo dõi sâu kênh truyền dữ liệu này.
- **Lợi dụng TURN relay của bên thứ ba:** Việc định tuyến qua `turn.cloudflare.com` giúp lưu lượng độc hại hòa lẫn vào lưu lượng WebRTC hợp pháp, che đậy địa chỉ IP thực sự của kẻ tấn công.
- **Rủi ro mã thứ ba trên trang nhạy cảm:** Vụ việc phơi bày lỗ hổng kiến trúc phổ biến khi các website nhúng chung pixel tiếp thị và script ngoài vào các trang đăng nhập và thanh toán mà không dùng iframe cô lập.
- **Các dấu hiệu nhận diện (IoC):** Nguồn chỉ ra các thành phần cần rà soát gồm script `Insds.js`, `gtage.js` từ các S3 bucket dạng `<brand>-static`, domain `*.northbridgeads[.]com` với các endpoint `/_cf/ice`, `/_cf/rel`, cùng các chuỗi định danh như `KghRtc`, `rtc-signal-v1` và `quickfetch`.

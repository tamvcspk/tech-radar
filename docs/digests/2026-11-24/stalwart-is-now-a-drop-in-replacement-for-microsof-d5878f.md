# Stalwart is now a drop-in replacement for Microsoft Exchange

!!! info "Nguồn"
    Nguồn gốc: <https://stalw.art/blog/microsoft-exchange-replacement/>
    Chất lượng phân tích: fulltext

Stalwart phiên bản 1.2.0 bổ sung các giao thức của Microsoft Exchange, cho phép thay thế máy chủ thư điện tử mà không làm gián đoạn trải nghiệm người dùng Outlook hiện tại.
Giải pháp mã nguồn mở AGPL này đóng vai trò cầu nối chuyển tiếp giúp bảo đảm chủ quyền dữ liệu, nhưng có những hạn chế nhất định về tính năng cũ và ứng dụng Outlook mới.

## Vấn đề

Microsoft đang dần định hướng người dùng chuyển dịch hoàn toàn lên đám mây Exchange Online. Trên môi trường tự lưu trữ (on-premises), Exchange 2016 và 2019 đã hết hạn hỗ trợ vào ngày 14/10/2025 (chương trình cập nhật mở rộng kết thúc tháng 10/2026 theo nguồn), phiên bản Exchange Server Subscription Edition (SE) không có thêm tính năng mới của đám mây, các API như EWS bắt đầu bị tắt dần và ứng dụng New Outlook hoàn toàn không hỗ trợ máy chủ on-premises. Đối với nhiều tổ chức thuộc khối pháp lý, hành chính công, y tế hay quốc phòng, việc đưa thư điện tử lên đám mây của nhà cung cấp Mỹ làm dấy lên nguy cơ về chủ quyền dữ liệu và phạm vi của luật CLOUD Act. Tuy nhiên, việc rời bỏ Exchange thường vấp phải rào cản lớn từ phía người dùng cuối vốn đã quen thuộc với Outlook và các tính năng như lịch chia sẻ hay ủy quyền; chuyển sang các giao thức chuẩn như IMAP/CalDAV thường buộc phải đổi client hoặc mất đi các tính năng nâng cao.

## Cách hoạt động

Stalwart 1.2.0 hoạt động như một hệ thống thay thế trực tiếp bằng cách hỗ trợ đầy đủ các giao thức mà ứng dụng Exchange sử dụng, chạy chung trên cùng một cổng HTTPS với JMAP và WebUI:
- Triển khai MAPI over HTTP (hỗ trợ cả cached và online mode cho Outlook Classic trên Windows), EWS (phiên bản schema Exchange 2010 SP2 đến 2016), Exchange ActiveSync (bản 14.1 và 16.1 cho thiết bị di động) cùng Autodiscover.
- Dữ liệu được chia sẻ hợp nhất: các giao thức Exchange hoạt động như một cổng kết nối bổ sung vào cùng hệ thống tài khoản; người dùng có thể truy cập đồng thời qua Outlook, ứng dụng di động, JMAP hoặc IMAP/CalDAV/CardDAV.
- Các quy tắc hòm thư (rules) tạo từ Outlook được lưu trên máy chủ và biên dịch thành Sieve để thực thi ngay khi thư đến, áp dụng cho mọi client khác.
- Quá trình di chuyển dữ liệu được thực hiện bởi công cụ Vandelay: chuyển thư, lịch, danh bạ từ Exchange on-premises (qua EWS) hoặc Microsoft 365 (qua Microsoft Graph hoặc EWS) sang Stalwart qua JMAP.

## Trade-off và hạn chế

- Thiếu vắng một số tính năng: Stalwart không cung cấp thư mục công cộng (public folders), hòm thư lưu trữ (archive mailboxes), tính năng quản lý thiết bị di động (MDM), không hỗ trợ RPC over HTTP (dành cho Outlook 2010 trở về trước), cũng như không hỗ trợ xác thực bằng Kerberos hay NTLM (chỉ hỗ trợ mật khẩu, app password hoặc OAuth).
- Không tương thích với New Outlook và ứng dụng Outlook di động: Phiên bản New Outlook trên Windows và Outlook trên iOS/Android định tuyến toàn bộ kết nối, tài khoản và mật khẩu thông qua hạ tầng đám mây của Microsoft, đi ngược lại mục tiêu tự chủ dữ liệu. Stalwart khuyến cáo người dùng tiếp tục dùng Outlook Classic hoặc ứng dụng gốc trên thiết bị di động qua ActiveSync.
- Gia tăng kích thước mã nguồn: Tính năng tương thích Exchange bổ sung khoảng 200.000 dòng code vào hệ thống (theo nguồn), dù đã được đóng gói độc lập.
- Giải pháp mang tính chất cầu nối: Do các giao thức như EWS và client Outlook Classic đang tiến gần đến vòng đời kết thúc, việc hỗ trợ Exchange chủ yếu phục vụ chuyển tiếp tạm thời nhằm giúp tổ chức có thời gian chuyển dịch dần sang các chuẩn mở như JMAP.

## Điểm đáng chú ý

- Toàn bộ tính năng tương thích Exchange nằm trong phiên bản mã nguồn mở Community edition phát hành theo giấy phép AGPL.
- Thiết kế kiến trúc dạng mô-đun: Mã nguồn phục vụ Exchange được tách biệt trong các crate riêng dưới cờ tính năng Cargo `exchange` và mặc định tắt trong cấu hình; người dùng có thể biên dịch loại bỏ hoàn toàn mà không để lại mã thừa trong tệp nhị phân.
- Không làm ô nhiễm dữ liệu chuẩn: Các thuộc tính đặc thù của Outlook được lưu riêng dưới dạng metadata bằng phần mở rộng JMAP Object Metadata và chỉ được ghi khi có client Exchange kết nối. Việc xóa metadata này sẽ loại bỏ hoàn toàn dấu vết Exchange mà không làm hỏng dữ liệu email chuẩn.
- Bổ sung nhiều tính năng hữu ích khác trong bản 1.2.0: Quy tắc thư máy chủ (Mail rules biên dịch sang Sieve), hỗ trợ xác nhận đã đọc Read receipts (theo chuẩn RFC 8098 và RFC 9007) và cấu hình giờ làm việc (Working hours) phục vụ tra cứu lịch bận/rảnh.

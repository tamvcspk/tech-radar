# Kagi Mail (public beta)

!!! info "Nguồn"
    Nguồn gốc: <https://blog.kagi.com/kagi-mail-public-beta>
    Chất lượng phân tích: fulltext

Kagi ra mắt phiên bản thử nghiệm công khai Kagi Mail cung cấp dịch vụ email và lịch riêng tư dựa trên các tiêu chuẩn mở như JMAP và IMAP.
Dịch vụ tích hợp các tính năng AI hỗ trợ xử lý hộp thư, cam kết không quảng cáo hay theo dõi với giá 99 USD mỗi năm hoặc đi kèm gói Ultimate.

## Vấn đề

Nhiều người dùng mong muốn chuyển đổi toàn bộ đời sống số ra khỏi hệ sinh thái của các hãng công nghệ lớn như Google để bảo vệ quyền riêng tư. Dù đã thay đổi trình duyệt hoặc công cụ tìm kiếm, hộp thư điện tử thường là mắt xích cuối cùng còn bị ràng buộc. Tuy nhiên, phần lớn các dịch vụ email phổ biến hiện nay đi kèm cơ chế giám sát người dùng, gắn mã theo dõi, hiển thị quảng cáo hoặc dùng dữ liệu cá nhân làm tập dữ liệu huấn luyện, khiến nhu cầu về một hòm thư an toàn, nhanh chóng, không khóa chặt người dùng (vendor lock-in) trở nên cấp thiết.

## Cách hoạt động

Kagi xây dựng một giải pháp hoàn chỉnh từ hạ tầng máy chủ đến ứng dụng người dùng, dựa trên các tiêu chuẩn mở:
- **Hạ tầng và giao thức:** Chạy trên máy chủ mã nguồn mở Stalwart, hỗ trợ đầy đủ các tiêu chuẩn IMAP, JMAP và CalDAV. Nhờ đó, người dùng có thể sử dụng ứng dụng của Kagi hoặc bất kỳ ứng dụng bên thứ ba tương thích nào như Apple Mail hay Thunderbird.
- **Thông số cơ bản:** Cung cấp địa chỉ đuôi `@kagimail.com`, không giới hạn bí danh (aliases), không giới hạn tên miền riêng (custom domains), tích hợp ứng dụng Lịch và cấp 50 GB dung lượng lưu trữ.
- **Quyền riêng tư mặc định:** Chặn hoặc dùng proxy đối với pixel theo dõi và hình ảnh từ xa nhằm tránh lộ thời gian, vị trí mở thư; cơ chế lọc người gửi (sender screening) giữ các liên hệ mới ở trạng thái chờ duyệt; hiển thị cảnh báo lừa đảo với nguồn gửi đáng ngờ và hiện logo BIMI cho nguồn gửi đã xác minh.
- **Trí tuệ nhân tạo (AI):** Cho phép người dùng tóm tắt quy tắc lọc thư bằng ngôn ngữ tự nhiên, phân loại hộp thư nổi bật (Inbox Highlights), truy vấn thông tin trong thư và văn bản trong ảnh/PDF quét bằng ngôn ngữ tự nhiên. AI có thể tắt hoàn toàn chỉ bằng một nút gạt; tính năng AI sử dụng chung hạn ngạch (allowance) từ tài khoản Kagi sẵn có. Dịch vụ cũng tích hợp sẵn Kagi Translate và kiểm tra lỗi chính tả khi viết thư.
- **Dành cho lập trình viên và người dùng nâng cao:** Hỗ trợ phím tắt, bảng lệnh (command palette), lọc nâng cao theo luật thông qua Sieve (không dùng AI), và cung cấp máy chủ MCP (Model Context Protocol) với quyền đọc hộp thư.

## Trade-off và hạn chế

- **Thiếu hụt tính năng cơ bản:** Hiện tại phiên bản beta chưa có danh bạ (Contacts/Address book), dự kiến đến quý 1 năm 2027 mới ra mắt. Tích hợp toàn diện với Kagi Assistant cũng phải chờ đến quý 1 năm 2027.
- **Chưa có ứng dụng di động gốc (native mobile apps):** Lộ trình đặt mục tiêu phát hành vào quý 3 năm 2027. Hiện tại trên di động chỉ có thể dùng ứng dụng web hoặc ứng dụng bên thứ ba hỗ trợ IMAP/JMAP.
- **Hộp thư dùng chung (shared mailboxes):** Đang trong trạng thái "sắp ra mắt" (coming soon) chứ chưa có sẵn ở thời điểm hiện tại.
- **Chi phí dịch vụ:** Dịch vụ có giá 99 USD/năm (cộng thuế) sau 60 ngày dùng thử miễn phí, hoặc bắt buộc phải đăng ký gói trả phí Kagi Ultimate, không có gói miễn phí vĩnh viễn.

## Điểm đáng chú ý

- **Chính sách không khóa người dùng (No lock-in):** Khi rời dịch vụ, người dùng được giữ quyền truy cập hòm thư trong vòng 6 tháng: 60 ngày đầu vẫn có thể gửi và nhận thư bình thường, 4 tháng tiếp theo duy trì quyền đọc và xuất dữ liệu thông qua thao tác xuất một lần nhấp (one-click export) hoặc các giao thức chuẩn.
- **Bảo mật và tích hợp doanh nghiệp:** Hỗ trợ cơ chế đăng nhập mạng xã hội hoặc nhà cung cấp danh tính riêng của tổ chức qua chuẩn OIDC, chia sẻ địa chỉ email tên miền chung cho nhóm hoặc gia đình.
- **Hỗ trợ giao thức MCP:** Việc tích hợp MCP server cấp quyền đọc thư mở ra khả năng tự động hóa và kết nối hộp thư trực tiếp vào các luồng xử lý AI bên ngoài theo chuẩn mở.

# Ladybird is now in alpha

!!! info "Nguồn"
    Nguồn gốc: <https://ladybird.org/posts/alpha/>
    Chất lượng phân tích: fulltext

Ladybird chính thức ra mắt phiên bản thử nghiệm alpha trên hai nền tảng macOS và Linux với engine tự xây dựng từ đầu thay vì phân nhánh.
Bản phát hành hướng tới việc phát hiện lỗi tương thích và củng cố bảo mật thông qua cập nhật tự động, hỗ trợ WebDriver cùng Firefox DevTools.

## Vấn đề

Trước đây, người dùng và lập trình viên muốn theo dõi sự tiến triển của Ladybird bắt buộc phải tự biên dịch trình duyệt từ mã nguồn. Bên cạnh đó, việc xây dựng một engine trình duyệt hoàn toàn mới từ đầu đòi hỏi phải đưa sản phẩm ra môi trường thực tế để người dùng kiểm thử độ tương thích web, báo cáo lỗi hiển thị và tìm kiếm các lỗ hổng bảo mật nhằm hoàn thiện hệ thống.

## Cách hoạt động

Ladybird vận hành trên một engine hoàn toàn mới do đội ngũ tự xây dựng từ đầu, không phải là bản phân nhánh (fork) từ bất kỳ engine nào khác, kết hợp với phần giao diện duyệt web cơ bản nhưng đầy đủ chức năng. Phiên bản alpha này được triển khai theo mô hình kênh phát hành liên tục (rolling channel) với các bản cập nhật tự động thường xuyên. Trình duyệt tích hợp sẵn cơ chế báo cáo lỗi trang web trực tiếp từ giao diện. Khi gặp sự cố sập (crash), người dùng có thể xem trước nội dung báo cáo sự cố để tự quyết định có gửi về cho đội ngũ phát triển hay không. Đối với các nhà phát triển web, trình duyệt hỗ trợ WebDriver để phục vụ kiểm thử tự động và tích hợp giao thức Firefox DevTools protocol.

## Trade-off và hạn chế

Do đang ở giai đoạn alpha, Ladybird vẫn tồn tại nhiều hạn chế kỹ thuật: một số trang web sẽ không thể hoạt động bình thường và trình duyệt có thể bị sập trong quá trình sử dụng. Về mặt an ninh mạng, đội ngũ phát triển tuyên bố chưa đưa ra bất kỳ cam kết nào về bảo mật ở thời điểm hiện tại và chấp nhận việc bị tấn công để tìm cách vá lỗi. Ngoài ra, giao diện và các tính năng bên ngoài engine vẫn còn ở mức khiêm tốn. Về nền tảng hỗ trợ, bản alpha hiện chỉ có thể tải về cho macOS và Linux, các hệ điều hành khác theo nguồn chưa được đề cập rõ.

## Điểm đáng chú ý

Điểm nổi bật nhất là việc Ladybird sở hữu engine độc lập mới hoàn toàn chứ không dựa vào các giải pháp có sẵn. Trình duyệt cũng hỗ trợ các tiêu chuẩn phát triển quen thuộc như WebDriver và Firefox DevTools, giúp lập trình viên dễ dàng thử nghiệm website của mình. Hơn nữa, việc cho phép người dùng đọc và kiểm soát báo cáo sự cố trước khi gửi thể hiện sự minh bạch trong việc thu thập dữ liệu lỗi.

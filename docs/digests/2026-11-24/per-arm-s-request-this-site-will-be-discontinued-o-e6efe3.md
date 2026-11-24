# Per Arm's request, this site will be discontinued on 4 December 2026 :(

!!! info "Nguồn"
    Nguồn gốc: <https://arm.jonpalmisc.com/>
    Chất lượng phân tích: fulltext

Trang tra cứu tài liệu AArch64 của Jon nhận yêu cầu gỡ bỏ từ phía Arm và sẽ dừng hoạt động vào ngày 4 tháng 12 năm 2026 theo nguồn.
Nền tảng này cung cấp tài liệu tra cứu tập lệnh và thanh ghi hệ thống cho Armv8-A và Armv9-A với tính năng tìm kiếm dựa trên WebAssembly.

## Vấn đề
Trang web cung cấp tài liệu kỹ thuật của Jon nhận thông báo từ phía luật sư của Arm yêu cầu phải gỡ bỏ trang hoặc sẽ phải đối mặt với hành động pháp lý. Vì lý do này, trang web được ấn định sẽ ngừng hoạt động vào ngày 4 tháng 12 năm 2026 (theo nguồn).

## Cách hoạt động
Nền tảng đóng vai trò là tài liệu tham khảo cho tập lệnh AArch64 cùng các thanh ghi hệ thống được định nghĩa bởi kiến trúc Armv8-A và Armv9-A. Người dùng có thể tra cứu thông tin thông qua ô tìm kiếm ở đầu mỗi trang hoặc duyệt danh sách thủ công. Chức năng tìm kiếm này được xử lý bằng cách sử dụng WebAssembly ngay trên trình duyệt.

## Trade-off và hạn chế
Tính năng tìm kiếm trên trang phụ thuộc chặt chẽ vào WebAssembly; nếu trình duyệt của người dùng không hỗ trợ hoặc tính năng này bị vô hiệu hóa (chẳng hạn khi bật Lockdown Mode của Apple), thanh tìm kiếm sẽ không hoạt động và chỉ hiển thị một dòng thông báo. Ngoài ra, việc đóng cửa trang web trong tương lai đặt ra nguy cơ làm hỏng các liên kết tham chiếu kỹ thuật, dù tác giả đang tìm giải pháp duy trì hoạt động cho các bookmark và liên kết này.

## Điểm đáng chú ý
Tác giả cho biết trang web đã phục vụ nhiều người dùng trong nhiều năm, trong đó có cả các nhân sự làm việc tại chính Arm. Thời hạn chấm dứt hoạt động được đưa ra là ngày 4 tháng 12 năm 2026 (theo nguồn), và hiện chưa rõ các giải pháp kỹ thuật cụ thể mà tác giả sẽ áp dụng để duy trì khả năng truy cập của các liên kết sau thời điểm này.

# Nextcloud Office Desktop app

!!! info "Nguồn"
    Nguồn gốc: <https://nextcloud.com/blog/euro-office-comes-to-your-desktop-with-the-nextcloud-office-desktop-app/>

    Chất lượng phân tích: fulltext

Nextcloud ra mắt ứng dụng Nextcloud Office Desktop dựa trên nền tảng Euro-Office hỗ trợ biên tập tài liệu và làm việc ngoại tuyến.
Phần mềm cho phép kết nối nhiều máy chủ Nextcloud để cộng tác thời gian thực, quản lý phông chữ cục bộ và ký số tài liệu.

## Vấn đề
Người dùng các ứng dụng văn phòng dựa trên web thường gặp khó khăn khi mất kết nối mạng hoặc khi hệ thống trực tuyến gặp sự cố gián đoạn. Bên cạnh đó, phiên bản làm việc trên trình duyệt gặp giới hạn trong việc truy cập trực tiếp các phông chữ cài sẵn trên hệ điều hành cục bộ, cũng như hạn chế khả năng ký số trực tiếp trên tài liệu lưu trữ nội bộ.

## Cách hoạt động
Nextcloud Office Desktop app vận hành trên nền tảng Euro-Office, cung cấp các trình chỉnh sửa cho văn bản, bảng tính, bản trình chiếu và tệp PDF. Phần mềm hỗ trợ tương thích với các định dạng tệp Microsoft Office (DOCX, XLSX, PPTX) và định dạng mở (ODT, ODS, ODP).

Người dùng có thể làm việc ngoại tuyến với tệp trên máy tính. Để làm việc trực tuyến và cộng tác thời gian thực, người dùng kết nối bằng cách nhập URL của phiên bản Nextcloud và đăng nhập thông tin tài khoản tại mục Clouds. Ứng dụng hỗ trợ kết nối đồng thời nhiều máy chủ Nextcloud khác nhau. Về mặt đồ họa và bảo mật, phần mềm cho phép gọi trực tiếp các phông chữ cài trên máy (như phông mặc định của hệ điều hành), ký số tài liệu qua thẻ Protection (yêu cầu chứng thư số), thiết lập mật khẩu và phân quyền (chỉ bình luận, điền biểu mẫu hoặc chỉ sửa đổi có theo dõi).

## Trade-off và hạn chế
Khi sử dụng phông chữ cục bộ trên thiết bị, nếu những người cộng tác khác không cài đặt phông chữ tương ứng, phiên bản tài liệu của họ sẽ bị chuyển sang phông chữ thay thế (fallback font). Tính năng ký số đòi hỏi phải có sẵn chứng thư số từ bộ phận CNTT hoặc các nhà cung cấp được phê duyệt, không thể tự phát hành trực tiếp. Về khả năng tương thích nền tảng, phiên bản macOS theo nguồn chỉ hỗ trợ Apple Silicon (hỗ trợ máy Mac dùng chip Intel chưa rõ). Ngoài ra, tài liệu nguồn chưa nêu rõ cơ chế xử lý xung đột dữ liệu khi chỉnh sửa ngoại tuyến và kết nối lại máy chủ.

## Điểm đáng chú ý
Ứng dụng là phần mềm mã nguồn mở phát hành theo giấy phép AGPL v3, cho phép người dùng tự biên dịch từ mã nguồn hoặc tải bản cài đặt định dạng .deb, .rpm trên Linux, bộ cài cho Windows (hỗ trợ cả x64 và ARM64) và macOS. Ứng dụng là sản phẩm đi kèm bản phát hành Nextcloud Hub 26 Summer, hướng đến quyền tự chủ kỹ thuật số với nền tảng Euro-Office được phát triển và quản trị tại châu Âu.

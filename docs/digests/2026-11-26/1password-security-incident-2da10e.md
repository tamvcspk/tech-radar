# 1Password Security Incident

!!! info "Nguồn"
    Nguồn gốc: <https://1password.com/blog/update-on-nov-2026-security-incident>

    Chất lượng phân tích: fulltext

1Password ghi nhận sự cố xâm nhập hệ thống backend và CI/CD thông qua tài khoản GitHub doanh nghiệp của một nhân viên, làm lộ mã nguồn và một số dữ liệu quản trị khách hàng.
Dữ liệu két mã hóa và nội dung lưu trữ của người dùng hoàn toàn không bị ảnh hưởng do kiến trúc bảo mật phân tầng không lưu giữ mật khẩu hay khóa bí mật trên máy chủ.

## Vấn đề

Kẻ tấn công đã chiếm quyền truy cập vào tài khoản GitHub doanh nghiệp của một nhân viên thuộc 1Password. Từ tài khoản này, đối tượng đã sao chép mã nguồn từ các kho riêng tư, truy cập vào hệ thống CI/CD (nơi chứa các secret liên quan đến hạ tầng) và đẩy mã độc vào các dịch vụ backend. Hệ quả là mã độc đã trích xuất và tải xuống dữ liệu quản trị của một tập hợp con người dùng, bao gồm: tên, địa chỉ email, định danh tài khoản, thời gian tạo và đăng nhập lần cuối, public key, các tham số giao thức SRP (Secure Remote Password), một số token trong liên kết gửi qua email và siêu dữ liệu cấu trúc nội bộ. Nội dung két mật khẩu (vault) của khách hàng không bị truy cập hay can thiệp.

## Cách hoạt động

Sau khi có quyền truy cập GitHub, kẻ tấn công can thiệp trực tiếp vào mã nguồn backend để tải các bản ghi quản trị. Dù dữ liệu tài khoản bị lộ, hệ thống áp dụng cơ chế xác thực nhiều lớp: các token gửi qua email dùng cho việc cấp phát (provisioning qua SCIM Bridge hoặc Hosted Provisioning) và khôi phục tài khoản không thể sử dụng độc lập. Để hoàn tất quy trình, token bắt buộc phải đi kèm với phiên đăng nhập SSO hoặc một mã xác thực phụ gửi tới email của người dùng. Về phía dữ liệu nhạy cảm nhất, 1Password không lưu mật khẩu tài khoản hay Secret Key; dữ liệu két mật khẩu được mã hóa bằng các khóa do người dùng nắm giữ nên kẻ tấn công không thể đọc được nội dung dù đã xâm nhập thành công vào backend.

## Trade-off và hạn chế

- Token phục hồi và cấp phát tài khoản nằm trong vùng dữ liệu backend bị trích xuất, tạo ra nguy cơ nếu cơ chế mã phụ đi kèm quá yếu; theo nguồn, hệ thống trước đó sử dụng mã 6 chữ số vốn có nguy cơ bị tấn công vét cạn (brute-force) cao hơn so với mã 10 ký tự chữ-số mới cập nhật.
- Hệ thống kiểm soát đẩy mã và phân quyền CI/CD chưa ngăn chặn triệt để hành vi đưa mã độc vào backend khi tài khoản nhân viên bị xâm phạm.
- Cơ chế và nguyên nhân ban đầu dẫn đến việc tài khoản GitHub của nhân viên bị chiếm quyền chưa rõ theo nguồn công bố.

## Điểm đáng chú ý

- Kiến trúc Zero-Knowledge phát huy tác dụng: Ngay cả khi mã nguồn, môi trường CI/CD và cơ sở dữ liệu quản trị bị xâm nhập, kẻ tấn công vẫn không thể giải mã các két bảo mật của khách hàng.
- Các tham số SRP và public key bị lộ được thiết kế công khai hoặc phi định danh bảo mật, không thể dùng độc lập để chiếm đoạt tài khoản.
- Biện pháp khắc phục kỹ thuật được triển khai gồm: vô hiệu hóa tài khoản bị ảnh hưởng, xoay vòng toàn bộ thông tin xác thực nội bộ có nguy cơ bị lộ, siết chặt kiểm soát endpoint/CI/CD/GitHub, tăng độ dài mã xác thực trong email từ 6 chữ số lên 10 ký tự chữ và số (theo nguồn), đồng thời thuê chuyên gia an ninh mạng độc lập kiểm tra lại toàn bộ quy trình xử lý.

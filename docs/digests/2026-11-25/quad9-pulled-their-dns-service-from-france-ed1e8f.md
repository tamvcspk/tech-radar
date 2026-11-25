# Quad9 pulled their DNS service from France

!!! info "Nguồn"
    Nguồn gốc: <https://quad9.net/news/blog/quad9-service-deactivation-in-france/>

    Chất lượng phân tích: fulltext

Quad9 ngừng cung cấp dịch vụ phân giải DNS tại Pháp do phán quyết tòa án buộc chặn các trang vi phạm bản quyền thể thao theo yêu cầu của beIN.
Thay vì can thiệp lọc nội dung tên miền, tổ chức này chọn từ chối toàn bộ truy vấn từ Pháp dựa trên GeoIP dù chấp nhận các sai số kỹ thuật.

## Vấn đề

Quad9 đối mặt với các yêu cầu pháp lý tại Pháp từ đơn vị nắm giữ bản quyền thể thao beIN, đòi hỏi nhà cung cấp này phải chặn các tên miền phát trực tuyến lậu. Phán quyết của tòa án giữ nguyên yêu cầu này và Quad9 đứng trước các khoản phạt vì không tuân thủ. Về mặt kỹ thuật và nguyên tắc, Quad9 phản đối việc biến các máy chủ đệ quy DNS (recursive DNS resolver) thành công cụ thực thi kiểm duyệt nội dung cho bên thứ ba, vì giải pháp này không tác động đến máy chủ gốc và bất kỳ ai cũng có thể tự thiết lập resolver riêng. Do không chấp nhận thỏa hiệp nguyên tắc cốt lõi là chỉ chặn rủi ro an ninh mạng mà không chặn nội dung, Quad9 buộc phải rút dịch vụ khỏi Pháp để vừa tuân thủ phán quyết vừa duy trì tôn chỉ hoạt động.

## Cách hoạt động

Theo nguồn, vào lúc 09:00 giờ CET ngày 24/11/2026, Quad9 tiến hành từ chối mọi truy vấn DNS gửi tới bất kỳ địa chỉ dịch vụ nào bắt nguồn từ Pháp, khiến việc phân giải DNS không thể thực hiện. Do không lưu trữ thông tin người dùng, Quad9 buộc phải dùng phương pháp định vị GeoIP để nhận diện lưu lượng từ quốc gia này. Tổ chức từ chối sử dụng cơ sở dữ liệu GeoIP để lọc cục bộ danh sách tên miền lậu, vì điều đó sẽ công nhận DNS là công cụ hạn chế nội dung và có nguy cơ mở rộng việc áp dụng luật pháp Pháp sang các quốc gia khác. Thay vào đó, bộ lọc GeoIP được áp dụng cho toàn bộ kết nối nhằm ngừng phục vụ hoàn toàn người dùng trong phạm vi quyền hạn của Pháp.

## Trade-off và hạn chế

- Sai số phân loại lớn: Phương pháp định vị GeoIP bộc lộ hạn chế cố hữu, tạo ra cả tình trạng chặn quá mức (overblocking - chặn nhầm truy vấn không thuộc Pháp) và chặn thiếu (underblocking - vẫn xử lý truy vấn của người dùng ở Pháp). Nguyên nhân là do dữ liệu định vị IP thường xuyên thiếu chính xác, IP bị mua bán, mạng di động và mạng diện rộng doanh nghiệp hoạt động xuyên biên giới, hoặc lưu lượng đi qua VPN và proxy. Mức độ thiếu chính xác cụ thể là bao nhiêu thì chưa rõ do Quad9 không thể đo lường.
- Tác động tiêu cực tới người dùng: Người dùng tại Pháp không nắm được thông tin sẽ bị mất kết nối DNS đột ngột. Khi phải chuyển sang dịch vụ phân giải khác, họ mất đi lớp bảo vệ trước phần mềm độc hại của Quad9 và có nguy cơ phải dùng các resolver có chính sách bảo mật kém hơn.
- Phương án tiêu cực nhất: Quad9 thừa nhận việc ngừng toàn bộ dịch vụ là một kết quả tồi tệ, chấp nhận hy sinh sự ổn định ngắn hạn để bảo vệ tính toàn vẹn của hệ thống DNS dài hạn.

## Điểm đáng chú ý

- Phân định rõ giữa an ninh mạng và can thiệp nội dung: Hệ thống của Quad9 lọc các mối đe dọa mạng (mã độc) trên địa chỉ 9.9.9.9 dựa trên đối tác tình báo nguy cơ (và có quyền can thiệp sửa đổi chủ quan nếu đối tác phân loại sai), đồng thời duy trì dải IP 9.9.9.10 mở hoàn toàn không áp dụng bất kỳ bộ lọc nào. Yêu cầu của tòa án Pháp ép buộc can thiệp lên mọi địa chỉ dịch vụ, phá vỡ cấu trúc và cam kết vận hành này.
- Nguy cơ phân mảnh Internet: Quad9 cảnh báo tiền lệ buộc DNS resolver chặn nội dung sẽ dẫn đến sự leo thang kiểm duyệt, mở rộng từ vi phạm bản quyền sang các phạm vi khác như mạng xã hội, ứng dụng nhắn tin, lý do đạo đức, tôn giáo hoặc chính trị.
- Tiền lệ pháp lý: Đây là cuộc chiến pháp lý thứ hai Quad9 phải đối mặt liên quan đến tính toàn vẹn của DNS; trước đó họ đã giữ vững lập trường và giành chiến thắng trong một vụ kiện tương tự tại Đức.

# The need for a formally verifiable mainstream programming language

!!! info "Nguồn"
    Nguồn gốc: <https://blainehansen.me/post/mainstream-verifiable-language/>

    Chất lượng phân tích: fulltext

Sự phát triển của LLM đang làm trầm trọng thêm khủng hoảng chất lượng phần mềm, đòi hỏi ngành lập trình phải phổ cập phương pháp kiểm chứng hình thức thay vì chỉ phụ thuộc vào giới nghiên cứu hàn lâm.
Dự án Magmide đề xuất giải pháp tiếp cận từ dưới lên bằng một ngôn ngữ biên dịch sang WebAssembly GC, đơn giản hóa hệ thống kiểu kiểu Rust và tích hợp dần công cụ chứng minh như SMT và Lean.

## Vấn đề
Chất lượng kỹ thuật phần mềm đang suy giảm nhanh chóng do các quy trình viết mã cẩu thả vốn có bị đẩy nhanh tốc độ bởi các mô hình ngôn ngữ lớn (LLM). Tác giả cho rằng cách duy nhất để giải quyết là ứng dụng kiểm chứng hình thức (formal verification) trên toàn bộ ngăn xếp phần mềm, kiểm chứng lại những gì có thể và viết lại phần còn lại.

Tuy nhiên, các công cụ kiểm chứng hiện nay gặp vấn đề nghiêm trọng về khả năng tiếp cận và tính dễ hiểu, dẫn đến việc không tạo ra được ảnh hưởng văn hóa trong giới kỹ sư công nghiệp. Việc kỳ vọng LLM tự động tạo mã được kiểm chứng hoàn chỉnh mà con người không cần hiểu là không khả thi. Dẫn lời Leonardo de Moura, nguồn nhấn mạnh rằng dù công cụ chứng minh bảo đảm tính toán học đúng đắn, con người vẫn bắt buộc phải đọc và xác nhận các phát biểu định lý để bảo đảm chúng phản ánh đúng mục tiêu thiết kế.

## Cách hoạt động
Thay vì tiếp cận theo hướng "từ trên xuống" (bắt đầu từ hệ thống toán học mạnh nhất rồi tìm cách làm nó dễ dùng hơn), tác giả định hướng dự án Magmide tiếp cận "từ dưới lên" (bottom-up) để đáp ứng đúng nhu cầu thực tế của kỹ sư:
- Biên dịch mã nguồn sang WebAssembly thông qua các tính năng Garbage Collection (Wasm GC).
- Sử dụng hệ thống kiểu lấy cảm hứng từ Rust nhưng loại bỏ sự phức tạp của cơ chế borrow-checker.
- Khởi đầu với Liquid Types vận hành bởi bộ giải SMT và Flow Effects để người dùng dễ học hơn. Tác giả liên hệ mô hình Flow Effects với cách Deno kiểm soát quyền khi thực thi để tăng mức độ an toàn.
- Theo thời gian, dự án dự định tích hợp Lean làm tầng chứng minh (proof layer) và ứng dụng mô hình logic phân tách (separation logic) như Iris để bootstrap cũng như tự kiểm chứng quá trình triển khai của chính ngôn ngữ.

## Trade-off và hạn chế
- Kế hoạch ban đầu của tác giả bị phá sản vì quá tham vọng: việc tự viết một hệ thống hỗ trợ chứng minh (proof assistant) mới và phát triển ngôn ngữ ở mức assembly là cực kỳ phức tạp và không cần thiết để thuyết phục kỹ sư sử dụng.
- Thiếu mô hình kinh doanh bền vững: tác giả từng theo đuổi dự án như một startup và nộp đơn xin tài trợ SBIR, nhưng sau đó nhận thấy việc thương mại hóa là gượng ép và dự án phù hợp nhất dưới dạng một hàng hóa công cộng thuần túy (public good).
- Việc chuyển sang Wasm GC giúp bỏ borrow-checker nhưng trade-off về khả năng kiểm chứng sâu xuống mức kim loại (bare-metal) hoặc hiệu năng cấp thấp như thiết kế assembly ban đầu chưa rõ đã được giải quyết trọn vẹn hay chưa.
- Toàn bộ thiết kế mới của Magmide hiện tại mới dừng ở mức tầm nhìn và lộ trình sau quá trình đúc rút kinh nghiệm; mức độ hoàn thiện của việc tích hợp Lean hay Iris vào hệ thống vẫn chưa rõ ràng trong văn bản nguồn.

## Điểm đáng chú ý
- Kiểm chứng an toàn không thể phụ thuộc vào một nhóm thiểu số các nhà nghiên cứu hình thức; toàn bộ nền kỹ thuật phần mềm phải thay đổi văn hóa và yêu cầu mã nguồn làm ra tối thiểu phải chứng minh được là an toàn.
- Mã nguồn có thể kiểm chứng cần phải chạy được ở mọi môi trường, từ trình duyệt web cho đến các hệ thống nhúng.
- Lập trình viên có thể tận dụng LLM để tăng tốc công việc, nhưng không thể thụ động chờ đợi một trí tuệ siêu nhân tạo (ASI) giải quyết mọi sai lầm nếu bản thân kỹ sư không nắm được các thuộc tính an toàn cơ bản của hệ thống.

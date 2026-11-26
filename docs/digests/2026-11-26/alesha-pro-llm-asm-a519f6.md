# alesha-pro/llm.asm

!!! info "Nguồn"
    Nguồn gốc: <https://github.com/alesha-pro/llm.asm>

    Chất lượng phân tích: readme

Dự án llm.asm triển khai các hệ thống LLM hoàn chỉnh hoàn toàn bằng 100% hợp ngữ x86-64 NASM mà không phụ thuộc vào thư viện ngoài.
Bài viết phân tích kỹ thuật dựa trên tài liệu README của kho lưu trữ để làm rõ kiến trúc thực thi, hiệu năng và các hạn chế cố hữu.

## Vấn đề

Phần lớn các công cụ chạy và huấn luyện mô hình ngôn ngữ lớn (LLM) hiện nay phụ thuộc vào ngăn xếp phần mềm nhiều tầng: thư viện runtime C/C++, Rust, libc, libm, các framework tính toán nặng nề và hệ điều hành tiêu chuẩn. Điều này làm tăng đáng kể kích thước tệp thực thi, kéo theo độ trễ khởi động, chi phí trừu tượng hóa và giảm tính tất định (determinism) khi tính toán trực tiếp trên phần cứng x86-64.

## Cách hoạt động

Theo thông tin từ README của dự án, toàn bộ hệ thống được hiện thực hóa qua 17.252 dòng lệnh hợp ngữ NASM thuần túy (không sử dụng C, C++, Rust hay libc), biên dịch bằng `nasm` và liên kết trực tiếp bằng `ld`. Dự án được chia làm ba thành phần chính:

- **Suy luận Qwen3-0.6B (`01-qwen3-inference/`)**: Tệp nhị phân tĩnh ELF trên Linux (kích thước theo nguồn là 14.712 byte với cờ `FAST_Q8=1` hoặc 14.008 byte với `FAST_Q8=0`). Tự hiện thực hóa bộ tách từ BPE, các phép toán hạt nhân (`expf`, `sincosf`, `RMSNorm`, `RoPE`, `SiLU`, `Softmax`), vòng lặp đa luồng thông qua trực tiếp syscall Linux `clone()` và `futex()`, cùng cơ chế nhân ma trận Q8_0 hỗ trợ AVX2, FMA và F16C.
- **Hệ điều hành LLM Bare-Metal (`02-baremetal-os/`)**: Tệp ELF nhị phân dung lượng 24.252 byte có thể khởi động trực tiếp không cần hệ điều hành trung gian. Quy trình khởi động đi từ Multiboot 1 sang chế độ Long Mode 64-bit, cấu hình bảng trang phân trang 2 MiB, kích hoạt SIMD (AVX2/FMA/F16C), đa xử lý đối xứng SMP qua ACPI/APIC và xuất giao diện REPL qua VGA, bàn phím PS/2 và cổng nối tiếp COM1.
- **Huấn luyện Mini-GPT (`03-minigpt-train/`)**: Tệp nhị phân kích thước 32.944 byte phục vụ huấn luyện mô hình từ đầu với độ chính xác FP32. Tự hiện thực thuật toán nhân ma trận SGEMM phân khối thanh ghi 6x16 AVX2+FMA, lan truyền ngược giải tích (analytical backward pass), thuật toán tối ưu hóa AdamW tách rời và giao diện dòng lệnh vẽ đồ thị Unicode Braille động.

Để nạp trọng số, dự án sử dụng một kịch bản Python độc lập để xuất mô hình từ HuggingFace sang định dạng nhị phân riêng biệt `.asmbin` (v1 định dạng FP32 scale hoặc v2 định dạng FP16 scale).

## Trade-off và hạn chế

Phân tích dựa trên tài liệu README chỉ ra một số điểm đánh đổi và giới hạn đáng chú ý:

- **Bất lợi trong xử lý Prompt (Prefill)**: Theo lưu ý trong benchmark của nguồn, `llama.cpp` sử dụng thuật toán batched GEMM cho pha tiền xử lý prompt (`pp34`), trong khi `llm.asm` xử lý theo cơ chế GEMV từng token một. Do đó, pha prefill không được tối ưu hoá theo lô như các công cụ hiện đại.
- **Ràng buộc phần cứng x86-64 nghiêm ngặt**: Đòi hỏi CPU x86-64 bắt buộc phải hỗ trợ đầy đủ các tập lệnh AVX2, FMA và F16C (từ Intel Haswell hoặc AMD Excavator trở lên). Dự án không hỗ trợ GPU hay các kiến trúc CPU khác như ARM.
- **Phạm vi mô hình cố định**: Mã nguồn được viết tối ưu gắn liền với cấu trúc cụ thể của mô hình Qwen3-0.6B và Mini-GPT. Việc thích ứng cho các kiến trúc LLM khác đòi hỏi viết lại hoặc chỉnh sửa trực tiếp mã nguồn hợp ngữ.
- **Phụ thuộc vào công cụ tiền xử lý**: Dù pha chạy máy không phụ thuộc runtime bên ngoài, quy trình chuyển đổi trọng số ban đầu vẫn bắt buộc phải có môi trường Python và thư viện NumPy.
- **Chi phí bảo trì cao**: Việc duy trì và gỡ lỗi 17.252 dòng hợp ngữ thuần x86-64 rất phức tạp, khó mở rộng tính năng so với việc dùng các ngôn ngữ bậc cao có trình biên dịch tối ưu hóa tự động.

## Điểm đáng chú ý

- **Dung lượng siêu tinh gọn**: Kích thước toàn bộ tệp thực thi chỉ dao động từ khoảng 14,7 KB (suy luận) đến gần 33 KB (huấn luyện hoàn chỉnh), hoàn toàn không có dynamic section khi kiểm tra bằng `readelf`.
- **Hiệu năng giải mã CPU**: Theo số liệu thử nghiệm trên CPU AMD EPYC 7642 được công bố trong nguồn, ở chế độ `FAST_Q8=1`, `llm.asm` đạt tốc độ giải mã từ 20,70 tok/s (1 luồng) đến 125,86 tok/s (đỉnh 126,81 tok/s ở 40 luồng), nhanh hơn `llama.cpp` CPU chạy Q8_0 từ 18% đến 36% trên cùng phần cứng.
- **Thời gian khởi động Bare-Metal**: Phiên bản hệ điều hành bare-metal khởi động trong khoảng 74–94 ms (theo nguồn), có thể hoạt động trên máy ảo Proxmox VE không cần ổ đĩa (0 GB disk) với tốc độ giải mã đạt 55,4 tok/s trên vi xử lý Intel Xeon E5-2670 v3.
- **Độ chính xác số học**: Theo nguồn, kết quả suy luận của `FAST_Q8=1` đạt độ tương đồng cosine 0.99965 và khớp chính xác 64/64 token greedy so với PyTorch FP32. Ở pha huấn luyện, mô hình đạt độ tương đồng cosine 1.0000000000 trên toàn bộ 21 tensor gradient so với bản tham chiếu PyTorch CPU.

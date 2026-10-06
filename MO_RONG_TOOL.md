# Mở rộng tool

Ghi lại công dụng của các model trên [ContextBoxAI](https://huggingface.co/contextboxai),
bỏ qua Kokoro-Vietnamese đã tìm hiểu trước đó.

## 1. Các model dùng để làm gì?

| Model | Công dụng | Ví dụ dễ hiểu |
| --- | --- | --- |
| [ViZipvoice](https://huggingface.co/contextboxai/ViZipvoice) | Đọc văn bản tiếng Việt và nhân bản giọng từ đoạn âm thanh mẫu. | Đưa bản thu giọng bạn, lời trong bản thu và một câu mới → tạo âm thanh đọc câu mới bằng giọng tương tự. |
| [Qwen3-1.7B-FC](https://huggingface.co/contextboxai/Qwen3-1.7B-FC) | Giúp chatbot chọn công cụ cần gọi, như tra dữ liệu hoặc gọi API. FC là Function Calling. | Bạn nói “Tra đơn hàng 123” → model chọn hàm tra đơn hàng và truyền mã 123. Phần mềm thực hiện việc tra cứu. |
| [halong_embedding](https://huggingface.co/contextboxai/halong_embedding) | Tìm kiếm văn bản theo ý nghĩa, tập trung vào tiếng Việt. Dùng làm phần tìm tài liệu cho chatbot. | Bạn hỏi “Tôi được nghỉ bao nhiêu ngày?” → tìm đoạn liên quan trong tài liệu chính sách nghỉ phép, dù câu chữ không giống hệt. |

## 2. Có thể mở rộng tool hiện tại thế nào?

### Tạo giọng từ bản thu bằng ViZipvoice

Đây là model phù hợp với nhu cầu tạo âm thanh theo giọng của bạn.
Để sử dụng, cần chuẩn bị:

1. Một đoạn thu giọng mẫu rõ ràng.
2. Nội dung lời nói trong đoạn thu đó.
3. Văn bản mới muốn đọc.

ViZipvoice là hệ thống TTS riêng. Cần cài chương trình tương ứng và tích hợp
thêm vào tool nếu muốn sử dụng trong cùng giao diện.

### Điều khiển chức năng bằng Qwen3-1.7B-FC

Có thể dùng để xây chatbot nhận yêu cầu bằng ngôn ngữ tự nhiên rồi chọn chức năng
của tool. Ví dụ ý tưởng: bạn yêu cầu “Đọc đoạn này và lưu thành WAV”, model chọn
hàm tạo âm thanh cùng các tham số phù hợp.

Lập trình viên cần cung cấp các hàm cho model và viết phần thực thi chúng.

### Tìm tài liệu bằng halong_embedding

Có thể dùng để tìm nội dung liên quan trong tài liệu tiếng Việt, phục vụ chatbot
hỏi đáp theo tài liệu. Nếu muốn chatbot viết câu trả lời, cần kết hợp thêm một
model tạo văn bản và phần xử lý tài liệu.

## 3. Tình trạng

Các mục trên là tài liệu tham khảo và ý tưởng mở rộng. Các model này hiện
**chưa được tích hợp vào dự án Kokoro-TTS-Local**.

Nếu ưu tiên việc tạo giọng từ bản thu, hướng mở rộng phù hợp trong danh sách
này là **ViZipvoice**.

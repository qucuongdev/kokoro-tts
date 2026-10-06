# Cách dùng Kokoro TTS

Máy đã cài xong. Hằng ngày bạn chỉ cần mở ứng dụng, chọn giọng và nhập văn bản.
Không cần API key hay mở Visual Studio.

## 1. Mở ứng dụng

1. Vào thư mục `D:\Work\Tool\Kokoro-TTS-Local`.
2. Nhấp đúp file **CHAY_TTS.cmd**.
3. Đợi cửa sổ hiện `Running on local URL`.
4. Mở **http://127.0.0.1:7860** bằng trình duyệt.

Giữ cửa sổ chạy mở khi sử dụng. Nhấn **Ctrl+C** trong cửa sổ đó để dừng.
Nếu ứng dụng đã chạy, mở thẳng địa chỉ trên, không cần mở thêm một phiên.
File `CHAY_TTS.cmd` sẽ kiểm tra cổng trước khi chạy. Nếu báo cổng 7860 đang
được sử dụng, dùng phiên đang mở hoặc dừng phiên cũ rồi chạy lại.

Nếu muốn chạy bằng lệnh, mở **Command Prompt (CMD)** và chạy hai dòng này:

```cmd
cd /d D:\Work\Tool\Kokoro-TTS-Local
CHAY_TTS.cmd
```

Chỉ sao chép nội dung trong ô lệnh, không sao chép phần dấu nhắc terminal.

## 2. Tạo âm thanh

1. Chọn giọng trong ô **Voice**.
2. Nhập văn bản bằng ngôn ngữ phù hợp với giọng đó.
3. Chọn **WAV**, đặt **Speed = 1.0**.
4. Bấm **Generate Speech**, đợi hoàn tất rồi nghe thử.

Một vài giọng để thử:

| Giọng | Ngôn ngữ |
| --- | --- |
| `vi_diem_trinh`, `vi_mai_linh` | Tiếng Việt |
| `vi_duc_an`, `vi_hung_thinh` | Tiếng Việt |
| `af_bella`, `af_heart` | Nữ, tiếng Anh Mỹ |
| `am_michael` | Nam, tiếng Anh Mỹ |
| `bf_emma` | Nữ, tiếng Anh Anh |
| `zf_xiaobei` | Nữ, tiếng Trung phổ thông |

Ví dụ tiếng Anh: `Hello, this is a test.`

Ví dụ tiếng Việt: `Xin chào, hôm nay tôi đang kiểm tra giọng đọc tiếng Việt.`

WAV dùng được ngay. MP3/AAC cần có FFmpeg. Lần đầu chọn một số ngôn ngữ có thể
cần tải thêm model hoặc từ điển.

## 3. File âm thanh lưu ở đâu?

Âm thanh tạo mới được lưu trong thư mục **audio** của dự án:

```text
D:\Work\Tool\Kokoro-TTS-Local\audio
```

File có tên dạng `tts_20261003_...wav`. Bạn mở thư mục này để lấy file.
Nếu bấm tải xuống trên trình duyệt, trình duyệt sẽ lưu thêm một bản vào thư mục tải xuống.

## 4. Có giọng tiếng Việt không?

**Có. Tool đã tích hợp [Kokoro-Vietnamese](https://huggingface.co/contextboxai/Kokoro-Vietnamese),
với 14 giọng tiếng Việt.**

Chọn **vi_diem_trinh** hoặc một giọng bắt đầu bằng **vi_**, rồi nhập tiếng Việt.
Các file giọng Việt trên máy này đã đổi tên theo tiền tố `vi_`, ví dụ
`vi_diem_trinh.pt`. Tool cũng nhận tên gốc như `diem_trinh.pt` nếu bạn tải lại
từ Hugging Face.

Khi mở bằng `CHAY_TTS.cmd`, model `kokoro_vi.pth` và cấu hình tiếng Việt được lưu tại:

```text
D:\Work\Tool\Kokoro-TTS-Local\models\vietnamese
```

Máy này đã cài xong phần tiếng Việt. Nếu cần cài lại phần này sau khi đã cài
dự án trên máy khác, mở CMD trong thư mục dự án và chạy một lần:

```cmd
venv\Scripts\python.exe -m pip install -r requirements-vietnamese.txt
set "KOKORO_VI_MODEL_DIR=%CD%\models\vietnamese"
venv\Scripts\python.exe -m kokoro_tts_local.setup_vietnamese --all-voices
```

## 5. Thêm giọng mới thế nào?

### Chọn giọng khác đã có

Máy có 54 giọng Kokoro gốc và 14 giọng tiếng Việt. Chỉ cần đổi lựa chọn trong ô **Voice**;
không cần cài lại thư viện.

### Thêm một file giọng Kokoro khác

1. Chuẩn bị file **`.pt` tương thích với model Kokoro đang dùng**, từ nguồn tin cậy.
   File phải thuộc ngôn ngữ đã hỗ trợ và có đúng tiền tố tên giọng, ví dụ
   `af_custom.pt` cho giọng nữ tiếng Anh Mỹ.
   Giọng Việt mới phải tương thích với model Kokoro-Vietnamese đang dùng và
   đặt tên dạng `vi_custom.pt`.
2. Nhấn **Win+R**, dán đường dẫn dưới đây rồi nhấn Enter:

   ```text
   %LOCALAPPDATA%\kokoro-tts-local\voices
   ```

3. Chép file `.pt` vào thư mục đó, cạnh các file giọng hiện có.
4. Dừng ứng dụng và mở lại **CHAY_TTS.cmd**.
5. Chọn tên giọng mới trong ô **Voice**.

Đây là thư mục giọng mặc định. Nếu trước đó đã đặt `KOKORO_VOICES_DIR`, dùng
thư mục được cấu hình bằng biến đó.

File WAV/MP3 là âm thanh; giao diện này chưa có chức năng biến bản thu của bạn
thành một giọng mới. Để tạo giọng từ bản thu, cần hệ thống có hỗ trợ nhân bản giọng.

## 6. Khi gặp lỗi

- **Cổng 7860 đang được sử dụng:** mở http://127.0.0.1:7860 để dùng phiên đang chạy.
  Nếu cần khởi động lại, dừng phiên cũ trước.
- **Có dòng FutureWarning:** có thể tiếp tục nếu ứng dụng vẫn chạy và tạo được âm thanh.
- **File Việt cũ chỉ có tiếng rè:** mở lại ứng dụng để nạp bản sửa model, rồi
  tạo một file mới. File đã tạo trước khi sửa sẽ giữ nguyên tiếng rè.
- **Thiếu thư viện, model hoặc không tạo được âm thanh:** ghi lại lệnh vừa chạy,
  giọng đã chọn và khoảng 20 dòng cuối của lỗi để kiểm tra.

Không cần chạy lại các lệnh cài thư viện mỗi lần sử dụng.

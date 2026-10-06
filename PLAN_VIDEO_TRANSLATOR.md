# Kế hoạch PoC ứng dụng dịch và lồng tiếng video trên Windows

**Trạng thái:** Đề xuất để đánh giá, chưa triển khai project mới.  
**Ngày lập:** 03/10/2026.  
**Mục tiêu quyết định:** Đánh giá tính khả thi, phạm vi, công nghệ và điều kiện nghiệm thu trước khi đầu tư phát triển đầy đủ.

## 1. Mục tiêu sản phẩm

Xây dựng ứng dụng desktop Windows cho phép nhập video, nhận diện lời nói, dịch nội dung, chỉnh sửa bản dịch, sinh giọng đọc, căn âm thanh theo thời gian và xuất video.

Ứng dụng phân phối bằng `Setup.exe`. Người dùng không cần tự cài Python, chạy lệnh hoặc cài thư viện. Bộ cài ban đầu nhỏ; các tài nguyên lớn được tải trong bước thiết lập sau khi người dùng xác nhận. Dung lượng sau cài đặt và lượng tải sẽ được xác định bằng bản build thực tế.

Sau khi có đủ tài nguyên, toàn bộ pipeline nhận diện, dịch và TTS phải chạy local, không yêu cầu API dịch hoặc gửi nội dung video đến dịch vụ bên ngoài.

```text
Video đầu vào
  → Nhận diện lời nói và xác định mốc thời gian
  → Tạo phụ đề gốc
  → Dịch local theo ngữ cảnh
  → Người dùng kiểm tra và chỉnh sửa
  → Sinh giọng từng đoạn bằng TTS
  → Căn thời lượng và vị trí audio
  → Trộn âm thanh
  → Xuất MP4, WAV và phụ đề
```

## 2. Phạm vi PoC và mở rộng đa ngôn ngữ

### Phạm vi kiểm chứng ban đầu

- Video một người nói, ưu tiên hướng dẫn, bài giảng và thuyết minh.
- Anh/Trung → Việt.
- Chỉnh sửa nội dung trước TTS, nghe thử và regenerate từng đoạn.
- CPU-first; GPU tùy chọn khi backend thực sự tương thích.
- Thay toàn bộ audio hoặc giảm âm lượng audio gốc và chèn thuyết minh.
- Xuất MP4, WAV, phụ đề gốc và phụ đề dịch.
- Lưu project, tiến độ và phục hồi công việc bị gián đoạn.

### Thiết kế đa ngôn ngữ

Giao diện tách ba lựa chọn: **ngôn ngữ nguồn → ngôn ngữ đích → giọng/accent**. Anh Mỹ và Anh Anh là lựa chọn giọng/accent, thường cùng dùng ngôn ngữ dịch là tiếng Anh.

Khả năng nhận diện, dịch và sinh giọng được quản lý riêng. Ngôn ngữ dịch được nhưng chưa có TTS tương ứng chỉ hỗ trợ xuất phụ đề. Các cặp ngôn ngữ bổ sung chỉ công bố hỗ trợ sau khi kiểm thử.

### Chưa thuộc PoC

- Lip-sync, nhân bản giọng và diễn xuất giọng chuyên sâu.
- Tách giọng nói khỏi nhạc nền để thay lời thoại mà giữ nguyên nền.
- Hội thoại nhiều người, lời nói chồng nhau và diarization.
- Timeline biên tập video chuyên nghiệp.

## 3. Project mới và tham chiếu Kokoro-TTS-Local

Đề xuất tạo project độc lập, song song với dự án hiện tại:

```text
D:\Work\Tool\
├── Kokoro-TTS-Local\    Nguồn tham khảo, chỉ đọc khi phát triển app mới
└── VideoTranslator\    Project mới, đường dẫn chờ xác nhận
```

**Phải refer dự án `Kokoro-TTS-Local` hiện tại để tái sử dụng lõi sinh giọng TTS. Kokoro không thực hiện dịch văn bản; translator local là thành phần riêng.**

Phần cần rà soát và tái sử dụng:

- Khởi tạo model, cache, khóa inference và sinh giọng trong `src/kokoro_tts_local/models.py`.
- Checkpoint, config, G2P, segmentation và tương thích voicepack tiếng Việt trong `src/kokoro_tts_local/vietnamese.py` và `setup_vietnamese.py`.
- Định tuyến ngôn ngữ, kiểm tra file giọng và các kiểm thử liên quan.

Đưa phần cần thiết vào `KokoroEngine` độc lập, giữ thông tin nguồn và giấy phép. Không mang nguyên giao diện Gradio, CLI hoặc cơ chế cắt nội dung của giao diện cũ sang app mới. Không sửa dự án Kokoro nguồn.

Bản đóng gói phải chứa đủ code và tài nguyên để hoạt động độc lập; không phụ thuộc folder hoặc môi trường Python của dự án Kokoro trên máy phát triển.

## 4. Công nghệ đề xuất

| Thành phần | Phương án | Ghi chú |
| --- | --- | --- |
| UI | PySide6, Qt Widgets | Editor desktop; Qt Designer để dựng layout |
| Preview | Qt Multimedia | Kiểm thử codec và Qt plugin trong bản đóng gói |
| Bảng segment | Qt Model/View | Đồng bộ lựa chọn với preview và timeline cơ bản |
| Lõi ứng dụng | Python 3.12 | Pin dependency sau khi kiểm chứng tương thích |
| Xử lý nền | Worker process riêng | UI nhận progress; có hủy, lỗi và kiểm tra worker |
| Dữ liệu | SQLite + file media | Transaction cho trạng thái; media lưu riêng |
| ASR | Faster-whisper | Chốt checkpoint/profile qua benchmark |
| Dịch | Local Translator abstraction | Chưa chốt model/runtime trước benchmark |
| TTS | KokoroEngine và các adapter mở rộng | Refer lõi Kokoro hiện tại |
| Media | FFmpeg / FFprobe | Phân phối bản build phù hợp và rà soát giấy phép |
| Đóng gói | PyInstaller `onedir` | Đóng gói runtime, worker và tài nguyên cần thiết |
| Installer | Inno Setup | Tạo `Setup.exe`, hỗ trợ cài/nâng cấp/gỡ |

Việc chọn model dịch phải dựa trên chất lượng Anh/Trung → Việt, tốc độ CPU, RAM, khả năng viết gọn và điều kiện phân phối. Không chốt model chỉ dựa trên tuyên bố đa ngôn ngữ.

## 5. Thiết kế nền tảng cần chốt

### 5.1. Project, đoạn lời nói và dòng phụ đề

Không coi một dòng SRT luôn tương đương một câu hoặc một đoạn TTS. Phân biệt:

- **Đoạn lời nói:** đơn vị dịch, sinh giọng và căn thời gian.
- **Dòng phụ đề:** đơn vị hiển thị, có thể chia một đoạn lời nói thành nhiều dòng.
- **Quan hệ ánh xạ:** giữ liên kết giữa đoạn lời nói và các dòng phụ đề.

Project lưu ID, video path/fingerprint, ngôn ngữ, phiên bản schema, cấu hình engine và render. Đoạn lời nói lưu ID ổn định, mốc thời gian, văn bản gốc, bản dịch tự động, bản người dùng sửa, giọng, tốc độ, artifact audio, thời lượng và trạng thái.

Lưu riêng nội dung được duyệt và đề xuất tự động. Khi video được di chuyển, hỗ trợ liên kết lại file và kiểm tra fingerprint.

### 5.2. Resource Manager và voice catalog

- Manifest gồm ID, phiên bản, nguồn, checksum, kích thước, tương thích và thông tin giấy phép.
- Tải tiếp, kiểm tra file và chỉ kích hoạt khi đủ bộ tài nguyên hợp lệ.
- Phân biệt runtime cơ bản, model lớn, voicepack và tài nguyên G2P.
- Lần thiết lập đầu cung cấp đầy đủ catalog giọng mặc định đã kiểm thử và đủ điều kiện phân phối; không yêu cầu tải từng giọng khi sử dụng.
- Chốt danh mục “đầy đủ” bằng danh sách cụ thể trước khi phát hành.
- Nhập `.pt` phải kiểm tra an toàn, cấu trúc tensor, ngôn ngữ/checkpoint tương thích và nghe thử. File `.pt` bất kỳ không mặc nhiên là giọng Kokoro hợp lệ.
- Thêm voicepack không tự bổ sung khả năng đọc một ngôn ngữ mới.

### 5.3. Timeline fitting policy

Mục tiêu là lời đọc bám mốc bắt đầu và khoảng kết thúc lời nói gốc, hạn chế lệch âm thanh so với hình. Timestamp ASR cần cho phép sửa; không cam kết chính xác tuyệt đối hoặc khớp môi.

1. Sinh audio và đo thời lượng thực tế.
2. Nếu ngắn: giữ tốc độ tự nhiên và thêm khoảng lặng phù hợp.
3. Nếu dài nhẹ: chỉnh tốc độ TTS hoặc tempo trong giới hạn đã kiểm chứng.
4. Nếu vẫn quá dài: đánh dấu để sửa; phase 5 bổ sung đề xuất dịch gọn và sinh lại với số lần thử giới hạn.
5. Không tự cắt mất lời, không đẩy các câu sau lệch dần và không tự ghi đè nội dung người dùng đã duyệt.
6. Chỉ sử dụng khoảng trống trước đoạn kế tiếp theo policy rõ ràng, không tạo chồng tiếng ngoài ý muốn.

Hiển thị thời gian được cấp, thời lượng audio, mức điều chỉnh và cảnh báo từng đoạn.

### 5.4. Translator và chiến lược tài nguyên máy

Translator nhận đoạn nguồn, ID, ngữ cảnh lân cận, ngôn ngữ đích, thuật ngữ và khoảng thời gian mục tiêu. Kiểm tra kết quả thiếu/trùng ID, rỗng và sai cấu trúc; lưu phiên bản model cùng tham số.

ASR, translator và TTS có lifecycle riêng. CPU là đường chạy cơ bản; kiểm tra GPU theo từng backend bằng thử nghiệm thực tế. Chạy tuần tự và giải phóng model khi cần để tránh giữ tất cả model trong RAM/VRAM.

### 5.5. Job state, recovery, cache và migration

- Theo dõi trạng thái từng job và đoạn: chờ, đang chạy, hoàn tất, lỗi, đã hủy, bị gián đoạn.
- Lưu kết quả sau mỗi đoạn; ghi media qua file tạm rồi đổi tên khi hoàn tất.
- Sau crash, kiểm tra artifact, phiên bản tài nguyên và cache trước khi tiếp tục.
- Cache key gồm input và cấu hình/phiên bản engine liên quan.
- Sửa câu chỉ vô hiệu hóa phần bị ảnh hưởng; đổi mix không cần sinh lại TTS.
- Backup trước migration; tách cache có thể xóa khỏi nội dung người dùng đã chỉnh sửa.

### 5.6. Editor UX

Workspace gồm preview, bảng đoạn lời nói/phụ đề, timeline cơ bản, panel chỉnh nội dung/giọng/timing và bảng công việc. Hỗ trợ nghe thử, regenerate chọn lọc, xử lý hàng loạt và lọc các đoạn lỗi hoặc không vừa thời gian.

Wizard chỉ dành cho thiết lập đầu và tạo project; không buộc người dùng đi lại toàn bộ quy trình khi sửa một đoạn.

## 6. Kế hoạch 6 phase

### Phase 1 — Kiểm chứng công nghệ và nền tảng

**Công việc:**

- Xác nhận đường dẫn và quyền thao tác, tạo project độc lập sau khi được duyệt.
- Chốt schema, engine interfaces, job state và cấu trúc module.
- Dựng khung PySide6 với preview, bảng dữ liệu mẫu và log.
- Build installer tối thiểu, kiểm tra worker và media trong bản đóng gói.
- Benchmark ứng viên ASR/dịch local trên tập mẫu Anh/Trung và máy mục tiêu.

**Nghiệm thu:** cài/mở được trên máy sạch; có báo cáo chất lượng, tốc độ, bộ nhớ và lựa chọn model/runtime khả thi. Nếu chưa đạt, điều chỉnh model hoặc cấu hình mục tiêu trước khi đầu tư UI sâu.

### Phase 2 — Resource Manager và engine local

**Công việc:**

- Refer và tách lõi Kokoro hiện tại thành `KokoroEngine`.
- Tích hợp runtime ASR và translator đã chọn; chưa cần pipeline hoàn chỉnh.
- Xây manifest, tải/kiểm tra/kích hoạt tài nguyên và catalog giọng.
- Thêm nhập `.pt`, nghe thử và quản lý tương thích.
- Kiểm tra CPU/GPU, fallback và nạp/gỡ model.

**Nghiệm thu:** các engine chạy trong bản đóng gói; tài nguyên hợp lệ; sinh giọng và dịch mẫu chạy offline; không phụ thuộc repo nguồn.

### Phase 3 — Editor và recovery

**Công việc:**

- Nhập video + SRT có sẵn, ánh xạ dòng phụ đề với đoạn lời nói.
- Chỉnh nội dung, timestamp, giọng và tốc độ; nghe thử và regenerate.
- Lưu tự động, trạng thái công việc, cache invalidation, hủy và phục hồi.

**Nghiệm thu:** sửa một đoạn chỉ tạo lại đoạn đó; mở lại giữ dữ liệu và tiến độ; kết quả hoàn tất không mất khi hủy/crash; UI vẫn phản hồi.

### Phase 4 — Căn audio và render

**Công việc:**

- Đo audio, đặt đúng timestamp, thêm khoảng lặng và chỉnh tốc độ trong giới hạn.
- Cảnh báo không vừa thời gian; người dùng sửa thủ công ở phase này.
- Thay audio hoặc giảm tiếng gốc và chèn thuyết minh.
- Xuất MP4, WAV và SRT; kiểm tra artifact đầu ra.

**Nghiệm thu:** không cắt mất lời, không lệch dần timeline; hiển thị đoạn cần sửa; render không cắt cụt video hoặc audio ngoài ý muốn.

### Phase 5 — Pipeline tự động và đa ngôn ngữ

**Công việc:**

- Tích hợp ASR/VAD/timestamp và chọn ngôn ngữ nguồn thủ công/tự động.
- Dịch local theo ngữ cảnh, thuật ngữ và kiểm tra ID.
- Giữ bước edit before TTS; thêm đề xuất viết gọn có giới hạn số lần thử.
- Lọc khả năng nhận diện/dịch/TTS, ngôn ngữ đích và accent.
- Hoàn thiện toàn bộ luồng xử lý video.

**Nghiệm thu:** PoC Anh/Trung → Việt một người nói hoàn chỉnh; chạy offline sau thiết lập; regenerate và phục hồi đúng. Chỉ công bố cặp ngôn ngữ bổ sung sau kiểm thử.

### Phase 6 — Hoàn thiện và phân phối

**Công việc:**

- Kiểm thử máy sạch, cấu hình CPU/GPU, mất mạng, thiếu dung lượng và crash.
- Hoàn thiện migration, cache cleanup, nâng cấp và xử lý bản tải lỗi.
- Rà soát giấy phép của code, thư viện, model, giọng và FFmpeg build.
- Hoàn thiện installer, hướng dẫn, thông báo lỗi và số liệu cấu hình tối thiểu.
- Tách thư mục chương trình khỏi dữ liệu người dùng; làm rõ chính sách gỡ app/giữ dữ liệu.

**Nghiệm thu:** cài/nâng cấp/gỡ đúng; giữ project và giọng tùy chỉnh khi nâng cấp; không yêu cầu người dùng chạy lệnh; có giới hạn sản phẩm và kết quả kiểm thử được ghi nhận.

**Mốc:** cuối phase 5 là PoC hoàn chỉnh; phase 6 là ứng viên phát hành. Mỗi phase tạo bản build kiểm thử, không chờ cuối dự án mới đóng gói.

## 7. Tiêu chí đánh giá và rủi ro

| Hạng mục | Chỉ số/kiểm tra | Thời điểm chốt |
| --- | --- | --- |
| ASR | Sai nội dung, tên riêng/số, timestamp, lời nói bị bỏ sót | Benchmark phase 1, xác minh phase 5 |
| Dịch | Giữ ý nghĩa, thuật ngữ, độ tự nhiên và câu thiếu | Benchmark phase 1, xác minh phase 5 |
| Timing | Lệch mốc bắt đầu, audio vượt khoảng được cấp, tỷ lệ cần sửa | Thử nghiệm phase 4 |
| TTS | Chất lượng nghe, phát âm, mức tăng tốc chấp nhận được | Phase 2–4 |
| Hiệu năng | Thời gian theo từng bước, RAM/VRAM đỉnh, dung lượng | Phase 1 và đo lại khi tích hợp |
| Recovery | Hủy/crash/tải gián đoạn và tiếp tục không mất dữ liệu | Phase 3 và 6 |
| Installer | Máy chưa có Python, worker, codec/plugin, nâng cấp/gỡ | Phase 1 và 6 |

Không đặt ngưỡng số hoặc cam kết tốc độ khi chưa có benchmark. Thống nhất ngưỡng nghiệm thu với người đánh giá sau kết quả đầu tiên. Dùng tập mẫu cố định cho các phiên bản.

Rủi ro lớn nhất là dịch local trên CPU chưa đạt đồng thời chất lượng và thời gian chờ phù hợp. Rủi ro tiếp theo là timestamp, chất lượng khi tăng tốc giọng, khác biệt máy đích và thiếu tài nguyên trong bundle. Các kết quả chưa đạt phải được ghi rõ; không đánh giá thành công chỉ bằng việc xuất được MP4.

## 8. Model hỗ trợ phát triển trong Codex

- **Ưu tiên năng lực:** GPT-6 Astra cho kiến trúc, review, recovery, concurrency và lỗi đóng gói khó; đề xuất reasoning High.
- **Cân bằng chi phí:** GPT-6.1 Sol cho triển khai thường ngày; đề xuất reasoning Medium, tăng khi xử lý vấn đề phức tạp.
- Việc lựa chọn phụ thuộc model thực tế có trong tài khoản Codex và kết quả sử dụng. Đây là gợi ý, không bảo đảm model tự hoàn thành đúng mọi yêu cầu.
- Model dùng trong Codex hỗ trợ lập trình, không phải model dịch local được nhúng vào app.

Nguồn: [OpenAI model catalog](https://developers.openai.com/api/docs/models), [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection). Gợi ý được kiểm tra tại ngày lập tài liệu; cần kiểm tra lại nếu triển khai vào thời điểm khác.

## 9. Quy tắc thao tác khi phát triển

Các quy tắc này cần đưa vào `AGENTS.md` của project mới sau khi project được phép tạo.

1. Chỉ tạo/sửa/xóa file thuộc project đang được giao và đường dẫn đã xác nhận. Kiểm tra đường dẫn đích trước thao tác, bao gồm đường dẫn qua symlink/junction.
2. Dự án Kokoro nguồn chỉ đọc. Chỉ đưa code/tài nguyên cần thiết sang project mới trong phạm vi đã được duyệt; giữ nguồn và giấy phép.
3. Không tự sửa project khác, Python global, môi trường khác, PATH, registry, cấu hình hệ thống hoặc driver.
4. Trước khi chạy chương trình/script, test, build, installer hoặc tải/cài phần mềm, thư viện/model: trình bày mục đích, lệnh/phạm vi, nguồn tải, nơi lưu và ảnh hưởng; chỉ thực hiện sau khi chủ dự án đồng ý.
5. Có thể duyệt một nhóm thao tác cụ thể; không coi việc duyệt plan là duyệt toàn bộ lệnh hoặc toàn bộ các phase. Phát sinh ngoài phạm vi cần xin duyệt thêm.
6. Dependency dùng môi trường riêng. Build, log, cache và file tạm phát triển được hướng vào project khi có thể. Thành phần bắt buộc ghi ngoài project phải khai báo và được duyệt; không tự tìm cách né quyền hạn.
7. Không tự xóa hàng loạt, reset Git, ghi đè dữ liệu người dùng, dừng tiến trình ngoài project hoặc chạy quyền quản trị.
8. Không tự mở rộng phạm vi hoặc dùng agent phụ nếu chưa được yêu cầu/cho phép.
9. Cuối phase báo cáo thay đổi, kiểm thử thực sự đã chạy, lỗi còn lại và artifact. Chỉ chuyển phase sau khi chủ dự án nghiệm thu.
10. Dùng `AGENTS.md` kết hợp workspace/sandbox giới hạn quyền ghi; tài liệu hướng dẫn không thay thế cơ chế cách ly.

**Phân biệt với sản phẩm:** quy tắc trên áp dụng cho hoạt động phát triển của Codex. App phát hành có chính sách riêng về người dùng xác nhận tải tài nguyên và chọn nơi lưu. Kiểm thử installer trên máy sạch có thể ghi ngoài project và cần được duyệt riêng.

## 10. Nội dung cần người đánh giá quyết định

- Phê duyệt phạm vi PoC và đường dẫn project mới.
- Xác định máy/cấu hình mục tiêu và cung cấp tập video mẫu có quyền sử dụng.
- Thống nhất catalog giọng mặc định và nhu cầu ngôn ngữ mở rộng ưu tiên.
- Duyệt danh mục công cụ/tài nguyên và nhóm thao tác phase 1 trước khi chạy/tải/cài.
- Đánh giá benchmark để chốt model, ngưỡng chất lượng, hiệu năng và phạm vi tiếp theo.
- Ước lượng thời gian, công sức và dung lượng sau phase 1; tài liệu hiện tại chưa cam kết các con số này.

## 11. Tài liệu tham khảo kỹ thuật

- [Qt for Python deployment](https://doc.qt.io/qtforpython-6/deployment/index.html)
- [PyInstaller: cơ chế đóng gói](https://pyinstaller.org/en/stable/operating-mode.html)
- [Inno Setup](https://jrsoftware.org/isinfo.php)
- [Faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
- [Kokoro-Vietnamese](https://huggingface.co/contextboxai/Kokoro-Vietnamese)
- [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html)

Các giấy phép và khả năng phân phối phải được kiểm tra theo đúng phiên bản, artifact và bản build được lựa chọn trước khi phát hành.

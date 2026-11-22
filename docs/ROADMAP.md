# Roadmap — MVP v2.0

| Mốc | Member A (Hardware/Embedded) | Member B (Backend/IoT) | Điều kiện đạt |
|---|---|---|---|
| M0 | Pinout, BOM 2 S3 + 2 servo | Schema S/M, API logic | Tài liệu v2.0 đồng nhất |
| M1 | Prototype 1 MG90S + MC-38 + chốt thật, đo nguồn | DB/Best Fit mock | Demo bench một ngăn |
| M2 | Central/Node ESP-NOW, Serial, ST7789/LVGL/keypad | FastAPI, Gateway Serial, auth/reservation | Giao tiếp đúng hai ngăn |
| M3 | Tích hợp 1 cửa/servo thật | Web App nhận + code kiosk 30s | Một đơn gửi→nhận E2E |
| M4 | Lắp 2 cửa (S/M), thử dòng/nguồn/lỗi | Best-fit S→M, concurrency, quản lý trạng thái | Hai ngăn E2E và xử lý lỗi |
| M5 | Telemetry, ổn định thiết bị | CoreIOT dashboard/notification | Demo giám sát thật |
| M6 | Evidence sơ đồ/điện/chốt | QA/báo cáo/video/README cài đặt | Nộp sản phẩm đúng yêu cầu |

**Không làm ngay:** bốn ngăn, size L, latch microswitch, OTA, buzzer, APK, ESP32 webserver. Chỉ bổ sung khi MVP ổn định và có nhu cầu điểm công nghệ. Các thí nghiệm relay/khóa 12V trước đó là lịch sử, không tính như bài test servo.

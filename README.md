## Backend Phase 1 đã triển khai

FastAPI + SQLite: [hướng dẫn Windows, schema, API và kiểm thử](docs/BACKEND_PHASE1.md). Cấu hình Phase 1 hiện hành là **2 ESP32-S3**, **L01=S, L02=M**, servo 5V + MC-38, không latch sensor. Best-fit S→S/M, M→M; không size L. Hoàn tất cần confirmation, chu kỳ cửa đúng phiên, CLOSED mới hợp lệ và LOCK_APPLIED đúng command, không có lỗi/offline/unknown. LOCK_APPLIED chỉ chứng minh servo đã được điều khiển, không chứng minh chốt gài cơ khí. Đây là cấu hình ưu tiên hơn các mô tả baseline cũ bên dưới; tài liệu v1.2 giữ nguyên.

---

# Smart Parcel Locker — MVP v2.0

**Cập nhật 23/11/2026.** Nhóm 2 người; **2 ESP32-S3 Yolo UNO, 2 ngăn L01=S và L02=M**, khóa bằng **2 servo MG90S 5V + chốt cơ khí**, đọc trạng thái cửa bằng **2 MC-38 NC**. Không dùng relay, khóa 12V, hay microswitch xác nhận chốt trong MVP.

## Kiến trúc

```text
PC: FastAPI + SQLite + Gateway Serial/MQTT ── CoreIOT
                | USB Serial JSON Lines
ESP32-S3 #1: Central/Kiosk (ST7789 240×240, LVGL, keypad 4×4)
                | ESP-NOW
ESP32-S3 #2: Locker Node
         ├── L01 (S): servo MG90S + MC-38
         └── L02 (M): servo MG90S + MC-38
```

Backend và Gateway là module trong **cùng một ứng dụng Python**, không tách thành hai HTTP server. Firmware PlatformIO/C++ Arduino. Web App dành cho admin/cư dân; CoreIOT để giám sát.

## Luồng chính

Shipper nhập mã phòng số, số điện thoại cư dân, kích thước S/M trên kiosk. Backend kiểm tra cư dân có sẵn và chọn ngăn best-fit: **S→S hoặc M; M→M**. Sau khi reservation/lệnh được lưu, Backend gửi UNLOCK qua USB Serial → Central → ESP-NOW → Locker Node. Shipper đặt hàng, đóng cửa, xác nhận. Servo khóa lại khi cửa đã đóng; MC-38 chỉ đo trạng thái cửa, không đo kiện hay chứng minh chốt đã gài.

Người nhận đăng nhập Web App, xác thực quyền sở hữu và **mã phiên 30 giây hiển thị ở kiosk**, nhận hàng, đóng cửa, xác nhận. Backend quản lý vòng đời giao dịch; lỗi hoặc trạng thái không xác định không được tự giải phóng ngăn.

## Phạm vi

MVP: 2 servo/chốt, 2 MC-38, 2 ESP32-S3, ST7789/LVGL, keypad, ESP-NOW, FastAPI/SQLite, Web App, Gateway PC, CoreIOT. **Để sau:** bốn ngăn, size L, microswitch chốt, buzzer, OTA, webserver trên ESP32, APK và các mở rộng khác. Các lần test khóa 12V/relay trước đây không phải bằng chứng đã test servo.

Xem [PROJECT_SPEC](docs/PROJECT_SPEC.md), [ARCHITECTURE](docs/ARCHITECTURE.md), [INTERFACES](docs/INTERFACES.md), [DECISIONS](docs/DECISIONS.md), [ROADMAP](docs/ROADMAP.md), [TEST_PLAN](docs/TEST_PLAN.md).

**Lưu ý:** các file là kế hoạch kỹ thuật, không tuyên bố đã có mã chạy hay test PASS nếu chưa có minh chứng. File đặc tả v1.2 ở root giữ làm lịch sử, không sửa.

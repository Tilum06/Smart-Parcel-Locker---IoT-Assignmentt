## Bổ sung triển khai Phase 1 (hiện hành)

Cấu hình ưu tiên: 2 ESP32-S3 (Central 1, Locker Node 2), 2 locker L01=S/L02=M, servo 5V + MC-38, không cảm biến chốt, không size L. FastAPI + SQLite đã có source Phase 1; [schema, API, setup và giới hạn](BACKEND_PHASE1.md). Hoàn tất gửi/nhận cần confirmation + OPEN→CLOSED đúng phiên + CLOSED mới hợp lệ + LOCK_APPLIED đúng command, không lỗi/offline/unknown. Không cần ENGAGED; LOCK_APPLIED chỉ là kết quả điều khiển servo, không xác minh chốt cơ khí. Nội dung Phase 1 này thay các mô tả cấu hình baseline cũ; v1.2 giữ lịch sử.

---

# Đặc tả hiện hành — Smart Parcel Locker v2.0

## Cấu hình chốt

| Thành phần | MVP |
|---|---|
| Central | 1 Yolo UNO ESP32-S3, ST7789 240×240 SPI/LVGL, keypad 4×4 |
| Locker Node | 1 Yolo UNO ESP32-S3, điều khiển cả hai ngăn qua ESP-NOW |
| Locker | L01=S, L02=M; kích thước cm chưa chốt |
| Khóa/cửa | 2 MG90S 180° + chốt cơ khí, 2 MC-38 NC |
| Nguồn servo | Nguồn 5V ngoài, GND chung ESP32; phải test dòng khi kéo/kẹt |
| PC | Python FastAPI + SQLite, Gateway Serial/MQTT cùng ứng dụng |
| Xác thực cư dân | Admin tạo tài khoản gắn mã phòng số và số điện thoại |
| Nhận hàng | Login Web App + đúng chủ đơn + mã phiên 30 giây tại kiosk |

Không dùng khóa 12V/relay, cảm biến hiện diện hàng hay microswitch chốt trong MVP. Chỉ có phản hồi cửa; servo LOCK_APPLIED không chứng minh chốt gài vật lý.

## Chức năng bắt buộc cho MVP

1. Kiosk nhập mã phòng, SĐT, size S/M; đối chiếu cư dân được admin tạo sẵn.
2. Backend best-fit: **S ưu tiên L01**, nếu bận được nâng lên L02; **M chỉ L02**; cấp ngăn atomic và loại offline/lỗi/đang dùng.
3. Backend lưu command intent/request ID trước khi gửi UNLOCK; Central chuyển tới Locker Node qua ESP-NOW.
4. Shipper đặt kiện và xác nhận thủ công, cửa phải có chu kỳ OPEN→CLOSED hợp lệ; Node chỉ LOCK khi cửa CLOSED.
5. Web App hiển thị thông báo cho đúng người nhận. Người nhận login, nhập mã phiên kiosk hạn 30 giây, một lần dùng, giới hạn thử và gắn đúng phiên/đơn/kiosk.
6. Người nhận lấy hàng, đóng cửa, xác nhận; Backend hoàn tất khi đủ điều kiện nghiệp vụ và kết quả servo hợp lệ, không tự kết luận vị trí chốt.
7. Gateway PC đẩy telemetry/notification phù hợp sang CoreIOT, không tiết lộ SĐT/mã phòng/mã phiên/token.

## Nguyên tắc vận hành

Door OPEN/CLOSED/UNKNOWN độc lập với servo_action IDLE/UNLOCK_APPLIED/LOCK_APPLIED/ERROR/UNKNOWN. Không có latch_feedback. ACK ≠ actuation result, actuation result ≠ xác nhận cơ khí. Không LOCK khi cửa OPEN/UNKNOWN; sau reset/mất kết nối, giữ UNKNOWN/MAINTENANCE và reconcile thay vì mở lại hay giải phóng ngăn tự động. Không tự tạo tài khoản từ input shipper.

## Còn phải đo/chốt

Góc servo, cơ cấu chốt, kích thước ngăn S/M, nguồn 5V–2A đủ tải hay không, chân Central SPI/keypad, độ trễ/debounce MC-38, schema Serial/ESP-NOW, timeout/dedup và khôi phục khi mất kết nối. Phần mở rộng 4 ngăn, cảm biến chốt, OTA, APK, webserver ESP32 sẽ xét sau.

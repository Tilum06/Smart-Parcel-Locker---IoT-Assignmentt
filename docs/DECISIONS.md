# Quyết định thiết kế — MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

Baseline ngày 25/11/2026. Đã chốt thiết kế không đồng nghĩa Implemented hoặc Verified.

| ID | Quyết định mục tiêu |
|---|---|
| C-01 | Hai Yolo UNO ESP32-S3: Central ID 1, Locker Node ID 2 |
| C-02 | Một Node quản lý L01=S và L02=M; không size L |
| C-03 | Mỗi ngăn MG90S 5V 180° + chốt cơ khí, MC-38 NC; không relay/khóa 12V/cảm biến kiện/microswitch chốt |
| C-04 | MC-38 đo cửa; ACK xác nhận nhận lệnh; LOCK_APPLIED chỉ kết quả điều khiển servo, không xác minh gài chốt |
| C-05 | FastAPI + SQLite + Gateway Serial/MQTT cùng ứng dụng Python |
| C-06 | Central↔Node ESP-NOW; PC↔Central USB Serial UTF-8 JSON Lines, baud ban đầu 115200 |
| C-07 | ST7789 SPI 240×240/LVGL, keypad 4×4; Central không cấp ngăn/quyết định quyền/điều khiển servo |
| C-08 | Mobile App yêu cầu Backend cấp PIN 6 chữ số/30 giây, nhập trên kiosk; one-use, owner/parcel/kiosk scope, giới hạn thử và rate limit; thay thiết kế mã do kiosk hiển thị |
| C-09 | S ưu tiên L01, có thể dùng L02; M chỉ L02; reserve atomic, loại ngăn offline/lỗi/đang dùng/unknown |
| C-10 | Pinout tập trung duy nhất tại [PINOUT](../hardware/PINOUT.md), không nhân bảng trong README module |
| C-11 | Tiêu thụ PIN atomic với tạo giao dịch/UNLOCK intent; Backend không phản hồi thì không mở; không TOTP offline |
| C-12 | Hai project PlatformIO C++ Arduino độc lập; config tập trung; giữ source thử nghiệm cũ |
| C-13 | CoreIoT giám sát/telemetry/thống kê/cảnh báo qua Gateway; triển khai song song bằng dữ liệu giả |

## Đã hiện thực trong Phase 1

SQLite stdlib/FastAPI/Pydantic, migration user_version=1, BEGIN IMMEDIATE, partial unique active transaction; auth/role/owner, best-fit S/M, durable intent và idempotency. Confirmation + OPEN→CLOSED đúng phiên + CLOSED mới (10 giây) + LOCK_APPLIED đúng command, không lỗi/offline/unknown mới hoàn tất. Không cần ENGAGED. Restart buộc offline, giữ reservation, không tự replay UNLOCK. [Phase 1](BACKEND_PHASE1.md).

**C-08/C-11 chưa có implementation PIN v2.1.** Phase 1 tạo opaque code từ kiosk, TTL 30 giây, hash, one-use, tối đa 5 lần sai; chưa có PIN 6 số, cấp mã phía resident, xác thực PIN tại kiosk hay rate limit kiosk toàn cục.

## Gate còn mở

| Gate | Cần chốt/xác minh | Owner đề xuất |
|---|---|---|
| P-01 | MAC, channel, serialization/version, packet size, timeout/retry/dedup, boot/sequence, bảo vệ ESP-NOW | Cả hai |
| P-02 | Board revision, board definition S3, Arduino/LVGL/library version, USB CDC và pin aliases; Central test đang esp32dev | Member 1 + review chung |
| P-03 | API cấp/verify/confirm PIN; kiosk identity/scope, collision atomic, verifier bảo vệ PIN, hạn mức sai/rate limit, retry/thu hồi/cấp lại | Cả hai |
| P-04 | Pinout board thực, BLK/CS module, thứ tự keypad; sơ đồ OhStem NeoPixel GPIO45 khác sample variant GPIO48 | Cả hai |
| P-05 | Góc/pulse servo, chốt, kích thước S/M, polarity/debounce MC-38, nguồn 5V–2A dưới tải | Member 2 + review chung |
| P-06 | Serial envelope/handshake/line limits, mapping DeviceEvent, liveness/reconcile, telemetry schema/CoreIoT mapping | Cả hai |

Không tự chọn tham số chưa có evidence. ID trong M0/v1.2 là lịch sử, không tự quy đổi thành quyết định đã đóng hiện nay. Mở rộng node/ngăn chỉ là khả năng thiết kế config, chưa triển khai. [Workflow](GIT_WORKFLOW.md), [roadmap](ROADMAP.md).

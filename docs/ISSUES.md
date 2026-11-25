# Công việc và backlog — MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

Trạng thái ngày 25/11/2026. Implemented là có source; Verified cần evidence đúng cấu hình. Các hàng Planned chưa được đóng bằng cập nhật tài liệu.

| ID | Owner đề xuất | Trạng thái | Công việc / điều kiện hoàn tất |
|---|---|---|---|
| DEC-01 | Cả hai | Planned | Chốt pinout/revision, protocol, API PIN, telemetry schema; review trước branch firmware |
| HW-01 | Member 2 + cả hai | Planned | MG90S + chốt, MC-38 polarity/debounce; góc/pulse, tải hai servo/nguồn 5V–2A có phép đo |
| FW-01 | Member 2 | Planned | Node S3 quản lý hai ngăn qua config; guard LOCK OPEN/UNKNOWN; result/door/status/error |
| FW-02 | Cả hai | Planned | ESP-NOW hai đầu: MAC/channel/serialization/version/security/retry/dedup/boot/sequence thống nhất |
| FW-03 | Member 1 | Planned | Central S3 ST7789/LVGL/keypad; nhập gửi và PIN, response/event; không tự quyết quyền |
| BE-01 | Cả hai | Implemented Phase 1 | SQLite + allocation atomic S→L01/L02, M→L02; chưa có adapter liveness thật |
| BE-02 | Cả hai | Planned v2.1 | API cấp PIN cho resident, verify tại kiosk, collision active scope, atomic consume/intent, confirm kiosk, attempts/rate limit, verifier và test |
| GW-01 | Member 1 Serial / Member 2 MQTT | Planned | Gateway cùng ứng dụng Python, map DeviceEvent, heartbeat/reconcile, không replay UNLOCK mù |
| APP-01 | Member 1 | Planned | Mobile login, kiện theo owner, yêu cầu/hiển thị PIN 6 số/countdown, kết nối API; hiện chỉ Expo starter |
| IOT-01 | Member 2 | Planned | MQTT giả lập song song, schema, Dashboard, thống kê/cảnh báo; helper có source, chưa live Verified |
| INT-01 | Cả hai | Planned | E2E một ngăn, sau đó hai ngăn, correlation và đủ evidence |
| INT-02 | Cả hai | Planned | Best-fit S→M, concurrency, PIN TTL/one-use/scope, offline/reboot/retry, mapping CoreIoT thật |
| QA-01 | Cả hai | Planned | Evidence phần cứng/E2E, đo nguồn và giới hạn sensor; review theo TEST_PLAN |
| DOC-01 | Cả hai | Planned | Cập nhật kết quả thực nghiệm, báo cáo/video và hướng dẫn demo sau tích hợp |

BE-01/Phase 1 và test firmware cũ không chứng minh BE-02 hoặc FW-01…03 đã hoàn thành. [API hiện có](BACKEND_PHASE1.md), [interfaces](INTERFACES.md), [roadmap](ROADMAP.md).

## Phụ thuộc

DEC-01 trước hai đầu ESP-NOW độc lập; HW-01 trước nghiệm thu FW-01; BE-02/FW-01/FW-02/FW-03/GW-01 trước INT-01; INT-01 trước INT-02/QA-01. APP-01 và IOT-01 có thể prototype với fixture ngay sau thống nhất schema, không đợi HIL. API PIN cần cả hai phối hợp trước Mobile/Serial integration.

## Backlog ngoài MVP

Mở rộng node/ngăn, size L, cảm biến chốt/kiện hàng, khóa 12V/relay, OTA, ESP32 local webserver và buzzer chỉ xem xét ở phiên bản sau. Giữ Test 8B/8C làm lịch sử thử nghiệm; không chuyển kết quả thành PASS servo. Không thêm tính năng mở rộng trong lần cập nhật tài liệu.

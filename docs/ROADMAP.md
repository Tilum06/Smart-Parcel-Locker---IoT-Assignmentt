# Roadmap và phân công — MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

**Planned; phân công đề xuất**, điều chỉnh theo tiến độ thực tế. Hai thành viên làm hai đầu firmware song song; CoreIoT dùng dữ liệu giả từ đầu, không chờ Embedded hoàn thành. Bảng phase mô tả thứ tự triển khai, không tự đánh dấu DONE từ tài liệu hoặc source test.

| Phase | Central | Locker Node | CoreIoT / Backend |
|---|---|---|---|
| 0 | Pinout, PlatformIO, protocol | Pinout, PlatformIO, protocol | Chốt telemetry schema |
| 1 | Test ST7789 | Test MG90S | Test MQTT bằng dữ liệu giả |
| 2 | Test keypad | Test MC-38 | Xây dựng Dashboard |
| 3 | LVGL và nhập liệu | Locker Controller | Cập nhật API nhận hàng |
| 4 | ESP-NOW Central | ESP-NOW Locker Node | MQTT Gateway |
| 5 | Xử lý response/event | Phản hồi trạng thái | Mobile App kết nối API |
| 6 | Kiosk Controller | Hoàn thiện hai ngăn | Cảnh báo và thống kê |
| 7 | Tích hợp hai board | Tích hợp hai board | Kiểm tra mapping dữ liệu |
| 8 | USB Serial | Kiểm thử thiết bị thật | Backend/Gateway integration |
| 9 | End-to-end testing | End-to-end testing | CoreIoT dữ liệu thật |

## Phân công đề xuất

| Thành viên | Phạm vi |
|---|---|
| Member 1 — Central Controller | ST7789, LVGL, keypad, Kiosk UI, ESP-NOW phía Central, USB Serial; Mobile App và kết nối API |
| Member 2 — Locker Node | MG90S, MC-38, Locker Controller, ESP-NOW phía Node; CoreIoT Dashboard và MQTT Gateway |
| Cả hai | Pinout, communication protocol, Gateway/Backend integration, integration test, lắp mô hình, báo cáo và demo |

Backend API PIN mới cần cả hai phối hợp; không mặc định đã có chỉ vì Phase 1 chạy được. Module common chỉ sửa sau thống nhất; [Git workflow](GIT_WORKFLOW.md).

## Điều kiện chuyển phase

- Phase 0: [PINOUT](../hardware/PINOUT.md) được kiểm revision/wiring; [protocol](INTERFACES.md) thống nhất schema và các tham số còn mở; hai project target S3, giữ test cũ.
- Phase 1–3: có evidence màn hình/keypad, servo/chốt/nguồn, polarity/debounce cửa; API PIN 6 số/30 giây và kiosk scope được thiết kế/kiểm thử; không lấy mock làm HIL.
- Phase 4–6: ACK/result/door/status tương quan đúng; retry không mở lặp; lỗi/reboot giữ trạng thái an toàn; App và Dashboard có thể dùng fixture trước tích hợp.
- Phase 7–8: radio/Serial/Gateway map đúng DeviceEvent Phase 1, liveness/reconcile và freshness, không giả evidence; hai servo không reset board.
- Phase 9: [test plan](TEST_PLAN.md) đủ evidence gửi/nhận hai ngăn, best-fit, PIN sai/hết hạn/dùng lại, offline/reboot và telemetry thật.

## Điểm xuất phát

Implemented: FastAPI/SQLite Phase 1 và simulator dùng flow mã kiosk cũ; Expo starter; helper MQTT; test radio/button/MC-38/relay. Chưa Verified E2E v2.1 hoặc servo thật. Báo cáo kiểm thử cũ giữ nguyên thời điểm/cấu hình; không suy rằng các phase mới đã hoàn tất. [Backlog](ISSUES.md), [quyết định còn mở](DECISIONS.md).

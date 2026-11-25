# Smart Parcel Locker — MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

Baseline thiết kế ngày **25/11/2026**, nhóm hai thành viên: **hai Yolo UNO ESP32-S3**, hai ngăn **L01=S, L02=M**. Mỗi ngăn có **MG90S 5V 180° + chốt cơ khí** và **MC-38 NC**.

```text
Resident Mobile App ── REST API ── PC: FastAPI + SQLite + Gateway
                                          ├── MQTT ── CoreIoT
                                          └── USB Serial
                                               Central (Node 1)
                                               ├── ST7789 SPI 240×240 / LVGL
                                               ├── Keypad 4×4
                                               └── ESP-NOW ── Locker Node (Node 2)
                                                               ├── L01 S: MG90S + MC-38
                                                               └── L02 M: MG90S + MC-38
```

Backend/Gateway là các module trong **cùng một ứng dụng Python**. Backend quyết định authentication, authorization, cấp ngăn và giao dịch. Central nhập liệu, hiển thị và chuyển tiếp; Locker Node điều khiển servo, đọc cửa. CoreIoT giám sát, telemetry, thống kê, cảnh báo. Hai ESP32 không bắt buộc kết nối Internet trực tiếp.

## Luồng mục tiêu

- **Gửi:** shipper nhập mã phòng, SĐT người nhận, size S/M tại kiosk → Backend xác minh cư dân, reserve atomic và lưu UNLOCK intent → Central → Node → đặt hàng, đóng cửa, xác nhận → Backend yêu cầu LOCK khi đủ điều kiện → hoàn tất khi đủ evidence. S ưu tiên L01, có thể nâng lên L02; M chỉ L02. Không cấp ngăn offline/lỗi/đang dùng/không rõ trạng thái.
- **Nhận:** cư dân đăng nhập Mobile App, chọn kiện của mình và yêu cầu mã → Backend cấp **chuỗi 6 chữ số, TTL 30 giây, một lần dùng** → App hiển thị mã/countdown → nhập tại keypad kiosk → Backend kiểm mã, chủ đơn, hạn và phạm vi kiosk; tiêu thụ mã atomic với tạo giao dịch và UNLOCK intent → lấy hàng, đóng cửa, xác nhận → hoàn tất và giải phóng ngăn khi đủ evidence. Backend không phản hồi thì không mở.

Evidence cần confirmation + chu kỳ OPEN→CLOSED đúng phiên + CLOSED còn mới + LOCK_APPLIED đúng command, không lỗi/offline/unknown. ACK chỉ xác nhận nhận lệnh; LOCK_APPLIED không chứng minh chốt cơ khí đã gài. Không có cảm biến hiện diện kiện hàng hoặc vị trí chốt.

## Trạng thái thực tế

| Nhãn | Ý nghĩa và hiện trạng |
|---|---|
| Implemented | Có source FastAPI/SQLite Phase 1, simulator cục bộ, helper MQTT, firmware thử nghiệm và Expo starter |
| Planned | Luồng Mobile App cấp PIN → kiosk nhập; firmware v2.1 ST7789/LVGL/keypad/servo và Gateway Serial/MQTT tích hợp |
| Verified | Chỉ dùng khi có evidence theo cấu hình cụ thể; kết quả cũ trong báo cáo không phải nghiệm thu v2.1 |
| Backlog | Size L, thêm node/ngăn, khóa 12V/relay, cảm biến chốt/kiện hàng, OTA, ESP32 webserver; ngoài MVP |

**Phase 1 vẫn dùng luồng cũ:** kiosk tạo opaque code, cư dân gửi code qua API nhận hàng. Chưa có API PIN 6 số hoặc Mobile App nghiệp vụ. Central thử nghiệm còn `board=esp32dev`; Test 8B/8C dùng relay/12V. Giữ các thí nghiệm để tham khảo, không coi là implementation v2.1.

## Tài liệu và chạy thử

- [Đặc tả](docs/PROJECT_SPEC.md), [kiến trúc](docs/ARCHITECTURE.md), [quyết định](docs/DECISIONS.md), [interfaces](docs/INTERFACES.md).
- [Pinout chính thức của dự án](hardware/PINOUT.md), [BOM](hardware/README.md), [roadmap/phân công](docs/ROADMAP.md), [backlog](docs/ISSUES.md), [Git workflow](docs/GIT_WORKFLOW.md).
- [Backend Phase 1: setup Windows, API, tests](docs/BACKEND_PHASE1.md), [simulator cục bộ](backend/demo/README.md), [test plan](docs/TEST_PLAN.md).

Pinout đã đối chiếu nguồn OhStem nhưng **chưa xác nhận bằng kiểm thử trên hai board thực tế**. Chỉ PINOUT.md chứa bảng đấu chân; README module dẫn chiếu tới đó.

## Tài liệu lịch sử

Giữ nguyên [đặc tả v1.2](PROJECT_SPEC_Smart_Parcel_Locker_v1.2.md), [Git sync review 23/11](docs/GIT_SYNC_REVIEW_2026-11-23.md) và các báo cáo/test cũ ở workspace gốc (SETUP_REPORT.md, M0_REVISION_REPORT.md, docs/M0_STATUS.md, TEST8A/B/C; không có trong tree kế thừa). Cấu hình/kết quả trong đó là ảnh chụp lịch sử, không thay thế baseline v2.1. [Tổng kết cập nhật](docs/DOCUMENTATION_V2_1_REVIEW.md).

# Đặc tả — Smart Parcel Locker MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

**Planned baseline, 25/11/2026.** Tài liệu mô tả mục tiêu; API đã có xem [Backend Phase 1](BACKEND_PHASE1.md). Implemented = có source; Planned = chưa tích hợp; Verified = có evidence theo cấu hình; Backlog = ngoài MVP.

## Cấu hình chính thức

| Thành phần | MVP v2.1 |
|---|---|
| Central, Node ID 1 | Yolo UNO ESP32-S3; ST7789 SPI 240×240, LVGL, keypad ma trận 4×4; ESP-NOW và USB Serial |
| Locker Node, Node ID 2 | Yolo UNO ESP32-S3, quản lý đồng thời cả hai ngăn |
| L01 / L02 | L01 size S; L02 size M; kích thước cơ khí cm chưa đo/chốt |
| Mỗi ngăn | MG90S 5V 180° + chốt cơ khí; MC-38 NC đọc cửa |
| PC | FastAPI + SQLite + Gateway Serial/MQTT cùng ứng dụng Python |
| Client | Resident Mobile App qua REST API; Web App production chưa triển khai |
| CoreIoT | Giám sát, telemetry, thống kê, cảnh báo qua Gateway PC |

Không dùng khóa điện 12V, relay, cảm biến kiện hàng, microswitch vị trí chốt, size L hoặc board thứ ba trong MVP. Những thiết bị/thí nghiệm cũ được giữ nguyên; chỉ xem xét mở rộng ở phiên bản sau.

Backend quản lý authentication, authorization, cấp ngăn, dữ liệu và giao dịch. Admin tạo tài khoản cư dân gắn mã phòng và SĐT; input shipper không tự tạo cư dân. Mã phòng là chuỗi số giữ số 0 đầu. Central chỉ thu input, hiển thị kiosk, chuyển request/command/event; không điều khiển servo trực tiếp, không tự cấp ngăn hoặc xác thực quyền nhận hàng. Node thực thi lệnh và báo cửa/kết quả servo. Gateway chỉ làm transport; CoreIoT không thay SQLite làm nguồn sự thật nghiệp vụ.

## Gửi hàng

1. Shipper chọn gửi hàng trên kiosk.
2. Nhập mã phòng.
3. Nhập SĐT người nhận.
4. Chọn size S hoặc M.
5. Central chuyển yêu cầu qua USB Serial tới Backend.
6. Backend xác minh cư dân và cấp ngăn: S ưu tiên L01, có thể dùng L02 nếu L01 không khả dụng; M chỉ L02. Loại ngăn offline, lỗi, đang dùng hoặc chưa xác định trạng thái. Reserve atomic để không cấp trùng.
7. Backend lưu UNLOCK intent rồi gửi qua Central/ESP-NOW đến Node.
8. Node điều khiển servo đúng ngăn, phản hồi kết quả.
9. Shipper đặt kiện, đóng cửa và xác nhận tại kiosk.
10. Node báo trạng thái MC-38 và chu kỳ cửa.
11. Backend yêu cầu LOCK khi có confirmation và CLOSED hợp lệ; Node từ chối LOCK khi OPEN/UNKNOWN.
12. Backend chỉ hoàn tất khi đủ bằng chứng hợp lệ, chuyển STORED/OCCUPIED.
13. Cư dân có thể xem kiện trên Mobile App khi phần tích hợp được triển khai.

## Nhận hàng — luồng mới Planned

1. Cư dân đăng nhập Mobile App.
2. Xem danh sách kiện của mình và chọn kiện cần nhận.
3. App yêu cầu Backend cấp mã nhận hàng.
4. Backend tạo **chuỗi 6 chữ số**, giữ số 0 đầu, TTL **30 giây**.
5. App hiển thị mã và countdown; thời gian Backend quyết định hiệu lực.
6. Cư dân nhập mã trên keypad kiosk; Central chuyển mã tới Backend qua USB Serial.
7. Backend xác thực mã, quyền sở hữu, kiện, thời hạn và phạm vi kiosk được phép sử dụng; kiểm trạng thái ngăn/thiết bị.
8. Nếu hợp lệ, Backend tiêu thụ mã một lần, tạo giao dịch PICKUP và lưu UNLOCK intent trong cùng transaction; gửi UNLOCK đúng ngăn.
9. Cư dân lấy hàng, đóng cửa và xác nhận tại kiosk. Contract xác nhận kiosk gắn giao dịch và quyền tương ứng là công việc tiếp theo, không phải endpoint Phase 1 đã có.
10. Node gửi trạng thái cửa/kết quả servo; Backend yêu cầu LOCK khi đủ điều kiện, hoàn tất và giải phóng ngăn khi đủ evidence.

Mã dùng bộ sinh số ngẫu nhiên phù hợp bảo mật, không trùng giữa các phiên active trong cùng phạm vi xác thực; xử lý collision và cấp/tiêu thụ đồng thời ở Backend. Giới hạn số lần nhập sai và tốc độ thử tại kiosk; ngưỡng v2.1 chưa chốt. Không lưu plaintext lâu dài hoặc vào log/audit/telemetry; thiết kế verifier bảo vệ PIN ngắn phải được review. Mã hết hạn/đã dùng không được tái sử dụng. Backend mất phản hồi thì không mở; không TOTP offline. Retry không tiêu thụ mã hoặc tạo UNLOCK lần hai.

## Evidence và giới hạn vật lý

Door state OPEN/CLOSED/UNKNOWN độc lập với servo action IDLE/UNLOCK_APPLIED/LOCK_APPLIED/ERROR/UNKNOWN. ACK ≠ kết quả servo; LOCK_APPLIED ≠ chốt gài cơ khí. Không có latch_feedback hoặc phép đo hiện diện kiện.

Hoàn tất cần confirmation + OPEN→CLOSED đúng transaction/boot/sequence + CLOSED còn mới + LOCK_APPLIED đúng command, không lỗi/offline/unknown. Phase 1 dùng freshness 10 giây; không tự áp thời gian đó làm mọi timeout transport. Lỗi/reboot/mất kết nối giữ reservation và yêu cầu reconcile; không tự AVAILABLE hoặc phát lại UNLOCK mù.

## Hiện trạng

Implemented: backend Phase 1, simulator localhost theo API cũ, Expo starter, helper MQTT và firmware test. Planned: PIN từ App nhập kiosk, API/contract mới, kiosk LVGL/keypad, servo controller và Gateway thật. Chưa có evidence nghiệm thu v2.1. [Pinout](../hardware/PINOUT.md), [interfaces](INTERFACES.md), [roadmap](ROADMAP.md), [test plan](TEST_PLAN.md).

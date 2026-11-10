# Sổ quyết định — baseline revision 1.3

Ngày cập nhật 10/11/2026. Nguồn phê duyệt mới: task người dùng “Finalize M0 Baseline”, §2–4. D-ID tiếp tục theo bảng §2.2 của v1.2, không đổi sang ID ở §15 bị lệch. Đóng chính sách không đồng nghĩa đã hiện thực/đo/test. Không tự ghi reviewer A/B đã ký wire contract; phê duyệt phạm vi do người dùng cung cấp.

## 1. Đã chốt

| ID | Quyết định áp dụng | Nguồn / lý do | Ảnh hưởng kỹ thuật |
|---|---|---|---|
| C-01 | 3 ESP32: #1 L01/L02, #2 L03/L04, #3 Central | v1.2 + approved §2.1 | Node chung firmware, cấu hình khác; Central một project |
| D-02 | Shipper chọn S/M/L theo bảng size được duyệt | v1.2 giữ nguyên | Chưa lấy kích thước cm mẫu làm số đo chế tạo |
| D-02A | 2S + 1M + 1L | v1.2 giữ nguyên | Fixture và tủ đủ 4 ngăn |
| D-02B | Best Fit và nâng size | v1.2 giữ nguyên | Chọn size nhỏ nhất đủ; lưu requested_size/allocated_locker_size |
| D-03 | ĐÓNG: mỗi ngăn có microswitch báo chốt gài; tổng 4 | Approved §2.4 | Latch ENGAGED/NOT_ENGAGED/UNKNOWN; không suy từ servo/ACK; NOT_ENGAGED không chứng minh mở hoàn toàn. Model/debounce/gá thuộc D-09 |
| D-04 | ĐÓNG chính sách: admin tạo trước cư dân gắn phòng số + SĐT + credentials | Approved §2.5 | Đối chiếu đúng người trước reserve, không tự tạo từ input shipper; phòng/SĐT không làm password. Chi tiết format/normalization/hash/session ở P-03 |
| D-05 | ĐÓNG chính sách: nhận qua Web App cần mã phiên ngắn hạn trên kiosk | Approved §2.6 | Bind kiosk/phiên nhận, ownership, một lần dùng, giới hạn thử, không log mã; có thể bị chia sẻ từ xa. TTL/format/attempt budget ở P-03/D-06 |
| D-07 | ĐÓNG transport: USB Serial, UTF-8 JSON Lines + LF | Approved §2.3 | Không debug text trên protocol, không thực thi line dở/sai; 115200 và 2048 byte chỉ giá trị thử P-01 |
| C-02 | Không cảm biến hàng | v1.1/v1.2 + approved §2.1 | Chỉ xác nhận người dùng; không tuyên bố cảm biến biết ngăn trống |
| C-03 | Mỗi ngăn servo/chốt + door sensor + latch microswitch | Approved §2.4, cập nhật C-03 cũ | 4 servo, 4 cửa, 4 latch; tách bằng chứng vật lý |
| C-04 | PC Python + FastAPI + SQLite; Backend/Gateway cùng ứng dụng, một HTTP server | Approved §2.2 | API/domain/persistence/adapter/Serial/MQTT là module logic; không microservices/broker nội bộ/server Gateway riêng; worker không chặn HTTP/ghi domain trực tiếp |
| C-05 | Không xác thực shipper; cư dân login và mở đúng quyền | v1.2 + approved §2.5/2.6 | Kiosk device/session vẫn cần auth; không đồng nghĩa xác thực người giao |
| C-06 | ESP-NOW, LVGL, ESP32 webserver, CoreIOT hai chiều/RuleChain/notification, OTA | v1.2 + approved §2.1/2.8 | Giữ mã công nghệ, không tính điểm từ tài liệu; ưu tiên thử OTA Central, phạm vi cuối D-10 mở |
| C-07 | Không SMS OTP, cảm biến hàng, TinyML trong MVP; giữ các loại trừ v1.2 khác | Approved §2.1 | Mã phiên kiosk không phải SMS OTP; vẫn có notification Web App/CoreIOT |
| C-08 | Task chỉ sửa baseline tài liệu, không cài/push/remote/credentials thật | Approved §7/9 | Không triển khai full firmware/API/Web App, giữ snapshot lịch sử |

## 2. Quyết định còn mở

| ID | Phần chưa chốt | Owner | Task / gate ảnh hưởng |
|---|---|---|---|
| D-01 | Kích thước kiện/ngăn và khoảng hở thật S/M/L | A, B review | HW-01 chế tạo cuối; FW-03 bảng size; không chặn thiết kế BE-01 theo category size |
| D-06 | Timeout/lease/retry/giữ ngăn/cửa, cửa sổ dedup; TTL mã phiên phối hợp P-03 | Both | FW-02/GW-01/BE-02 trước nghiệm thu M2; INT-01; không tự hết hạn rồi AVAILABLE |
| D-08 | Recovery đầy đủ sau boot, xác nhận sai, admin exception; đặc biệt Backend đứt khi cửa đang mở | Both | Recovery tối thiểu ở BE-01/02 + FW-02/GW-01 M2; BE-03 M4 mở rộng. Chưa chọn hành vi actuator ngoại tuyến |
| D-09 | Board YoloUNO/revision, model servo/nguồn/GPIO/góc/debounce/cơ khí, microswitch và wiring | A | HW-01 điện, FW-01/03 build/upload; không chọn pin/board profile đoán |
| D-10 | Phạm vi OTA cuối, partition/flash/RAM, Wi-Fi/ESP-NOW đồng thời, recovery và đối chiếu T14 giảng viên | A, B hỗ trợ | Thử sớm Central ở M1 nếu board sẵn; FW-05/QA-01 nghiệm thu cuối; không bảo đảm chỉ Central đủ 2 điểm, không loại mở rộng node |

D-03/D-04/D-05/D-07 đã đóng chính sách; các chi tiết kỹ thuật chưa đo không bị đóng theo. Mã D-08/D-09 ở §15 của v1.2 không được dùng: canonical D-08=recovery, D-09=hardware, D-10=OTA. Nguồn gốc giữ nguyên làm lịch sử.

## 3. Trạng thái các đề xuất triển khai hiện có

| ID | Trạng thái sau revision | Chi tiết còn cần duyệt / đo | Owner / gate |
|---|---|---|---|
| P-01 | CHỐT transport USB Serial theo D-07; còn REVIEW wire v1/M1 subset/M2 integration | Source/target, ACK không sensor, STATUS/event mapping đã ghi thống nhất trong INTERFACES; byte/enum, session invalidation, retry, buffer, baud và các ngưỡng chưa được test/duyệt wire cuối | Both, DEC-01 từng phần → FW-02/GW-01/INT-01 |
| P-02 | CHỐT Python/FastAPI/SQLite và PlatformIO/C/C++/Arduino | Python/dependency/lib version, board profile/revision/flash/partition, Web App framework và lockfile chưa chọn/đo | B PC, A firmware; trước build tương ứng |
| P-03 | CHỐT policy cư dân tạo trước + mã phòng số + mã phiên kiosk | Độ dài/chuẩn hóa phòng-SĐT, uniqueness, hash password/reset/session, kiosk provisioning, code length/alphabet/TTL/attempt budget/digest, local/RPC auth, bảo vệ dữ liệu lưu | B chủ trì, A kiosk; BE-01/02, WEB-01, FW-03/04, IOT-01 |
| P-04 | CHỐT mapping L01=S, L02=S, L03=M, L04=L | Tie-break ID nhỏ nhất là đề xuất, chưa tự coi đã duyệt | Both review trước allocator fixture nghiệm thu BE-01 |
| P-05 | CÒN MỞ | Tuổi trạng thái per ngăn, heartbeat/STATUS sampling, boot/epoch, startup reconciliation và nhận diện door cycle đúng phiên | Both; FW-02/GW-01/BE-02/INT-01 |

Các mức M1 và M2/M3 dùng chung v1 trong [INTERFACES](INTERFACES.md), không phải protocol prototype tách rời. Prototype bench không cấp quyền mở nghiệp vụ. Không claim exactly-once, command revocation hay recovery đã chạy khi chưa có implementation/test.

## 4. Quy trình review và bằng chứng

Quyết định chính sách đã duyệt ở task này được ghi ngày/nguồn như trên. Wire/parameter review tiếp theo ghi lựa chọn, reviewer thật, ngày, fixture/build/số đo, ảnh hưởng tài liệu/test và phần được unblock; không giả chữ ký A/B. DEC-01 đóng từng gate cần cho nhánh công việc, không đòi cloud/OTA hoàn tất trước HW-01 hoặc BE-01 thiết kế. Mọi thay đổi tiếp theo cập nhật [PROJECT_SPEC](PROJECT_SPEC.md), [INTERFACES](INTERFACES.md), [TEST_PLAN](TEST_PLAN.md) và Issue tương ứng.

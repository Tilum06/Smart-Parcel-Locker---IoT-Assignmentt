# Interfaces — MVP v2.1

Transport và PIN v2.1 là **Planned/DRAFT**, chưa phải wire contract đã kiểm chứng. REST API có source hiện tại được mô tả riêng tại [BACKEND_PHASE1](BACKEND_PHASE1.md).

## Các chặng giao tiếp

| Chặng | Transport | Phạm vi |
|---|---|---|
| Resident Mobile App ↔ Backend | REST API | Login, danh sách kiện thuộc mình, yêu cầu PIN, đọc trạng thái |
| PC ↔ Central ID 1 | USB Serial, JSON Lines/LF, UTF-8, baud ban đầu 115200 | Request, command, response, event |
| Central ID 1 ↔ Locker Node ID 2 | ESP-NOW | UNLOCK, LOCK, GET_STATUS; ACK, COMMAND_RESULT, DOOR_EVENT, STATUS, ERROR |
| Gateway ↔ CoreIoT | MQTT | Giám sát, telemetry, thống kê, cảnh báo; chưa tích hợp production |

L01/L02 đều thuộc Node 2. Central định tuyến, không xác thực mã hoặc quyết định cấp ngăn. ESP32 không cần Internet trực tiếp.

## Envelope ESP-NOW cần thống nhất

| Field khái niệm | Ý nghĩa |
|---|---|
| protocol_version | Version schema; giá trị/số byte chưa chốt |
| source_node_id / target_node_id | Nguồn/đích 1 hoặc 2, khớp peer được cấu hình |
| locker_id | L01/L02 cho từng ngăn; scope GET_STATUS toàn node cần chốt |
| request_id / command_id | Correlation, timeout/retry/dedup; quy tắc ánh xạ ID cần thống nhất |
| transaction_id | Correlation Backend; status ngoài giao dịch cần quy tắc riêng |
| boot_id | Nhận biết reboot, vô hiệu evidence boot cũ |
| sequence | Phát hiện lặp/đảo thứ tự trong boot; độ rộng/wrap policy cần chốt |
| message_type | Command hoặc response/event đã liệt kê |
| payload | Action, door state, servo result hoặc error theo type |

Đây là field ngữ nghĩa, **không phải struct hoặc JSON byte layout đã chốt**. Không gửi raw C++ struct phụ thuộc padding. Hai thành viên phải chốt serialization/endianness/length validation trước khi code độc lập.

| Type | Ý nghĩa | Không được suy ra |
|---|---|---|
| ACK | Đã nhận lệnh | Servo thành công, cửa đóng, chốt gài |
| COMMAND_RESULT | Kết quả servo: UNLOCK_APPLIED/LOCK_APPLIED hoặc lỗi | Vị trí chốt cơ khí |
| DOOR_EVENT | MC-38 OPEN/CLOSED/UNKNOWN sau debounce | Có/không có kiện hàng |
| STATUS | Snapshot thiết bị/cửa/servo/liveness theo schema sẽ chốt | Hoàn tất giao dịch chỉ từ snapshot |
| ERROR | Lỗi có correlation khi có thể | Được phép giải phóng ngăn |

Door state và servo action độc lập; không latch_feedback/ENGAGED giả. Node từ chối LOCK nếu OPEN/UNKNOWN. Backend cần confirmation + OPEN→CLOSED đúng phiên + CLOSED mới + LOCK_APPLIED đúng command, không lỗi/offline/unknown. Freshness Phase 1 là 10 giây; timeout radio/Serial chưa chốt.

## PC ↔ Central và adapter Phase 1

JSON Lines UTF-8, một message mỗi dòng, baud khởi đầu 115200. Cần chốt envelope, line limit, framing khi dòng lỗi, version handshake, correlation, reconnect, backpressure, timeout/retry và đồng bộ thời gian. Dòng debug phải được xử lý để parser không hiểu nhầm là event nghiệp vụ. COM port là cấu hình máy, không commit.

| Wire mục tiêu | Boundary Python đã có | Công việc còn lại |
|---|---|---|
| UNLOCK / LOCK | DeviceAdapter.send(command_id, transaction_id, locker_id, action) | Adapter thật và dedup command |
| ACK | DeviceEvent.kind='ACK' | Kiểm peer/version/correlation |
| COMMAND_RESULT | UNLOCK_APPLIED, LOCK_APPLIED, ERROR | Validate result rồi map, không biến ACK thành APPLIED |
| DOOR_EVENT | DOOR_OPEN, DOOR_CLOSED, SENSOR | Event ID, boot, sequence, thời gian tin cậy/freshness |
| STATUS / GET_STATUS | Chưa có mapper/dispatch GET_STATUS hoàn chỉnh | Heartbeat, trạng thái ngoài transaction và reconcile |

`devices.ingest` chỉ cho adapter tin cậy gọi nội bộ; không tạo HTTP sensor endpoint cho production. `PendingDeviceAdapter` không sinh thành công giả; `dispatch_pending` chưa tự chạy startup. Retry/reboot/mất kết nối không được mở lại mù hoặc auto AVAILABLE. Backend không phản hồi thì Central không tự mở.

## REST hiện có và thay đổi v2.1

Phase 1 prefix `/api/v1`; bearer + role/ownership; mutation nghiệp vụ dùng `X-Request-ID`. Đường dẫn/response thực tế xem [API contract Phase 1](BACKEND_PHASE1.md#api-contract); không dùng endpoint sơ bộ trong tài liệu cũ để tích hợp.

| Nghiệp vụ | Implemented Phase 1 | Planned v2.1 |
|---|---|---|
| Cấp mã | KIOSK/ADMIN POST /api/v1/kiosk-sessions với parcel_id | RESIDENT chủ kiện yêu cầu mã trên App |
| Định dạng | secrets.token_urlsafe(16), opaque code, hash trong DB | Chuỗi 6 chữ số giữ 0 đầu; CSPRNG; không collision giữa phiên active cùng scope |
| Xác thực | RESIDENT POST /api/v1/pickups/{parcel_id} với session_id + code | Kiosk tin cậy chuyển PIN keypad; Backend tìm phiên, kiểm owner/parcel/expiry/kiosk scope |
| TTL/one-use | 30 giây, tối đa 5 lần sai theo phiên | 30 giây, one-use; hạn mức sai/rate limit kiosk phải chốt, chưa có implementation |
| Xác nhận lấy | RESIDENT POST /api/v1/pickups/{parcel_id}/confirm | Xác nhận tại kiosk cần contract/authorization gắn đúng transaction |

Chưa đặt tên endpoint mới như thể đã triển khai. Trước sửa API cần chốt request/response/lỗi, kiosk identity/scope, parcel binding, cấp lại/thu hồi, collision handling và migration. Tiêu thụ PIN + tạo PICKUP + lưu UNLOCK intent phải atomic; retry không mở lần hai. Không lưu PIN plaintext lâu dài hoặc vào log; verifier phải tính tới không gian 6 chữ số. App countdown chỉ là UX; Backend kiểm expiry. Không TOTP offline.

## Tham số chưa chốt

MAC, channel, packet serialization, timeout, retry, deduplication và bảo vệ ESP-NOW phải được cả hai thống nhất. Channel 6/broadcast/không mã hóa trong test hiện có là cấu hình thí nghiệm, không được kế thừa thành policy MVP. Chốt nguồn thời gian/gateway timestamp và chống replay trước khi nhận evidence thật. [DECISIONS](DECISIONS.md).

Telemetry schema/CoreIoT mapping là Planned; không chứa SĐT, mã phòng, PIN, password, token hoặc verifier. CoreIoT không cấp quyền mở tủ độc lập Backend.

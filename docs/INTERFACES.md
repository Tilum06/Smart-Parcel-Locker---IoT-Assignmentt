# Hợp đồng giao tiếp — baseline revision 1.3

Ngày 10/11/2026. USB Serial/JSON Lines và một ứng dụng Python/FastAPI đã được duyệt. Tài liệu này sửa draft v1 để source/target, ACK/STATUS, event và internal adapter thống nhất. **Byte layout/enum/session mechanism và tham số dưới đây là thiết kế cần DEC-01 review, chưa có implementation/test.** Không gán chữ ký A/B hoặc tuyên bố exactly-once. [DECISIONS](DECISIONS.md) phân biệt policy đã đóng và phần còn mở.

## 1. Hai mức cùng protocol v1

| Mức | Mục đích | Tập message và điều kiện |
|---|---|---|
| M1 Prototype Contract | Bench một ngăn, servo/cửa/microswitch và transport đơn giản | COMMAND UNLOCK/LOCK/GET_STATUS, ACK, ERROR, DOOR_EVENT, STATUS; cùng schema/ID/enum v1 dưới đây; epoch=0 chỉ bench, fixture không tạo đơn thật |
| M2–M3 Integration Contract | Thực hiện nghiệp vụ, chống lặp và đối chiếu kết quả | M1 + HEARTBEAT, CONTROL_SESSION, LATCH_FEEDBACK, handshake, transaction mapping, epoch/lease, dedup/freshness/recovery tối thiểu; không cho epoch=0 mở nghiệp vụ |

M1 không tạo protocol khác để viết lại; fixture dùng serializer và contract v1, giữ trường chưa kích hoạt ở giá trị bench quy định. Bước M1 không chứng nhận quyền nghiệp vụ hoặc phục hồi M2. Không triển khai M2 actuator trước review session validity/security/timeout.

## 2. ID, địa chỉ và bằng chứng

- `request_id`: UUID 128-bit cho mỗi thao tác; retry cùng thao tác giữ nguyên ID/payload. Serial/API là chuỗi UUID, radio 16 byte; request ID **không cấp quyền**.
- `transaction_id`: UUID của phiên gửi/nhận do Backend tạo. UNLOCK, LOCK và confirmation có request ID riêng, cùng transaction. Radio không mang transaction_id; Backend/Gateway lưu mapping request_id + locker + epoch → transaction trước send.
- Radio có `source_node_id` và `target_node_id` riêng. COMMAND: 3→1 hoặc 3→2; ACK/ERROR/STATUS/DOOR_EVENT/LATCH_FEEDBACK/HEARTBEAT: 1/2→3. CONTROL_SESSION: 3→1/2. Không còn trường `node_id` mơ hồ trong contract hiện hành.
- Serial device envelope giữ nguyên **logical radio endpoints** trên: PC relay COMMAND dưới danh nghĩa controller 3 tới node đích; không coi PC là node 0 hay đổi target thành 3 chỉ vì đi qua USB. Sender vật lý/actor PC được xác thực bằng session riêng. Message kiosk/HELLO thuộc envelope link riêng dùng `kiosk_id`/`controller_id`, không giả là radio frame.
- `locker_id`: radio 1…4, Serial L01…L04; mapping cố định #1 L01/L02, #2 L03/L04. HEARTBEAT cấp node dùng 0/null, không COMMAND mở broadcast. Kiểm peer vật lý + source/target + locker mapping trước thực thi.
- `boot_id`: phiên boot sender; `sequence`: uint32 tăng trong boot của sender. Không thay sequence khi forward. Wrap, sinh boot ID không trùng và cửa sổ out-of-order cần duyệt P-01/P-05; reboot làm mất bảo đảm dedup phải dừng và reconcile.
- PC chưa gửi radio: COMMAND Serial có boot_id/sequence=null; Central gán boot/sequence của chính nó khi encode radio và có thể echo metadata forward cho trace. Gateway không giả counter Central. ACK/STATUS/event từ node giữ boot/sequence node. expected_node_boot_id=0 chỉ cho GET_STATUS khám phá; UNLOCK/LOCK phải khớp boot đã quan sát, kể cả bench.
- `ACK RECEIVED`: nhận/chấp nhận xử lý; `ACK APPLIED`: áp dụng tín hiệu điều khiển. Cả hai **không chứa bằng chứng cửa/chốt**. Callback radio/ghi serial thành công chỉ là transport delivery, không được biến thành node ACK.
- `door_state`: OPEN/CLOSED/UNKNOWN. `servo_command_state`: IDLE/UNLOCK_APPLIED/LOCK_APPLIED/ERROR/UNKNOWN. `latch_feedback`: ENGAGED/NOT_ENGAGED/UNKNOWN từ microswitch. NOT_ENGAGED không chứng minh chốt mở hoàn toàn. Không dùng trường lock_state=UNLOCKED hoặc suy latch từ servo.

## 3. Radio v1 — draft layout dùng chung

Little-endian, encode/decode tường minh, không gửi C struct có padding. Header mới **32 byte** (thêm source/target riêng thay node_id cũ), payload budget ≤192, tổng thiết kế ≤224 byte. Đây là budget draft, chưa phải giới hạn radio được xác minh. Draft cũ chưa có code nên sửa layout trước khi đóng v1; không tự nhận tương thích byte với draft 31-byte trong snapshot lịch sử.

| Thứ tự | Trường | Byte |
|---|---|---:|
| 1 | version=1 | 1 |
| 2 | message_type | 1 |
| 3 | flags=0 | 1 |
| 4 | reserved=0 | 1 |
| 5 | source_node_id | 1 |
| 6 | target_node_id | 1 |
| 7 | locker_id | 1 |
| 8 | sequence sender | 4 |
| 9 | request_id, 0 cho event tự phát | 16 |
| 10 | boot_id sender | 4 |
| 11 | payload_length | 1 |

Byte fields/type enum đều cần review round-trip trước FW-02. Byte order UUID là 16 byte theo thứ tự hex của UUID canonical, không dùng byte-swap theo native GUID của OS.

| Type / enum draft | Payload thiết kế | Mức |
|---|---|---|
| COMMAND=1 | operation_code uint8: UNLOCK=1, LOCK=2, GET_STATUS=3; expected_node_boot_id uint32; command_epoch UUID16 | M1/M2 |
| ACK=2 | operation_code uint8; stage uint8 RECEIVED=1/APPLIED=2; request ID gốc ở header, không sensor fields | M1/M2 |
| ERROR=3 | error_code uint16; request ID gốc nếu biết; không stacktrace/secret | M1/M2 |
| DOOR_EVENT=4 | door_state uint8; observed_epoch UUID16; header request ID=0 | M1/M2 |
| DEVICE_HEARTBEAT=5 | uptime_ms uint32; firmware_version UTF-8 zero-padded 16 byte; locker=0 | M2 |
| STATUS=6 | door/servo/latch mỗi trường uint8; sampled_uptime_ms uint32; observed_epoch UUID16; last_command_request_id UUID16 (0 nếu không biết); control_generation uint32; lease_remaining_ms uint32 | M1/M2 |
| CONTROL_SESSION=7 | action INSTALL=1/REVOKE=2 uint8; generation uint32; expected_node_boot_id uint32; command_epoch UUID16; lease_ms uint32 | M2 draft cần review |
| LATCH_FEEDBACK=8 | latch_feedback uint8; observed_epoch UUID16; header request ID=0 | M2; M1 đọc latch trong STATUS |

Enums trạng thái draft: door UNKNOWN=0/OPEN=1/CLOSED=2; servo UNKNOWN=0/IDLE=1/UNLOCK_APPLIED=2/LOCK_APPLIED=3/ERROR=4; latch UNKNOWN=0/ENGAGED=1/NOT_ENGAGED=2. ACK operation_code 4=INSTALL_SESSION, 5=REVOKE_SESSION cho CONTROL_SESSION; không dùng chúng làm COMMAND opcode.

STATUS header có request_id của COMMAND/CONTROL_SESSION gây ra snapshot hoặc request GET_STATUS đang trả lời; payload last_command_request_id là lệnh actuator gần nhất node thực sự áp dụng. Query GET_STATUS và control-session action không được ghi đè last_command_request_id. Snapshot đọc cảm biến hiện thời, không lấy ACK payload hoặc cache PC làm sensor mới; giữ boot/sequence/sample time khi relay. observed_epoch là grant còn hiệu lực tại thời điểm lấy mẫu, bằng 0 khi chưa install/đã revoke/expire; lease_remaining_ms=0 khi không còn grant. control_generation là generation cao nhất node đã nhận cho locker trong boot, kể cả đã revoke, cho phép reconcile sau PC restart. M1 dùng 0 cho ba trường grant này; integration không dùng epoch 0 để dựng bằng chứng completion của phiên.

Sai version/length/enum/flags/peer/source-target/locker thì drop/log lỗi có giới hạn hoặc ERROR khi đã xác định request hợp lệ; không actuator. Error enum draft: INVALID_MESSAGE=1, UNSUPPORTED_VERSION=2, WRONG_NODE_OR_LOCKER=3, REQUEST_CONFLICT=4, BUSY=5, DEVICE_FAULT=6, STATE_UNKNOWN=7, TIMEOUT=8, DOOR_NOT_CLOSED=9, STALE_COMMAND=10. Pairing, bảo vệ peer/anti-replay, radio channel và coexistence Wi-Fi cần P-01/P-03/D-09 review; MAC list không tự đủ xác thực.

## 4. Serial USB và ví dụ thống nhất

UTF-8 JSON Lines kết thúc LF đã duyệt. 115200 baud thử nghiệm, 8N1 đề xuất; giới hạn thử 2048 byte **bao gồm LF**, buffer/baud cần kiểm chứng trên board/USB. Không debug text trên protocol. Parse một object khi line hoàn chỉnh; line quá dài discard đến LF, JSON/schema sai trả lỗi có rate limit và không thực thi. Không log raw line có SĐT hoặc mã phiên.

Ví dụ giả cùng transaction; COMMAND đầu vào PC chưa có counter radio, còn ACK/STATUS giữ boot_id/sequence thực từ node:

```json
{"version":1,"message_type":"COMMAND","source_node_id":3,"target_node_id":1,"locker_id":"L01","request_id":"12f86249-d1f5-4b45-ae7c-b1a7e66286ae","transaction_id":"8ebc352a-2974-4fe0-a7b3-97e0fa3ce41b","boot_id":null,"sequence":null,"payload":{"command":"UNLOCK","expected_node_boot_id":101,"command_epoch":"a5072151-5ec5-43c5-a7c5-77e2c36110a1"}}
```

```json
{"version":1,"message_type":"ACK","source_node_id":1,"target_node_id":3,"locker_id":"L01","request_id":"12f86249-d1f5-4b45-ae7c-b1a7e66286ae","transaction_id":"8ebc352a-2974-4fe0-a7b3-97e0fa3ce41b","boot_id":101,"sequence":44,"payload":{"command":"UNLOCK","stage":"APPLIED"}}
```

```json
{"version":1,"message_type":"STATUS","source_node_id":1,"target_node_id":3,"locker_id":"L01","request_id":"12f86249-d1f5-4b45-ae7c-b1a7e66286ae","transaction_id":"8ebc352a-2974-4fe0-a7b3-97e0fa3ce41b","boot_id":101,"sequence":45,"payload":{"door_state":"CLOSED","servo_command_state":"UNLOCK_APPLIED","latch_feedback":"NOT_ENGAGED","sampled_uptime_ms":12000,"observed_epoch":"a5072151-5ec5-43c5-a7c5-77e2c36110a1","last_command_request_id":"12f86249-d1f5-4b45-ae7c-b1a7e66286ae","control_generation":7,"lease_remaining_ms":8000}}
```

ACK JSON chỉ map ACK radio, không tự thêm sensor. STATUS riêng giữ bằng chứng của node. NOT_ENGAGED ở ví dụ chưa chứng minh đã mở hoàn toàn, cửa vẫn CLOSED; transaction chưa được coi đã có door cycle. Door/latch event tự phát Serial có request_id=null, transaction_id chỉ được bổ sung khi Backend mapping observed_epoch hợp lệ; chưa map thì null, không gán theo “lệnh gần nhất”.

Link envelope riêng: version, message_type, request_id UUID, controller_id=3, kiosk_id, link_session_id (khi đã handshake), transaction_id khi có, payload. HELLO/HELLO_ACK trao capabilities/contract_level PROTOTYPE hoặc INTEGRATION, controller boot, link_session_id mới, không dùng ID như credential. Backend/kiosk provisioning và schema auth cụ thể còn P-03.

| Message link | Payload tối thiểu / kết quả |
|---|---|
| DEPOSIT_REQUEST | room_code chuỗi số, recipient_phone chuỗi, parcel_size S/M/L; trả RESULT với acceptance/error và transaction/parcel/ngăn/size |
| DEPOSIT_CONFIRM | parcel_id và transaction_id của phiên kiosk; chuyển domain event DEPOSIT_CONFIRMED_BY_SHIPPER |
| PICKUP_SESSION_REQUEST | kiosk_id, yêu cầu phiên nhận mới; không dùng thông tin shipper làm auth |
| PICKUP_SESSION_RESULT | pickup_session_id, mã bí mật chỉ cho display kiosk, expiry/attempt policy đã duyệt; không đưa vào log/telemetry công khai |
| RESULT | request_id gốc, trạng thái ACCEPTED/PENDING/REJECTED/COMPLETED theo nghiệp vụ, error nếu có; ACCEPTED không phải đã mở |
| HELLO/HELLO_ACK | link session/capabilities/version/boot; schema chi tiết review trước GW-01 integration |

## 5. Mapping sensor, command result và event nghiệp vụ

| Nguồn | Serial / service event | Quy tắc |
|---|---|---|
| Radio ACK | ACK → DEVICE_ACK | Giữ request/source/target/boot/sequence/stage; không sensor; không hoàn tất đơn |
| Radio STATUS | STATUS → DEVICE_STATUS | Giữ query/command request ID và last_command_request_id, sample time/epoch; Backend kiểm freshness |
| Radio DOOR_EVENT | DOOR_EVENT → DOOR_STATE_CHANGED | request_id null; gắn đúng active epoch/boot, ghi OPEN rồi CLOSED đúng phiên |
| Radio LATCH_FEEDBACK | LATCH_FEEDBACK → LATCH_FEEDBACK_CHANGED | Microswitch thật, không suy từ servo; epoch/boot/sequence xác định độ mới |
| Kiosk DEPOSIT_CONFIRM | DEPOSIT_CONFIRMED_BY_SHIPPER | Confirmation user, không parcel measurement |
| API confirm-pickup | PICKUP_CONFIRMED_BY_RECIPIENT | Tên chuẩn duy nhất cho xác nhận lấy; không dùng PICKUP_CONFIRMED_BY_USER ở contract hiện hành |
| Correlated ACK + STATUS / timeout | DEVICE_COMMAND_RESULT | Outcome CONTROL_APPLIED, SENSOR_CONDITION_MET, FAILED hoặc UNKNOWN; Backend service suy từ evidence đúng kiểu, không Gateway tự tạo sensor result |

Backend phát LOCK khi user confirmation + door OPEN→CLOSED đúng epoch + cửa CLOSED còn mới; lưu LOCK intent với request ID riêng trước send. Node kiểm tra door CLOSED tại thực thi, OPEN/UNKNOWN thì ERROR DOOR_NOT_CLOSED, không servo. LOCK terminal SENSOR_CONDITION_MET cần STATUS mới sau áp dụng, last_command_request_id đúng LOCK, servo LOCK_APPLIED, door CLOSED và latch ENGAGED. ACK APPLIED hoặc event latch đơn lẻ không đủ completion. UNLOCK CONTROL_APPLIED chỉ nói điều khiển đã chạy, không nói mở hoàn toàn; door OPEN mới ghi fact cửa mở. Timeout/mâu thuẫn → UNKNOWN/FAILED theo evidence, không báo thành công.

## 6. Timeout, dedup, freshness và command hết hiệu lực

| Tham số | Giá trị thử đề xuất, chưa đo/duyệt |
|---|---|
| Node RECEIVED ACK | 500 ms, tối đa 2 lần gửi lại cùng ID/payload nếu dedup/session còn hợp lệ |
| APPLIED/STATUS result | 2 s; quá hạn query STATUS/reconcile, không tự mở lại |
| Heartbeat / offline | 5 s / 15 s; không thay freshness cảm biến từng ngăn |
| Cửa/xác nhận | 30 s để thử cảnh báo, không trả AVAILABLE khi hết hạn |
| Serial/API chờ | 3 s rồi pending/timeout có request ID; không hàm ý rollback actuator |
| Dedup/lease/queue/STATUS sampling | Capacity/TTL/persistence/ngưỡng freshness còn D-06/P-01/P-05 |
| Kiosk code | TTL, length/alphabet, max attempts/rate limit còn P-03/D-06, chưa chọn số chính thức |

Mỗi hop chịu timeout cục bộ và báo loại/stage; Backend sở hữu deadline nghiệp vụ. Retry không tạo request ID mới. Same ID/payload trả kết quả cache, payload khác REQUEST_CONFLICT; hai ID khác nhau còn cần unique active operation/transaction ở Backend. Không hứa exactly-once sau reboot/cache eviction.

**Cơ chế invalidation M2 đề xuất để review:** Backend giữ command intent/deadline trong DB; adapter/Central kiểm còn hiệu lực trước dequeue/send. Một control epoch riêng cho locker/transaction được install ở node bằng CONTROL_SESSION, bind expected node boot và generation tăng trong boot; node chỉ nhận actuator command đúng active epoch, đúng boot, lease chưa hết. Lease đếm bằng monotonic clock tại node; retry INSTALL không gia hạn lease cũ. Grant generation cũ, epoch bị revoke/expire hoặc boot không khớp bị từ chối. GET_STATUS có thể chạy không grant để quan sát, không mở khóa.

REVOKE đánh dấu epoch terminal; không được INSTALL lại cùng generation/epoch để vô tình mở lại. Mỗi action hợp lệ cập nhật generation cao nhất, duplicate không reset lease; Backend đọc STATUS/control_generation trước grant mới sau restart. Sau boot node không giữ grant còn hiệu lực cho tới handshake/reconcile mới. Không cấp/giải phóng ngăn sang phiên mới chỉ vì deadline PC hết: cần ACK REVOKE và STATUS mới cùng boot, generation phù hợp, observed_epoch=0/lease_remaining_ms=0, door CLOSED/latch ENGAGED, hoặc quy trình recovery được duyệt; thiếu bằng chứng giữ UNKNOWN. Các fact confirmation/door cycle và LOCK trước revoke vẫn phải lưu/đối chiếu, epoch 0 không tự tạo completion. Nhờ đó command cũ không được dùng để mở phiên/người nhận khác. Lease node/PC không được giả là đồng hồ đồng bộ; thời điểm expire local, race grant/revoke, cache/persistence/generation/boot uniqueness và security phải được DEC-01 review/test trước integration. Đây chưa phải cơ chế đã được cài đặt hoặc xác nhận hoàn chỉnh.

Reconnect: hủy quyền gửi queue cũ → HELLO session mới → GET_STATUS từng locker/boot → Backend so DB intent/result/epoch/freshness → revoke/đối chiếu trước cấp epoch mới. Snapshot không đủ dựng lại door cycle đã mất thì giữ ngoại lệ. M2 phải xử lý tối thiểu lost ACK/disconnect/boot và không auto AVAILABLE; BE-03 bổ sung recovery/admin toàn diện. Policy Backend mất khi cửa mở còn D-08; không tự thêm lock/offline-open.

## 7. Contract nội bộ Gateway–Backend trong cùng ứng dụng

Đây là contract logic, không network API/server riêng và chưa cần sinh Python class/file:

| Entry point / event | Dữ liệu và trách nhiệm |
|---|---|
| submit_device_command(intent) | Backend service gọi sau commit intent: request_id, transaction_id, src=3, target, locker, operation, expected boot, epoch, deadline. Adapter trả QUEUED/REJECTED và reason; QUEUED không phải node ACK |
| on_device_event(envelope) | Worker đẩy parsed ACK/STATUS/DOOR_EVENT/LATCH_FEEDBACK/ERROR/HEARTBEAT qua ingress có giới hạn; service kiểm peer/session/schema/correlation/boot/sequence/freshness trước ghi domain |
| on_connection_status(change) | Link Serial/MQTT/node, CONNECTED/DISCONNECTED/UNKNOWN, session/boot, reason và receive time; service quyết định ngăn bị chặn, không worker tự AVAILABLE |
| on_transport_result(result) | request ID, hop/stage, DELIVERED/REJECTED/TIMEOUT/FAILED; không giả lập node APPLIED hoặc latch state |
| invalidate_pending(scope) | Service đóng/cancel/deadline/session thay đổi: loại pending command trong adapter/relay và khởi động revoke/reconcile node; xóa queue không chứng minh command trên radio đã bị thu hồi |

FastAPI lifecycle sở hữu khởi động/dừng worker. I/O blocking chạy ngoài event loop; thread/task giao tiếp bằng queue/callback async phù hợp được review, có giới hạn/backpressure không drop im lặng event quan trọng. Worker không mutate order/locker/SQLite; service và persistence sở hữu transaction. Shutdown/disconnect đánh dấu pending unknown, không replay mọi command khi restart. M2 fixture cần chứng minh event→service ordering, queue full/timeout/cancel/reconnect và HTTP vẫn đáp ứng (TC-35); chưa có queue capacity hoặc SLA được duyệt.

## 8. Backend API dự kiến

FastAPI là server duy nhất, auth/ownership do domain service kiểm tra. Mọi POST thay đổi có request_id UUID; idempotency scope actor+operation+payload và durable result. Username/password hashing/session/reset/CSRF/TLS và kiosk provisioning còn P-03; không chọn credential thật hoặc mật khẩu phòng/SĐT. Mã phòng chuỗi chữ số, SĐT chuỗi; chuẩn hóa/độ dài/uniqueness cần BE-01/02 thiết kế trước hiện thực.

| API | Actor / request chính | Hành vi |
|---|---|---|
| POST /deposits | Kiosk auth: room_code, recipient_phone, parcel_size, request_id | Chỉ đúng cư dân admin tạo trước; 202 có parcel/transaction/locker/requested_size/allocated_locker_size/size_upgraded/state; không tự tạo tài khoản |
| POST /deposits/{id}/confirm | Kiosk đúng transaction, request_id | Ghi user confirmation; accept trước/sau đóng cửa, chưa đủ evidence thì pending |
| GET /me/parcels | Resident auth | Chỉ đơn thuộc session actor |
| GET /me/notifications | Resident auth | Chỉ thông báo actor; schema/pagination cần review |
| POST /kiosk/pickup-sessions | Kiosk auth, kiosk_id, request_id | Tạo pickup_session_id/code/expiry/attempt policy cho display; không tạo quyền mở trước ownership |
| POST /parcels/{id}/pickup | Owner auth: kiosk_id, pickup_code, request_id | Kiểm mã/phiên/ownership/state; atomic consume/bind với owner+parcel+pickup transaction, lưu UNLOCK intent rồi 202 pending |
| POST /parcels/{id}/confirm-pickup | Owner và active pickup transaction, request_id | Ghi PICKUP_CONFIRMED_BY_RECIPIENT, chỉ complete sau door cycle và LOCK/latch đúng phiên |
| POST /admin/lockers/{id}/maintenance | Admin: enabled, reason, request_id | Audit, không xóa active transaction; ra bảo trì cần reconcile |

Login/logout, admin tạo/sửa/reset cư dân và polling `GET /transactions/{id}` là API hỗ trợ cần chốt schema/auth ở BE-02; polling chỉ actor/kiosk đúng scope. Không dùng client user_id/room_code làm quyền. Thông tin mã phiên không đưa lên GET /me/parcels, CoreIOT hoặc public log.

Mã phiên gắn kiosk và pickup_session khi phát; lúc redeem atomic bind vào owner/parcel/transaction, kiểm expiry/attempts trước intent. Không có SMS OTP. Retry đúng request sau consume trả kết quả cũ qua idempotency trước kiểm mã đã dùng; một request/parcel/owner khác dùng lại mã phải bị từ chối. Không log mã raw, không giữ plaintext bí mật dài hạn; cách digest/protect và thông số cần review P-03. Mã có thể chia sẻ từ xa, chỉ xác nhận thao tác dùng phiên kiosk, không chứng minh vị trí tuyệt đối.

Error envelope: request_id, error.code, message công khai an toàn, retryable. Giữ INVALID_ROOM_PHONE/INVALID_SIZE/RECIPIENT_NOT_FOUND/NO_SUITABLE_LOCKER/DEVICE_OFFLINE/REQUEST_CONFLICT/INVALID_STATE/BUSY/STATE_UNKNOWN. Bổ sung dự kiến PICKUP_CODE_INVALID/EXPIRED/USED/SESSION_MISMATCH/ATTEMPTS_EXCEEDED; API có thể che chi tiết để tránh dò mã, audit không chứa code. HTTP status draft: 400 validation, 401 auth, 403/404 scope theo policy, 409 conflict/state/no locker, 429 rate limit, 503 offline/unknown, 500 safe error. HTTP response không chứng minh thiết bị mở; timeout sau send phải lưu unknown/pending.

## 9. CoreIOT và gate nghiệm thu

Telemetry: door_state, latch_feedback, servo_command_state, availability, node_online, errors, transaction_count, firmware_version; không SĐT/phòng/mã phiên/token. Topic, RPC schema, authenticated actor/service role, device provisioning và tenant config còn P-03/IOT-01. RPC từ MQTT worker đi qua Backend service kiểm quyền/state trước submit_device_command. Webserver local ESP32 tương tự, không actuator bypass Backend. Notification sự cố CoreIOT khác thông báo đơn trong Web App.

DEC-01 đóng từng phần: M1 serializer/fixture/guard LOCK/STATUS có latch, M2 identity/wire/mapping/epoch/recovery tối thiểu, cloud/OTA review sau theo gate. Byte/enum/timeout/grant/security chưa được phê duyệt từ việc ghi tài liệu; chưa có test HIL, parser, code, exactly-once hay khả năng đạt điểm T14 được xác minh. Xem TC-24…35 trong [TEST_PLAN](TEST_PLAN.md).

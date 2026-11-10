# Kế hoạch kiểm thử — baseline revision 1.3

Ngày 10/11/2026. **Chưa có code/test executable hoặc kết quả chức năng/HIL trong repository.** Giữ TC-01…29 và TC-16/17 tiểu mục, thêm TC-30…35 cho quyết định mới. Mọi số lần/ngưỡng đề xuất phải review; không ghi PASS thay cho BLOCKED/NOT RUN.

## 1. Mức thử và fixture

- M1 bench: 1 servo/chốt + 1 door sensor + 1 latch microswitch, sketch/test jig thuộc HW-01; contract v1 subset, epoch=0 chỉ bench. Thử riêng display/radio/OTA nếu board/toolchain đúng, chưa cần E2E.
- M2: fake Serial/device transport, fake clock, SQLite tạm/dữ liệu giả; integration contract/expired command/auth/recovery tối thiểu. Test worker với HTTP và service ingress.
- M3: một ngăn E2E có cư dân admin tạo trước, mã phiên kiosk và door/latch thật. M4: đủ L01=S/L02=S/L03=M/L04=L, hai node, full Web App/admin/recovery.
- Fixture identity: ít nhất hai cư dân giả, mã phòng chuỗi chỉ có số, SĐT giả; credentials riêng không bằng phòng/SĐT, một admin/kiosk đã xác thực. Phòng/SĐT normalization/uniqueness, session/hash/code params phải được thiết kế/duyệt P-03 trước nghiệm thu thực.
- Door OPEN/CLOSED/UNKNOWN, servo command và latch ENGAGED/NOT_ENGAGED/UNKNOWN độc lập. NOT_ENGAGED không chứng minh chốt mở hoàn toàn. Không fixture cảm biến hàng.
- Mỗi evidence ghi TC/FR/Issue, ngày, commit/build, contract/decision revision, setup/initial state, steps/expected/actual, request/transaction/boot/sequence/epoch, kết quả và reviewer; khử SĐT, code, password/token. Simulation không thay HIL.

## 2. Luồng chính và allocation

| Test / yêu cầu | Setup / bước | Acceptance Criteria | Mức / owner |
|---|---|---|---|
| TC-01 / FR-01/03/05 | Nhập/sửa/xem lại phòng số, SĐT giả, S/M/L rồi gửi | Đúng cư dân đã tạo mới reserve; đúng ngăn nhận UNLOCK, UI báo allocated size, audit intent trước send | M3 / Both |
| TC-02 / FR-03/11 | Chỉ còn S/M, yêu cầu L | NO_SUITABLE_LOCKER; không reservation/command mở | M2 / B |
| TC-03 / FR-04/12 | Barrier 2 request khác ID tranh một ngăn, đề xuất 20 lượt reset DB | Mỗi lượt chỉ một active reservation; không cùng ngăn cho hai đơn; DB/audit nhất quán | M2 / B |
| TC-19 / FR-03 | 2S bận, M/L trống; gửi S | Cấp M, requested=S/allocated=M, size_upgraded=true, UI báo nâng size | M2 + UI / B,A |
| TC-20 / FR-03 | S/M bận, L trống; thử S rồi reset thử M | Cả hai cấp L, lưu đúng size | M2 / B |
| TC-21 / FR-03 | Chỉ S trống, gửi M | Từ chối, không cấp nhỏ hơn/không command | M2 / B |
| TC-22 / FR-03 | S/M trống gửi S, thêm hai S hợp lệ | Chọn S; tie-break nhỏ nhất chỉ bắt buộc nếu P-04 duyệt, không chiếm M | M2 / B |
| TC-04 / FR-06 | Cửa đã mở/đóng nhưng shipper chưa confirm | Không STORED/OCCUPIED; timeout giữ không khả dụng, không tự LOCK ngoài trigger đã duyệt | M2/M3 / Both |
| TC-05 / FR-07 | Confirm nhưng cửa còn OPEN hoặc UNKNOWN | Không LOCK/không complete; UI nhắc, cảnh báo theo ngưỡng duyệt; node tự kiểm cửa khi nhận LOCK | M1/M3 / Both |
| TC-06 / FR-07/08 | Có door cycle cùng phiên, shipper confirm, cửa CLOSED; LOCK và latch ENGAGED | Một STORED/OCCUPIED và một notification đúng người; chỉ ACK APPLIED hoặc CLOSED/ENGAGED từ trước không đủ | M3 / Both |
| TC-07 / FR-02 | Phòng/SĐT không khớp hoặc dữ liệu admin không xác định duy nhất | Từ chối trước reserve/mở, không tự tạo cư dân/thông báo nhầm | M2 / B |
| TC-08 / FR-09 | Chủ đơn login, lấy mã từ kiosk và pickup | Đúng kiosk/phiên/mã còn hạn/ownership, atomic one-use, một pickup active; chỉ đúng ngăn mở | M3 / Both |
| TC-09 / FR-08/09/NFR-04 | Cư dân B đọc/mở đơn A; sửa user_id/phòng/parcel; dùng mã hợp lệ nhưng sai owner | Không lộ đơn/thông báo, không command mở; code không thay quyền sở hữu | M2/M3 / B |
| TC-10 / FR-10 | Đã mở/đóng cửa nhưng người nhận chưa confirm lấy | Không COMPLETED/AVAILABLE; giữ không khả dụng và xử lý timeout/exception theo policy | M3 / Both |
| TC-11 / FR-10 | Confirm lấy + door cycle đúng phiên + LOCK/CLOSED/ENGAGED mới, epoch cũ vô hiệu | Atomic COMPLETED/AVAILABLE, không còn command cũ có thể mở phiên khác; audit là user confirmation, không sensor hàng | M3 / Both |

## 3. Lỗi, ngoại lệ và bảo vệ dữ liệu

| Test / yêu cầu | Setup / bước | Acceptance Criteria | Mức / owner |
|---|---|---|---|
| TC-12 / FR-11/16 | Giữ cửa mở quá ngưỡng đã duyệt | Đúng ngăn có log/RuleChain/notification, không LOCK khi OPEN và không auto AVAILABLE | M5 / Both |
| TC-13 / FR-05/11 | Tắt Node A, đợi offline; gửi nhiều size | Loại L01/L02, không mở node offline; không đánh nhầm B offline; phân biệt heartbeat với freshness cửa/chốt | M2/HIL / Both |
| TC-14 / FR-12/NFR-03 | Cắt serial/reboot node/Central/PC tại reserve, sau UNLOCK, sau confirm, trước/sau LOCK và trước commit cuối | Intent/DB còn, không AVAILABLE; handshake/status/epoch đối chiếu, stale event không hoàn tất mới. Tối thiểu lost ACK/disconnect M2, full crash matrix BE-03 M4; policy mất Backend khi cửa OPEN chưa duyệt thì BLOCKED | M2/M4 / Both |
| TC-15 / FR-13 | Admin vào/ra MAINTENANCE, non-admin thử, active transaction còn | Không phân bổ bảo trì, không xóa active transaction; ra bảo trì cần reconcile/epoch invalidation/audit | M4 / B |
| TC-18 / NFR-08 | Nhấn đặt khi rỗng, nhấn lấy khi còn hàng | Demo/report thừa nhận hệ thống không phát hiện được; không log PARCEL_PRESENT/ABSENT_SENSOR_VERIFIED | Review/HIL / Both |
| TC-23 / FR-01/02 | Thiếu trường, room_code có chữ/dấu, size lạ, payload quá dài; credentials giống phòng/SĐT | Từ chối đúng policy trước reserve/send; admin setup không mặc định password từ phòng/SĐT; chưa chọn policy chi tiết thì BLOCKED nhánh đó | M2 / B |
| TC-24 / NFR-02/FR-09 | Cùng ID/payload 3 lần, cùng ID khác payload, double-click khác ID | Một side effect/active operation; cached result; REQUEST_CONFLICT khi payload khác; code đã consume không mở lần nữa | M2/M3 / Both |
| TC-25 / NFR-02 | Mất ACK sau servo áp dụng, retry cùng ID trong boot/epoch còn hợp lệ | Không servo lần hai, không đơn thứ hai; query STATUS tách sensor, không gắn sensor giả vào ACK; kết quả chưa rõ giữ UNKNOWN | M2/HIL / Both |
| TC-26 / NFR-03 | Đổi boot, sequence cũ/sai thứ tự, event epoch cũ, replay ACK | Không hoàn tất phiên mới từ stale evidence, dừng actuator retry, GET_STATUS/reconcile; không dựng door cycle từ snapshot cũ | M2/HIL / Both |
| TC-27 / FR-05/14/15/NFR-04 | Sai peer/src/dst/locker, flags/version/length/enum, line dở/sai JSON, RPC/local trái quyền | Không mở, parser bounded, source-target 3→1/2 hoặc 1/2→3 đúng; local/RPC qua Backend service | M2/M5 / Both |
| TC-28 / FR-07/11/NFR-08 | Door CLOSED nhưng chốt kẹt/không gài, latch UNKNOWN, chỉ ACK servo, switch nhả | Không completion nếu chưa ENGAGED mới; NOT_ENGAGED không được báo vị trí mở hoàn toàn, ERROR/UNKNOWN quan sát đúng | M1/M3 / A |
| TC-29 / FR-12/NFR-05/06 | Dùng dữ liệu giả có dấu nhận biết, restart DB, xem log/telemetry/export/Git | DB/intent bền vững; không SĐT/phòng/pickup_code/password/token công khai; audit vẫn trace được request/transaction/sensor state | M2/M6 / B |

## 4. Test bổ sung cho baseline mới

| Test / yêu cầu | Bước quan trọng | Acceptance Criteria / gate | Mức / owner |
|---|---|---|---|
| TC-30 / FR-07/NFR-08 | Test door và latch độc lập; gửi LOCK khi OPEN/UNKNOWN; switch latch nhả khi cửa vẫn CLOSED | Không actuator LOCK nếu door chưa CLOSED; latch phản ánh microswitch, không suy từ servo/door; NOT_ENGAGED không chứng minh unlock hoàn toàn | M1 rồi M3 / A |
| TC-31 / FR-09/NFR-04/05 | Mã đúng, sai, hết hạn, đã dùng, khác kiosk/pickup_session/owner/parcel, quá attempts; retry request gốc sau consume | Không mở ở nhánh sai, không consume nhầm; bind/consume atomic một lần; retry cùng request trả kết quả cũ; TTL/attempt/format/digest/session policy phải duyệt P-03/D-06; không log mã, nêu hạn chế chia sẻ từ xa | M2/M3 / B,A |
| TC-32 / FR-06/07/10 | Cả gửi và nhận: confirm trước CLOSED, CLOSED trước confirm; thiếu OPEN, door cycle cũ hoặc boot đổi | Hai thứ tự hợp lệ cùng complete khi LOCK+ENGAGED đủ mới; thiếu door cycle đúng transaction không complete; LOCK intent luôn commit trước send; không UI deadlock do thứ tự thao tác | M2/M3 / Both |
| TC-33 / FR-14/17/18/NFR-07 | Cùng build Central chạy kiosk/keypad + ESP-NOW + Serial + webserver và OTA; có request/pending transaction | Đo RAM/flash/partition/coexistence, không mất evidence/mở nhầm, sau reboot reconcile không auto AVAILABLE; update khi transaction active và fail recovery phải có policy D-10/P-03 trước nghiệm thu | Spike M1 nếu sẵn, full M5/M6 / Both |
| TC-34 / FR-05/12/NFR-02/03 | Expire/dequeue command, revoke epoch, delay/replay grant/command, generation cũ, node boot mới, DB restart | Command hết hiệu lực không mở phiên mới; queue invalidation không coi là thu hồi radio; revoke/lease/boot và status đối chiếu trước tái cấp; thiếu bằng chứng giữ UNKNOWN; cơ chế draft phải review trước test | M2/M3, mở rộng M4 / Both |
| TC-35 / FR-15/NFR-01/04 | Fake Serial/MQTT blocking, queue đầy, event out-of-order, cancel/disconnect/shutdown; gọi HTTP đồng thời | Worker không chặn event loop hoặc ghi domain trực tiếp; service validation/persistence nhận event, backpressure báo lỗi, không drop im lặng evidence, submit QUEUED không thành node ACK; ngưỡng đáp ứng đo/duyệt, chưa có SLA số | M2 / B |

## 5. Minh chứng công nghệ và nộp bài

| Test / công nghệ | Acceptance / evidence thật |
|---|---|
| TC-16A / FR-14 T07 | Webserver tự viết chạy trên ESP32; thao tác có quyền và từ chối trái quyền qua Backend, video/log + TC-33 |
| TC-16B / FR-17 T14 | Ưu tiên Central: firmware v1.0→v1.1, update/reboot, version và servo/cửa/latch/radio/Serial còn đúng; artifact/checksum/video; D-10 scope/partition/recovery và T14 đối chiếu giảng viên còn gate, không hứa đủ 2 điểm chỉ Central |
| TC-16C / FR-18 N03 | ST7789 thật chạy LVGL/keypad form phòng số/SĐT/size, nâng size, confirm và hiển thị mã phiên; không dùng ảnh mockup thay evidence |
| TC-17A / FR-15 T08 | Telemetry node→PC app→CoreIOT và RPC hợp lệ đi ngược/ACK thật; trái quyền không tới servo; worker/service trace đầy đủ, không PII/secret |
| TC-17B / FR-16 T11/T12/T13 | Template/dashboard giám sát/điều khiển có kiểm quyền; RuleChain tạo notification từ ngưỡng cửa/offline; export sạch + video/ảnh/timestamp |
| T06 / FR-05 | FW-02 có log radio thật hai node, ACK/STATUS và loss/retry, TC-13/24…27; không tính từ schema tài liệu |

DOC-01 phải kiểm PDF theo mẫu và tên `[Mã lớp]_[Mã nhóm]_BaoCaoIoT.pdf`, bảng tự đánh giá công nghệ, bảng phân công, ≥5 tham khảo/trích phần kế thừa, GitHub cho giảng viên truy cập và lịch sử commit cả A/B, khai báo phạm vi dùng AI, video demo khuyến nghị 5–10 phút. Kiểm tái lập bằng hướng dẫn setup/build/run đã thực hiện. Mã công nghệ chỉ tính từ mức hoàn thành/evidence được giảng viên đánh giá, tổng theo thông báo tối đa 10; không thêm TinyML/T10/T15.

## 6. Exit criteria theo mốc

M0: consistency tài liệu/IDs/link/dependency và giữ snapshot lịch sử; không PASS chức năng. M1: bench một ngăn/sketch/fixture và thiết kế giả, không cần API/E2E. M2: foundations/integration contract, atomic allocation/auth/parser, dedup/freshness/recovery tối thiểu có test; chưa chứng nhận full workflow. M3: một ngăn E2E confirmation+door cycle+LOCK+latch và mã kiosk, lỗi tối thiểu có evidence. M4: bốn ngăn/Web App/full recovery; M5: công nghệ/combined Central; M6: acceptance/report/demo.

Chưa có code/board/tenant/ngưỡng duyệt thì NOT RUN/BLOCKED. Mỗi feature DONE cần code trên môi trường đích, test PASS, evidence/tài liệu cập nhật và thành viên còn lại review; không coi consistency check M0 là test chức năng PASS.

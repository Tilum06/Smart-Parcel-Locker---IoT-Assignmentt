# Lộ trình M0–M6 — revision 1.3

Ngày 10/11/2026. Giữ các mốc cũ; cập nhật theo phê duyệt Finalize M0 Baseline. Lịch nội bộ chưa phải ngày nộp chính thức; đối chiếu tuần 16/thông báo môn khi lập lịch. A=Embedded, B=Backend/IoT, Both=cùng thực hiện/review. [DECISIONS](DECISIONS.md) là chuẩn gate, không dùng report cũ để mở lại D-03/04/05/07.

| Mốc | Member A | Member B | Dependency / gate theo việc | Deliverable và exit criteria khác nhau |
|---|---|---|---|---|
| M0 — Project Setup / baseline revision | Đồng bộ node/kiosk/lock/firmware contract | Đồng bộ một app FastAPI, identity/session, serial và dữ liệu | Quyết định approved mới, kiểm consistency | Revision 1.3, đặc tả/kiến trúc/interfaces/backlog/test plan nhất quán; QA tài liệu, chưa cần firmware/API chạy |
| M1 — Một ngăn prototype và thiết kế | HW-01 có servo/door/microswitch và sketch/test jig tối thiểu; chuẩn bị board/nguồn/pin; thử riêng ESP-NOW, LVGL/ST7789, OTA Central nếu sẵn | BE-01 phần schema/Best Fit bằng dữ liệu giả, mock transport và fixtures; review password/session/phone design | DEC-01 duyệt từng phần; D-09 cho điện/board, D-01 chỉ chặn số đo/chế tạo cuối; không đợi cloud/OTA hoàn tất | Prototype bench quan sát được door/latch và guard không LOCK khi cửa mở, contract M1 fixtures được review; bản thiết kế DB/test matrix, chưa yêu cầu API/E2E hoàn chỉnh |
| M2 — Foundations và integration contract | FW-01 node, FW-02 radio, FW-03 kiosk và bridge Serial; M2 contract giữ chung v1 | BE-01 schema/allocator atomic, BE-02 API FastAPI, GW-01 Serial trong cùng app; code session/ownership | Board/toolchain P-02/D-09, wire P-01, auth P-03, freshness P-05, timeout/recovery D-06/D-08 phần tối thiểu | ACK/STATUS riêng, source/target/correlation, intent trước send, dedup, expired command và reconnect tối thiểu; parser/allocator/auth fixtures và HIL nền có evidence; chưa gọi là chu trình E2E hoàn tất |
| M3 — Một ngăn end-to-end | Ghép FW-03 + node door/latch thật, kiểm UNLOCK/door cycle/LOCK | Ghép Backend/Gateway/SQLite, client nhận có auth + mã kiosk; full Web App chưa bắt buộc | INT-01 sau HW-01/FW-01/02/03/BE-01/02/GW-01; policy và contract M2 liên quan phải được duyệt | Một lần gửi–nhận đúng chủ, mã one-use, confirmation cả hai thứ tự, door cycle + latch; lost ACK/disconnect không mở lặp/auto AVAILABLE; log/video đúng mức bằng chứng |
| M4 — Bốn ngăn, Web App và full recovery | Nhân 4 cơ cấu, 2 node đúng L01…L04 và kiểm nguồn/mapping | WEB-01, BE-03 maintenance/reconciliation đầy đủ, INT-02 | M3, D-01 số đo thật/P-04 tie-break, D-08 recovery/admin đầy đủ | 2S/1M/1L Best Fit+nâng size+concurrency, đúng quyền; offline/lỗi/bảo trì bị loại; full crash/admin matrix và Web App |
| M5 — CoreIOT, ESP32 webserver và OTA | FW-04 T07, FW-05 T14; cùng firmware Central kiosk/radio/Serial/web/OTA | IOT-01 T08/T11, IOT-02 T12/T13; RPC qua service cùng app | Tenant/auth/topic/RPC P-03, D-10 phạm vi/partition/coexistence, dependencies từng Issue | Minh chứng T07/T08/T11/T12/T13/T14/N03 và TC-33 combined-load; không bảo đảm OTA Central đủ điểm nếu chưa đối chiếu giảng viên |
| M6 — Acceptance và nộp bài | Số đo, sơ đồ/evidence phần cứng, test lỗi và contribution | QA-01/DOC-01, report/data/demo, hướng dẫn chạy tái lập | INT-02/BE-03/FW-04/05/IOT-02, các blocker Must Have đóng | Tests/evidence thực, PDF đúng mẫu/tên, self-assessment/phân công, ≥5 tham khảo, khai báo AI, lịch sử Git của cả A/B, GitHub access và video |

## M1 bắt đầu song song

Both làm DEC-01 theo từng phần, không cần chốt mọi cloud/OTA parameter mới cho A/B thiết kế. A có thể khảo sát board/BOM/cơ khí và làm test jig HW-01 sau duyệt điện/nguồn; không phải đợi firmware FW-01 hoàn chỉnh M2. B bắt đầu BE-01 thiết kế category size, tài khoản giả, command intent/result, reservation/state schema và mock transport mà không cần tủ bốn ngăn hoặc cm cuối.

PlatformIO/C++/Arduino và Python/FastAPI/SQLite đã chọn; board profile/version/partition và frontend framework chưa khóa. Những thử nghiệm riêng M1 về ESP-NOW/ST7789/LVGL/OTA chỉ làm nếu có target/toolchain đúng; không biến optional early spike thành gate cho mọi nhánh. OTA trên Central là ưu tiên thử, D-10 phạm vi cuối vẫn mở và có thể mở rộng node.

## Recovery tối thiểu trước INT-01

FW-02/GW-01/BE-01/BE-02 cùng chịu M2: request ID/dedup, intent bền vững, lost ACK query/reconcile, dừng queue khi disconnect/boot đổi, handshake/GET_STATUS, giữ UNKNOWN, command epoch/expiry/invalidation đã review và test. BE-03 M4 mở rộng mọi điểm crash, admin maintenance, xác nhận sai và policy ngoại tuyến đầy đủ; không trì hoãn toàn bộ NFR-03 đến M4.

Nếu policy Backend mất khi cửa đang mở (D-08) chưa duyệt, chỉ được bench quan sát có kiểm soát, không nghiệm thu tình huống vận hành đó. Không tự khóa khi cửa mở hoặc tự AVAILABLE để cho demo đi tiếp.

## Gate còn mở và cách review

- D-01: số đo/clearance thật; không chặn thuật toán S/M/L bằng fixture giả.
- D-06/P-01/P-05: timeout/buffer/baud, wire/lease, dedup/freshness; giá trị trong INTERFACES chỉ thử nghiệm.
- D-08: recovery/admin/policy khi cửa mở mất Backend; tối thiểu M2 và full M4 phải được tách rõ.
- D-09/P-02: target/revision/nguồn/GPIO/model/lib/flash, không đoán board profile.
- D-10: OTA scope/partition/memory/Wi-Fi/radio và T14 cần đối chiếu, không đóng theo ưu tiên Central.
- P-03: auth/session/provisioning, chuẩn hóa dữ liệu/hash password, TTL/format/attempt limit mã kiosk và RPC/local control.
- P-04: mapping đã chốt, tie-break ID nhỏ nhất còn review.

Mỗi buổi tích hợp dùng một baseline/build và contract revision, log request/transaction/boot/epoch đã khử secret. Thay đổi hợp đồng cập nhật cả hai đầu và test; không thêm server/broker nội bộ. Xem [ISSUES](ISSUES.md) cho Dependencies đầy đủ và [TEST_PLAN](TEST_PLAN.md) cho acceptance/evidence; kế hoạch không phải kết quả chạy.

# Đặc tả đang áp dụng — IOT-SPL

**Revision 1.3 — M0 baseline revision, 10/11/2026.** Nguồn hiện hành: các quyết định nhóm phê duyệt và tài liệu này. [v1.2 gốc](../PROJECT_SPEC_Smart_Parcel_Locker_v1.2.md) là tài liệu lịch sử, giữ nguyên; các quyết định mới ở đây thay thế nội dung cũ tương ứng. Giữ FR-01…18, NFR-01…08, Issue ID hiện có.

Thay đổi so với M0 ban đầu: FastAPI + Gateway cùng một ứng dụng Python; USB Serial; 4 microswitch chốt bắt buộc; tài khoản cư dân tạo trước; mã phòng số; mã phiên nhận tại kiosk; mapping ngăn cố định; PlatformIO/Arduino; ưu tiên thử OTA Central. Giao thức byte/enum, tham số và thiết kế triển khai trong INTERFACES vẫn cần review/đo theo [DECISIONS](DECISIONS.md); quyết định kiến trúc không phải minh chứng chạy thành công.

## 1. Cấu hình đã duyệt

| Thành phần | Baseline |
|---|---|
| ESP32 #1 Locker A | L01=S, L02=S |
| ESP32 #2 Locker B | L03=M, L04=L |
| ESP32 #3 Central | Một project chứa ESP-NOW, USB Serial, LVGL/ST7789 SPI 240×240, keypad 4×4, webserver và OTA |
| Mỗi ngăn | 1 servo/chốt + 1 cảm biến cửa + 1 microswitch xác nhận chốt gài |
| Tổng khóa/cảm biến | 4 servo, 4 cảm biến cửa, 4 microswitch chốt; không cảm biến kiện hàng |
| Firmware | PlatformIO, C/C++, Arduino framework; node dùng chung project và khác cấu hình |
| PC | Python + FastAPI + SQLite, Backend và Gateway là module trong cùng một ứng dụng; một HTTP server |
| CoreIOT | Giám sát, điều khiển qua Backend, RuleChain và notification sự cố |
| Người nhận | Admin tạo trước tài khoản gắn mã phòng dạng chữ số, SĐT và thông tin đăng nhập |
| Nhận hàng | Đăng nhập + sở hữu đơn + mã phiên nhận hàng ngắn hạn từ kiosk |

Board YoloUNO/revision, flash/partition, phiên bản thư viện ST7789/LVGL, nguồn/GPIO/model servo/góc quay/debounce vẫn mở. Kích thước cm của S/M/L chưa chốt; số đo v1.2 chỉ minh họa. Shipper tự chọn size theo bảng kích thước được duyệt, hệ thống không đo hàng. Tie-break locker ID nhỏ nhất còn là đề xuất review, còn mapping L01…L04 đã duyệt.

## 2. Must Have — chức năng

| ID | Yêu cầu đang áp dụng | Acceptance intent / test |
|---|---|---|
| FR-01 | Kiosk nhập/sửa/xem lại mã phòng số, SĐT và S/M/L | Ba trường bắt buộc, không nhập mã phòng chữ; TC-01/23/16C |
| FR-02 | Đối chiếu phòng + SĐT với tài khoản cư dân admin đã tạo | Chỉ reserve khi có đúng một người nhận hợp lệ; không tự tạo tài khoản; TC-07/23 |
| FR-03 | Best Fit S→S/M/L, M→M/L, L→L | Chọn ngăn nhỏ nhất đủ size, lưu requested_size/allocated_locker_size, báo nâng size; TC-02/19…22 |
| FR-04 | Reservation atomic SQLite | Một active transaction/ngăn, không cấp trùng; TC-03 |
| FR-05 | UNLOCK đúng node/ngăn qua ESP-NOW | Lưu intent/request ID trước gửi, đối chiếu ACK và STATUS, không mở khi offline/UNKNOWN; TC-01/13/24…27/34 |
| FR-06 | Shipper xác nhận đã đặt hàng | Ghi xác nhận người dùng, không gọi là phép đo hàng; TC-04/18/32 |
| FR-07 | Cửa và chốt được kiểm chứng độc lập | Node không LOCK khi cửa OPEN/UNKNOWN; chỉ đủ khóa khi door CLOSED + latch ENGAGED mới; TC-05/06/28/30 |
| FR-08 | Thông báo đơn trong Web App | Chỉ đúng tài khoản thấy đơn/thông báo, một thông báo khi gửi hoàn tất; TC-06/09 |
| FR-09 | Nhận hàng có auth, ownership và mã phiên kiosk | Mã đúng kiosk/phiên, còn hạn, một lần dùng, giới hạn thử; duplicate không mở thêm; TC-08/09/24/31 |
| FR-10 | Người nhận xác nhận đã lấy hàng | Chỉ COMPLETED/AVAILABLE khi đủ xác nhận + door cycle đúng phiên + LOCK + latch ENGAGED; TC-10/11/32 |
| FR-11 | Cảnh báo sự cố | Hết ngăn, cửa mở lâu, lỗi khóa quan sát được, offline, mất kết nối; TC-02/12…14/28/30 |
| FR-12 | SQLite, intent/result và audit bền vững | Lưu liên kết người nhận, size, trạng thái, confirmation, command intent/result, lỗi; không log SĐT/mã phiên/secret công khai; TC-03/14/29/34 |
| FR-13 | Admin bảo trì/xử lý ngoại lệ | Không cấp MAINTENANCE; không xóa active transaction; ra bảo trì phải đối chiếu; TC-15 |
| FR-14 | Webserver tự phát triển trên ESP32 — T07 | Local giám sát/điều khiển có quyền, route Backend; TC-16A/27/33 |
| FR-15 | PC Gateway hai chiều — T08 | Serial/MQTT worker không chặn HTTP, mọi thay đổi nghiệp vụ qua Backend service; TC-17A/35 |
| FR-16 | CoreIOT — T11/T12/T13 | Template/dashboard, RuleChain và notification thực, không thay database đơn; TC-12/17B |
| FR-17 | OTA — T14 | Ưu tiên thử Central sớm, hai version và kiểm sau reboot; phạm vi cuối/điểm cần đối chiếu giảng viên; TC-16B/33 |
| FR-18 | LVGL — N03 | Form, bảng size đã duyệt, hướng dẫn gửi/nhận và mã phiên trên ST7789 thật; TC-16C/31/33 |

T06 gắn FR-05. T07/T08/T11/T12/T13/T14/N03 đã có kế hoạch, chưa có code hoặc test thực tế. Mã/điểm đối chiếu thông báo môn học được cung cấp riêng cho nhóm, không phát hành tài liệu đó trong repository public; chỉ giảng viên đánh giá từ minh chứng. OTA chỉ trên Central không tự bảo đảm đủ 2 điểm T14.

## 3. Must Have — phi chức năng

| ID | Ràng buộc / tiêu chí |
|---|---|
| NFR-01 | Tách API, business services, persistence và transport trong một ứng dụng Python; Gateway không phân ngăn/hoàn tất; không microservices/broker nội bộ/server thứ hai |
| NFR-02 | Atomic reservation, request ID chống lặp xuyên transport; semantic guard chống hai request khác ID cho cùng phiên; ACK khác completion; TC-03/24/25/34 |
| NFR-03 | Timeout/reboot/mất kết nối không tự AVAILABLE; intent lưu trước send, reconcile boot/freshness/command còn hiệu lực; TC-14/26/34 |
| NFR-04 | Quyền từ session server, chủ đơn + mã phiên kiosk; local/RPC qua service kiểm quyền; request ID không cấp quyền; TC-09/27/31/35 |
| NFR-05 | Không log/công khai SĐT, mã phòng, pickup_code, mật khẩu/token; mã bí mật được bảo vệ, không mặc định mật khẩu bằng phòng/SĐT; TC-29/31 |
| NFR-06 | Audit request/transaction/node/ngăn/boot/sequence, thay đổi state, lỗi và mức bằng chứng; không ghi mã phiên vào log công khai |
| NFR-07 | Hai người review hợp đồng theo từng phần, dependency/version khóa sau xác minh; A/B làm song song bằng fixture, không đợi cloud/OTA cho mọi việc |
| NFR-08 | Door OPEN/CLOSED/UNKNOWN; servo command state độc lập; latch ENGAGED/NOT_ENGAGED/UNKNOWN. NOT_ENGAGED không chứng minh chốt mở hoàn toàn; không sensor hàng; TC-18/28/30 |

Tham số chưa đo/duyệt: timeout, lease, heartbeat/freshness, buffer, retry/dedup, độ dài/TTL/số lần thử mã phiên, định dạng chi tiết phòng/SĐT, password hashing/session, giới hạn nguồn/radio/latency. Không biến giá trị thử trong INTERFACES thành SLA.

## 4. Identity, phân bổ và mã phiên

`room_code` là chuỗi chỉ có chữ số để giữ được số 0 đầu; giới hạn độ dài/format cụ thể chưa duyệt. SĐT là chuỗi; quy tắc chuẩn hóa, tính duy nhất của cặp phòng–SĐT và xử lý dữ liệu admin trùng phải được thiết kế BE-01/02 trước hiện thực. Thiếu/không khớp/không xác định duy nhất thì từ chối, không tự tạo người nhận mới. Admin tạo thông tin đăng nhập riêng; không dùng phòng/SĐT làm mật khẩu mặc định. Password hashing, reset và session policy thuộc phần thiết kế còn mở P-03.

Chỉ cấp ngăn AVAILABLE, online, có snapshot đủ mới/tin cậy, không lỗi/bảo trì/active transaction. Reserve, active transaction và command intent phải nhất quán SQLite; không giữ transaction DB trong lúc chờ radio. Hết ngăn phù hợp thì NO_SUITABLE_LOCKER và không gửi mở.

Backend phát mã phiên ngắn hạn cho phiên nhận của kiosk đã xác thực, Central chỉ hiển thị qua ST7789. Khi yêu cầu nhận, người dùng nộp mã; Backend kiểm chủ đơn rồi atomic bind/consume mã với kiosk, tài khoản, kiện và pickup transaction. Mã không được tái dùng để mở lần khác; retry cùng request hợp lệ chỉ trả kết quả cũ. Sai/hết hạn/đã dùng/khác kiosk hoặc phiên/bị giới hạn thử đều không mở. TTL, độ dài, alphabet, attempt budget, lưu digest và session/auth cụ thể chờ P-03/D-06. Mã có thể bị chia sẻ từ xa, không chứng minh tuyệt đối vị trí vật lý và không phải SMS OTP.

## 5. Trạng thái, workflow và điều kiện hoàn tất

**Ngăn:** AVAILABLE → RESERVED → DEPOSITING → OCCUPIED → COLLECTING → AVAILABLE; FAULT/MAINTENANCE/UNKNOWN. **Đơn:** CREATED → DEPOSITING → STORED → PICKUP_PENDING → COMPLETED; CANCELLED/EXCEPTION. Không đổi các ID/trạng thái cũ thành hệ khác.

Gửi: nhận thông tin → đối chiếu cư dân → reserve + lưu UNLOCK intent trước send → ACK điều khiển/STATUS → quan sát cửa mở và đóng lại đúng phiên → shipper confirmation → Backend lưu/phát LOCK khi cửa đóng hợp lệ → node kiểm tra cửa lần nữa trước servo → ACK và STATUS/LATCH_FEEDBACK mới → STORED/OCCUPIED và thông báo. Confirmation có thể trước hoặc sau đóng cửa; giữ độc lập hai bằng chứng và chỉ phát LOCK khi guard phù hợp. Không buộc UI phải theo một thứ tự confirmation/đóng cửa cứng.

Nhận: đăng nhập/chủ đơn + mã phiên kiosk → tạo pickup transaction duy nhất và lưu UNLOCK intent → điều khiển/door cycle → recipient confirmation trước hoặc sau đóng cửa → LOCK an toàn → COMPLETED/AVAILABLE khi cùng phiên có confirmation, door cycle và door CLOSED + latch ENGAGED sau LOCK. NOT_ENGAGED chỉ nói microswitch không báo gài, không phải UNLOCKED đã xác minh.

Không có door cycle đúng phiên thì không hoàn tất dù cảm biến đang CLOSED/ENGAGED từ trước. ACK transport/servo không đủ. Thiếu bằng chứng, timeout/reboot/mất kết nối không giải phóng; ngăn UNKNOWN/FAULT và transaction EXCEPTION hoặc pending đối chiếu theo D-08. Không LOCK khi cửa OPEN/UNKNOWN, không UNLOCK mới khi trạng thái chưa biết. Policy riêng khi Backend mất kết nối trong lúc cửa mở vẫn chưa chốt, không tự thêm hành vi actuator ngoại tuyến.

## 6. Optional và ngoài phạm vi

| ID | Hạng mục | Trạng thái |
|---|---|---|
| OPT-01 | Luân phiên ngăn cùng size | Tùy chọn sau Best Fit; tie-break ID nhỏ nhất đang chờ review |
| OPT-02 | Thống kê nâng size/hiệu suất | Tùy chọn từ audit |
| OPT-03 | TinyML | Sau MVP, không triển khai M0–M6 hiện tại |

Không có cảm biến kiện hàng, SMS OTP, SMS/email notification cho đơn, QR/RFID/camera, thanh toán, xác thực shipper thật hay tích hợp hãng vận chuyển trong MVP. Cảm biến cửa và 4 microswitch chốt là bắt buộc. Mã phiên kiosk, Web App notification đơn và CoreIOT notification sự cố vẫn trong phạm vi.

## 7. Truy vết và deliverable môn học

[TEST_PLAN](TEST_PLAN.md) có acceptance, [ISSUES](ISSUES.md) có owner/dependency và [ROADMAP](ROADMAP.md) tách M1 prototype, M2 nền tích hợp/recovery tối thiểu, M3 một ngăn E2E. Mọi tính năng chỉ DONE khi code chạy trên môi trường đích, test/evidence phù hợp và người còn lại review. Các test hiện chỉ là kế hoạch.

DOC-01 cần PDF theo mẫu, tên `[Mã lớp]_[Mã nhóm]_BaoCaoIoT.pdf`, bảng tự đánh giá công nghệ, bảng phân công, ≥5 tham khảo, trích phần kế thừa, GitHub có quyền giảng viên và lịch sử commit của cả hai thành viên, khai báo phạm vi dùng AI, video demo (khuyến nghị 5–10 phút). Mã điểm được tính từ minh chứng, tổng cuối theo thông báo tối đa 10. Mốc tuần 16 phải đối chiếu lịch môn, không tự suy ngày nộp.

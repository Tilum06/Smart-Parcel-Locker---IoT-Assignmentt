# PROJECT SPECIFICATION — SMART PARCEL LOCKER

**Mã dự án:** IOT-SPL  
**Phiên bản:** v1.2 — Chốt cơ cấu 2S + 1M + 1L, chọn S/M/L và quy tắc nâng size  
**Ngày cập nhật:** 10/11/2026  
**Nhóm:** 02 thành viên  
**Mục tiêu môn học:** BTL Internet of Things, CoreIOT + ESP32-S3/YoloUNO  
**Trạng thái:** Đã chốt cơ cấu 4 ngăn và quy tắc chọn size; kích thước thực tế và các quyết định kỹ thuật khác vẫn đang mở.

> **Nguồn yêu cầu:** Các quyết định của nhóm và thông báo BTL IoT. Giá trị tham số, giao thức, ngưỡng thời gian, cách bố trí size và acceptance criteria dưới đây là đề xuất nội bộ để hiện thực, không phải quy định bổ sung của giảng viên.

## 1. Quyết định đã chốt và thay đổi so với v1.0

| Hạng mục | Cấu hình chính thức |
|---|---|
| Thành viên | 2 |
| Mô hình | **4 ngăn: 2×S, 1×M, 1×L** |
| Vi điều khiển | 3 ESP32-S3/YoloUNO |
| Locker Node A | ESP32 #1 quản lý ngăn 1–2 |
| Locker Node B | ESP32 #2 quản lý ngăn 3–4 |
| Central Controller | ESP32 #3, kiosk và điều phối ESP-NOW |
| Màn hình / nhập liệu | ST7789 SPI 240×240 chạy LVGL, keypad vật lý 4×4 |
| Khóa mô hình | Servo + chốt cơ khí; phản hồi trạng thái chốt **chưa chốt** |
| Cảm biến hàng hóa | **KHÔNG SỬ DỤNG** IR, load cell hoặc cảm biến có/không có kiện hàng |
| Cảm biến cửa | Giữ cảm biến cửa đóng/mở cho mỗi ngăn (đề xuất dùng công tắc từ/microswitch) |
| Thông tin shipper nhập | **Mã số phòng, số điện thoại người nhận, size S/M/L**; lựa chọn theo bảng kích thước công bố tại kiosk |
| Phân ngăn | **Best Fit**, tự chọn ngăn trống nhỏ nhất phù hợp; **cho phép nâng lên size lớn hơn** khi hết size tương ứng; tránh cấp trùng |
| Xác nhận bỏ/lấy hàng | Thao tác xác nhận của shipper/người nhận; **không có xác minh bằng cảm biến hàng** |
| Xác thực shipper | Không có, chỉ giới hạn cho demo |
| Người nhận | Đăng nhập Web App để xem đơn và yêu cầu mở ngăn |
| Thông báo người nhận | Trong Web App, không SMS/email/OTP trong MVP |
| IoT | ESP-NOW, PC Gateway 2 chiều, CoreIOT, RuleChain, notification, OTA |
| Lưu dữ liệu | SQLite tại PC Backend/Gateway |
| Bảo trì | Admin được chuyển ngăn vào/ra MAINTENANCE |
| TinyML | Để sau, chưa nằm trong MVP |

**Changelog v1.2 (so với v1.1):**

1. Chốt bốn ngăn theo cơ cấu **2 S + 1 M + 1 L**; mã ngăn tạm đề xuất `L01=S`, `L02=S`, `L03=M`, `L04=L` (có thể đổi vị trí vật lý, không đổi quy tắc).
2. Chốt shipper **chọn S/M/L**, dựa trên bảng kích thước giới hạn của từng loại thay vì nhập ba kích thước vào keypad.
3. Chốt **cho phép cấp ngăn lớn hơn khi hết ngăn đúng size**, luôn lấy ngăn nhỏ nhất còn khả dụng.
4. Cập nhật phân bổ, tiêu chí kiểm thử, BOM và backlog; **kích thước cụ thể (cm) là giá trị đề xuất, chưa chốt cơ khí**.

**Lịch sử thay đổi v1.1:**

1. Xóa yêu cầu phần cứng và xử lý `PARCEL_PRESENT`, `PARCEL_ABSENT`, cảm biến IR/load cell/HX711.
2. Bổ sung ba trường bắt buộc khi đăng ký gửi: `room_code`, `recipient_phone`, `parcel_size`.
3. Thay chiến lược chọn ngăn bất kỳ bằng **best-fit theo size và trạng thái ngăn**.
4. Quy trình gửi/nhận dùng xác nhận người dùng và cảm biến cửa; không tuyên bố thiết bị tự phát hiện có/không có hàng.
5. Cập nhật API, trạng thái, test case, BOM và backlog tương ứng.

## 2. Quy tắc size đã chốt và quyết định kỹ thuật còn mở

### 2.1. Các quyết định đã chốt

| Mã | Quyết định | Trạng thái |
|---|---|---|
| D-02 | Shipper chọn size theo **S / M / L** với giới hạn kích thước được công bố tại kiosk | **ĐÃ CHỐT** |
| D-02A | Phân chia 4 ngăn: **2 S, 1 M, 1 L** | **ĐÃ CHỐT** |
| D-02B | Cho phép cấp ngăn **lớn hơn**; áp dụng Best Fit | **ĐÃ CHỐT** |

**Bố trí ngăn logic đề xuất:** `L01=S`, `L02=S`, `L03=M`, `L04=L` (thứ tự vật lý có thể thay đổi).

**Bảng ngưỡng kích thước mẫu cho mô hình để bàn — CHƯA CHỐT SỐ ĐO CUỐI CÙNG:**

| Size | Kích thước kiện tối đa đề xuất (rộng × cao × sâu) | Kích thước lọt lòng ngăn tối thiểu đề xuất | Số ngăn |
|---|---|---|---:|
| S | 8 × 8 × 8 cm | 10 × 10 × 10 cm | 2 |
| M | 12 × 12 × 12 cm | 14 × 14 × 14 cm | 1 |
| L | 16 × 16 × 16 cm | 18 × 18 × 18 cm | 1 |

Các kích thước trên **chỉ là phương án tham khảo để thiết kế mô hình**, không phải kích thước người dùng đã xác nhận. Nhóm cần đo lại kích thước lọt lòng thực tế sau khi dựng vách, cửa, bản lề và chốt; điều chỉnh giới hạn kiện hàng để có khoảng hở thao tác. Không đánh giá khả năng chứa dựa riêng vào thể tích; phải vừa cả ba chiều theo một hướng đặt hợp lệ.

**Giao diện kiosk:** Hiển thị lần lượt `S – tối đa ...`, `M – tối đa ...`, `L – tối đa ...` trên ST7789. Người gửi tự chọn size phù hợp; hệ thống **không đo kích thước hàng**. Màn hình có thể hiển thị thông số đầy đủ trong trang thông tin size riêng để tránh chữ quá nhỏ.

**Quy tắc cấp ngăn:**

1. Kiểm tra đơn và tài khoản người nhận theo quy trình đã chốt; chỉ xét ngăn `AVAILABLE`, online, không lỗi và không bảo trì.
2. Tìm ngăn có size **nhỏ nhất nhưng không nhỏ hơn size hàng**: `S → S/M/L`, `M → M/L`, `L → L`.
3. Nếu có nhiều ngăn cùng size (hai ngăn S), chọn ngăn có ID nhỏ nhất còn hợp lệ để kết quả dễ kiểm thử (có thể đổi sang luân phiên sau).
4. Đặt giữ ngăn bằng **giao dịch atomic SQLite**, ngăn việc hai yêu cầu đồng thời cấp cùng một ngăn.
5. Khi không còn ngăn đủ lớn, trả `NO_SUITABLE_LOCKER` và không mở khóa.
6. Nếu cấp ngăn lớn hơn, hiển thị rõ `Đã nâng size từ S lên M` (hoặc trường hợp tương ứng) để shipper biết ngăn được chọn.
7. Ghi `requested_size`, `allocated_locker_size`, `locker_id` trong bản ghi đơn để đối chiếu và tạo số liệu cho báo cáo.

**Ví dụ:** Nếu L01 và L02 (S) đang có hàng, L03 (M) trống và L04 (L) trống, một kiện S được cấp L03; kiện M sau đó được cấp L04; kiện L tiếp theo bị từ chối vì không còn ngăn L.

### 2.2. Các quyết định còn mở

| ID | Quyết định | Mức ưu tiên | Gợi ý, chưa chốt |
|---|---|---|---|
| D-01 | **Kích thước thực tế** của S/M/L, kích thước kiện tối đa và khoảng hở cơ khí | **Blocker** | Có bảng mẫu tại 2.1; đo/duyệt kích thước trước khi dựng tủ |
| D-03 | Cơ chế xác nhận chốt servo đã gài thật | **Blocker** | Microswitch phản hồi chốt, hoặc ghi rõ chỉ kiểm tra lệnh servo và hạn chế an toàn |
| D-04 | Liên kết `room_code` + số điện thoại với tài khoản Web App | **Blocker** | Danh sách phòng–tài khoản đã đăng ký trước; không dựa vào số phòng đơn thuần |
| D-05 | Có cần xác nhận người nhận đang đứng tại tủ trước khi mở từ Web App? | Cao | Mã phiên kiosk ngắn hạn hoặc cơ chế tương đương |
| D-06 | Thời gian giữ ngăn và timeout mở cửa | Cao | Cần timeout, trường hợp gửi dở cần kiểm tra trước khi giải phóng |
| D-07 | Kết nối Controller ↔ PC Gateway | Trung bình | USB Serial + JSON Lines |
| D-08 | Khôi phục giao dịch mất mạng, mất điện, người dùng xác nhận sai | Cao | Không tự gán ngăn AVAILABLE sau khi khởi động lại |
| D-09 | Loại servo, nguồn, chốt, vật liệu, sơ đồ chân | Cao | Thử độ ổn định cơ khí trước khi lắp 4 ngăn |
| D-10 | Phạm vi cập nhật OTA | Trung bình | Demo ít nhất một ESP32 với thay đổi firmware kiểm chứng được |

## 3. Mục tiêu và phạm vi

Hệ thống 4 ngăn hỗ trợ chu trình: **đăng ký bằng phòng + số điện thoại + size → phân ngăn → mở chốt → shipper đặt hàng và xác nhận → cửa đóng/khóa → thông báo Web App → người nhận đăng nhập và yêu cầu mở → lấy hàng và xác nhận → đóng/khóa → hoàn tất**.

Trong MVP **không có**: SMS OTP, đầu đọc QR, RFID, camera, cảm biến kiện hàng, xác thực shipper thật, thanh toán, tích hợp bên vận chuyển, TinyML. Demo không đồng nghĩa sản phẩm đủ an toàn để vận hành công cộng.

## 4. Kiến trúc hệ thống

```text
  Ngăn 1–2                     Ngăn 3–4
[Servo + Door Sensor]        [Servo + Door Sensor]
          |                           |
  ESP32 #1 Locker A          ESP32 #2 Locker B
          \                           /
           +------- ESP-NOW ----------+
                       |
           ESP32 #3 Central Controller
           ST7789 + LVGL + Keypad 4×4
               Local Webserver
                       |
             USB Serial (đề xuất)
                       |
              PC Gateway/Backend
         SQLite + Web App + size allocator
                       |
                   MQTT 2 chiều
                       |
                     CoreIOT
      Dashboard + RuleChain + Notification
```

| Thành phần | Trách nhiệm |
|---|---|
| ESP32 #1/#2 | Điều khiển servo; đọc cảm biến cửa; phản hồi trạng thái chốt nếu có phần cứng phù hợp; truyền qua ESP-NOW |
| ESP32 #3 | LVGL + keypad, hiển thị nhập phòng/điện thoại/size và thông tin ngăn, ESP-NOW, Webserver T07, OTA |
| PC Gateway/Backend | Quản lý đơn, tài khoản, ngăn/size, giao dịch SQLite, nhận/truyền lệnh và trạng thái hai chiều, đồng bộ CoreIOT |
| Web App | Người nhận đăng nhập, xem thông báo/đơn, tạo yêu cầu mở ngăn; admin bảo trì |
| CoreIOT | Dashboard giám sát; RuleChain; notification sự cố; điều khiển quản trị được phân quyền |

## 5. Luồng nghiệp vụ chính

### 5.1. Gửi hàng

1. Shipper chọn **GỬI HÀNG** tại kiosk.
2. Nhập **mã số phòng**, **số điện thoại người nhận** và chọn **S/M/L** theo bảng kích thước quy định hiển thị trên ST7789; xem lại và xác nhận thông tin.
3. Backend kiểm tra dữ liệu. Quy tắc đối chiếu `room_code` + `recipient_phone` với tài khoản cần được chốt tại D-04; không gửi thông báo nhầm tài khoản.
4. Backend tạo đơn `CREATED`, tìm ngăn `S/M/L` theo **best-fit** và được phép nâng size như mục 2.1; giữ ngăn nguyên tử ở `RESERVED` và ghi nhận size yêu cầu/size được cấp.
5. Qua Gateway → Controller → Locker Node, gửi lệnh mở servo. Hệ thống xác nhận lệnh và quan sát trạng thái cửa, nếu có; chuyển `DEPOSITING`.
6. Shipper **tự đặt hàng và nhấn 'ĐÃ ĐẶT HÀNG'** trên kiosk. Đây là xác nhận của người dùng, **không phải phép đo cảm biến**.
7. Shipper đóng cửa; hệ thống đọc cửa đóng và điều khiển chốt về trạng thái khóa. Nếu chưa có cảm biến chốt, ghi `LOCK_COMMAND_ACK` thay vì khẳng định `LOCKED` vật lý.
8. Nếu đạt chính sách xác nhận của nhóm, Backend cập nhật đơn `STORED`, ngăn `OCCUPIED`, ghi log và tạo thông báo trong Web App của đúng người nhận.
9. Nếu cửa không đóng/servo lỗi/giao dịch timeout: đưa sang `EXCEPTION`/`UNKNOWN`, không tự gán AVAILABLE khi chưa được đối chiếu; người quản trị xử lý khi cần.

### 5.2. Nhận hàng

1. Người nhận đăng nhập Web App bằng tài khoản được liên kết với phòng và số điện thoại; thấy các đơn của mình.
2. Chọn **NHẬN HÀNG**. Backend kiểm tra quyền, trạng thái đơn/ngăn, kết nối, khóa/door; kiểm tra hiện diện tại kiosk nếu D-05 được thông qua.
3. Backend tạo phiên nhận duy nhất, gửi lệnh mở đúng ngăn, chuyển `COLLECTING` khi lệnh/điều kiện mở được xác nhận.
4. Người nhận lấy kiện hàng rồi chọn **'ĐÃ LẤY HÀNG'** trên Web App; đây là xác nhận của người dùng, **không có cảm biến xác nhận ngăn trống**.
5. Người nhận đóng cửa, chốt khóa được điều khiển. Backend chỉ đánh dấu `COMPLETED` khi đã có xác nhận người nhận và điều kiện cửa/khóa theo chính sách đã chốt.
6. Ngăn trở về `AVAILABLE` theo quy tắc nhóm thống nhất; lịch sử lưu sự kiện `PICKUP_CONFIRMED_BY_USER`, không ghi `PARCEL_ABSENT_SENSOR_VERIFIED`.
7. Nếu người nhận không xác nhận hoặc cửa chưa đóng, tiếp tục trạng thái `COLLECTING`/`EXCEPTION`, cảnh báo và xử lý bảo trì khi cần.

### 5.3. Giới hạn do không có cảm biến hàng

- Không thể tự phát hiện shipper bỏ trống ngăn nhưng nhấn 'Đã đặt hàng'.
- Không thể tự phát hiện người nhận chưa lấy hàng nhưng nhấn 'Đã lấy hàng'.
- Không thể tự xác minh ngăn trống sau giao dịch; độ tin cậy của bước này dựa trên người dùng, chính sách vận hành và kiểm tra quản trị nếu có bất thường.
- Cần nêu rõ giới hạn trong báo cáo, test case và video. Không tuyên bố hệ thống tự động kiểm chứng hiện diện hàng hóa.

## 6. Trạng thái và quy tắc nhất quán

**Ngăn:** `AVAILABLE → RESERVED → DEPOSITING → OCCUPIED → COLLECTING → AVAILABLE`, với `FAULT`, `MAINTENANCE`, `UNKNOWN`.

**Đơn:** `CREATED → DEPOSITING → STORED → PICKUP_PENDING → COMPLETED`, với `CANCELLED`, `EXCEPTION`.

**Sự kiện:** `ROOM_PHONE_SIZE_SUBMITTED`, `LOCKER_RESERVED`, `UNLOCK_REQUESTED`, `DOOR_OPENED`, `DEPOSIT_CONFIRMED_BY_SHIPPER`, `DOOR_CLOSED`, `LOCK_COMMAND_ACK`, `DEPOSIT_COMPLETED`, `PICKUP_REQUESTED`, `PICKUP_CONFIRMED_BY_RECIPIENT`, `PICKUP_COMPLETED`, `DEVICE_OFFLINE`, `MAINTENANCE_CHANGED`.

**Bất biến bắt buộc:** Một ngăn không được cấp cho nhiều đơn cùng lúc; không tự reset về `AVAILABLE` sau reboot nếu chưa có kết quả đối chiếu; mọi lệnh mở cần `request_id` để tránh xử lý lặp.

## 7. Functional Requirements và Acceptance Criteria

| ID | Yêu cầu | Tiêu chí nghiệm thu |
|---|---|---|
| FR-01 | Kiosk cho nhập mã phòng, SĐT, size | Nhập/sửa/xác nhận bằng keypad + ST7789 thực |
| FR-02 | Kiểm tra đầu vào và định danh tài khoản người nhận | Dữ liệu thiếu/sai bị từ chối; không phát thông báo nhầm người |
| FR-03 | Phân ngăn theo S/M/L | Đúng cơ cấu 2S+1M+1L; ưu tiên ngăn nhỏ nhất còn trống; được cấp ngăn lớn hơn; không bao giờ cấp ngăn nhỏ hơn |
| FR-04 | Chống cấp trùng ngăn | Hai yêu cầu đồng thời không nhận cùng một ngăn |
| FR-05 | Mở khóa qua ESP-NOW | Mở đúng ngăn; ghi ACK/lỗi; không mở khi node offline |
| FR-06 | Xác nhận gửi do shipper thực hiện | Không có xác nhận thì không hoàn tất gửi; xác nhận không được trình bày là dữ liệu cảm biến |
| FR-07 | Kiểm tra cửa đóng và thao tác khóa | Chỉ cập nhật trạng thái theo mức phản hồi cơ khí thực có |
| FR-08 | Thông báo trong Web App | Đúng tài khoản người nhận thấy đơn, tài khoản khác không thấy |
| FR-09 | Người nhận đăng nhập và yêu cầu lấy hàng | Chỉ đúng tài khoản được mở đúng ngăn; chống double-submit |
| FR-10 | Người nhận xác nhận đã lấy hàng | Không hoàn tất nếu chưa xác nhận hoặc cửa chưa đóng |
| FR-11 | Cảnh báo sự cố | Tủ hết ngăn phù hợp, cửa mở quá lâu, servo lỗi, node offline, mất kết nối |
| FR-12 | SQLite và audit log | Lưu đơn, phòng, SĐT (được bảo vệ), size, ngăn, trạng thái, xác nhận, lỗi; dữ liệu còn sau restart |
| FR-13 | Chế độ bảo trì | Admin đưa ngăn vào/ra MAINTENANCE, không phân bổ ngăn này |
| FR-14 | Webserver trên ESP32 (T07) | Giám sát, thao tác local được phân quyền và demo trên ESP32 thực |
| FR-15 | PC Gateway hai chiều (T08) | Telemetry lên CoreIOT và lệnh ngược về ESP32 được xác nhận |
| FR-16 | CoreIOT T11/T12/T13 | Dashboard theo template, RuleChain có xử lý và nhận notification |
| FR-17 | OTA (T14) | Có firmware v1.0→v1.1, cập nhật và chạy ổn định sau reboot |
| FR-18 | LVGL (N03) | ST7789 chạy menu nhập liệu, kết quả phân ngăn và hướng dẫn gửi/nhận |

## 8. Interfaces (dự thảo)

### 8.1. Đơn hàng / yêu cầu gửi

```json
{
  "room_code": "A-305",
  "recipient_phone": "09xxxxxxxx",
  "parcel_size": "M",
  "request_id": "req-demo-001"
}
```

Ví dụ dữ liệu giả, không phải thông tin người nhận thực.

Backend phản hồi một trong các kết quả: `ACCEPTED`, `RECIPIENT_NOT_FOUND`, `INVALID_ROOM_PHONE`, `INVALID_SIZE`, `NO_SUITABLE_LOCKER`, `DEVICE_OFFLINE`, `ERROR`. Khi được cấp ngăn thành công, phản hồi kèm `parcel_id`, `locker_id`, `requested_size`, `allocated_locker_size`, `transaction_state`, và `size_upgraded` (boolean).

### 8.2. ESP-NOW

Cần tối thiểu `version`, `node_id`, `locker_id`, `sequence`, `message_type`, `door_state`, `servo_command_state`, `request_id`; `lock_state` chỉ được ghi là `LOCKED` nếu có phản hồi phần cứng hợp lệ. **Không có trường `parcel_state`.**

### 8.3. Controller ↔ Gateway

Đề xuất USB Serial + JSON Lines, gồm `COMMAND`, `ACK`, `ERROR`, `DOOR_EVENT`, `DEVICE_HEARTBEAT`, `STATUS`. Có cơ chế timeout, retry an toàn và chống xử lý lệnh trùng.

### 8.4. Backend / Web App

- `POST /deposits` — Nhận phòng, số điện thoại, size; cấp ngăn theo best-fit.
- `POST /deposits/{id}/confirm` — Shipper xác nhận đã đặt hàng, backend đối chiếu cửa và phản hồi khóa theo thiết kế.
- `GET /me/parcels` — Người nhận xem các kiện hàng liên kết tài khoản.
- `GET /me/notifications` — Hộp thông báo Web App.
- `POST /parcels/{id}/pickup` — Người nhận yêu cầu mở ngăn.
- `POST /parcels/{id}/confirm-pickup` — Người nhận xác nhận đã lấy hàng.
- `POST /admin/lockers/{id}/maintenance` — Quản trị viên bảo trì ngăn.

Phân quyền mọi API; không dựa vào `user_id`/`room_code` do client tự khai để xác định quyền mở khóa.

### 8.5. CoreIOT

Telemetry: `door_state`, `lock_state` nếu có phản hồi, `locker_availability`, `node_online`, `errors`, `transaction_count`. Không gửi SĐT và mã phòng lên dashboard nếu không cần. T11 template/dashboard; T12 RuleChain cảnh báo cửa mở lâu, node offline và sai lệch trạng thái; T13 notification CoreIOT về sự cố (khác thông báo kiện hàng trên Web App).

## 9. BOM — Phần cứng dự kiến

| Thành phần | Số lượng | Trạng thái |
|---|---:|---|
| ESP32-S3/YoloUNO | 3 | Chốt số lượng |
| TFT ST7789 SPI 240×240 | 1 | Đã có |
| Keypad ma trận 4×4 | 1 | Đã chốt cách nhập |
| Servo + cơ cấu chốt | 4 bộ | Chốt nguyên lý, chưa chốt model |
| Cảm biến cửa (reed switch/microswitch) | 4 | Giữ trong kiến trúc |
| Cảm biến phản hồi chốt | 0–4 | Chưa chốt D-03 |
| Nguồn servo riêng, dây và phụ kiện | 1 bộ | Chưa chốt thông số |
| Khung tủ 4 ngăn (2×S, 1×M, 1×L) | 1 | **Đã chốt cơ cấu; kích thước cm chưa chốt D-01** |
| PC/Laptop Gateway + Backend | 1 | Cần để demo |
| Cảm biến phát hiện hàng IR/load cell/HX711 | **0** | **Loại bỏ khỏi dự án** |

## 10. Ánh xạ mã điểm BTL

| Mã | Công nghệ / minh chứng | Điểm |
|---|---|---:|
| T06 | ESP-NOW giữa các ESP32 | 1,5 |
| T07 | Webserver tự phát triển **trên ESP32** | 1,0 |
| T08 | PC Gateway gom dữ liệu, gửi CoreIOT, nhận và phân phối lệnh | 1,0 |
| T11 | Template, dashboard, giám sát và điều khiển CoreIOT | 1,0 |
| T12 | RuleChain tạo tính năng thông minh | 1,0 |
| T13 | CoreIOT notification khi vượt ngưỡng/sự cố | 0,5 |
| T14 | OTA firmware ESP32, có demo cập nhật thực | 2,0 |
| **Tổng công nghệ** | | **8,0** |
| N03 | ST7789 chạy LVGL trên ESP32 | +1 nâng cao |
| Báo cáo | Theo mẫu, số liệu thử nghiệm, >= 5 tài liệu tham khảo | Tối đa 2 |

Mã công nghệ chỉ tính khi đã hiện thực và có minh chứng; tổng điểm BTL theo thông báo giới hạn tối đa 10. TinyML giữ ngoài MVP.

## 11. Test Plan (cập nhật, không dùng cảm biến hàng)

| Test ID | Tình huống | PASS |
|---|---|---|
| TC-01 | Nhập phòng, SĐT và size hợp lệ | Tạo đơn, chọn ngăn phù hợp; mở đúng ngăn |
| TC-02 | Yêu cầu hàng L nhưng chỉ còn S/M | Trả `NO_SUITABLE_LOCKER`; không mở khóa |
| TC-03 | Hai yêu cầu gửi gần đồng thời | Không được phân bổ trùng ngăn |
| TC-19 | Hai ngăn S đã bận; M trống; gửi hàng S | Cấp ngăn M; lưu `size_upgraded=true` |
| TC-20 | Hai ngăn S và M đã bận; L trống; gửi hàng S hoặc M | Cấp ngăn L; không cấp ngăn nhỏ không phù hợp |
| TC-21 | Chỉ còn S trống; gửi hàng M | Trả `NO_SUITABLE_LOCKER`; không cấp ngăn S |
| TC-22 | Có cả S và M trống; gửi hàng S | Ưu tiên S; giữ M cho kiện lớn hơn |
| TC-04 | Shipper không bấm xác nhận đã đặt hàng | Không chuyển đơn thành `STORED` |
| TC-05 | Shipper bấm xác nhận nhưng cửa còn mở | Không hoàn tất, nhắc đóng cửa, báo timeout nếu quá hạn |
| TC-06 | Cửa đóng và xác nhận đặt hàng | Đơn chuyển `STORED` theo chính sách khóa đã chọn; thông báo đúng người |
| TC-07 | Phòng và SĐT không khớp tài khoản | Không gán đơn nhầm người; trả lỗi/đưa vào quy trình đã chốt |
| TC-08 | Người nhận đúng tài khoản yêu cầu mở | Chỉ đúng ngăn được mở |
| TC-09 | Người dùng khác yêu cầu mở | Từ chối, không gửi lệnh mở |
| TC-10 | Người nhận chưa bấm xác nhận đã lấy | Không chuyển `COMPLETED` |
| TC-11 | Người nhận xác nhận đã lấy, cửa đóng | Hoàn tất giao dịch và giải phóng ngăn theo chính sách |
| TC-12 | Cửa mở quá lâu | Ghi sự kiện, CoreIOT RuleChain/notification hoạt động |
| TC-13 | Tắt một Locker Node | Không phân bổ/mở ngăn của node offline |
| TC-14 | Ngắt kết nối/khởi động lại khi có đơn | Không tự gán ngăn `AVAILABLE` khi chưa đối chiếu |
| TC-15 | Đưa ngăn vào MAINTENANCE | Không phân bổ ngăn; có audit log |
| TC-16 | ESP32 Webserver, OTA, LVGL | Demo được T07, T14, N03 trên thiết bị thật |
| TC-17 | CoreIOT dashboard và Gateway hai chiều | Demo T08, T11/T12/T13 |
| TC-18 | Kiểm tra giới hạn không cảm biến hàng | Báo cáo xác định rõ đây là xác nhận người dùng, không kết luận đo được kiện hàng |

## 12. Work Packages và phân công

| WP | Chủ trì | Đầu ra | Phụ thuộc |
|---|---|---|---|
| WP-01 Khung, size, servo, cửa | A | Mô hình 2×S, 1×M, 1×L có kích thước đo được, sơ đồ điện | D-01, D-03 |
| WP-02 Firmware Locker Node | A | Servo, door sensor, ESP-NOW | WP-01 |
| WP-03 Kiosk LVGL / keypad | A | Form phòng + SĐT + lựa chọn S/M/L; thông số kích thước; xác nhận gửi | Giao thức |
| WP-04 Webserver ESP32 + OTA | A | T07/T14 và minh chứng | WP-03 |
| WP-05 PC Gateway + CoreIOT | B | USB Serial, MQTT, RPC, telemetry hai chiều | D-07 |
| WP-06 Backend phân ngăn + SQLite | B | Best-fit S/M/L, fallback lên size lớn, đặt giữ atomic, audit log | D-01, D-04 |
| WP-07 Web App người nhận | B | Đăng nhập, thông báo, yêu cầu mở, xác nhận nhận | D-04, D-05 |
| WP-08 RuleChain/notification/bảo trì | B | T12/T13, admin maintenance | WP-05, WP-06 |
| WP-09 Tích hợp, đo đạc, báo cáo | A+B | Test plan, GitHub, báo cáo PDF và video | Tất cả |

Hai thành viên cùng duyệt giao thức, state machine, phân quyền và các API trước khi lập trình độc lập.

## 13. Lộ trình 6 tuần (đề xuất)

| Tuần | Mốc hoàn thành |
|---|---|
| 1 | Chốt **kích thước cm** theo cơ cấu 2S+1M+1L, quyền người nhận, sơ đồ cơ khí và giao thức |
| 2 | Servo/cửa, 2 Locker Nodes, ESP-NOW, giao diện LVGL nhập phòng/SĐT/size |
| 3 | Backend SQLite best-fit, cấp ngăn atomic; Gateway và CoreIOT telemetry |
| 4 | Tích hợp gửi–nhận Web App, xác nhận người dùng, RPC hai chiều, xử lý lỗi |
| 5 | Webserver ESP32, RuleChain/notification, OTA, thử nghiệm mất kết nối |
| 6 | Kiểm thử, đo đạc, sửa lỗi, README, báo cáo PDF và video demo |

Ưu tiên hạn nộp chính thức tuần 16 theo thông báo của môn hơn lịch nội bộ.

## 14. Definition of Done

Task chỉ DONE khi (1) code lên repo; (2) chạy được trên môi trường đích; (3) test tương ứng PASS; (4) có ảnh/log/video hoặc dữ liệu đo; (5) cập nhật tài liệu/API/GPIO; (6) thành viên còn lại review.

## 15. Quyết định cần chốt tiếp

- [x] **D-02/D-02A/D-02B:** 2×S, 1×M, 1×L; chọn S/M/L trên kiosk theo giới hạn kích thước niêm yết; cho phép cấp ngăn lớn hơn.
- [ ] **D-01:** Chốt kích thước kiện tối đa và kích thước lọt lòng thực tế (cm/mm) cho S, M, L; bảng ở 2.1 chỉ là đề xuất.
- [ ] **D-03:** Có cảm biến xác nhận chốt khóa không? Nếu không, chấp nhận giới hạn xác nhận khóa ở mức lệnh servo.
- [ ] **D-04:** Quy tắc xác thực kết hợp **mã phòng + SĐT** với tài khoản nhận hàng.
- [ ] **D-05:** Người nhận phải hiện diện tại kiosk khi mở Web App hay cho phép mở từ xa?
- [ ] **D-06:** Timeout khi shipper/người nhận không hoàn tất thao tác; quy trình xử lý ngăn có thể chứa hàng.
- [ ] **D-07:** USB Serial hay LAN kết nối Controller ↔ PC; xử lý khôi phục.
- [ ] **D-08:** Servo, nguồn, GPIO, vật liệu và cơ cấu cửa.
- [ ] **D-09:** Node nào phải demo OTA.

**Không còn quyết định chọn loại cảm biến hàng.** Quyết định loại bỏ cảm biến hàng đã được chốt từ v1.1. Cơ cấu 2S/1M/1L, giao diện chọn S/M/L và quy tắc nâng size đã chốt ở v1.2; chỉ còn phải quyết định các kích thước thực tế và phần cứng/cơ chế xác thực liên quan.

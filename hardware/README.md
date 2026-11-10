# Phần cứng và HW-01 — baseline revision 1.3

Owner **Member A**, B review mapping/giao tiếp. Loại feedback đã duyệt D-03: mỗi ngăn có servo/chốt, door sensor và **microswitch xác nhận chốt gài**. Chưa đo/đấu điện hoặc chốt model/nguồn/GPIO, không tự chọn board profile/góc servo.

## BOM phạm vi đã duyệt

| Hạng mục | Số lượng | Phần còn cần đo/duyệt |
|---|---:|---|
| ESP32-S3/YoloUNO | 3 | Board/revision/pinout, flash/partition/profile Arduino |
| ST7789 SPI 240×240 | 1 | Module thực, điện áp/pin và LVGL/display lib version |
| Keypad ma trận 4×4 | 1 | Mapping hàng/cột, nhập phòng số/sửa/xóa/size |
| Servo + chốt | 4 bộ | Model/tải/góc/hành trình/gá/nguồn D-09 |
| Cảm biến cửa | 4 | Loại/model/polarity/debounce/gá thực |
| Microswitch chốt | **4** | Model/gá/polarity/debounce để đo ENGAGED, không còn phương án 0 microswitch |
| Nguồn servo và dây/đầu nối/bảo vệ | 1 bộ | Thông số theo tải đo và sơ đồ điện đã duyệt |
| Tủ 2S/1M/1L | 1 bộ | L01/L02=S, L03=M, L04=L; kích thước cm/clearance D-01 chưa chốt |
| PC/cáp USB dữ liệu | 1 bộ | USB Serial đã chọn, test COM/board thực |
| Cảm biến hàng IR/load cell/HX711 | **0** | Không thuộc MVP |

Door OPEN/CLOSED/UNKNOWN, servo command và latch ENGAGED/NOT_ENGAGED/UNKNOWN phải đo riêng. Microswitch chỉ xác nhận chốt gài: nhả switch không chứng minh đã xác minh vị trí mở hoàn toàn. Không suy latch từ góc/ACK/cửa.

## HW-01 M1 không chờ FW-01

HW-01 có thể chứa sketch/test jig tối thiểu điều khiển servo và đọc hai sensor để đo/gá một ngăn, không cần project firmware đầy đủ M2. Nếu thử radio/Serial, dùng subset protocol v1 M1 trong [INTERFACES](../docs/INTERFACES.md), không tạo protocol khác. Test jig không tạo đơn thật hoặc quyền mở nghiệp vụ.

- [ ] Ghi/chụp đúng board YoloUNO/revision, pinout chính thức và flash/partition; xác minh target trước build/upload.
- [ ] Chọn cơ cấu một ngăn, model servo/door/microswitch; đo hành trình/tải/nguồn và điều kiện thử trước cấp điện.
- [ ] Duyệt nguồn servo và wiring phù hợp điện áp/tải thực, mass tham chiếu/dây/bảo vệ; không suy khả năng cấp servo từ chân nguồn board.
- [ ] Bảng GPIO cho từng node servo/door/latch và Central ST7789/keypad/USB; kiểm chân chức năng/khởi động, không đoán pin.
- [ ] Đo polarity/debounce/gá cửa và latch; tách UNKNOWN, test switch nhả không coi là mở hoàn toàn.
- [ ] Sketch/jig test guard LOCK chỉ khi door CLOSED; OPEN/UNKNOWN phải từ chối trước servo, TC-28/30.
- [ ] Đề xuất 20 chu kỳ sau duyệt tải/số lần, ghi reset/jam/latch không gài; có ảnh/log/video thực, không ghi PASS trước thử.
- [ ] D-01 đo lọt lòng/clearance/kiện tối đa trước chế tạo cuối và bảng size thật; số cm mẫu v1.2 không phải sản xuất. Khảo sát/test jig không đợi chốt cả tủ.
- [ ] Dán nhãn mapping L01/L02=S, L03=M, L04=L; chỉ nhân bốn cơ cấu khi một ngăn đủ bằng chứng.
- [ ] Nếu board/toolchain sẵn, spike riêng ESP-NOW, ST7789/LVGL và OTA Central; đo RAM/flash/partition/Wi-Fi-radio coexistence, không coi scope T14 cuối đã đóng.

Không cần cloud/OTA xong để bắt đầu BOM/prototype, nhưng D-09 điện/board phải được kiểm trước đấu/build. Model/nguồn/GPIO/góc/debounce vẫn mở; [DECISIONS](../docs/DECISIONS.md) theo dõi D-01/09/10. Giữ số đo/sơ đồ/BOM đã review tại đây, không credential thật. [TEST_PLAN](../docs/TEST_PLAN.md) là acceptance, chưa có test hardware chạy.

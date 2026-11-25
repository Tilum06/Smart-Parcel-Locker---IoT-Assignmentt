# Pinout — Smart Parcel Locker MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

**Nguồn tham chiếu duy nhất cho đấu chân của dự án**, cập nhật 25/11/2026. Đây là **baseline triển khai dự kiến**, đã đối chiếu tài liệu nhưng **chưa Verified trên hai board thực tế**. Các README chỉ tóm tắt và dẫn về đây.

## Nguồn đối chiếu và giới hạn

1. [OhStem: giới thiệu Yolo UNO, mục sơ đồ chân](https://docs.ohstem.vn/en/latest/yolo_uno/yolo_uno_khoi_lenh/gioi_thieu_yolo_uno.html), [ảnh pinout chính thức](https://docs.ohstem.vn/en/latest/_images/so_do_chan.jpg), đọc trực tiếp ngày 25/11/2026. Các cặp D2…D11 và A0/A1/A3 dùng bên dưới khớp ảnh; không cần đổi mapping mục tiêu.
2. [OhStem: môi trường PlatformIO](https://wiki.ohstem.vn/orc_bot/arduino_platformio/cai_dat) dẫn tới sample AITT-VN; [variant Yolo UNO trong sample](https://github.com/AITT-VN/orc_hub_arduino_examples/blob/main/variants/yolo_uno/pins_arduino.h) cho A0=1, A1=2, A3=4, SDA=11, SCL=12, TX=43, RX=44. SPI mặc định trong variant khác SPI tùy chỉnh ST7789 của dự án; không dùng mặc định thay bảng này.
3. [Espressif: GPIO ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html) và [ESP32-S3 datasheet, strapping](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf): USB GPIO19/20; hạn chế flash/PSRAM; chân strapping.

**Sai lệch nguồn cần xử lý trước firmware:** ảnh OhStem ghi NeoPixel GPIO45, D13 GPIO48, D12 GPIO47; sample variant lại định nghĩa PIN_NEOPIXEL=48. Trang OhStem cũng mô tả LED ở D13. Không thể lấy một board definition chung để chứng minh đúng revision đang cầm. Giữ cả GPIO45/GPIO48 ngoài phân bổ MVP, đối chiếu revision/schematic/board thật trước dùng LED onboard. Không tự kết luận một nguồn sai hoặc sửa firmware thử nghiệm.

Chưa có ảnh/revision/schematic và phép đo của hai board dự án. Việc khớp tài liệu không thay thế xác minh nhãn chân, continuity và thử chức năng trên board thật. Tên Dn in trên board **không đồng nghĩa GPIOn**; khi dùng Arduino cần kiểm alias của board definition hoặc cấu hình số GPIO thực tập trung trong pin_config.h.

## Central Controller — Node ID 1

### ST7789 SPI 240×240

| ST7789 | Yolo UNO | GPIO | Chức năng |
|---|---|---:|---|
| VCC | 3.3V | — | Nguồn, kiểm module thực tế |
| GND | GND | — | Mass |
| SCL/SCK | D7 | 10 | SPI Clock |
| SDA/MOSI | D8 | 17 | SPI Data |
| RES/RST | D10 | 21 | Reset |
| DC | D9 | 18 | Data/Command |
| CS | D11 | 38 | Chip Select |
| BLK/BL | 3.3V | — | Backlight, chỉ nối sau khi kiểm thông số module |

Sử dụng SPI tùy chỉnh; không cần MISO với màn hình chỉ ghi. Module không có CS: cấu hình CS=-1, giữ GPIO38 dự phòng. Không giả định pinout vật lý hoặc mạch backlight của mọi module giống nhau; kiểm điện áp/dòng và mạch BLK trước khi nối trực tiếp nguồn. Chưa chốt thư viện/display initialization/rotation theo module thực.

### Keypad ma trận 4×4

| Keypad | Yolo UNO | GPIO |
|---|---|---:|
| R1 | D2 | 5 |
| R2 | D3 | 6 |
| R3 | D4 | 7 |
| R4 | D5 | 8 |
| C1 | D6 | 9 |
| C2 | A0 | 1 |
| C3 | A1 | 2 |
| C4 | A3 | 4 |

```text
1  2  3  A
4  5  6  B
7  8  9  C
*  0  #  D
```

Keypad thụ động, không cần nguồn riêng. Thứ tự tám dây R1–R4/C1–C4 phải xác minh bằng datasheet hoặc đồng hồ thông mạch; không suy từ vị trí đầu cáp. Mapping phím chức năng, debounce và xử lý nhập PIN là Planned.

## Locker Node — Node ID 2

| Thiết bị | Yolo UNO | GPIO | Mode |
|---|---|---:|---|
| Servo L01 (S) | D4 | 7 | PWM Output |
| Servo L02 (M) | D6 | 9 | PWM Output |
| MC-38 L01 | A3 | 4 | INPUT_PULLUP |
| MC-38 L02 | A0 | 1 | INPUT_PULLUP |

MG90S: đỏ → +5V ngoài; nâu/đen → GND nguồn; cam/vàng → GPIO PWM tương ứng. GND nguồn nối GND Node. Kiểm màu dây trên servo thực, không cấp servo từ GPIO/3.3V. PWM frequency, pulse width và góc đóng/mở chưa chốt; hiệu chỉnh theo cơ cấu chốt, không mặc định 0°/90°.

MC-38: một dây GPIO, một dây GND; INPUT_PULLUP và software debounce. **Nếu tiếp điểm đóng khi nam châm gần:** LOW=CLOSED, HIGH=OPEN. Đây là cực tính dự kiến; tên NC không đủ để kết luận trong lắp đặt thực tế. Đo tiếp điểm khi nam châm gần/xa, kiểm vị trí lắp và debounce trước chốt firmware. Đứt dây/đọc không đáng tin phải được xử lý theo trạng thái an toàn, không suy chốt đã gài.

## Tổng hợp GPIO trên từng board

Hai board có không gian GPIO độc lập; GPIO7 dùng trên cả hai không gây xung đột. Không có GPIO trùng giữa các chức năng đã phân bổ **trên cùng một board**. GPIO38 chỉ dùng nếu ST7789 có CS.

| Phân loại | Central ID 1 | Locker Node ID 2 |
|---|---|---|
| Đã phân bổ | 1, 2, 4, 5, 6, 7, 8, 9 (keypad); 10, 17, 18, 21, 38 (display) | 7, 9 (servo); 4, 1 (cửa) |
| Còn trống ở header, có thể xem xét sau review | D12/GPIO47; GPIO38 nếu CS=-1 | A1/GPIO2, D2/GPIO5, D3/GPIO6, D5/GPIO8, D7/GPIO10, D8/GPIO17, D9/GPIO18, D10/GPIO21, D11/GPIO38, D12/GPIO47 |
| Reserved native USB | GPIO19, GPIO20 | GPIO19, GPIO20 |
| Reserved I2C | SDA/A4/GPIO11, SCL/A5/GPIO12 | SDA/A4/GPIO11, SCL/A5/GPIO12 |
| Reserved UART | D1/TX/GPIO43, D0/RX/GPIO44 | D1/TX/GPIO43, D0/RX/GPIO44 |
| Không nên dùng: strapping/BOOT | GPIO0, A2/GPIO3, GPIO45, GPIO46 | GPIO0, A2/GPIO3, GPIO45, GPIO46 |
| Reserved onboard, cần kiểm revision | GPIO45 NeoPixel theo ảnh; D13/GPIO48 liên quan LED, khác sample | GPIO45 NeoPixel theo ảnh; D13/GPIO48 liên quan LED, khác sample |
| Không phân bổ cho MVP: flash/PSRAM | GPIO26–32; GPIO33–37 nếu module dùng Octal memory | GPIO26–32; GPIO33–37 nếu module dùng Octal memory |
| Chưa chứng minh được đưa ra header/rảnh | GPIO13–16, GPIO39–42; các pad khác không thể hiện trong sơ đồ | GPIO13–16, GPIO39–42; các pad khác không thể hiện trong sơ đồ |

Reserved và không nên dùng có thể giao nhau (GPIO45 vừa strapping vừa onboard); không cộng các hàng thành số GPIO rảnh. GPIO22–25 không tồn tại trên ESP32-S3. Header/Grove/GVS có thể là cùng một net: không tính nhiều chân độc lập và không cắm thiết bị thứ hai lên net đã dùng. Không suy thêm mapping A6 từ tên cổng khi chưa đối chiếu schematic.

## Nguồn điện và kiểm thử

- Central cấp USB từ laptop; Locker Node cấp USB riêng.
- Servo có nguồn **5V ngoài**; adapter 5V–2A hiện có **phải kiểm thử hai servo dưới tải**, không mặc định đủ dòng.
- GND nguồn servo phải chung GND Locker Node. Không cấp servo từ GPIO/3.3V hoặc mặc định đường 5V USB board chịu được tải motor.
- Hai ESP32 không cần nối GND trực tiếp với nhau vì ESP-NOW. Không nối tùy tiện các đường +5V của USB và nguồn servo.
- Đo điện áp/dòng khi chạy từng servo, cả hai và khi chốt chịu tải; kiểm brownout/reset/nhiệt và cơ khí. Chưa có evidence tải, góc hay trạng thái khóa cơ khí.

Trước đấu/nạp firmware v2.1: xác nhận revision hai board → nhãn/GPIO → CS/BLK module → keypad continuity → MC-38 polarity → servo không tải rồi có chốt → hai servo/nguồn → ghi log/ảnh/phép đo. Central test hiện còn esp32dev và test relay dùng chân trùng servo mục tiêu: phải chọn đúng firmware cho đúng wiring, không coi project test là cấu hình v2.1 đã sẵn sàng.

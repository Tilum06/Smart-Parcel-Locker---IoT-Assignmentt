# Central Controller — MVP v2.1, Phase 0

Project PlatformIO độc lập, C++/Arduino, cho Central Yolo UNO ESP32-S3 **Node ID 1**. Firmware version **2.1.0-phase0**. Repository phát triển `E:/01_Study/project/iot/Assignment` (sau chuyển từ worktree Phase 0), branch `feat/central-controller`, base `origin/feat/embedded` tại `65801fbbe2ee6d6022ecadafa3e2a58fee986bc0`.

## Phạm vi đã chuẩn bị

Implemented Phase 0: Serial startup banner (Node ID/version), heartbeat mỗi 1000 ms bằng millis với phép trừ unsigned chịu được wrap, pin constants và cấu hình build. Không chờ Serial vô hạn, không delay dài, không FSM/task riêng. Startup log có thể bị bỏ lỡ nếu monitor chưa mở; mở monitor rồi reset board để xem banner.

Chưa triển khai ST7789, keypad, LVGL, ESP-NOW, kiosk UI hoặc USB Serial JSON Lines nghiệp vụ. Các dòng log hiện tại là debug text, không phải protocol trong [INTERFACES](../../docs/INTERFACES.md). Không khởi tạo/đọc/điều khiển các GPIO ngoại vi, LED onboard hoặc servo. Không thêm lib_deps.

```text
central-controller/
├── platformio.ini
├── .gitignore
├── README.md
├── include/
│   └── pin_config.h
├── src/
│   └── main.cpp
├── kiosk/        # Tài liệu có sẵn, giữ nguyên
└── webserver/    # Tài liệu có sẵn, giữ nguyên
```

## Board definition, flash, PSRAM và USB

| Thiết lập | Lựa chọn Phase 0 |
|---|---|
| PlatformIO Core đã dùng | 6.2.0 |
| Platform | platformio/espressif32@8.0.0 |
| Arduino-ESP32 | 3.3.12, package platformio/framework-arduinoespressif32@4.30312.261024 |
| ESP32-S3 support libraries | platformio/framework-arduinoespressif32-esp32s3-libs@3.3.12 |
| Board base cài sẵn | esp32-s3-devkitc-1, MCU esp32s3, CPU 240 MHz, generic variant esp32s3 |
| Flash profile | Override 4MB, partitions default.csv, app tối đa 1.310.720 byte; DIO 80 MHz |
| PSRAM | Tắt; không định nghĩa BOARD_HAS_PSRAM, không chọn OPI khi chưa xác minh module |
| USB | ARDUINO_USB_MODE=1 (Hardware CDC/JTAG), ARDUINO_USB_CDC_ON_BOOT=1 |
| Serial monitor | 115200; không hardcode upload_port/monitor_port |

Board base mặc định mô tả DevKitC-1-N8 (8MB, không PSRAM), **không phải khẳng định phần cứng Yolo UNO là N8**. Các override flash/partition ở trên thay default 8MB của base. Không có board yolo_uno cài sẵn trong platform đã kiểm; Phase 0 dùng target S3 chung và số GPIO thực. Không dùng board=esp32dev.

Nguồn đã đối chiếu ngày 25/11/2026:

- [OhStem: cài Arduino/Yolo UNO](https://wiki.ohstem.vn/yolo_uno/arduino_yolo_uno/cai_dat) dẫn tới [board package index chính thức](https://raw.githubusercontent.com/AITT-VN/ohstem_arduino_board/main/package_xcon_index.json).
- Đã tải [OhStem Boards 3.1.3](https://github.com/AITT-VN/ohstem_arduino_board/releases/download/v3.1.3/ohstem_esp32-3.1.3.zip) chỉ để đọc boards.txt; kiểm SHA-256 khớp index: `36dd25b33054c173fb7968109651d8725bde7e0407ed18cf9145686ffb38ed7a`. Không cài/đổi framework của hãng vào toolchain.
- boards.txt cho yolo_uno: MCU esp32s3, default flash 4MB, partitions default; có lựa chọn DIO 80MHz, PSRAM disabled/QSPI/OPI và USB Hardware CDC/JTAG + CDC On Boot. Profile Phase 0 chọn 4MB/DIO/PSRAM disabled từ các lựa chọn được hãng hỗ trợ.
- [Trang giới thiệu OhStem](https://docs.ohstem.vn/en/latest/yolo_uno/yolo_uno_khoi_lenh/gioi_thieu_yolo_uno.html) có mô tả flash 16MB và bullet 4MB; [sample PlatformIO do OhStem dẫn tới](https://github.com/AITT-VN/orc_hub_arduino_examples/blob/main/boards/yolo_uno.json) lại chọn 8MB. Vì không có revision/module thực tế, **4MB là profile build bảo thủ được hãng cung cấp, chưa là phép đo dung lượng board**. PSRAM dung lượng/type vẫn chưa xác minh, chưa cần bật cho heartbeat.
- [Sample USB của hãng](https://github.com/AITT-VN/orc_hub_arduino_examples/blob/main/platformio.ini) dùng USB_MODE=1 và CDC_ON_BOOT=1; khớp HWCDC của Arduino-ESP32 đang cài.

Generic variant có default SPI/I2C/LED khác sơ đồ Yolo UNO; không dùng Dn alias, LED_BUILTIN, SPI/Wire mặc định. [PINOUT.md](../../hardware/PINOUT.md) là nguồn pinout duy nhất; include/pin_config.h chỉ chuyển mapping Central thành constants, không gọi pinMode/digitalWrite/SPI.begin. CS mặc định GPIO38; nếu module không có CS, thêm `-DCENTRAL_TFT_CS_GPIO=-1` vào build_flags. Không đổi các giá trị còn lại theo alias.

## Build — không kết nối/nạp board

Từ repository root của worktree Central, nếu pio có trong PATH:

```powershell
pio run --project-dir firmware/central-controller -e central_yolo_uno_s3
```

Máy hiện tại dùng executable đã cài (không nằm PATH):

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe" run --project-dir firmware/central-controller -e central_yolo_uno_s3
```

Build output, log và archive tham chiếu nằm trong .pio bị Git ignore. Source Phase 0 được lưu với commit `feat(central): initialize ESP32-S3 PlatformIO project`; không upload và không sao chép source thử nghiệm ESP32 thường. Kết quả build ban đầu tại worktree Phase 0 25/11/2026: **SUCCESS**, exit code 0, 34,73 giây; không có compiler warning/error trong log. RAM 22.328/327.680 byte (6,8%); chương trình 314.742/1.310.720 byte (24,0%). firmware.bin có kích thước file 320.032 byte (khác số dung lượng chương trình do image header/alignment).

Đã dùng esptool 5.4.0 image-info chỉ đọc file: firmware.bin và bootloader.bin đều đúng ESP32-S3, header 4MB/DIO/80MHz, checksum/hash hợp lệ; ESP-IDF v5.5.5. Log build: `.pio/phase0-build.log`. Các metadata này chỉ xác minh artifact, không đo phần cứng. Không upload/monitor hoặc chạy Phase 1.

## Upload và Serial Monitor — người dùng thực hiện

Xác minh revision/module, flash và đường USB của board trước khi upload. Từ root worktree, thay COMx bằng cổng vừa nhận diện (không sửa/commit COM vào platformio.ini):

```powershell
$pioCentral = "$env:USERPROFILE\.platformio\penv\Scripts\pio.exe"
& $pioCentral device list
& $pioCentral run --project-dir firmware/central-controller -e central_yolo_uno_s3 -t upload --upload-port COMx
& $pioCentral device monitor --project-dir firmware/central-controller -e central_yolo_uno_s3 --port COMx --baud 115200
```

Không thực hiện các lệnh upload/monitor trong lần setup này. Sau mở monitor, reset để xem banner, kiểm Node ID 1, version 2.1.0-phase0 và heartbeat cách khoảng 1000 ms. Build PASS không chứng minh board boot, USB CDC hay timing thực tế đã Verified.

## Giới hạn và công việc sau Phase 0

Chưa kiểm phần cứng: revision/module/flash/PSRAM, USB enumeration/reset và log/timing heartbeat; CS/BLK màn hình, thứ tự cáp keypad, wiring. Sai lệch GPIO45/GPIO48 LED trong tài liệu nguồn chưa giải quyết; Phase 0 không dùng LED. Chưa triển khai các gate protocol/API hoặc Phase 1.

Kiến trúc mục tiêu vẫn Central làm UI/bridge, không trực tiếp điều khiển servo/cấp ngăn/quyết định quyền. [Kiosk UI](kiosk/README.md), [interfaces](../../docs/INTERFACES.md), [Git workflow](../../docs/GIT_WORKFLOW.md). Firmware radio/button esp32dev ở workspace gốc là thử nghiệm riêng, không có trong project mới này.

## Tổ chức mục tiêu — hai project độc lập

C++ Arduino Framework/PlatformIO; cây dưới đây là định hướng, **không tuyên bố các file đã có**:

```text
firmware/
├── common/
│   ├── protocol.h
│   └── device_config.h
├── central-controller/
│   ├── platformio.ini
│   ├── README.md
│   ├── include/
│   │   └── pin_config.h
│   └── src/
│       ├── main.cpp
│       ├── display.cpp
│       ├── keypad.cpp
│       ├── kiosk.cpp
│       ├── espnow.cpp
│       └── serial_comm.cpp
└── locker-node/
    ├── platformio.ini
    ├── README.md
    ├── include/
    │   └── pin_config.h
    └── src/
        ├── main.cpp
        ├── servo.cpp
        ├── door_sensor.cpp
        ├── locker.cpp
        └── espnow.cpp
```

Giữ code đơn giản/modular; tập trung node/locker ID, số ngăn, GPIO và tham số thiết bị trong config phù hợp, không hardcode số ngăn tại nhiều logic. Cho phép bổ sung node/ngăn qua cấu hình về sau, chưa triển khai mở rộng. Không bắt buộc tạo cây này trong lần sửa tài liệu. Member 1 phụ trách Central/Mobile theo [phân công đề xuất](../../docs/ROADMAP.md); common protocol phải thống nhất trước hai người code độc lập. [Git workflow](../../docs/GIT_WORKFLOW.md).

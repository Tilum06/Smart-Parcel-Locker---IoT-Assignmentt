# Central Controller — MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

**Planned:** Yolo UNO ESP32-S3, **Node ID 1**, ST7789 SPI 240×240/LVGL, keypad 4×4, ESP-NOW tới Node 2 và USB Serial tới PC. Không trực tiếp điều khiển servo, cấp ngăn hoặc quyết định quyền nhận hàng. [Pinout chính thức](../../hardware/PINOUT.md), [Kiosk UI](kiosk/README.md), [interfaces](../../docs/INTERFACES.md).

Gửi: thu mã phòng/SĐT/size S-M và confirmation. Nhận: thu PIN 6 số do Mobile App hiển thị, giữ 0 đầu, gửi Backend xác thực. Không hiển thị mã cấp cho App theo thiết kế cũ, không tự mở khi Backend không phản hồi. Hiển thị phản hồi/hướng dẫn/lỗi theo transaction; ACK không đồng nghĩa servo thành công hoặc chốt gài.

## Hiện trạng source

Có test radio/button Test 6A/6B/7 và common helpers; **platformio.ini hiện dùng board=esp32dev, COM cá nhân**. Đây là cấu hình thử nghiệm trước v2.1, chưa phải build Yolo UNO S3/LVGL/keypad/Serial JSON Lines đã tích hợp. Không sửa/xóa test hay cấu hình này trong lần cập nhật tài liệu. Chuyển target S3, pin aliases/USB CDC và bỏ COM khỏi baseline chia sẻ là công việc tiếp theo có review.

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

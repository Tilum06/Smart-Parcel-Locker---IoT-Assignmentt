# Locker Node — MVP v2.1

**Planned:** một Yolo UNO ESP32-S3 **Node ID 2** quản lý đồng thời **L01=S/L02=M**. Mỗi ngăn có MG90S 5V 180° + chốt cơ khí và MC-38 NC. Nguồn servo 5V ngoài, GND chung Node; Node cấp USB riêng. [Pinout duy nhất](../../hardware/PINOUT.md) chứa bảng đấu dây, GPIO và kiểm nguồn/polarity/góc cần thực hiện.

Nhận UNLOCK/LOCK/GET_STATUS qua ESP-NOW từ Central ID 1. ACK chỉ đã nhận; COMMAND_RESULT là kết quả servo; DOOR_EVENT là trạng thái cửa; STATUS là snapshot; ERROR báo lỗi. Kiểm locker/command/transaction/boot/sequence và dedup theo [contract cần chốt](../../docs/INTERFACES.md). LOCK khi OPEN/UNKNOWN phải bị từ chối. Không tự cấp ngăn/xác thực người nhận, không auto AVAILABLE/replay UNLOCK sau reboot. LOCK_APPLIED không chứng minh chốt gài cơ khí; không có latch sensor hoặc cảm biến kiện hàng.

## Source thử nghiệm đang giữ

Có test radio/button và MC-38, cùng chương trình relay/khóa 12V Test 8B/8C. Các tài liệu `TEST8A.md`, `TEST8B.md`, `TEST8C.md` (ở workspace gốc, không nằm trong branch tài liệu này) là hướng dẫn/evidence thử nghiệm trước v2.1, giữ nguyên. platformio.ini đang target esp32-s3-devkitc-1 với COM cá nhân; đó chưa là xác nhận board definition Yolo UNO đúng revision. Firmware servo hai ngăn/controller nghiệp vụ chưa tích hợp; không suy test relay PASS thành MG90S PASS.

## Tổ chức tiếp theo

Project PlatformIO C++ Arduino độc lập với Central. Cây mục tiêu đầy đủ tại [Central README](../central-controller/README.md#tổ-chức-mục-tiêu--hai-project-độc-lập): include/pin_config.h và src/main.cpp, servo.cpp, door_sensor.cpp, locker.cpp, espnow.cpp. Common dự kiến protocol.h/device_config.h; chưa bắt buộc tạo file ngay.

Cấu hình tập trung ID/GPIO/số ngăn/tham số; không rải hardcode locker count trong logic. Giữ modular đơn giản, cho phép mở rộng về sau nhưng chưa triển khai thêm node/ngăn. Member 2 phụ trách Node/CoreIoT/MQTT theo [phân công đề xuất](../../docs/ROADMAP.md). [Git workflow](../../docs/GIT_WORKFLOW.md).

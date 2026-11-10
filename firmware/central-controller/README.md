# Central Controller — baseline revision 1.3

Owner **Member A**, ESP32 #3. Đã chọn PlatformIO/C/C++/Arduino; một project chứa ESP-NOW, USB Serial, ST7789/LVGL, keypad 4×4, webserver và OTA. `kiosk/`/`webserver/` là module cùng firmware, chưa có code/build config.

Central relay tới #1 L01/L02 hoặc #2 L03/L04, không phân bổ ngăn/DB đơn. USB Serial JSON Lines LF đã duyệt; 115200 và giới hạn thử 2048 byte/line/timeout cần đo. Không debug text trên protocol, không thêm sensor vào ACK. STATUS giữ source/target, boot/sequence/epoch và request correlation; mã phiên display không log công khai.

FW-03 form phòng số/SĐT/size và mã nhận kiosk; FW-04 local HTTP qua Backend service kiểm quyền; FW-05 ưu tiên thử OTA Central. D-10 scope cuối còn mở/T14 cần đối chiếu giảng viên, có thể mở rộng node. Có thể spike riêng display/radio/OTA ở M1 nếu board/toolchain sẵn, không chặn HW-01/BE-01 design.

Board/revision/profile/GPIO/lib version/flash/partition chưa khóa. TC-33 phải thử cùng build kiosk+ESP-NOW+Serial+webserver+OTA và pending transaction/reboot, không giả định coexistence/memory đủ. Đọc [INTERFACES](../../docs/INTERFACES.md), [DECISIONS](../../docs/DECISIONS.md), [TEST_PLAN](../../docs/TEST_PLAN.md). Policy mất Backend khi cửa mở vẫn D-08, không tự tạo offline actuator workflow.

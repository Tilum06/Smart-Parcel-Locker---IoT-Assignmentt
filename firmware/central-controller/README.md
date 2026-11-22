# Central/Kiosk — ESP32-S3 #1, v2.0

Central giờ là **Yolo UNO ESP32-S3**, không phải ESP32 thứ ba hoặc ESP32 thường. Một firmware PlatformIO/C++ Arduino gồm ESP-NOW, USB Serial JSON Lines tới PC, ST7789 240×240 SPI/LVGL và keypad 4×4. Một Locker Node #2 nhận lệnh cho L01/L02.

Central không tự cấp ngăn hoặc quyết định chủ đơn. Nó nhận input shipper (mã phòng/số điện thoại/size S-M), gửi Backend qua Serial, hiển thị mã phiên nhận hàng TTL 30s và định tuyến command/status. Pinout Central cần chốt riêng cho màn hình SPI/keypad. Webserver local và OTA chưa là mục tiêu MVP, chỉ giữ trong backlog mở rộng.

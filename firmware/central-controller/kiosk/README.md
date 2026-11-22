# Kiosk ST7789/LVGL/Keypad — v2.0

Chạy trên **Central ESP32-S3 #1**, ST7789 SPI 240×240 + keypad 4×4. Shipper nhập **mã phòng số, SĐT, size S hoặc M**, xác nhận; Backend cấp L01(S)/L02(M) theo best-fit. Kiosk hiển thị trạng thái hướng dẫn đặt/nhận hàng, tạo phiên nhận trên Backend và hiện **mã 30 giây** để người nhận nhập trên Web App.

Không lưu/trưng bày dữ liệu cá nhân vượt cần thiết; không xem khóa đã thực sự gài chỉ vì servo trả ACK. Form hiển thị fallback S→M nếu L01 bận. Board/lib/chân SPI/keypad cần xác minh.

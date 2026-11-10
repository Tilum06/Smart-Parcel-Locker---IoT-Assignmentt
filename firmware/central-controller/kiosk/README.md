# Kiosk LVGL/keypad — revision 1.3

Owner **Member A**, FW-03. ST7789 SPI 240×240 + LVGL/keypad 4×4 trong Central; chưa có UI chạy được. Room code chỉ chữ số, SĐT chuỗi, chọn S/M/L; nhập/sửa/xem lại rồi Backend đối chiếu cư dân admin tạo trước. Không tự tạo account, không xác thực shipper, không log SĐT.

Hiển thị ngăn/nâng size và hướng dẫn đặt; ghi confirmation độc lập với DOOR_EVENT, chấp nhận confirm trước hoặc sau đóng cửa. Backend chỉ phát LOCK khi có door cycle đúng phiên và cửa CLOSED; completion còn cần STATUS/latch ENGAGED mới, không báo xong từ ACK.

Nhận hàng: chọn phiên kiosk, Backend cấp mã ngắn hạn qua kênh kiosk đã auth, hiển thị trên ST7789; người nhận nhập vào Web App. Bind kiosk/pickup session, one-use/TTL/attempt policy còn P-03/D-06 cần duyệt; không log hoặc gửi code lên CoreIOT. Mã có thể chia sẻ từ xa, không chứng minh vị trí tuyệt đối, không SMS OTP.

D-01 bảng kích thước thật còn mở, số cm mẫu không phải chính thức; D-09/P-02 GPIO/display lib version còn gate. UI có thể prototype M1 bằng fixture, integration M2. Đọc [INTERFACES](../../../docs/INTERFACES.md), [TEST_PLAN](../../../docs/TEST_PLAN.md): TC-01/04/05/16C/19/31/32/33; chưa có kết quả PASS chức năng.

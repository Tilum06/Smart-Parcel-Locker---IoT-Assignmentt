# Kiosk ST7789 / LVGL / Keypad — MVP v2.1

**Planned**, chạy trên Central Yolo UNO ESP32-S3 Node 1. ST7789 SPI 240×240 và keypad ma trận 4×4. [Pinout duy nhất](../../../hardware/PINOUT.md); thứ tự dây keypad, CS/BLK màn hình và library version chưa Verified trên phần cứng.

Gửi: chọn gửi → mã phòng → SĐT người nhận → size S/M → chuyển Backend → hiển thị ngăn được cấp/hướng dẫn → đặt hàng/đóng cửa/xác nhận. Backend best-fit S→L01 hoặc L02, M→L02; Central chỉ hiển thị kết quả, không tự cấp ngăn.

Nhận v2.1: người nhận login App, chọn kiện và xem PIN 6 chữ số/30 giây do Backend cấp → nhập PIN tại keypad → Central gửi USB Serial tới Backend → Backend kiểm quyền/kiện/hạn/kiosk scope, tiêu thụ một lần và gửi UNLOCK → hiển thị hướng dẫn lấy hàng, đóng cửa, xác nhận. Giữ số 0 đầu; hỗ trợ sửa/hủy theo UI sẽ chốt. Không log PIN/PII, không tự mở nếu Backend mất phản hồi; không TOTP offline.

Kiosk không còn hiển thị mã để người dùng nhập lên App theo thiết kế mục tiêu. **Phase 1/simulator vẫn dùng flow mã kiosk cũ**, chưa có API PIN/keypad mới. Xác nhận nhận hàng từ kiosk cần contract/authorization mới; hiện endpoint confirm pickup thuộc resident. [Interfaces](../../../docs/INTERFACES.md).

ACK, kết quả servo và MC-38 là các dữ liệu khác nhau. Không thông báo chốt cơ khí đã gài chỉ từ LOCK_APPLIED; không có cảm biến chốt/kiện hàng. Firmware kiosk tích hợp chưa có evidence PASS.

# Web App cư dân/admin — revision 1.3

Owner **Member B**, WEB-01. Client của API trong app PC FastAPI duy nhất, khác LVGL kiosk và webserver ESP32. Chưa chọn frontend framework/chưa có app chạy được.

Cư dân admin tạo trước đăng nhập, xem đơn/thông báo của mình, đến kiosk lấy mã phiên trên ST7789, nhập mã khi yêu cầu pickup. Backend kiểm owner/state/kiosk-session/TTL/attempts và atomic one-use; client không tự khai quyền bằng user_id/phòng. Phòng chỉ chữ số/SĐT không là password mặc định. Session/password/code details còn P-03, policy mã kiosk đã duyệt D-05.

Xác nhận lấy trước hoặc sau đóng cửa đều được; phải có door cycle đúng phiên, LOCK, door CLOSED và latch ENGAGED mới Backend hoàn tất. UI thể hiện pending/error/known sensor, không báo đã mở từ 202/ACK hoặc NOT_ENGAGED. Mã có thể chia sẻ từ xa, không chứng minh vị trí tuyệt đối và không SMS OTP; không log mã/phone/password.

Admin maintenance không xóa active transaction, ra bảo trì cần reconcile. UI fixture có thể dựng trước full dependencies; nghiệm thu theo BE-02/BE-03/INT-01. [TEST_PLAN](../docs/TEST_PLAN.md) TC-08…11/15/24/31/32; [INTERFACES](../docs/INTERFACES.md) API/code error, chưa có PASS chức năng.

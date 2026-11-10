# ESP32 local webserver — revision 1.3

Owner **Member A**, FW-04/T07. Module HTTP chạy trên Central, khác Web App người nhận/HTTP FastAPI trên PC. Chưa có server thực thi. Một firmware chứa kiosk/radio/Serial/webserver/OTA, không tạo project riêng cho cùng ESP32.

Giám sát và yêu cầu local có quyền: Central chuyển qua Serial tới Backend service trong app PC để kiểm actor/state trước command. Không endpoint mở servo bypass service; ACK không chứng minh latch ENGAGED. Cơ chế auth/provisioning P-03 và policy mất Backend D-08 vẫn mở, không tự thêm offline-open/LOCK khi cửa mở.

Nghiệm thu TC-16A/27/33 trên board thật: local auth/điều khiển, từ chối trái quyền, đồng thời kiosk+radio+Serial+webserver+OTA. Dùng [INTERFACES](../../../docs/INTERFACES.md) và [TEST_PLAN](../../../docs/TEST_PLAN.md); không lưu credential source, không tính T07 từ tài liệu.

# CoreIOT — baseline revision 1.3

Owner **Member B**, IOT-01/IOT-02; tenant/device access chưa kiểm chứng. CoreIOT MQTT adapter/worker thuộc cùng app Python/FastAPI với Backend và Serial, không server/broker nội bộ riêng.

T08 hai chiều, T11 template/dashboard giám sát/điều khiển, T12 RuleChain, T13 notification sự cố. RPC tới worker phải qua Backend service kiểm role/state và lưu intent rồi mới device command, không trực tiếp mở actuator hoặc mutate đơn. Gateway không tự phân ngăn/hoàn tất.

Telemetry door_state/latch_feedback/servo command, availability/online/errors/count/version; không lock_state suy từ servo, không SĐT/phòng/pickup_code/token. STATUS là evidence riêng, ACK không sensor. Topic/RPC/provisioning/role P-03, ngưỡng/freshness D-06/P-05 còn mở; chỉ lưu export sạch khi đã có tenant.

Thông báo sự cố CoreIOT khác notification đơn Web App; cả hai vẫn trong MVP dù không SMS OTP. TC-12/17A/17B/29/35 cần log/ảnh/video thật, kế hoạch không phải điểm đạt. Đọc [INTERFACES](../docs/INTERFACES.md)/[TEST_PLAN](../docs/TEST_PLAN.md). DOC-01 cần self-assessment với trạng thái thực, không thêm TinyML/T10/T15.

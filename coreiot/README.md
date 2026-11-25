# CoreIoT — MVP v2.1

**Planned:** giám sát, telemetry, thống kê và cảnh báo cho Central ID 1, Locker Node ID 2 và L01=S/L02=M qua MQTT Gateway PC trong cùng ứng dụng Python với Backend. Hai ESP32 không bắt buộc trực tiếp Internet. CoreIoT không là nguồn sự thật đơn hàng hoặc đường mở khóa bỏ qua Backend.

Schema cần chốt từ phase 0: node/locker identity, door_state, servo_action, trạng thái nghiệp vụ, online/fault, version và thời gian/counter phù hợp. Không latch_feedback/ENGAGED giả hoặc chỉ số hiện diện kiện; MC-38 chỉ đo cửa, servo result không chứng minh gài chốt. Không gửi SĐT, mã phòng, PIN, password/token/verifier.

Có helper **Implemented** tại tests/coreiot/test5_telemetry.py, gửi dữ liệu giả bằng MQTT; chưa có Dashboard/Gateway production hoặc evidence live v2.1. MQTT ACK chỉ chứng minh broker nhận message theo helper, không chứng minh Dashboard/thiết bị thật. Giữ báo cáo cũ theo ngày/cấu hình, không tự đánh dấu Verified.

Member 2 phụ trách theo [đề xuất](../docs/ROADMAP.md). Chốt telemetry schema → MQTT giả lập → Dashboard → Gateway → cảnh báo/thống kê → mapping thật → E2E; triển khai song song, không đợi Embedded hoàn tất. [Interfaces](../docs/INTERFACES.md), [test plan](../docs/TEST_PLAN.md).

## REST API Phase 1 đã triển khai

Contract hiện hành và ví dụ tại [BACKEND_PHASE1](BACKEND_PHASE1.md); OpenAPI `/openapi.json`, Swagger `/docs`. Prefix `/api/v1`: auth login/logout; rooms/residents; lockers; deposits + confirm; kiosk-sessions; pickups + confirm; parcels + history; transactions. Bearer + role/ownership; mutation nghiệp vụ dùng X-Request-ID. Mã kiosk one-use 30s gắn parcel/resident/kiosk/session. Chỉ L01=S/L02=M, 2 ESP32-S3, servo 5V + MC-38, không latch sensor. Door snapshot mới hợp lệ và OPEN→CLOSED đúng phiên kết hợp confirmation + LOCK_APPLIED đúng command mới hoàn tất khi không lỗi/offline/unknown; kết quả servo không chứng minh chốt cơ khí. Giao thức firmware chưa tích hợp; không có endpoint HTTP nhận sensor giả. Contract Phase 1 này ưu tiên hơn baseline bên dưới.

---

# Hợp đồng giao tiếp dự kiến — v2.0

**DRAFT**: Logic được thống nhất, schema byte/JSON và timeout chưa kiểm nghiệm đầy đủ. Có 2 node: **Central ID=1, Locker Node ID=2**, cả L01 và L02 thuộc Node 2.

| Chặng | Transport | Chức năng |
|---|---|---|
| PC ↔ Central | USB Serial UTF-8 JSON Lines/LF, baud thử 115200 | Request, command, response, event |
| Central ↔ Locker Node | ESP-NOW | UNLOCK/LOCK/GET_STATUS; ACK, RESULT, DOOR_EVENT, STATUS |
| Web App ↔ Backend | HTTP có session | Login, đơn, mã phiên, xác nhận |
| Gateway ↔ CoreIOT | MQTT | Telemetry/notification/RPC có kiểm quyền |

**Các field chung:** request_id, transaction_id, source_node_id, target_node_id, locker_id (L01/L02), boot_id, sequence và freshness/deadline cần hoàn thiện. ACK chỉ chứng minh đã nhận/xử lý message; COMMAND_RESULT mô tả lệnh servo; DOOR_EVENT/STATUS mô tả MC-38.

**Trạng thái:** door_state = OPEN/CLOSED/UNKNOWN; servo_action = IDLE/UNLOCK_APPLIED/LOCK_APPLIED/ERROR/UNKNOWN. **Không có latch_feedback** trong MVP; không phát trường ENGAGED giả từ góc servo. Business status (AVAILABLE/RESERVED/OCCUPIED/UNKNOWN/MAINTENANCE) nằm ở Backend.

**API sơ bộ:** POST /deposits, POST /deposits/{id}/confirm, GET /me/parcels, POST /pickups/session, POST /pickups/verify, POST /pickups/{id}/confirm, GET /lockers. Backend xác minh chủ đơn, mã phiên **TTL 30 giây**, one-use, giới hạn thử và ràng buộc order/user/kiosk/session.

**Điều kiện:** lệnh UNLOCK phải được lưu intent trước gửi; LOCK chỉ khi cửa CLOSED còn mới. Door OPEN→CLOSED và xác nhận thủ công đều cần cho hoàn tất nghiệp vụ; lỗi/reboot/offline không auto AVAILABLE. Không log PII, code, mật khẩu/token. Tham số giao thức final sau khi thử trên hai ESP32-S3.

# Backend module — Python/FastAPI/SQLite revision 1.3

Owner **Member B**, BE-01→BE-02→BE-03. Một app PC chứa cả Backend và Gateway, một FastAPI HTTP server; chưa có API/schema/migration/code chạy được. Không tạo microservices, broker nội bộ hoặc server Gateway riêng.

Backend sở hữu API/auth, business services, persistence SQLite: Best Fit, atomic reservation, identity/ownership, transactions, intent/result/idempotency, audit và Web App notifications. Service gọi transport adapter sau commit intent; workers Serial/MQTT chỉ đẩy event/connection/result qua ingress, không ghi domain. Không giữ transaction SQLite chờ radio.

Admin tạo trước cư dân gắn room_code **chuỗi chỉ chữ số**, recipient_phone chuỗi, credentials riêng; không auto-create từ shipper, không mặc định password bằng phòng/SĐT. BE-01/02 phải thiết kế length/normalization/uniqueness, password hashing/reset/session/provisioning và bảo vệ dữ liệu trước hiện thực (P-03), không tạo credential thật ở M0.

Kiosk cấp mã phiên nhận ngắn hạn, resident auth nhập mã khi pickup. Service kiểm ownership/state, kiosk/session, TTL/attempts rồi atomic bind/consume code với owner+parcel+transaction và tạo UNLOCK intent. Code một lần dùng, duplicate request đúng trả kết quả cũ, không dùng lại mở lần khác; không log code, không SMS OTP; có thể chia sẻ từ xa. Tham số/format/digest/session còn review P-03/D-06.

Schema design cần thể hiện L01/L02=S/L03=M/L04=L, fresh sensor state độc lập online, account association, active transaction/reservation, command intent/epoch/deadline/result, confirmations/door cycle, notification/audit, kiosk pickup session one-use. Chưa chốt số bảng. Fixture M1 dùng dữ liệu giả, Best Fit category không cần cm thật. Tie-break ID nhỏ nhất còn P-04 review.

M2 BE-01/02 cùng FW-02/GW-01 xử lý tối thiểu lost ACK/disconnect/boot/expired command trước INT-01. Completion chỉ có user confirmation + door cycle đúng phiên + LOCK result/door CLOSED/latch ENGAGED mới; NOT_ENGAGED không chứng minh mở hoàn toàn. Không tự AVAILABLE hoặc suy từ DB cũ; BE-03 M4 mở rộng recovery/admin, D-08 mất Backend khi cửa mở vẫn cần policy.

Đọc [PROJECT_SPEC](../docs/PROJECT_SPEC.md), [INTERFACES](../docs/INTERFACES.md), [TEST_PLAN](../docs/TEST_PLAN.md). Python/runtime/package versions và Web App framework chưa khóa; chưa có lệnh chạy/migrate/test được xác minh.

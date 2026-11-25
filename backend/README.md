# Backend — FastAPI + SQLite, mục tiêu MVP v2.1

**Implemented Phase 1:** auth/role/ownership, cư dân/phòng, SQLite migration/seed, allocation atomic L01=S/L02=M, durable command intent, idempotency, state/evidence và tests. Setup Windows, API thật, giới hạn và kết quả kiểm chứng có ngày tại [BACKEND_PHASE1](../docs/BACKEND_PHASE1.md). Simulator cục bộ: [hướng dẫn riêng](demo/README.md).

Backend chịu trách nhiệm nghiệp vụ, authentication, authorization, cấp ngăn, lưu dữ liệu và giao dịch. Best-fit S ưu tiên L01, có thể L02; M chỉ L02; không cấp ngăn offline/lỗi/đang dùng/unknown. Backend/Gateway là module trong cùng ứng dụng Python, không đổi kiến trúc hiện có.

**Planned v2.1:** Resident Mobile App yêu cầu PIN 6 chữ số/30 giây, giữ 0 đầu; keypad kiosk nhận PIN và chuyển Backend. Backend kiểm owner/parcel/expiry/kiosk scope, chống collision phiên active, giới hạn sai/rate limit, tiêu thụ atomic với tạo PICKUP/UNLOCK intent. Không plaintext lâu dài/log, không mở khi Backend mất phản hồi, không TOTP offline. API/confirm kiosk/verifier và migration cần thiết kế tiếp theo, chưa có source.

Phase 1 hiện vẫn dùng **kiosk tạo opaque code → resident gửi code qua API**. Không thể chỉ đổi UI rồi gọi đó là PIN v2.1; [so sánh contract](../docs/INTERFACES.md). Production seed offline; chưa có Serial/MQTT/ESP-NOW adapter thật.

Hoàn tất cần confirmation + OPEN→CLOSED đúng phiên + CLOSED mới (Phase 1: 10 giây) + LOCK_APPLIED đúng command, không lỗi/offline/unknown. Không latch sensor; LOCK_APPLIED chỉ kết quả điều khiển servo, không chứng minh chốt gài. Không HTTP sensor evidence giả trong production; giữ reservation khi lỗi/restart. [Kiến trúc](../docs/ARCHITECTURE.md).

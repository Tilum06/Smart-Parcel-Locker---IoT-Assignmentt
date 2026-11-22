## Phase 1: source và cách chạy

Backend đã có SQLite migration/seed, auth, API, service allocation, state/evidence và pytest. Xem [BACKEND_PHASE1](../docs/BACKEND_PHASE1.md) để setup Windows, tạo tài khoản/demo, chạy server, Swagger, pytest và contract đầy đủ. Chỉ L01=S/L02=M trên Locker Node 2, Central 1; 2 ESP32-S3. Không có cảm biến chốt. Confirmation + OPEN→CLOSED + CLOSED mới + LOCK_APPLIED đúng command, không lỗi/offline/unknown mới hoàn tất; kết quả servo không chứng minh chốt gài cơ khí. Production mặc định offline, không có API sinh bằng chứng giả. Phần này ưu tiên hơn các cấu hình baseline cũ bên dưới.

---

# Backend — FastAPI + SQLite, v2.0

Backend quản lý cư dân/admin, room_code dạng chuỗi số, số điện thoại, login, giao dịch, reservation và audit. Mapping chỉ có **L01=S, L02=M**, best-fit **S→S/M, M→M**. Không có size L trong MVP. SQLite là nguồn sự thật nghiệp vụ; Gateway Serial/MQTT là module trong cùng Python app, không server độc lập.

UNLOCK intent phải persist trước khi gửi; ACK khác kết quả servo/door cycle. Đơn STORED/COMPLETED yêu cầu confirmation và sự kiện cửa đúng phiên, LOCK khi cửa đã CLOSED và kết quả không lỗi. Không có latch microswitch nên không được báo đã xác minh chốt vật lý. Web App nhận hàng qua login + đúng chủ + mã kiosk 30s, one-use, giới hạn thử, không log secrets/PII.

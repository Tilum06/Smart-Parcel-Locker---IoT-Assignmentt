# ESP32 local webserver — backlog mở rộng v2.0

Webserver trực tiếp trên Central ESP32-S3 (mục T07) **không phải blocker của MVP 2 ngăn**. Khi triển khai, mọi thao tác yêu cầu mở ngăn phải qua Backend FastAPI để kiểm auth/state, không tạo endpoint truy cập servo trực tiếp. Chưa có implement/test/evidence để nhận điểm T07.

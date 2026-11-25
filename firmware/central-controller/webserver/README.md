# ESP32 local webserver — Backlog ngoài MVP v2.1

Webserver trực tiếp trên Central chưa triển khai và không chặn MVP hai ngăn. Resident Mobile App dùng REST API trên PC theo [kiến trúc v2.1](../../../docs/ARCHITECTURE.md); đây là thành phần khác webserver trên ESP32.

Nếu mở rộng sau này, yêu cầu mở ngăn vẫn phải qua Backend authentication/authorization và state guards. Không tạo đường gọi servo bỏ qua Backend. Chưa có evidence nghiệm thu webserver thiết bị; không dùng simulator PC thay cho minh chứng này.

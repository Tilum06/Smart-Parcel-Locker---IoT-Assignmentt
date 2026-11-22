# Gateway PC — v2.0

Module Gateway chạy **trong cùng ứng dụng Python FastAPI + SQLite**, không là server HTTP thứ hai. USB Serial UTF-8 JSON Lines (baud 115200 thử nghiệm) tới **Central ESP32-S3 #1**; Central chuyển ESP-NOW tới **Locker Node #2** điều khiển L01/L02. Gateway route/correlate command, ACK, COMMAND_RESULT, DOOR_EVENT và STATUS; không trực tiếp phân bổ ngăn/chuyển trạng thái nghiệp vụ. MQTT adapter đẩy trạng thái được phép công bố lên CoreIOT, nhận RPC qua Backend auth/service. Không log SĐT, mã phòng, mã nhận, password/token.

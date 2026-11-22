# CoreIOT — v2.0

Theo dõi **một Central S3 + một Locker Node S3** và hai ngăn **L01=S/L02=M** qua Gateway PC/MQTT. Telemetry: door_state, servo_action, availability nghiệp vụ, online/fault/version/event count. **Không có latch_feedback** hay cảm biến hiện diện kiện; không dựng chỉ số khẳng định chốt vật lý ENGAGED. Dashboard/notification dùng để giám sát, không làm nguồn DB đơn hoặc bỏ qua Backend auth. Không gửi SĐT, room_code, pickup_code, token/credential.

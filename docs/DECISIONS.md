## Quyết định Phase 1 bổ sung (hiện hành)

- 2 ESP32-S3: Central 1, Locker Node 2; chỉ L01=S và L02=M, servo 5V + MC-38; không latch sensor/microswitch, không size L.
- SQLite stdlib + FastAPI/Pydantic; migration user_version=1, FK bật, partial unique active transaction, BEGIN IMMEDIATE.
- Best-fit S→S/M, M→M; cùng size ưu tiên ID tăng dần (tạm thời).
- Hoàn tất nghiệp vụ: confirmation + OPEN→CLOSED đúng transaction + CLOSED mới hợp lệ + LOCK_APPLIED đúng command, không lỗi/offline/unknown; không cần ENGAGED. LOCK_APPLIED không chứng minh chốt gài cơ khí.
- Seed offline; không tự online, tự giải phóng khi timeout/restart hay sinh sensor giả trong production.
- [Contract và giới hạn Phase 1](BACKEND_PHASE1.md) ưu tiên hơn cấu hình baseline cũ; giữ nguyên tài liệu lịch sử v1.2.

---

# Quyết định — v2.0 (23/11/2026)

| Mã | Đã chốt | Thay thế |
|---|---|---|
| C-01 | 2 **Yolo UNO ESP32-S3**: Central + Locker Node | 3 ESP32 / 2 locker node |
| C-02 | 2 ngăn: **L01 S, L02 M** | 2S + 1M + 1L |
| C-03 | 2 servo **MG90S 5V** + chốt cơ khí + 2 cảm biến **MC-38 NC** | Khóa 12V/relay, 4 servo và microswitch chốt |
| C-04 | MC-38 chỉ đo cửa; không cảm biến hàng/chốt trong MVP | Latch ENGAGED được đo trực tiếp |
| C-05 | FastAPI + SQLite + Gateway Serial/MQTT cùng một ứng dụng | Không đổi |
| C-06 | Central/Node qua ESP-NOW; Central/PC qua USB Serial | Mapping 3 node cũ |
| C-07 | Kiosk ST7789/LVGL/keypad trên Central | Không đổi |
| C-08 | Admin tạo cư dân trước; login + quyền sở hữu + mã nhận 30s tại kiosk | Không đổi, TTL nay chốt chính sách |
| C-09 | Best-fit S→S/M, M→M | S→S/M/L, M→M/L, L→L |

**Còn mở:** kiểm board revision/pinout; góc servo/chốt; kích thước S/M; dòng nguồn 5V khi tải; debounce MC-38; version framework/LVGL; timeout, retry, trạng thái lỗi và mã phiên; CoreIOT mapping. Không tuyên bố servo đã khóa cơ khí chỉ từ ACK/góc quay.

**Mở rộng để sau:** 4 ngăn, cảm biến chốt, buzzer, OTA, APK và webserver trên thiết bị. File PROJECT_SPEC_Smart_Parcel_Locker_v1.2.md tại root là lịch sử, không chỉnh sửa.

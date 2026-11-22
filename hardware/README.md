# Hardware — v2.0 (2 servo lockers)

| Linh kiện | SL | Ghi chú |
|---|---:|---|
| Yolo UNO ESP32-S3 | 2 | Central + Locker Node |
| ST7789 SPI 240×240 | 1 | Kiosk |
| Keypad 4×4 | 1 | Kiosk |
| Servo MG90S 5V 180° | 2 | Mỗi ngăn một servo + chốt/gá |
| MC-38 NC | 2 | Đọc trạng thái cửa |
| Nguồn DC 5V–2A | 1 | Đã có, phải đo dòng đỉnh/tải; nâng nếu không đủ |
| Dây, đầu nối, cáp USB | Theo nhu cầu | Tránh kéo dòng servo trên breadboard/USB board |
| Khóa điện 12V, relay, diode flyback, microswitch chốt | 0 trong MVP | Giữ làm vật tư dự phòng nếu đã mua |

## Pinout gợi ý Locker Node (chưa chốt sau test)

| Thiết bị | Chân Yolo UNO | GPIO |
|---|---|---|
| Servo L01 signal | D4 | GPIO7 |
| Servo L02 signal | D6 | GPIO9 |
| MC-38 L01 | A3 + GND | GPIO4 |
| MC-38 L02 | A0 + GND | GPIO1 |

Dây **đỏ** của mỗi servo → nguồn +5V ngoài; dây **nâu/đen** → GND nguồn ngoài; dây **cam/vàng** → GPIO signal. **GND nguồn ngoài phải nối chung với GND ESP32-S3.** Cảm biến MC-38 NC nối giữa GPIO và GND, firmware INPUT_PULLUP + debounce. Không đưa +12V vào servo 5V, không cấp servo từ GPIO/3V3 hay mặc định chân 5V USB board đủ dòng.

**Cơ khí:** servo không tự khóa nếu thiếu tay gạt/chốt; chốt phải giữ được cửa nhẹ, không đặt lực giữ lớn lên bánh răng servo. MC-38 CLOSED không chứng minh chốt gài. Cần đo góc servo thật, không mặc định 0° và 90°.

**Checklist:** test 1 servo không tải → 1 chốt → 1 cửa và MC-38 → nhân sang 2 ngăn; đo 5V khi motor chạy/kẹt, bảo vệ nguồn, kiểm reset, dán nhãn dây và quay video. Central cần bảng pin riêng cho SPI/keypad trước khi lắp.

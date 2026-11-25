# Hardware — MVP v2.1

Thiết kế mục tiêu: hai Yolo UNO ESP32-S3, Central ID 1 và Locker Node ID 2; Node quản lý L01=S/L02=M. **Nguồn pinout duy nhất:** [PINOUT.md](PINOUT.md), gồm ST7789, keypad, servo/cửa, GPIO reserved và sơ đồ nguồn. Mapping đã đối chiếu OhStem, chưa Verified trên board thực.

| Linh kiện | Số lượng | Ghi chú |
|---|---:|---|
| Yolo UNO ESP32-S3 | 2 | Central + Locker Node |
| ST7789 SPI 240×240 | 1 | LVGL trên Central |
| Keypad ma trận 4×4 | 1 | Thụ động, xác minh thứ tự R/C |
| MG90S 5V 180° | 2 | Mỗi ngăn một servo + chốt cơ khí |
| MC-38 NC | 2 | Cảm biến cửa, không phải cảm biến chốt/kiện |
| Adapter 5V–2A hiện có | 1 | Phải đo hai servo có tải, không mặc định đủ dòng |
| Cáp USB, dây, đầu nối, gá/chốt | Theo lắp ráp | Central USB laptop; Node USB riêng; servo nguồn ngoài |

Không dùng khóa điện 12V, relay, cảm biến hiện diện kiện, microswitch chốt, size L hoặc board thứ ba. Vật tư/test cũ giữ làm tham khảo, không phải evidence MVP servo.

GND nguồn servo nối GND Node; không cấp servo từ GPIO/3.3V. Hai ESP32 không cần nối GND với nhau vì ESP-NOW. Góc/pulse, cơ cấu chốt, polarity/debounce MC-38, CS/BLK màn hình và revision LED onboard còn cần xác minh. Không suy chốt gài từ LOCK_APPLIED. [Test plan](../docs/TEST_PLAN.md).

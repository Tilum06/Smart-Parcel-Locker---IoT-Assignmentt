# Backlog — MVP v2.0

| ID | Owner | Công việc |
|---|---|---|
| DEC-01 | Both | Thống nhất pinout, cơ khí, nguồn, contract và recovery |
| HW-01 | A | Prototype **1 MG90S + 1 MC-38 + chốt**; đo nguồn/góc và guard cửa |
| FW-01 | A | Locker Node S3 duy nhất, 2 servo + 2 MC-38, STATUS/ERROR |
| FW-02 | A | ESP-NOW Central S3 ↔ Locker Node S3, dedup/request ID |
| FW-03 | A | Kiosk Central ST7789/LVGL + keypad 4×4, USB Serial |
| BE-01 | B | SQLite + Best Fit L01=S/L02=M và reservation atomic |
| BE-02 | B | FastAPI, tài khoản cư dân, owner auth, giao dịch và code 30s |
| GW-01 | B | Gateway Serial/MQTT cùng ứng dụng PC |
| INT-01 | Both | End-to-end **một ngăn** |
| WEB-01 | B | Web App cư dân/admin tối thiểu |
| INT-02 | Both | End-to-end **hai ngăn**, best-fit S→M, tình huống lỗi |
| IOT-01 | B | CoreIOT telemetry/dashboard/notification |
| QA-01 | Both | HIL/khôi phục/đo đạc/evidence |
| DOC-01 | Both | Báo cáo/video/README, phân công và minh chứng |

**Backlog mở rộng (không chặn MVP):** FW-04 webserver local ESP32; FW-05 OTA; HW-02 microswitch chốt; HW-03 mở rộng 4 ngăn/size L; APP-01 APK; UX-01 buzzer.

**Phụ thuộc chính:** HW-01 → FW-01 → INT-01; BE-01/BE-02/GW-01/FW-02/FW-03 → INT-01; INT-01 → INT-02 → QA-01. Không tự đánh dấu DONE khi mới có tài liệu.

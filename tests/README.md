# Kiểm thử — MVP v2.1

> **Phạm vi branch:** feat/embedded kế thừa origin/feat/demo-simulator tại fa1c26b. Các nhận xét về Expo starter và firmware test bên dưới được quan sát ở workspace gốc feat/resident-mobile-app (firmware test còn untracked); các source đó không được đưa vào branch tài liệu này.

[Test plan](../docs/TEST_PLAN.md) là kế hoạch hiện hành: hai Yolo UNO ESP32-S3, L01=S/L02=M, hai MG90S và hai MC-38. Implemented = có source; Planned/NOT RUN = chưa kiểm; Verified/PASS chỉ khi có evidence đúng cấu hình. Không dùng test relay/12V cũ làm PASS servo hoặc host/mock làm HIL.

## Bộ kiểm thử hiện có

- backend/tests: Phase 1 và simulator; `python -m pytest -q` tại root sau cài backend/requirements.txt. Kiểm atomic best-fit, auth/ownership, mã opaque từ kiosk/TTL/one-use, lifecycle/evidence/restart. Chưa kiểm API PIN 6 số v2.1 vì API chưa có.
- firmware/locker-node/test và firmware/common: host/test helpers cho các chương trình thử nghiệm; giữ nguyên source cùng hướng dẫn TEST8A/B/C. Chưa nghiệm thu firmware servo/kiosk v2.1.
- coreiot/test5_telemetry.py: smoke MQTT dữ liệu giả thủ công; không nằm trong pytest.ini, không tự chứng minh Dashboard hoặc thiết bị thật.

Kết quả có ngày giữ tại [Phase 1](../docs/BACKEND_PHASE1.md), [simulator](../backend/demo/README.md), [Git sync review lịch sử](../docs/GIT_SYNC_REVIEW_2026-11-23.md); không cập nhật kết quả cũ thành kết quả lần này.

## Kiểm thử tiếp theo

Phase 0 pinout/protocol/schema; phase 1–3 ST7789/keypad/servo/MC-38 và API PIN mới; phase 4–8 radio/Serial/Gateway/reconcile; phase 9 gửi/nhận hai ngăn, best-fit, PIN owner/scope/TTL/collision/concurrency/rate limit, lỗi/offline/reboot và CoreIoT dữ liệu thật. [Roadmap](../docs/ROADMAP.md).

Evidence gồm wiring/revision, cấu hình nguồn, phép đo tải/góc/polarity/debounce, log correlation đã che secrets, ảnh/video. MC-38 chỉ đo cửa, không chứng minh chốt gài hoặc kiện hàng hiện diện. Pinout chỉ tại [PINOUT](../hardware/PINOUT.md).

# Test plan — MVP v2.1

Kế hoạch kiểm thử, **chưa có PASS v2.1** từ lần cập nhật tài liệu. Implemented = có source; Planned/NOT RUN = chưa kiểm; Verified/PASS chỉ dùng khi có log/ảnh/video/phép đo với đúng cấu hình. Test relay/khóa 12V cũ không chứng minh servo; simulator/host test không phải HIL.

## Kiểm tra phần cứng

| Test | Nội dung | Điều kiện đạt |
|---|---|---|
| HW-00 | Hai Yolo UNO S3 đúng revision, đối chiếu nhãn/GPIO theo PINOUT | Mapping đúng, không xung đột USB/strapping/onboard; giải quyết sai lệch LED |
| HW-01 | ST7789 SPI tùy chỉnh, CS/BLK module thật | Hiển thị 240×240, LVGL hoạt động; điện áp/dòng BLK phù hợp |
| HW-02 | Keypad 16 phím và continuity cáp | Đúng R/C/layout, debounce; nhập/sửa PIN giữ 0 đầu |
| HW-03 | MG90S từng ngăn không tải rồi có chốt | Hiệu chỉnh góc/pulse, không kẹt/nóng; không suy khóa cơ khí từ result |
| HW-04 | MC-38 gần/xa nam châm, mở/đóng cửa, rung/đứt dây | Xác minh polarity, debounce, xử lý UNKNOWN/an toàn |
| HW-05 | LOCK khi OPEN/UNKNOWN | Node từ chối, không điều khiển LOCK |
| HW-06 | L01/L02 và hai servo chạy có tải | Đúng ngăn, không ảnh hưởng ngăn kia, đo nguồn 5V–2A; không brownout/reset |

## Giao tiếp và nghiệp vụ

| Test | Nội dung | Kỳ vọng |
|---|---|---|
| COM-01 | Central 1↔Node 2, L01/L02; UNLOCK/LOCK/GET_STATUS | Correlation đúng, ACK tách result/door/status/error |
| COM-02 | Mất/gửi lặp/đảo packet, version/type/length sai, peer lạ, reboot | Validate, dedup, không mở lặp; fail closed và reconcile |
| COM-03 | Serial JSON Lines UTF-8/115200, dòng lỗi/dở dang, ngắt/cắm USB | Khôi phục framing, không tạo lệnh giả; không replay UNLOCK mù |
| BE-01 | S hai ngăn trống; L01 bận; M khi L02 bận | S ưu tiên L01 rồi L02; M không dùng L01 |
| BE-02 | Offline/fault/unknown/đang dùng và hai yêu cầu đồng thời | Không cấp ngăn không hợp lệ, không cấp trùng |
| AUTH-01 | App đúng owner chọn kiện và yêu cầu mã | Chuỗi 6 chữ số, giữ 0 đầu, TTL 30 giây; countdown không quyết hiệu lực |
| AUTH-02 | Nhập PIN tại keypad, đúng kiosk/parcel/owner | Backend tiêu thụ một lần atomic với tạo PICKUP/UNLOCK intent |
| AUTH-03 | Sai PIN/chủ đơn/kiện/kiosk scope, hết hạn đúng biên 30s, mã đã dùng | Từ chối; attempts/rate limit kiosk theo policy đã chốt |
| AUTH-04 | Collision hai phiên active cùng scope; hai verify đồng thời | Không cấp mã mơ hồ; tối đa một giao dịch/UNLOCK; retry idempotent |
| AUTH-05 | Backend/Serial mất phản hồi, App countdown lệch | Không mở offline, không TOTP; Backend là nơi kiểm expiry |
| AUTH-06 | Log/audit/DB/telemetry và retry cấp PIN | Không giữ plaintext lâu dài hoặc log mã/token; verifier bảo vệ PIN ngắn được review |
| INT-01 | Gửi→nhận một ngăn rồi cả L01/L02 | Confirmation + OPEN→CLOSED đúng phiên + CLOSED mới + LOCK_APPLIED đúng command |
| INT-02 | Thiếu từng evidence, stale/reordered event, lỗi/offline/boot đổi | Không hoàn tất/tự giải phóng; giữ reservation và reconcile |
| IOT-01 | Telemetry giả lập rồi nguồn thật | Mapping door/servo/online/business đúng; thống kê/cảnh báo đúng, không PII/secrets |

Ngưỡng retry/timeout/debounce, rate limit và hạn mức PIN v2.1 chưa chốt: ghi expected theo contract đã review trước chạy; không tự lấy tham số test cũ làm production policy. Freshness Phase 1 hiện là 10 giây, không phải mọi timeout giao tiếp.

## Kiểm chứng source hiện có

Backend: tại root sau cài backend/requirements.txt, chạy `python -m pytest -q` (pytest.ini thu thập backend/tests). Bộ test hiện có kiểm Phase 1/simulator theo **flow opaque code kiosk cũ**, chưa kiểm API PIN v2.1. [Hướng dẫn Phase 1](BACKEND_PHASE1.md), [simulator](../backend/demo/README.md).

Firmware host/build và báo cáo TEST8A/B/C giữ nguyên. Chưa build target v2.1 hoặc upload trong lần sửa tài liệu. Helper MQTT tại tests/coreiot/test5_telemetry.py chỉ là smoke thủ công; MQTT ACK không chứng minh Dashboard hay HIL hoạt động.

## Evidence cần lưu

Ghi ngày, commit, board revision, environment/library, wiring/pinout, nguồn và cấu hình protocol; log request/command/transaction/boot/sequence đã che secrets; ảnh chốt, đo nguồn, polarity, video gửi/nhận/best-fit/lỗi. Nêu rõ giới hạn: MC-38 chỉ đo cửa, không xác minh chốt gài hoặc kiện hiện diện. [PINOUT](../hardware/PINOUT.md), [tests README](../tests/README.md).

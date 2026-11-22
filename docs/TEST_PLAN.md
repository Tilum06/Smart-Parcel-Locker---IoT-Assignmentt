## Kiểm thử backend Phase 1

Chạy `python -m pytest -q` tại root sau khi cài `backend/requirements.txt`; tests trong `backend/tests`, database tạm và mock adapter. Bao phủ seed L01=S/L02=M offline, Best-fit, allocation atomic/concurrency, dedup, auth/ownership, mã kiosk TTL/one-use và state/evidence. Chính sách hiện hành không latch sensor: đủ confirmation + cycle + CLOSED mới + LOCK_APPLIED thì hoàn tất; thiếu từng điều kiện, OPEN/UNKNOWN, stale/offline không hoàn tất. Mock không sinh ENGAGED. [Hướng dẫn](BACKEND_PHASE1.md). Không phải kết quả kiểm thử phần cứng hay CoreIOT.

---

# Test plan — MVP v2.0

Chỉ đánh dấu **PASS** khi có log/ảnh/video với **2 S3 + 2 MG90S + 2 MC-38**. Test relay/khóa 12V không phải test servo.

| Test | Nội dung | Kỳ vọng |
|---|---|---|
| HW-01 | MG90S một ngăn không tải rồi có chốt | Quay tới hai vị trí không kẹt/nóng; nguồn ổn định |
| HW-02 | MC-38 NC OPEN/CLOSED | Polarity, debounce chính xác |
| HW-03 | LOCK khi door OPEN/UNKNOWN | Không thực thi servo LOCK |
| HW-04 | L01 và L02 riêng lẻ | Đúng servo, ngăn kia không bị ảnh hưởng |
| HW-05 | Hai servo chạy theo tình huống thực | Không brownout/reset, nguồn 5V đủ dòng |
| COM-01 | ESP-NOW một Central ↔ một Node | ACK/STATUS/result tương ứng, không nhầm ngăn |
| COM-02 | Serial PC ↔ Central | JSON Lines, timeout/khôi phục không sinh lệnh mở lặp |
| BE-01 | S, hai ngăn trống | Ưu tiên L01(S) |
| BE-02 | S, L01 bận | Nâng lên L02(M) nếu hợp lệ |
| BE-03 | M, L02 bận | Không chọn L01(S) |
| BE-04 | Hai đơn đồng thời | Không cấp trùng |
| INT-01 | Gửi/nhận một ngăn | Confirmation + door cycle + servo result; không suy chốt gài |
| AUTH-01 | Code nhận đúng chủ ≤30s | Một lần dùng và mở đúng ngăn |
| AUTH-02 | Sai/hết hạn/đã dùng/khác chủ | Từ chối, giới hạn thử |
| ERR-01 | Door UNKNOWN, kẹt servo, offline/reboot | UNKNOWN/MAINTENANCE, không tự AVAILABLE |
| IOT-01 | Telemetry/dashboard CoreIOT | Trạng thái đúng, không lộ PII/token |

Thu thập sơ đồ wiring, ảnh chốt, log request/transaction/boot (đã che bí mật), đo nguồn 5V, video gửi→nhận và best-fit S→M. Báo cáo giới hạn: MC-38 đo cửa, không xác nhận gài chốt.

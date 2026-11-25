# Gateway PC — MVP v2.1

**Planned:** module transport trong cùng ứng dụng Python FastAPI + SQLite, không tách HTTP server thứ hai. USB Serial UTF-8 JSON Lines, baud ban đầu 115200 tới Central ID 1; Central chuyển ESP-NOW tới Locker Node ID 2 cho L01=S/L02=M. MQTT nối PC với CoreIoT để giám sát, telemetry, thống kê, cảnh báo; hai ESP32 không bắt buộc Internet trực tiếp.

Gateway correlate request/command/transaction/boot/sequence; map ACK, COMMAND_RESULT, DOOR_EVENT, STATUS, ERROR vào boundary thiết bị. Không tự cấp ngăn hoặc quyết định quyền. Backend lưu intent trước gửi và chỉ hoàn tất khi đủ confirmation/cycle/CLOSED mới/LOCK_APPLIED hợp lệ, không lỗi/offline/unknown. ACK không chứng minh servo chạy hay chốt cơ khí đã gài.

Implemented hiện chỉ có boundary `backend/devices.py` với PendingDeviceAdapter và hook dispatch/ingest; chưa có Serial/MQTT adapter production, heartbeat/reconcile hoặc STATUS mapper hoàn chỉnh. `tests/coreiot/test5_telemetry.py` là smoke helper dữ liệu giả, không phải Gateway tích hợp. [Contract và mapping cần làm](../docs/INTERFACES.md), [Phase 1](../docs/BACKEND_PHASE1.md).

PIN nhận hàng v2.1 đi từ App → người dùng nhập keypad → Serial → Backend xác thực; Backend không phản hồi thì không mở. API mới chưa triển khai. Không log PIN/SĐT/mã phòng/password/token. Member 1 phụ trách Serial, Member 2 MQTT theo [đề xuất](../docs/ROADMAP.md); schema và tích hợp là việc chung. CoreIoT dùng fixture song song từ phase 0–1.

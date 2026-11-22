# Git sync review — 23/11/2026

Repository: `Tilum06/Smart-Parcel-Locker---IoT-Assignmentt`.
Branch: `feat/demo-simulator`; starting HEAD and remote branch:
`31834a3630724add5aadcf452b4db3497d105a43`.

## Phạm vi và trạng thái triển khai

Các tài liệu v2.0 mô tả **thiết kế mục tiêu**, không xác nhận firmware đã tích hợp.
Backend Phase 1 và simulator đã có trong lịch sử Git trước lần đồng bộ này.
Không có code Android mới trong lần đồng bộ này.

- Backend: FastAPI/SQLite, seed offline L01=S/L02=M, best-fit, reservation atomic,
  auth/role/ownership, idempotency, kiosk code one-use 30 giây, vòng đời gửi/nhận,
  audit và kiểm tra evidence theo transaction/boot/sequence/freshness.
- Simulator: ứng dụng localhost riêng, SQLite riêng, dashboard và sự kiện thiết bị
  thủ công, gửi/nhận, restart/offline/error/reset; không thay bằng chứng phần cứng.
- Firmware local chưa commit: Test 6A ping/pong ESP-NOW; Test 6B nút/LED,
  debounce, sequence và timeout; Test 8A đọc MC-38; Test 8B relay bench tự động;
  Test 8C nút kích xung relay 500 ms, cooldown và cutoff timer.
- Helper CoreIOT: gửi ba telemetry mô phỏng, QoS 1, kiểm PUBACK và timeout;
  không chứng minh dữ liệu đã được CoreIOT lưu hoặc dashboard đã hoạt động.

## Kiểm tra Backend

`python -m pytest -q`: **75 passed, 1 warning**, 64,60 giây, Python trong `.venv`.
Warning là deprecation `anyio.abc.BlockingPortal` từ Starlette.
Lần chạy sandbox ban đầu dừng sau khi không tiến triển; chạy lại ngoài sandbox
hoàn tất. Tests chạy trên working tree, có cả thay đổi mật khẩu 8 ký tự đang giữ
lại; không có test chuyên biệt xác nhận quyết định giảm từ 12 xuống 8 ký tự.

`pip check`, `compileall backend tests/coreiot` và
`node --check backend/demo/static/app.js`: PASS.

Giữ nguyên, không commit `backend/manage.py`, `backend/schemas.py` và
`docs/BACKEND_PHASE1.md`: cùng thay đổi policy password 12 → 8 ký tự.
Đây là thay đổi giảm ràng buộc bảo mật, cần đánh giá riêng; không rollback.
Trên GitHub, policy vẫn là 12–128 ký tự sau lần push này.

## Kiểm tra Firmware và PlatformIO

Build-only bằng PlatformIO đã cài: **5/5 SUCCESS**:

- `central_esp32`
- `locker_b_s3`
- `locker_b_s3_test8a`
- `test8b_relay_s3`
- `test8c_lock_s3`

Toolchain quan sát: Espressif32 8.0.0, Arduino-ESP32 3.3.12.
Lần build sandbox bị chặn ghi lock/cache trong hồ sơ người dùng; chạy lại với
quyền truy cập toolchain đã hoàn tất. Không upload hoặc thao tác board.

Host harness biên dịch bằng `g++ -std=c++17 -Wall -Wextra -Werror`:

- Test 6A/6B codec/logic: PASS.
- Test 8B: **FAIL** tại `test8b_host.cpp:30`. Source đặt `PULSE_MS=2000`,
  trong khi test và `TEST8B.md` yêu cầu ON 300 ms. Tại 2300 ms test muốn OFF
  nhưng relay vẫn ON. Không sửa source, test hoặc tài liệu để che lỗi.
- Test 8C: PASS cho `normal`, `create-failure`, `start-failure`, `late-arm`.
  Host mocks không chứng minh timing/concurrency hoặc an toàn điện trên board.

**Dừng commit toàn bộ nhóm firmware thử nghiệm** do lỗi Test 8B và các điểm chưa
nhất quán cần giải quyết cùng nhau:

1. Central `board=esp32dev`, GPIO LED 2/nút 5; thiết kế v2.0 yêu cầu Yolo UNO S3.
2. Protocol Test 6A/6B dùng Central ID=3/Node ID=2; thiết kế dùng Central ID=1.
3. Firmware mặc định chỉ là demo ESP-NOW nút/LED, chưa có servo hai ngăn,
   LOCK guard MC-38, protocol nghiệp vụ, Serial JSON Lines, kiosk LVGL/keypad.
4. Test 8B/8C dùng relay/khóa 12V, khác MVP MG90S 5V; không dùng làm evidence servo.
5. PlatformIO chưa pin version; COM10/COM11 phụ thuộc máy. Cần khóa board/framework
   và profile trước tích hợp. Build thành công không xác minh profile đúng board thật.

Gateway Serial/MQTT production, CoreIOT dashboard/notification, Web App production,
Android App, HIL và quy trình reconcile vận hành vẫn còn phải triển khai/xác minh.
Production dùng `PendingDeviceAdapter`, không tự phát sinh sensor evidence.
Backend hiện không yêu cầu ENGAGED và không suy chốt vật lý từ LOCK_APPLIED.

## Kiểm tra CoreIOT

Đã đọc toàn bộ helper, kiểm AST/cú pháp và nhánh thiếu dependency.
Chạy `python -I tests/coreiot/test5_telemetry.py`: **BLOCKED, exit 2** vì `.venv`
chưa có `paho-mqtt>=2,<3`; không cài thêm và không gửi dữ liệu ra broker.
Helper được commit như công cụ kiểm thử thủ công đã review, không ghi nhận live PASS.
Broker cố định port 1883, không TLS: không dùng token production qua mạng không tin cậy.
Không có token hardcode; nhập token bằng env hoặc getpass, không echo fallback.
`pytest.ini` chỉ collect `backend/tests`; helper không nằm trong 75 tests nói trên.

## File được đồng bộ

Commit Git hygiene: `.gitignore` (bổ sung `.vscode/` và `~$*`).

Commit Documentation:

```text
README.md
backend/README.md
coreiot/README.md
docs/ARCHITECTURE.md
docs/DECISIONS.md
docs/INTERFACES.md
docs/ISSUES.md
docs/PROJECT_SPEC.md
docs/ROADMAP.md
docs/TEST_PLAN.md
docs/GIT_SYNC_REVIEW_2026-11-23.md
firmware/central-controller/README.md
firmware/central-controller/kiosk/README.md
firmware/central-controller/webserver/README.md
firmware/locker-node/README.md
gateway/README.md
hardware/README.md
tests/README.md
web-app/README.md
```

Commit CoreIOT test helper: `tests/coreiot/test5_telemetry.py`.

## File loại khỏi commit

- Ba file policy password liệt kê ở trên: giữ modified, cần đánh giá riêng.
- `firmware/common/*.h`, hai `firmware/*/platformio.ini`, hai
  `firmware/*/.gitignore`, toàn bộ `firmware/*/src/`, `firmware/locker-node/test/`
  và `firmware/locker-node/TEST8A.md`, `TEST8B.md`, `TEST8C.md`:
  giữ untracked, nhóm firmware đang bị chặn; không chọn lẻ để tạo project thiếu file.
- Hai `firmware/*/.vscode/`: cấu hình IDE local, giữ trên ổ đĩa và ignore.
- `docs/~$ongBao_BaiTapLon_IoT.docx`: file khóa Office, ignore, không đọc nội dung.
- `.pio/` (bao gồm binary host), `.venv/`, Python/test caches, SQLite runtime,
  logs, secrets/credentials và thông báo môn học đã bị ignore: không stage.

Đã kiểm tra diff, danh sách untracked, index ban đầu rỗng, ignore rules và mẫu
secret phổ biến trong source/config mới; không thấy secret hardcode trong phần review.
Không đưa dữ liệu runtime, số điện thoại thật hoặc token vào commit.
Không xóa/ghi đè thay đổi cũ, không sửa lỗi ngoài phạm vi, không merge/force-push.

## Điều kiện trước Android branch

Lần đồng bộ này chủ động để working tree còn dirty vì các mục đang giữ lại.
Không tạo `feat/resident-mobile-app` hoặc mang ngầm thay đổi firmware/password sang đó.
Cần quyết định riêng cho các thay đổi đang giữ, hoặc dùng worktree sạch từ commit
đã push khi bắt đầu Android. Báo cáo chat cuối cùng ghi SHA push và git status thực tế.

# Bàn giao tài liệu MVP v2.1 — branch feat/embedded

Ngày 25/11/2026. Theo yêu cầu tiếp theo của người dùng: tạo worktree riêng, branch feat/embedded từ origin/feat/demo-simulator; chỉ commit/push tài liệu, không merge main, không đổi các branch hiện có, chưa tạo feat/central-controller/feat/locker-node.

## Branch và nguồn

- Base: origin/feat/demo-simulator tại `fa1c26b83810f58168cc8f131d1b94afca9e8a9a`.
- Đã kiểm GitHub bằng ls-remote trước khi tạo: base khớp remote; feat/embedded chưa tồn tại.
- Branch mới: feat/embedded; remote đích: origin/feat/embedded.
- Commit message: `docs(embedded): finalize MVP v2.1 architecture and pinout`.
- SHA commit được báo sau commit; dùng git log -1 để đọc, không nhúng SHA tự tham chiếu vào chính commit.

## Bảo toàn workspace gốc

Workspace gốc E:/01_Study/project/iot/Assignment vẫn ở feat/resident-mobile-app, HEAD f5cdef9187a32531343c32df8e36326b4fb0ab7c. Toàn bộ tài liệu v2.1 và thay đổi local ban đầu được giữ nguyên tại đó; không reset/clean/stash/stage/commit trên checkout gốc.

Không chuyển policy mật khẩu local 8 ký tự, source firmware untracked, cấu hình PlatformIO/COM cá nhân hoặc source Expo starter vào branch mới. Backend Phase 1 trên branch Embedded giữ policy 12–128 ký tự theo base; chỉ thêm phần đối chiếu v2.1. Những nhận xét về test firmware/Expo có nhãn phạm vi workspace gốc, không tuyên bố chúng nằm trong tree Embedded.

## File tài liệu cập nhật

- [README.md](../README.md)
- [backend/README.md](../backend/README.md)
- [backend/demo/README.md](../backend/demo/README.md)
- [coreiot/README.md](../coreiot/README.md)
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/BACKEND_PHASE1.md](BACKEND_PHASE1.md)
- [docs/DECISIONS.md](DECISIONS.md)
- [docs/INTERFACES.md](INTERFACES.md)
- [docs/ISSUES.md](ISSUES.md)
- [docs/PROJECT_SPEC.md](PROJECT_SPEC.md)
- [docs/ROADMAP.md](ROADMAP.md)
- [docs/TEST_PLAN.md](TEST_PLAN.md)
- [firmware/central-controller/README.md](../firmware/central-controller/README.md)
- [firmware/central-controller/kiosk/README.md](../firmware/central-controller/kiosk/README.md)
- [firmware/central-controller/webserver/README.md](../firmware/central-controller/webserver/README.md)
- [firmware/locker-node/README.md](../firmware/locker-node/README.md)
- [gateway/README.md](../gateway/README.md)
- [hardware/README.md](../hardware/README.md)
- [tests/README.md](../tests/README.md)
- [web-app/README.md](../web-app/README.md)

## File mới

- [docs/GIT_WORKFLOW.md](GIT_WORKFLOW.md)
- [hardware/PINOUT.md](../hardware/PINOUT.md)
- [mobile/README.md](../mobile/README.md)
- [docs/DOCUMENTATION_V2_1_REVIEW.md](DOCUMENTATION_V2_1_REVIEW.md)

## Thiết kế và khác biệt implementation

Baseline: hai Yolo UNO ESP32-S3, Central 1/Node 2; L01=S/L02=M; hai MG90S 5V + chốt cơ khí, hai MC-38 NC. Central ST7789/LVGL/keypad, ESP-NOW và USB Serial; Backend/Gateway cùng ứng dụng Python; CoreIoT giám sát/telemetry/thống kê/cảnh báo. [Đặc tả](PROJECT_SPEC.md), [kiến trúc](ARCHITECTURE.md).

Nhận mục tiêu: Mobile App yêu cầu PIN 6 chữ số/30 giây, nhập tại keypad để Backend kiểm owner/parcel/expiry/kiosk scope, consume atomic với tạo giao dịch/UNLOCK intent. Không mở khi Backend không phản hồi; không TOTP offline. Phase 1 vẫn dùng opaque code do kiosk tạo và resident submit qua API; API PIN mới/confirm kiosk/rate limit chưa có. [Interfaces](INTERFACES.md).

ACK, kết quả servo, trạng thái cửa và STATUS được phân biệt. LOCK_APPLIED không chứng minh chốt gài cơ khí; không cảm biến chốt/kiện hàng. Cấu hình relay/12V, ba board/bốn ngăn và flow cũ chỉ còn trong lịch sử hoặc phần implementation cũ/Backlog có nhãn. Không lấy PASS test cũ làm evidence servo v2.1.

## Pinout và phần chưa xác minh

Nguồn pinout duy nhất: [hardware/PINOUT.md](../hardware/PINOUT.md). Mapping mục tiêu khớp ảnh OhStem; chưa HIL trên board dự án. Sai lệch NeoPixel GPIO45 trong ảnh và GPIO48 trong sample được giữ thành gate revision, không tự chọn mapping onboard.

Còn cần xác minh revision/board definition/USB CDC, ST7789 CS/BLK, keypad continuity, polarity/debounce MC-38, góc/pulse/chốt, kích thước S/M và tải nguồn 5V–2A. Chưa chốt MAC/channel/serialization/packet size/timeout/retry/dedup/security, Serial envelope/handshake/timebase, heartbeat/reconcile, telemetry schema và API/verifier/rate limit PIN.

## Trước khi chia hai branch firmware

Review source local riêng, chọn baseline code, xác minh pinout/nguồn/target S3/framework/library; hai thành viên thống nhất protocol và config chung; chốt API PIN/confirmation và mapping DeviceEvent/CoreIoT. Chỉ tạo branch con khi được yêu cầu. [Git workflow](GIT_WORKFLOW.md), [roadmap/phân công](ROADMAP.md), [test plan](TEST_PLAN.md).

## Kiểm tra Markdown và liên kết

PASS: 26 file Markdown, 119 liên kết nội bộ có target/heading hợp lệ; UTF-8 và fence hợp lệ. git diff --check đạt; chỉ 24 file .md trong phạm vi thay đổi (20 cập nhật, 4 mới). Không có source Mobile trong worktree này nên không chạy Expo tại đây. Lint/typecheck đã PASS ở workspace gốc trong lần cập nhật trước, không phải kiểm thử branch Embedded.

## Kiểm tra scope và bảo toàn

Chỉ file .md trong danh sách trên được stage. Kiểm tra trước stage: checksum toàn bộ 145 file trong snapshot workspace gốc giữ nguyên, git status giữ nguyên và HEAD/branch gốc không đổi. Các refs branch hiện có được đối chiếu lại sau push. Tài liệu lịch sử có trong base, source Backend và helper MQTT giữ nguyên; không đưa firmware test chưa track vào commit. Không chạy lại backend/firmware/HIL/MQTT cho thay đổi tài liệu.

## Kiểm tra Git và kết quả xuất bản

Chạy git diff --check, kiểm staged diff --check và staged name-status trước commit. Sau commit/push, đối chiếu SHA local với refs/heads/feat/embedded trên GitHub, upstream và git status của worktree. Kết quả/SHA cuối được báo trong phản hồi bàn giao; workspace gốc được phép còn dirty như snapshot ban đầu.

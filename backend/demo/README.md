# Parcel Lab — Development Demo Simulator

Giao diện HTML/CSS/JavaScript và một FastAPI development app riêng, dùng lại business
logic Phase 1. Chỉ chạy cục bộ; không phải Web App production. Không firmware/CoreIOT.

## Khởi chạy trên Windows

Mở PowerShell tại repository root, dùng Python 3.11+:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m backend.demo --port 8001
```

Mở **http://127.0.0.1:8001/**. Dừng bằng Ctrl+C. Không cần chạy `backend.manage init`,
không cần khai báo credential và không cần chạy production server trước.
Nếu đã có `.venv` và dependencies thì chỉ cần lệnh cuối. CLI chỉ nhận `--port`;
host cố định 127.0.0.1, một worker, `proxy_headers=False`, không có tùy chọn host LAN.

SQLite riêng: **`backend/demo/data/simulator.sqlite3`**, tự khởi tạo bằng schema thật và
thêm các bảng dành riêng cho demo. Không đọc/ghi `backend/data/locker.sqlite3`.
`LOCKER_DB_PATH` không chọn database cho simulator. Nếu biến này trỏ trùng file demo,
startup từ chối để tránh nhầm môi trường. File SQLite/journal và `.venv` được Git ignore.

Khởi tạo tài khoản giả:

| Username | Vai trò | Phòng | SĐT giả |
|---|---|---|---|
| demo-admin | ADMIN | — | — |
| demo-kiosk | KIOSK | — | — |
| resident-001 | RESIDENT | 001 | 0000000001 |
| resident-002 | RESIDENT | 002 | 0000000002 |

Mật khẩu ngẫu nhiên được tạo trong RAM mỗi lần startup và lưu PBKDF2 trong DB.
Xem mục **Tài khoản demo được tạo sẵn** trong giao diện. Mật khẩu cư dân 001 được điền
sẵn nhưng phải bấm **Đăng nhập cư dân**. Khi nhập username cư dân 002 và rời ô nhập,
giao diện điền mật khẩu demo của cư dân đó. Có thể nhập sai để thử authentication.
Kiosk demo đăng nhập tự động bằng API auth thật khi tải trang; cư dân đăng nhập thủ công.
Không sử dụng dữ liệu thật. Không đưa mật khẩu/token/code vào Git, URL hay console log.

## Demo gửi hàng

1. Bấm **Kết nối Node**. Mặc định L01=S và L02=M đều AVAILABLE nhưng **offline**.
2. Nhập phòng `001`, SĐT `0000000001`, size S, bấm **Đặt ngăn gửi hàng**.
   Backend Best-fit chọn L01 nếu còn trống; S có thể dùng L02, M chỉ dùng L02.
3. Ở card ngăn được cấp, bấm **UNLOCK**: adapter gửi UNLOCK_APPLIED đúng command.
4. Bấm **Mở cửa**, sau đó **Đóng cửa** để tạo chu kỳ OPEN→CLOSED đúng transaction.
5. Chọn đơn tại **Đơn cần xác nhận**, bấm **Xác nhận đã gửi hàng**.
6. Bấm **LOCK** khi dữ liệu CLOSED còn mới → parcel STORED, locker OCCUPIED.

Không có bước phần cứng tự chạy. Bấm confirmation sớm chỉ ghi nhận ý định nghiệp vụ;
không tự tạo OPEN/CLOSED/LOCK_APPLIED hay hoàn tất đơn.

## Demo nhận hàng

1. Bấm **Đăng nhập cư dân** bằng đúng chủ đơn; chỉ đơn của người đó hiện trong form nhận.
2. Chọn đơn STORED, bấm **Lấy mã kiosk**. Mã một lần có **TTL 30 giây**;
   UI hiển thị thời gian còn lại, backend mới là nơi quyết định hiệu lực/quyền.
3. Bấm **Xác thực nhận hàng**. Có thể sửa mã để thử lỗi; sau 5 lần sai, phiên bị khóa.
4. Ở ngăn được cấp, bấm **UNLOCK**, **Mở cửa**, **Đóng cửa**.
5. Bấm **Xác nhận đã lấy hàng**, rồi **LOCK** khi dữ liệu CLOSED còn mới.
6. Backend chuyển parcel COMPLETED, locker AVAILABLE; hai giao dịch DEPOSIT/PICKUP
   được giữ trong lịch sử.

## Quan sát, lỗi và reset

- Dashboard và trạng thái DB được poll mỗi 1,5 giây; sau mỗi thao tác sẽ refresh ngay.
  Poll/countdown chỉ đọc, không sinh tín hiệu thiết bị. Mất đồng bộ có banner, không tự đổi trạng thái.
- Dải UNLOCK/OPEN/CLOSED/CONFIRM/LOCK thể hiện evidence đã lưu, không dự đoán kết quả.
- **Snapshot CLOSED mới** là thao tác thủ công: làm mới dữ liệu cửa trong đúng phiên,
  không tạo chu kỳ OPEN→CLOSED. Backend chỉ dùng CLOSED không quá **10 giây**.
  Nếu chờ lâu giữa các bước, bấm nút này rồi LOCK; nếu LOCK đã APPLIED nhưng CLOSED
  cũ, snapshot mới có thể hoàn tất phiên khi đã đủ các điều kiện khác.
- **Ngắt kết nối** làm pending transactions chuyển EXCEPTION, locker UNKNOWN, reservation
  vẫn active. **Mô phỏng lỗi** có tác dụng tương tự cho ngăn đang có phiên pending.
- Kết nối lại không giải phóng ngăn UNKNOWN và không tự khôi phục giao dịch lỗi.
  Khởi động lại app giữ parcel/reservation nhưng buộc offline, door snapshot UNKNOWN,
  thu hồi token và tạo mật khẩu demo mới. Không tự phát lại UNLOCK.
- Xem **Đơn hàng**, tab **Sự kiện/Giao dịch**, lọc theo đơn và mở **SQLite Inspector**.
  Inspector là snapshot read-only của các bảng, loại bỏ hash code/password và bearer token.
- **Reset demo** có hộp thoại xác nhận. Đây là thao tác chủ động xóa dữ liệu giao dịch demo
  trong một SQLite transaction, thu hồi token, đưa hai ngăn AVAILABLE nhưng offline và door UNKNOWN.
  Không xóa file, không chạm database production, không phải timeout/recovery tự động.
  Các account giả và mật khẩu hiện tại được giữ; UI đăng nhập kiosk lại và yêu cầu login cư dân lại.

**LOCK_APPLIED chỉ xác nhận servo đã được điều khiển. Không chứng minh chốt đã gài cơ khí.**
Simulator không có latch sensor và không phát sinh ENGAGED. Hoàn tất dùng confirmation,
door cycle, CLOSED mới hợp lệ, LOCK_APPLIED đúng command và không lỗi/offline/unknown.

## Phân tách môi trường

- Production vẫn là `backend.main:app`; không import package `backend.demo`, không có
  `/demo/*`, `/assets/*` hoặc giao diện simulator. Source production và 61 tests gốc giữ nguyên.
- `create_demo_app()` bọc application factory thật, tái sử dụng toàn bộ `/api/v1/*`:
  auth, role/ownership, allocation atomic, dedup, kiosk TTL và lifecycle.
- HTTP mô phỏng chỉ đăng ký trong development app:

| Method + path | Chức năng |
|---|---|
| GET / | Giao diện |
| GET /demo/bootstrap | Credential demo ngẫu nhiên trong RAM, chỉ dành cho localhost |
| GET /demo/state | Snapshot DB nhất quán, không có secret hashes/token |
| POST /demo/node | `{ "online": true/false }` — kết nối/ngắt cả Node |
| POST /demo/lockers/{id}/events | event_id, transaction_id, kind, door; các sự kiện thiết bị thủ công |
| POST /demo/reset | Reset chủ động database demo |

- Dev endpoint là công cụ điều khiển đáng tin cậy tại localhost, không yêu cầu role production.
  Mutation (kể cả `/api/v1/*` trong app demo) cần **`X-Demo-Control: 1`**. API nghiệp vụ
  vẫn cần bearer + X-Request-ID theo contract thật. Frontend tự thêm các header này.
- App từ chối client không phải loopback, Host ngoài localhost/127.0.0.1/::1, Origin khác
  origin của app hoặc Sec-Fetch-Site=cross-site. Không bật CORS. Không triển khai qua proxy,
  tunnel, LAN hoặc cloud. Credential demo có chủ ý đọc được bởi các process trên máy local.
- Không dùng Swagger của app demo: CSP chỉ cho phép tài nguyên local. Swagger production
  tại port 8000 giữ nguyên. Thao tác demo qua UI hoặc HTTP client với header nói trên.
- Database demo có marker riêng, từ chối file có sẵn không đúng marker trước khi sửa schema.
  Có kiểm tra trùng đường dẫn/hardlink với database production được cấu hình.
  Reset chỉ xóa các bảng dữ liệu demo đã định danh; không xóa/drop file hay migration production.
- Adapter dựng DeviceEvent với boot/sequence/timestamp/command tương ứng rồi gọi `devices.ingest`
  thật. Không viết lại Best-fit/state machine ở frontend. Event ID lặp cùng payload không tạo
  snapshot mới; khác payload bị từ chối. Một process serializes HTTP requests để reset và
  các bước mô phỏng không chạy xen kẽ; SQLite vẫn chịu trách nhiệm reservation atomic.

## Source và kiểm thử

| File | Nội dung |
|---|---|
| `__main__.py` | CLI cố định loopback |
| `app.py` | Development-only routes, static mount, guard và application factory |
| `simulator.py` | Demo DB/seed/reset/snapshot, adapter thiết bị thủ công |
| `static/index.html` | Dashboard/forms/history/inspector |
| `static/app.css` | Layout desktop/mobile, trạng thái trực quan |
| `static/app.js` | Gọi API thật, tương tác thủ công, polling và countdown read-only |
| `../tests/test_demo.py` | Integration tests simulator/cách ly production |

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests/test_demo.py -q
.\.venv\Scripts\python.exe -m pytest -q
node --check backend/demo/static/app.js
```

Không cần Node.js để chạy simulator; lệnh cuối chỉ là kiểm tra cú pháp JavaScript khi có Node.
Test dùng database tạm, giả lập kết nối qua các endpoint development và gọi business API thật.
Bao phủ lifecycle đầy đủ, thiếu evidence, stale snapshot, restart, lỗi/offline, reset/token,
TTL/ownership, dedup, bảo vệ localhost/Origin, file marker, static assets và production isolation.

Kết quả ngày 23/11/2026 trên Windows/Python 3.13.15: **75 passed, 0 failed** trong
71,71 giây, gồm **61 tests Phase 1 không sửa** và **14 tests simulator mới**. Một
DeprecationWarning từ Starlette/AnyIO về BlockingPortal, không có test bị skip.
`pip check`, compile Python và `node --check` thành công. Đã kiểm chứng bằng trình duyệt:
S cấp L01; UNLOCK/OPEN/CLOSED/confirmation/LOCK → STORED/OCCUPIED; login cư dân,
mã kiosk và chu trình nhận → COMPLETED/AVAILABLE; history/Inspector và reset về offline.
Console không có lỗi JavaScript ở lần kiểm tra sau restart. Kiểm tra production xác nhận
không có route simulator và database production mẫu không thay đổi byte nào.

## Giới hạn

Đây là lab một người dùng, một process, không mô phỏng dòng điện servo, kẹt chốt,
debounce cảm biến, ACK/retry radio/Serial, clock đồng bộ ESP32 hay giao thức phần cứng.
Không HIL, firmware, CoreIOT, notification hoặc Web App production. Sau EXCEPTION cần
reset dữ liệu demo; chưa có quy trình reconcile thủ công cho vận hành thật. Bảng sự kiện UI
hiển thị tối đa 120 sự kiện mới nhất; Inspector vẫn đọc toàn bộ snapshot. Không nhập PII thật.

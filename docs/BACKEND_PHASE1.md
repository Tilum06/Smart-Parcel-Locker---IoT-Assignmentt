# Backend Phase 1 — Database + FastAPI

Tài liệu triển khai hiện hành, 23/11/2026. Backend/Gateway thuộc **một ứng dụng PC**.
Chỉ có **2 ESP32-S3**: Central (node 1), Locker Node (node 2), với **L01=S, L02=M**.
Servo 5V; cảm biến cửa OPEN/CLOSED. Không triển khai firmware, Web App, CoreIOT.
Các mô tả 3 ESP32, 4 locker hoặc size L trong baseline cũ không áp dụng cho Phase 1.
File lịch sử `PROJECT_SPEC_Smart_Parcel_Locker_v1.2.md` giữ nguyên.

## Cài đặt trên Windows (PowerShell, tại repository root)

Yêu cầu Python 3.11+; đã kiểm chứng bằng Python 3.13.15.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe -m backend.manage init
.\.venv\Scripts\python.exe -m backend.manage create-account --username locker-admin --role ADMIN
.\.venv\Scripts\python.exe -m backend.manage create-account --username central-kiosk --role KIOSK
.\.venv\Scripts\python.exe -m backend.manage demo
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

CLI hỏi mật khẩu qua `getpass`, yêu cầu 12–128 ký tự và nhập lại. Không có credential mặc định.
Demo tạo cư dân `demo-resident`, phòng **"001"**, SĐT giả **"0000000001"**;
mật khẩu do người chạy đặt. Demo chạy một lần trên database mới; trùng account báo lỗi,
không cập nhật tài khoản đang có. Không đưa dữ liệu cá nhân thật vào demo/test.

Swagger: <http://127.0.0.1:8000/docs>; OpenAPI: <http://127.0.0.1:8000/openapi.json>.
Login, copy `access_token`, chọn **Authorize** rồi nhập token. Các API mutation nghiệp vụ
cần header **X-Request-ID** (1–128 ký tự, duy nhất theo account).
Chỉ bind localhost mặc định; triển khai LAN cần TLS qua reverse proxy và kiểm soát truy cập.

Database mặc định `backend/data/locker.sqlite3`; đổi bằng `$env:LOCKER_DB_PATH` hoặc
`python -m backend.manage --db path/to/file.sqlite3 init`. Không commit SQLite/journal.

## Schema và migration

`backend/db.py` dùng SQLite stdlib với SQL parameterized, row factory, foreign keys bật
trên **mọi connection**, timeout/busy_timeout 15 giây. `PRAGMA user_version=1` là migration
đầu tiên, chạy DDL + seed atomic dưới BEGIN IMMEDIATE; lặp init không reset dữ liệu.
Schema mới hơn ứng dụng bị từ chối. Thêm migration version tiếp theo khi thay schema;
không dùng drop/create cho database đã có dữ liệu. Sao lưu database trước nâng cấp.

| Bảng | Quan hệ/ràng buộc chính |
|---|---|
| rooms | PK id; UNIQUE room_code TEXT, CHECK chỉ ASCII số, giữ số 0 đầu |
| residents | FK room_id → rooms; UNIQUE(room_id, phone) |
| accounts | UNIQUE username; PBKDF2-SHA256 600.000 vòng + salt; role ADMIN/RESIDENT/KIOSK; resident_id UNIQUE FK, bắt buộc cho RESIDENT |
| auth_sessions | SHA256 của bearer token ngẫu nhiên; FK account; TTL 1 giờ; logout thu hồi |
| lockers | PK ID; CHECK size S/M, state, online 0/1; node_id; boot/sequence/thời gian quan sát gần nhất |
| parcels | FK resident; requested_size; CHECK parcel status; created_at |
| transactions | FK parcel + locker; DEPOSIT/PICKUP; PENDING/COMPLETED/EXCEPTION; confirmation và door/lock sequence |
| commands | Durable UNLOCK/LOCK intent; FK transaction; UNIQUE(transaction, action); PENDING/APPLIED/ERROR |
| event_logs | Audit trạng thái, confirmation, intent, sự kiện thiết bị; FK parcel/transaction/locker; không lưu secrets/PII |
| device_events | UNIQUE event_id + payload fingerprint, FK transaction; dedup sự kiện thiết bị |
| request_records | PK(account, request_id); operation, fingerprint, response; idempotency bền qua restart |
| kiosk_sessions | FK kiosk account, parcel, resident; hash code ngẫu nhiên; TTL 30s; one-use; tối đa 5 lần sai |

Partial UNIQUE indexes trên transactions(locker_id) và (parcel_id) WHERE active=1
ngăn hai giao dịch active cùng ngăn hoặc cùng đơn. EXCEPTION vẫn active và giữ reservation;
chỉ COMPLETED mới active=0. Một parcel có giao dịch DEPOSIT rồi PICKUP, cùng locker.

## Best-fit và concurrency

`services.allocate` độc lập FastAPI: đối chiếu cư dân tồn tại bằng **room_code + phone**;
không tạo cư dân từ input shipper. Kiện **S→S rồi M**, **M→M**. Cùng size ưu tiên
ID tăng dần (quy tắc tạm thời). Chỉ AVAILABLE + online và không có active transaction.
Chọn ngăn, tạo parcel/transaction, RESERVED, audit, UNLOCK intent và dedup response
trong **một BEGIN IMMEDIATE**. Request khác chờ writer rồi đọc trạng thái mới.
Partial unique indexes là lớp bảo vệ bổ sung; bất kỳ lỗi nào rollback toàn bộ mutation.

## State và bằng chứng vật lý

Locker: AVAILABLE → RESERVED → DEPOSITING → OCCUPIED → COLLECTING → AVAILABLE.
UNKNOWN, FAULT, MAINTENANCE loại khỏi allocation. UNKNOWN/FAULT chỉ tới MAINTENANCE;
MAINTENANCE chỉ về UNKNOWN. Không có API tự giải phóng/reconcile trong Phase 1.

Parcel: CREATED → DEPOSITING → STORED → PICKUP_PENDING → COMPLETED.
CREATED có thể tới CANCELLED (state graph, chưa có endpoint hủy); các trạng thái chưa
kết thúc có thể EXCEPTION. `state.py` từ chối transition ngoài graph.

1. HTTP chấp nhận nghiệp vụ → reserve + UNLOCK intent PENDING.
2. ACK chỉ được audit; không chứng minh lệnh đã áp dụng.
3. UNLOCK_APPLIED đúng command/transaction/locker/boot → DEPOSITING, hoặc tiếp tục PICKUP_PENDING.
4. Cảm biến OPEN rồi CLOSED đúng phiên và đúng thứ tự; confirmation là điều kiện độc lập.
5. Có cả confirmation + CLOSED quan sát không quá 10s → lưu LOCK intent.
6. LOCK_APPLIED đúng command, door CLOSED → ghi kết quả servo đã được điều khiển.
7. Khi confirmation + OPEN→CLOSED + CLOSED còn mới + LOCK_APPLIED đã đủ, không có lỗi,
   mất kết nối hoặc trạng thái không xác định → DEPOSIT hoàn tất/STORED/OCCUPIED,
   hoặc PICKUP hoàn tất/COMPLETED/AVAILABLE. Có thể hoàn tất ngay khi LOCK_APPLIED đến
   nếu snapshot CLOSED trước đó còn mới; nếu snapshot đã cũ thì giữ pending đến khi có
   SENSOR CLOSED hợp lệ mới. Không yêu cầu cảm biến chốt hoặc ENGAGED.

Sự kiện phải không quá 10s, không ở tương lai, không trước transaction/command,
sequence tăng và observed_at không lùi. Duplicate event cùng payload là no-op;
cùng event ID nhưng payload khác bị từ chối. Boot thay đổi, lỗi, offline hoặc mở lại cửa
sau LOCK intent → UNKNOWN/EXCEPTION, vẫn giữ reservation. CLOSED quá cũ khi confirm
không phát LOCK; cần sự kiện CLOSED mới. Thiếu bằng chứng giữ pending vô thời hạn;
không có timeout tự giải phóng. Restart giữ trạng thái/reservation, xóa cờ online,
không phát lại UNLOCK. Adapter tương lai phải reconcile và xác nhận liveness trước cấp mới.

**Quyết định phần cứng hiện hành:** không dùng latch sensor/microswitch. MC-38 chỉ đo
cửa CLOSED; MG90S LOCK_APPLIED chỉ xác nhận servo đã được điều khiển, **không chứng minh
chốt đã gài cơ khí**. Backend hoàn tất nghiệp vụ theo các bằng chứng nêu trên và không
phát sinh ENGAGED giả. Không tạo endpoint giả lập cảm biến cho production.

`devices.DeviceAdapter` là boundary transport trong cùng ứng dụng. `PendingDeviceAdapter`
không sinh sự kiện thành công. `ingest` chỉ để gateway tin cậy gọi nội bộ; HTTP client không
thể gửi bằng chứng vật lý. `dispatch_pending` là hook tích hợp tương lai, không được gọi tự động
ở startup; retry/dedup transport và recovery/reconciliation cần triển khai trước kết nối thật.
`MockDeviceAdapter` chỉ nằm trong tests và chỉ sinh kết nối, door snapshots và kết quả servo giả cho kiểm thử; không sinh ENGAGED.

Locker được seed AVAILABLE nhưng **online=0**; production chưa có heartbeat/adapter thật,
nên POST deposits trả 409 no_suitable_locker. Test fixture bật online trên DB tạm;
demo CLI không bật online và không giả lập cảm biến.

## API contract

Mọi route có prefix `/api/v1`. Bearer session được lưu hash, password lưu PBKDF2;
room/phone chỉ dùng tra cứu người nhận, không là quyền mở khóa.

| Method + path | Quyền | Nội dung |
|---|---|---|
| POST /auth/login | Public | username/password → access_token, token_type, expires_in=3600 |
| POST /auth/logout | Đã login | Thu hồi token hiện tại |
| POST /rooms | ADMIN | room_code string → id, room_code |
| GET /rooms | ADMIN/RESIDENT | Admin xem tất cả; cư dân chỉ phòng mình |
| POST /residents | ADMIN | room_code, phone, username, password; phòng phải tồn tại |
| GET /residents | ADMIN/RESIDENT | Admin xem tất cả; cư dân chỉ thông tin mình |
| GET /lockers | Đã login | id, size, state, online, node_id |
| GET /lockers/{locker_id} | Đã login | Chi tiết locker |
| POST /deposits | KIOSK/ADMIN | room_code, recipient_phone, parcel_size → allocation (201) |
| POST /deposits/{parcel_id}/confirm | KIOSK/ADMIN | Ghi xác nhận gửi; không chứng minh đã khóa |
| POST /kiosk-sessions | KIOSK/ADMIN | parcel_id STORED → session_id, code, expires_at, ttl_seconds=30 (201) |
| POST /pickups/{parcel_id} | RESIDENT chủ đơn | session_id + code → tạo giao dịch PICKUP, lưu UNLOCK intent |
| POST /pickups/{parcel_id}/confirm | RESIDENT chủ đơn | Ghi xác nhận lấy hàng |
| GET /parcels | ADMIN/RESIDENT | Danh sách theo quyền |
| GET /parcels/{parcel_id} | ADMIN/chủ đơn | Chi tiết trạng thái |
| GET /parcels/{parcel_id}/history | ADMIN/chủ đơn | Audit theo thứ tự ID |
| GET /transactions | ADMIN/RESIDENT | Danh sách giao dịch theo quyền |
| GET /transactions/{transaction_id} | ADMIN/chủ đơn | Chi tiết confirmation + evidence sequences |

Tất cả mutation nghiệp vụ (ngoài login/logout) cần X-Request-ID. Cùng actor + ID + operation
+ payload trả lại response đã lưu, không làm lại. Cùng ID khác operation/payload → 409.
Response đã lưu là snapshot; GET parcel để lấy trạng thái mới. Kiosk code chỉ trả một lần,
hash được lưu; retry phát mã trả **409 kiosk_code_already_issued** để tránh lưu plaintext.
Không đưa password/code/token vào audit. Payload fingerprint tạo resident không chứa password;
khi retry, backend kiểm tra password với hash tài khoản để từ chối payload khác.

Mã kiosk có entropy 128 bit, gắn parcel/resident/kiosk account/phiên; hết hạn đúng 30s,
one-use. Sai code tăng attempts bền trong DB, cùng request ID không tăng lại. Sau 5 lần
sai khóa phiên; sai chủ đơn không tiêu thụ mã. Không dùng room/phone làm authorization.
Phase 1 dùng opaque code cho kiosk, chưa có UI/keypad nhập mã hay chọn định dạng PIN ngắn.

Mã lỗi JSON `{"detail":"..."}`: 401 thiếu/sai/hết hạn bearer; 403 sai role/chủ đơn/mã phiên;
404 resource/recipient không tồn tại; 409 hết ngăn, sai state, ID conflict, unique conflict;
422 sai schema (size L, room không phải chuỗi số, field lạ…); 503 SQLite unavailable/busy.

Ví dụ gửi hàng (khi có trusted device online):

```http
POST /api/v1/deposits
Authorization: Bearer <kiosk-token>
X-Request-ID: deposit-demo-001
Content-Type: application/json

{"room_code":"001","recipient_phone":"0000000001","parcel_size":"S"}
```

```json
{"parcel_id":"<uuid>","transaction_id":"<uuid>","locker_id":"L01",
 "requested_size":"S","allocated_size":"S","status":"CREATED"}
```

Xác nhận: `POST /api/v1/deposits/<parcel_id>/confirm`, bearer KIOSK, request ID mới,
không body. Response có parcel_id, transaction_id, status; vẫn CREATED/DEPOSITING nếu thiếu evidence.
Nhận: kiosk tạo `POST /kiosk-sessions` với `{"parcel_id":"<uuid>"}`; cư dân đăng nhập
và `POST /pickups/<parcel_id>` với `{"session_id":"<uuid>","code":"<one-time-code>"}`.
Response có parcel_id, transaction_id, locker_id, status PICKUP_PENDING. Confirmation nhận tương tự.

## Kiểm chứng

```powershell
.\.venv\Scripts\python.exe -m backend.manage init
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
```

`pytest.ini` chỉ thu thập `backend/tests`; firmware native tests và script CoreIOT nằm ngoài
Phase 1. Tests dùng SQLite riêng theo tmp_path và PII giả, kiểm allocation/best-fit,
concurrency service + HTTP, idempotency, state guards, restart, authorization, TTL/one-use,
stale/reordered events, boot changes, missing sensor proof và lifecycle đầy đủ với mock.
Không có kết quả test phần cứng từ bộ test này.

Kết quả thực tế ngày 23/11/2026 trên Windows/Python 3.13.15: **61 passed, 0 failed**
(24,25 giây), một DeprecationWarning của Starlette/AnyIO về BlockingPortal.
`backend.manage init` và `pip check` thành công. Smoke Uvicorn thật trên localhost:
startup thành công; `/openapi.json` HTTP 200 (16 paths, 18 operations), `/docs` HTTP 200;
SQLite integrity_check=ok, đúng L01=S/L02=M và cả hai offline. Không có mock route trong OpenAPI.

Chưa triển khai: Serial/ESP-NOW/MQTT, heartbeat/reconcile thật, firmware, Web App,
notification, CoreIOT, reset mật khẩu, rate limiting login ở lớp triển khai, migration từ schema
không có user_version do bên khác tự tạo, và quy trình vận hành xử lý EXCEPTION thủ công.

## Đối chiếu thiết kế mục tiêu MVP v2.1 — 25/11/2026

Phần Phase 1 ở trên giữ mô tả implementation/API hiện có và kết quả kiểm thử tại thời điểm ghi nhận. Những câu chưa triển khai firmware/Web App/CoreIoT là phạm vi Phase 1; workspace gốc còn có firmware thử nghiệm và Expo starter; branch này chỉ kế thừa helper MQTT, không mang theo các source local/branch Mobile, chưa phải tích hợp v2.1. Policy mật khẩu trên branch này vẫn 12–128 ký tự, đúng source kế thừa; thay đổi local 8–128 ký tự ở workspace gốc không được đưa vào commit này.

| Nội dung | Implemented Phase 1 | Planned v2.1 |
|---|---|---|
| Nơi cấp mã | KIOSK/ADMIN tạo kiosk-session | RESIDENT chủ kiện yêu cầu từ Mobile App |
| Mã | Opaque secrets.token_urlsafe(16), không phải PIN ngắn | Chuỗi 6 chữ số giữ 0 đầu, CSPRNG; không trùng phiên active cùng scope |
| Nơi nhập/xác thực | RESIDENT gửi session_id + code qua API pickup | Nhập keypad, Central chuyển Serial, Backend kiểm owner/parcel/expiry/kiosk scope |
| TTL và thử sai | 30 giây, one-use, tối đa 5 lần sai theo phiên | 30 giây, one-use; giới hạn sai/rate limit kiosk cần thiết kế, chưa có source |
| Xác nhận lấy | Endpoint confirm thuộc RESIDENT | Contract xác nhận kiosk gắn đúng giao dịch/quyền cần cập nhật |

Giữ kiến trúc FastAPI + SQLite + Gateway trong cùng ứng dụng Python. Công việc tiếp theo: API/schema/migration cần thiết cho cấp/verify/confirm PIN, collision handling, verifier bảo vệ PIN ngắn, atomic consume + tạo PICKUP + UNLOCK intent, idempotency và giới hạn thử. Không log/lưu plaintext mã lâu dài, không mở khi Backend không phản hồi, không TOTP offline. Chưa đặt tên endpoint mới hoặc tuyên bố chúng đã triển khai.

Cần adapter Serial/ESP-NOW/MQTT thật, heartbeat/reconcile, mapping COMMAND_RESULT/DOOR_EVENT/STATUS sang DeviceEvent; không coi timeout 10 giây của evidence là timeout transport đã chốt. Các điều kiện confirmation/cycle/CLOSED mới/LOCK_APPLIED và giới hạn không chứng minh chốt gài vẫn giữ nguyên. [Interfaces v2.1](INTERFACES.md), [đặc tả mục tiêu](PROJECT_SPEC.md), [pinout baseline](../hardware/PINOUT.md).

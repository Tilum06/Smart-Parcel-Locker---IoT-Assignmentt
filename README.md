# Smart Parcel Locker — baseline M0 revision 1.3

Ngày 10/11/2026. Nhóm 2 người, 3 ESP32-S3/YoloUNO, L01/L02=S, L03=M, L04=L. Mỗi ngăn có servo/chốt, cảm biến cửa và **microswitch xác nhận chốt gài**. Central dùng ST7789 SPI 240×240/LVGL/keypad 4×4, ESP-NOW và USB Serial.

**Đặc tả áp dụng:** [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md), revision 1.3 theo các quyết định nhóm đã duyệt. [v1.2 gốc](PROJECT_SPEC_Smart_Parcel_Locker_v1.2.md) giữ nguyên làm lịch sử; quyết định mới trong đặc tả hiện hành thay thế nội dung cũ tương ứng.

Repository hiện là khung và tài liệu, chưa có firmware/API/Web App/test executable. Quyết định được duyệt không đồng nghĩa code, test HIL hoặc điểm công nghệ đã đạt. Xem [DECISIONS](docs/DECISIONS.md) cho gate còn mở và [ROADMAP](docs/ROADMAP.md) cho điều kiện bắt đầu từng mốc. Report nội bộ và thông báo môn học không được phát hành trong repository public.

## Thiết kế đã chốt

- **PC:** một ứng dụng Python + FastAPI + SQLite, một HTTP server. Backend sở hữu auth/business/allocation/state/audit; Gateway là module Serial/MQTT và device adapter cùng ứng dụng, không microservices/broker nội bộ/server Gateway riêng. Worker không chặn HTTP hay ghi domain trực tiếp.
- **Firmware:** PlatformIO, C/C++, Arduino; một project Locker Node dùng chung cho #1/#2, một Central chứa radio/Serial/kiosk/webserver/OTA. Board/revision/profile/GPIO/lib version/partition chưa khóa.
- **Transport PC:** USB Serial UTF-8 JSON Lines + LF. 115200 baud và 2048 byte/line là giá trị thử, timeout/buffer cần đo; không debug text trên protocol.
- **Khóa:** tổng 4 servo, 4 door sensor, 4 latch microswitch. Door/servo/latch độc lập; NOT_ENGAGED không chứng minh chốt mở hoàn toàn. ACK không chứng minh chốt gài.
- **Identity:** admin tạo trước cư dân gắn phòng chỉ có số, SĐT, credentials riêng. Đối chiếu đúng người trước reserve, không tự tạo cư dân từ shipper; không password mặc định bằng phòng/SĐT.
- **Nhận:** Web App login + đúng chủ đơn + mã phiên ngắn hạn hiển thị tại kiosk, bind phiên/kiosk, one-use và giới hạn thử. Đây không phải SMS OTP và có thể bị chia sẻ từ xa, không chứng minh vị trí tuyệt đối.
- **Allocation:** Best Fit S→S/M/L, M→M/L, L→L, chỉ AVAILABLE/online/fresh, không lỗi/bảo trì/active transaction. Cm thật chưa chốt, tie-break ID nhỏ nhất còn review.
- **Hoàn tất:** confirmation + cửa đã OPEN→CLOSED đúng phiên + LOCK intent/result + door CLOSED/latch ENGAGED mới. Không LOCK khi cửa OPEN/UNKNOWN, không auto AVAILABLE khi timeout/reboot/mất kết nối.

## Cấu trúc và tài liệu

```text
Assignment/                              # gốc Git hiện tại
├── README.md
├── .gitignore
├── PROJECT_SPEC_Smart_Parcel_Locker_v1.2.md # lịch sử yêu cầu
├── firmware/
│   ├── locker-node/                      # một project cho node #1/#2
│   └── central-controller/               # một project ESP32 #3
│       ├── kiosk/
│       └── webserver/
├── backend/                              # module nghiệp vụ/API của app PC
├── gateway/                              # module Serial/MQTT cùng app PC
├── web-app/                              # client cư dân/admin
├── coreiot/                              # mapping và export sạch
├── hardware/                             # BOM/sơ đồ/số đo
├── tests/                                # kế hoạch/evidence, chưa executable
└── docs/
    ├── PROJECT_SPEC.md                   # hiện hành revision 1.3
    ├── ARCHITECTURE.md
    ├── INTERFACES.md
    ├── DECISIONS.md
    ├── ROADMAP.md
    ├── ISSUES.md
    └── TEST_PLAN.md
```

Đọc theo thứ tự: [PROJECT_SPEC](docs/PROJECT_SPEC.md) → [DECISIONS](docs/DECISIONS.md) → [ARCHITECTURE](docs/ARCHITECTURE.md) → [INTERFACES](docs/INTERFACES.md) → [TEST_PLAN](docs/TEST_PLAN.md), [ISSUES](docs/ISSUES.md), [ROADMAP](docs/ROADMAP.md). Không tạo thêm tầng `smart-parcel-locker/` trong workspace.

## Bắt đầu M1

**Both:** DEC-01 duyệt theo phần: M1 bench/serializer/sensor guard trước, M2 wire/session/recovery tối thiểu trước tích hợp; cloud/OTA không chặn mọi nhánh. D-03/04/05/07 đã đóng policy; D-01/06/08/09/10 và P-01…05 phần parameter/implementation còn gate.

**Member A:** [hardware checklist](hardware/README.md), HW-01 một ngăn với sketch/test jig tối thiểu, không đợi FW-01 M2. Khảo sát YoloUNO/revision/pinout/nguồn và 4 microswitch, duyệt điện trước thử. Có thể spike ESP-NOW/LVGL/OTA Central sớm nếu target/toolchain sẵn; OTA scope cuối/T14 còn D-10.

**Member B:** BE-01 thiết kế SQLite/Best Fit và dữ liệu cư dân giả, intent/result/idempotency + mock transport/fixture. Chốt normalization/password hashing/session/code parameters trước implementation. Một FastAPI app nhập module Gateway; không chạy Backend/Gateway như hai server riêng. Chưa tạo manifest/config build đoán hoặc lệnh chạy chưa xác minh.

M1 là prototype/design; M2 là foundations + integration contract + recovery tối thiểu; M3 mới nghiệm thu một ngăn E2E. Full recovery/maintenance BE-03 M4 không thay phần tối thiểu trước INT-01. Phần Backend mất khi cửa đang OPEN vẫn cần policy D-08, không tự thiết kế actuator ngoại tuyến.

## Git và bảo vệ dữ liệu

Repository: [Smart Parcel Locker — IoT Assignment](https://github.com/Tilum06/Smart-Parcel-Locker---IoT-Assignmentt), nhánh baseline `main`. Đề xuất nhánh ngắn `feat/HW-01-prototype`, `feat/BE-01-allocation`, `fix/FW-02-retry`, người còn lại review trước merge; không cần develop. Chỉ feature có code/test/evidence thật mới DONE, lịch sử commit phải thể hiện đóng góp thực của cả hai thành viên.

Nếu Git báo dubious ownership, kiểm tra chủ sở hữu và đường dẫn trước. Khi đã xác minh đúng repository, có thể dùng ngoại lệ chỉ cho một lệnh; thay đường dẫn ví dụ bằng root tuyệt đối của checkout hiện tại:

```powershell
git -c safe.directory="C:/path/to/Smart-Parcel-Locker" status
```

Không dùng safe.directory=`*`, không đổi global config/owner tự động. Không commit SĐT/phòng/log thật, pickup_code, token CoreIOT, password/Wi-Fi, credentials hay SQLite runtime. `.gitignore` chỉ là bộ lọc, phải review diff/config/export.

## Phạm vi và minh chứng

Không sensor hàng, SMS OTP, TinyML, xác thực shipper thật, QR/RFID/camera/thanh toán trong MVP. Mã phiên kiosk, notification đơn trên Web App và notification sự cố CoreIOT vẫn có. Không tuyên bố hệ thống biết ngăn trống bằng sensor.

T06/T07/T08/T11/T12/T13/T14/N03 là kế hoạch cần code/test/evidence thật. OTA ưu tiên thử Central, không mặc định đủ 2 điểm T14, vẫn có thể mở rộng node. DOC-01 cần PDF đúng mẫu/tên, bảng tự đánh giá/phân công, ≥5 tham khảo, trích kế thừa/khai báo dùng AI, GitHub access/commit cả A/B và video demo theo thông báo môn.

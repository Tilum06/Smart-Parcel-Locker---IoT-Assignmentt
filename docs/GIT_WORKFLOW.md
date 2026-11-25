# Git workflow — MVP v2.1

Đây là **đề xuất nguồn gốc phát triển**, không phải yêu cầu viết lại lịch sử Git. Theo yêu cầu tiếp theo của người dùng, tài liệu được commit/push trên feat/embedded trong worktree riêng. Không tạo hai branch firmware con, không merge main hoặc thay đổi branch hiện có.

## Sơ đồ đề xuất

```text
main
└── feat/BE-01-allocation
    └── feat/demo-simulator
        ├── feat/resident-mobile-app
        ├── feat/coreiot
        └── feat/embedded
            ├── feat/central-controller
            └── feat/locker-node
```

| Branch | Vai trò |
|---|---|
| feat/embedded | Baseline chung và tích hợp Embedded |
| feat/central-controller | Member 1 phụ trách Central |
| feat/locker-node | Member 2 phụ trách Locker Node |
| feat/coreiot | Dashboard và MQTT Gateway |
| feat/resident-mobile-app | Ứng dụng cư dân và kết nối API |

Tên branch trên là đề xuất cụ thể của dự án. feat/embedded được tạo từ origin/feat/demo-simulator theo yêu cầu. Các branch còn lại chỉ là đề xuất; không tạo branch con hoặc đổi các branch hiện có trong lần này.

## Hiện trạng đã quan sát

Ngày 25/11/2026: worktree riêng ở branch `feat/embedded`, tạo từ `origin/feat/demo-simulator` tại `fa1c26b83810f58168cc8f131d1b94afca9e8a9a`. Đã kiểm tra GitHub trước tạo: remote chưa có feat/embedded và branch nguồn khớp remote-tracking. Commit/push tài liệu được người dùng yêu cầu; không merge main.

Workspace gốc vẫn ở feat/resident-mobile-app, HEAD f5cdef9187a32531343c32df8e36326b4fb0ab7c, giữ nguyên toàn bộ thay đổi local. Firmware thử nghiệm untracked, Expo starter trên branch Mobile và policy mật khẩu local 8 ký tự không được đưa vào branch tài liệu này. Backend kế thừa vẫn yêu cầu 12–128 ký tự. [Báo cáo](DOCUMENTATION_V2_1_REVIEW.md).

## Quy tắc làm việc hai thành viên

1. Hai thành viên phát triển firmware trên branch riêng, chỉ sửa source thuộc phạm vi phụ trách. Member 1 quản lý central-controller; Member 2 quản lý locker-node. Gateway/backend và common phải phối hợp review.
2. Protocol chung phải thống nhất trước sửa `firmware/common/`; thay contract cần cả hai review, không sửa một đầu rồi merge độc lập.
3. PR firmware về `feat/embedded`; build đúng target S3 và kiểm thử tương ứng trước merge. Review pinout, schema/correlation, guard cửa, retry/reboot và evidence.
4. Không push trực tiếp main, không force push. Không commit build/cache, credentials/token, database runtime hoặc COM port cá nhân.
5. Không reset/clean/stash hoặc ghi đè thay đổi local khi chưa được phép. Tách phần test cũ và thay đổi mật khẩu bằng quyết định riêng của nhóm; giữ file và evidence lịch sử.

## Trước khi chia branch firmware

- Chọn commit nền và xử lý quyền sở hữu các thay đổi local; rà staged diff để tránh mang theo source ngoài phạm vi.
- Chốt [PINOUT](../hardware/PINOUT.md) trên đúng board revision và sơ đồ nguồn. Central test đang esp32dev, không phải baseline S3 đã xác minh.
- Thống nhất [INTERFACES](INTERFACES.md): node/locker ID, MAC/channel, serialization/version, timeout/retry/dedup, boot/sequence, bảo vệ ESP-NOW và Serial envelope.
- Thống nhất cấu hình chung, board/framework/library version, USB CDC, cách override COM tại máy và quy trình build/test; không ghi COM cá nhân vào baseline mới.
- Chốt contract API PIN v2.1 và mapping DeviceEvent để hai đầu firmware dùng cùng ý nghĩa ACK/result/door/status.
- Baseline tích hợp feat/embedded chứa tài liệu; chỉ tạo hai branch con khi được yêu cầu ở bước sau. Không dùng sơ đồ đề xuất để rebase/viết lại lịch sử hiện có.

# Resident Mobile App — MVP v2.1

**Planned trên feat/embedded:** thư mục này chỉ chứa tài liệu. Expo/React Native starter dùng Expo Router nằm trên branch feat/resident-mobile-app; source Mobile và package.json không được đưa vào commit tài liệu Embedded.

## Luồng mục tiêu

1. Cư dân đăng nhập, xem danh sách kiện của mình và chọn kiện cần nhận.
2. App yêu cầu Backend cấp PIN **6 chữ số**, giữ số 0 đầu, TTL **30 giây**.
3. App hiển thị mã/countdown; người nhận nhập mã trên keypad kiosk.
4. Central chuyển mã tới Backend; Backend kiểm owner/parcel/expiry/kiosk scope, tiêu thụ một lần atomic với tạo giao dịch/UNLOCK intent.
5. Người nhận lấy hàng, đóng cửa và xác nhận; App theo dõi kết quả Backend khi đủ evidence.

Countdown chỉ hỗ trợ UI, Backend quyết định hiệu lực. Không log mã/token hoặc đặt vào URL; không TOTP offline; Backend không phản hồi thì không mở. App không trực tiếp điều khiển servo.

**API PIN chưa triển khai.** Phase 1 trên branch này vẫn dùng KIOSK tạo opaque code và RESIDENT gửi session_id/code qua API pickup. Cần chốt API PIN/confirmation kiosk trước tích hợp. [Interfaces](../docs/INTERFACES.md), [Phase 1](../docs/BACKEND_PHASE1.md).

Member 1 phụ trách Mobile/API theo [phân công đề xuất](../docs/ROADMAP.md). Việc chạy starter/lint/typecheck thực hiện ở checkout Mobile có source và theo hướng dẫn của branch đó; không chạy lệnh Expo tại worktree tài liệu này.

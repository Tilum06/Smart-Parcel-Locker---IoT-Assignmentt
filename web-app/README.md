# Web App — trạng thái trong MVP v2.1

Thư mục hiện chỉ có tài liệu, **chưa có Web App production**. Client nhận hàng mục tiêu là [Resident Mobile App](../mobile/README.md): App login/chọn kiện/yêu cầu PIN 6 chữ số/30 giây, nhập PIN tại keypad kiosk và Backend xác thực. Không tiếp tục mô tả kiosk hiển thị mã để người nhận nhập Web App như luồng mục tiêu.

[Simulator development](../backend/demo/README.md) có giao diện web localhost dùng **API Phase 1 cũ** (kiosk tạo opaque code, cư dân xác thực qua API). Giữ để thử nghiệp vụ, không coi là Mobile App/Web App production v2.1. Giao diện admin/cư dân web chưa được triển khai trong lần này.

Backend vẫn quản lý auth/ownership/allocation và evidence trên L01=S/L02=M. MC-38 đo cửa; LOCK_APPLIED không chứng minh gài chốt. [Kiến trúc](../docs/ARCHITECTURE.md), [API thực tế và phần Planned](../docs/INTERFACES.md).

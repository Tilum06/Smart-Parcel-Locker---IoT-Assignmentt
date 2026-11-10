# Kiểm thử và evidence — revision 1.3

Chỉ có [TEST_PLAN](../docs/TEST_PLAN.md), chưa có executable hoặc evidence chức năng. Giữ TC-01…29 và tiểu mục, thêm TC-30…35 cho latch/LOCK guard, kiosk code, hai thứ tự confirmation/cửa, combined Central, expired command và adapter/worker.

M1: bench một ngăn/jig trong HW-01, subset protocol v1 và dữ liệu giả. M2: foundations + parser/allocator/auth/worker và recovery tối thiểu, không chờ BE-03 full M4. M3: một ngăn gửi–nhận E2E có mã kiosk và door cycle/LOCK/latch thật. Kế hoạch hay mock không thay test HIL/điểm công nghệ.

Evidence ghi ngày/TC/FR/Issue/commit/build/contract revision, setup/initial state, steps/expected/actual, request/transaction/boot/sequence/epoch, PASS/FAIL/BLOCKED/NOT RUN và reviewer. Khử phone/phòng/pickup_code/password/token, không commit DB/log runtime; `.log` bị ignore, dùng report Markdown/CSV đã review hoặc artifact sạch.

TC-33 kiểm cùng build kiosk+ESP-NOW+Serial+webserver+OTA; TC-31 code sai/expired/used/khác phiên/attempt limit; TC-32 confirmation trước hoặc sau đóng cửa; TC-30 door/latch độc lập và không LOCK khi OPEN/UNKNOWN. M0 consistency chỉ là QA tài liệu, không tạo PASS giả cho các test chưa hiện thực. DOC-01 tự đánh giá phải nêu đúng kế hoạch/code/test/evidence và phần dùng AI.

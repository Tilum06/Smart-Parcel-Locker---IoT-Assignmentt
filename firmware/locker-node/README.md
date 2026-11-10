# Locker Node — baseline revision 1.3

Owner **Member A**, HW-01/FW-01/FW-02. M0 chỉ tài liệu, chưa code/config build. Đã chọn PlatformIO, C/C++, Arduino; một project cho #1 L01=S/L02=S và #2 L03=M/L04=L bằng cấu hình, không một project/ngăn.

Mỗi ngăn có servo/chốt, door sensor và microswitch latch bắt buộc. Door OPEN/CLOSED/UNKNOWN, servo command, latch ENGAGED/NOT_ENGAGED/UNKNOWN độc lập. ACK/APPLIED không chứng minh ENGAGED; switch nhả không chứng minh chốt mở hoàn toàn. Node không phân ngăn hoặc cảm biến hàng; không LOCK khi door OPEN/UNKNOWN, không UNLOCK mới khi trạng thái/epoch chưa biết.

HW-01 có sketch/test jig để đo một ngăn trước FW-01. M1 dùng subset v1 UNLOCK/LOCK/GET_STATUS/ACK/ERROR/DOOR_EVENT/STATUS; M2 bổ sung epoch/dedup/boot/freshness/recovery theo [INTERFACES](../../docs/INTERFACES.md), không protocol khác. ACK không sensor, STATUS/latch evidence riêng, source/target đúng route.

Trước build/upload phải xác minh YoloUNO/revision/profile, flash/partition, servo/nguồn/GPIO/góc/debounce/lib version trong D-09/P-02; không tự điền config đoán. Boot không auto AVAILABLE hoặc replay actuator. TC-28/30 bench, TC-24…27/34 radio và epoch là test mục tiêu, chưa chạy. [DECISIONS](../../docs/DECISIONS.md) và [ISSUES](../../docs/ISSUES.md) ghi gate.

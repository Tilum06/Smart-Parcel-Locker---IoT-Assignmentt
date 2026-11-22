# Locker Node — ESP32-S3 #2, v2.0

**Một node duy nhất** điều khiển **L01=S và L02=M**, không còn Locker A/B riêng. PlatformIO + C++ Arduino. Mỗi ngăn: MG90S (servo/chốt) + MC-38 NC. D4/GPIO7: servo L01; D6/GPIO9: servo L02; A3/GPIO4: MC-38 L01; A0/GPIO1: MC-38 L02 (chỉ là mapping đề xuất, phải test).

Node nhận lệnh UNLOCK/LOCK/GET_STATUS qua ESP-NOW từ Central, kiểm locker_id/request_id/trạng thái, phát ACK riêng với COMMAND_RESULT và DOOR_EVENT/STATUS. Chỉ LOCK khi cửa CLOSED; UNKNOWN/OPEN từ chối. Không phân ngăn, không tự cấp đơn, không auto AVAILABLE khi reboot hoặc lỗi. Servo action không đồng nghĩa chốt vật lý đã gài, **không có latch sensor**. Nguồn servo 5V ngoài và GND chung, tránh kẹt/quá tải.

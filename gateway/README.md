# Gateway module trong PC app — revision 1.3

Owner **Member B**, GW-01/IOT-01/IOT-02. Gateway và Backend thuộc **cùng một ứng dụng Python + FastAPI + SQLite**, một HTTP server; không app/server/broker nội bộ riêng. Chưa có code/manifest/dependency khóa version.

Gateway sở hữu Serial Gateway, device transport adapter và CoreIOT MQTT worker. USB Serial UTF-8 JSON Lines LF đã chốt D-07; 115200 baud/2048 byte line gồm LF/timeout chỉ thử nghiệm. Parser bounded, line dở/sai không thực thi, debug text tách khỏi protocol. ACK map đúng ACK radio, không thêm sensor; STATUS/event giữ source/target/boot/sequence/epoch và correlation.

Worker I/O không chặn FastAPI; phát device event/connection/transport result tới Backend service, không reserve, complete hoặc ghi SQLite nghiệp vụ trực tiếp. Contract nội bộ submit_device_command/on_device_event/on_connection_status/on_transport_result/invalidate_pending ở [INTERFACES](../docs/INTERFACES.md), không network API thứ hai. Queue/backpressure/lifecycle và version còn review, không sinh abstraction khi chưa cần.

M1 mock transport/fixtures v1; M2 handshake/status/reconnect, lost ACK/dedup/epoch invalidation tối thiểu trước INT-01. Disconnect không replay queue mù hoặc auto AVAILABLE. RPC MQTT cũng qua Backend auth/state. Không log raw line chứa phone/code/secret, không gửi chúng lên CoreIOT. TC-25…27/34/35 và TC-17A là kế hoạch chưa chạy.

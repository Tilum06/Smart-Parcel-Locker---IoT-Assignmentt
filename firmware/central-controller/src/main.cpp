#include <Arduino.h>

#include "pin_config.h"

namespace {
constexpr uint8_t kNodeId = 1;
constexpr char kFirmwareVersion[] = "2.1.0-phase0";
constexpr uint32_t kSerialBaud = 115200;
constexpr uint32_t kHeartbeatIntervalMs = 1000;
uint32_t lastHeartbeatMs = 0;
}  // namespace

void setup() {
    Serial.begin(kSerialBaud);
    Serial.println("Smart Parcel Locker - Central Controller");
    Serial.printf("Node ID: %u\n", static_cast<unsigned>(kNodeId));
    Serial.printf("Firmware version: %s\n", kFirmwareVersion);
    Serial.println("Phase 0: Serial heartbeat only; peripherals not initialized.");
    lastHeartbeatMs = millis();
}

void loop() {
    const uint32_t now = millis();
    if (static_cast<uint32_t>(now - lastHeartbeatMs) >= kHeartbeatIntervalMs) {
        lastHeartbeatMs = now;
        Serial.printf("Heartbeat | node=%u | firmware=%s | uptime_ms=%lu\n",
                      static_cast<unsigned>(kNodeId), kFirmwareVersion,
                      static_cast<unsigned long>(now));
    }
}

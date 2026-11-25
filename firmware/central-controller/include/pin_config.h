#pragma once

// Numeric ESP32-S3 GPIOs from hardware/PINOUT.md.
// Declarations only: Phase 0 does not initialize peripheral pins.
#ifndef CENTRAL_TFT_CS_GPIO
#define CENTRAL_TFT_CS_GPIO 38
#endif

namespace central {
namespace pins {
constexpr int kTftSck = 10;
constexpr int kTftMosi = 17;
constexpr int kTftMiso = -1;
constexpr int kTftRst = 21;
constexpr int kTftDc = 18;
constexpr int kTftCs = CENTRAL_TFT_CS_GPIO;
constexpr int kTftWidth = 240;
constexpr int kTftHeight = 240;

constexpr int kKeypadRows[4] = {5, 6, 7, 8};
constexpr int kKeypadCols[4] = {9, 1, 2, 4};

static_assert(kTftCs == 38 || kTftCs == -1,
              "Use GPIO38, or -1 for a display without CS");
}  // namespace pins
}  // namespace central

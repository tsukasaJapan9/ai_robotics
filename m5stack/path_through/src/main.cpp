#include <M5Unified.h>

HardwareSerial& serialToDevice = Serial1; // Dynamixelなど外部デバイス用

void setup() {
  auto cfg = M5.config();
  M5.begin(cfg);

  Serial.begin(1000000);  // USBシリアル（PCとの通信）
  serialToDevice.begin(1000000, SERIAL_8N1, 33, 32); // RX=13, TX=14（必要に応じてピン番号調整）

  Serial.println("Serial pass-through started.");
}

void loop() {
  // USB -> Device
  while (Serial.available()) {
    serialToDevice.write(Serial.read());
  }

  // Device -> USB
  while (serialToDevice.available()) {
    Serial.write(serialToDevice.read());
  }
}

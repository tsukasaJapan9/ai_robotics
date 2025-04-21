import time

import serial

LED_MAX_BRIGHTNESS = 32

# M5Stackと接続しているシリアルポートを指定（例: 'COM3'や'/dev/ttyUSB0'）
ser = serial.Serial("/dev/ttyUSB0", 115200)
time.sleep(2)  # 接続待機

# 送信するRGBデータ（例: R, G, B の順）
rgb_data: list[int] = []
for i in range(64):
    r = i
    g = 0
    b = 0
    rgb_data.extend([r, g, b])

for _ in range(10):
    ser.write(bytearray(rgb_data))
    time.sleep(0.1)
ser.close()
